# AGENTS.md

This file mirrors the workspace guidance in `CLAUDE.md` for non-Claude agents and models.

## Project

Local-first, Apple Silicon RAG over Indian SEBI Circulars. FastAPI service + Gradio UI. Hybrid retrieval (FAISS + BM25) with cross-encoder reranking, citation generation, and supersession-aware lineage.

## Principles

- Local-first, reproducible engineering.
- Apple Silicon first (MLX/MLX-LM preferred over generic runtimes where appropriate).
- Treat official SEBI publications as authoritative.

## Refusal Criteria (Explicit Triggers)

When any of these conditions apply, refuse or abstain — do not guess:

| Trigger | Response |
|---------|----------|
| Insufficient retrieved evidence for a legal/regulatory question | "I don't know based on the available evidence." |
| Request to redesign the architecture without explicit instruction | "Not without explicit request. Current architecture is validated — 791 tests passing." |
| Request to review files not provided | "I can only review files you provide. Please supply the diff or file contents." |
| Request to fabricate citations, legal interpretations, or data | Refuse outright. No fabrication of SEBI circulars, regulations, or metrics. |
| Retrieval confidence below abstention threshold (~0.4) | Return the evidence only; do not generate a conclusion. |
| Task outside coding agent scope (e.g., infrastructure ops, non-code changes) | Decline and suggest the appropriate owner or tool. |

**Golden rule**: When in doubt, say "I don't know based on the available evidence." — never guess.

## Quick Reference (inline — no file read needed)

| Command | Purpose |
|---------|---------|
| `make serve` | FastAPI backend on port 8000 |
| `make ui` | Gradio UI dashboard |
| `make test` | Offline test suite (791 passed) |
| `make reindex` | Annotate corpus + rebuild index |
| `make index` | Build/persist FAISS+BM25 only |
| `make scrape` | Fetch SEBI circulars (MAX=N) |
| `make scrape-master` | Fetch master circulars (MAX_MASTER=N) |
| `make calibrate` | Retrieval calibration sweep |
| `make eval-asof` | As-of-date golden eval |
| `make bench-retrieval` | Retrieval-only benchmark |
| `make bench-rerank` | Reranker benchmark |
| `make benchmark-export` | BEIR/TREC/RAG export |
| `make export-datasets` | Export dataset configs |
| `make measure` | Collect pipeline metrics (parsing latency, retrieval recall, MRR, etc.) |
| `make golden-v7-gate` | Arm v7 CI gate (refuses <100 adjudicated) |

For the full target list, read `README.md`.

## Context Files (read on demand — NOT pre-injected)

The agent reads these files only when the task requires their content. They are **not** pre-loaded into the system prompt.

1. **`docs/project_context.md`** — Architecture, validation sequence, evaluation metrics, design decisions. Read when you need: architecture details, validation steps, calibration parameters, golden-set info, or directory structure.
2. **`docs/status.md`** — Completed work, blockers, historical decisions. Read when you need to understand what work has been completed, what blockers exist, or the history of a specific feature.

Infer completed work from `docs/status.md` before requesting information. Read `docs/project_context.md` when you need architecture details.

## Architecture

Pipeline: scrape → ingest_pdf → lineage.annotate → build_index → retrieve → rerank → generate.

| File (`src/sebi_rag/`) | Purpose |
|------|---------|
| `api.py` | FastAPI entry point, app factory, key-in-body auth |
| `pipeline.py` | `RAGPipeline` orchestration; `regulatory_basis_status` surfaced per-citation |
| `retrieve.py` | `HybridRetriever` — FAISS + BM25 RRF fusion (SPLADE eval-only) |
| `rerank.py` / `embeddings.py` | Cross-encoder / BGE-M3 embedding |
| `segment.py` | Hierarchical chunking (`CircularMeta`, `Chunk`) |
| `lineage.py` | Supersession tracking + corpus annotation |
| `regulations.py` | Regulation identity, alias table, name resolution |
| `reg_citations.py` | Regulation citations from circular text |
| `reg_lineage.py` | Circular→regulation edges + `regulatory_basis_status` |
| `generate.py` | Local generation + abstention gate (MLX-LM/Ollama) |
| `eval.py` / `eval_harness.py` / `benchmark.py` | Metrics, golden-set runner, BEIR/TREC export |
| `splade.py`, `hyde.py`, `context_headers.py` | Retrieval experiments (opt-in, off by default) |

### ⚠️ Two parallel code paths

`*_spaces.py` (`api_spaces`, `corpus_spaces`, `generate_spaces`) plus root `app.py` are the
CPU-only Hugging Face Spaces demo — no MLX/MPS. **Do not edit the Spaces modules when fixing
the local Apple-Silicon pipeline, or vice versa.** Config lives in `config.toml [spaces]`;
runbook in `README-spaces.md`.

### ⚠️ Never add fields to `CircularMeta`

`hierarchical_chunk()` does `meta=asdict(meta)` (`segment.py:131`), so a new
`CircularMeta` field lands in every chunk payload (77.8k chunks) and mutates the
persisted index. Additive per-circular metadata goes on the corpus JSONL record
only — see `master_meta.annotate_master_fields` and
`reg_lineage.annotate_regulation_fields`.

## Validation

See `docs/project_context.md` §6 for the full validation sequence (12 steps).

### Blockers

- Any FAIL is a blocker.
- Do not continue until resolved.
- `docs/status.md` must reflect resolution before proceeding.

## Testing & Evaluation

- `make test` runs `pytest -q -m "not integration"`.
- Golden sets live in `eval/golden/`; benchmark runs land in `eval/runs/`.
- `golden_v7.jsonl` (n=260) is the reporting set; CI gates on `adjudicated_n >= 100`.
- Use `make validate-corpus` after any ingest or repair.
- Interventions are specced in `docs/superpowers/specs/`, planned in `plans/`, results in `reports/`.

## Workflow

### Code Review

Review only supplied files. Never infer contents of unseen files. If changes elsewhere are
needed, describe them abstractly and request those files.

### Debugging

Inputs: Goal, Command, Last 20–30 log lines.

Return: PASS / FAIL, One most likely root cause, One best fix, Verification command.

### Performance

Optimize only validated stages. Recommend changes expected to produce measurable (>10%) benefit.

## Tool Usage Conventions

### LSP-First (symbol-aware over text search)
- **Rename/refactor:** Always use `lsp references` before renaming any exported symbol. Text grep misses cross-file callsites, re-exports, and dynamic dispatch targets.
- **Pre-edit check:** Run `lsp diagnostics` on the target file before editing to surface existing type errors or unused imports.
- **Code actions:** Prefer `lsp code_actions` for import fixes, quick-fixes, and server-known refactors over hand edits.
- **Definition/type:** Use `lsp definition` / `lsp type_definition` for navigation; never guess symbol locations.

### Subagent Parallelism
- **Multi-file changes:** Dispatch parallel `scout` agents for independent file discovery (e.g., find all callers of a symbol, locate test files).
- **Independent tasks:** Use `task` with parallel subagents for truly independent work slices — no serialization unless data dependency exists.
- **No overhead:** Each task must skip formatters, linters, and project-wide test suites. Validate once at the end.

### Browser Verification
- **Gradio UI changes:** Verify via `browser` tool before yielding app changes. Open the Gradio UI, exercise changed paths, confirm visual output.
- **Never yield app changes** without browser verification of the actual surface — screenshots or aria snapshots as proof.

### Hub Dev Server Lifecycle
- **FastAPI/Gradio:** Use `hub start` for long-running services (dev server, watcher, debugger). Never use raw `bash` for persistent processes.
- **Pattern:** `hub start name="api" application="make" args=["serve"] ready={log: "Uvicorn running", port: 8000, timeout: 30}`
- **Teardown:** `hub stop api` before killing terminal; `hub restart api` for config changes.

## Environment

- `SEBI_RAG_API_KEY` — API auth token (FastAPI key-in-body guard)
- `HF_HUB_DISABLE_XET=1`, `TOKENIZERS_PARALLELISM=false`, `OMP_NUM_THREADS=1`, `PYTORCH_ENABLE_MPS_FALLBACK=1`, `PYTHONPATH=src` — all set via the Makefile `ENV` var
- `PORT` — default 8000; override with `PORT=9000 make serve`

> **Cache note:** This file is part of the stable prompt prefix (~9.2KB). Do not add timestamps, session IDs, or dynamic content. Changes to any prefix byte invalidate the cache.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## Output Constraints
- Use explicit output schemas (JSON, markdown tables, bullet lists).
- Ask for diffs instead of full rewrites.
- Keep responses concise — prefer bullet points over prose.
- When validation fails, return: Status, Reason, Root cause, Exact commands, Verification command.
- When validation passes, return: PASS + Next recommended step.

## Session Workflow
- Split work into phases: discovery → implementation → verification. Start fresh sessions (`/new`) for each phase.
- Carry forward a spec/summary between sessions (write to file, read in next session).
- Use `--fork` to branch from a decision point without carrying stale history.
- Stale context from failed attempts charges you on every subsequent turn — reset when switching phases.

## Model Routing
- Simple tasks (extraction, classification, formatting, short code edits) → use `low` thinking level.
- Standard tasks (debugging, multi-file changes, testing) → use `medium` thinking level.
- Complex tasks (architecture decisions, validation sequences, complex refactoring) → use `high` thinking level via `/model`.
- Route tasks to match model strength to task risk. Keep stronger models for ambiguous planning and final synthesis.

## 📉 Status Optimization Protocol
*Trigger: Apply these rules whenever creating, updating, or reading `@docs/status.md`.*

**Goal:** Maintain `@docs/status.md` as a **High-Density Context Anchor** optimized for LLM token limits (Hot Cache), not human reading.

**Strict Formatting Rules:**
1.  **Prose-to-Data Conversion**: Never write descriptive paragraphs. Convert all system states, configurations, and environment details into **YAML** or **JSON-like Key-Value** blocks.
    *   *Bad:* "The server runs on port 8001 and uses the v1 api."
    *   *Good:* `server: { port: 8001, api: v1, status: active }`
2.  **Visual State Matrix**: Use emoji flags (✅, ⚠️, ❌, ⏳) and single-line tables to track feature progress.
3.  **Zero Fluff**: Strip all meta-commentary ("Here is the status...", "I have updated..."). The file must contain **only** facts.
4.  **Anchor Preservation**: You are FORBIDDEN from abbreviating file paths, error constants, API routes, or variable names. These are **Retrieval Anchors** and must match the codebase character-for-character.
5.  **TDD/BDD Parity**: Ensure the status reflects *current* passing tests. Do not document planned features as "active" unless verified by a passing test.

## 📉 Documentation Token Optimization Protocol
*Trigger: Apply these rules whenever creating, updating, or reading files inside `@docs/`.*

**Goal:** Maintain documentation as high-density, low-token Context Anchors optimized for LLM Hot Cache processing rather than fluid human reading.

**Strict Formatting Rules:**
1. **System-to-Schema Conversion**: Convert all descriptive system states, folder directories, module purposes, configurations, and data flows into **YAML** or single-line JSON structures. Never use narrative paragraphs.
2. **Zero-Fluff State Matrices**: Use compact tables and explicit emoji status flags to track features. Eliminate historical logs, alternative options that were skipped, or prose justifications.
3. **Anchor Preservation**: You are strictly FORBIDDEN from abbreviating or modifying file paths, exact technological stack tags, domain structures, error constants, or variable names. They must match the source files character-for-character to maintain exact semantic retrieval hooks.
4. **TDD/BDD Alignment**: Documentation metrics must map directly to active BDD feature files or unit test baselines. Do not document unverified or loose conceptual ideas as active states.

## 🧠 Self-Optimization Plugin (Telemetry Engine)
*Trigger: Use when running complex coding sessions that benefit from hardware-aware parameter optimization.*

**Purpose:** Sustainable meta-optimization loop between hardware (Mac M4 48GB), oMLX inference server (Qwen3.6-35B on 127.0.0.1:8001), and coding output quality.

**Location:** `scripts/telemetry_engine.py`
**Storage:** `~/.omp/telemetry_history.json`
**Full reference:** `docs/telemetry_plugin.md` (on-demand read, not injected per turn)

### Commands
| Command | Description |
|---|---|
| `python scripts/telemetry_engine.py status` | Show hardware state, safety margin, oMLX connectivity |
| `python scripts/telemetry_engine.py record --quality 5` | Record run outcome (1-5 scale) |
| `python scripts/telemetry_engine.py record --success` | Shortcut for quality=5 |
| `python scripts/telemetry_engine.py record --fail` | Shortcut for quality=1 |
| `python scripts/telemetry_engine.py suggest "Complex Coding"` | Get optimized parameters from historical data |
| `python scripts/telemetry_engine.py history --top 10` | Show recent telemetry entries |

### Safety Logic
- **Soft limit:** 3.3 GB RAM headroom (free_ram >= 3.3 GB)
- If violated: flags run as "Unstable", recommends reducing oMLX Hot Cache or Context Window
- Only safe runs (is_safe=true) are used for parameter optimization

### Integration Workflow
1. Before complex coding session: run `suggest "Complex Coding"` to get optimal params
2. After session: run `record --quality N` (or `--success`/`--fail`)
3. Review: run `history --top 20` to see trends over time

### Parameter Defaults (used when no history exists)
- Complex Coding: temperature=0.2, min_p=0.05, context_window=8192
- Simple Query: temperature=0.1, min_p=0.1, context_window=4096


### Turn-Based Optimization (Auto-Run After Every Turn)
*Trigger: Runs automatically at the conclusion of EVERY conversational turn.*

**Lifecycle:** Execute after generating initial internal draft, prior to rendering final output.

**Threshold-Gated Optimization (NEW):**
- Only triggers when current score drops below rolling baseline by DRIFT_MARGIN (default: 1.0)
- Baseline computed from last BASELINE_WINDOW (default: 10) turns
- Prevents unnecessary optimization when output quality is stable

**Workflow (4 hidden steps):**
1. **State Analysis:** Inspect prompt complexity, code/schema presence, multi-file scope
2. **Draft Generation:** Produce optimal structural candidate response
3. **Self-Critique Matrix:** Score draft against three criteria:
   - Conciseness (0-10): penalize filler phrases, long sentences
   - Technical Fidelity (0-10): flag outdated patterns, syntax errors
   - Instruction Adherence (0-10): verify response matches prompt requirements
4. **Degradation Check:** Compare scores against baseline (avg - DRIFT_MARGIN)
   - If degraded: apply Correction Pass + record to telemetry
   - If not degraded: skip optimization (return "Fully Optimized")

**Output Schema (rendered above primary response):**
```
[⚙️ Plugin Optimizations: Fully Optimized]          ← no degradation detected
[⚙️ Plugin Optimizations: Degraded X→Y, corrected]  ← degradation detected + fixed
```

**CLI Access:** `python scripts/telemetry_engine.py optimize --prompt "..." --draft "..." [--json]`




