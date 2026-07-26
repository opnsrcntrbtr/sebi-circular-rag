"""Offline tests for the golden-v7 CI gate flip (spec 2026-07-23 sec 8).

The gate is deliberately a two-key lock: golden_v7 becomes the CI reporting
set only when `gate_v7.json` exists AND reports adjudicated_n >= 100. Until
then CI keeps running on frozen golden_v5, so a half-adjudicated v7 can never
silently become the thing that gates merges.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.derive_thresholds import derive_floors  # noqa: E402
from golden_v7.gate_select import (  # noqa: E402
    MIN_ADJUDICATED_N,
    floors_ok,
    select_golden,
)

V5 = Path("/eval/golden_v5.jsonl")
V7 = Path("/eval/golden_v7.jsonl")


def _gate_file(tmp_path, **payload):
    p = tmp_path / "gate_v7.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# select_golden
# ---------------------------------------------------------------------------

def test_env_override_wins_over_everything(tmp_path):
    gate = _gate_file(tmp_path, adjudicated_n=250)
    got = select_golden({"SEBI_RAG_GOLDEN": "/custom/set.jsonl"}, gate, V5, V7)
    assert got == Path("/custom/set.jsonl")


def test_armed_gate_selects_v7(tmp_path):
    gate = _gate_file(tmp_path, adjudicated_n=120)
    assert select_golden({}, gate, V5, V7) == V7


def test_exactly_at_threshold_arms(tmp_path):
    gate = _gate_file(tmp_path, adjudicated_n=MIN_ADJUDICATED_N)
    assert select_golden({}, gate, V5, V7) == V7


def test_below_threshold_falls_back_to_v5(tmp_path):
    gate = _gate_file(tmp_path, adjudicated_n=90)
    assert select_golden({}, gate, V5, V7) == V5


def test_missing_gate_file_falls_back_to_v5(tmp_path):
    assert select_golden({}, tmp_path / "nope.json", V5, V7) == V5


def test_malformed_gate_file_falls_back_to_v5(tmp_path):
    """A corrupt gate file must not arm the gate, and must not crash CI
    either - fall back to the frozen set exactly as if it were absent."""
    p = tmp_path / "gate_v7.json"
    p.write_text("{not json", encoding="utf-8")
    assert select_golden({}, p, V5, V7) == V5


def test_gate_file_without_adjudicated_n_falls_back_to_v5(tmp_path):
    assert select_golden({}, _gate_file(tmp_path, floors={}), V5, V7) == V5


# ---------------------------------------------------------------------------
# floors_ok
# ---------------------------------------------------------------------------

def test_floors_ok_when_every_metric_meets_its_floor():
    report = {"recall_at_k": 0.96, "citation_recall": 0.80, "abstention_accuracy": 1.0}
    floors = {"recall_at_k": 0.95, "citation_recall": 0.75}
    assert floors_ok(report, floors) is True


def test_floors_ok_is_inclusive_at_the_boundary():
    assert floors_ok({"recall_at_k": 0.95}, {"recall_at_k": 0.95}) is True


def test_floors_not_ok_when_one_metric_is_below():
    report = {"recall_at_k": 0.96, "citation_recall": 0.70}
    floors = {"recall_at_k": 0.95, "citation_recall": 0.75}
    assert floors_ok(report, floors) is False


def test_missing_metric_fails_closed():
    """A floor naming a metric the report does not carry cannot be shown to
    hold, so the gate must not pass it - a silently-absent metric is exactly
    how a gate degrades into always-green."""
    assert floors_ok({"recall_at_k": 0.99}, {"citation_recall": 0.75}) is False


def test_no_floors_is_vacuously_ok():
    assert floors_ok({"recall_at_k": 0.1}, {}) is True


# ---------------------------------------------------------------------------
# derive_floors
# ---------------------------------------------------------------------------

def test_derived_floor_sits_below_the_observed_mean():
    """The floor is a bootstrap lower bound minus a cushion, never the mean.
    Gating on the mean would fail roughly half of all reruns that changed
    nothing, because resampling noise lands below it about as often as above."""
    values = [1.0] * 90 + [0.0] * 10          # mean 0.90
    floors = derive_floors({"recall": values})
    assert floors["recall_at_k"] < 0.90
    assert floors["recall_at_k"] > 0.75       # but still a meaningful bar


def test_derive_floors_skips_metrics_with_no_scored_queries():
    """A metric nobody scored must not be floored at 0 - a 0 floor is not a
    gate, it is decoration that always passes."""
    floors = derive_floors({"recall": [1.0, 1.0], "citation_recall": []})
    assert "citation_recall" not in floors
    assert "recall_at_k" in floors


def test_derived_floor_never_goes_negative():
    assert derive_floors({"recall": [0.0, 0.0, 0.0]})["recall_at_k"] == 0.0


def test_citation_precision_is_reported_but_never_floored():
    """It trades off against citation_recall, so flooring both pins the
    retriever's operating point and blocks a legitimate precision/recall
    rebalance that leaves overall quality unchanged."""
    floors = derive_floors({"recall": [1.0], "citation_precision": [1.0],
                            "citation_recall": [1.0], "abstention": [1.0]})
    assert "citation_precision" not in floors
    assert set(floors) == {"recall_at_k", "citation_recall", "abstention_accuracy"}


def test_floor_names_match_the_gate_report_keys():
    """derive_floors emits gate-report metric names, not the internal
    score_row names - floors_ok looks metrics up by these exact keys, and a
    mismatch would silently fail closed on every run."""
    floors = derive_floors({"recall": [0.9], "citation_recall": [0.9],
                            "abstention": [0.9]})
    report = {"recall_at_k": 0.95, "citation_recall": 0.95,
              "abstention_accuracy": 0.95}
    assert floors_ok(report, floors) is True
