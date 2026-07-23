## Project

Local-first, Apple Silicon RAG over Indian SEBI Circulars. FastAPI service + Gradio UI. Hybrid retrieval (FAISS + BM25) with cross-encoder reranking, citation generation, and supersession-aware lineage.

## Quick Start

```bash
# Install deps (Python 3.12 only — pyproject pins >=3.12,<3.13; creates .venv/ which the Makefile uses)
uv sync

# Run commands
make serve   # FastAPI backend on port 8000 (set SEBI_RAG_API_KEY in env)
make ui      # Gradio UI dashboard
make ops     # Local ops HTTP server for n8n automations (port 8765)
make test    # Run offline test suite
make annotate # Recompute supersession status only
make index   # Build/persist FAISS+BM25 index and lineage.json only
make reindex # Annotate corpus + rebuild FAISS/BM25 index (chains annotate + index)
make scrape   # Fetch SEBI circulars (MAX=N to limit count)
make scrape-master   # Fetch SEBI master circulars (MAX_MASTER=N to limit count)
make verify-master    # Coverage report vs live SEBI master-circular listing (OFFLINE=1 to skip fetch)
make scrape-regs      # Fetch SEBI regulations (Updated List, sid=1&ssid=3)
make reg-edges        # Build circular→regulation edges + annotate corpus (offline, idempotent)
make audit-regs       # Precision audit of regulation edges (sample + Clopper-Pearson CI)
make calibrate       # Retrieval calibration sweep
make eval-asof # As-of-date golden eval; writes eval/runs/asof-$ASOF_OUT (default: baseline)
make bench-retrieval # Retrieval-only benchmark + TREC runfile
make bench-rerank    # Reranker benchmark (--models bge,qwen0.6b)
make benchmark-export # Golden v6 build + BEIR/TREC/RAG benchmark export
make export-datasets  # Export publishable dataset configs to dist/datasets
```

## Architecture

Pipeline: scrape → ingest_pdf → lineage.annotate → build_index → retrieve → rerank → generate.

| File (`src/sebi_rag/`) | Purpose |
|------|---------|
| `api.py` | FastAPI entry point, app factory, key-in-body auth |
| `pipeline.py` | `RAGPipeline` orchestration |
| `retrieve.py` | `HybridRetriever` — FAISS + BM25 RRF fusion (optional SPLADE leg, eval-only) |
| `rerank.py` / `embeddings.py` | Cross-encoder reranking / BGE-M3 embedding |
| `segment.py` | Hierarchical chunking (`CircularMeta`, `Chunk`) |
| `lineage.py` | Supersession tracking + corpus annotation |
| `regulations.py` | Regulation identity, alias table, name resolution |
| `reg_citations.py` | Regulation citations extracted from circular text |
| `reg_lineage.py` | Circular→regulation edges + `regulatory_basis_status` annotation |
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

## Testing & Evaluation

- `make test` runs `pytest -q -m "not integration"`. The `integration` marker exercises real
  bge-m3 / cross-encoder weights (slow) — run explicitly with `pytest -m integration`.
- Golden sets and probe queries live in `eval/golden/` and `eval/probes/`; benchmark runs land
  in `eval/runs/`. Retrieval changes are gated by an A/B run against these before promotion.
- Interventions are specced in `docs/superpowers/specs/`, planned in `plans/`, results in `reports/`.

## Environment

- `SEBI_RAG_API_KEY` — API auth token (FastAPI key-in-body guard)
- `HF_HUB_DISABLE_XET=1`, `TOKENIZERS_PARALLELISM=false`, `OMP_NUM_THREADS=1`, `PYTORCH_ENABLE_MPS_FALLBACK=1`, `PYTHONPATH=src` — all set via the Makefile `ENV` var; running scripts outside `make` needs them set manually
- `PORT` — default 8000; override with `PORT=9000 make serve`

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
