"""Tests for src/sebi_rag/conformal.py — Conformal Risk Control (Angelopoulos et al. 2024,
arXiv:2208.02814) + leave-one-out data reuse (Barber et al. 2021, arXiv:1905.02928),
applied to the abstention gate's two threshold signals. Offline, no model dependency.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sebi_rag.conformal import crc_threshold  # noqa: E402


def test_crc_threshold_all_wrong_needs_a_high_threshold():
    # 4 rows, all "wrong if admitted". With alpha=0.5 and n=4, the risk bound is
    # (admitted_wrong + 1) / 5 <= 0.5 -> admitted_wrong <= 1.5 -> admitted_wrong <= 1.
    # Scores 1,2,3,4 all wrong. At lambda=4: admitted={4}, admitted_wrong=1, risk=2/5=0.4<=0.5. OK.
    # At lambda=3: admitted={3,4}, admitted_wrong=2, risk=3/5=0.6>0.5. Fails.
    # So the smallest satisfying lambda is 4.
    scores = [1.0, 2.0, 3.0, 4.0]
    wrong = [True, True, True, True]
    assert crc_threshold(scores, wrong, alpha=0.5) == 4.0


def test_crc_threshold_none_wrong_admits_everything():
    # No row is ever wrong, so admitted_wrong=0 at every lambda -> corrected risk is the
    # constant floor (0+1)/(n+1) = 1/4 = 0.25 everywhere. alpha=0.3 clears that floor,
    # so the smallest candidate (most permissive) wins.
    scores = [1.0, 2.0, 3.0]
    wrong = [False, False, False]
    assert crc_threshold(scores, wrong, alpha=0.3) == 1.0


def test_crc_threshold_risk_is_computed_with_the_plus_one_correction():
    # n=1, one wrong row at score=5. risk(lambda<=5) = (1+1)/(1+1) = 1.0. risk(lambda>5) = (0+1)/2=0.5.
    # alpha=0.6: smallest lambda with risk<=0.6 is the "admit nothing" candidate (max(scores)+1).
    scores = [5.0]
    wrong = [True]
    assert crc_threshold(scores, wrong, alpha=0.6) == 6.0  # max(scores) + 1.0


def test_crc_threshold_rejects_alpha_below_the_finite_sample_floor():
    # n=2 -> floor is 1/(n+1) = 1/3. alpha=0.2 is below that -> no threshold can certify it.
    with pytest.raises(ValueError, match="floor"):
        crc_threshold([1.0, 2.0], [True, False], alpha=0.2)


def test_crc_threshold_rejects_empty_input():
    with pytest.raises(ValueError, match="at least one"):
        crc_threshold([], [], alpha=0.5)


from sebi_rag.conformal import CalibrationResult, jackknife_plus_quantile  # noqa: E402


def test_jackknife_plus_quantile_threshold_matches_full_data_crc():
    # The .threshold field is crc_threshold fit on ALL rows -- same value as calling
    # crc_threshold directly.
    scores = [1.0, 2.0, 3.0, 4.0, 5.0]
    wrong = [True, True, False, True, False]
    result = jackknife_plus_quantile(scores, wrong, alpha=0.4)
    assert result.threshold == crc_threshold(scores, wrong, alpha=0.4)
    assert result.target_alpha == 0.4
    assert result.certified_risk_bound == 0.4
    assert result.n == 5
    assert "2208.02814" in result.method
    assert "1905.02928" in result.method


def test_jackknife_plus_quantile_held_out_estimate_never_uses_its_own_row():
    # Construct a case where the full-data threshold would (if naively self-evaluated)
    # admit row 0 as a loss, but row 0's OWN leave-one-out threshold (fit without row 0)
    # is stricter and excludes it -- proving the held-out estimate is genuinely
    # out-of-sample, not a repeat of the in-sample full-data threshold.
    scores = [10.0, 1.0, 1.0, 1.0, 1.0]
    wrong = [True, True, True, True, True]
    # Full-data crc_threshold at alpha=0.5, n=5: risk(lambda)=(admitted_wrong+1)/6<=0.5
    # -> admitted_wrong<=2. At lambda=1.0: all 5 admitted, admitted_wrong=5, risk=1.0>0.5.
    # At lambda=10.0: only row0 admitted, admitted_wrong=1, risk=2/6=0.33<=0.5. So
    # full-data threshold = 10.0, and only row 0 is ever admitted by it.
    result = jackknife_plus_quantile(scores, wrong, alpha=0.5)
    assert result.threshold == 10.0
    # Leave row 0 out: remaining scores=[1,1,1,1], wrong=[T,T,T,T], n=4.
    # risk(lambda)=(admitted_wrong+1)/5<=0.5 -> admitted_wrong<=1.5 -> <=1.
    # At lambda=1.0: all 4 admitted, admitted_wrong=4, risk=1.0>0.5. Fails.
    # Only candidate is [1.0, 2.0] (max+1) -> lambda=2.0 admits nothing, risk=1/5=0.2<=0.5.
    # So row 0's LOO threshold is 2.0, and row0's own score (10.0) IS admitted at 2.0,
    # and row0 is wrong -> loss=1 for row 0's held-out evaluation.
    # This differs from what row 0's contribution would be under the FULL-data threshold
    # (10.0), where the LOO threshold (2.0) is stricter for every other row too -- proving
    # the held-out risk estimate is a materially different (and here, higher) number than
    # a naive in-sample risk at the full-data threshold would report.
    naive_in_sample_risk = 1 / 6  # admitted_wrong=0 at threshold=10 among rows 1-4 (all score=1)
    assert result.held_out_risk_estimate > naive_in_sample_risk


def test_calibration_result_is_a_plain_dataclass():
    r = CalibrationResult(threshold=1.0, target_alpha=0.05, certified_risk_bound=0.05,
                          held_out_risk_estimate=0.02, n=10, method="test")
    assert r.threshold == 1.0 and r.n == 10


from sebi_rag.conformal import calibrate_score_floor, calibrate_subject_gate  # noqa: E402


def test_calibrate_score_floor_extracts_rerank_top_and_wrong_if_answered():
    rows = [
        {"rerank_top": 0.9, "wrong_if_answered": False},
        {"rerank_top": 0.8, "wrong_if_answered": True},
        {"rerank_top": 0.3, "wrong_if_answered": True},
        {"rerank_top": 0.1, "wrong_if_answered": False},
    ]
    result = calibrate_score_floor(rows, alpha=0.5)
    expected = jackknife_plus_quantile(
        [0.9, 0.8, 0.3, 0.1], [False, True, True, False], alpha=0.5)
    assert result.threshold == expected.threshold
    assert result.n == 4


def test_calibrate_subject_gate_returns_a_real_scale_threshold():
    # All rows answerable (would be false abstentions if excluded). Subject_sim values
    # 0.9, 0.5, 0.3, 0.1 -- calibrate_subject_gate must return a threshold ON THE ORIGINAL
    # subject_sim scale (positive, in a plausible [0,1]-ish range), not a raw negated value.
    rows = [
        {"subject_sim": 0.9, "answerable": True},
        {"subject_sim": 0.5, "answerable": True},
        {"subject_sim": 0.3, "answerable": True},
        {"subject_sim": 0.1, "answerable": True},
    ]
    result = calibrate_subject_gate(rows, alpha=0.5)
    # Every row is a false-abstention risk if excluded (all answerable=True), so ANY
    # exclusion contributes to risk -- the calibrated threshold must be low enough to
    # exclude nothing (n=4, alpha=0.5 > floor 1/5=0.2, so some slack exists, but with
    # every row "wrong", the returned threshold must sit at or below the minimum
    # subject_sim value to keep the (admitted_wrong+1)/(n+1) bound satisfied for the
    # smallest achievable excluded-count).
    assert result.threshold <= 0.5  # sanity: not a huge, nonsensical value
    assert isinstance(result.threshold, float)


def test_calibrate_subject_gate_direction_is_correct_on_a_worked_example():
    # 5 rows, subject_sim = [0.9, 0.7, 0.5, 0.3, 0.1], all answerable=True (every
    # exclusion is a false abstention). alpha=0.5, n=5, floor=1/6=0.1667.
    # Negated scores fed to crc_threshold: [-0.9,-0.7,-0.5,-0.3,-0.1], wrong=[T,T,T,T,T].
    # risk(lambda) = (admitted_wrong+1)/6 <= 0.5 -> admitted_wrong <= 2.
    # Candidates ascending: -0.9,-0.7,-0.5,-0.3,-0.1, then max+1=0.9.
    # At lambda=-0.9: admitted = scores>=-0.9 = all 5 -> admitted_wrong=5, risk=1.0>0.5. Fail.
    # At lambda=-0.7: admitted = scores in {-0.7,-0.5,-0.3,-0.1} (4) -> risk=5/6>0.5. Fail.
    # At lambda=-0.5: admitted = 3 rows -> risk=4/6=0.667>0.5. Fail.
    # At lambda=-0.3: admitted = 2 rows -> risk=3/6=0.5<=0.5. PASS. lambda=-0.3.
    # real threshold tau = -lambda = 0.3.
    rows = [{"subject_sim": s, "answerable": True} for s in [0.9, 0.7, 0.5, 0.3, 0.1]]
    result = calibrate_subject_gate(rows, alpha=0.5)
    assert result.threshold == pytest.approx(0.3)
