# Benchmark re-scoring: bootstrap CIs and paired significance

Replayed from frozen TREC runfiles in `eval/runs`; 10,000 resamples, seed 0, 95% intervals. No pipeline re-run — the runfiles are the record.

## golden

| run | n | recall@10 | 95% CI | replay == archive |
|---|---|---|---|---|
| ft-golden | 45 | 95.6 | 88.9–100.0 | yes |
| iv-final-golden | 45 | 95.6 | 88.9–100.0 | yes |
| iv10-a-golden | 45 | 95.6 | 88.9–100.0 | yes |
| iv10-b-golden | 45 | 95.6 | 88.9–100.0 | yes |
| iv11-a-golden | 45 | 95.6 | 88.9–100.0 | yes |
| iv11-b-golden | 45 | 95.6 | 88.9–100.0 | yes |
| iv11-splade-only-golden | 45 | 86.7 | 75.6–95.6 | n/a (no results.json) |
| iv2-golden | 45 | 97.8 | 93.3–100.0 | yes |
| iv6-golden | 45 | 95.6 | 88.9–100.0 | yes |
| iv7-golden | 45 | 95.6 | 88.9–100.0 | yes |
| iv8-golden | 45 | 95.6 | 88.9–100.0 | yes |
| iv9-golden | 45 | 93.3 | 84.4–100.0 | yes |

### Paired comparisons

| comparison | n | control | treatment | delta | 95% CI | p | queries changed | verdict |
|---|---|---|---|---|---|---|---|---|
| iv1+iv2 governing-clause folding + glossary (ADOPTED) | 45 | 95.6 | 97.8 | +2.2 | +0.0–+6.7 | 1.000 | 1 | not distinguishable |
| iv8 HyDE hypothetical-passage third leg | 45 | 95.6 | 95.6 | +0.0 | +0.0–+0.0 | 1.000 | 0 | not distinguishable |
| iv9 contextual headers (full corpus) | 45 | 95.6 | 93.3 | -2.2 | -6.7–+0.0 | 1.000 | 1 | not distinguishable |
| iv10 targeted headers (scoped sidecar) | 45 | 95.6 | 95.6 | +0.0 | +0.0–+0.0 | 1.000 | 0 | not distinguishable |
| iv11 SPLADE learned-sparse third leg | 45 | 95.6 | 95.6 | +0.0 | -6.7–+6.7 | 1.000 | 2 | not distinguishable |

## probes

| run | n | recall@10 | 95% CI | replay == archive |
|---|---|---|---|---|
| ft-probes | 25 | 96.0 | 88.0–100.0 | yes |
| iv-final-probes | 25 | 100.0 | 100.0–100.0 | yes |
| iv10-a-probes | 25 | 100.0 | 100.0–100.0 | yes |
| iv10-b-probes | 25 | 100.0 | 100.0–100.0 | yes |
| iv11-a-probes | 25 | 100.0 | 100.0–100.0 | yes |
| iv11-b-probes | 25 | 96.0 | 88.0–100.0 | yes |
| iv11-splade-only-probes | 25 | 96.0 | 88.0–100.0 | n/a (no results.json) |
| iv2-probes | 25 | 100.0 | 100.0–100.0 | yes |
| iv6-probes | 25 | 100.0 | 100.0–100.0 | yes |
| iv7-probes | 25 | 100.0 | 100.0–100.0 | yes |
| iv8-probes | 25 | 100.0 | 100.0–100.0 | yes |
| iv9-probes | 25 | 96.0 | 88.0–100.0 | yes |

### Paired comparisons

| comparison | n | control | treatment | delta | 95% CI | p | queries changed | verdict |
|---|---|---|---|---|---|---|---|---|
| iv1+iv2 governing-clause folding + glossary (ADOPTED) | 25 | 96.0 | 100.0 | +4.0 | +0.0–+12.0 | 1.000 | 1 | not distinguishable |
| iv8 HyDE hypothetical-passage third leg | 25 | 100.0 | 100.0 | +0.0 | +0.0–+0.0 | 1.000 | 0 | not distinguishable |
| iv9 contextual headers (full corpus) | 25 | 100.0 | 96.0 | -4.0 | -12.0–+0.0 | 1.000 | 1 | not distinguishable |
| iv10 targeted headers (scoped sidecar) | 25 | 100.0 | 100.0 | +0.0 | +0.0–+0.0 | 1.000 | 0 | not distinguishable |
| iv11 SPLADE learned-sparse third leg | 25 | 100.0 | 96.0 | -4.0 | -12.0–+0.0 | 1.000 | 1 | not distinguishable |

## Reading this table

`queries changed` is the number of discordant queries — the only ones carrying information in a paired test. Under the null, each discordant query contributes one coin flip, so a two-sided test needs at least **6 discordant queries all moving the same way** before any delta can reach p < 0.05. Every comparison above has 0–2. The p-values are therefore not evidence that these interventions are neutral; they are evidence that the golden set cannot tell, in either direction.

Consequence for the iv-series gate verdicts: each accept/reject decision was made on a point-estimate delta that the same data cannot distinguish from noise. The adopted intervention (iv1+iv2) and the rejected ones (iv8-iv11) are, on this evidence, equally unproven.

