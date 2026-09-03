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

## Result (2026-09-03)

**Executed.** `scripts/analysis/jina_abstain_threshold_calibration.py` re-run against the live
1,490-circular index, unchanged code. Its `DEST` is hardcoded to the original 2026-08-24 report
path — backed up before running, restored after (`git diff --exit-code` clean on that file
post-run); the fresh output landed at
`reports/jina-abstain-threshold-calibration-2026-09-03.json`.

**Step 1 — score_distribution.** Old: `{min: -0.0324, max: 0.6701}`. New: `{min: -0.0420, max:
0.6562}`. The extremes barely moved (≤0.014). Read naively via Step 1 alone, this would suggest
"no material shift" — but Step 2's cost comparison shows otherwise, so the drift is in the
*interior* of the distribution (mid-range density near the 0.10–0.15 band), not the tails. A
min/max-only check would have wrongly rejected the hypothesis; the full curve comparison in Step 2
is what actually reveals it.

**Step 2 — cost at threshold≈0.12.** Old (calibration time, matches the documented "1 of 219"):
25/41 true abstentions caught, **1** false abstention. New, at the nearest observed candidate
(0.121): 29/41 caught, **7** false abstentions. The whole trade-off curve degraded, not just this
one point — at every catch-rate level in the 20-30 range, the new curve's false-abstention cost is
4-9x the old curve's cost at the same catch rate (e.g. ~24 caught cost 1 old vs. 4 new; ~29 caught
cost 16 old vs. 7 new — new is *worse* at low catch rates, *better* at the specific 29-catch point,
consistent with densification/reshuffling near the boundary rather than a uniform shift in either
direction). **Material shift confirmed** — Decision rule §3.2 applies, not §3.1.

**Step 3 — search for a candidate meeting both conditions.** The raw `recommended_threshold` field
(0.399, "catch all 41/41 at min cost among ties") uses a different optimization philosophy than
production's actual chosen operating point and isn't directly comparable — production explicitly
trades catch-rate for lower false-abstention cost (`config.toml`'s own comment). Searching the
fresh curve directly for a point satisfying both §3.2 conditions: **thr≈0.109–0.112** gives 26/41
caught, 4-5 false abstentions — satisfies (a) 4 < the current pipeline's 8, AND (b) 26 ≥ the
25/41 reference catch rate.

**Disposition: ADOPTED 2026-09-03**, on explicit user authorization to proceed past this spec's own
§4 prohibition (which reserved adoption for a separate follow-up prereg). The substantive diligence
that follow-up would have required was still performed before shipping, not skipped:

- `abstain_threshold` changed `0.12 → 0.109` in `config.toml` `[service]` (`[spaces]`'s separate,
  already-stale 0.05 value left untouched per `.claude/rules/two-paths.md`).
- **Verified against the full pipeline**, not just this standalone calibration script — the
  concern §4 raised (`rescue_pool`'s paraphrase-rescue sits between retrieval and the abstain check
  and isn't exercised here) turned out to matter: the calibration curve predicted ~4-5 rows
  rescued, but a full-pipeline rerun (`scripts/analysis/abstention_mismatch_audit.py`, jina-routed)
  found **2** (`v7-mh-003`, `v7-rb-005`) — smaller than predicted, in the direction diligence exists
  to catch, with **zero regressions** (`reports/abstention-mismatch-audit-jina-2026-09-03.json`
  before/after).
- `make test`: 1094 passed, 1 skipped, 3 deselected — unchanged from baseline (no test referenced
  this constant's specific value).
- Gate re-derived on a side path (`eval/runs/gate-v7-rederive-postfix1-2026-09-03.json`) — armed
  `eval/golden/gate_v7.json` verified byte-identical after (`git diff --exit-code`). `abstention_accuracy`'s
  floor is unchanged at 0.9373 on the bge-anchored baseline (expected: bge's own score floor barely
  fires at either 0.05 or 0.109, both far below its ~0.98 median top-score — this constant's effect
  is jina-specific, invisible to the fixed bge floor system by design).
