"""Uncertainty quantification for benchmark runs.

The golden set is n=56 answerable-or-abstain items, so a single query is worth
~1.8 recall points. Point-estimate deltas between intervention runs at that
scale are not interpretable on their own — the iv-series gate verdicts each
rest on one or two queries changing. Two standard IR tools close that gap:

- `bootstrap_ci`: percentile bootstrap over per-query scores, for the
  uncertainty of a single run's mean.
- `paired_delta`: comparison of two runs scored on the same queries, reporting
  the mean difference with a paired bootstrap interval and a two-sided Fisher
  randomization (permutation) p-value — the significance test recommended for
  IR run comparison by Smucker, Allan & Carterette (CIKM 2007), which pairs on
  the query and makes no distributional assumption.
- `clopper_pearson_ci`: exact interval for a binomial proportion. Reach for
  this when outcomes are strictly binary pass/fail (the as-of cases) and for
  the bootstrap when per-query scores are continuous or mixed-valued
  (recall@10, where multi-circular queries score fractionally).

Every function takes an explicit seed and is deterministic given one.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.stats import beta


@dataclass(frozen=True)
class BootstrapCI:
    point: float          # observed mean
    lo: float             # lower percentile bound
    hi: float             # upper percentile bound
    n: int                # queries the mean is over
    confidence: float
    n_resamples: int


@dataclass(frozen=True)
class PairedResult:
    n: int                # queries scored by BOTH runs
    mean_a: float
    mean_b: float
    delta: float          # mean_b - mean_a
    ci_lo: float
    ci_hi: float
    p_value: float        # two-sided randomization test
    confidence: float
    n_resamples: int
    query_ids: list[str] = field(default_factory=list)

    @property
    def significant(self) -> bool:
        """True when the randomization test rejects at 1 - confidence AND the
        paired interval excludes zero. Both must agree before a verdict is
        reported as a real effect."""
        alpha = 1.0 - self.confidence
        return self.p_value < alpha and (self.ci_lo > 0.0 or self.ci_hi < 0.0)


def bootstrap_ci(
    values: list[float],
    *,
    confidence: float = 0.95,
    n_resamples: int = 10000,
    seed: int = 0,
) -> BootstrapCI:
    """Percentile bootstrap interval for the mean of per-query scores."""
    arr = np.asarray(values, dtype="float64")
    if arr.size == 0:
        raise ValueError("bootstrap_ci needs at least one per-query score")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, arr.size, size=(n_resamples, arr.size))
    means = arr[idx].mean(axis=1)
    tail = (1.0 - confidence) / 2.0
    lo, hi = np.quantile(means, [tail, 1.0 - tail])
    return BootstrapCI(
        point=float(arr.mean()), lo=float(lo), hi=float(hi), n=int(arr.size),
        confidence=confidence, n_resamples=n_resamples,
    )


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


def paired_delta(
    a: dict[str, float],
    b: dict[str, float],
    *,
    confidence: float = 0.95,
    n_resamples: int = 10000,
    seed: int = 0,
) -> PairedResult:
    """Compare run `b` against run `a` on their shared queries.

    Returns mean_b - mean_a with a paired bootstrap interval and a two-sided
    randomization p-value. Under the null the two systems are interchangeable
    on each query, so the test flips the sign of each per-query difference at
    random; p is the share of resamples whose mean difference is at least as
    extreme as the observed one, using the (count+1)/(n+1) estimator so p is
    never reported as exactly zero.
    """
    ids = sorted(set(a) & set(b))
    if not ids:
        raise ValueError("paired_delta needs queries scored by both runs")
    va = np.array([a[q] for q in ids], dtype="float64")
    vb = np.array([b[q] for q in ids], dtype="float64")
    diff = vb - va
    observed = float(diff.mean())

    rng = np.random.default_rng(seed)
    idx = rng.integers(0, diff.size, size=(n_resamples, diff.size))
    boot = diff[idx].mean(axis=1)
    tail = (1.0 - confidence) / 2.0
    ci_lo, ci_hi = np.quantile(boot, [tail, 1.0 - tail])

    signs = rng.choice(np.array([-1.0, 1.0]), size=(n_resamples, diff.size))
    perm = (signs * diff).mean(axis=1)
    extreme = int(np.sum(np.abs(perm) >= abs(observed) - 1e-12))
    p_value = (extreme + 1) / (n_resamples + 1)

    return PairedResult(
        n=len(ids), mean_a=float(va.mean()), mean_b=float(vb.mean()),
        delta=observed, ci_lo=float(ci_lo), ci_hi=float(ci_hi),
        p_value=float(p_value), confidence=confidence,
        n_resamples=n_resamples, query_ids=ids,
    )
