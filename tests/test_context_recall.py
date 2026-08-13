"""The gate must measure the context window, not just the fusion list.

`pipeline.query` returns `retrieved_ids` from `candidates` — the PRE-rerank
fusion output (pipeline.py:141). `score_row`'s `recall` is computed over that,
so the gate's headline retrieval metric describes the retriever, not the
`top_k` contexts the answer and its citations are actually built from (which
are post-rerank and post-`demote_superseded`).

Measured 2026-08-13 over 204 answerable non-as_of rows:
    recall over fusion list  0.9534   complete misses  9
    recall over contexts     0.9240   complete misses 15
The gate overstates recall by 2.94pp and hides 6 complete misses.

`context_recall` is added alongside `recall_at_k` rather than replacing it —
the retriever metric stays meaningful, it was just never the whole story.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from sebi_rag.generate import (  # noqa: E402
    ExtractiveStubGenerator, answer_with_abstention,
)
from sebi_rag.segment import Chunk  # noqa: E402


def _chunk(cid: str, text: str = "body text") -> Chunk:
    return Chunk(id=cid, doc_id=cid.split("#")[0], section="s", text=text)


def _reranked(chunks, score=0.9):
    return [(c, score) for c in chunks]


# --- Answer must expose what the generator actually saw --------------------

def test_answer_records_the_context_ids_it_used():
    ctx = [_chunk("A/1#0"), _chunk("B/1#0"), _chunk("C/1#0")]
    ans = answer_with_abstention(
        "q", _reranked(ctx), ExtractiveStubGenerator(), threshold=0.05, top_k=10)
    assert ans.context_ids == ["A/1#0", "B/1#0", "C/1#0"]


def test_context_ids_respect_top_k():
    ctx = [_chunk(f"D{i}/1#0") for i in range(5)]
    ans = answer_with_abstention(
        "q", _reranked(ctx), ExtractiveStubGenerator(), threshold=0.05, top_k=2)
    assert len(ans.context_ids) == 2


def test_context_ids_populated_even_when_abstaining():
    """An abstention still had a context window; measuring retrieval delivery
    must not depend on whether the pipeline chose to answer."""
    ctx = [_chunk("A/1#0")]
    ans = answer_with_abstention(
        "q", _reranked(ctx, score=0.001), ExtractiveStubGenerator(),
        threshold=0.05, top_k=10)
    assert ans.abstained and ans.abstention_reason == "score_floor"
    assert ans.context_ids == ["A/1#0"]


# --- the metric must reach the gate ----------------------------------------

def test_vectors_exposes_context_recall():
    from golden_v7.score import vectors

    recs = [{"adjudicated": True, "recall": 1.0, "context_recall": 0.5,
             "ndcg": 0.8, "citation_precision": 1.0, "citation_recall": 1.0,
             "abstention": 1.0}]
    assert vectors(recs)["context_recall"] == [0.5]


def test_gate_floors_context_recall():
    from golden_v7.derive_thresholds import derive_floors

    floors = derive_floors({"recall": [0.95], "context_recall": [0.92]})
    assert "context_recall" in floors, "the gate cannot see context-window delivery"


def test_context_recall_floor_catches_a_regression_fusion_recall_misses():
    """Demotion or reranking can empty the context window while the fusion
    list is untouched - exactly the 6 rows the old gate could not see."""
    from golden_v7.derive_thresholds import derive_floors
    from golden_v7.gate_select import floors_ok

    floors = derive_floors({"recall": [0.95, 0.95], "context_recall": [0.92, 0.92]})
    report = {"recall_at_k": 0.95, "context_recall": 0.60}
    assert floors_ok(report, floors) is False
