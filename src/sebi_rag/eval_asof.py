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
    n = len(results)
    n_pass = sum(1 for r in results if r.passed)
    return {
        "n": n,
        "passed": n_pass,
        "accuracy": (n_pass / n) if n else 0.0,
        "failures": [r.id for r in results if not r.passed],
    }
