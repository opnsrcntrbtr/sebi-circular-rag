# As-of Confidence Intervals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Report as-of pipeline accuracy with a Clopper-Pearson exact confidence interval, and persist per-case run artifacts so future as-of comparisons need no model loads.

**Architecture:** Add a binomial-proportion estimator to the existing `stats.py` (which already holds the recall@10 bootstrap), make `eval_asof.summarize()` emit CI keys additively, and give `scripts/eval_asof.py` the same persistence + fingerprint metadata that `scripts/bench_retrieval.py` already writes.

**Tech Stack:** Python 3.12, pytest, scipy (`scipy.stats.beta`), numpy.

**Spec:** `docs/superpowers/specs/2026-07-21-asof-confidence-intervals-design.md`

## Global Constraints

- Python `>=3.12,<3.13`; the repo venv is `.venv/`, driven by the Makefile.
- All new tests are offline — no model weights, no network, no `integration` marker.
- Run tests with the Makefile env: `PYTHONPATH=src .venv/bin/python -m pytest`.
- `tests/test_eval_asof.py::test_summarize_reports_accuracy_and_failures` must pass **unmodified**. Changes to `summarize()` are additive only; `n`, `passed`, `accuracy`, `failures` keep their exact current meaning.
- The stdout JSON print in `scripts/eval_asof.py` is preserved — existing consumers must keep working.
- Clopper-Pearson exact is the estimator for binary pass/fail proportions. Do not substitute Wilson or bootstrap.
- Reference values (95%, verified): 9/10 → `[0.554984, 0.997471]`; 12/13 → `[0.639703, 0.998054]`; 3/3 → `[0.292402, 1.0]`; 0/5 → `[0.0, 0.521824]`.

## File Structure

| File | Responsibility | Change |
|---|---|---|
| `pyproject.toml` | dependency declaration | Modify — add `numpy`, `scipy` |
| `src/sebi_rag/stats.py` | uncertainty estimators | Modify — add `ProportionCI`, `clopper_pearson_ci` |
| `src/sebi_rag/eval_asof.py` | as-of case runners + summary | Modify — `summarize()` gains CI keys |
| `scripts/eval_asof.py` | as-of run entry point | Modify — persist `results.json` |
| `tests/test_stats.py` | estimator tests | Modify — add `TestClopperPearson` |
| `tests/test_eval_asof.py` | as-of harness tests | Modify — add CI-key tests (existing test untouched) |
| `tests/test_asof_persistence.py` | run-artifact shape | Create |

---

### Task 1: Clopper-Pearson estimator

**Files:**
- Modify: `pyproject.toml:6-20` (dependencies list)
- Modify: `src/sebi_rag/stats.py` (add dataclass + function)
- Test: `tests/test_stats.py` (append new class)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `ProportionCI(point: float, lo: float, hi: float, n: int, successes: int, confidence: float, method: str)` and `clopper_pearson_ci(successes: int, n: int, *, confidence: float = 0.95) -> ProportionCI`. Task 2 imports both.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_stats.py`:

```python
from sebi_rag.stats import ProportionCI, clopper_pearson_ci


class TestClopperPearson:
    def test_known_interval_for_nine_of_ten(self):
        ci = clopper_pearson_ci(9, 10)
        assert ci.point == pytest.approx(0.9)
        assert ci.lo == pytest.approx(0.554984, abs=1e-5)
        assert ci.hi == pytest.approx(0.997471, abs=1e-5)
        assert ci.method == "clopper-pearson"

    def test_known_interval_for_twelve_of_thirteen(self):
        ci = clopper_pearson_ci(12, 13)
        assert ci.lo == pytest.approx(0.639703, abs=1e-5)
        assert ci.hi == pytest.approx(0.998054, abs=1e-5)

    def test_all_successes_pins_upper_bound_at_one(self):
        # The Beta quantile is undefined at k == n; must be pinned explicitly.
        ci = clopper_pearson_ci(3, 3)
        assert ci.hi == 1.0
        assert ci.lo == pytest.approx(0.292402, abs=1e-5)

    def test_zero_successes_pins_lower_bound_at_zero(self):
        ci = clopper_pearson_ci(0, 5)
        assert ci.lo == 0.0
        assert ci.hi == pytest.approx(0.521824, abs=1e-5)

    def test_empty_sample_gives_vacuous_interval(self):
        # An as-of run with no cases in a mode must not crash the run.
        ci = clopper_pearson_ci(0, 0)
        assert (ci.lo, ci.hi) == (0.0, 1.0)
        assert ci.point == 0.0

    def test_interval_brackets_the_point_estimate(self):
        ci = clopper_pearson_ci(7, 10)
        assert ci.lo <= ci.point <= ci.hi

    def test_higher_confidence_widens_the_interval(self):
        narrow = clopper_pearson_ci(9, 10, confidence=0.80)
        wide = clopper_pearson_ci(9, 10, confidence=0.99)
        assert wide.hi - wide.lo > narrow.hi - narrow.lo

    def test_is_wider_than_the_bootstrap_on_the_same_binary_data(self):
        """The reason for the switch: the percentile bootstrap cannot exceed
        the observed maximum, so it under-covers on binary outcomes."""
        values = [1.0] * 9 + [0.0]
        boot = bootstrap_ci(values, n_resamples=4000, seed=0)
        exact = clopper_pearson_ci(9, 10)
        assert exact.lo < boot.lo
        assert exact.hi > boot.hi

    def test_rejects_more_successes_than_trials(self):
        with pytest.raises(ValueError):
            clopper_pearson_ci(11, 10)

    def test_rejects_negative_inputs(self):
        with pytest.raises(ValueError):
            clopper_pearson_ci(-1, 10)
        with pytest.raises(ValueError):
            clopper_pearson_ci(1, -10)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_stats.py -q`
Expected: collection error — `ImportError: cannot import name 'ProportionCI'`.

- [ ] **Step 3: Declare numpy and scipy**

In `pyproject.toml`, the `[project] dependencies` list currently ends with `"httpx>=0.28.1",`. Add two entries after `"bm25s>=0.3.9",`:

```toml
    "bm25s>=0.3.9",
    "numpy>=2.0",
    "scipy>=1.14",
```

Both are imported directly by `stats.py` but arrive only transitively via torch and sentence-transformers today.

- [ ] **Step 4: Implement the estimator**

In `src/sebi_rag/stats.py`, add the scipy import beside the numpy one:

```python
import numpy as np
from scipy.stats import beta
```

Append after `bootstrap_ci`:

```python
@dataclass(frozen=True)
class ProportionCI:
    point: float          # successes / n
    lo: float
    hi: float
    n: int
    successes: int
    confidence: float
    method: str


def clopper_pearson_ci(
    successes: int,
    n: int,
    *,
    confidence: float = 0.95,
) -> ProportionCI:
    """Clopper-Pearson exact interval for a binomial proportion.

    Use this for strictly binary pass/fail outcomes — as-of case results, for
    instance. `bootstrap_ci` is the wrong tool there: a percentile bootstrap
    can never return a bound above the observed maximum, so at 12/13 it pins
    the upper bound at 100% and under-covers. Clopper-Pearson inverts the
    exact binomial test and guarantees at least nominal coverage, at the cost
    of being conservative (intervals slightly too wide).

    n == 0 yields the vacuous [0, 1] rather than raising, so a mode with no
    cases does not abort a run.
    """
    if successes < 0 or n < 0:
        raise ValueError(f"negative counts: successes={successes}, n={n}")
    if successes > n:
        raise ValueError(f"successes={successes} exceeds n={n}")
    if n == 0:
        return ProportionCI(point=0.0, lo=0.0, hi=1.0, n=0, successes=0,
                            confidence=confidence, method="clopper-pearson")

    tail = (1.0 - confidence) / 2.0
    # The Beta quantile is undefined at the boundaries, so pin them.
    lo = 0.0 if successes == 0 else float(beta.ppf(tail, successes, n - successes + 1))
    hi = 1.0 if successes == n else float(
        beta.ppf(1.0 - tail, successes + 1, n - successes))
    return ProportionCI(
        point=successes / n, lo=lo, hi=hi, n=n, successes=successes,
        confidence=confidence, method="clopper-pearson",
    )
```

- [ ] **Step 5: Extend the module docstring**

In `src/sebi_rag/stats.py`, the docstring bullet list currently ends with the `paired_delta` bullet. Add a third bullet after it:

```
- `clopper_pearson_ci`: exact interval for a binomial proportion. Reach for
  this when outcomes are strictly binary pass/fail (the as-of cases) and for
  the bootstrap when per-query scores are continuous or mixed-valued
  (recall@10, where multi-circular queries score fractionally).
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_stats.py -q`
Expected: PASS, 24 tests (14 existing + 10 new).

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml src/sebi_rag/stats.py tests/test_stats.py
git commit -m "stats: Clopper-Pearson exact interval for binary proportions"
```

---

### Task 2: `summarize()` emits CI keys

**Files:**
- Modify: `src/sebi_rag/eval_asof.py:74-82`
- Test: `tests/test_eval_asof.py` (append; do not modify the existing test)

**Interfaces:**
- Consumes: `clopper_pearson_ci` from Task 1.
- Produces: `summarize(results) -> dict` with keys `n`, `passed`, `accuracy`, `failures` (unchanged) plus `ci_lo: float`, `ci_hi: float`, `ci_method: str`. Task 3 consumes this dict.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_eval_asof.py`:

```python
def test_summarize_reports_a_clopper_pearson_interval():
    from sebi_rag.eval_asof import AsofCaseResult
    results = [
        AsofCaseResult(id=f"p{i}", mode="pipeline", passed=True, detail="")
        for i in range(9)
    ] + [AsofCaseResult(id="p9", mode="pipeline", passed=False, detail="")]
    summary = summarize(results)
    assert summary["accuracy"] == 0.9
    assert summary["ci_lo"] == pytest.approx(0.554984, abs=1e-5)
    assert summary["ci_hi"] == pytest.approx(0.997471, abs=1e-5)
    assert summary["ci_method"] == "clopper-pearson"


def test_summarize_all_pass_pins_upper_bound():
    from sebi_rag.eval_asof import AsofCaseResult
    results = [
        AsofCaseResult(id=f"s{i}", mode="selector", passed=True, detail="")
        for i in range(3)
    ]
    summary = summarize(results)
    assert summary["ci_hi"] == 1.0
    assert summary["ci_lo"] < 1.0


def test_summarize_handles_an_empty_mode():
    summary = summarize([])
    assert summary["n"] == 0
    assert summary["accuracy"] == 0.0
    assert (summary["ci_lo"], summary["ci_hi"]) == (0.0, 1.0)
```

`tests/test_eval_asof.py` does **not** currently import pytest. Add it above the `from pathlib import Path` line:

```python
import pytest
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_eval_asof.py -q`
Expected: FAIL with `KeyError: 'ci_lo'`.

- [ ] **Step 3: Implement**

In `src/sebi_rag/eval_asof.py`, add the import beside the existing ones:

```python
from .stats import clopper_pearson_ci
```

Replace `summarize` (currently lines 74-82) with:

```python
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
```

- [ ] **Step 4: Run the full as-of test file**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_eval_asof.py -q`
Expected: PASS, including the pre-existing `test_summarize_reports_accuracy_and_failures` unmodified.

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/eval_asof.py tests/test_eval_asof.py
git commit -m "eval_asof: report Clopper-Pearson interval on case accuracy"
```

---

### Task 3: Persist the as-of run

**Files:**
- Modify: `scripts/eval_asof.py:58-66` (replace the print block)
- Create: `tests/test_asof_persistence.py`

**Interfaces:**
- Consumes: `summarize()` output from Task 2; `benchmark.run_metadata(...)` (existing, keyword-only: `root`, `corpus_path`, `index_dir`, `golden_path`, `run_name`, `models`, `params`, `started_at`).
- Produces: `sebi_rag.eval_asof.build_report(selector_results, pipeline_results, metadata) -> dict` — the serializable run artifact. Extracted into the module (not the script) so it is testable offline without model loads.

- [ ] **Step 1: Write the failing test**

Create `tests/test_asof_persistence.py`:

```python
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


def test_report_is_json_serializable(tmp_path):
    selector, pipeline = _results()
    report = build_report(selector, pipeline, {"git_commit": "abc"})
    path = tmp_path / "results.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["metrics"]["pipeline"]["passed"] == 9
    assert loaded["cases"][0]["id"] == "asof-p0"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_asof_persistence.py -q`
Expected: collection error — `ImportError: cannot import name 'build_report'`.

- [ ] **Step 3: Implement `build_report`**

Append to `src/sebi_rag/eval_asof.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_asof_persistence.py -q`
Expected: PASS, 3 tests.

- [ ] **Step 5: Wire persistence into the script**

In `scripts/eval_asof.py`, add to the import block near the top (after the `os`/`sys`/`json` imports):

```python
import time
```

Change the `sebi_rag.eval_asof` import (currently lines 29-31) to include `build_report`:

```python
from sebi_rag.eval_asof import (  # noqa: E402
    build_report, load_golden_asof, run_pipeline_cases, run_selector_cases,
)
```

Add after the other `sebi_rag` imports:

```python
from sebi_rag.benchmark import run_metadata  # noqa: E402
```

Add `started = time.time()` immediately before the `s = Settings.load()` line.

Then replace the final `print(json.dumps({...}, indent=2))` block (currently lines 58-66) with:

```python
golden_path = os.environ.get(
    "SEBI_RAG_GOLDEN_ASOF", str(ROOT / "eval" / "golden" / "golden_asof_v1.jsonl"))
run_name = os.environ.get("ASOF_OUT", "baseline")

report = build_report(selector_results, pipeline_results, run_metadata(
    root=ROOT,
    corpus_path=s.corpus_path,
    index_dir=s.index_dir,
    golden_path=golden_path,
    run_name=f"asof-{run_name}",
    models={"embedder": "BAAI/bge-m3",
            "retriever": "FAISS+BM25/RRF",
            "reranker": "BAAI/bge-reranker-v2-m3",
            "generator": "ExtractiveStubGenerator"},
    params={"abstain_threshold": s.abstain_threshold},
    started_at=started,
))

out = ROOT / "eval" / "runs" / f"asof-{run_name}"
out.mkdir(parents=True, exist_ok=True)
(out / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

print(json.dumps({**report["metrics"], "out": str(out)}, indent=2))
```

Note the `cases` list moves out of stdout into the artifact; the per-mode
metrics that were printed before are still printed, under the same
`selector` / `pipeline` / `overall` keys.

The `cases = load_golden_asof(...)` call above must now reuse `golden_path`;
move the `golden_path` assignment above it and change that line to:

```python
cases = load_golden_asof(golden_path)
```

- [ ] **Step 6: Verify the script compiles without running models**

Run: `PYTHONPATH=src .venv/bin/python -c "import ast,pathlib; ast.parse(pathlib.Path('scripts/eval_asof.py').read_text())"`
Expected: no output, exit 0.

- [ ] **Step 7: Run the full offline suite**

Run: `make test`
Expected: PASS, 326 tests (310 existing + 10 Task 1 + 3 Task 2 + 3 Task 3), 2 deselected.

- [ ] **Step 8: Commit**

```bash
git add scripts/eval_asof.py src/sebi_rag/eval_asof.py tests/test_asof_persistence.py
git commit -m "eval_asof: persist per-case run artifact with fingerprint metadata"
```

---

### Task 4: Record the baseline run

**Files:**
- Create: `eval/runs/asof-baseline/results.json` (generated)
- Modify: `CLAUDE.md` (Quick Start command list)

**Interfaces:**
- Consumes: everything from Tasks 1-3.
- Produces: the committed baseline artifact future as-of runs compare against.

This task loads bge-m3 and the cross-encoder on MPS. It takes a few minutes and needs the persisted index at `data/index`.

- [ ] **Step 1: Run the as-of eval for real**

Run: `make eval-asof`
Expected: JSON on stdout with `pipeline`, `selector`, `overall`, and `out`. The `pipeline` block should carry `ci_lo` ≈ 0.55 and `ci_hi` ≈ 0.997 if the result is still 9/10.

If the pass counts differ from 9/10 and 3/3, that is a real change in the
system since 2026-07-12 — record the actual numbers, do not adjust the code
to reproduce the old ones.

- [ ] **Step 2: Confirm the artifact landed**

Run: `PYTHONPATH=src .venv/bin/python -c "import json; d=json.load(open('eval/runs/asof-baseline/results.json')); print(d['metrics']['pipeline']); print(len(d['cases']), 'cases'); print(sorted(d['metadata'])[:6])"`
Expected: the pipeline metrics dict, `13 cases`, and metadata keys including `corpus_sha256`, `git_commit`, `golden_sha256`, `index_fingerprint`.

- [ ] **Step 3: Document the target**

In `CLAUDE.md`, the Quick Start block has the line:

```
make eval-asof # As-of-date golden eval (selector + pipeline cases)
```

Replace it with:

```
make eval-asof # As-of-date golden eval; writes eval/runs/asof-$ASOF_OUT (default: baseline)
```

- [ ] **Step 4: Commit**

```bash
git add eval/runs/asof-baseline/results.json CLAUDE.md
git commit -m "eval: record as-of baseline run with confidence intervals"
```

---

## Self-Review

**Spec coverage:**
- §1 estimator → Task 1
- §2 additive `summarize()` → Task 2
- §3 persistence + metadata → Task 3
- §4 declare numpy/scipy → Task 1 Step 3
- Testing section → Tasks 1, 2, 3 (all listed cases covered; the
  "wider than bootstrap" check is Task 1 Step 1)
- Success criteria 1-4 → Tasks 1-4; criterion 5 (paper can state the
  interval) is satisfied by the Task 4 artifact.

**Type consistency:** `clopper_pearson_ci` returns `ProportionCI` with field
`method`; `summarize()` reads `ci.lo`, `ci.hi`, `ci.method` and emits
`ci_lo`, `ci_hi`, `ci_method`; `build_report` consumes those exact string
keys and pops the same three from the pooled block. `AsofCaseResult` fields
(`id`, `mode`, `passed`, `detail`) match the existing dataclass.

**Known risk:** `run_metadata` requires `golden_path`; the as-of golden file
differs from the retrieval golden, so `golden_sha256` in as-of artifacts
fingerprints `golden_asof_v1.jsonl`, not `golden_v6.jsonl`. This is correct
but means the two run families' `golden_sha256` values are not comparable.
