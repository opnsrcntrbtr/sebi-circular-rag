## Project

Local-first, Apple Silicon RAG over Indian SEBI Circulars. FastAPI service + Gradio UI. Hybrid retrieval (FAISS + BM25) with cross-encoder reranking, citation generation, and supersession-aware lineage.

## Quick Start

```bash
# Install deps (requires Python 3.12–3.13)
uv sync

# Run commands
make serve   # FastAPI backend on port 8000 (set SEBI_RAG_API_KEY in env)
make ui      # Gradio UI dashboard
make test    # Run offline test suite
make reindex # Annotate corpus + rebuild FAISS/BM25 index
make scrape   # Fetch SEBI circulars (MAX=N to limit count)
```

## Environment

- `SEBI_RAG_API_KEY` — API auth token (FastAPI key-in-body guard)
- `HF_HUB_DISABLE_XET=1`, `TOKENIZERS_PARALLELISM=false`, `PYTORCH_ENABLE_MPS_FALLBACK=1` — set via Makefile/Make variables (Apple Silicon MPS)
- `PORT` — default 8000; override with `PORT=9000 make serve`

## Source Structure (`src/sebi_rag/`)

| File | Purpose |
|------|---------|
| `api.py` | FastAPI entry point (app factory, auth middleware) |
| `pipeline.py` | Core RAG pipeline orchestration |
| `retrieve.py` | Hybrid FAISS + BM25 retrieval |
| `rerank.py` | Cross-encoder reranking |
| `embeddings.py` | Embedding generation (BGE-M3, etc.) |
| `lineage.py` | Circular supersession tracking |
| `corpus.py` | Corpus JSONL ingestion/persistence |
| `ui.py` | Gradio dashboard entry point |
| `settings.py` | Config-driven settings |

## Graphify (Optional)

Knowledge graph lives at `graphify-out/`. When the graph exists:

- Query: `graphify query "<question>"` — returns scoped subgraph (~50 tokens/result)
- Relationships: `graphify path "<A>" "<B>"`
- Concept: `graphify explain "<concept>"`
- Wiki navigation: if `graphify-out/wiki/index.md` exists, use it instead of raw source browsing
- For broad architecture review, check `graphify-out/GRAPH_REPORT.md`
- Keep current with: `graphify update .` (AST-only, no API cost)
