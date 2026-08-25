"""Conformal Risk Control (Angelopoulos, Bates, Fisch, Lei, Schuster; ICLR 2024,
arXiv:2208.02814) applied to the abstention gate's two hand-fit thresholds
(Settings.abstain_threshold, SEBI_RAG_SUBJ_THRESHOLD), with leave-one-out data reuse in
the spirit of Barber, Candes, Ramdas, Tibshirani's jackknife+ (Annals of Statistics 49(1),
2021, arXiv:1905.02928) so golden_v7's 260 rows are used for both fitting and honest
out-of-sample evaluation without a hard calibration/test split.

Design doc: docs/superpowers/specs/2026-08-26-conformal-abstention-calibration-design.md.
No model or pipeline dependency -- every function here is a pure computation over
pre-computed (score, correctness) pairs.
"""
from __future__ import annotations

from dataclasses import dataclass


def crc_threshold(scores: list[float], wrong: list[bool], alpha: float) -> float:
    """Conformal Risk Control threshold for a monotone 0/1 loss.

    A row i is "admitted" at threshold lambda iff scores[i] >= lambda. The loss at row i
    and threshold lambda is `wrong[i] AND admitted(i, lambda)` -- e.g. for the score-floor
    gate, scores[i] is rerank_top and wrong[i] is "this row's answer was actually wrong",
    so the loss is "answered AND wrong". Raising lambda only ever removes rows from the
    admitted set, so the empirical risk R(lambda) = mean(loss) is non-increasing in
    lambda, which is what makes a single-threshold search well-posed.

    Returns the SMALLEST lambda such that the finite-sample-corrected empirical risk
    (Angelopoulos et al. Theorem 1, with loss bound B=1 for a 0/1 loss):

        R_hat(lambda) = (sum(loss(i, lambda) for i) + 1) / (n + 1)

    is <= alpha. This is the most permissive (most-admitting) threshold that still
    certifies the risk bound.

    Raises ValueError if `scores`/`wrong` is empty, or if alpha is at or below this
    sample's finite-sample floor 1/(n+1) -- no threshold can certify a bound that tight
    at this sample size, since even admitting nothing leaves risk = 1/(n+1).
    """
    n = len(scores)
    if n == 0:
        raise ValueError("crc_threshold requires at least one calibration row")
    floor = 1.0 / (n + 1)
    if alpha <= floor:
        raise ValueError(
            f"alpha={alpha} is at or below this sample's finite-sample floor "
            f"1/(n+1)={floor:.4f} (n={n}) -- no threshold can certify a risk bound "
            f"this tight at this sample size (CRC, arXiv:2208.02814, Thm 1)."
        )
    candidates = sorted(set(scores)) + [max(scores) + 1.0]
    for lam in candidates:
        admitted_wrong = sum(
            1 for s, w in zip(scores, wrong) if w and s >= lam
        )
        risk = (admitted_wrong + 1) / (n + 1)
        if risk <= alpha:
            return lam
    raise AssertionError(
        "no threshold satisfied the risk bound despite the floor check -- "
        "this indicates a bug in crc_threshold, not a data problem"
    )


@dataclass
class CalibrationResult:
    threshold: float
    target_alpha: float
    certified_risk_bound: float
    held_out_risk_estimate: float
    n: int
    method: str


def jackknife_plus_quantile(scores: list[float], wrong: list[bool],
                            alpha: float) -> CalibrationResult:
    """Leave-one-out data reuse (in the spirit of Barber et al. 2021, arXiv:1905.02928)
    wrapped around crc_threshold (Angelopoulos et al. 2024, arXiv:2208.02814).

    Not a literal instantiation of Barber et al.'s regression-interval construction --
    there is no fitted predictive model here, `scores`/`wrong` are pre-computed external
    signals (e.g. a reranker's score and a citation-correctness label). What is reused
    from their paper is the DATA-REUSE PHILOSOPHY: rather than a single calibration/test
    split (which would fragment an already-small dataset's boundary cases), every row is
    held out exactly once to get an honest out-of-sample check of the FINAL threshold's
    performance, without permanently spending any row purely on evaluation.

    Returns a CalibrationResult whose `threshold` is crc_threshold() fit on ALL n rows
    (the deployable value), and whose `held_out_risk_estimate` is the mean, over i in
    1..n, of whether row i's own admission decision -- at the threshold fit on the OTHER
    n-1 rows -- was a loss event (wrong[i] AND scores[i] >= that leave-one-out threshold).
    That estimate never evaluates a row against a threshold that row helped fit.
    """
    n = len(scores)
    threshold = crc_threshold(scores, wrong, alpha)
    loo_losses = []
    for i in range(n):
        other_scores = scores[:i] + scores[i + 1:]
        other_wrong = wrong[:i] + wrong[i + 1:]
        loo_threshold = crc_threshold(other_scores, other_wrong, alpha)
        admitted = scores[i] >= loo_threshold
        loo_losses.append(1.0 if (admitted and wrong[i]) else 0.0)
    held_out_risk = sum(loo_losses) / n
    return CalibrationResult(
        threshold=threshold, target_alpha=alpha, certified_risk_bound=alpha,
        held_out_risk_estimate=held_out_risk, n=n,
        method=("CRC (arXiv:2208.02814) + leave-one-out data reuse "
                "(Barber et al. 2021, arXiv:1905.02928)"),
    )
