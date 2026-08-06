# Benchmark re-scoring: bootstrap CIs and paired significance

Replayed from frozen TREC runfiles in `eval/runs`; 10,000 resamples, seed 0, 95% intervals. No pipeline re-run — the runfiles are the record.

## golden

| run | frame | n | recall@10 | 95% CI | replay == archive |
|---|---|---|---|---|---|
| ft-golden | E1/f01d8779 | 45 | 95.6 | 88.9–100.0 | yes |
| iv-final-golden | E2/f01d8779 | 45 | 95.6 | 88.9–100.0 | yes |
| iv10-a-golden | E2/f01d8779 | 45 | 95.6 | 88.9–100.0 | yes |
| iv10-b-golden | E2/f01d8779 | 45 | 95.6 | 88.9–100.0 | yes |
| iv11-a-golden | E2/f01d8779 | 45 | 95.6 | 88.9–100.0 | yes |
| iv11-b-golden | E2/f01d8779 | 45 | 95.6 | 88.9–100.0 | yes |
| iv11-splade-only-golden | — | 45 | 86.7 | 75.6–95.6 | n/a (no results.json) |
| iv2-golden | E1/f01d8779 | 45 | 97.8 | 93.3–100.0 | yes |
| iv6-golden | E2/f01d8779 | 45 | 95.6 | 88.9–100.0 | yes |
| iv7-golden | E2/f01d8779 | 45 | 95.6 | 88.9–100.0 | yes |
| iv8-golden | E2/f01d8779 | 45 | 95.6 | 88.9–100.0 | yes |
| iv9-golden | E2/f01d8779 | 45 | 93.3 | 84.4–100.0 | yes |

### Paired comparisons

| comparison | n | control | treatment | delta | 95% CI | p | queries changed | verdict |
|---|---|---|---|---|---|---|---|---|
| iv1+iv2 governing-clause folding + glossary (ADOPTED) | 45 | 95.6 | 97.8 | +2.2 | +0.0–+6.7 | 1.000 | 1 | not distinguishable |
| iv8 HyDE hypothetical-passage third leg | 45 | 95.6 | 95.6 | +0.0 | +0.0–+0.0 | 1.000 | 0 | not distinguishable |
| iv9 contextual headers (full corpus) | 45 | 95.6 | 93.3 | -2.2 | -6.7–+0.0 | 1.000 | 1 | not distinguishable |
| iv10 targeted headers (scoped sidecar) | 45 | 95.6 | 95.6 | +0.0 | +0.0–+0.0 | 1.000 | 0 | not distinguishable |
| iv11 SPLADE learned-sparse third leg | 45 | 95.6 | 95.6 | +0.0 | -6.7–+6.7 | 1.000 | 2 | not distinguishable |

## probes

| run | frame | n | recall@10 | 95% CI | replay == archive |
|---|---|---|---|---|---|
| ft-probes | E1/99a9da66 | 25 | 96.0 | 88.0–100.0 | yes |
| iv-final-probes | E2/99a9da66 | 25 | 100.0 | 100.0–100.0 | yes |
| iv10-a-probes | E2/99a9da66 | 25 | 100.0 | 100.0–100.0 | yes |
| iv10-b-probes | E2/99a9da66 | 25 | 100.0 | 100.0–100.0 | yes |
| iv11-a-probes | E2/99a9da66 | 25 | 100.0 | 100.0–100.0 | yes |
| iv11-b-probes | E2/99a9da66 | 25 | 96.0 | 88.0–100.0 | yes |
| iv11-splade-only-probes | — | 25 | 96.0 | 88.0–100.0 | n/a (no results.json) |
| iv2-probes | E1/99a9da66 | 25 | 100.0 | 100.0–100.0 | yes |
| iv6-probes | E2/99a9da66 | 25 | 100.0 | 100.0–100.0 | yes |
| iv7-probes | E2/99a9da66 | 25 | 100.0 | 100.0–100.0 | yes |
| iv8-probes | E2/99a9da66 | 25 | 100.0 | 100.0–100.0 | yes |
| iv9-probes | E2/99a9da66 | 25 | 96.0 | 88.0–100.0 | yes |

### Paired comparisons

| comparison | n | control | treatment | delta | 95% CI | p | queries changed | verdict |
|---|---|---|---|---|---|---|---|---|
| iv1+iv2 governing-clause folding + glossary (ADOPTED) | 25 | 96.0 | 100.0 | +4.0 | +0.0–+12.0 | 1.000 | 1 | not distinguishable |
| iv8 HyDE hypothetical-passage third leg | 25 | 100.0 | 100.0 | +0.0 | +0.0–+0.0 | 1.000 | 0 | not distinguishable |
| iv9 contextual headers (full corpus) | 25 | 100.0 | 96.0 | -4.0 | -12.0–+0.0 | 1.000 | 1 | not distinguishable |
| iv10 targeted headers (scoped sidecar) | 25 | 100.0 | 100.0 | +0.0 | +0.0–+0.0 | 1.000 | 0 | not distinguishable |
| iv11 SPLADE learned-sparse third leg | 25 | 100.0 | 96.0 | -4.0 | -12.0–+0.0 | 1.000 | 1 | not distinguishable |

## Appendix — cross-frame figures are NOT COMPARABLE

A *frame* is the pair (corpus snapshot, eval set); two runs are comparable only within one frame. This archive spans four corpora (E1–E4) and three eval sets. Every A/B pair above is internally valid — control and treatment always shared a frame — but runs from different frames cannot be ranked against one another, and no intervention here was measured on the current corpus (`5f626dd9`) or on golden_v7. `rescore_runs.py` now raises rather than emitting a cross-frame comparison.

## Reading this table

`queries changed` is the number of discordant queries — the only ones carrying information in a paired test. Under the null, each discordant query contributes one coin flip, so a two-sided test needs at least **6 discordant queries all moving the same way** before any delta can reach p < 0.05. Every comparison above has 0–2. The p-values are therefore not evidence that these interventions are neutral; they are evidence that the golden set cannot tell, in either direction.

Consequence for the iv-series gate verdicts: each accept/reject decision was made on a point-estimate delta that the same data cannot distinguish from noise. The adopted intervention (iv1+iv2) and the rejected ones (iv8-iv11) are, on this evidence, equally unproven.

