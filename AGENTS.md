# AGENTS.md

Canonical project guidance for all coding agents working in this repo. `CLAUDE.md` is a thin
`@AGENTS.md` import stub plus any Claude-Code-only notes — edit this file, not that one.

## Project

Local-first, Apple Silicon RAG over Indian SEBI Circulars. FastAPI service + Gradio UI. Hybrid retrieval (FAISS + BM25) with cross-encoder reranking, citation generation, and supersession-aware lineage.

## Principles

- Local-first, reproducible engineering.
- Apple Silicon first (MLX/MLX-LM preferred over generic runtimes where appropriate).
- Treat official SEBI publications as authoritative.

## Refusal Criteria (Explicit Triggers)

**Golden rule**: When in doubt, say "I don't know based on the available evidence." — never guess.

Full trigger table and the two abstention-gate thresholds (score floor vs. groundedness —
routinely confused, see the ⚠️ note there) live in `.claude/rules/refusal-criteria.md`. Read
it before citing a specific threshold value; do not restate the numbers here.

## Quick Reference (inline — no file read needed)

| Command | Purpose |
|---------|---------|
| `make serve` | FastAPI backend on port 8000 |
| `make ui` | Gradio UI dashboard |
| `make test` | Offline test suite (867 passed, 2 skipped) |
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

### Symbol-aware over text search
Prefer your runtime's symbol-aware navigation/refactor tools (definitions, references,
diagnostics, code actions) over grep-based renames when one is available — text search misses
cross-file callsites, re-exports, and dynamic dispatch targets. Claude Code: use its LSP tool
where present; otherwise Grep is the fallback, not the default.

### Browser Verification
- **Gradio UI changes:** Verify via a browser automation tool before yielding app changes. Open the Gradio UI, exercise changed paths, confirm visual output.
- **Never yield app changes** without browser verification of the actual surface — screenshots or aria snapshots as proof.

### Agent-specific tool surfaces
Some runtimes in this workspace additionally expose `lsp`/`scout`/`hub` primitives (oh-my-pi).
Claude Code does not — see `docs/oh-my-pi-tooling.md` only if your runtime provides that surface.

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
*Trigger: Use when running complex coding sessions that benefit from hardware-aware parameter
optimization, or when asked about the turn-based self-critique/correction pass.*

Full protocol (architecture, CLI commands, safety logic, Turn-Based Optimization lifecycle,
output schema) lives in `docs/telemetry_plugin.md` — read it on demand, not injected per turn.
