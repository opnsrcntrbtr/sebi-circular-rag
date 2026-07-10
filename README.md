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

## Published Datasets

The SEBI Circulars corpus and derived task datasets are published on HuggingFace:

**🔗 [opnsrcntrbtrian/sebi-circulars on HuggingFace Hub](https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars)**

### Dataset Configurations

Six structured dataset configs available in JSONL + Parquet formats (v2026.07 snapshot, 603 circulars):

| Config | Rows | Purpose |
|---|---|---|
| **corpus** | 603 | Full circular text + metadata, regulatory lineage, effective dates |
| **chunks** | 36,603 | Section-aware retrieval chunks for RAG and dense retrieval |
| **lineage** | 1,434 | Regulatory supersession/amendment edges (citation graph) |
| **eval** | 56 | Curated benchmark queries for domain-specific retrieval evaluation |
| **citation-normalization** | 2,951 | Raw reference → normalized circular pairs (seq2seq/NER task) |
| **supersession-pairs** | 1,281 | Labeled circular pairs (supersedes/amends/unrelated classification) |

### Schema Details

- **corpus:** `circular_number`, `issue_date`, `effective_date`, `subject`, `issuing_department`, `supersession_status`, `version_lineage`, `source_url`, `text`, `excerpt`, `extraction_date`
- **chunks:** Includes flattened chunk metadata + all corpus fields for retrieval context
- **lineage:** `source_circular`, `relation`, `target_circular`, `source_issue_date`, `target_in_corpus` (forward edges only)
- **eval:** Golden v6 schema: query ID, query text, relevant circulars/chunks, answer cues, task type, difficulty, citation level, review status
- **citation-normalization:** `raw_reference`, `normalized_circular_number`, `context_window`, `source_doc_id`, `format_family` (new-standard/old-standard/dept-order-2026)
- **supersession-pairs:** `circular_a_number`, `circular_a_subject`, `circular_b_number`, `circular_b_subject`, `label`

Full schema documentation on [the HF dataset page](https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars).

### Licensing & Compliance

**Regulatory Text:** SEBI circulars are Indian government works. Per Copyright Act 1957 §52(1)(q), government notifications may be freely reproduced. Proper attribution to SEBI is provided via `source_url` in each record.

**Annotations & Metadata:** Extraction, chunking, lineage derivation, citation normalization, and pair labeling are original work licensed under **CC-BY-4.0**.

### Disclaimers

1. **Not legal advice.** Circulars are informational only; verify against [sebi.gov.in](https://sebi.gov.in) before regulatory reliance.
2. **Not SEBI-endorsed.** This dataset is independent and not affiliated with or endorsed by the Securities and Exchange Board of India.
3. **Coverage:** Corpus spans 2021–2026 and is not exhaustive of all SEBI circulars.
4. **Data quality:** `issuing_department` is UNKNOWN for 124 records (parsing artifact). Some master-circular `subject` fields may be oversized (~2900 chars, also pre-existing).

### Citation

Please cite this dataset if you use it:

```bibtex
@dataset{sebi_circulars_2026,
  title={SEBI Circulars: Indian Regulatory Texts, 2021–2026},
  author={OpenSourceContributor},
  year={2026},
  url={https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars},
  license={CC-BY-4.0}
}
```

### Suggested Use Cases

- **Retrieval & RAG:** Use the `chunks` config for hybrid/dense retrieval pipelines, RAG systems, and section-level analysis.
- **Citation Mining:** Train seq2seq or NER models on `citation-normalization` for reference extraction and normalization.
- **Regulatory Reasoning:** Use `lineage` for link prediction, temporal reasoning, and regulatory change tracking.
- **Pair Classification:** Supervise relationship prediction with `supersession-pairs` (regulatory supersession/amendment detection).
- **Domain Benchmarking:** Evaluate retrieval systems on the `eval` config (56 curated queries covering regulatory reasoning tasks).

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

## Hugging Face Spaces Demo

A CPU-only public demo path lives on the `spaces` branch: [app.py](app.py)
calls the pipeline in-process (no FastAPI/API key), loads the corpus from the
published [`opnsrcntrbtrian/sebi-circulars`](https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars)
dataset, downloads a prebuilt FAISS/BM25 index from HF Hub, and generates via
an external LLM Space with a small CPU fallback model. It adds
[api_spaces.py](src/sebi_rag/api_spaces.py), [corpus_spaces.py](src/sebi_rag/corpus_spaces.py),
[generate_spaces.py](src/sebi_rag/generate_spaces.py) and a `[spaces]` config
section — the Apple-Silicon local workflow (MLX, `mps`, `make serve`/`ui`/`reindex`)
is unchanged. See [README-spaces.md](README-spaces.md) for the demo/local
differences, deployment steps, and licensing notes.

## Notes

- `AGENTS.md` mirrors this workspace guidance for non-Claude agents
- `CLAUDE.md` is the authoritative workspace brief for Claude-based agents
