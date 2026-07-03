# Project Context — SEBI Circular RAG

> Authoritative architecture record. Consult before requesting any information.
> Governed by `SEBI_RAG_Claude_Desktop_Engineering_Handbook.md`. Last updated: 2026-06-29.

## 1. Purpose

Production-grade, local-first Retrieval-Augmented Generation system over Indian
SEBI Circulars. Optimised for deterministic engineering, reproducibility, minimal
token consumption, Apple Silicon performance, and legal-domain factual accuracy.
Official SEBI publications are authoritative; if retrieved evidence is
insufficient the system answers **"I don't know based on the available
evidence."** rather than guessing.

## 2. Hardware

- MacBook Pro (November 2024)
- Apple M4 Pro, 14-core CPU
- 48 GB unified memory
- 1 TB SSD

## 3. Operating System

- Latest stable macOS (version pinned during Validation Step 1).
- Local-first AI stack; no external GPU; allowlisted network only for corpus
  fetch and dependency install.

## 4. Target Architecture

Pipeline stages:

1. **Ingestion** — fetch official SEBI circulars; record provenance (source URL,
   fetch date, checksum).
2. **Segmentation (mandatory)** — hierarchical chunking: document → section →
   paragraph, packed to ≈1200 chars with ≈150-char overlap. PDF-aware: when
   extracted text lacks blank-line breaks, falls back to single-newline, then
   sentence, then hard-window splitting (no mid-clause splits where a break
   exists). Each chunk carries a stable retrieval ID for precise citation.
3. **Metadata extraction (mandatory)** — per document/chunk: circular number,
   issue date, effective date, subject, issuing department, supersession status,
   amendment history, version lineage. Cross-document supersession is resolved by
   `lineage.py` (P2): references are classified supersedes/amends/cites from the
   circular text, AND master-circular re-issues are detected by normalised title
   (newest version supersedes older), producing a lineage graph and an
   in_force|superseded|amended status; superseded chunks are demoted in rerank and
   flagged at retrieval time.
4. **Indexing** — Dense: FAISS (HNSW/Flat, in-memory) over bge-m3 baseline
   embeddings. Sparse: BM25 lexical index (bm25s or Tantivy). Indexes are
   versioned.
5. **Stage-1 retrieval (mandatory hybrid)** — dense (FAISS) + sparse (BM25) run in
   parallel, fused by Reciprocal Rank Fusion (RRF) into a candidate pool of ~50–100.
6. **Stage-2 reranking (mandatory)** — cross-encoder reranker
   (bge-reranker-v2-m3 / Qwen3-Reranker via MLX) → top-k context.
7. **Generation** — local LLM. Default MLX-LM Qwen2.5-1.5B-4bit (Apple-Silicon
   native; sweep: faithfulness 1.0, groundedness 0.89, ~2.6s/query; 3B avail for
   groundedness 0.95 @ 3.3s). Ollama optional via SEBI_RAG_GENERATOR. Abstention
   gate:
   if reranker confidence is below the configured threshold, return the abstention
   answer; never generate unsupported legal conclusions.
8. **Evaluation (mandatory component)** — see §7.

```
                ┌─ Dense ANN  (FAISS, bge-m3 baseline) ─┐
Query ──────────┤                                       ├─ RRF ─ pool(50–100) ─ cross-encoder reranker ─ top-k ─ LLM ─ answer + citations
                └─ Sparse lexical (BM25 / Tantivy) ─────┘                                                              │
                                                                                                   abstain if below threshold
```

## 5. Dependency Versions

Versions are pinned at their validation step; entries marked *(pin @ validation)*
are confirmed against the installed toolchain before use — not assumed here.

- Xcode Command Line Tools — *(pin @ validation)*
- Homebrew — *(pin @ validation)*
- Python — 3.12.13 (project `.venv`; system default 3.14.6 unused — no mlx-lm wheel)
- uv — 0.11.25
- Git — 2.54.0 (Homebrew; Apple Git 2.50.1 also present)
- MLX 0.31.2 / MLX-LM 0.31.3 (validated in `.venv`)
- Ollama — 0.19+ (MLX backend on Apple Silicon) *(pin @ validation)*
- PyTorch (MPS) — 2.12.1 (**required**: baseline runtime for bge-m3 embeddings +
  cross-encoder reranker via sentence-transformers / FlagEmbedding)
- sentence-transformers — 5.6.0
- FlagEmbedding — 1.4.0
- FAISS — faiss-cpu 1.14.3 (Apple Silicon arm64)
- hf-xet — 1.5.1 (Xet transfer; large weights). Note: bge-m3 weights are Xet-backed;
  if downloads stall, set `HF_HUB_DISABLE_XET=1` and ignore onnx/`pytorch_model.bin`
  duplicates as needed.
- Embedding model — bge-m3 (baseline, runs on PyTorch MPS; dense 1024 + sparse +
  ColBERT validated)
- Reranker — bge-reranker-v2-m3 via **sentence-transformers CrossEncoder** on MPS
  (validated). NOTE: FlagEmbedding 1.4.0 FlagReranker is incompatible with
  transformers 5.12.1 (`prepare_for_model` removed) — use CrossEncoder, not
  FlagReranker.
- Lexical index — bm25s or Tantivy *(select @ retrieval stage)*

## 6. Validation Sequence

Exactly the handbook sequence; no additions. One step at a time; never validate a
later stage until the current one passes.

1. Hardware & macOS
2. Xcode CLT
3. Homebrew
4. Python + uv
5. Git
6. MLX
7. Ollama
8. PyTorch MPS (only if required)
9. FAISS
10. Embeddings
11. Repository tests
12. End-to-end RAG

## 7. Performance Goals & Evaluation

Mandatory evaluation metrics:

- Retrieval: Recall@k, MRR, nDCG
- Legal grounding: citation precision, citation recall, groundedness / faithfulness
- Behaviour: abstention rate
- System: latency, index build time, Apple Silicon memory usage

Performance rule: optimise only validated stages; recommend changes expected to
yield ≥10% measurable benefit. Quantization baseline: 4-bit group-size 64, with
embedding/projection layers at 6–8 bit.

Calibrated retrieval params (scripts/calibrate.py, real stack over 29 circulars /
20,349 chunks, golden_v3, supersession demotion on): **top_k = 3**,
**abstain_threshold ≈ 0.4** (cross-encoder). Recall@10 = 1.0, abstention = 1.0;
citation precision 0.96 / recall 1.0 at top_k=3 (0.97/1.0 at top_k=2; 0.76 at
top_k=5). Index persisted at data/index/ (reload 0.34s). Re-run after corpus growth.

## 8. Design Decisions

- **D1 Hybrid retrieval is mandatory.** FAISS (dense) + BM25 (sparse) + RRF form
  Stage-1. FAISS is retained as the dense engine, not replaced.
  *Amended 2026-07-02 (ADR-001):* LanceDB is the sanctioned benchmark candidate
  for the dense store at ≥100k-chunk scale; replacement only on ≥10% evidence.
- **D2 bge-m3 is the baseline embedding model only** — subject to benchmarking
  against a Qwen-family embedder and one lightweight Apple Silicon model. Do not
  change the baseline without benchmark evidence.
  *Amended 2026-07-02 (ADR-001):* Qwen3-Embedding-0.6B (embedder) and
  Qwen3-Reranker-0.6B/4B via MLX (reranker) are the sanctioned benchmark
  candidates; D6 canonical-runtime rules apply.
- **D3 Sparse path = BM25.** bge-m3 supplies dense only for the baseline; its
  sparse/ColBERT vectors are deferred to avoid fusion double-counting.
- **D4 Reranking is a mandatory production stage**, not an implementation detail.
- **D5 Citation-grounded evaluation + abstention policy are architectural
  components**, not optional add-ons.
- **D7 Embeddings + reranking run on PyTorch MPS** (sentence-transformers /
  FlagEmbedding) as the baseline. This keeps bge-m3's dense+sparse+ColBERT heads on
  their sanctioned runtime (D2) and avoids hand-porting to MLX. MLX-native embedders
  remain D2 benchmark candidates only. PyTorch MPS stability to be re-confirmed at
  Step 10 under real reranker load. Generation stays on MLX-LM/Ollama (D6).
- **D6 One canonical benchmark runtime** (MLX-LM or Ollama), with pinned model
  version, quantization, runtime params, and seeds. Alternative runtimes allowed
  for experimentation but must be tagged and never mixed into official benchmarks
  without documentation.

## 9. Engineering Constraints

- Deterministic, reproducible, token-minimal responses.
- Apple Silicon first: prefer MLX / MLX-LM / Metal where appropriate.
- Treat SEBI publications as primary legal authority; never fabricate citations or
  legal interpretations.
- Validate one step at a time; any FAIL is a blocker — stop until resolved and
  `docs/status.md` updated.
- Review only supplied files; never infer contents of unseen files.

## 10. Directory Structure (target)

```
SEBI circular RAG/
├── docs/
│   ├── project_context.md      # this file (authoritative architecture)
│   └── status.md               # completed work, pending, blockers
├── data/
│   ├── raw/                    # fetched circulars + provenance
│   └── processed/              # chunks + metadata
├── data/index/                # persisted index (dense.faiss + bm25/ + chunks.jsonl)
│                               # built by scripts/build_index.py, loaded by api.py
├── src/
│   ├── ingest/                 # fetch + provenance
│   ├── segment/                # hierarchical chunking + metadata
│   ├── retrieve/               # dense, sparse, RRF fusion
│   ├── rerank/                 # cross-encoder
│   ├── generate/               # LLM + abstention gate
│   ├── lineage.py              # P2 cross-document supersession
│   ├── ingest_pdf.py           # PDF -> corpus
│   ├── api.py                  # FastAPI /health, /ready, /query (auth, rate, timeout)
│   ├── settings.py             # config.toml + env overrides
│   └── eval/                   # metrics harness + eval_harness.py
├── config.toml                 # service config (env-overridable)
├── Makefile / run.sh           # operations (test, reindex, serve, scrape)
├── deploy/com.sebi-rag.plist   # launchd user agent
├── eval/
│   └── golden/                 # labelled SEBI query→answer+citation set (PENDING)
└── SEBI_RAG_Claude_Desktop_Engineering_Handbook.md
```

## 11. Reproducibility Requirements

- Pin all dependency versions at their validation step.
- Pin model version, quantization, runtime parameters, and random seeds for the
  canonical benchmark runtime.
- Version every index; record per-document provenance (source URL, fetch date,
  checksum); deterministic rebuild path.
- Benchmark results must always identify the runtime used.
- Runtime env guards (set before torch/FlagEmbedding init; pinned in
  tests/conftest.py): `TOKENIZERS_PARALLELISM=false`, `OMP_NUM_THREADS=1`,
  `PYTORCH_ENABLE_MPS_FALLBACK=1`. Required to run bge-m3 (FlagEmbedding) and the
  cross-encoder together on MPS without a segfault.

## 12. Known Architectural Prerequisites (tracked in status.md)

- **P1** — Labelled SEBI evaluation set (query → answer + citation). Gates metric
  computation and calibration of RRF constant, candidate-pool size, rerank top-k,
  and abstention threshold.
- **P2** — Metadata lineage extraction (supersession / amendment / version),
  which requires cross-document linking, not single-document parsing.
