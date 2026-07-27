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

## Quick Start

See README.md for the full make target list. Common targets: `make serve` (API), `make test` (tests), `make reindex` (rebuild index).

## Context

Always consult before asking questions:
1. `docs/project_context.md` (architecture)
2. `docs/status.md` (completed work and blockers)

Infer completed work from these files before requesting information.

## Architecture

Pipeline: scrape → ingest_pdf → lineage.annotate → build_index → retrieve → rerank → generate.

| File (`src/sebi_rag/`) | Purpose |
|------|---------|
| `api.py` | FastAPI entry point, app factory, key-in-body auth |
| `pipeline.py` | `RAGPipeline` orchestration; `regulatory_basis_status` is surfaced per-citation in the API (`CitationMeta.regulations`) and UI, with an in-text advisory note for `repealed_basis` circulars |
| `retrieve.py` | `HybridRetriever` — FAISS + BM25 RRF fusion (optional SPLADE leg, eval-only) |
| `rerank.py` / `embeddings.py` | Cross-encoder reranking / BGE-M3 embedding |
| `segment.py` | Hierarchical chunking (`CircularMeta`, `Chunk`) |
| `lineage.py` | Supersession tracking + corpus annotation |
| `regulations.py` | Regulation identity, alias table, name resolution, `load_regulations`/`reg_display_name` |
| `reg_citations.py` | Regulation citations extracted from circular text |
| `reg_lineage.py` | Circular→regulation edges + `regulatory_basis_status` annotation; `build_regulatory_index` (query-layer lookup) |
| `generate.py` | Local generation + abstention gate (MLX-LM/Ollama via `Generator` protocol) |
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

### Validation Sequence

1.  Hardware & macOS
2.  Xcode CLT
3.  Homebrew
4.  Python + uv
5.  Git
6.  MLX
7.  Ollama
8.  PyTorch MPS (only if required)
9.  FAISS
10. Embeddings
11. Repository tests
12. End-to-end RAG

Never validate later stages until the current stage passes.

### Blockers

- Any FAIL is a blocker.
- Do not continue until resolved.
- `docs/status.md` must reflect resolution before proceeding.

## Testing & Evaluation

- `make test` runs `pytest -q -m "not integration"` (use `pytest -m integration` for real model weights).
- Golden sets live in `eval/golden/`; benchmark runs land in `eval/runs/`. Retrieval changes are gated by A/B runs before promotion.
- `golden_v7.jsonl` (n=260) is the reporting set; CI gates on frozen `golden_v5` until v7's `adjudicated_n >= 100`.
- Use `make validate-corpus` after any ingest or repair (see README.md for full golden-v7 pipeline and benchmark details).
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
- `HF_HUB_DISABLE_XET=1`, `TOKENIZERS_PARALLELISM=false`, `OMP_NUM_THREADS=1`, `PYTORCH_ENABLE_MPS_FALLBACK=1`, `PYTHONPATH=src` — all set via the Makefile `ENV` var; running scripts outside `make` needs them set manually
- `PORT` — default 8000; override with `PORT=9000 make serve`

## System Prompt

You are my engineering coworker for a production-grade local-first SEBI Circular RAG on Apple Silicon.

Rules:
- Be deterministic.
- Prefer concise responses.
- Validate one task only.
- Respect `docs/project_context.md` and `docs/status.md` as authoritative project context.
- Treat official SEBI documents as the primary legal authority.
- Never fabricate citations or legal interpretations.
- Never speculate if retrieval evidence is insufficient.
- Default to MLX/MLX-LM and Apple-native tooling when appropriate.
- Do not redesign the architecture unless explicitly requested.
- Never review files that were not provided.
- Never skip ahead in the validation sequence.
- Treat failed validation as a blocker.
- Return only the minimum information needed.

Validation response: Status: PASS / FAIL

Reason: Short explanation.

If FAIL:
- Root cause
- Exact commands
- Verification command

Always finish successful validations with:

PASS

Next recommended step: `<single next validation task>`

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).