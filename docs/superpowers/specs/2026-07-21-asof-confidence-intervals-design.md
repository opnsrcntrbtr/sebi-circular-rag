# As-of accuracy confidence intervals

**Date:** 2026-07-21
**Status:** approved
**Depends on:** `src/sebi_rag/stats.py` (commit 5f462de)

## Problem

`make eval-asof` reports as-of accuracy as a bare point estimate — most
recently 12/13 = 92.3%. The temporal-validity work is the intended headline
contribution of the resource/dataset-track paper, so this is the number a
reviewer will interrogate first, and it currently carries no uncertainty.

The 2026-07-21 re-scoring of the retrieval benchmark
(`reports/ci_rescore.md`) established that the iv-series verdicts are
unpowered at n=45. The as-of set is n=13. The same objection lands harder
here, and it is better to state the interval ourselves than to have it
supplied by a reviewer.

A second, smaller problem: `scripts/eval_asof.py` prints to stdout and
persists nothing. Unlike `bench_retrieval`, there is no frozen artifact, so
any future comparison of an as-of change against a baseline requires two live
runs with bge-m3 and the cross-encoder loaded on MPS.

## What this produces

```
pipeline   9/10  =  90.0%   CP95 [55.5, 99.7]
selector   3/3   = 100.0%   CP95 [29.2, 100.0]   (regression check)
pooled    12/13  =  92.3%   reported without CI
```

The headline as-of accuracy cannot be distinguished from ~56% at n=10. That
is the honest state of the claim. Publishing it converts an unqualified
92.3% into a defensible statement plus a concrete sample-size target, and it
is the finding this work exists to surface — not a reason to withhold it.

## Decisions

**Estimator: Clopper-Pearson exact.** As-of outcomes are strictly binary
pass/fail. The percentile bootstrap in `stats.bootstrap_ci` is a poor
estimator for a small-sample binomial proportion: it can never return a bound
above the observed maximum, so at 12/13 it pins the upper bound at 100% and
under-covers. Clopper-Pearson guarantees at least nominal coverage. It is
wider than Wilson — conservative rather than anti-conservative — which is the
right trade for the one number under scrutiny. `bootstrap_ci` remains the
tool for recall@10, where per-query values are not strictly binary.

**Reporting scope: per-mode, pipeline is the headline.** The 13 cases split
into 10 pipeline cases (end-to-end `RAGPipeline.query(as_of=...)` citation
match) and 3 selector cases. The `eval_asof` module docstring already states
that selector cases are regression tests only — `governing_on` is meaningful
just for small pre-verified families, because the lineage graph is one
~942-node connected component from master reference-list over-tagging.
Pooling a unit regression with an end-to-end metric is a category error.
Pipeline accuracy is the paper's number; selector is reported as regression
status.

**Persist per-case outcomes; no comparison flag yet.** Persistence is what
makes any future A/B possible without re-running models. A `--compare` flag
is deferred: `paired_delta` already handles binary outcomes correctly (its
sign-flip randomization on ±1 differences *is* the exact McNemar test), so
wiring it up is cheap once a second as-of run exists. There is nothing to
compare against today.

## Design

### 1. `stats.py` — proportion estimator

Add `ProportionCI(point, lo, hi, n, successes, confidence, method)` and:

```python
def clopper_pearson_ci(successes: int, n: int, *,
                       confidence: float = 0.95) -> ProportionCI
```

Exact Beta-quantile inversion via `scipy.stats.beta`:

- `lo = Beta(k, n-k+1).ppf(alpha/2)`, pinned to `0.0` when `k == 0`
- `hi = Beta(k+1, n-k).ppf(1-alpha/2)`, pinned to `1.0` when `k == n`

Both boundary pins are required — the Beta quantile is undefined there.
`n == 0` returns the vacuous `[0.0, 1.0]` rather than raising, so an empty
mode does not crash a run. `successes > n` or negative inputs raise
`ValueError`.

The module docstring gains a line on which estimator to reach for: bootstrap
for continuous or mixed-valued per-query scores, Clopper-Pearson for binary
pass/fail proportions.

### 2. `eval_asof.summarize()` — additive only

Existing keys (`n`, `passed`, `accuracy`, `failures`) keep their exact
current meaning and values. `tests/test_eval_asof.py::test_summarize_reports_accuracy_and_failures`
pins them and is not modified.

Adds `ci_lo`, `ci_hi`, `ci_method: "clopper-pearson"`. `summarize()` stays a
pure function of counts and computes an interval for whatever it is handed;
the measurement-vs-regression distinction is a reporting concern, handled in
the script.

### 3. `scripts/eval_asof.py` — persist a run

Writes `eval/runs/asof-<name>/results.json` (default name `baseline`,
override with the `ASOF_OUT` environment variable):

```json
{
  "metrics": {
    "pipeline": {"n": 10, "passed": 9, "accuracy": 0.9,
                 "ci_lo": 0.555, "ci_hi": 0.997,
                 "ci_method": "clopper-pearson", "failures": ["asof-p5"]},
    "selector": {"...": "...", "role": "regression",
                 "note": "governing_on unit check on pre-verified families"},
    "overall":  {"n": 13, "passed": 12, "accuracy": 0.923,
                 "note": "pooled across incommensurable modes; no CI claimed"}
  },
  "cases": [{"id": "asof-p1", "mode": "pipeline", "passed": true, "detail": "..."}],
  "metadata": { "corpus_sha256": "...", "index_fingerprint": "...",
                "golden_sha256": "...", "git_commit": "...", "...": "..." }
}
```

`overall` is retained for continuity with the historical 92.3% but carries no
CI, so the pooled number stays available without being quotable as a
headline. Metadata comes from `benchmark.run_metadata(...)`, giving as-of
runs the same fingerprints `bench_retrieval` records so two runs can be
checked for comparability before being compared.

The existing stdout JSON print is preserved, so anything reading it today
keeps working.

### 4. `pyproject.toml` — declare numpy and scipy

Both are imported directly (`numpy` by `stats.py` since 5f462de, `scipy` as
of this change) but arrive only transitively via torch and
sentence-transformers. A resolution change on `uv sync` could break the eval
harness with no warning. Move both into `[project] dependencies`.

## Testing

All offline. No model loads, no `integration` marker.

`clopper_pearson_ci`:
- known values against published tables: 9/10 → [0.5550, 0.9975],
  12/13 → [0.6397, 0.9981], 3/3 → [0.2924, 1.0]
- `k == 0` → `lo == 0.0`; `k == n` → `hi == 1.0`
- `n == 0` → `[0.0, 1.0]`
- interval brackets the point estimate
- higher confidence widens the interval
- invalid inputs (`successes > n`, negatives) raise `ValueError`
- wider than the bootstrap interval on the same binary data (the reason for
  the switch)

`summarize()`:
- the existing accuracy/failures test stays green unmodified
- CI keys present with `ci_method == "clopper-pearson"`
- an all-pass mode yields `ci_hi == 1.0` and `ci_lo < 1.0`
- a 0-case mode yields the vacuous interval and does not raise

Persistence:
- `tmp_path` round-trip: written JSON parses, contains all three metric
  blocks, the full per-case list, and the metadata fingerprint keys
- `overall` block carries no `ci_lo`/`ci_hi`

## Out of scope

- Expanding the as-of golden set beyond 13 cases (deferred; this spec
  quantifies the need for it)
- Re-running the pipeline to refresh 12/13 — whatever the current run
  produces gets persisted
- Any change to the recall@10 bootstrap path
- Human adjudication of as-of labels
- A `--compare` flag (see Decisions)

## Success criteria

1. `make eval-asof` prints and persists per-mode Clopper-Pearson intervals.
2. `eval/runs/asof-baseline/results.json` exists with per-case outcomes and
   run metadata; a future run is comparable without loading a model.
3. The existing `test_eval_asof.py` suite passes unmodified.
4. `numpy` and `scipy` are declared dependencies.
5. The paper can state as-of pipeline accuracy with an interval and cite a
   sample-size target for closing it.
