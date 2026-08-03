"""Tests for B' selective citations: select_citations() and its integration."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sebi_rag.segment import Chunk  # noqa: E402
from sebi_rag.generate import (  # noqa: E402
    select_citations, citation_scorer_for, _CITATION_MARGIN_DEFAULT)


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

# --- Regression test: Settings-built pipeline honors citation_scorer flag ---

def test_settings_citation_scorer_enabled_true():
    """When citation_scorer_enabled=True, Settings loads a non-None scorer."""
    from sebi_rag.settings import Settings
    s = Settings("/dev/null", "/tmp", citation_scorer_enabled=True, citation_margin=0.2)
    assert s.citation_scorer_enabled is True
    assert s.citation_margin == 0.2


def test_settings_citation_scorer_enabled_false():
    """When citation_scorer_enabled=False, Settings loads scorer disabled."""
    from sebi_rag.settings import Settings
    s = Settings("/dev/null", "/tmp", citation_scorer_enabled=False)
    assert s.citation_scorer_enabled is False


# --- citation_scorer_for: the single shared enable/disable decision -----------
# All three pipeline builders (build_default_pipeline, eval_json,
# derive_thresholds) route through this so eval and production can never
# disagree on whether B' is active (the train/serve skew we are closing).

def test_citation_scorer_for_returns_reranker_when_enabled():
    scorer = _FakeReranker({})
    assert citation_scorer_for(True, scorer) is scorer


def test_citation_scorer_for_returns_none_when_disabled():
    scorer = _FakeReranker({})
    assert citation_scorer_for(False, scorer) is None
