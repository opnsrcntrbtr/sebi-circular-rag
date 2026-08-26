# Ideas Backlog — Extension Evaluation

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
