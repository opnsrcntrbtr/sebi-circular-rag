# Autoresearch: Extension Evaluation for SEBI RAG Project

## Objective
Evaluate Tier 1 Pi extensions (pi-green-loop, pi-lens, pi-hashline-edit-pro) against the SEBI RAG project's recurring workflows. Measure goal outcome quality, throughput impact, and token overhead. Decide whether to keep or discard each extension after 1 week of real usage.

## Metrics
- **Primary**: Token overhead % (target: ≤3% of ~3,500 baseline = ≤105 tokens) — lower is better
- **Secondary**: Test feedback time (partial change), LSP lookup time, edit success rate

## How to Run
`./.auto/measure.sh` — outputs `METRIC name=value` lines. Measures:
- Baseline token count (without extensions)
- Test feedback time for partial changes
- LSP lookup time
- Edit success rate with hashline edits

## Files in Scope
- `.auto/prompt.md` — this file (update as experiments accumulate)
- `.auto/measure.sh` — benchmark script
- `.auto/checks.sh` — correctness checks (make test)
- `src/sebi_rag/` — project source (for testing extension impact)
- `.pi/agent/skills/` — installed skills (graphify is already present)

## Off Limits
- Do NOT install Tier 2 or Tier 3 extensions during this evaluation
- Do NOT modify `CircularMeta` in `segment.py` (project constraint)
- Do NOT replace homegrown `smart_compact` / `telemetry_engine.py` / `smart_save_memory`
- Do NOT install memory extensions (pi-memory, pi-hermes-memory, red-skills-memory)

## Constraints
- `make test` must pass after any extension install
- Token overhead must stay ≤3% of baseline
- All measurements must be repeatable (run 3x, report median)

## What's Been Tried
- **Baseline established**: ~3,500 tokens/session without extensions
- **Tier 1 extensions identified**: pi-green-loop (0.4%), pi-lens (0.5%), pi-hashline-edit-pro (0.6%)
- **Estimated combined overhead**: ~1.5% — within target

## Evaluation Phases
### Phase 1: Install & Smoke Test (Days 1-2)
1. Install all 3 Tier 1 extensions
2. Verify LSP-first navigation works with graphify
3. Verify test scoping works for partial changes
4. Run `make test` — must pass

### Phase 2: Goal Outcome Quality (Days 3-4)
1. Fix a regression in `generate.py` — measure time to fix + test pass rate
2. Add a field to `master_meta.py` — verify hash anchors stable, no CircularMeta mutation
3. Multi-file change: update `pipeline.py` + `api.py` — check consistency

### Phase 3: Throughput & Overhead (Days 5-6)
1. Measure session token count with extensions (target: <3,605)
2. Measure test feedback time for partial change (target: <15s with green-loop vs ~90s full suite)
3. Measure LSP lookup time (target: <10s with pi-lens vs ~30s manual)
4. Measure edit success rate with hashline edits (target: >95%)

### Phase 4: Decision Gate (Day 7)
- Keep extension if it meets success criteria
- Discard if it fails or adds >1% overhead without clear benefit
- Document final verdict in this file

## Decision Criteria
| Extension | Keep if... | Discard if... |
|---|---|---|
| pi-green-loop | Test feedback <20s for partial changes | No measurable speedup vs full suite |
| pi-lens | LSP lookups <15s, fewer manual lsp calls | Conflicts with graphify, no improvement |
| pi-hashline-edit-pro | Zero stale-anchor bugs in 10+ edits | Edit failures >5% of attempts |
