# Session Handoff - 2026-08-18

## current_task
Score-floor false-abstention diagnostic (hybrid-gate-prereg 2026-08-13, §10b): re-ran the 19 `score_floor` rows against the current index (rebuilt 2026-08-17, 730 circulars / 78,630 chunks). **Done: 15/19 now pass; 4 remain as pure cross-encoder mismatches (all `para-*` rows).**

## blockers
None.

## next_steps
- Inspect the 4 CE_MISMATCH rows (`para-mfmaster`, `para-glitch`, `para-mfborrow`, `para-pricedata`): dump top-5 pool chunks + relevant chunks per query; determine why bge-reranker-v2-m3 scores the relevant docs 0.01-0.36 (table/appendix chunks? query-doc phrasing mismatch?).
- Spec a preregistered intervention in `docs/superpowers/specs/` based on findings (scoring improvement, not gate tuning — all gate-tuning levers exhausted per 2026-08-13 decision).
- Record diagnostic result in `docs/status.md` (YAML/table format per status protocol); secondary: semantic gate for 3 false answers, fresh full eval on the 730-record index.

## metrics
No change (diagnostic only; no pipeline code/config touched). Gate still passes: citation_recall 0.881 (floor 0.8169), citation_precision 0.192 (floor 0.1577), abstention_accuracy 0.981 (floor 0.934).

## decisions
- Diagnostic classification: NOW_PASSES / CE_MISMATCH (in pool, ce_top < 0.42) / RECALL_DEEP (reachable at dense k=200, not in top-50 pool) / RECALL_ABSENT (in index, unreachable at k=200) / DOC_MISSING.
- 15/19 flipping to pass on the rebuilt index means corpus expansion + rebuild resolved most; the remaining 4 are a CE scoring problem, not recall — `ce_relevant_best ≈ ce_top` on all 4 (0.3577 / 0.1024 / 0.0296 / 0.0114 vs gate 0.42).

## files_touched
- `scripts/score_floor_diagnostic.py` - new: re-runs the 19 rows, classifies each
- `reports/score-floor-diagnostic-2026-08-18.json` - new: full per-row results

## config_changes
None.
