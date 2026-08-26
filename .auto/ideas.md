# Ideas Backlog — Extension Evaluation

## Evaluation Results (2026-08-27)
### pi-green-loop
- **Verdict**: Marginal benefit — 47% faster full test suite (26.5s vs 50s) but NO actual test scoping
- **Why no scoping**: Requires config to map source→test files; doesn't work out-of-box for this project
- **Token overhead**: +50 tokens (0.8%) — within target
- **Decision**: Keep if 23.5s per test run saving is valuable; otherwise discard

### pi-lens (deferred)
- **Token overhead**: +150 tokens (2.5%) — within 3% target individually
- **Status**: Not installed yet, deferred pending pi-green-loop evaluation

### pi-hashline-edit-pro (deferred)
- **Token overhead**: +200 tokens (3.3%) — slightly over 3% target
- **Status**: Not installed yet, deferred

## Potential Future Extensions (not yet evaluated)
- **pi-background-tasks** — Durable background shell tasks for 50min reindex / 38min eval runs
- **pi-goal-x** — Durable objectives with Sisyphus mode, auto-continue, structured tasks
- **pi-subagents (official)** — Multi-agent delegation for multi-file changes
- **cc-safety-net** — Destructive command blocking + secret file access prevention

## Ideas for SEBI RAG Specific Extensions
- **golden-set validator** — Pre-commit check that golden_v7.jsonl is still valid (adjudicated_n >= 100)
- **corpus integrity checker** — Verify chunks.jsonl matches corpus JSONL after reindex
- **eval regression detector** — Auto-flag when recall_at_10 drops below floor after changes
- **lineage anomaly detector** — Flag circulars with missing supersession edges

## Dead Ends
- External memory extensions (pi-memory, pi-hermes-memory) — homegrown smart_compact + telemetry_engine.py sufficient
- Broad methodology packs (bigpowers, red-skills-dev) — too generic for project-specific needs
