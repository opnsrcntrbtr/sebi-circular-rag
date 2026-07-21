"""Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests)."""
from __future__ import annotations

import math

import pytest

from sebi_rag.stats import bootstrap_ci, paired_delta


class TestBootstrapCI:
    def test_constant_values_give_degenerate_interval(self):
        ci = bootstrap_ci([0.5] * 20, n_resamples=200, seed=0)
        assert ci.point == pytest.approx(0.5)
        assert ci.lo == pytest.approx(0.5)
        assert ci.hi == pytest.approx(0.5)

    def test_interval_brackets_the_point_estimate(self):
        values = [1.0] * 53 + [0.0] * 3  # ~ recall 0.946 at n=56
        ci = bootstrap_ci(values, n_resamples=2000, seed=0)
        assert ci.lo <= ci.point <= ci.hi
        assert ci.lo < ci.hi  # a real interval, not a point

    def test_is_deterministic_for_a_given_seed(self):
        values = [1.0] * 50 + [0.0] * 6
        a = bootstrap_ci(values, n_resamples=1000, seed=7)
        b = bootstrap_ci(values, n_resamples=1000, seed=7)
        assert (a.lo, a.hi) == (b.lo, b.hi)

    def test_seed_changes_the_resampling(self):
        # Continuous scores: binary per-query scores put the bootstrap means on
        # a coarse discrete grid where two seeds often agree exactly.
        values = [i / 56 for i in range(56)]
        a = bootstrap_ci(values, n_resamples=1000, seed=7)
        c = bootstrap_ci(values, n_resamples=1000, seed=8)
        assert (a.lo, a.hi) != (c.lo, c.hi)

    def test_higher_confidence_widens_the_interval(self):
        values = [1.0] * 50 + [0.0] * 6
        narrow = bootstrap_ci(values, confidence=0.80, n_resamples=4000, seed=0)
        wide = bootstrap_ci(values, confidence=0.99, n_resamples=4000, seed=0)
        assert wide.hi - wide.lo > narrow.hi - narrow.lo

    def test_small_sample_interval_is_wide_enough_to_matter(self):
        """The point of this module: at n=56 and recall ~0.956 the interval must
        be wide enough that a 2-point delta cannot be called a regression."""
        values = [1.0] * 53 + [0.0] * 3
        ci = bootstrap_ci(values, n_resamples=4000, seed=0)
        assert ci.hi - ci.lo > 0.05

    def test_empty_input_rejected(self):
        with pytest.raises(ValueError):
            bootstrap_ci([], n_resamples=100, seed=0)


class TestPairedDelta:
    def test_identical_runs_have_zero_delta_and_no_significance(self):
        a = {f"q{i}": 1.0 for i in range(20)}
        r = paired_delta(a, dict(a), n_resamples=500, seed=0)
        assert r.delta == pytest.approx(0.0)
        assert r.p_value == pytest.approx(1.0)
        assert r.n == 20

    def test_uniform_improvement_is_detected(self):
        a = {f"q{i}": 0.0 for i in range(30)}
        b = {f"q{i}": 1.0 for i in range(30)}
        r = paired_delta(a, b, n_resamples=2000, seed=0)
        assert r.delta == pytest.approx(1.0)
        assert r.p_value < 0.01
        assert r.ci_lo > 0.0

    def test_single_query_difference_is_not_significant(self):
        """One query flipping out of 56 is exactly the iv9-style verdict: the
        randomization test must refuse to call it a regression."""
        a = {f"q{i}": 1.0 for i in range(56)}
        b = dict(a)
        b["q0"] = 0.0
        r = paired_delta(a, b, n_resamples=4000, seed=0)
        assert r.delta == pytest.approx(-1 / 56)
        assert r.p_value > 0.05

    def test_aligns_on_common_queries_only(self):
        a = {"q1": 1.0, "q2": 0.0, "only_in_a": 1.0}
        b = {"q1": 1.0, "q2": 0.0, "only_in_b": 0.0}
        r = paired_delta(a, b, n_resamples=200, seed=0)
        assert r.n == 2
        assert r.query_ids == ["q1", "q2"]

    def test_disjoint_query_sets_rejected(self):
        with pytest.raises(ValueError):
            paired_delta({"a": 1.0}, {"b": 1.0}, n_resamples=100, seed=0)

    def test_delta_sign_is_b_minus_a(self):
        a = {"q1": 0.0, "q2": 0.0}
        b = {"q1": 1.0, "q2": 0.0}
        r = paired_delta(a, b, n_resamples=200, seed=0)
        assert r.delta > 0
        assert r.mean_a == pytest.approx(0.0)
        assert r.mean_b == pytest.approx(0.5)

    def test_p_value_is_bounded_away_from_zero(self):
        """Randomization p-values use the (count+1)/(n+1) estimator, so a
        p-value of exactly 0 — which would overstate significance — is
        impossible."""
        a = {f"q{i}": 0.0 for i in range(40)}
        b = {f"q{i}": 1.0 for i in range(40)}
        r = paired_delta(a, b, n_resamples=1000, seed=0)
        assert r.p_value > 0
        assert math.isclose(r.p_value, 1 / 1001, rel_tol=1e-9)
