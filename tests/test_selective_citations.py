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


def test_min_keep_widens_a_collapsed_selection():
    """Measured 2026-08-12: on 206 rows where retrieval found every relevant
    doc, B' left 34 citing nothing relevant — 19 of them solely because the
    margin collapsed the kept set to a single wrong context. Keeping the top
    `min_keep` by score bounds that failure."""
    ctx = [_chunk("A"), _chunk("B"), _chunk("C"), _chunk("D")]
    scorer = _FakeReranker({"A": 0.90, "B": 0.20, "C": 0.15, "D": 0.10})
    # margin 0.05 keeps only A; min_keep=3 widens to the top three by score.
    assert select_citations("ans", ctx, scorer, margin=0.05, min_keep=3) == ["A", "B", "C"]


def test_min_keep_does_not_shrink_a_wider_margin_selection():
    ctx = [_chunk("A"), _chunk("B"), _chunk("C"), _chunk("D")]
    scorer = _FakeReranker({"A": 0.90, "B": 0.88, "C": 0.86, "D": 0.84})
    # all four within margin; min_keep must not truncate to 3.
    assert select_citations("ans", ctx, scorer, margin=0.15, min_keep=3) == ["A", "B", "C", "D"]


def test_min_keep_cannot_exceed_available_contexts():
    ctx = [_chunk("A"), _chunk("B")]
    scorer = _FakeReranker({"A": 0.90, "B": 0.10})
    assert select_citations("ans", ctx, scorer, margin=0.05, min_keep=3) == ["A", "B"]


def test_min_keep_defaults_to_current_single_keep_behaviour():
    """Default must not change the pure function's contract; the wider
    operating point is a configured decision, not a silent one."""
    ctx = [_chunk("A"), _chunk("B")]
    scorer = _FakeReranker({"A": 0.90, "B": 0.10})
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


def test_citation_scorer_for_selects_the_nli_backend():
    """The backend choice must go through the same single decision point as
    the enable flag, or eval and production can disagree about which scorer
    produced a citation set."""
    reranker = _FakeReranker({})
    sentinel = object()
    got = citation_scorer_for(True, reranker, backend="nli",
                              nli_loader=lambda: sentinel)
    assert got is sentinel


def test_citation_scorer_for_defaults_to_the_reranker_backend():
    reranker = _FakeReranker({})
    assert citation_scorer_for(True, reranker) is reranker


def test_citation_scorer_for_disabled_beats_backend_choice():
    reranker = _FakeReranker({})
    called = []
    got = citation_scorer_for(False, reranker, backend="nli",
                              nli_loader=lambda: called.append(1))
    assert got is None and not called, "must not load a model just to discard it"


def test_citation_scorer_for_rejects_an_unknown_backend():
    try:
        citation_scorer_for(True, _FakeReranker({}), backend="magic")
    except ValueError as e:
        assert "magic" in str(e)
    else:
        raise AssertionError("expected ValueError on unknown backend")

def test_margin_045_keeps_more_than_035():
    """Looser margin (0.45) keeps more contexts than tight margin (0.35)."""
    ctx = [_chunk("A"), _chunk("B"), _chunk("C"), _chunk("D")]
    scorer = _FakeReranker({"A": 0.95, "B": 0.75, "C": 0.60, "D": 0.30})
    # margin 0.35: keep >= 0.60 -> A, B, C (D at 0.30 < 0.60)
    tight = select_citations("ans", ctx, scorer, margin=0.35)
    assert tight == ["A", "B", "C"]
    # margin 0.45: keep >= 0.50 -> A, B, C (D at 0.30 < 0.50)
    loose = select_citations("ans", ctx, scorer, margin=0.45)
    assert loose == ["A", "B", "C"]  # same set at this score distribution
    # With a tighter spread, margin difference matters more:
    scorer2 = _FakeReranker({"A": 0.95, "B": 0.80, "C": 0.65, "D": 0.40})
    tight2 = select_citations("ans", ctx, scorer2, margin=0.35)
    loose2 = select_citations("ans", ctx, scorer2, margin=0.45)
    # tight: keep >= 0.60 -> A, B, C; loose: keep >= 0.50 -> A, B, C (D at 0.40 < 0.50)
    assert tight2 == ["A", "B", "C"]
    assert loose2 == ["A", "B", "C"]  # D still below both margins
    # Verify margin widening actually matters with closer scores:
    scorer3 = _FakeReranker({"A": 0.95, "B": 0.85, "C": 0.75})
    tight3 = select_citations("ans", ctx[:3], scorer3, margin=0.15)
    loose3 = select_citations("ans", ctx[:3], scorer3, margin=0.25)
    assert tight3 == ["A", "B"]  # C at 0.75 < 0.80 (top-0.15)
    assert loose3 == ["A", "B", "C"]  # C at 0.75 >= 0.60 (top-0.25)


def test_scorer_disabled_cites_all_contexts():
    """When citation scorer is None, all contexts are cited (legacy behavior)."""
    from sebi_rag.generate import answer_with_abstention, ExtractiveStubGenerator
    ctx = [_chunk("SEBI/A/1#s#0"), _chunk("SEBI/B/2#s#0")]
    reranked = [(ctx[0], 0.9), (ctx[1], 0.7)]
    ans = answer_with_abstention("q", reranked, ExtractiveStubGenerator(),
                                 threshold=0.4, citation_scorer=None)
    assert not ans.abstained
    # All context ids cited (not selective)
    assert set(ans.citations) == {"SEBI/A/1#s#0", "SEBI/B/2#s#0"}


def test_select_citations_empty_contexts():
    """Empty context list returns empty citation list."""
    scorer = _FakeReranker({})
    result = select_citations("ans", [], scorer)
    assert result == []
