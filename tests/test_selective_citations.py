"""Tests for B' selective citations: select_citations() and its integration."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sebi_rag.segment import Chunk  # noqa: E402
from sebi_rag.generate import select_citations, _CITATION_MARGIN_DEFAULT  # noqa: E402


def _chunk(cid: str, text: str = "x") -> Chunk:
    return Chunk(id=cid, doc_id=cid.split("#")[0], section="s", text=text)


class _FakeReranker:
    """Deterministic scorer: returns preset answer-relevance scores, sorted desc."""

    def __init__(self, scores: dict[str, float]):
        self._scores = scores

    def rerank(self, query, candidates):
        paired = [(c, self._scores[c.id]) for c in candidates]
        paired.sort(key=lambda cs: -cs[1])
        return paired


# --- Task 1: select_citations() pure function ---

def test_keeps_only_contexts_within_margin_of_top():
    ctx = [_chunk("A"), _chunk("B"), _chunk("C")]
    scorer = _FakeReranker({"A": 0.90, "B": 0.80, "C": 0.40})
    # margin 0.15: keep >= 0.75 -> A, B; drop C
    assert select_citations("ans", ctx, scorer, margin=0.15) == ["A", "B"]


def test_always_keeps_at_least_one_when_all_below_margin():
    ctx = [_chunk("A"), _chunk("B")]
    scorer = _FakeReranker({"A": 0.90, "B": 0.10})
    # margin 0.05: only A within margin of itself -> exactly the top
    assert select_citations("ans", ctx, scorer, margin=0.05) == ["A"]


def test_empty_contexts_returns_empty():
    assert select_citations("ans", [], _FakeReranker({}), margin=0.15) == []


def test_returns_ids_in_original_context_order_not_score_order():
    ctx = [_chunk("A"), _chunk("B"), _chunk("C")]
    scorer = _FakeReranker({"A": 0.80, "B": 0.95, "C": 0.85})  # score order B,C,A
    # all within 0.15 of top (0.95): keep all, but in context order A,B,C
    assert select_citations("ans", ctx, scorer, margin=0.15) == ["A", "B", "C"]


def test_default_margin_is_sigmoid_scale():
    assert 0.0 < _CITATION_MARGIN_DEFAULT < 1.0

from sebi_rag.generate import answer_with_abstention, ExtractiveStubGenerator  # noqa: E402


def _reranked(chunks):
    return [(c, 0.9) for c in chunks]  # all above abstain threshold


# --- Task 2: answer_with_abstention integration ---

def test_answer_with_scorer_filters_citations():
    ctx = [_chunk("A", "alpha text"), _chunk("B", "beta text"), _chunk("C", "gamma")]
    scorer = _FakeReranker({"A": 0.95, "B": 0.90, "C": 0.30})
    ans = answer_with_abstention(
        "q", _reranked(ctx), ExtractiveStubGenerator(), threshold=0.05, top_k=10,
        citation_scorer=scorer, citation_margin=0.15)
    assert ans.citations == ["A", "B"]           # C dropped (below margin)


def test_answer_without_scorer_cites_all_contexts_backward_compat():
    ctx = [_chunk("A"), _chunk("B"), _chunk("C")]
    ans = answer_with_abstention(
        "q", _reranked(ctx), ExtractiveStubGenerator(), threshold=0.05, top_k=10)
    assert set(ans.citations) == {"A", "B", "C"}  # unchanged default
