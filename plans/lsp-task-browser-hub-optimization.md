# Plan: LSP + Subagent + Browser + Memory + Dev Server Optimization

**Goal:** Adopt 5 oh-my-pi capabilities to improve development velocity and correctness on the SEBI RAG project (791 tests, 260 golden items, regulatory content).

**Scope:** Workflow conventions + lightweight automation. No architecture changes to `src/sebi_rag/`.

---

## Phase 1: LSP Enablement (Day 1)

### Current State
- `pyright` configured but not started; LSP reload confirmed working
- 20+ diagnostics (mostly `reportMissingImports` in scripts, a few type mismatches)
- Cross-file renames done manually (misses callsites)

### Changes

**1.1 LSP Usage Convention (AGENTS.md update)**
- File: `AGENTS.md` → add "LSP-first" section under Engineering conventions
- Rule: All cross-file renames use `lsp references` before editing, `lsp rename` for execution
- Rule: Pre-edit diagnostics check via `lsp diagnostics` on affected files

**1.2 Diagnostic Triage (optional, low priority)**
- 17 `reportMissingImports` errors are in scripts with optional deps (pyarrow, bm25s, huggingface_hub) — not blockers
- 3 real type errors in `bench_retrieval.py` (retriever attribute assignment) — fixable
- 1 type error in `app.py` (RAGPipeline | object → replace) — fixable

### Acceptance
- `lsp status` shows pyright as "ready" (not just "configured")
- AGENTS.md documents LSP-first convention

---

## Phase 2: Subagent-Driven Test Work (Day 1-2)

### Current State
- `make test` runs `pytest -q -m "not integration"` (791 tests)
- Multi-module changes require sequential test discovery + fix cycles

### Changes

**2.1 Parallel Test Discovery Convention**
- For any change touching N source files: spawn N parallel `scout` agents to find affected tests
- Each scout runs: grep for function/class references in `tests/` + `scripts/`
- Consolidate results before fix phase

**2.2 Parallel Fix Pattern**
- When fixes are independent (different modules), use `task` with parallel workers
- When fixes share files, serialize or let agents auto-resolve over IRC

### Acceptance
- Documented workflow in AGENTS.md: "For multi-file changes, use `task` with parallel scouts for test discovery"
- No code changes required — this is a workflow convention

---

## Phase 3: Browser-Based UI Verification (Day 1)

### Current State
- Gradio UI at `src/sebi_rag/ui.py` (368 lines)
- No automated UI verification; visual changes verified manually or not at all
- Recent change: `fix(app): Gradio 5+ chat message format + missing latency_ms`

### Changes

**3.1 Browser Verification Convention (AGENTS.md update)**
- Rule: Before yielding any `app.py` or `ui.py` changes, verify via `browser` tool
- Verification checklist:
  - Chat message rendering (answer + citations)
  - Citation preview inline display
  - Superseded citation highlighting
  - As-of date picker functionality
  - API URL validation (SSRF guard)

**3.2 Optional: Lightweight UI Smoke Test Script**
- File: `scripts/verify_ui.sh` (optional, low priority)
- Starts Gradio UI in headless mode, takes screenshot of key components
- Not a full test suite — just visual regression check

### Acceptance
- AGENTS.md documents browser verification step before yielding app changes
- No code changes to `src/sebi_rag/` required

---

## Phase 4: Retain Architecture Decisions (Day 1)

### Current State
- Complex calibration params, RRF weights, supersession logic scattered across code + config
- Decisions lost between sessions

### Changes

**4.1 Retain Key Architecture Decisions**
Store via `retain` tool:

```yaml
# Calibration (scripts/calibrate.py methodology)
- golden_set: golden_v7.jsonl (n=260, adjudicated >= 100 for CI gate)
- calibration_grid: top_k in {1,2,3,5}, thr in {0.05, 0.2, 0.4, 0.6}
- selected: top_k=3 (config), abstain_threshold=0.05 (config) — note: calibrate.py defaults TOP_K=3, THR=0.4 for diagnostics
- RRF k_const: 60 (retrieve.py:75) — rank-only fusion, no score weighting
- RRF top_n: 50 (retrieve.py:76) — pool size before reranker

# Supersession Logic
- As-of queries: EXCLUDE superseded circulars (not demote) — prevents 0.3x penalty from keeping superseded chunks above alternatives
- Non-as-of: demote with superseded_penalty=0.3 (config.toml)
- Detection: regex-based (SUPERSEDE_RE, AMEND_RE in lineage.py)
- Lineage structure: supersedes=dict[str,list[str]] (newer -> [older])

# Pipeline Architecture
- RAGPipeline fields: abstain_threshold, superseded_penalty, citation_margin=0.35, citation_min_keep=1
- Citation scorer (B'): post-hoc cross-encoder filter, enabled by default
- Eval generator: "mlx" (production parity; 20x slower than stub but accurate)
- F3 incremental encoding: per-doc checksum manifest, reuses unchanged embedding rows

# Config Decisions
- abstain_threshold=0.05 (config) vs calibrate.py diagnostic default 0.4
- citation_margin=0.35 (MLX-parallel sweep: P+5.4%, recall 0.8721, n=219)
- top_k=10 (increased from 5: citation_recall 0.772→0.888)
- encode_batch_size=32 (MPS prefers larger batches)
```

### Acceptance
- All key decisions stored in memory system
- `recall` returns these facts when queried about calibration, RRF, or supersession logic

---

## Phase 5: Hub-Managed Dev Servers (Day 1-2)

### Current State
- `make serve` → uvicorn on port 8000 (manual start/stop)
- `make ui` → Gradio on port 7860 (manual start/stop)
- No process lifecycle management

### Changes

**5.1 Dev Server Lifecycle Convention (AGENTS.md update)**
- Rule: Use `hub start` for long-running processes instead of manual `make serve`/Ctrl+C
- Pattern:
  ```
  hub(op="start", name="api", application="$(VENV)/bin/uvicorn", 
      args=["sebi_rag.api:app", "--host", "127.0.0.1", "--port", "8000"],
      ready={"log": "Uvicorn running", "port": 8000, "timeout": 15})
  ```
- Use `hub logs name="api"` for server output inspection
- Use `hub stop name="api"` for clean shutdown

**5.2 Optional: Dev Helper Script**
- File: `scripts/dev.sh` (optional, low priority)
- Wrapper that starts both API + UI via hub, handles cleanup on exit

### Acceptance
- AGENTS.md documents hub-based dev server management
- No code changes to `src/sebi_rag/` required

---

## Summary of Changes

| Phase | Files Changed | Type | Effort |
|-------|--------------|------|--------|
| 1. LSP Convention | `AGENTS.md` | Doc update | 5 min |
| 2. Subagent Convention | `AGENTS.md` | Doc update | 5 min |
| 3. Browser Convention | `AGENTS.md` | Doc update | 5 min |
| 4. Retain Decisions | Memory system (no files) | Data entry | 10 min |
| 5. Hub Convention | `AGENTS.md` | Doc update | 5 min |

**Total: ~30 minutes, all doc/memory changes. Zero code changes.**

---

## Clarifying Questions

1. **Diagnostic triage:** Should we fix the 3 real type errors in `bench_retrieval.py` and `app.py` now, or defer? (They're in scripts/eval paths, not production pipeline.)

2. **Browser verification scope:** Should we verify the Gradio UI against the *current* state (post recent `fix(app)` changes) or wait for a specific change to verify?

3. **Dev server script:** Is `scripts/dev.sh` worth building, or is the AGENTS.md convention sufficient? (Convention alone means remembering hub commands; script means a one-liner `./scripts/dev.sh`.)

4. **Retain priority:** Should we also store evaluation metrics (MRR, citation_recall values from recent runs) or just architecture decisions?
