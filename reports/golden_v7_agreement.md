# Golden v7 external-annotation agreement

Cohen's kappa and raw agreement per annotator pair per stratum, over rows in the external-100 sample where both annotators in the pair voted. Abstain rows (no claude label in Task 8) compare against an implicit `frozenset()` claude label matching their authored `abstain: true` state.

| stratum | pair | n | kappa | raw agreement |
|---|---|---|---|---|
| body_paraphrase | claude-qwen | 23 | 0.338 | 34.8% |
| far_negative | claude-qwen | 4 | 1.000 | 100.0% |
| hard_negative | claude-qwen | 15 | 1.000 | 100.0% |
| lineage_supersession | claude-qwen | 15 | 0.250 | 26.7% |
| multi_hop | claude-qwen | 8 | 0.111 | 12.5% |
| numeric_table | claude-qwen | 12 | 0.000 | 0.0% |
| repealed_basis | claude-qwen | 8 | 0.111 | 12.5% |
| title_direct | claude-qwen | 15 | 0.062 | 6.7% |

## Claude-label accuracy vs externals

34/100 matched (34.0%), 95% CI 24.8–44.2% (clopper-pearson).

## Promotion outcomes

Promotion unit (spec sec7 as amended 2026-07-26): PROVISION-level - an external confirms claude's label via exact set match, containment, or picking any chunk whose text contains the row's span quote. The kappa table above stays at exact-set level, deliberately stricter than the promotion rule, so the reported agreement is never flattered by the amendment.

- promoted: 63
- flipped: 0
- queued: 37
