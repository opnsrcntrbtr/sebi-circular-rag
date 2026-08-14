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

The implementation details and validation history are tracked in [docs/status.md](docs/status.md) and the validation sequence is documented in [docs/project_context.md](docs/project_context.md).

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
make export-datasets  # Export dataset configs (JSONL + Parquet)
make measure     # Collect pipeline metrics (parsing latency, retrieval recall, MRR, etc.)
make rescore     # Rescore existing eval runs
make trec-parity # TREC runfile parity check
make qrels       # Generate QRELS for TREC evaluation
```

## Testing & Evaluation

- `make test` runs `pytest -q -m "not integration"`. The `integration` marker exercises real bge-m3 / cross-encoder weights (slow) — run explicitly with `pytest -m integration`.
 - `scripts/bench_metrics.py` collects 6 pipeline metrics (parsing latency, supersession precision, temporal accuracy, retrieval recall, context precision, MRR). Run via `make measure` or `python scripts/bench_metrics.py --smoke` for a fast smoke test. Outputs to `.auto/measure.sh` for the autoresearch dashboard.
- `golden_v7.jsonl` (n=260, stratified, span-anchored `{doc, quote}` chunk labels, plus a `review_status` lifecycle of `seeded`/`draft` → `adjudicated`) is the reporting set. **CI does not gate on it yet.** `scripts/eval_json.py` reports on v7 only once `eval/golden/gate_v7.json` exists *and* records `adjudicated_n >= 100`; until then it falls back to frozen `golden_v5`, so a partially reviewed v7 cannot silently become the set that gates merges. `SEBI_RAG_GOLDEN` overrides the choice. Arm the gate with `make golden-v7-gate` (refuses below 100 and says why). `golden_v1..v6`, `probes_v1`, and `golden_asof_v1` are frozen.
- `make golden-v7-*` drives the v7 pipeline: `-seed`, `-mine`, `-pool`, `-packet`, `-packet-ingest`, `-local`, `-gemini`, `-agree`, `-agree-report`, `-gate`. The **primary** external-annotation leg (`-local`) calls a local oMLX server (Anthropic-compatible API on `127.0.0.1:8001` — deliberately not 8000, which `make serve` binds; `Qwen3.6-35B-A3B-MLX-4bit`, votes as `annotator: "qwen"`) — no quota, no network. The Gemini leg (`-gemini`) is ON HOLD: its free tier allows ~20 requests/day/model, a multi-day wall for a 100-row pass. Both legs cache per row and resume, and every row in one leg must come from the **same** model or the agreement statistics measure model differences rather than label uncertainty (`agreement.py` discovers the LLM leg generically and fails loud on two at once).
- `make validate-corpus` checks corpus integrity: no two records share a body text, and each record's `circular_number` is derivable from its own text. Add `--deep` to also re-extract every PDF and compare. **Run it after any ingest, backfill, or repair** — both invariants exist because those bug classes shipped undetected (see `docs/status.md` 2026-07-25).
- Interventions are specced in `docs/superpowers/specs/`, planned in `plans/`, results in `reports/`.

## Recommended Usage

For a full installation and operator walkthrough, see [docs/USAGE.md](docs/USAGE.md). The Gradio UI demo is captured in [docs/assets/demo.webp](docs/assets/demo.webp).

## Published Datasets

The SEBI Circulars corpus and derived task datasets are published on HuggingFace:

**🔗 [opnsrcntrbtrian/sebi-circulars on HuggingFace Hub](https://huggingface.co/datasets/opnsrcntrbtrian/sebi-circulars)**

### Dataset Configurations

Six structured dataset configs available in JSONL + Parquet formats (v2026.08 snapshot, 728 circulars):

| Config | Rows | Purpose |
|---|---|---|
| **corpus** | 728 | Full circular text + metadata, regulatory lineage, effective dates |
| **chunks** | 78,585 | Section-aware retrieval chunks for RAG and dense retrieval |
| **lineage** | 4,577 | Regulatory supersession/amendment edges (citation graph) |
| **eval** | 56 | Curated benchmark queries for domain-specific retrieval evaluation |
| **citation-normalization** | 8,901 | Raw reference → normalized circular pairs (seq2seq/NER task) |
| **supersession-pairs** | 2,769 | Labeled circular pairs (supersedes/amends/unrelated classification) |

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
3. **Coverage:** Corpus spans 2010–2026, including all 130 SEBI master circulars, and is not exhaustive of all SEBI circulars.
4. **Data quality:** `issuing_department` is UNKNOWN for 0/728 records (parsing artifact resolved). Some master-circular `subject` fields may be oversized (~2900 chars, also pre-existing).

### Citation

Please cite this dataset if you use it:

```bibtex
@dataset{sebi_circulars_2026,
  title={SEBI Circulars: Indian Regulatory Texts, 2010–2026},
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

### Longer-Term Direction

- Improve retrieval precision as the corpus gets denser
- Strengthen groundedness-based abstention for legal-safety use cases
- Continue operational hardening so the service remains reproducible and easy to run locally

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
| `generate.py` | Local generation + abstention gate (MLX-LM/Ollama via `Generator` protocol); `select_citations()` B' answer-relevance filter |
| `eval.py` / `eval_harness.py` / `benchmark.py` | Metrics, golden-set runner, BEIR/TREC export |
| `splade.py`, `hyde.py`, `context_headers.py` | Retrieval experiments (opt-in, off by default) |
| `attribution.py` | Attribution scoring for generated answers |
| `settings.py` | Configuration model (`Settings`) with env overrides |
| `stats.py` | Corpus/index statistics helpers |
| `device.py` | Device detection (MPS/CPU) for MLX backend selection |
| `eval_asof.py` | As-of-date golden evaluation runner |
| `measure.py` | Pipeline metrics collection (parsing latency, retrieval recall, MRR) |
| `splade_encoder.py` | SPLADE sparse encoder (eval-only, off by default) |
| `expand.py` | Query expansion utilities |
| `master_meta.py` | Master circular metadata management (`annotate_master_fields`) |
| `corpus.py` | Corpus I/O and validation helpers |
| `metadata.py` | Metadata schema definitions |

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

## Notes

- `AGENTS.md` mirrors this workspace guidance for non-Claude agents
- `CLAUDE.md` is the authoritative workspace brief for Claude-based agents (absorbed all content from the former `SEBI_RAG_Claude_Desktop_Engineering_Handbook.md`)
- `SEBI_RAG_Claude_Desktop_Engineering_Handbook.md` is now redundant — its unique content (Principles, Context, Validation, Workflow, System Prompt) has been absorbed into `CLAUDE.md` and `AGENTS.md`
