## Project

Local-first, Apple Silicon RAG over Indian SEBI Circulars. FastAPI service + Gradio UI. Hybrid retrieval (FAISS + BM25) with cross-encoder reranking, citation generation, and supersession-aware lineage.

## Quick Start

```bash
# Install deps (requires Python 3.12–3.13)
uv sync

# Run commands
make serve   # FastAPI backend on port 8000 (set SEBI_RAG_API_KEY in env)
make ui      # Gradio UI dashboard
make ops     # Local ops HTTP server for n8n automations (port 8765)
make test    # Run offline test suite
make reindex # Annotate corpus + rebuild FAISS/BM25 index
make scrape   # Fetch SEBI circulars (MAX=N to limit count)
make scrape-master   # Fetch SEBI master circulars (MAX_MASTER=N to limit count)
make verify-master    # Coverage report vs live SEBI master-circular listing (OFFLINE=1 to skip fetch)
make calibrate       # Retrieval calibration sweep
make bench-retrieval # Retrieval-only benchmark + TREC runfile
make bench-rerank    # Reranker benchmark (--models bge,qwen0.6b)
make benchmark-export # Golden v6 build + BEIR/TREC/RAG benchmark export
make export-datasets  # Export publishable dataset configs to dist/datasets
```

## Environment

- `SEBI_RAG_API_KEY` — API auth token (FastAPI key-in-body guard)
- `HF_HUB_DISABLE_XET=1`, `TOKENIZERS_PARALLELISM=false`, `PYTORCH_ENABLE_MPS_FALLBACK=1` — set via Makefile/Make variables (Apple Silicon MPS)
- `PORT` — default 8000; override with `PORT=9000 make serve`

## Current Handoffs

- Benchmark/evaluation continuation: `docs/superpowers/2026-07-09-benchmark-evaluation-handoff.md`
- Retrieval/benchmark infrastructure inventory: `docs/superpowers/2026-07-11-retrieval-benchmark-inventory.md`

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
