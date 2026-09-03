# Preregistration — abstain_threshold Post-Corpus-Growth Drift Check

**Written before execution.** Decision rule in §3 is fixed as of this document's commit. No
threshold has been changed.

## 0. Motivation

`docs/superpowers/specs/2026-09-03-architecture-review-w1-diagnostics.md`'s abstention root-cause
investigation found 8 of 21 `abstention_accuracy` mismatches are false abstentions via
`score_floor`, with `rerank_top` clustered tightly at 0.0499–0.1135 — just under
`abstain_threshold = 0.12` (`config.toml`). That threshold was calibrated 2026-08-24
(`scripts/analysis/jina_abstain_threshold_calibration.py`,
`reports/jina-abstain-threshold-calibration-2026-08-24.json`) against the **730-circular** corpus,
documented at calibration time to cost "1 of 219 false abstentions." The corpus grew to 1,490
circulars on 2026-08-28 — four days later. The live measurement now shows 8 score-floor false
abstentions, an 8x increase over the calibration-time cost estimate. This spec checks whether that
increase is attributable to the score distribution shifting under corpus growth (a stale
threshold) or to something else (query mix, chunker changes) before touching the threshold.

## 1. Method

**Step 1 — reproduce the calibration, unchanged code, current corpus.** Re-run
`scripts/analysis/jina_abstain_threshold_calibration.py` against the live (1,490-circular) index,
without changing `abstain_threshold`. Compare its `score_distribution` (min/max/percentiles)
against the 2026-08-24 report's own `score_distribution`. This isolates "did the distribution
move" from "did the threshold's cost estimate become wrong" — the former is a necessary condition
for the latter, and is cheap to check first (a percentile shift with no cost-count change would
falsify the drift hypothesis outright).

**Step 2 — recompute the false-abstention cost at threshold=0.12 on the current corpus** using
the same calibration script's own curve output (`recommended_threshold`, `curve` fields already
computed by the existing script — no new code needed for this step, only a fresh run).

**Step 3 (only if Step 1/2 confirm drift) — recompute the calibration curve fresh** and compare
the resulting `recommended_threshold` against the current 0.12. If they materially differ, that is
the candidate new threshold; if they don't, the false-abstention increase is not explained by
corpus-driven score drift and this spec's hypothesis is rejected.

## 2. Endpoints

| role | metric | source |
|---|---|---|
| PRIMARY | false-abstention count at threshold=0.12 on current (1,490) corpus vs. 2026-08-24 report's "1 of 219" | fresh `jina_abstain_threshold_calibration.py` run |
| PRIMARY | score_distribution min/max/percentile shift, old corpus vs. current | same run, diffed against `reports/jina-abstain-threshold-calibration-2026-08-24.json` |
| GUARDRAIL | true-abstention catch rate at any candidate new threshold must not fall below 0.12's current 25/41 (the 2026-08-24 report's own catch rate) | same curve output |

## 3. Decision rule — fixed in advance

1. If Step 1/2 shows **no material score-distribution shift** and the false-abstention count at
   0.12 is close to the original "1 of 219" estimate (i.e., the live 8-row count is not explained
   by threshold miscalibration) → **REJECT** this hypothesis; the 8 false abstentions have a
   different cause (report as unexplained, do not force-fit a threshold story).
2. If Step 1/2 shows a **material shift** and a fresh curve computation (Step 3) recommends a
   threshold that: (a) reduces false-abstention count below the current 8, AND (b) does not drop
   true-abstention catch rate below 25/41 → **candidate for adoption**, but adoption itself
   requires a follow-up prereg (this spec is diagnostic only, per the not-permitted list below).
3. If (a) holds but (b) fails (catch rate drops) → **REJECT**, matching `docs/status.md`'s R1
   precedent (2026-08-19): a threshold move that trades away true-abstention catches to rescue
   false ones is the same rejected trade-off in the opposite direction.

## 4. Not permitted after seeing the result

- Changing `abstain_threshold` in `config.toml` as part of this spec's execution — this spec
  produces a recommendation and evidence; adoption is a separate, explicit decision requiring its
  own verification pass (browser/API smoke test per `AGENTS.md`'s Tool Usage Conventions if the
  change ships) and gate re-derivation.
- Treating a single query-level anecdote from the 8 mismatches as sufficient evidence — the
  decision rule requires the full curve/distribution comparison, not eyeballing the 8 `rerank_top`
  values already listed in the diagnostics doc.
- Widening scope to also address the hard_negative subject-gate mechanism or `HYBRID_THRESHOLD` —
  those are separate specs (`2026-09-03-hard-negative-subject-gate-prereg.md`,
  `2026-09-03-hybrid-threshold-jina-prereg.md`) with independent decision rules.
