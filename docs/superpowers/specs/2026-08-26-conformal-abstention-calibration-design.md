# Design + Preregistration — R7: conformal-calibrated abstention thresholds

**Written before execution.** This document is both the architectural design (per
`superpowers:brainstorming`) and the preregistered experiment spec (per this project's own
convention — `docs/superpowers/specs/`). Decision rule (§6) and the not-permitted list (§8) are
fixed as of this document's commit. No calibration has been run; no code has been written.
**Implementation is out of scope for this document** — per the chosen process, this hands off to
`superpowers:writing-plans` for a reviewable implementation plan (TDD steps, checkpoints) rather
than executing immediately, unlike the jina-B′ arm (2026-08-25) which ran in the same session.

Roadmap: `docs/research-roadmap-2026-08-19.md` R7 ("calibrated abstention instead of fitted
thresholds"), pursued after R6 (late chunking) and R5 (tables at ingest) were both gated out in
this same session (`docs/status.md` 2026-08-26) by their own preconditions before any design work
started on either.

---

## 0. Why this, and why now

The repo's own words on the two hand-fit gate thresholds: *"any threshold picked here is fitted to
the observed maximum — textbook overfitting"* (status.md, 2026-08-13). Two independent lines of
evidence back this up:

- **Threshold tuning is measured dead, twice**, on both signals: subject threshold 0.42→0.40 is net
  zero (rescues 2, releases 2 — interleaved bands); relaxing `score_floor` answers 13 abstain rows
  but releases 13 false positives (2026-08-13). Both searches were exhausted by grid sweep, not by
  a principled stopping rule.
- **The gate is a conjunction** (`rerank_top ≥ floor` **AND** subject/section gate), so either
  noisy signal vetoes alone — and this session's two gated-out candidates (R6, R5) both
  independently surfaced the same live symptom: `v7-nt-013`, `v7-nt-025` (this session,
  `reports/r5-numeric-table-gate-2026-08-26.json`) and `v7-ls-029` (2026-08-13) are all
  `subject_gate` false abstentions, undiagnosed by anything else in the roadmap.

**What R7 is not claiming.** This is not a claim that conformal calibration will rescue those
specific 3 rows, or move `abstention_accuracy` by a large margin — per the chosen success bar
(§6), it is held to the same effect-floor-and-guardrail standard as every other arm, and the
boundary-case count in golden_v7 is small (single digits) by construction, so a large accuracy
delta is not expected. The value being tested is **provenance**: a threshold with a stated,
finite-sample risk bound versus one selected by grid search against the same data it is now
being defended with — a materially different property for a tool this project's own refusal
criteria hold to a "golden rule": *"When in doubt, say 'I don't know based on the available
evidence.'"*

---

## 1. What this is not

- **Not a new combined risk score.** 2026-08-26 research check found `UR-RAG` (June 2026, fuses
  four runtime signals into one calibrated score) and `BalanceRAG` (arXiv:2605.20084, joint risk
  calibration for cascaded RAG) — both closer to a from-scratch redesign of the gate's combination
  logic. **Rejected in advance**: bigger change, more validation risk, and the AND-gate's
  conjunction structure is not what's implicated by the evidence in §0 — the *thresholds* are.
- **Not a hard train/calibration split of golden_v7.** Splitting n=260 in half would leave the
  already-single-digit boundary cases concentrated unpredictably in one half or the other. Chosen
  instead: full-data reuse via jackknife+ (§3).
- **Not a change to the AND-gate's combination logic**, `_is_non_sebi_domain`, or
  `superseded_penalty`. Single variable: where the two threshold *values* come from.
- **Not a generator change.** Both signals (`rerank_top`, `subject_sim`/`section_score`) are
  computed independently of which generator produces the answer text (`rerank.py`, `generate.py`'s
  `SubjectSimJudge`) — R0's lesson (generator swaps can't move signals they don't touch) applies
  here by construction, not by re-derivation.

---

## 2. Method

### 2.1 The calibration primitive: Conformal Risk Control + jackknife+

**Conformal Risk Control** (Angelopoulos, Bates, Fisch, Lei, Schuster; [arXiv:2208.02814](https://arxiv.org/abs/2208.02814),
ICLR 2024) generalizes split conformal prediction to control the expected value of *any monotone
loss function*, not just miscoverage — verified via primary source: the paper's own framing is
threshold selection such that `E[loss(threshold)] ≤ α` holds with a finite-sample guarantee, tight
up to O(1/n). **C-RAG** ([arXiv:2402.03181](https://arxiv.org/pdf/2402.03181)) confirms this
applies to "general bounded risk functions" in a RAG generation setting specifically — verified via
primary-source fetch of the abstract, which certifies "an upper confidence bound of generation
risks" for such functions. This is the right tool for the score-floor and subject-gate thresholds
because both are already monotone: raising `rerank_top`'s floor only ever *removes* answered rows
from consideration (never re-admits one that a lower floor excluded), and the same holds for the
subject-gate threshold. Monotonicity is what makes a single scalar threshold search well-posed for
risk control, and it is what the current hand-fit thresholds already assume implicitly.

**Jackknife+** (Barber, Candès, Ramdas, Tibshirani; [arXiv:1905.02928](https://arxiv.org/abs/1905.02928),
*Annals of Statistics* 49(1), 2021) supplies the small-sample answer: rather than a single
calibration/test split, it uses **every** observation for both fitting and calibration via
leave-one-out folds, and proves valid marginal coverage under exchangeability for any
symmetric-in-the-data fitting procedure — the standard citation for "the dataset is too small to
split cleanly." Applied here: for `i = 1..260`, fit the conformal-risk-controlled threshold on the
other 259 rows, and record what row *i*'s **held-out** decision would have been. This is what makes
the eventual evaluation honest rather than circular (§0's exact worry) — each row's correctness
check happens on a threshold that never saw that row.

### 2.2 Two independent applications, not one joint procedure

Per the chosen scope (§1: no new combined score), the primitive from §2.1 is applied **twice**,
once per existing signal, each with its own risk definition:

| signal | current value | risk controlled | monotone direction |
|---|---|---|---|
| `rerank_top` / `score_floor` (`Settings.abstain_threshold`) | 0.05 (bge) / 0.12 (jina, recalibrated 2026-08-24) | **false-answer rate**: among rows with `rerank_top ≥ floor` (i.e. answered), the fraction that are wrong/ungrounded | raising the floor only removes answered rows |
| `subject_sim` / `section_score` (`SEBI_RAG_SUBJ_THRESHOLD`, `SEBI_RAG_SECT_THRESHOLD`) | 0.42 / 0.60 | **false-abstention rate**: among rows with `subject_sim < threshold` (i.e. abstained on this signal), the fraction that were actually answerable and correctly grounded | raising the threshold only removes rows from the "passes" set |

The AND-gate combination in `generate.py` is untouched — this only replaces where the two numbers
in `config.toml` / `SEBI_RAG_SUBJ_THRESHOLD` come from.

**⚠️ Fairness of the eventual comparison.** The *current* hand-fit values were themselves derived by
grid search against this same golden_v7 set (2026-07-30 through 2026-08-13 entries in status.md).
Evaluating the calibrated thresholds honestly (via jackknife+'s per-row held-out decisions, §2.1)
and then comparing against the *fixed, already-shipped* current thresholds applied as-is to the
same rows is the fair comparison — it does not re-derive the current thresholds under the same
held-out discipline (they are production constants, not a procedure to re-run), and does not need
to, since production already applies them as fixed constants to every incoming row regardless of
fold.

**⚠️ Known asymmetry, stated rather than discovered later.** This comparison is not symmetric, and
the asymmetry cuts *against* adoption, not for it: the current fixed thresholds get whatever
in-sample advantage their original grid search over this same 260-row set already bought them,
while the calibrated thresholds are held to an honest, held-out standard by construction. A
calibrated arm that still clears §6's effect floor under that harder standard is real evidence;
the reverse asymmetry (calibrated arm getting an unfair advantage) is not possible here. This is a
conservative bias in the experiment's design, not a flaw to fix.

### 2.3 What data feeds calibration

Fresh per-row scores under **current production** — Jina reranker (ADR-004), recalibrated
`abstain_threshold=0.12` — not the `reports/score-floor-utility-2026-08-19.json` dump, which
predates both. Per-row fields needed: `rerank_top` (already computed pre-gate in
`answer_with_abstention`), `subject_sim`/`section_score` (from `SubjectSimJudge`), and ground truth
(`abstain: bool` from golden_v7, cross-checked against whether the row was in fact correctly
grounded when answered — reusing `_measure`'s zero-cite/citation_recall logic from the jina cohort
script, §9). All 260 rows (both abstain and answerable) are in scope, since both signals fire on
every row regardless of the gold label.

---

## 3. Endpoints

| role | metric | note |
|---|---|---|
| **PRIMARY** | `abstention_accuracy`, honest (jackknife+ leave-one-out) estimate for the calibrated thresholds vs the fixed current thresholds applied to the same 260 rows | matches this project's existing gate metric definition (`score.py`) exactly, so the comparison is apples-to-apples with `gate_v7.json`'s own floor |
| **GUARDRAIL** | false-answer rate (rows answered where the answer is wrong/ungrounded) | **zero tolerance on increase** — the legal-risk-critical direction; a calibrated threshold that trades this away for a headline accuracy number is not an improvement for this project |
| **GUARDRAIL** | `citation_recall`, `citation_precision`, `recall_at_k`, `context_recall`, `ndcg_at_10` | must not fall below their armed floors (`gate_v7.json`) — expected invariant by construction, since neither calibrated signal touches retrieval, reranking, or citation selection, but checked rather than assumed (§0's own lesson) |
| SECONDARY | the certified risk bound itself (`α` achieved per Conformal Risk Control's guarantee) for each of the two thresholds | reported as the qualitative deliverable even if the primary is null — this is the "principled provenance" half of §0's claim |
| CONFIRMATORY | whether `v7-nt-013`, `v7-nt-025`, `v7-ls-029` (the three documented `subject_gate` false abstentions) flip under the calibrated subject threshold | diagnostic only, not a second adoption path (same discipline as the jina-B′ spec's §8) |

---

## 4. Arms

**Control** — current fixed thresholds (`abstain_threshold`, `SEBI_RAG_SUBJ_THRESHOLD`/
`SEBI_RAG_SECT_THRESHOLD`), applied as-is. Production today.

**C1** — conformal-risk-controlled score-floor threshold (jackknife+, target risk levels swept
across a small preregistered grid — e.g. α ∈ {0.05, 0.10} — chosen for interpretability against
the existing floor's observed behavior, not fitted post-hoc to the result).

**C2** — conformal-risk-controlled subject-gate threshold, same jackknife+ procedure, its own risk
definition (§2.2).

**C1+C2** — both calibrated thresholds active simultaneously (the deployable configuration, since
production runs the AND-gate with both signals live).

**Rejected in advance:**
- Sweeping the target risk level α *after* seeing which value produces the best headline number —
  the grid must be fixed here, in this document, before any calibration runs (§8).
- Combining C1 and C2 into a single joint threshold search — rejected in §1 as a scope change.
- Re-deriving `gate_v7.json`'s floors under this arm unless C1+C2 is adopted (§7, mirrors the
  jina-B′ spec's §7 reasoning: this arm does not change the generator, so unlike R1 it does not
  require a floor re-derivation to measure against).

---

## 5. Testing (TDD) — for the implementation plan, not run here

- `jackknife_plus_quantile(scores, alpha)` against **synthetic data with a known closed-form
  quantile** (e.g. uniform or Gaussian scores where the target quantile is analytically known) —
  proves the primitive is correct independent of any golden_v7 data.
- `calibrate_score_floor` / `calibrate_subject_gate` against **fake per-row score/label fixtures**
  (offline, no model — mirrors this codebase's `_FakeReranker` convention), covering: monotonicity
  is respected, the leave-one-out held-out decision never uses the row it's evaluating, and the
  degenerate case (all rows on one side of a candidate threshold) does not crash.
- No changes to `generate.py`'s gate logic itself, so no new production-path integration tests are
  needed unless C1+C2 is adopted, at which point the change is exactly two config constants — the
  same "shipped inert until adopted" pattern every prior arm in this repo follows.

---

## 6. Decision rule — fixed in advance

Adopt **C1+C2** (not C1 or C2 individually — the AND-gate runs both in production) **only if all
three hold**, evaluated at whichever α ∈ {0.05, 0.10} was preregistered as primary before running
(pick one now, not after seeing results — **α = 0.05** is primary, matching this project's existing
`score_floor` scale and the field's typical default; α = 0.10 is reported as a secondary sensitivity
check only):

1. **`abstention_accuracy` (honest, jackknife+ held-out) increases by ≥ +0.01 absolute** over the
   fixed current thresholds on the same 260 rows. Smaller than the jina-B′ arm's +0.02 citation
   floor, deliberately — `abstention_accuracy`'s current armed floor (0.9412) and observed
   production value (0.981, `full-eval-2026-08-15.json`) already sit close to ceiling, so the
   achievable headroom is narrower than citation_precision's was. A floor set at the citation
   arms' +0.02 would be unreachable by construction, which is itself a form of guardrail-gaming
   forbidden by §8 — better to set a floor that is meaningful at this metric's actual headroom and
   report honestly if even +0.01 isn't cleared.
2. **False-answer rate does not increase.** Zero tolerance on direction — mirrors every prior arm's
   most important guardrail, and is the one this project's refusal criteria treat as non-negotiable
   ("no fabrication... never guess").
3. **No other gate floor falls below `gate_v7.json`**, checked (not assumed) even though §3 expects
   invariance by construction.

**If 1 holds but 2 or 3 fails → REJECT.** Recorded as rejected, not "promising."

**If 1 fails → still report the certified risk bound (§3 secondary) as the qualitative deliverable**,
explicitly distinguished from an adoption recommendation. This is the one arm in this project's
history where a null on the primary does not make the whole exercise a no-op, provided the
guardrails hold — a documented, finite-sample-guaranteed threshold has standalone value for a legal
tool even without an accuracy gain, but that value is reported as exactly that, not inflated into a
pass on §6.

---

## 7. Confirmation required before adoption

C1+C2 clearing §6 is **not** adoption. Required before arming `config.toml` /
`SEBI_RAG_SUBJ_THRESHOLD`:

- Full `eval_json_full` (n=260) against the armed floors, `floors_ok: true`.
- No gate re-derivation needed (§4) — this arm does not change the generator, reranker, or citation
  scorer, so `gate_v7.json`'s floors remain valid to measure against, unlike R1 which introduced a
  second generator into the citation path.

---

## 8. Not permitted after seeing the result

- Changing the primary endpoint, the α grid, the +0.01 effect floor, or which α is primary.
- Re-running jackknife+ with a different risk definition for either signal and reporting that
  instead.
- Reporting a §6-failing result as "directionally positive," or the qualitative certified-bound
  deliverable (§6, "if 1 fails") as if it were an adoption pass.
- Cherry-picking the confirmatory row-flip check (§3) as an adoption basis if the primary fails.
- Sweeping `superseded_penalty`, `citation_margin`, or any other unrelated constant "while we're in
  here" — single variable per arm, this project's standing rule since the `superseded_penalty`
  precedent.

---

## 9. Implementation notes (for the plan, not executed by this document)

**Files (planned, not yet written):**
- `src/sebi_rag/conformal.py` — `jackknife_plus_quantile`, `calibrate_score_floor`,
  `calibrate_subject_gate`, `CalibrationResult` dataclass (threshold, target_alpha, certified risk
  bound, n, method citation string). Pure functions, no model dependency — offline calibration
  library, analogous to how `scripts/golden_v7/derive_thresholds.py` is a standalone calibration
  script rather than a runtime component.
- `scripts/analysis/conformal_abstention_calibration.py` — three-phase, matching this repo's
  established pattern (`warrant_scorer_cohort.py`, `jina_citation_scorer_cohort.py`): a
  **generate** phase producing fresh per-row `rerank_top`/`subject_sim`/ground-truth records under
  current production; a **calibrate** phase running the two jackknife+ procedures over that dump
  (no model loaded — pure computation, can rerun cheaply without regenerating); a **report** phase
  applying §6 mechanically.
- `tests/test_conformal.py` — new file, §5's TDD suite.
- No change to `generate.py`, `pipeline.py`, `settings.py`'s gate logic — only `config.toml` /
  `SEBI_RAG_SUBJ_THRESHOLD` values change, and only on adoption (§7).

**Hard constraints.** No new field on `CircularMeta`. No edit to `*_spaces.py` or root `app.py`. No
change to the AND-gate's combination logic (§1).

**Cost premise.** Cheap relative to every prior arm in this session: no re-encode (unlike R6), no
7B judge (unlike R1), no new model residency (unlike the jina-B′ arm before its reuse-wiring). The
generate phase is one production pipeline pass over 260 rows (~40min per the established
`eval_json_full` baseline); the calibrate phase is pure numpy, seconds; jackknife+'s O(n) leave-
one-out folds are 260 threshold re-fits over already-computed scalar scores, not 260 model calls.

---

## 10. OUTCOME (recorded after execution)

**❌ REJECTED 2026-08-26.** Plan `docs/superpowers/plans/2026-08-26-conformal-abstention-calibration.md`,
executed inline (`superpowers:executing-plans`). Script
`scripts/analysis/conformal_abstention_calibration.py`, reports `reports/conformal-calibration-
generate.json`, `-calibrate.json`, `-report-2026-08-26.json`. Full golden_v7 (n=260); score-floor
calibration set 254 rows (6 excluded — abstained or no gold citations to check "wrong_if_answered"
against), subject-gate calibration set 228 rows (32 excluded — subject_sim never computed, i.e.
short-circuited by score_floor or non_sebi_domain first).

**Certified thresholds at α=0.05 (primary):** score_floor **0.2692** (production: 0.12),
subject_gate **0.4482** (production: 0.42) — both LOO held-out risk estimates (0.0472, 0.0439)
close to the 0.05 target, confirming the calibration procedure itself worked correctly.

| metric | control (production, fixed) | calibrated (α=0.05, honest LOO-fit) | delta | rule |
|---|---|---|---|---|
| abstention_accuracy | 0.9654 | **0.7154** | **−0.2500** | §6.1 needs ≥ +0.01 ❌ |
| false_answer_count | 21 | **10** | −11 | §6.2 (no increase) ✅ |
| false_answer_rate | 0.0808 | 0.0385 | −0.0423 | — |

**Verdict: REJECT, decisively, on §6.1 alone** (§6.2 passes — false answers actually fell). The
calibrated score-floor threshold (0.2692) is more than double production's recalibrated Jina floor
(0.12); applied honestly it turns a large fraction of genuinely-answerable rows into false
abstentions, costing 25 percentage points of overall accuracy to buy an 11-row reduction in wrong
answers. This is not a marginal miss — it is CRC correctly doing what it was asked (controlling
false-answer risk at 5%) at a cost to coverage this application's operating point does not accept.

**Confirmatory check (§3, diagnostic only):** none of the three documented `subject_gate` false
abstentions flip to answered under the calibrated threshold — `v7-nt-013` and `v7-nt-025` remain
abstained (calibrated subject_gate threshold 0.4482 is *stricter* than production's 0.42, so if
anything it moves away from rescuing them); `v7-ls-029` was not abstained in this run at all
(production behaviour differs from the 2026-08-13 diagnosis it was recorded under — plausibly from
intervening changes, e.g. ADR-004's Jina adoption — not investigated further here, diagnostic only
per §8). The arm's own motivating cases are not rescued, consistent with the primary result.

**What this establishes.** The repo's fitted thresholds (0.12, 0.42) were not simply unprincipled —
on this evidence they sit at a materially more permissive point on the risk/coverage trade-off than
a 5%-false-answer-risk conformal target would select, and that permissiveness is load-bearing for
overall accuracy. A looser α (0.10) was recorded as a secondary sensitivity check per §6 but is
**not** promoted to primary post-hoc (§8) — the report captured it (score_floor 0.1638, subject_gate
0.4776 at α=0.10) for the record, not as a second adoption path.

**Not permitted and not done:** no re-running with a different α as primary, no cherry-picking the
α=0.10 secondary run to rescue the result, no re-deriving `gate_v7.json` (this arm changes neither
generator, reranker, nor citation scorer — §7 was correctly never needed since the primary rejected
before reaching confirmation).

**Shipped, and stays inert.** `src/sebi_rag/conformal.py` (`crc_threshold`, `CalibrationResult`,
`jackknife_plus_quantile`, `calibrate_score_floor`, `calibrate_subject_gate`), 12 offline tests
(`tests/test_conformal.py`, including a real boundary-condition fix caught by the plan's own
smoke-testing discipline — see the plan's Task 5 commit), and the three-phase analysis script.
`config.toml` / `SEBI_RAG_SUBJ_THRESHOLD` untouched — production's fitted thresholds remain in
place. 893 tests pass (881 baseline + 12 new), no regressions; the calibration library itself
(`conformal.py`) is now available for any future arm that needs Conformal Risk Control on a
different signal, even though this specific application of it did not clear adoption.
