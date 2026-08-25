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
