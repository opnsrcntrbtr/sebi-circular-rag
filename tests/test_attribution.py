"""NLI attribution scorer for B' citation selection.

B' needs to know whether a context *supports* the answer, not whether it is
topically relevant to it. These tests pin the two things that silently break
an entailment scorer: taking the wrong class index, and losing the Reranker
protocol's contract.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sebi_rag.attribution import NLIAttributionScorer, entailment_index  # noqa: E402
from sebi_rag.segment import Chunk  # noqa: E402


def _chunk(cid: str, text: str = "x") -> Chunk:
    return Chunk(id=cid, doc_id=cid.split("#")[0], section="s", text=text)


# --- entailment_index: the silent-inversion guard ---------------------------

def test_entailment_index_read_from_id2label_not_assumed():
    # cross-encoder/nli-deberta-v3-base order: contradiction, entailment, neutral
    assert entailment_index({0: "contradiction", 1: "entailment", 2: "neutral"}) == 1


def test_entailment_index_handles_a_different_label_order():
    # MNLI checkpoints commonly use entailment first. Hardcoding 1 would invert
    # the scorer here and read as a null result rather than a bug.
    assert entailment_index({0: "entailment", 1: "neutral", 2: "contradiction"}) == 0


def test_entailment_index_is_case_insensitive():
    assert entailment_index({0: "CONTRADICTION", 1: "ENTAILMENT"}) == 1


def test_entailment_index_raises_when_absent():
    """Failing loudly beats scoring on an arbitrary class."""
    try:
        entailment_index({0: "positive", 1: "negative"})
    except ValueError as e:
        assert "entailment" in str(e).lower()
    else:
        raise AssertionError("expected ValueError when no entailment label exists")


# --- NLIAttributionScorer: Reranker protocol contract -----------------------

class _FakeNLI:
    """Stands in for the cross-encoder: maps context text -> 3 class logits."""

    id2label = {0: "contradiction", 1: "entailment", 2: "neutral"}

    def __init__(self, logits_by_text):
        self._m = logits_by_text

    def predict(self, pairs, batch_size=32, **kw):
        # pairs are [premise(context), hypothesis(answer)]
        return [self._m[premise] for premise, _ in pairs]


def _scorer(logits_by_text):
    return NLIAttributionScorer.from_model(_FakeNLI(logits_by_text))


def test_scores_by_entailment_probability_and_sorts_descending():
    ctx = [_chunk("A", "a"), _chunk("B", "b"), _chunk("C", "c")]
    # B entails most strongly, then A, then C.
    s = _scorer({"a": [0.0, 2.0, 0.0], "b": [0.0, 5.0, 0.0], "c": [0.0, -3.0, 0.0]})
    out = s.rerank("the answer", ctx)
    assert [c.id for c, _ in out] == ["B", "A", "C"]


def test_scores_are_probabilities_in_unit_interval():
    """select_citations compares scores against a sigmoid-scale margin, so an
    unbounded logit would make the margin meaningless."""
    ctx = [_chunk("A", "a"), _chunk("B", "b")]
    s = _scorer({"a": [0.0, 9.0, 0.0], "b": [0.0, -9.0, 0.0]})
    for _, score in s.rerank("ans", ctx):
        assert 0.0 <= score <= 1.0


def test_contradiction_scores_below_entailment_for_same_logit_magnitude():
    ctx = [_chunk("A", "a"), _chunk("B", "b")]
    # A: strong contradiction. B: strong entailment.
    s = _scorer({"a": [5.0, 0.0, 0.0], "b": [0.0, 5.0, 0.0]})
    out = dict((c.id, v) for c, v in s.rerank("ans", ctx))
    assert out["B"] > out["A"]


def test_empty_candidates_returns_empty():
    assert _scorer({}).rerank("ans", []) == []
