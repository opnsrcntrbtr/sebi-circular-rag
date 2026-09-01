"""Offline tests for scripts/finetune/roundtrip_filter.py's pure pieces.
roundtrip_check needs a real retriever, so it's exercised via a fake
retriever object here, matching the pattern established for
mine_structural_pairs.py's mine_hard_negatives tests - never a live
embedder/index in this suite.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from finetune.roundtrip_filter import (  # noqa: E402
    build_text_to_doc_map,
    filter_boilerplate,
    load_rows,
    resolve_positive_doc,
    roundtrip_check,
)
from finetune.mine_structural_pairs import MIN_CHUNK_CHARS  # noqa: E402

LONG = "x" * MIN_CHUNK_CHARS


def _row(query="q", positive="p", positive_doc=None, **over):
    base = {"query": query, "positive": positive, "template": "t", "source_doc": "D"}
    if positive_doc is not None:
        base["positive_doc"] = positive_doc
    base.update(over)
    return base


# ---------------------------------------------------------------------------
# load_rows
# ---------------------------------------------------------------------------

def test_load_rows_reads_jsonl_and_skips_blank_lines(tmp_path):
    import json
    path = tmp_path / "rows.jsonl"
    path.write_text(json.dumps(_row(query="a")) + "\n\n" + json.dumps(_row(query="b")) + "\n",
                    encoding="utf-8")
    rows = load_rows(path)
    assert [r["query"] for r in rows] == ["a", "b"]


# ---------------------------------------------------------------------------
# filter_boilerplate
# ---------------------------------------------------------------------------

def test_filter_boilerplate_drops_signature_positives():
    rows = [_row(positive="clean substantive text " + LONG),
            _row(positive=LONG + " Yours faithfully, A Manager")]
    kept, n_dropped = filter_boilerplate(rows)
    assert len(kept) == 1
    assert n_dropped == 1
    assert "Yours faithfully" not in kept[0]["positive"]


def test_filter_boilerplate_keeps_all_when_none_are_boilerplate():
    rows = [_row(positive="clean one " + LONG), _row(positive="clean two " + LONG)]
    kept, n_dropped = filter_boilerplate(rows)
    assert len(kept) == 2
    assert n_dropped == 0


# ---------------------------------------------------------------------------
# build_text_to_doc_map / resolve_positive_doc
# ---------------------------------------------------------------------------

def test_build_text_to_doc_map_strips_context_header():
    chunks_by_doc = {"DOC1": [
        {"doc_id": "DOC1", "text": "DOC1 | Some subject | s/1\nreal body text"}]}
    m = build_text_to_doc_map(chunks_by_doc)
    assert m == {"real body text": "DOC1"}


def test_resolve_positive_doc_prefers_explicit_field():
    row = _row(positive="some text", positive_doc="EXPLICIT_DOC")
    # even if the text map would resolve to something else, the explicit
    # field wins - it's the ground truth when present
    text_to_doc = {"some text": "WRONG_DOC"}
    assert resolve_positive_doc(row, text_to_doc) == "EXPLICIT_DOC"


def test_resolve_positive_doc_falls_back_to_text_lookup_when_field_absent():
    row = _row(positive="some text")  # no positive_doc - predates the field
    text_to_doc = {"some text": "LOOKED_UP_DOC"}
    assert resolve_positive_doc(row, text_to_doc) == "LOOKED_UP_DOC"


def test_resolve_positive_doc_returns_none_when_unresolvable():
    row = _row(positive="text not in the corpus map")
    assert resolve_positive_doc(row, {}) is None


# ---------------------------------------------------------------------------
# roundtrip_check - fake retriever, deterministic ranking
# ---------------------------------------------------------------------------

@dataclass
class _FakeChunk:
    doc_id: str


class _FakeRetriever:
    """retrieve(query, top_n) -> [(chunk, score), ...]. Ranking is keyed by
    the QUERY string itself so tests can control exactly what each query
    "retrieves" without a real embedder/index."""

    def __init__(self, rankings: dict[str, list[str]]):
        self._rankings = rankings

    def retrieve(self, query: str, top_n: int):
        docs = self._rankings.get(query, [])
        return [(_FakeChunk(doc_id=d), 1.0) for d in docs[:top_n]]


def test_roundtrip_check_keeps_row_when_positive_doc_is_retrieved():
    rows = [_row(query="q1", positive="p1", positive_doc="DOC_A")]
    retriever = _FakeRetriever({"q1": ["DOC_A", "DOC_B"]})
    kept, stats = roundtrip_check(rows, retriever, text_to_doc={}, top_k=10)
    assert len(kept) == 1
    assert stats["n_kept"] == 1
    assert stats["n_failed_roundtrip"] == 0


def test_roundtrip_check_drops_row_when_positive_doc_not_retrieved():
    rows = [_row(query="q1", positive="p1", positive_doc="DOC_A")]
    retriever = _FakeRetriever({"q1": ["DOC_X", "DOC_Y"]})  # DOC_A never appears
    kept, stats = roundtrip_check(rows, retriever, text_to_doc={}, top_k=10)
    assert kept == []
    assert stats["n_failed_roundtrip"] == 1


def test_roundtrip_check_respects_top_k_window():
    rows = [_row(query="q1", positive="p1", positive_doc="DOC_A")]
    # DOC_A is retrieved, but only at rank 3 - outside a top_k=2 window
    retriever = _FakeRetriever({"q1": ["DOC_X", "DOC_Y", "DOC_A"]})
    kept, stats = roundtrip_check(rows, retriever, text_to_doc={}, top_k=2)
    assert kept == []
    assert stats["n_failed_roundtrip"] == 1


def test_roundtrip_check_falls_back_to_text_map_when_no_positive_doc_field():
    rows = [_row(query="q1", positive="p1")]  # no positive_doc field
    text_to_doc = {"p1": "DOC_A"}
    retriever = _FakeRetriever({"q1": ["DOC_A"]})
    kept, stats = roundtrip_check(rows, retriever, text_to_doc, top_k=10)
    assert len(kept) == 1
    assert kept[0]["positive_doc"] == "DOC_A"  # stamped onto the output row


def test_roundtrip_check_drops_row_with_unresolvable_positive_doc():
    rows = [_row(query="q1", positive="text nowhere in the corpus")]
    retriever = _FakeRetriever({"q1": ["DOC_A"]})
    kept, stats = roundtrip_check(rows, retriever, text_to_doc={}, top_k=10)
    assert kept == []
    assert stats["n_no_doc_resolved"] == 1


def test_roundtrip_check_empty_rows_returns_empty():
    kept, stats = roundtrip_check([], _FakeRetriever({}), text_to_doc={})
    assert kept == []
    assert stats["n_kept"] == 0
