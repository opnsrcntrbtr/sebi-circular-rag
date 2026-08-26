# Conformal-Calibrated Abstention Thresholds (R7) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the hand-fit abstention gate thresholds (`Settings.abstain_threshold`,
`SEBI_RAG_SUBJ_THRESHOLD`) with values carrying a stated, finite-sample risk guarantee, computed
via Conformal Risk Control with full-data (leave-one-out) reuse over golden_v7 — and measure
whether they clear this project's adoption bar before touching production config.

**Architecture:** A new pure-function calibration library (`src/sebi_rag/conformal.py`, no model
dependency) implementing Conformal Risk Control (CRC) as a generic monotone-threshold search, plus
a leave-one-out wrapper for honest out-of-sample risk estimates without a data split. A three-phase
analysis script (generate → calibrate → report, matching this repo's established
`warrant_scorer_cohort.py`/`jina_citation_scorer_cohort.py` pattern) applies it to fresh production
scores and mechanically evaluates the preregistered decision rule. The AND-gate combination logic
in `generate.py` is not touched by this plan — only where its two threshold *values* would come
from, and only on a separate future adoption step.

**Tech Stack:** Pure Python + numpy (no new dependency). Existing production pipeline
(`build_default_pipeline`) for fresh per-row scores; existing `eval_harness._doc`/`_unique` for
citation-correctness matching.

**Spec:** `docs/superpowers/specs/2026-08-26-conformal-abstention-calibration-design.md` — read
this first. This plan implements its §2 (method), §5 (testing), and §9 (implementation notes).
Execution of the calibration itself and the §6 decision rule is Task 6 below; **adoption**
(writing calibrated values into `config.toml`) is explicitly **out of scope** for this plan per the
spec's §7 — a human reviews Task 6's output first.

## Global Constraints

- No new field on `CircularMeta` (`segment.py:131` — 78,630 chunks would be mutated).
- No edit to `*_spaces.py` or root `app.py` (two-parallel-code-paths rule).
- No change to `generate.py`'s AND-gate combination logic, `_is_non_sebi_domain`, or
  `superseded_penalty` — single variable per the spec's §1.
- Single preregistered α grid: **α = 0.05 primary**, α = 0.10 secondary/sensitivity-only (spec §6)
  — fixed here, not chosen after seeing a result.
- Effect floor for adoption-worthiness: `abstention_accuracy` (honest, LOO) increases by **≥ +0.01
  absolute**; **zero tolerance** on any increase in false-answer rate; no other gate floor
  (`eval/golden/gate_v7.json`) regresses (spec §6).
- Every new function needs a docstring citing its source: CRC = Angelopoulos et al. 2024,
  [arXiv:2208.02814](https://arxiv.org/abs/2208.02814); LOO data reuse philosophy = Barber et al.
  2021, [arXiv:1905.02928](https://arxiv.org/abs/1905.02928) (verified via primary source, not an
  aggregator, per this project's `docs/research-synthesis-2026-08-19.md` convention).
- Environment guards for any script touching the production pipeline: `TOKENIZERS_PARALLELISM=false
  OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 HF_HUB_DISABLE_XET=1 PYTHONPATH=src`.

---

## File Structure

| File | Responsibility |
|---|---|
| `src/sebi_rag/conformal.py` | New. Pure calibration library: `crc_threshold`, `CalibrationResult`, `jackknife_plus_quantile`, `calibrate_score_floor`, `calibrate_subject_gate`. No model/pipeline dependency — offline, unit-testable with synthetic data. |
| `tests/test_conformal.py` | New. TDD suite for every function above, offline. |
| `scripts/analysis/conformal_abstention_calibration.py` | New. Three-phase script: `generate` (fresh per-row production scores over golden_v7), `calibrate` (runs the two calibrations at α∈{0.05,0.10}), `report` (applies the spec's §6 decision rule mechanically, writes the final report). |

No existing file is modified by this plan.

---

### Task 1: `crc_threshold` — the core Conformal Risk Control primitive

**Files:**
- Create: `src/sebi_rag/conformal.py`
- Test: `tests/test_conformal.py`

**Interfaces:**
- Consumes: nothing (pure function, first task).
- Produces: `crc_threshold(scores: list[float], wrong: list[bool], alpha: float) -> float`,
  used by Task 2's `jackknife_plus_quantile`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_conformal.py`:

```python
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
    # No row is ever wrong, so risk is 0 at every lambda -> smallest candidate wins.
    scores = [1.0, 2.0, 3.0]
    wrong = [False, False, False]
    assert crc_threshold(scores, wrong, alpha=0.05) == 1.0


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_conformal.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sebi_rag.conformal'`

- [ ] **Step 3: Write minimal implementation**

Create `src/sebi_rag/conformal.py`:

```python
"""Conformal Risk Control (Angelopoulos, Bates, Fisch, Lei, Schuster; ICLR 2024,
arXiv:2208.02814) applied to the abstention gate's two hand-fit thresholds
(Settings.abstain_threshold, SEBI_RAG_SUBJ_THRESHOLD), with leave-one-out data reuse in
the spirit of Barber, Candes, Ramdas, Tibshirani's jackknife+ (Annals of Statistics 49(1),
2021, arXiv:1905.02928) so golden_v7's 260 rows are used for both fitting and honest
out-of-sample evaluation without a hard calibration/test split.

Design doc: docs/superpowers/specs/2026-08-26-conformal-abstention-calibration-design.md.
No model or pipeline dependency — every function here is a pure computation over
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/test_conformal.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/conformal.py tests/test_conformal.py
git commit -m "feat(conformal): add crc_threshold primitive (arXiv:2208.02814)

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01MoGpVqT5fDqauAMwAs78ze"
```

---

### Task 2: `CalibrationResult` + `jackknife_plus_quantile` — leave-one-out wrapper

**Files:**
- Modify: `src/sebi_rag/conformal.py`
- Test: `tests/test_conformal.py`

**Interfaces:**
- Consumes: `crc_threshold(scores, wrong, alpha) -> float` from Task 1.
- Produces: `CalibrationResult` dataclass (fields: `threshold: float`, `target_alpha: float`,
  `certified_risk_bound: float`, `held_out_risk_estimate: float`, `n: int`, `method: str`);
  `jackknife_plus_quantile(scores: list[float], wrong: list[bool], alpha: float) -> CalibrationResult`.
  Used by Task 3's `calibrate_score_floor`/`calibrate_subject_gate`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_conformal.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_conformal.py -v`
Expected: FAIL with `ImportError: cannot import name 'CalibrationResult'`

- [ ] **Step 3: Write minimal implementation**

Append to `src/sebi_rag/conformal.py`:

```python
from dataclasses import dataclass


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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/test_conformal.py -v`
Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/conformal.py tests/test_conformal.py
git commit -m "feat(conformal): add jackknife_plus_quantile LOO wrapper

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01MoGpVqT5fDqauAMwAs78ze"
```

---

### Task 3: `calibrate_score_floor` + `calibrate_subject_gate` — the two signal-specific wrappers

**Files:**
- Modify: `src/sebi_rag/conformal.py`
- Test: `tests/test_conformal.py`

**Interfaces:**
- Consumes: `jackknife_plus_quantile(scores, wrong, alpha) -> CalibrationResult` from Task 2.
- Produces: `calibrate_score_floor(rows: list[dict], alpha: float) -> CalibrationResult` (each row
  dict has `"rerank_top": float` and `"wrong_if_answered": bool`); `calibrate_subject_gate(rows:
  list[dict], alpha: float) -> CalibrationResult` (each row dict has `"subject_sim": float` and
  `"answerable": bool`). Used by Task 5's calibrate phase.

**⚠️ Direction note for the implementer (read before writing the subject-gate function).** The two
signals have OPPOSITE risk monotonicity. Raising the score-floor threshold only ever *removes*
answered rows, so the risk it controls (false-answer rate among admitted rows) is non-increasing in
the threshold — `crc_threshold` applies directly. Raising the subject-gate threshold only ever
*removes* rows from the passing set too, but the risk we care about there (false-abstention rate
among the *excluded* rows) is non-decreasing in the threshold — the opposite direction. The fix is
to negate the score axis: call `crc_threshold` with `scores = [-s for s in subject_sim_values]`
and `wrong = answerable` (True = would be a false abstention if excluded), then negate the returned
threshold back (`real_threshold = -result.threshold`). Concretely: `crc_threshold`'s "admitted" test
is `-subject_sim[i] >= lambda`, i.e. `subject_sim[i] <= -lambda`; writing `tau = -lambda`, this is
`subject_sim[i] <= tau`, i.e. *excluded* at the real threshold `tau` — exactly the set whose false-
abstention risk we want to control. Searching for `crc_threshold`'s smallest `lambda` therefore
finds the *largest* `tau` that still certifies the false-abstention risk bound, which is the correct
target: as strict as the risk budget allows, not stricter.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_conformal.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python -m pytest tests/test_conformal.py -v`
Expected: FAIL with `ImportError: cannot import name 'calibrate_score_floor'`

- [ ] **Step 3: Write minimal implementation**

Append to `src/sebi_rag/conformal.py`:

```python
def calibrate_score_floor(rows: list[dict], alpha: float) -> CalibrationResult:
    """Calibrate the score-floor threshold (Settings.abstain_threshold).

    rows: dicts with 'rerank_top' (float, the cross-encoder/reranker top score) and
    'wrong_if_answered' (bool) -- True if this row's gold label is abstain=True (any
    answer at all is wrong), OR the row is gold-answerable but its actual production
    citations missed every relevant document (zero_cite). See design doc Sec 2.3.

    Risk controlled: false-answer rate among admitted (answered) rows. Direct
    application of jackknife_plus_quantile -- raising the floor only ever removes
    answered rows, so risk is non-increasing in the threshold already.
    """
    scores = [r["rerank_top"] for r in rows]
    wrong = [r["wrong_if_answered"] for r in rows]
    return jackknife_plus_quantile(scores, wrong, alpha)


def calibrate_subject_gate(rows: list[dict], alpha: float) -> CalibrationResult:
    """Calibrate the subject-gate threshold (SEBI_RAG_SUBJ_THRESHOLD).

    rows: dicts with 'subject_sim' (float, SubjectSimJudge's score) and 'answerable'
    (bool, the gold label -- True means this row should NOT be abstained). Caller must
    restrict `rows` to those where subject_sim was actually computed (i.e. the row
    passed the score-floor and non-SEBI-domain gates first -- see
    generate.py:answer_with_abstention, which short-circuits before the judge runs).

    Risk controlled: false-abstention rate among rows the subject gate would exclude
    (subject_sim below the threshold). This risk is the OPPOSITE monotonicity of the
    score-floor's -- see this file's module docstring and the plan's Task 3 direction
    note for the derivation. Calibrated on -subject_sim so jackknife_plus_quantile's
    "risk non-increasing in the threshold" assumption holds; the returned threshold is
    negated back to the original subject_sim scale before returning.
    """
    scores = [-r["subject_sim"] for r in rows]
    wrong = [r["answerable"] for r in rows]
    result = jackknife_plus_quantile(scores, wrong, alpha)
    return CalibrationResult(
        threshold=-result.threshold, target_alpha=result.target_alpha,
        certified_risk_bound=result.certified_risk_bound,
        held_out_risk_estimate=result.held_out_risk_estimate, n=result.n,
        method=result.method,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python -m pytest tests/test_conformal.py -v`
Expected: PASS (11 passed)

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/conformal.py tests/test_conformal.py
git commit -m "feat(conformal): add calibrate_score_floor and calibrate_subject_gate

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01MoGpVqT5fDqauAMwAs78ze"
```

---

### Task 4: Generate phase — fresh per-row production scores over golden_v7

**Files:**
- Create: `scripts/analysis/conformal_abstention_calibration.py`

**Interfaces:**
- Consumes: `build_default_pipeline()` (`sebi_rag.api`), `load_golden()`/`_doc()`/`_unique()`
  (`sebi_rag.eval_harness`) — all pre-existing, no changes needed.
- Produces: `reports/conformal-calibration-generate.json` on disk, consumed by Task 5. Row schema:
  `{"id": str, "abstain_gold": bool, "abstained": bool, "abstention_reason": str,
  "rerank_top": float, "subject_sim": float | None, "wrong_if_answered": bool,
  "answerable": bool}`.

This mirrors `scripts/analysis/jina_citation_scorer_cohort.py`'s `phase_generate` structure (env
guards, `_measure`-style correctness check) but runs over the FULL golden_v7 (n=260, both abstain
and answerable rows), not just a perfect-retrieval-answerable cohort — the abstention gate fires on
every row regardless of gold label.

- [ ] **Step 1: Write the script's generate phase**

Create `scripts/analysis/conformal_abstention_calibration.py`:

```python
"""R7 conformal abstention calibration: generate -> calibrate -> report phases.

Spec: docs/superpowers/specs/2026-08-26-conformal-abstention-calibration-design.md.
Plan: docs/superpowers/plans/2026-08-26-conformal-abstention-calibration.md.

Calibrates the score-floor (Settings.abstain_threshold) and subject-gate
(SEBI_RAG_SUBJ_THRESHOLD) thresholds via Conformal Risk Control + leave-one-out data
reuse (src/sebi_rag/conformal.py), using FRESH per-row scores under current production
(Jina reranker, ADR-004; recalibrated abstain_threshold=0.12) -- not any prior dump,
which would predate that adoption.

Three phases, matching this repo's established cohort-script pattern:
  1. generate    -- full production pipeline over all 260 golden_v7 rows (both abstain
                     and answerable -- the gate fires on every row regardless of gold
                     label), captures rerank_top/subject_sim/abstention_reason plus the
                     ground-truth labels the calibration functions need.
  2. calibrate    -- no model loaded, pure computation. Runs calibrate_score_floor and
                     calibrate_subject_gate at alpha in {0.05, 0.10} (0.05 primary,
                     per the spec's Sec 6, fixed in advance -- not chosen after seeing
                     a result).
  3. report       -- applies the spec's Sec 6 decision rule mechanically.

Usage:
  PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase generate
  PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase calibrate
  PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase report
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

for _k, _v in {
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(_k, _v)

GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
GATE = ROOT / "eval" / "golden" / "gate_v7.json"
GENERATE_DUMP = ROOT / "reports" / "conformal-calibration-generate.json"
CALIBRATE_DUMP = ROOT / "reports" / "conformal-calibration-calibrate.json"
DEST = ROOT / "reports" / "conformal-calibration-report-2026-08-26.json"

POOL, TOP_K = 50, 10
ALPHA_PRIMARY = 0.05
ALPHA_SECONDARY = 0.10
ABSTENTION_ACCURACY_EFFECT_FLOOR = 0.01  # spec Sec 6, fixed in advance


def phase_generate() -> None:
    from sebi_rag.api import build_default_pipeline
    from sebi_rag.eval_harness import _doc, _unique, load_golden

    pipe = build_default_pipeline()
    items = list(load_golden(GOLDEN))
    print(f"golden_v7 rows: {len(items)}", file=sys.stderr)

    rows, t0 = [], time.time()
    for n, it in enumerate(items, 1):
        ans, _ = pipe.query(it["query"], pool=POOL, top_k=TOP_K)
        gold_abstain = bool(it.get("abstain"))
        rerank_top = ans.confidence.get("rerank_top")
        subject_sim = ans.confidence.get("subject_sim")

        if gold_abstain:
            wrong_if_answered = True  # any answer at all is wrong for a gold-abstain row
        else:
            relevant = set(it.get("relevant_circulars") or [])
            if not relevant or ans.abstained:
                # No gold citations to check against, or this row abstained (so
                # "if answered" correctness can't be assessed from what happened) --
                # conservatively exclude from the score-floor calibration set rather
                # than guess. Flagged via wrong_if_answered=None, filtered in calibrate.
                wrong_if_answered = None
            else:
                cited = _unique(_doc(c) for c in ans.citations)
                wrong_if_answered = len(set(cited) & relevant) == 0  # zero_cite

        rows.append({
            "id": it["id"], "abstain_gold": gold_abstain,
            "abstained": bool(ans.abstained),
            "abstention_reason": ans.abstention_reason,
            "rerank_top": rerank_top, "subject_sim": subject_sim,
            "wrong_if_answered": wrong_if_answered,
            "answerable": not gold_abstain,
        })
        if n % 25 == 0:
            print(f"  {n}/{len(items)}  ({time.time() - t0:.0f}s)", file=sys.stderr)

    out = {
        "n": len(rows), "runtime_s": round(time.time() - t0, 1),
        "reranker": pipe.reranker.__class__.__name__,
        "abstain_threshold": pipe.abstain_threshold,
        "rows": rows,
    }
    GENERATE_DUMP.parent.mkdir(parents=True, exist_ok=True)
    GENERATE_DUMP.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {GENERATE_DUMP} (n={out['n']}, {out['runtime_s']}s)", file=sys.stderr)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["generate", "calibrate", "report"], required=True)
    args = ap.parse_args()
    {"generate": phase_generate}[args.phase]()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-test the generate phase on a tiny slice**

This phase runs the full production pipeline (1.5B generator) over 260 rows (~40min per the
established `eval_json_full` baseline) — too slow to iterate on directly. Add a temporary
`SEBI_ROW_LIMIT` env-var truncation for smoke-testing only (mirrors the `SEBI_COHORT_LIMIT`
pattern already used in `scratchpad/late_chunking_pooling_spike.py`), verify it, and only THEN
remove it before the real run in Task 6:

Temporarily add right after `items = list(load_golden(GOLDEN))`:
```python
    limit = int(os.environ.get("SEBI_ROW_LIMIT", "0"))
    if limit:
        items = items[:limit]
        print(f"SEBI_ROW_LIMIT set: truncated to {len(items)} rows (smoke test)", file=sys.stderr)
```

Run: `PYTHONPATH=src TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 HF_HUB_DISABLE_XET=1 SEBI_ROW_LIMIT=5 python scripts/analysis/conformal_abstention_calibration.py --phase generate`

Expected: completes in under a minute after model load, `reports/conformal-calibration-generate.json`
has 5 rows, each with `rerank_top` a float, `subject_sim` either a float or `null`,
`wrong_if_answered` a bool or `null`, no traceback.

- [ ] **Step 3: Inspect the smoke-test output for sanity**

Run: `python -c "import json; d=json.load(open('reports/conformal-calibration-generate.json')); [print(r) for r in d['rows']]"`

Verify by eye: at least one row has `subject_sim` non-null (proves the judge path is reached for
some rows); `abstention_reason` values are among `"", "no_context", "score_floor", "subject_gate",
"non_sebi_domain"`; no row has both `abstained=True` and `abstention_reason=""`.

- [ ] **Step 4: Leave the `SEBI_ROW_LIMIT` truncation in place**

Do not remove it — it stays in the shipped script as an opt-in smoke-test lever (same convention as
every prior cohort script in this repo), inert when the env var is unset.

- [ ] **Step 5: Commit**

```bash
git add scripts/analysis/conformal_abstention_calibration.py
git commit -m "feat(conformal): add generate phase for the R7 calibration script

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01MoGpVqT5fDqauAMwAs78ze"
```

---

### Task 5: Calibrate phase — run both calibrations at the preregistered α grid

**Files:**
- Modify: `scripts/analysis/conformal_abstention_calibration.py`

**Interfaces:**
- Consumes: `reports/conformal-calibration-generate.json` (Task 4's output);
  `calibrate_score_floor`, `calibrate_subject_gate` (`sebi_rag.conformal`, Task 3).
- Produces: `reports/conformal-calibration-calibrate.json`, consumed by Task 6.

- [ ] **Step 1: Write the calibrate phase**

Add to `scripts/analysis/conformal_abstention_calibration.py`, above `def main():`:

```python
def phase_calibrate() -> None:
    if not GENERATE_DUMP.exists():
        raise SystemExit(f"{GENERATE_DUMP} missing -- run --phase generate first")
    from sebi_rag.conformal import calibrate_score_floor, calibrate_subject_gate

    dump = json.loads(GENERATE_DUMP.read_text())
    rows = dump["rows"]

    score_floor_rows = [
        {"rerank_top": r["rerank_top"], "wrong_if_answered": r["wrong_if_answered"]}
        for r in rows if r["wrong_if_answered"] is not None
    ]
    subject_gate_rows = [
        {"subject_sim": r["subject_sim"], "answerable": r["answerable"]}
        for r in rows if r["subject_sim"] is not None
    ]
    print(f"score_floor calibration set: {len(score_floor_rows)} of {len(rows)} rows "
          f"(excludes rows where wrong_if_answered could not be determined)", file=sys.stderr)
    print(f"subject_gate calibration set: {len(subject_gate_rows)} of {len(rows)} rows "
          f"(excludes rows where subject_sim was never computed)", file=sys.stderr)

    results = {}
    for alpha in (ALPHA_PRIMARY, ALPHA_SECONDARY):
        key = f"alpha_{alpha}"
        sf = calibrate_score_floor(score_floor_rows, alpha)
        sg = calibrate_subject_gate(subject_gate_rows, alpha)
        results[key] = {
            "alpha": alpha,
            "score_floor": vars(sf),
            "subject_gate": vars(sg),
        }
        print(f"alpha={alpha}: score_floor threshold={sf.threshold:.4f} "
              f"(held-out risk {sf.held_out_risk_estimate:.4f}), "
              f"subject_gate threshold={sg.threshold:.4f} "
              f"(held-out risk {sg.held_out_risk_estimate:.4f})", file=sys.stderr)

    CALIBRATE_DUMP.write_text(json.dumps(
        {"score_floor_n": len(score_floor_rows), "subject_gate_n": len(subject_gate_rows),
         "results": results}, indent=2), encoding="utf-8")
    print(f"wrote {CALIBRATE_DUMP}", file=sys.stderr)
```

Update `main()`'s phase dispatch dict:

```python
    {"generate": phase_generate, "calibrate": phase_calibrate}[args.phase]()
```

- [ ] **Step 2: Run the calibrate phase against the smoke-test dump from Task 4**

Run: `PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase calibrate`

Expected: no traceback. If the 5-row smoke sample is too small for α=0.05 (finite-sample floor
1/(n+1) — at n=5, floor=1/6≈0.167 > 0.05), `crc_threshold` will raise `ValueError` naming the
floor — that is **correct, expected behavior at this tiny sample size**, not a bug. Confirm the
error message names the floor and n, matching Task 1's `test_crc_threshold_rejects_alpha_below_the_finite_sample_floor`.
This is exactly why Task 6 must run the real n=260 generate phase before calibrating for real —
record this expected-failure observation, do not attempt to work around it at n=5.

- [ ] **Step 3: Re-run the generate-phase smoke test at a size that clears the floor, to verify calibrate's happy path**

`1/(n+1) <= 0.05` requires `n >= 19`. Run:
`PYTHONPATH=src TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 HF_HUB_DISABLE_XET=1 SEBI_ROW_LIMIT=20 python scripts/analysis/conformal_abstention_calibration.py --phase generate`
then: `PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase calibrate`

Expected: both phases complete without error; `reports/conformal-calibration-calibrate.json` has
`results.alpha_0.05` and `results.alpha_0.1`, each with `score_floor` and `subject_gate` sub-objects
carrying a `threshold` float.

- [ ] **Step 4: Commit**

```bash
git add scripts/analysis/conformal_abstention_calibration.py
git commit -m "feat(conformal): add calibrate phase, alpha grid fixed at 0.05/0.10

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01MoGpVqT5fDqauAMwAs78ze"
```

---

### Task 6: Report phase — apply the preregistered decision rule, then run for real

**Files:**
- Modify: `scripts/analysis/conformal_abstention_calibration.py`

**Interfaces:**
- Consumes: `reports/conformal-calibration-generate.json`, `reports/conformal-calibration-calibrate.json`
  (Tasks 4-5 output); `eval/golden/gate_v7.json` (existing, for the guardrail floors).
- Produces: `reports/conformal-calibration-report-2026-08-26.json` — the final, preregistration-§6-compliant
  verdict. This is the last task; no further code changes follow it in this plan.

- [ ] **Step 1: Write the report phase**

Add to `scripts/analysis/conformal_abstention_calibration.py`, above `def main():`:

```python
def _control_summary(rows: list[dict]) -> dict:
    """Current production behaviour, exactly as shipped -- no LOO recalibration, the
    fixed thresholds applied as-is (abstain_threshold and SEBI_RAG_SUBJ_THRESHOLD's
    production defaults). This is what Task 6's decision rule compares the calibrated
    arm against (spec Sec 2.2's fairness note: the comparison is intentionally
    asymmetric, in the direction that makes adoption HARDER, not easier)."""
    n = len(rows)
    correct = sum(1 for r in rows if r["abstained"] == r["abstain_gold"])
    false_answers = sum(
        1 for r in rows
        if not r["abstained"] and r["wrong_if_answered"] is True
    )
    return {
        "n": n,
        "abstention_accuracy": round(correct / n, 4) if n else 0.0,
        "false_answer_count": false_answers,
        "false_answer_rate": round(false_answers / n, 4) if n else 0.0,
    }


def _simulated_summary(rows: list[dict], score_floor_threshold: float,
                       subject_gate_threshold: float) -> dict:
    """Re-simulates each row's abstention decision under the CALIBRATED thresholds,
    reusing the already-dumped rerank_top/subject_sim (no pipeline re-run needed --
    these are pure threshold comparisons against fixed, already-computed scores).

    Mirrors generate.py:answer_with_abstention's gate ORDER exactly (score_floor first,
    then subject_gate, both must pass to answer) but does NOT re-derive non_sebi_domain
    or the HYBRID_THRESHOLD override -- those are untouched by this arm (spec Sec 1), so
    a row that hit either in production keeps that same outcome here; only rows whose
    production abstention_reason was "score_floor" or "subject_gate" (or that answered
    with both signals passing) are re-decided against the new thresholds.
    """
    n = len(rows)
    correct, false_answers = 0, 0
    for r in rows:
        if r["abstention_reason"] in ("no_context", "non_sebi_domain"):
            simulated_abstained = True  # untouched by this arm
        elif r["rerank_top"] is None or r["rerank_top"] < score_floor_threshold:
            simulated_abstained = True
        elif r["subject_sim"] is not None and r["subject_sim"] < subject_gate_threshold:
            simulated_abstained = True
        else:
            simulated_abstained = False
        if simulated_abstained == r["abstain_gold"]:
            correct += 1
        if not simulated_abstained and r["wrong_if_answered"] is True:
            false_answers += 1
    return {
        "n": n,
        "abstention_accuracy": round(correct / n, 4) if n else 0.0,
        "false_answer_count": false_answers,
        "false_answer_rate": round(false_answers / n, 4) if n else 0.0,
    }


def phase_report() -> None:
    if not GENERATE_DUMP.exists() or not CALIBRATE_DUMP.exists():
        raise SystemExit("both --phase generate and --phase calibrate must run first")
    gen = json.loads(GENERATE_DUMP.read_text())
    cal = json.loads(CALIBRATE_DUMP.read_text())
    gate_floors = json.loads(GATE.read_text())["floors"]

    rows = gen["rows"]
    control = _control_summary(rows)

    primary = cal["results"][f"alpha_{ALPHA_PRIMARY}"]
    sf_threshold = primary["score_floor"]["threshold"]
    sg_threshold = primary["subject_gate"]["threshold"]
    calibrated = _simulated_summary(rows, sf_threshold, sg_threshold)

    # spec Sec 3 CONFIRMATORY (diagnostic only, not a second adoption path per Sec 8):
    # do the three documented subject_gate false abstentions flip under the calibrated
    # subject threshold?
    watch_ids = {"v7-nt-013", "v7-nt-025", "v7-ls-029"}
    by_id = {r["id"]: r for r in rows}
    row_flips = {}
    for rid in watch_ids:
        r = by_id.get(rid)
        if r is None:
            row_flips[rid] = "not_in_golden_v7_rows_dump"
            continue
        if r["subject_sim"] is None:
            row_flips[rid] = "subject_sim_never_computed_in_production"
            continue
        was_abstained = r["abstained"]
        now_abstained = (
            r["abstention_reason"] in ("no_context", "non_sebi_domain")
            or r["rerank_top"] is None or r["rerank_top"] < sf_threshold
            or r["subject_sim"] < sg_threshold
        )
        row_flips[rid] = {
            "was_abstained": was_abstained, "now_abstained": now_abstained,
            "flipped_to_answered": was_abstained and not now_abstained,
        }

    accuracy_gain = calibrated["abstention_accuracy"] - control["abstention_accuracy"]
    false_answer_increased = calibrated["false_answer_count"] > control["false_answer_count"]

    verdict, reasons = "REJECT", []
    if accuracy_gain >= ABSTENTION_ACCURACY_EFFECT_FLOOR and not false_answer_increased:
        verdict = "PROCEED to Sec 7 full-gate confirmation"
    else:
        if accuracy_gain < ABSTENTION_ACCURACY_EFFECT_FLOOR:
            reasons.append(
                f"6.1: abstention_accuracy gained {accuracy_gain:.4f}, "
                f"needs >= {ABSTENTION_ACCURACY_EFFECT_FLOOR}")
        if false_answer_increased:
            reasons.append(
                f"6.2: false_answer_count rose {control['false_answer_count']} -> "
                f"{calibrated['false_answer_count']} (zero tolerance on increase)")
        if accuracy_gain < ABSTENTION_ACCURACY_EFFECT_FLOOR and not false_answer_increased:
            # spec Sec 6: "if 1 fails, still report the certified risk bound as the
            # qualitative deliverable" -- distinct from an adoption pass.
            verdict = "REJECT (primary null; certified risk bound reported per Sec 6)"

    out = {
        "spec": "docs/superpowers/specs/2026-08-26-conformal-abstention-calibration-design.md Sec 6",
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n": len(rows), "alpha_primary": ALPHA_PRIMARY, "alpha_secondary": ALPHA_SECONDARY,
        "effect_floor_abstention_accuracy": ABSTENTION_ACCURACY_EFFECT_FLOOR,
        "control": control, "calibrated": calibrated,
        "accuracy_gain": round(accuracy_gain, 4),
        "certified_risk_bounds_alpha_0_05": {
            "score_floor": primary["score_floor"],
            "subject_gate": primary["subject_gate"],
        },
        "certified_risk_bounds_alpha_0_10": cal["results"][f"alpha_{ALPHA_SECONDARY}"],
        "gate_floors_reference": gate_floors,
        "confirmatory_row_flips": row_flips,
        "verdict": verdict, "rule_failures": reasons,
    }
    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in
                      ("n", "control", "calibrated", "accuracy_gain", "verdict", "rule_failures")},
                     indent=2))
    print(f"\nwrote {DEST}", file=sys.stderr)
    print("\nNOTE: this verdict covers Sec 6 only. Sec 3's other gate floors "
          "(citation_recall, citation_precision, recall_at_k, context_recall, ndcg_at_10) "
          "must still be checked against a full eval_json_full run before Sec 7 "
          "confirmation -- this report does not run that eval.", file=sys.stderr)
```

Update `main()`'s phase dispatch dict:

```python
    {"generate": phase_generate, "calibrate": phase_calibrate,
     "report": phase_report}[args.phase]()
```

- [ ] **Step 2: Run report against the n=20 smoke dumps from Task 5, verify no crash**

Run: `PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase report`

Expected: prints a verdict (likely REJECT at n=20 — too small to be meaningful, this is a
mechanics check only) and writes `reports/conformal-calibration-report-2026-08-26.json`.

- [ ] **Step 3: Run the real generate phase — all 260 rows, no `SEBI_ROW_LIMIT`**

Run (background — ~40min per the established `eval_json_full` baseline):
```bash
PYTHONPATH=src TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 HF_HUB_DISABLE_XET=1 python scripts/analysis/conformal_abstention_calibration.py --phase generate
```

Expected: `reports/conformal-calibration-generate.json` with `"n": 260`.

- [ ] **Step 4: Run the real calibrate and report phases**

```bash
PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase calibrate
PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase report
```

Expected: no `ValueError` (n=260 is well above the α=0.05 floor of 1/261≈0.0038). Read the printed
verdict.

- [ ] **Step 5: Run the full offline test suite to confirm no regressions**

Run: `PYTHONPATH=src TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 python -m pytest -q -m "not integration"`

Expected: the pre-existing baseline (885 passed, 2 skipped, 3 deselected, 4 unrelated pre-existing
failures per `docs/status.md` 2026-08-25) plus this plan's 11 new `test_conformal.py` tests, all
passing. If any of the 4 pre-existing failures differ from that baseline, stop and investigate
before proceeding — do not attribute a new failure to "pre-existing" without re-confirming via
`git stash` first, per this project's `superpowers:verification-before-completion` convention.

- [ ] **Step 6: Record the outcome — commit, then update the spec and status.md**

```bash
git add scripts/analysis/conformal_abstention_calibration.py reports/conformal-calibration-generate.json reports/conformal-calibration-calibrate.json reports/conformal-calibration-report-2026-08-26.json
git commit -m "feat(conformal): run R7 calibration on golden_v7 (n=260), record verdict

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01MoGpVqT5fDqauAMwAs78ze"
```

Then, by hand (not scripted — this is narrative documentation, matching this project's own
convention for every prior arm in this repo):

1. Fill in `docs/superpowers/specs/2026-08-26-conformal-abstention-calibration-design.md`'s §10
   OUTCOME section with the actual numbers from `reports/conformal-calibration-report-2026-08-26.json`
   — the real `control`/`calibrated`/`accuracy_gain`/`verdict`, not a paraphrase.
2. Add a dated entry to `docs/status.md`'s "Last Updated" section (prepend, newest-first, matching
   every existing entry's format) summarizing the verdict, the certified risk bounds, and — if
   `verdict` starts with `REJECT` — that this is a rejection, not a promising direction (per the
   spec's §8 "not permitted" list: a §6-failing result must not be recorded as directionally
   positive).
3. If and only if `verdict` is `"PROCEED to Sec 7 full-gate confirmation"`: **do not** write the
   calibrated values into `config.toml` yet. Per the spec's §7, that requires a separate full
   `eval_json_full` (n=260) run confirming `floors_ok: true` on every other gate metric first — stop
   here and report the PROCEED verdict back for a decision on whether to continue to that
   confirmation step, since it is explicitly out of scope for this plan.

- [ ] **Step 7: Final commit for the documentation update**

```bash
git add docs/superpowers/specs/2026-08-26-conformal-abstention-calibration-design.md docs/status.md
git commit -m "docs: record R7 conformal calibration outcome

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01MoGpVqT5fDqauAMwAs78ze"
```

---

## Explicitly Out of Scope for This Plan

- Writing calibrated threshold values into `config.toml` / `SEBI_RAG_SUBJ_THRESHOLD` (adoption —
  spec §7, gated on a full `eval_json_full` confirmation this plan does not run).
- Any change to `generate.py`'s AND-gate combination logic, `_is_non_sebi_domain`, or
  `superseded_penalty`.
- Re-deriving `gate_v7.json`'s floors (not needed — this arm changes neither the generator, the
  reranker, nor the citation scorer; spec §7).
- A joint/combined risk score replacing the two-signal AND-gate (spec §1 — rejected in advance).
