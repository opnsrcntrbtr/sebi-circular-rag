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
- uv — 0.11.28
- Git — 2.55.0 (Homebrew; Apple Git 2.50.1 also present)
- MLX 0.32.0 / MLX-LM 0.31.3 (validated in `.venv`)
- Ollama — 0.19+ (MLX backend on Apple Silicon) *(pin @ validation)*
- PyTorch (MPS) — 2.13.0 (**required**: baseline runtime for bge-m3 embeddings +
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
- Lexical index — bm25s 0.3.9 *(select @ retrieval stage)*

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
│   ├── status.md               # completed work, pending, blockers
│   ├── next_steps.md           # active roadmap
│   ├── validation_roadmap.md   # handbook validation sequence
│   ├── scraping_plan.md        # SEBI scraping strategy
│   ├── n8n_automation_plan.md  # ops automation plan
│   ├── adr-001-*.md            # architecture decision records
│   ├── adr-002-*.md
│   ├── adr-003-*.md
│   ├── graphify-analysis/      # cross-module analysis reports
│   └── superpowers/            # plans, reports, specs (interventions)
├── data/
│   ├── raw/                    # fetched PDFs + .sha256 checksums (705 records)
│   ├── corpus/                 # circulars.jsonl (processed corpus)
│   ├── manifests/              # build manifests
│   └── index/                  # persisted index
│       ├── dense.faiss         # FAISS dense store
│       ├── bm25/               # BM25 sparse index
│       ├── chunks.jsonl        # enriched chunks (22k+ chunks)
│       ├── lineage.json        # supersession graph (1,200+ edges)
│       ├── embeddings.npy      # cached embeddings (incremental indexing)
│       ├── manifest.json       # doc-level sha256 manifest
│       ├── meta.json           # corpus metadata
│       └── splade.npz          # SPLADE sidecar (eval-only, off by default)
├── src/
│   └── sebi_rag/               # flat module (no subpackages)
│       ├── api.py              # FastAPI /health, /ready, /query (auth, rate, timeout)
│       ├── api_spaces.py       # CPU HF Space variant (do not edit for local pipeline)
│       ├── pipeline.py         # RAGPipeline orchestration; regulatory_basis_status
│       ├── retrieve.py         # HybridRetriever — FAISS + BM25 RRF fusion
│       ├── splade.py           # SPLADE retrieval (opt-in, eval-only)
│       ├── splade_encoder.py   # SPLADE encoder
│       ├── context_headers.py  # Context header generation (opt-in)
│       ├── hyde.py             # HyDE retrieval (opt-in)
│       ├── rerank.py           # Cross-encoder reranker (bge-reranker-v2-m3 / Qwen3)
│       ├── embeddings.py       # bge-m3 embeddings (Dense + Sparse + ColBERT)
│       ├── segment.py          # Hierarchical chunking (~1200 chars, ~150 overlap)
│       ├── lineage.py          # P2: cross-document supersession / amendment / version
│       ├── master_meta.py      # Master circular metadata enrichment
│       ├── metadata.py         # CircularMeta / Chunk dataclasses
│       ├── generate.py         # Local LLM generation + abstention gate (MLX/Ollama)
│       ├── generate_spaces.py  # CPU HF Space variant
│       ├── corpus.py           # Corpus management (load, save, annotate)
│       ├── corpus_spaces.py    # CPU HF Space variant
│       ├── eval.py             # Metrics (Recall@k, MRR, nDCG, citation precision/recall)
│       ├── eval_asof.py        # As-of-date golden evaluation
│       ├── eval_harness.py     # Evaluation harness + metrics computation
│       ├── benchmark.py        # Retrieval benchmark + BEIR/TREC export
│       ├── settings.py         # config.toml + env overrides
│       ├── device.py           # Device detection (MPS / CPU)
│       ├── stats.py            # Corpus / index statistics
│       ├── expand.py           # Query expansion utilities
│       ├── reg_citations.py    # Regulation citations from circular text
│       ├── reg_lineage.py      # Circular→regulation edges + regulatory_basis_status
│       ├── regulations.py      # Regulation identity, alias table, name resolution
│       ├── verify_master.py    # Master circular verification
│       ├── ui.py               # Gradio UI
├── scripts/                    # CLI scripts (build, scrape, eval, ops)
│       ├── build_index.py      # Index builder (full + incremental)
│       ├── calibrate.py        # Retrieval calibration (RRF, top-k, threshold)
│       ├── scrape_sebi.py      # SEBI scraper (master-circulars + regular)
│       ├── scrape_regulations.py  # SEBI regulations scraper
│       ├── build_golden.py     # Golden set builder
│       ├── build_golden_v6.py  # Golden v6 builder
│       ├── build_reg_edges.py  # Circular→regulation edge builder
│       ├── build_splade_index.py  # SPLADE index builder
│       ├── eval_json.py        # Eval result scoring
│       ├── eval_gate.py        # Groundedness / subject-sim judge evaluation
│       ├── eval_asof.py        # As-of-date eval runner
│       ├── bench_generators.py # Generator benchmark (faithfulness/groundedness)
│       ├── bench_rerankers.py  # Reranker benchmark (AUROC, cluster separation)
│       ├── bench_retrieval.py  # Retrieval benchmark + TREC runfile
│       ├── export_benchmark.py # BEIR/TREC/RAG benchmark export
│       ├── export_datasets.py  # Dataset export (chunks, corpus, lineage)
│       ├── golden_v7/          # Full golden-v7 adjudication pipeline
│       │       ├── agreement.py
│       │       ├── build_pool.py
│       │       ├── derive_thresholds.py
│       │       ├── gate_select.py
│       │       ├── local_adjudicate.py
│       │       ├── gemini_adjudicate.py
│       │       └── ...
│       ├── validate_corpus.py  # Corpus integrity validator
│       ├── repair_corpus_text.py  # Corpus text repair
│       ├── renumber.py         # Circular number re-derivation
│       ├── audit_reg_edges.py  # Regulation edge audit
│       ├── rescore_runs.py     # Eval run rescoring
│       ├── ops_server.py       # n8n ops server
│       ├── deploy_space.py     # HF Space deployment
│       └── ...
├── tests/                      # 50+ test files (offline + integration)
│       ├── conftest.py         # Fixtures, env guards, mock models
│       ├── test_*.py           # Unit + integration tests
├── eval/
│   ├── golden/                 # Labelled SEBI query→answer+citation sets
│   │       ├── golden_v1.jsonl … golden_v7.jsonl  # Evolving golden sets
│   │       ├── gate_v7.json  # v7 gate floors (recall, citation_recall, abstention)
│   │       └── v7_annotations/  # Human adjudication annotations
│   ├── probes/                 # Probe queries (probes_v1.jsonl)
│   └── runs/                   # Eval run results (baseline, asof, fp16, SPLADE, …)
├── reports/                    # Intervention reports (golden_v7 agreement, master coverage, …)
├── graphify-out/               # Generated knowledge graph (graph.json, GRAPH_REPORT.md)
├── logs/                       # Automation logs (canary, discover, refresh)
├── automation/                 # n8n workflow exports
├── dist/                       # Dataset exports (AIKO, Zenodo)
├── deploy/
│       ├── com.sebi-rag.plist        # Main launchd user agent
│       └── com.sebi-rag-ops.plist    # Ops server launchd agent
├── app.py                      # Root-level HF Space entry point (CPU-only)
├── run.sh                      # Local service launcher
├── run_ops.sh                  # Ops server launcher
├── Makefile                    # Operations (test, reindex, serve, scrape, calibrate, …)
├── config.toml                 # Service config (env-overridable)
├── pyproject.toml              # Project metadata + dependencies
├── uv.lock                     # Pinned dependency lockfile
├── requirements-spaces.txt     # HF Space dependencies (separate from local)
├── README.md                   # Project readme
├── README-spaces.md            # HF Space runbook
├── AGENTS.md                   # Non-Claude agent guidance
└── CLAUDE.md                   # Claude agent guidance
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

- **P1** — Labelled SEBI evaluation set: **COMPLETED** (`golden_v7`, n=260,
  `adjudicated_n`=103, gate armed). Calibrated: `top_k`=3, `score_floor`=0.05,
  SubjectSimJudge two-tier gate.
- **P2** — Metadata lineage extraction: **COMPLETED** (`lineage.py`, 1,222 edges,
  74 superseded-in-corpus, answer-layer warnings wired).
