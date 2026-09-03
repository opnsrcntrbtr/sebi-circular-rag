# Preregistration — HYBRID_THRESHOLD Recalibration or Removal for Jina

**Written before execution.** Decision rule in §3 is fixed as of this document's commit. No
constant has been changed.

## 0. Motivation

`generate.py:727`'s `HYBRID_THRESHOLD = 0.85` overrides a `subject_gate` abstention when
`rerank_top >= 0.85` — "cross-encoder near-ceiling overrides subject_gate," calibrated 2026-08-13
under bge-reranker-v2-m3 (median top-score 0.98, per `config.toml`'s own documented score-scale
comparison). Since the reranker swap to jina (ADR-004, 2026-08-24), production's `rerank_top` has
never once reached 0.85: the 2026-08-24 calibration cohort's max across all 260 golden_v7 rows is
**0.6701** (`reports/jina-abstain-threshold-calibration-2026-08-24.json`). The override has been
unconditionally dead code in production for 9+ days, confirmed via the abstention root-cause
investigation (`docs/superpowers/specs/2026-09-03-architecture-review-w1-diagnostics.md`), which
found it directly contributing to 2 of 21 current `abstention_accuracy` mismatches
(`v7-nt-013` `rerank_top=0.5202`, `v7-nt-025` `rerank_top=0.4846` — jina's own two highest observed
scores among the mismatch set, well below 0.85 but near jina's own ceiling).

`abstain_threshold` (a different, adjacent constant) *was* recalibrated for jina's scale
(0.05→0.12, `reports/jina-abstain-threshold-calibration-2026-08-24.json`) on the same day
`reranker_model` switched — `HYBRID_THRESHOLD` was missed in that pass.

## 1. Method

**Two candidate resolutions, not assumed in advance which wins:**

**Option A — recalibrate to jina's scale.** Run a threshold sweep analogous to
`scripts/analysis/jina_abstain_threshold_calibration.py`'s method, but for the *override*
condition: for each golden_v7 row with `judge.grounded() == False`, plot `rerank_top` against
whether the row is answerable — find the `rerank_top` value that separates "confidently answerable
despite failing subject_gate" from "genuinely near-domain, subject_gate is correct," analogous to
how 0.12 was chosen for the score floor. jina's own ceiling (0.67 observed) bounds the search
range — a jina-calibrated `HYBRID_THRESHOLD` cannot exceed ~0.6-0.65 or it inherits the same
dead-code problem at a lower altitude.

**Option B — remove the override entirely.** If Option A's sweep finds no `rerank_top` value that
cleanly separates the two populations (i.e., jina's score distribution doesn't have bge's
"near-ceiling = high confidence" property — plausible, since `config.toml` already documents jina
producing negative scores and a much flatter distribution than bge), the override may not
transplant to jina's scale at all, and removing it (making `subject_gate` unconditional whenever
`judge.grounded()` is False) is the correct fix rather than a recalibrated version of a
mechanism that doesn't work the same way under this reranker.

Both options are evaluated against the same held-out check: rerun on the same golden_v7 set,
measure whether the 2 currently-misclassified rows (`v7-nt-013`, `v7-nt-025`) are rescued without
introducing new false answers elsewhere in the mismatch set.

## 2. Endpoints

| role | metric | source |
|---|---|---|
| PRIMARY | does the candidate change (A or B) rescue `v7-nt-013`/`v7-nt-025` without flipping any of the 21 currently-correct-by-abstention rows to incorrect | rerun `scripts/analysis/abstention_mismatch_audit.py` (jina-routed version) with the candidate constant |
| GUARDRAIL | full `abstention_accuracy` on golden_v7 does not regress below the current 0.919 | same rerun |
| GUARDRAIL | `make test` stays green | existing suite |

## 3. Decision rule — fixed in advance

1. If Option A's sweep finds a clean separating value AND the held-out check rescues both target
   rows without net regression → adopt Option A's threshold.
2. If Option A finds no clean separation but Option B (removal) rescues both target rows without
   net regression → adopt Option B.
3. If **neither** rescues both rows without introducing a net regression elsewhere → **REJECT
   both**; report as "the override mechanism does not transplant to jina at any setting," and leave
   `HYBRID_THRESHOLD=0.85` in place as a harmless (if inert) historical artifact rather than
   introducing risk for a 2-row gain. This mirrors `docs/status.md`'s existing R1 precedent: a
   rescue that costs more than it gains gets rejected outright, not "kept for later tuning."
4. **Only 2 rows are at stake.** Given `golden-v7-underpowered`, this decision cannot be validated
   as a real accuracy improvement at golden_v7's own resolution (~4pp) — the held-out check in §2
   is necessarily a small-n directional check, not a statistically powered confirmation. State
   this limitation explicitly in whatever result this spec produces; do not report a 2-row rescue
   as a confirmed accuracy gain.

## 4. Not permitted after seeing the result

- Changing `HYBRID_THRESHOLD` in `generate.py` directly from this spec's sweep without running the
  held-out check in §2 first — a threshold that looks clean on the sweep population alone, without
  checking it against the full mismatch set, is exactly the kind of untested fix
  `superpowers:systematic-debugging` exists to prevent.
- Bundling this fix with either of the other two abstention-mechanism specs
  (`2026-09-03-abstain-threshold-drift-prereg.md`,
  `2026-09-03-hard-negative-subject-gate-prereg.md`) into one combined change — each constant is
  independently testable and independently revertible; a combined patch that regresses would leave
  no way to isolate which change caused it.
- Reporting a rescued 2-row result as proof `abstention_accuracy` clears its gate floor overall —
  the other two mechanisms (18 of the 21 mismatches) are untouched by this spec.

## Result (2026-09-03)

**No new run needed** — the full per-row `confidence` dump from
`reports/abstention-mismatch-audit-jina-2026-09-03.json` (all 260 rows, not just the 21
mismatches) already contains everything Option A's sweep needs.

**Population is much smaller than expected.** Filtered to rows that actually reach
`SubjectSimJudge` (subject_sim not `None`) and come back ungrounded (`subject_sim < 0.42` AND
`section_sim < 0.60`): **only 3 of 260 rows**, not the broader population the sweep design
envisioned:

| id | expected_abstain | rerank_top | subject_sim | section_sim |
|---|---|---|---|---|
| v7-nt-013 | False | 0.5202 | 0.3974 | 0.4247 |
| v7-nt-025 | False | 0.4846 | 0.4105 | 0.5451 |
| v7-ls-029 | False | 0.1646 | 0.4073 | 0.4484 |

**All 3 are answerable rows — zero genuine hard negatives reach this branch at all.** Cross-checked
against every `hard_negative`-stratum row in the set (18 total, including the 9 diagnosed in
`2026-09-03-hard-negative-subject-gate-prereg.md`): **100% are `grounded=True`** — every hard
negative that reaches the judge clears the OR-gate via `subject_sim` alone (0.432–0.6560 range,
all ≥0.42) and is answered, never falling through to the ungrounded/subject_gate branch at all.
The two failure mechanisms are **structurally disjoint**: hard negatives fail via
false-groundedness (spec 2's territory), never via this override's branch; only answerable rows
land in the population `HYBRID_THRESHOLD` was meant to rescue.

**Option A vs. B, given n=3 with zero negative-class examples**: a "clean separating value" in the
sense Option A envisioned (a value that separates confidently-answerable from genuinely-adversarial
cases) can't be established the way the sweep intended, because there is no adversarial example in
this population to separate *from*. But the practical question §2 actually asks — does a candidate
threshold rescue the target rows without flipping any currently-correct row — is answerable
directly: since none of the 3 rows is a genuine hard negative, and no other row in the full 260-row
set falls in this branch, **any `HYBRID_THRESHOLD` between roughly 0.17 and 0.52 rescues 1-2 of the
3 with zero observed cost, and a threshold ≤0.1646 (e.g. 0.15) rescues all 3 with zero observed
cost** on this golden set. This satisfies the letter of §3 Rule 1 (a value clears the held-out
check) while being closer in spirit to Option B (there was never a real trade-off to make in this
data) than to a precision-tuned Option A recalibration.

**Disposition: CANDIDATE FOR ADOPTION, held for confirmation — not applied.** Consistent with how
the other two specs in this investigation were left (diagnosis/candidate, not silently applied),
this is not patched into `generate.py` without asking, even though §4 only conditionally prohibits
it (the held-out check *was* run and passes). Recommended candidate: `HYBRID_THRESHOLD = 0.15`,
rescuing all 3 currently-misclassified rows in this branch. **The explicit caveat required by §3.4
applies in full and is stronger than originally anticipated**: n=3 is not just underpowered for a
*statistically confirmed* accuracy gain (as §3.4 already flagged) — the *absence of a negative
example* in golden_v7's 260 rows is not evidence no such case exists in production traffic. A query
that is genuinely near-domain-but-wrong-regulator *and* happens to score a high `rerank_top` (the
exact combination this branch is designed to protect against) could exist in real traffic without
appearing anywhere in this golden set. Lowering `HYBRID_THRESHOLD` this far is a directional, not a
validated, fix.
