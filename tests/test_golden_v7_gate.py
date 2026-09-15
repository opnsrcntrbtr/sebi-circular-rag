"""Offline tests for the golden-v7 CI gate flip (spec 2026-07-23 sec 8).

The gate is deliberately a two-key lock: golden_v7 becomes the CI reporting
set only when `gate_v7.json` exists AND reports adjudicated_n >= 100. Until
then CI keeps running on frozen golden_v5, so a half-adjudicated v7 can never
silently become the thing that gates merges.
"""
import json
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.derive_thresholds import derive_floors, stack_from_settings  # noqa: E402
from golden_v7.gate_select import (  # noqa: E402
    MIN_ADJUDICATED_N,
    floors_ok,
    select_golden,
    stack_matches,
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
# stack_matches (2026-09-15, docs/superpowers/specs/2026-09-03-gate-stack-fingerprint-prereg.md)
# ---------------------------------------------------------------------------

def _stack(**overrides):
    base = {
        "embed_model": "BAAI/bge-m3",
        "chunker_version": "2026-09-03-toc-long-title-merge",
        "corpus_n": 1490,
        "chunk_n": 83752,
        "generator": "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
        "citation_margin": 0.35,
        "citation_scorer_enabled": True,
        "abstain_threshold": 0.109,
        "production_reranker_model": "jina",
    }
    base.update(overrides)
    return base


def test_stack_matches_returns_empty_when_all_axes_match():
    gate = {"stack": _stack()}
    assert stack_matches(gate, _stack()) == []


def test_stack_matches_reports_mismatched_axis_name():
    gate = {"stack": _stack(chunker_version="2026-09-01-table-row-merge")}
    assert stack_matches(gate, _stack()) == ["chunker_version"]


def test_stack_matches_ignores_production_reranker_model_difference():
    """bge-derived floor vs. jina-running production is the expected steady
    state, not drift - comparing this axis would fire a false alarm on every
    run for as long as production stays on a non-bge reranker."""
    gate = {"stack": _stack(production_reranker_model="bge")}
    assert stack_matches(gate, _stack(production_reranker_model="jina")) == []


def test_stack_matches_treats_missing_stack_key_as_unverifiable():
    """Every gate_v7.json that exists today (including the currently-armed
    one) has no 'stack' key - this must report as unverifiable, not as a
    silent pass."""
    assert stack_matches({"adjudicated_n": 260, "floors": {}}, _stack()) != []


def _settings(**overrides):
    base = dict(embed_model="BAAI/bge-m3", reranker_model="jina",
                abstain_threshold=0.109, citation_margin=0.35,
                citation_scorer_enabled=True, mlx_model="mlx-community/Qwen2.5-1.5B-Instruct-4bit")
    base.update(overrides)
    return types.SimpleNamespace(**base)


def test_stack_from_settings_uses_exact_stack_matches_axis_names():
    """A stack block whose keys don't exactly match _STACK_AXES would make
    stack_matches() silently report every comparable axis as always-mismatched
    (dict.get returns None on both sides only by coincidence) - round-trip
    through stack_matches() against itself is the contract that actually
    matters, not just eyeballing the key names."""
    stack = stack_from_settings(_settings(), chunker_version="2026-09-03-x",
                                 chunk_n=83752, corpus_n=1490)
    assert stack_matches({"stack": stack}, stack) == []


def test_stack_from_settings_records_but_does_not_compare_reranker_split():
    """derivation_reranker is a constant (never read from config); production_
    reranker_model reflects live Settings - both present, only the second is a
    _STACK_AXES member, and it is deliberately excluded from comparison."""
    from golden_v7.gate_select import _STACK_AXES

    stack = stack_from_settings(_settings(reranker_model="jina"),
                                 chunker_version="c", chunk_n=1, corpus_n=1)
    assert stack["derivation_reranker"] == "bge-reranker-v2-m3"
    assert stack["production_reranker_model"] == "jina"
    assert "production_reranker_model" not in _STACK_AXES


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


def test_citation_precision_is_gated_after_B_prime():
    """B' gates citation_precision alongside recall/recall_tradeoff/abstention.
    The filter improves precision but lowers citation_recall; the gate now
    protects both sides of that trade-off so a future regression is caught."""
    floors = derive_floors({"recall": [1.0], "citation_precision": [1.0],
                            "citation_recall": [1.0], "abstention": [1.0]})
    assert "citation_precision" in floors
    assert set(floors) == {"recall_at_k", "citation_recall", "abstention_accuracy",
                           "citation_precision"}


def test_gate_floors_rank_quality_not_only_recall():
    """recall_at_k is ceiling-limited (baseline 0.956 leaves ~9 failing
    queries of 216), so it cannot detect a ranking regression that keeps the
    same documents in the top-10 but reorders them. nDCG@10 has ~30pp of
    headroom on the same runs and must be gated too."""
    floors = derive_floors({"recall": [0.9], "ndcg": [0.7]})
    assert "ndcg_at_10" in floors, "gate cannot see rank quality"


def test_ndcg_floor_catches_a_reordering_regression_recall_misses():
    floors = derive_floors({"recall": [1.0, 1.0], "ndcg": [0.90, 0.90]})
    # Same docs retrieved (recall untouched), but ranked worse.
    report = {"recall_at_k": 1.0, "ndcg_at_10": 0.40}
    assert floors_ok(report, floors) is False


def test_vectors_exposes_ndcg_for_floor_derivation():
    """derive_floors reads its vectors from score.vectors(); a metric absent
    there can never be floored no matter what _GATED_METRICS says."""
    from golden_v7.score import vectors

    recs = [{"adjudicated": True, "recall": 1.0, "ndcg": 0.8,
             "citation_precision": 1.0, "citation_recall": 1.0,
             "abstention": 1.0}]
    assert vectors(recs)["ndcg"] == [0.8]


def test_every_derived_floor_is_emitted_by_the_eval_report():
    """floors_ok fails closed on a metric the report does not carry, so a
    floor name with no matching key in eval_json's gate_report turns the gate
    permanently red. This couples the two sides so adding a gated metric to
    one without the other cannot ship."""
    from golden_v7.derive_thresholds import _FLOOR_NAMES

    src = (Path(__file__).resolve().parents[1] / "scripts" / "eval_json.py"
           ).read_text(encoding="utf-8")
    gate_block = src.split("gate_report = {", 1)[1].split("}", 1)[0]
    for floor_name in _FLOOR_NAMES.values():
        assert f'"{floor_name}"' in gate_block, (
            f"{floor_name} is gated but never reported -> gate fails closed")


def test_eval_json_calls_stack_matches_and_reports_gate_verdict():
    """eval_json.py has no main() and boots real MPS models at import, so it
    cannot be unit-tested directly - same constraint
    test_every_derived_floor_is_emitted_by_the_eval_report already works
    around with a source-text scan. Spec's endpoint #2: eval_json.py's
    reporting path must visibly distinguish verified-pass / verified-fail /
    unverifiable, never collapsing the third into either of the first two -
    this locks that stack_matches() is actually wired in, not just imported."""
    src = (Path(__file__).resolve().parents[1] / "scripts" / "eval_json.py"
           ).read_text(encoding="utf-8")
    assert "stack_matches(" in src
    assert '"gate_verdict"' in src
    assert '"stack_drift"' in src


def test_floor_names_match_the_gate_report_keys():
    """derive_floors emits gate-report metric names, not the internal
    score_row names - floors_ok looks metrics up by these exact keys, and a
    mismatch would silently fail closed on every run."""
    floors = derive_floors({"recall": [0.9], "citation_recall": [0.9],
                            "abstention": [0.9]})
    report = {"recall_at_k": 0.95, "citation_recall": 0.95,
              "abstention_accuracy": 0.95}
    assert floors_ok(report, floors) is True
