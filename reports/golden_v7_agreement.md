# Golden v7 external-annotation agreement

Cohen's kappa and raw agreement per annotator pair per stratum, over rows in the external-100 sample where both annotators in the pair voted. Abstain rows (no claude label in Task 8) compare against an implicit `frozenset()` claude label matching their authored `abstain: true` state.

| stratum | pair | n | kappa | raw agreement |
|---|---|---|---|---|
| body_paraphrase | claude-qwen | 23 | 0.338 | 34.8% |
| body_paraphrase | claude-human | 7 | 0.533 | 57.1% |
| body_paraphrase | qwen-human | 7 | 0.632 | 71.4% |
| far_negative | claude-qwen | 4 | 1.000 | 100.0% |
| far_negative | claude-human | 1 | 1.000 | 100.0% |
| far_negative | qwen-human | 1 | 1.000 | 100.0% |
| hard_negative | claude-qwen | 15 | 1.000 | 100.0% |
| hard_negative | claude-human | 4 | 1.000 | 100.0% |
| hard_negative | qwen-human | 4 | 1.000 | 100.0% |
| lineage_supersession | claude-qwen | 15 | 0.250 | 26.7% |
| lineage_supersession | claude-human | 5 | 1.000 | 100.0% |
| lineage_supersession | qwen-human | 5 | 0.348 | 40.0% |
| multi_hop | claude-qwen | 8 | 0.111 | 12.5% |
| multi_hop | claude-human | 2 | 0.000 | 0.0% |
| multi_hop | qwen-human | 2 | 0.000 | 0.0% |
| numeric_table | claude-qwen | 12 | 0.000 | 0.0% |
| numeric_table | claude-human | 4 | 1.000 | 100.0% |
| numeric_table | qwen-human | 4 | 0.000 | 0.0% |
| repealed_basis | claude-qwen | 8 | 0.111 | 12.5% |
| repealed_basis | claude-human | 2 | 1.000 | 100.0% |
| repealed_basis | qwen-human | 2 | 0.333 | 50.0% |
| title_direct | claude-qwen | 15 | 0.062 | 6.7% |
| title_direct | claude-human | 5 | 0.348 | 40.0% |
| title_direct | qwen-human | 5 | 0.348 | 40.0% |

## Claude-label accuracy vs externals

56/130 matched (43.1%), 95% CI 34.4–52.0% (clopper-pearson).

## Promotion outcomes

Promotion unit (spec sec7 as amended 2026-07-26): PROVISION-level - an external confirms claude's label via exact set match, containment, or picking any chunk whose text contains the row's span quote. The kappa table above stays at exact-set level, deliberately stricter than the promotion rule, so the reported agreement is never flattered by the amendment.

- promoted: 63
- flipped: 0
- queued: 37
