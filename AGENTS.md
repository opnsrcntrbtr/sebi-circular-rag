# AGENTS.md

This file mirrors the workspace guidance in `CLAUDE.md` for non-Claude agents and models.

## Project

Local-first, Apple Silicon RAG over Indian SEBI Circulars. FastAPI service + Gradio UI. Hybrid retrieval (FAISS + BM25) with cross-encoder reranking, citation generation, and supersession-aware lineage.

## Principles

- Local-first, reproducible engineering.
- Apple Silicon first (MLX/MLX-LM preferred over generic runtimes where appropriate).
- Treat official SEBI publications as authoritative.
- If retrieved evidence is insufficient, reply "I don't know" rather than guessing.
- Never change the agreed architecture unless explicitly requested.

## Quick Reference (inline — no file read needed)

| Command | Purpose |
|---------|---------|
| `make serve` | FastAPI backend on port 8000 |
| `make ui` | Gradio UI dashboard |
| `make test` | Offline test suite (546 functions) |
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
| `make validate-corpus` | Corpus integrity check (run after ingest/repair) |
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
