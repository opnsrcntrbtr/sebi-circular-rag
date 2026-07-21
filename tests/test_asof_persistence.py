"""Shape of the persisted as-of run artifact."""
from __future__ import annotations

import json

from sebi_rag.eval_asof import AsofCaseResult, build_report


def _results():
    pipeline = [
        AsofCaseResult(id=f"asof-p{i}", mode="pipeline", passed=True, detail="c=[]")
        for i in range(9)
    ] + [AsofCaseResult(id="asof-p10", mode="pipeline", passed=False, detail="c=[]")]
    selector = [
        AsofCaseResult(id=f"asof-s{i}", mode="selector", passed=True, detail="ok")
        for i in range(3)
    ]
    return selector, pipeline


def test_report_carries_per_mode_metrics_and_cases():
    selector, pipeline = _results()
    report = build_report(selector, pipeline, {"git_commit": "abc123"})

    assert report["metrics"]["pipeline"]["n"] == 10
    assert report["metrics"]["pipeline"]["ci_method"] == "clopper-pearson"
    assert report["metrics"]["selector"]["role"] == "regression"
    assert report["metadata"]["git_commit"] == "abc123"
    assert len(report["cases"]) == 13
    assert {c["mode"] for c in report["cases"]} == {"pipeline", "selector"}


def test_pooled_overall_carries_no_interval():
    """Pooling a unit regression with an end-to-end metric is not a valid
    measurement; the number is kept for continuity but must not be quotable
    as a headline."""
    selector, pipeline = _results()
    overall = build_report(selector, pipeline, {})["metrics"]["overall"]

    assert overall["n"] == 13
    assert overall["passed"] == 12
    assert "ci_lo" not in overall
    assert "ci_hi" not in overall
    assert "note" in overall


def test_pipeline_metrics_are_not_polluted_by_selector_cases():
    """The headline number must be the 10 pipeline cases alone — the whole
    point of reporting per-mode."""
    selector, pipeline = _results()
    metrics = build_report(selector, pipeline, {})["metrics"]

    assert metrics["pipeline"]["n"] == 10
    assert metrics["pipeline"]["passed"] == 9
    assert metrics["pipeline"]["failures"] == ["asof-p10"]
    assert metrics["selector"]["n"] == 3


def test_report_is_json_serializable(tmp_path):
    selector, pipeline = _results()
    report = build_report(selector, pipeline, {"git_commit": "abc"})
    path = tmp_path / "results.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["metrics"]["pipeline"]["passed"] == 9
    assert loaded["cases"][0]["id"] == "asof-s0"
