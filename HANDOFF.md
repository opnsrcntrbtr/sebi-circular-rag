# Handoff

## State
- Graphify updated: 2035 nodes, 4363 edges, 129 communities (labeled)
- B' selective citations ARMED (margin=0.35): recall=0.943, precision=0.224, citation_recall=0.783, abstention=0.962 (all floors pass)
- Citation recall variance analysis complete: task_type drives variance, numeric_table (0.633) and lineage_supersession (0.725) worst
- Docs synced: `docs/status.md` + `docs/project_context.md` updated with fresh eval values (commit 0361753)

## Next
1. Decide variance reduction approach: tighter margin (Δ=0.25), stratum-specific margins, smarter fallback, or operational monitoring
2. If implementing: modify `generate.py` `select_citations()` + re-derive thresholds via `scripts/golden_v7/derive_thresholds.py`
3. Re-run `make eval-asof golden_v7` after any margin change

## Context
- B' filter removes ALL relevant contexts when answer-relevance scores spread thin → citation_recall=0 on 44/260 queries (17%)
- Precision win (0.224 vs baseline 0.119) is real but recall variance is the trade-off
- oMLX on :8001, 667 tests pass, gate_v7.json armed