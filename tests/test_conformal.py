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
