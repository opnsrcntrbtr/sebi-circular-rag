# AGENTS.md

This file mirrors the workspace guidance in `CLAUDE.md` for non-Claude agents and models.

## Project

Local-first, Apple Silicon RAG over Indian SEBI Circulars. FastAPI service + Gradio UI. Hybrid retrieval with FAISS + BM25, cross-encoder reranking, citation generation, and supersession-aware lineage.

## Quick Start

```bash
# Install deps (requires Python 3.12-3.13)
uv sync

# Run commands
make serve   # FastAPI backend on port 8000 (set SEBI_RAG_API_KEY in env)
make ui      # Gradio UI dashboard
make test    # Run offline test suite
make reindex # Annotate corpus + rebuild FAISS/BM25 index
make scrape  # Fetch SEBI circulars (MAX=N to limit count)
```

## Environment

- `SEBI_RAG_API_KEY` - API auth token for the FastAPI key-in-body guard
- `HF_HUB_DISABLE_XET=1`, `TOKENIZERS_PARALLELISM=false`, `PYTORCH_ENABLE_MPS_FALLBACK=1` - set via Makefile/Make variables for Apple Silicon MPS
- `PORT` - default `8000`; override with `PORT=9000 make serve`

## Source Structure (`src/sebi_rag/`)

| File | Purpose |
|------|---------|
| `api.py` | FastAPI entry point, app factory, auth middleware |
| `benchmark.py` | Golden v6 validation, BEIR/TREC export, run metadata helpers |
| `pipeline.py` | Core RAG pipeline orchestration |
| `retrieve.py` | Hybrid FAISS + BM25 retrieval |
| `rerank.py` | Cross-encoder reranking |
| `embeddings.py` | Embedding generation (BGE-M3, etc.) |
| `lineage.py` | Circular supersession tracking |
| `corpus.py` | Corpus JSONL ingestion and persistence |
| `ui.py` | Gradio dashboard entry point |
| `settings.py` | Config-driven settings |

## Graphify (Optional)

Knowledge graph lives at `graphify-out/`. When the graph exists:

- Query: `graphify query "<question>"` - returns scoped subgraph (~50 tokens/result)
- Relationships: `graphify path "<A>" "<B>"`
- Concept: `graphify explain "<concept>"`
- Wiki navigation: if `graphify-out/wiki/index.md` exists, use it instead of raw source browsing
- For broad architecture review, check `graphify-out/GRAPH_REPORT.md`
- Keep current with `graphify update .` (AST-only, no API cost)

## Current Handoffs

- Benchmark/evaluation continuation: `docs/superpowers/2026-07-09-benchmark-evaluation-handoff.md`

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
