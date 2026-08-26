# Autoresearch: Extension Evaluation for SEBI RAG Project

## Objective
Evaluate Tier 1 Pi extensions (pi-green-loop, pi-lens, pi-hashline-edit-pro) against the SEBI RAG project's recurring workflows. Measure goal outcome quality, throughput impact, and token overhead. Decide whether to keep or discard each extension after 1 week of real usage.

## Metrics
- **Primary**: Token overhead % (target: ≤3% of ~6,080 current total = ≤182 tokens) — lower is better
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
- `.pi/agent/skills/` — installed skills (graphify already present, ~2,580 tokens)
- `.pi/agent/npm/node_modules/pi-*` — npm-installed extensions

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
- **Baseline established**: ~6,080 tokens/session (AGENTS.md 3,500 + graphify skill ~2,580)
- **Measured extension overhead** (tool definitions, not README files):
  - pi-green-loop: +50 tokens (0.8%) ✅
  - pi-lens: +150 tokens (2.5%) ✅
  - pi-hashline-edit-pro: +200 tokens (3.3%) ⚠️ slightly over target
- **Combined Tier 1**: +400 tokens (6.6%) ❌ exceeds target
- **pi-green-loop evaluation results**:
  - Runs pytest directly: ~26.5s vs `make test` ~50s (47% faster, bypasses Makefile overhead)
  - Does NOT scope tests to affected files for this project — runs full 905-item suite
  - `--affected` flag requires additional config to map source→test files
  - Verdict: marginal benefit (47% faster full suite) vs no actual test scoping
- **Revised recommendation**: pi-green-loop provides marginal benefit; consider if 23.5s saving per test run justifies the token overhead

## Evaluation Phases
### Phase 1: Install & Smoke Test (Days 1-2) — ✅ COMPLETE
1. ✅ Installed pi-green-loop only (0.8% overhead, within target)
2. ❌ Test scoping does NOT work for this project (requires source→test config)
3. ✅ `make test` passes (pre-existing failures unchanged)
4. ✅ Measured: 26.5s vs 50s (47% faster, but full suite run)

## Phase 2: 1-Week Usage Evaluation (Days 3-9)
1. Keep pi-green-loop installed
2. Track: how often is `pi-green-loop check` used vs `make test`?
3. Track: actual time saved across all test runs in the week
4. Day 9: Review usage frequency and total time saved
5. Decision: Keep or discard based on real-world utility

## Phase 3: Re-evaluate Tier 1 Extensions (Day 10)
1. If pi-green-loop kept: check remaining token budget for pi-lens (2.5%)
2. If pi-green-loop discarded: revert installation
3. Re-assess pi-lens and pi-hashline-edit-pro based on lessons learned

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
| pi-lens (deferred) | LSP lookups <15s, fewer manual lsp calls | Conflicts with graphify, no improvement |
| pi-hashline-edit-pro (deferred) | Zero stale-anchor bugs in 10+ edits | Edit failures >5% of attempts |
