"""Offline tests for scripts/finetune/eval_phase0.py - the Phase A
stratified control-vs-treatment comparison that decides the plan's
Phase 0 kill-switch gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from finetune.eval_phase0 import (  # noqa: E402
    GATE_STRATA,
    compare,
    gate_verdict,
    parse_run_doc,
    score_run,
)


def _golden_row(rid, task_type, relevant, abstain=False):
    return {"id": rid, "task_type": task_type,
           "relevant_circulars": relevant, "abstain": abstain}


# ---------------------------------------------------------------------------
# parse_run_doc
# ---------------------------------------------------------------------------

def test_parse_run_doc_orders_by_rank(tmp_path):
    path = tmp_path / "run.doc.trec"
    path.write_text(
        "q1 Q0 DOC_B 2 0.5 run\n"
        "q1 Q0 DOC_A 1 0.9 run\n"
        "q2 Q0 DOC_C 1 0.7 run\n",
        encoding="utf-8")
    result = parse_run_doc(path)
    assert result["q1"] == ["DOC_A", "DOC_B"]
    assert result["q2"] == ["DOC_C"]


def test_parse_run_doc_skips_blank_lines(tmp_path):
    path = tmp_path / "run.doc.trec"
    path.write_text("q1 Q0 DOC_A 1 0.9 run\n\n", encoding="utf-8")
    assert parse_run_doc(path) == {"q1": ["DOC_A"]}


# ---------------------------------------------------------------------------
# score_run
# ---------------------------------------------------------------------------

def test_score_run_excludes_abstain_rows():
    golden = [_golden_row("r1", "t", ["DOC_A"], abstain=True)]
    scored = score_run({"r1": ["DOC_A"]}, golden)
    assert scored == {}


def test_score_run_excludes_rows_with_no_relevant_circulars():
    golden = [_golden_row("r1", "t", [])]
    scored = score_run({"r1": ["DOC_A"]}, golden)
    assert scored == {}


def test_score_run_computes_recall_and_ndcg_for_a_perfect_hit():
    golden = [_golden_row("r1", "numeric_table", ["DOC_A"])]
    scored = score_run({"r1": ["DOC_A", "DOC_B"]}, golden)
    assert scored["r1"]["recall"] == 1.0
    assert scored["r1"]["ndcg"] == 1.0
    assert scored["r1"]["task_type"] == "numeric_table"


def test_score_run_zero_for_a_row_with_no_ranking_at_all():
    """A query id present in golden but missing from the run file (e.g. a
    pipeline error on that row) scores 0, not a KeyError - the row is
    still counted, just as a miss."""
    golden = [_golden_row("r1", "t", ["DOC_A"])]
    scored = score_run({}, golden)
    assert scored["r1"]["recall"] == 0.0


# ---------------------------------------------------------------------------
# compare - the core stratified/subset comparison
# ---------------------------------------------------------------------------

def _holdout(row_split):
    return {"row_split": row_split}


def test_compare_only_uses_ids_present_in_both_control_and_treatment():
    control = {"r1": {"recall": 0.5, "ndcg": 0.5, "task_type": "t"},
              "r2": {"recall": 1.0, "ndcg": 1.0, "task_type": "t"}}
    treatment = {"r1": {"recall": 0.8, "ndcg": 0.8, "task_type": "t"}}
    # r2 missing from treatment -> excluded from the comparison entirely,
    # not silently scored as a treatment-side zero
    result = compare(control, treatment, _holdout({}))
    assert result["overall"]["n"] == 1


def test_compare_computes_delta_as_treatment_minus_control():
    control = {"r1": {"recall": 0.4, "ndcg": 0.4, "task_type": "numeric_table"}}
    treatment = {"r1": {"recall": 0.7, "ndcg": 0.6, "task_type": "numeric_table"}}
    result = compare(control, treatment, _holdout({}))
    assert result["overall"]["delta_recall"] == round(0.7 - 0.4, 4)
    assert result["overall"]["delta_ndcg"] == round(0.6 - 0.4, 4)


def test_compare_groups_by_stratum():
    control = {"r1": {"recall": 0.5, "ndcg": 0.5, "task_type": "numeric_table"},
              "r2": {"recall": 0.5, "ndcg": 0.5, "task_type": "multi_hop"}}
    treatment = {"r1": {"recall": 0.5, "ndcg": 0.5, "task_type": "numeric_table"},
                "r2": {"recall": 0.5, "ndcg": 0.5, "task_type": "multi_hop"}}
    result = compare(control, treatment, _holdout({}))
    assert set(result["by_stratum"]) == {"numeric_table", "multi_hop"}


def test_compare_groups_by_holdout_subset_and_leaves_unclassified_rows_separate():
    control = {"r1": {"recall": 0.5, "ndcg": 0.5, "task_type": "t"},
              "r2": {"recall": 0.5, "ndcg": 0.5, "task_type": "t"}}
    treatment = {"r1": {"recall": 0.5, "ndcg": 0.5, "task_type": "t"},
                "r2": {"recall": 0.5, "ndcg": 0.5, "task_type": "t"}}
    holdout = _holdout({"held_out": ["r1"], "in_corpus": [], "mixed": []})
    result = compare(control, treatment, holdout)
    assert result["by_holdout_subset"]["held_out"]["n"] == 1
    assert result["by_holdout_subset"]["unclassified"]["n"] == 1  # r2


# ---------------------------------------------------------------------------
# gate_verdict - significance-gated (F-04 fix: replaces the OR-of-3
# directional screen that PROCEEDed on a single stratum's positive sign)
# ---------------------------------------------------------------------------

def _rows(task_type, control_vals, treatment_vals):
    """{row_id: {...}} for control/treatment given parallel recall lists.
    Row ids are namespaced by task_type so callers can merge multiple
    strata's dicts without id collisions."""
    control = {f"{task_type}_r{i}": {"recall": v, "ndcg": v, "task_type": task_type}
              for i, v in enumerate(control_vals)}
    treatment = {f"{task_type}_r{i}": {"recall": v, "ndcg": v, "task_type": task_type}
                for i, v in enumerate(treatment_vals)}
    return control, treatment


def test_gate_verdict_proceeds_only_on_a_significant_positive_stratum():
    """A clean, large, consistent lift in one stratum (n=12, treatment
    strictly above control on every row) must clear significance and
    PROCEED - the gate is not required to be uselessly conservative, only
    to require real evidence instead of a bare sign."""
    control, treatment = _rows("multi_hop", [0.2] * 12, [0.9] * 12)
    verdict, by_stratum = gate_verdict(control, treatment)
    assert verdict.startswith("PROCEED")
    assert by_stratum["multi_hop"]["verdict"] == "significant_positive"


def test_gate_verdict_stops_on_a_significant_regression():
    control, treatment = _rows("lineage_supersession", [0.9] * 12, [0.2] * 12)
    verdict, by_stratum = gate_verdict(control, treatment)
    assert verdict.startswith("STOP")
    assert by_stratum["lineage_supersession"]["verdict"] == "significant_negative"


def test_gate_verdict_reports_inconclusive_on_noisy_small_n():
    """This is the exact shape of the original Phase 0 data (n=20-40,
    one or two rows moving): a directional-only screen would PROCEED here;
    the significance-gated version must not - it should report inconclusive
    instead of manufacturing a verdict from noise."""
    control, treatment = _rows(
        "numeric_table",
        [1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0],
        [1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0][:-1] + [1.0],  # 1 row flips
    )
    verdict, by_stratum = gate_verdict(control, treatment)
    assert by_stratum["numeric_table"]["verdict"] == "inconclusive"
    assert verdict.startswith("INCONCLUSIVE")


def test_gate_verdict_stratum_with_too_few_rows_is_insufficient_data_not_a_crash():
    control, treatment = _rows("lineage_supersession", [1.0], [1.0])
    verdict, by_stratum = gate_verdict(control, treatment)
    assert by_stratum["lineage_supersession"]["verdict"] == "insufficient_data"
    assert by_stratum["numeric_table"]["verdict"] == "insufficient_data"
    assert verdict.startswith("INCONCLUSIVE")


def test_gate_verdict_regression_wins_over_a_different_strata_positive():
    """A significant regression in one gate stratum stops the whole gate
    even if another gate stratum is significantly positive - asymmetric by
    design, same spirit as the original screen, now evidence-gated."""
    c1, t1 = _rows("multi_hop", [0.2] * 12, [0.9] * 12)
    c2, t2 = _rows("lineage_supersession", [0.9] * 12, [0.2] * 12)
    verdict, by_stratum = gate_verdict({**c1, **c2}, {**t1, **t2})
    assert verdict.startswith("STOP")
    assert by_stratum["multi_hop"]["verdict"] == "significant_positive"
    assert by_stratum["lineage_supersession"]["verdict"] == "significant_negative"


def test_gate_strata_matches_the_three_named_in_the_plan():
    assert GATE_STRATA == ("numeric_table", "multi_hop", "lineage_supersession")
