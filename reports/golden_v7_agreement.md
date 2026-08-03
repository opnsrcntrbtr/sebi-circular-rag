# Golden v7 external-annotation agreement

Per annotator pair per stratum, over rows in the external-100 sample where both annotators in the pair voted. `kappa` and `raw agreement` are exact chunk-id-set equality (deliberately strict). `AC1` is Gwet's prevalence-robust coefficient (fixes the base-rate paradox that collapses kappa on skewed strata like numeric_table). `provision` is agreement at the PROVISION level - the unit the pipeline actually promotes on (exact set, containment, or same span quote). Abstain rows (no claude label in Task 8) compare against an implicit `frozenset()` claude label matching their authored `abstain: true` state.

| stratum | pair | n | kappa | AC1 | raw agreement | provision |
|---|---|---|---|---|---|---|
| body_paraphrase | claude-qwen | 37 | 0.265 | 0.257 | 27.0% | 78.4% |
| body_paraphrase | claude-human | 3 | 0.250 | 0.172 | 33.3% | 100.0% |
| body_paraphrase | qwen-human | 3 | 0.250 | 0.172 | 33.3% | 66.7% |
| far_negative | claude-qwen | 4 | 1.000 | 1.000 | 100.0% | 100.0% |
| hard_negative | claude-qwen | 15 | 1.000 | 1.000 | 100.0% | 100.0% |
| lineage_supersession | claude-qwen | 24 | 0.201 | 0.190 | 20.8% | 100.0% |
| lineage_supersession | claude-human | 5 | 0.762 | 0.761 | 80.0% | 100.0% |
| lineage_supersession | qwen-human | 5 | 0.348 | 0.316 | 40.0% | 100.0% |
| multi_hop | claude-qwen | 13 | 0.071 | 0.039 | 7.7% | 100.0% |
| numeric_table | claude-qwen | 19 | 0.000 | -0.027 | 0.0% | 100.0% |
| numeric_table | claude-human | 1 | 0.000 | -1.000 | 0.0% | 100.0% |
| numeric_table | qwen-human | 1 | 0.000 | -1.000 | 0.0% | 100.0% |
| repealed_basis | claude-qwen | 13 | 0.291 | 0.275 | 30.8% | 100.0% |
| repealed_basis | claude-human | 1 | 0.000 | -1.000 | 0.0% | 100.0% |
| repealed_basis | qwen-human | 1 | 0.000 | -1.000 | 0.0% | 0.0% |
| title_direct | claude-qwen | 25 | 0.077 | 0.060 | 8.0% | 68.0% |
| title_direct | claude-human | 6 | 0.294 | 0.260 | 33.3% | 100.0% |
| title_direct | qwen-human | 6 | 0.143 | 0.084 | 16.7% | 83.3% |

## Claude-label accuracy vs externals

Exact chunk-id-set match: 48/166 (28.9%), 95% CI 22.2–36.4% (clopper-pearson).

Provision-level match: 150/166 (90.4%), 95% CI 84.8–94.4% (clopper-pearson).

## Promotion outcomes

Promotion unit (spec sec7 as amended 2026-07-26): PROVISION-level - an external confirms claude's label via exact set match, containment, or picking any chunk whose text contains the row's span quote. The kappa table above stays at exact-set level, deliberately stricter than the promotion rule, so the reported agreement is never flattered by the amendment.

- promoted: 103
- flipped: 0
- queued: 47
