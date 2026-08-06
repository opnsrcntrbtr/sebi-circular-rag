"""Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):
Cohen's kappa, the promotion truth table, applying decisions to golden rows,
and resolving a flip's winning chunk ids into {doc, quote} spans via pools.
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import golden_v7.agreement as agr  # noqa: E402
from golden_v7.agreement import (  # noqa: E402
    _claude_accuracy_ci,
    _provision_agree,
    _render_report,
    _resolve_governing_spans,
    _stratum_kappas,
    apply,
    cohen_kappa,
    decide,
    gwet_ac1,
)
from sebi_rag.stats import clopper_pearson_ci  # noqa: E402


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


def test_decide_llm_leg_is_annotator_agnostic():
    """The LLM leg is whichever single non-claude/non-human annotator voted -
    "qwen" (the local oMLX leg) must drive the same truth table "gemini"
    does, with no per-name configuration. The Task 12 pivot swaps the leg's
    model family; the promotion rules must not care."""
    row = _row(id="v7-nt-008", task_type="numeric_table")
    assert decide(row, {"claude": ["c1"], "qwen": ["c1"]}, dated_ids=set()) \
        == ("promote", None)
    decision, _ = decide(row, {"claude": ["c1"], "qwen": ["c2"]}, dated_ids=set())
    assert decision == "queue"
    decision, new = decide(row, {"claude": ["c1"], "qwen": ["c2"], "human": ["c2"]},
                           dated_ids=set())
    assert decision == "flip_promote" and set(new) == {"c2"}


def test_decide_same_provision_other_chunk_promotes_with_pool():
    """Amendment 2026-07-26 (user-approved): the promotion unit is the
    PROVISION, not the chunk-id set. Master circulars repeat the same clause
    across body/annexure/FAQ chunks, and the harness itself already grades
    every quote-containing chunk as gold (resolve_chunk_spans: all overlap
    matches count) - measured on the pilot, exact-set agreement was ~10%
    while provision-level was ~60% for BOTH model families. An external
    picking a different chunk copy of claude's quoted provision confirms
    the label."""
    quote = "the upfront margin shall be collected at the rate of twenty per cent"
    row = _row(id="v7-nt-020", task_type="numeric_table",
               relevant_chunks=[{"doc": "C/1", "quote": quote}])
    pool = _pool("v7-nt-020", [
        {"chunk_id": "c1", "doc": "C/1", "text": f"C/1 | S | X\nIntro. {quote}."},
        {"chunk_id": "c9", "doc": "C/1", "text": f"C/1 | S | Annexure\nAs stated, {quote} in all cases."},
        {"chunk_id": "c5", "doc": "C/1", "text": "C/1 | S | Y\nUnrelated fee provisions apply."},
    ])
    votes = {"claude": ["c1"], "qwen": ["c9"]}
    assert decide(row, votes, dated_ids=set(), pool=pool) == ("promote", None)


def test_decide_different_provision_with_pool_still_queues():
    row = _row(id="v7-nt-021", task_type="numeric_table",
               relevant_chunks=[{"doc": "C/1", "quote": "x" * 50}])
    pool = _pool("v7-nt-021", [
        {"chunk_id": "c1", "doc": "C/1", "text": "C/1 | S | X\n" + "x" * 50},
        {"chunk_id": "c5", "doc": "C/1", "text": "C/1 | S | Y\nsomething else entirely here"},
    ])
    decision, _ = decide(row, {"claude": ["c1"], "qwen": ["c5"]},
                         dated_ids=set(), pool=pool)
    assert decision == "queue"


def test_decide_superset_confirms_without_pool():
    """External marked claude's chunk governing plus extras: claude's label
    is confirmed by containment alone - no pool lookup needed."""
    row = _row(id="v7-nt-022", task_type="numeric_table")
    assert decide(row, {"claude": ["c1"], "qwen": ["c1", "c2"]},
                  dated_ids=set()) == ("promote", None)


def test_decide_abstain_dispute_via_literal_queues():
    """The abstain protocol can never emit non-empty governing (no letters
    are offered) - its ONLY dispute signal is a non-blank expected_literal.
    Without the literals param this dispute was invisible and a disputed
    abstain auto-promoted."""
    row = _row(id="v7-hn-020", task_type="hard_negative", abstain=True,
               relevant_circulars=[], relevant_chunks=[], must_contain=[],
               must_not_cite=[], expected_citation_level="none")
    votes = {"qwen": [], "human": []}
    literals = {"qwen": "SEBI LODR Reg 30 covers this", "human": ""}
    decision, _ = decide(row, votes, dated_ids=set(), literals=literals)
    assert decision == "queue"
    # both blank -> genuine three-way confirm-abstain -> promote
    assert decide(row, votes, dated_ids=set(),
                  literals={"qwen": "", "human": ""}) == ("promote", None)


def test_decide_never_flips_answerable_row_to_empty():
    """Two externals both replying NONE on an answerable row must queue,
    not flip: a flip writes their shared set into relevant_chunks, and an
    empty relevant_chunks on a non-abstain row is not a valid label - it
    is an arbitration case."""
    row = _row(id="v7-nt-023", task_type="numeric_table")
    decision, _ = decide(row, {"claude": ["c1"], "qwen": [], "human": []},
                         dated_ids=set())
    assert decision == "queue"


def test_decide_two_llm_annotators_fails_loud():
    """One external-LLM leg at a time: two would make "the LLM vote"
    ambiguous, and silently preferring either would corrupt the agreement
    stats. Mixed legs must be an error, never a guess."""
    row = _row(id="v7-nt-009", task_type="numeric_table")
    try:
        decide(row, {"claude": ["c1"], "gemini": ["c1"], "qwen": ["c1"]},
               dated_ids=set())
        assert False, "expected ValueError"
    except ValueError as e:
        assert "gemini" in str(e) and "qwen" in str(e)


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


# ---------------------------------------------------------------------------
# (e) gwet_ac1 - prevalence-robust agreement (fixes the kappa base-rate paradox)
# ---------------------------------------------------------------------------

def test_gwet_ac1_identical_lists_is_one():
    a = [["c1"], [], ["c2", "c3"], ["c1"]]
    assert gwet_ac1(a, a) == 1.0


def test_gwet_ac1_empty_input_is_one():
    assert gwet_ac1([], []) == 1.0


def test_gwet_ac1_both_constant_and_identical_is_one():
    a = [["c1"], ["c1"], ["c1"]]
    assert gwet_ac1(a, a) == 1.0


def test_gwet_ac1_exceeds_kappa_on_skewed_high_agreement():
    """The kappa base-rate paradox: one label dominates, raw agreement is high,
    yet Cohen's kappa collapses because chance agreement is inflated. Gwet's
    AC1 does not over-correct for prevalence, so it stays high - this is why
    numeric_table (heavily skewed) read kappa~0 despite real agreement."""
    a = [["c1"]] * 8 + [[], ["c2"]]
    b = [["c1"]] * 8 + [["c2"], []]
    k = cohen_kappa(a, b)
    ac1 = gwet_ac1(a, b)
    assert ac1 > k
    assert ac1 > 0.7          # tracks the 0.8 raw agreement
    assert k < 0.5            # kappa understates it


# ---------------------------------------------------------------------------
# (f) _provision_agree - symmetric provision-level match (reuses _confirms_claude)
# ---------------------------------------------------------------------------

def test_provision_agree_both_empty_is_true():
    assert _provision_agree(frozenset(), frozenset(), None, None) is True


def test_provision_agree_containment_either_direction():
    # superset in either slot confirms the shared provision
    assert _provision_agree(frozenset({"c1"}), frozenset({"c1", "c2"}), None, None) is True
    assert _provision_agree(frozenset({"c1", "c2"}), frozenset({"c1"}), None, None) is True


def test_provision_agree_disjoint_without_pool_is_false():
    assert _provision_agree(frozenset({"c1"}), frozenset({"c2"}), None, None) is False


def test_provision_agree_empty_vs_nonempty_is_false():
    assert _provision_agree(frozenset(), frozenset({"c1"}), None, None) is False


def test_provision_agree_same_provision_other_chunk_via_pool():
    """Different chunk copies of the same quoted provision agree at provision
    level even though the exact chunk-id sets differ."""
    quote = "the upfront margin shall be collected at the rate of twenty per cent"
    row = _row(id="v7-nt-020", task_type="numeric_table",
               relevant_chunks=[{"doc": "C/1", "quote": quote}])
    pool = _pool("v7-nt-020", [
        {"chunk_id": "c1", "doc": "C/1", "text": f"C/1 | S | X\nIntro. {quote}."},
        {"chunk_id": "c9", "doc": "C/1", "text": f"C/1 | S | Annexure\nAs stated, {quote} in all cases."},
    ])
    assert _provision_agree(frozenset({"c1"}), frozenset({"c9"}), row, pool) is True


# ---------------------------------------------------------------------------
# (g) _stratum_kappas / _claude_accuracy_ci - provision-level + AC1 reporting
# ---------------------------------------------------------------------------

def _same_provision_fixture():
    quote = "the upfront margin shall be collected at the rate of twenty per cent"
    rid = "v7-nt-020"
    rows_by_id = {rid: _row(id=rid, task_type="numeric_table",
                            relevant_chunks=[{"doc": "C/1", "quote": quote}])}
    votes_by_row = {rid: {"claude": ["c1"], "qwen": ["c9"]}}
    pools_by_id = {rid: _pool(rid, [
        {"chunk_id": "c1", "doc": "C/1", "text": f"C/1 | S | X\nIntro. {quote}."},
        {"chunk_id": "c9", "doc": "C/1", "text": f"C/1 | S | Annexure\nAs stated, {quote} in all cases."},
    ])}
    return rows_by_id, votes_by_row, pools_by_id, [rid]


def test_stratum_kappas_adds_ac1_and_provision_agreement():
    rows_by_id, votes_by_row, pools_by_id, ids = _same_provision_fixture()
    out = _stratum_kappas(rows_by_id, votes_by_row, ids, pools_by_id)
    r = next(x for x in out if x["pair"] == ("claude", "qwen"))
    assert "ac1" in r and "provision_agreement" in r
    # exact-set disagrees (c1 vs c9) but they are the same provision
    assert r["raw_agreement"] == 0.0
    assert r["provision_agreement"] == 1.0


def test_claude_accuracy_ci_returns_exact_and_provision():
    rows_by_id, votes_by_row, pools_by_id, ids = _same_provision_fixture()
    exact_ci, prov_ci = _claude_accuracy_ci(rows_by_id, votes_by_row, ids, pools_by_id)
    assert exact_ci.n == prov_ci.n == 1
    assert exact_ci.successes == 0      # exact chunk-id sets differ
    assert prov_ci.successes == 1       # same provision


def test_render_report_includes_ac1_and_provision():
    kappa_rows = [{"stratum": "numeric_table", "pair": ("claude", "qwen"),
                   "n": 1, "kappa": 0.0, "ac1": 1.0,
                   "raw_agreement": 0.0, "provision_agreement": 1.0}]
    md = _render_report(kappa_rows,
                        (clopper_pearson_ci(0, 1), clopper_pearson_ci(1, 1)),
                        Counter())
    assert "AC1" in md
    assert "provision" in md.lower()


# ---------------------------------------------------------------------------
# (h) main(report_only=...) - refresh the report without churning the gate set
# ---------------------------------------------------------------------------

def _min_agreement_fixture(tmp_path, monkeypatch):
    golden = tmp_path / "golden.jsonl"
    golden.write_text(json.dumps(_row(id="v7-nt-001", task_type="numeric_table",
                                       review_status="draft")) + "\n")
    votes = tmp_path / "votes.jsonl"
    votes.write_text(
        json.dumps({"id": "v7-nt-001", "annotator": "claude", "governing": ["c1"]}) + "\n"
        + json.dumps({"id": "v7-nt-001", "annotator": "qwen", "governing": ["c1"]}) + "\n")
    pools = tmp_path / "pools.jsonl"
    pools.write_text(json.dumps({"id": "v7-nt-001", "candidates": [
        {"chunk_id": "c1", "doc": "C/1", "text": "C/1 | S | X\nbody"}]}) + "\n")
    sample = tmp_path / "sample.json"
    sample.write_text(json.dumps({"external": ["v7-nt-001"]}))
    monkeypatch.setattr(agr, "DEFAULT_GOLDEN_PATH", golden)
    monkeypatch.setattr(agr, "DEFAULT_VOTES_PATH", votes)
    monkeypatch.setattr(agr, "DEFAULT_POOLS_PATH", pools)
    monkeypatch.setattr(agr, "DEFAULT_SAMPLE_PATH", sample)
    monkeypatch.setattr(agr, "DEFAULT_QUEUE_PATH", tmp_path / "queue.jsonl")
    monkeypatch.setattr(agr, "DEFAULT_REPORT_PATH", tmp_path / "report.md")
    return golden, tmp_path


def test_main_report_only_does_not_rewrite_golden_or_queue(tmp_path, monkeypatch):
    golden, tmp = _min_agreement_fixture(tmp_path, monkeypatch)
    before = golden.read_text()
    agr.main(report_only=True)
    assert golden.read_text() == before                 # gate set untouched
    assert not (tmp / "queue.jsonl").exists()            # no queue churn
    assert (tmp / "report.md").exists()                  # report still refreshed


def test_main_default_rewrites_golden_and_queue(tmp_path, monkeypatch):
    golden, tmp = _min_agreement_fixture(tmp_path, monkeypatch)
    agr.main()
    assert '"review_status": "adjudicated"' in golden.read_text()  # promoted
    assert (tmp / "queue.jsonl").exists()
