# Golden v7 Expansion — Session Handoff Notes

**Worktree:** `golden-v7-expansion` (at `.worktrees/golden-v7`)
**Merged to main:** `ac9c797` (merge commit)
**Main HEAD:** `8ea3797` (includes merge + label map update)

## What's Done (on main)

- **Tasks 1–14** all implemented and committed
- **Gate armed:** `adjudicated_n: 103` (≥ 100 threshold met)
- **Tests:** 603 passed, 0 failures
- **Eval:** 13/13, 100% accuracy
- **246 files** merged (+165k/-22k lines)

## What's Pending (post-gate, can wait on main)

1. **Arbitration queue** (50 rows) — annotator disagreements unresolved
   - File: `eval/golden/v7_annotations/arbitration_queue.jsonl`
   - These are rows where claude/qwen/human disagreed; need an arbitrator

2. **Untargeted seeded rows** (34 rows) — short-ID rows from v5 never adjudicated
   - IDs: `surv`, `depo`, `secc`, `esg`, `sse`, `pms`, `reit`, etc.

3. **Zero-vote rows** (8 rows) — no votes at all
   - IDs: `abstain`, `hn-buyback`, `hn-delist`, `hn-esop`, `hn-muni`, `fn-001`, `fn-002`, `v7-ls-040`

4. **Regenerate results.json** — run `make eval-asof` to update timestamp/git_commit

## Worktree Deletion

The worktree at `.worktrees/golden-v7` is safe to delete:
```bash
git worktree remove golden-v7
```

All worktree commits are reachable from main (merge commit `ac9c797` contains them).

## Key Files for Reference

- Plan: `docs/superpowers/plans/2026-07-24-golden-v7-expansion.md`
- Spec: `docs/superpowers/specs/2026-07-23-golden-v7-expansion-design.md`
- Gate: `eval/golden/gate_v7.json`
- Golden set: `eval/golden/golden_v7.jsonl` (260 rows, 103 adjudicated)
- Votes: `eval/golden/v7_annotations/votes.jsonl` (373 votes)
- Arbitration: `eval/golden/v7_annotations/arbitration_queue.jsonl` (50 rows)
- Scripts: `scripts/golden_v7/` (13 scripts)
