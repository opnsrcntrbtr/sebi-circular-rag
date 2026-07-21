"""As-of-date golden evaluation runner (P4b).

Two case modes drawn from eval/golden/golden_asof_v1.jsonl:
- selector: exercises Lineage.governing_on directly against a caller-supplied
  dates dict. Per the 2026-07-12 metadata-migration Fable checkpoint, the
  lineage graph is one ~942-node connected component (master reference-list
  over-tagging), so governing_on is only meaningful when dates is scoped to a
  small, pre-verified family — never the full-corpus dates dict outside these
  regression cases.
- pipeline: exercises RAGPipeline.query(as_of=...) end-to-end; a citation
  match against expected_any (and none against avoid) counts as pass.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .lineage import Lineage
from .pipeline import RAGPipeline
from .stats import clopper_pearson_ci


def load_golden_asof(path: str | Path) -> list[dict]:
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


@dataclass
class AsofCaseResult:
    id: str
    mode: str
    passed: bool
    detail: str


def run_selector_cases(lineage: Lineage, dates: dict[str, str],
                       cases: list[dict]) -> list[AsofCaseResult]:
    out = []
    for c in cases:
        if c["mode"] != "selector":
            continue
        actual = lineage.governing_on(c["entry"], c["as_of"], dates)
        passed = actual == c["expected"]
        out.append(AsofCaseResult(
            id=c["id"], mode="selector", passed=passed,
            detail=f"expected={c['expected']!r} actual={actual!r}",
        ))
    return out


def run_pipeline_cases(pipeline: RAGPipeline, cases: list[dict]) -> list[AsofCaseResult]:
    out = []
    for c in cases:
        if c["mode"] != "pipeline":
            continue
        ans, _ = pipeline.query(c["query"], as_of=c["as_of"])
        cites = ans.citations
        expected_any = c.get("expected_any", [])
        avoid = c.get("avoid", [])
        hit = any(cid.startswith(exp) for cid in cites for exp in expected_any)
        bad = any(cid.startswith(av) for cid in cites for av in avoid)
        passed = hit and not bad
        out.append(AsofCaseResult(
            id=c["id"], mode="pipeline", passed=passed,
            detail=f"citations={cites}",
        ))
    return out


def summarize(results: list[AsofCaseResult]) -> dict:
    """Aggregate case results with an exact confidence interval.

    Pure function of the pass/fail counts, so it computes an interval for
    whatever it is handed. Whether that interval is a *measurement* or a
    regression check is a reporting decision made by the caller — see
    scripts/eval_asof.py, which labels selector cases as regression-only.
    """
    n = len(results)
    n_pass = sum(1 for r in results if r.passed)
    ci = clopper_pearson_ci(n_pass, n)
    return {
        "n": n,
        "passed": n_pass,
        "accuracy": (n_pass / n) if n else 0.0,
        "ci_lo": ci.lo,
        "ci_hi": ci.hi,
        "ci_method": ci.method,
        "failures": [r.id for r in results if not r.passed],
    }


def build_report(
    selector_results: list[AsofCaseResult],
    pipeline_results: list[AsofCaseResult],
    metadata: dict,
) -> dict:
    """Assemble the persisted as-of run artifact.

    Pipeline accuracy is the headline measurement. Selector cases are a
    governing_on unit regression over small pre-verified families (see the
    module docstring) and are tagged as such. The pooled figure is retained
    for continuity with the historical 92.3% but carries no interval, since
    pooling incommensurable modes is not a valid measurement.
    """
    selector = summarize(selector_results)
    selector["role"] = "regression"
    selector["note"] = "governing_on unit check on pre-verified families"

    pooled = summarize(selector_results + pipeline_results)
    for key in ("ci_lo", "ci_hi", "ci_method"):
        pooled.pop(key, None)
    pooled["note"] = "pooled across incommensurable modes; no CI claimed"

    return {
        "metrics": {
            "pipeline": summarize(pipeline_results),
            "selector": selector,
            "overall": pooled,
        },
        "cases": [
            {"id": r.id, "mode": r.mode, "passed": r.passed, "detail": r.detail}
            for r in selector_results + pipeline_results
        ],
        "metadata": metadata,
    }
