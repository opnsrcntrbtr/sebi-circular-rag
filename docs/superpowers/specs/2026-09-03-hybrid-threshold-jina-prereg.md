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
