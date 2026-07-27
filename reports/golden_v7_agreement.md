# Golden v7 external-annotation agreement

Cohen's kappa and raw agreement per annotator pair per stratum, over rows in the external-100 sample where both annotators in the pair voted. Abstain rows (no claude label in Task 8) compare against an implicit `frozenset()` claude label matching their authored `abstain: true` state.

| stratum | pair | n | kappa | raw agreement |
|---|---|---|---|---|
| body_paraphrase | claude-qwen | 37 | 0.265 | 27.0% |
| body_paraphrase | claude-human | 3 | 0.250 | 33.3% |
| body_paraphrase | qwen-human | 3 | 0.250 | 33.3% |
| far_negative | claude-qwen | 4 | 1.000 | 100.0% |
| hard_negative | claude-qwen | 15 | 1.000 | 100.0% |
| lineage_supersession | claude-qwen | 24 | 0.200 | 20.8% |
| lineage_supersession | claude-human | 5 | 0.762 | 80.0% |
| lineage_supersession | qwen-human | 5 | 0.348 | 40.0% |
| multi_hop | claude-qwen | 13 | 0.071 | 7.7% |
| numeric_table | claude-qwen | 19 | 0.000 | 0.0% |
| numeric_table | claude-human | 1 | 0.000 | 0.0% |
| numeric_table | qwen-human | 1 | 0.000 | 0.0% |
| repealed_basis | claude-qwen | 13 | 0.291 | 30.8% |
| repealed_basis | claude-human | 1 | 0.000 | 0.0% |
| repealed_basis | qwen-human | 1 | 0.000 | 0.0% |
| title_direct | claude-qwen | 25 | 0.077 | 8.0% |
| title_direct | claude-human | 6 | 0.294 | 33.3% |
| title_direct | qwen-human | 6 | 0.143 | 16.7% |

## Claude-label accuracy vs externals

48/166 matched (28.9%), 95% CI 22.2–36.4% (clopper-pearson).

## Promotion outcomes

Promotion unit (spec sec7 as amended 2026-07-26): PROVISION-level - an external confirms claude's label via exact set match, containment, or picking any chunk whose text contains the row's span quote. The kappa table above stays at exact-set level, deliberately stricter than the promotion rule, so the reported agreement is never flattered by the amendment.

- promoted: 100
- flipped: 0
- queued: 50
