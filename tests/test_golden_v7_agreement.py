"""Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):
Cohen's kappa, the promotion truth table, applying decisions to golden rows,
and resolving a flip's winning chunk ids into {doc, quote} spans via pools.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.agreement import (  # noqa: E402
    _resolve_governing_spans,
    apply,
    cohen_kappa,
    decide,
)


def _row(**over):
    base = {
        "id": "v7-ls-001", "query": "q",
        "relevant_circulars": ["C/1"], "relevant_chunks": [],
        "answer_contains": "a", "must_contain": ["a"], "must_not_contain": [],
        "must_not_cite": [], "abstain": False, "as_of": None,
        "task_type": "lineage_supersession", "difficulty": "hard",
        "expected_citation_level": "chunk", "rationale": "r",
        "label_source": "v7-miner-lineage", "review_status": "draft",
    }
    base.update(over)
    return base


def _pool(rid, candidates):
    return {"id": rid, "candidates": candidates}


# ---------------------------------------------------------------------------
# (a) cohen_kappa
# ---------------------------------------------------------------------------

def test_cohen_kappa_identical_lists_is_one():
    a = [["c1"], [], ["c2", "c3"], ["c1"]]
    assert cohen_kappa(a, a) == 1.0


def test_cohen_kappa_independent_looking_lists_is_low():
    a = [["c1"], [], ["c2"], ["c1"], [], ["c2"]]
    b = [[], ["c1"], ["c1"], [], ["c2"], ["c1"]]
    assert cohen_kappa(a, b) < 0.5


def test_cohen_kappa_both_constant_and_identical_is_one():
    a = [["c1"], ["c1"], ["c1"]]
    b = [["c1"], ["c1"], ["c1"]]
    assert cohen_kappa(a, b) == 1.0


def test_cohen_kappa_empty_input_is_one():
    assert cohen_kappa([], []) == 1.0


# ---------------------------------------------------------------------------
# (b) decide() truth table
# ---------------------------------------------------------------------------

def test_decide_gemini_only_agrees_with_claude_promotes():
    row = _row(id="v7-nt-001", task_type="numeric_table")
    votes = {"claude": ["c1"], "gemini": ["c1"]}
    decision, new_governing = decide(row, votes, dated_ids=set())
    assert decision == "promote"
    assert new_governing is None


def test_decide_gemini_only_disagrees_with_claude_queues():
    row = _row(id="v7-nt-002", task_type="numeric_table")
    votes = {"claude": ["c1"], "gemini": ["c2"]}
    decision, _ = decide(row, votes, dated_ids=set())
    assert decision == "queue"


def test_decide_three_way_all_agree_promotes():
    row = _row(id="v7-nt-003", task_type="numeric_table")
    votes = {"claude": ["c1"], "gemini": ["c1"], "human": ["c1"]}
    decision, new_governing = decide(row, votes, dated_ids=set())
    assert decision == "promote"
    assert new_governing is None


def test_decide_three_way_split_queues():
    row = _row(id="v7-nt-004", task_type="numeric_table")
    votes = {"claude": ["c1"], "gemini": ["c2"], "human": ["c3"]}
    decision, _ = decide(row, votes, dated_ids=set())
    assert decision == "queue"


def test_decide_human_and_gemini_agree_on_alternative_flips():
    row = _row(id="v7-nt-005", task_type="numeric_table")
    votes = {"claude": ["c1"], "gemini": ["c2"], "human": ["c2"]}
    decision, new_governing = decide(row, votes, dated_ids=set())
    assert decision == "flip_promote"
    assert set(new_governing) == {"c2"}


def test_decide_dated_id_queues_even_on_full_agreement():
    row = _row(id="v7-ls-006", task_type="lineage_supersession", as_of="2023-05-01")
    votes = {"claude": ["c1"], "gemini": ["c1"], "human": ["c1"]}
    decision, _ = decide(row, votes, dated_ids={"v7-ls-006"})
    assert decision == "queue"


def test_decide_abstain_row_no_claude_vote_externals_confirm_promotes():
    """Abstain rows have no explicit claude vote at all (Task 8 never judged
    them) - claude's implicit label is treated as frozenset() (confirmed
    abstain), consistent with the row's authored abstain:True/relevant_chunks
    == [] state. Both externals independently confirming abstain (governing
    == []) is then just three-way agreement against that implicit label."""
    row = _row(id="v7-hn-001", task_type="hard_negative", abstain=True,
              relevant_circulars=[], relevant_chunks=[], must_contain=[],
              must_not_cite=[], expected_citation_level="none")
    votes = {"gemini": [], "human": []}
    decision, new_governing = decide(row, votes, dated_ids=set())
    assert decision == "promote"
    assert new_governing is None


def test_decide_abstain_row_no_claude_vote_externals_dispute_flips():
    """Both externals independently think something DOES govern (disputing
    the authored abstain) - a genuine disagreement from the implicit
    frozenset() claude label, handled the same as any other flip."""
    row = _row(id="v7-hn-002", task_type="hard_negative", abstain=True,
              relevant_circulars=[], relevant_chunks=[], must_contain=[],
              must_not_cite=[], expected_citation_level="none")
    votes = {"gemini": ["c9"], "human": ["c9"]}
    decision, new_governing = decide(row, votes, dated_ids=set())
    assert decision == "flip_promote"
    assert set(new_governing) == {"c9"}


def test_decide_no_external_votes_queues():
    row = _row(id="v7-nt-007", task_type="numeric_table")
    decision, _ = decide(row, {"claude": ["c1"]}, dated_ids=set())
    assert decision == "queue"


# ---------------------------------------------------------------------------
# (c) apply()
# ---------------------------------------------------------------------------

def test_apply_promote_sets_adjudicated_only():
    rows = [_row(id="v7-nt-001", review_status="draft", relevant_chunks=[{"doc": "C/1", "quote": "x" * 50}])]
    decisions = {"v7-nt-001": ("promote", None)}
    out = apply(rows, decisions)
    assert out[0]["review_status"] == "adjudicated"
    assert out[0]["relevant_chunks"] == [{"doc": "C/1", "quote": "x" * 50}]
    assert out[0]["label_source"] == "v7-miner-lineage"  # untouched


def test_apply_flip_promote_rebuilds_spans_and_label_source():
    rows = [_row(id="v7-nt-002", review_status="draft")]
    new_spans = [{"doc": "C/9", "quote": "y" * 50}]
    decisions = {"v7-nt-002": ("flip_promote", new_spans)}
    out = apply(rows, decisions)
    assert out[0]["review_status"] == "adjudicated"
    assert out[0]["relevant_chunks"] == new_spans
    assert out[0]["label_source"] == "external-flip"


def test_apply_queue_decision_leaves_row_untouched():
    rows = [_row(id="v7-nt-003", review_status="draft")]
    decisions = {"v7-nt-003": ("queue", None)}
    out = apply(rows, decisions)
    assert out[0]["review_status"] == "draft"
    assert out[0]["label_source"] == "v7-miner-lineage"


def test_apply_row_without_a_decision_is_never_touched():
    rows = [_row(id="v7-nt-004", review_status="seeded"),
            _row(id="v7-nt-005", review_status="draft")]
    decisions = {"v7-nt-004": ("promote", None)}
    out = apply(rows, decisions)
    assert out[0]["review_status"] == "adjudicated"
    assert out[1]["review_status"] == "draft"  # no entry in decisions -> untouched


def test_apply_does_not_mutate_input_rows():
    rows = [_row(id="v7-nt-006", review_status="draft")]
    decisions = {"v7-nt-006": ("promote", None)}
    apply(rows, decisions)
    assert rows[0]["review_status"] == "draft"


# ---------------------------------------------------------------------------
# (d) _resolve_governing_spans - chunk id -> {doc, quote} via the row's pool
# ---------------------------------------------------------------------------

def test_resolve_governing_spans_uses_first_60_body_chars():
    body = "The upfront margin shall be collected at the rate of twenty per cent of turnover payable within 30 days."
    pool = _pool("v7-nt-001", [
        {"chunk_id": "C/1#s#0", "doc": "C/1", "text": f"C/1 | Subject | Section\n{body}"},
    ])
    spans = _resolve_governing_spans(["C/1#s#0"], pool)
    assert spans == [{"doc": "C/1", "quote": body[:60]}]


def test_resolve_governing_spans_short_body_uses_whole_body():
    pool = _pool("v7-nt-002", [
        {"chunk_id": "C/2#s#0", "doc": "C/2", "text": "C/2 | Subject | Section\nshort body"},
    ])
    spans = _resolve_governing_spans(["C/2#s#0"], pool)
    assert spans == [{"doc": "C/2", "quote": "short body"}]


def test_resolve_governing_spans_raises_on_chunk_not_in_pool():
    pool = _pool("v7-nt-004", [
        {"chunk_id": "C/4#a#0", "doc": "C/4", "text": "C/4 | S | X\n" + "a" * 70},
    ])
    try:
        _resolve_governing_spans(["C/4#nope#0"], pool)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "C/4#nope#0" in str(e)


def test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order():
    pool = _pool("v7-nt-003", [
        {"chunk_id": "C/3#a#0", "doc": "C/3", "text": "C/3 | S | X\n" + "a" * 70},
        {"chunk_id": "C/3#b#0", "doc": "C/3", "text": "C/3 | S | Y\n" + "b" * 70},
    ])
    spans = _resolve_governing_spans(["C/3#a#0", "C/3#b#0", "C/3#a#0"], pool)
    assert spans == [{"doc": "C/3", "quote": "a" * 60}, {"doc": "C/3", "quote": "b" * 60}]
