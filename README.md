# SEBI Circular RAG

Local-first, Apple Silicon RAG over Indian SEBI circulars. The system ingests official circulars, builds a hybrid FAISS + BM25 index, reranks results with a cross-encoder, generates grounded answers with an abstention gate, and returns citations with supersession status and faithfulness checks behind a config-driven FastAPI service.

## Current State

The project is not just a prototype. The current stack includes:

- A scraper and PDF ingestion path for SEBI circulars
- Chunking, metadata enrichment, lineage tracking, and persisted indexing
- Hybrid retrieval with reranking and grounded answer generation
- Answer-layer abstention, supersession warnings, and faithfulness checks
- Authenticated FastAPI `/health` and `/query` endpoints
- A Gradio UI for interactive exploration

The implementation details and validation history are tracked in [docs/status.md](docs/status.md) and the validation sequence is documented in [docs/validation_roadmap.md](docs/validation_roadmap.md).

## Quick Start

```bash
# Install dependencies
uv sync

# Start the API
make serve

# Start the UI
make ui

# Run the offline test suite
make test

# Rebuild the index after corpus updates
make reindex

# Fetch circulars
make scrape
```

`make serve` starts the FastAPI backend on port 8000. Set `SEBI_RAG_API_KEY` before launching.

## Recommended Usage

For a full installation and operator walkthrough, see [docs/USAGE.md](docs/USAGE.md). The Gradio UI demo is captured in [docs/assets/demo.webp](docs/assets/demo.webp).

## What Ships Today

- Hybrid retrieval with FAISS + BM25
- Cross-encoder reranking
- Grounded answers with abstention
- Faithfulness and supersession-aware safety checks
- Persisted index and lineage data for faster restarts
- FastAPI service and Gradio UI

## Road Map

The roadmap below reflects the current planning status from [docs/next_steps.md](docs/next_steps.md).

### Completed

- Packaging and deployment wiring is in place: config, persisted lineage, process scripts, and health/readiness support
- Larger MLX generation model sweep is complete and the current default is tuned for the existing corpus
- Corpus growth via the scraper has been implemented, including pagination and OCR fallback support

### In Progress / Remaining

- Expand corpus coverage with more regular circulars and continued ingestion validation
- Improve OCR handling for scanned PDFs that do not yield reliable text extraction
- Continue evaluation work as the corpus grows, especially calibration and benchmark maintenance
- Keep tightening safety for near-domain, non-governing queries

### Longer-Term Direction

- Improve retrieval precision as the corpus gets denser
- Strengthen groundedness-based abstention for legal-safety use cases
- Continue operational hardening so the service remains reproducible and easy to run locally

## Source Map

The core implementation lives under [src/sebi_rag/](src/sebi_rag/):

- [api.py](src/sebi_rag/api.py) - FastAPI app, auth, and endpoints
- [pipeline.py](src/sebi_rag/pipeline.py) - retrieval, reranking, generation, and gating orchestration
- [retrieve.py](src/sebi_rag/retrieve.py) - hybrid retrieval
- [rerank.py](src/sebi_rag/rerank.py) - cross-encoder reranking
- [lineage.py](src/sebi_rag/lineage.py) - supersession tracking
- [corpus.py](src/sebi_rag/corpus.py) - corpus ingestion and persistence
- [ui.py](src/sebi_rag/ui.py) - Gradio entry point
- [settings.py](src/sebi_rag/settings.py) - configuration model

## Notes

- `AGENTS.md` mirrors this workspace guidance for non-Claude agents
- `CLAUDE.md` is the authoritative workspace brief for Claude-based agents
