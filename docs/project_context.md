# Project Context — SEBI Circular RAG

> Authoritative architecture record. Consult before requesting any information.
> Governed by `SEBI_RAG_Claude_Desktop_Engineering_Handbook.md`. Last updated: 2026-07-27 (Target Architecture + Design Decisions updated).

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
   fetch date, checksum). `ingest_pdf.py`: PDF text extraction (with OCR fallback
   for scanned PDFs), metadata parsing (circular number, dates, subject,
   department, version_lineage), F4 injection scanning (OWASP LLM01 — flags
   instruction-like content in extracted text for review, never silently drops).
2. **Segmentation (mandatory)** — hierarchical chunking: document → section →
   paragraph, packed to ≈1200 chars with ≈150-char overlap. PDF-aware: when
   extracted text lacks blank-line breaks, falls back to single-newline, then
   sentence, then hard-window splitting (no mid-clause splits where a break
   exists). Each chunk carries a stable retrieval ID for precise citation.
   Wrapped-clause folding: absorbs hard-wrapped continuation lines after headings.
   Intervention #1: prepends governing clause for numbered sub-clauses.
   F1: contextual enrichment — prepends document identity (circular number +
   subject) to every chunk for disambiguation. `CircularMeta` fields:
   circular_number, issue_date, effective_date, subject, issuing_department,
   supersession_status (in_force|superseded|amended), amendment_history,
   version_lineage, circular_type, validity_status (current|superseded|partially_superseded|unknown), superseded_by_id.
3. **Metadata extraction (mandatory)** — per document/chunk: circular number,
   issue date, effective date, subject, issuing department, supersession status,
   amendment history, version lineage. Cross-document supersession is resolved by
   `lineage.py` (P2): references are classified supersedes/amends/cites from the
   circular text, AND master-circular re-issues are detected by normalised title
   (newest version supersedes older), producing a lineage graph and an
   in_force|superseded|amended status; superseded chunks are demoted in rerank and
   flagged at retrieval time. Regulation-level annotation: `reg_lineage.py`
   builds Circular→regulation edges; `regulations.py` resolves regulation identity
   and alias table. `CitationMeta.regulations` and `regulatory_basis_status`
   (current|repealed_basis|mixed|unknown) surfaced per-citation in the API; in-text
   advisory note appended when a cited circular rests on a repealed regulation.
4. **Indexing** — Dense: FAISS (IndexFlatIP, in-memory) over bge-m3 baseline
   embeddings. Sparse: BM25 lexical index (bm25s). Indexes are versioned via
   `manifest.json` with per-document checksums (supports incremental indexing —
   F3: encode only new/changed documents, reuse cached embedding rows for
   unchanged ones).
5. **Stage-1 retrieval (mandatory hybrid)** — dense (FAISS) + sparse (BM25) run
   sequentially, fused by Reciprocal Rank Fusion (RRF) into a candidate pool of
   ~50–100. Optional SPLADE learned-sparse third leg (eval-only, off by default).
   Optional HyDE hypothetical-passage third dense leg (intervention #5, off by
   default). Query expansion (statutory-synonym expansion) applied to sparse leg
   only — BM25 misses lay vocabulary; dense keeps the raw query.
6. **Stage-2 reranking (mandatory)** — production: cross-encoder reranker
   (bge-reranker-v2-m3 via sentence-transformers CrossEncoder on MPS). Benchmark
   candidate: Qwen3-Reranker via MLX (causal-LM, P("yes") vs P("no")). Test
   fallback: deterministic LexicalReranker (query-coverage score). → top-k context.
7. **Generation** — local LLM. Default MLX-LM Qwen2.5-1.5B-Instruct-4bit
   (Apple-Silicon native). Ollama optional via SEBI_RAG_GENERATOR (deterministic:
   temperature 0, fixed seed). Abstention gate: if reranker confidence is below
   the configured threshold (calibrated ≈ 0.4), return the abstention answer
   ("I don't know based on the available evidence."); never generate unsupported
   legal conclusions. ADR-002 certainty architecture: SubjectSimJudge (two-tier
   groundedness — max cosine(query, subject line) with threshold 0.42, plus
   section-heading tier at 0.60); MLXJudge (deterministic groundedness judge on
   MLX, modes: identify/provisions). Confidence bands: high (subject_sim ≥ 0.65
   + faithfulness 1.0), medium (passed all gates), low (abstained). Advisory mode:
   `advisory=True` returns a clearly-labelled low-confidence draft answer on gate
   failure (never authoritative). `as_of` date-scoped queries: score against law as
   of a date (circular demoted only if superseding circular was issued by that
   date). Faithfulness check: every cited circular id in square brackets must
   appear in retrieved context; unsupported citations flagged.
8. **Evaluation (mandatory component)** — see §7.

```
                ┌─ Dense ANN  (FAISS IndexFlatIP, bge-m3 baseline) ─┐
Query ──────────┤                                               ├─ RRF ─ pool(50–100) ─ cross-encoder (bge-reranker-v2-m3) ─ top-k ─ LLM ─ answer + citations
                └─ Sparse lexical (bm25s) ────────────────────────┘                              │
                                                                                   ┌─ Judge (SubjectSim/MLX) ─ abstain if not grounded
                                                                                   │
                                                                                   └─ Faithfulness check (citation ids in context)
                                                                                                   │
                                                                                   ┌─ Abstain if below threshold (≈ 0.4)
                                                                                   │
                                                                                   └─ Advisory mode: low-confidence draft on gate failure (advisory=True)
                                                                                                   │
                                                                                   ┌─ as_of: date-scoped (demote only if superseded by as_of date)
                                                                                   │
                                                                                   └─ Optional SPLADE / HyDE third legs (eval-only, off by default)
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

Canonical source: `docs/project_context.md` §6. Mirrored in `CLAUDE.md` and
`AGENTS.md` for agent self-containment. One step at a time; never validate a
later stage until the current one passes. Any FAIL is a blocker — stop,
record root cause + exact commands + verification command in `docs/status.md`,
resolve before proceeding.

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

### 7.1 Mandatory Evaluation Metrics

| Category | Metric | Where Measured |
|----------|--------|----------------|
| **Retrieval** | Recall@k, MRR, nDCG@k | `src/sebi_rag/eval.py` (recall_at_k, mrr, ndcg_at_k); `eval_harness.py` (chunk-level recall@k, chunk MRR) |
| **Citation** | Citation precision, citation recall | `eval_harness.py`, `golden_v7/score.py` |
| **Groundedness** | Faithfulness (every bracketed citation id in answer appears in retrieved context), groundedness proxy (answer_contains hit rate on answered items) | `eval_harness.py` |
| **Behaviour** | Abstention accuracy, must_not_cite violation rate | `eval_harness.py`, `golden_v7/score.py` |
| **System** | Latency (ms per query), index build time, Apple Silicon memory usage | `eval_harness.py` (avg_latency_s), `benchmark.py` (run metadata) |
| **Safety** | Injection flag count (8 pattern classes at ingest) | `eval_json.py` (live corpus scan) |
| **Certainty** | Confidence bands (high | medium | low), abstention_reason enum (no_context | score_floor | subject_gate) | `generate.py` (SubjectSimJudge), `pipeline.py` |

### 7.2 Performance Rule

Optimise only validated stages; recommend changes expected to yield ≥10%
measurable benefit. Quantization baseline: 4-bit group-size 64, with
embedding/projection layers at 6–8 bit.

### 7.3 Calibrated Retrieval Parameters

Real stack calibration over 705 circulars / 77,841 chunks (golden_v7):

- **top_k = 3** (default, configurable via `SEBI_RAG_TOP_K`)
- **score_floor = 0.05** (cross-encoder; configurable via `SEBI_RAG_ABSTAIN_THRESHOLD`)
- **SubjectSimJudge threshold = 0.42** (two-tier: subject_sim ≥ 0.42 OR section_sim ≥ 0.60)
- **Section threshold = 0.60** (configurable via `SEBI_RAG_SECT_THRESHOLD`)
- Index persisted at `data/index/` (reload 0.34s). Re-run after corpus growth.

### 7.4 Golden-Set Architecture

- **Reporting set**: `eval/golden/golden_v7.jsonl` (n=260, `adjudicated_n`=103).
  Strata: title_direct 40, body_paraphrase 60, numeric_table 30,
  lineage_supersession 40, multi_hop 20, repealed_basis 20, hard_negative 40,
  far_negative 10. 53 abstain rows, 15 dated `as_of` rows.
- **Frozen fallback**: `golden_v5.jsonl` (n=56) — used when v7 gate is not armed.
- **Golden v6**: `golden_v6.jsonl` (n=56) — intermediate set.
- **Gate**: `eval/golden/gate_v7.json` — armed at `adjudicated_n = 103`.
  Floors (2.5th-percentile lower bound minus 0.005 cushion):
  recall_at_k = 0.9126, citation_recall = 0.3126, abstention_accuracy = 0.83.
  CI gates on v7 only when `adjudicated_n >= 100`.
- **Adjudication pipeline** (`scripts/golden_v7/`): seed, mine_strata, build_pool,
  gate_select, local_adjudicate (Qwen3.6-35B-MLX), gemini_adjudicate (on hold),
  agreement, relabel_repooled, backfill_escalations, derive_thresholds, score.

### 7.5 Evaluation Infrastructure

| Script | Purpose |
|--------|---------|
| `scripts/eval_json.py` | Production-mirrored eval via `RAGPipeline` (stub generator — no LLM); golden-set resolution (v7 gate → v5 fallback); prints JSON for n8n |
| `scripts/eval_harness.py` | `run_eval()` → `EvalReport` (recall, MRR, nDCG, citation prec/rec, abstention acc, groundedness proxy, faithfulness, latency, chunk-level metrics) |
| `scripts/golden_v7/score.py` | Per-row scoring shared by `eval_json.py` and `derive_thresholds.py`; `vectors()` aggregates to metric vectors |
| `scripts/bench_retrieval.py` | Retrieval-only benchmark + TREC runfile export |
| `scripts/bench_rerankers.py` | Reranker benchmark (AUROC, cluster separation) |
| `scripts/bench_generators.py` | Generator benchmark (faithfulness, groundedness, latency) |
| `scripts/eval_gate.py` | Groundedness / subject-sim judge evaluation |
| `scripts/eval_asof.py` | As-of-date golden evaluation |
| `scripts/rescore_runs.py` | Re-score archived runs with bootstrap CIs + paired significance |
| `scripts/export_benchmark.py` | BEIR/TREC/RAG benchmark export |
| `scripts/export_datasets.py` | Dataset export (chunks, corpus, lineage, eval) |
| `scripts/calibrate.py` | Retrieval calibration sweep (RRF, top-k, threshold) |

### 7.6 Current Baseline Numbers (golden_v7, adjudicated subset, n=103)

- recall_at_k: **0.9126** (gate floor)
- citation_recall: **0.3126** (gate floor)
- abstention_accuracy: **0.83** (gate floor)
- Full-set numbers on v5 (n=56, for reference): recall@10 0.956, citation_precision 0.711,
  citation_recall 0.889, abstention_accuracy 0.839.

### 7.7 Index Performance

- Full seed build: ~507s (22,273 chunks at 207 circulars).
- Incremental reindex: ~5s (no-op, all docs reused).
- Index reload: 0.34s.
- Disk: `embeddings.npy` ≈ 91 MB (22k chunks); scales to ~2 GB at 500k chunks.

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
- **D8 Certainty architecture (ADR-002).** Every response carries a confidence
  block (`{rerank_top, margin, subject_sim, section_sim}`) and a banded
  `certainty` (high | medium | low), never a probability. **High** = passed
  both gates ∧ subject_sim ≥ 0.65 ∧ faithfulness 1.0 (100% citation recall on
  golden_v5). **Medium** = passed gates otherwise. **Low** = any gate failed
  (always on abstention). `abstention_reason` enum: `no_context | score_floor |
  subject_gate` — distinguishes client error, far-domain, and near-domain
  ungrounded. Advisory mode (`advisory=True`): on `score_floor`/`subject_gate`
  with non-empty context, response additionally carries `draft_answer` prefixed
  "LOW CONFIDENCE — not regulatory guidance…" (never the default, never
  produced for `no_context`). `as_of` date-scoped queries: score against law as
  of a date (circular demoted only if superseding circular issued by that date).
  Two-tier groundedness gate: SubjectSimJudge (max cosine(query, subject line),
  threshold 0.42) OR section-heading tier (threshold 0.60). MLXJudge (deterministic
  groundedness judge on MLX, modes: identify/provisions) available but not
  default (scale-unstable). Faithfulness check: every cited circular id in
  square brackets must appear in retrieved context; unsupported citations flagged.
  *Amended 2026-07-02 (ADR-002):* two-tier subject/section gate adopted —
  `grounded = subject_sim ≥ 0.42 OR section_sim ≥ 0.60`.
- **D9 Apple Neural Engine (ANE) declined (ADR-003).** The pipeline stays on MLX
  (generation) and MPS/MLX (embeddings/reranker). ANE is an energy-efficiency
  engine (~93+ tok/s vs ~9 tok/s on 8B model); throughput-oriented server RAG
  on plugged-in Apple Silicon does not benefit. Revisit only if battery life,
  thermal envelope, or always-on background inference becomes an explicit goal.
- **D10 F1–F5 findings (ADR-001).** F1 — contextual chunk enrichment: prepend
  `<circular_no> | <subject> | <section>` to each chunk before embedding
  (criterion met: +23% citation precision, recall@10 held at 1.0). F2 —
  Qwen3-Reranker MLX benchmark rejected (AUROC 0.799 vs baseline 0.812;
  baseline retained). F3 — incremental indexing: checksum-keyed encode
  (`embeddings.npy` cache + per-doc manifest); delta-only encode, FAISS-Flat/
  BM25 rebuilt from cached matrix (deletion-safe vs HNSW). F4 —
  prompt-injection hardening: 8 injection-pattern classes scanned at ingest
  (OWASP LLM01); `<<<SOURCE>>>` delimiters in prompts; timing-safe API key
  compare (`secrets.compare_digest`); localhost binding. F5 — golden-set
  circularity fix: held-out paraphrase queries + hard negatives (golden_v5/v6/v7
  with human adjudication). All F1–F5 accepted and implemented.
- **D11 Wrapped-clause folding (Intervention #1).** SEBI PDFs hard-wrap clause
  text; a non-heading paragraph right after a heading is usually its continuation.
  Absorb into the recorded head unless the head is already terminated or capped.
  Additionally, numbered sub-clauses ("4.1.1.2. …") are meaningless without their
  governing clause ("4.1.1 On and from the date… the CRA shall:"). Prepend the
  nearest recorded ancestor heading to every chunk so both retrievers see the
  context.
- **D12 Query expansion via statutory-synonym glossary (Intervention #2).**
  SEBI circulars use statutory vocabulary (freeze, dematerialised, rescinded)
  where users ask in lay terms (block, electronic, replaced). Appending statutory
  synonyms to the BM25 query closes the vocabulary gap without touching the
  index; the dense leg keeps the raw query. Deterministic and additive: the
  original query is always preserved as a prefix. Entries grounded in
  `eval/runs/ft-traces/buckets.md` failure analysis.
- **D13 Optional third RRF legs (Interventions #5, iv9, iv11).** HyDE (Part B):
  hypothetical statutory passage as additive third dense leg (opt-in, off by
  default, silent failure). SPLADE: learned-sparse third RRF leg (opt-in,
  eval-only, off by default). Contextual headers: one lay+statutory sentence per
  deep sub-clause/annex chunk (opt-in, off by default, silent failure). All
  three are non-destructive — the mandatory dense + BM25 + RRF path is
  unchanged; enabling any third leg requires explicit configuration.
- **D14 Regulation-level annotation.** Regulations are consolidated living
  documents (no circular_number, no issue_date, one current row each), keyed by
  deterministic `reg_id` slug. Three-stage resolution: exact token match, then
  hand-maintained `REGULATION_ALIASES` table (acronyms like "PIT" →
  "prohibition-of-insider-trading"), then Jaccard fuzzy match (threshold 0.8).
  `regulatory_basis_status` (current|repealed_basis|mixed|unknown) derived from
  resolved regulation statuses; `CitationMeta.regulations` surfaced per-citation
  in the API. In-text advisory note appended when a cited circular rests on a
  repealed regulation.
- **D15 API surface.** FastAPI service: key-in-body auth (`X-API-Key` header,
  `secrets.compare_digest`), rate limiting (429, configurable `SEBI_RATE_PER_MIN`,
  default 60 req/min), per-query timeout (504, configurable), `/health` (chunk/
  circular counts, generator info), `/ready` (eager pipeline build), `/query`
  (full response schema with `confidence`, `certainty`, `abstention_reason`,
  `citations_meta` including `regulatory_basis_status` and `regulations`).
  `retrieval_only` mode swaps in `ExtractiveStubGenerator` for testing.

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
│   ├── scraping_plan.md        # SEBI scraping strategy
│   ├── n8n_automation_plan.md  # ops automation plan
│   ├── adr-001-*.md            # architecture decision records
│   ├── adr-002-*.md
│   ├── adr-003-*.md
│   ├── graphify-analysis/      # cross-module analysis reports
│   │       └── eval-gate-lineage-bridge.md
│   ├── assets/                 # Demo assets (demo.webp)
│   └── superpowers/            # Intervention plans, reports, specs
│           ├── plans/          # 25 intervention plan docs
│           ├── reports/        # Intervention reports
│           └── specs/          # 17 intervention spec docs
├── data/
│   ├── raw/                    # fetched PDFs + .sha256 checksums (705 records)
│   ├── corpus/                 # circulars.jsonl (processed corpus)
│   │       ├── circulars.jsonl             # Processed corpus
│   │       ├── context_headers_targeted.jsonl  # Targeted context headers
│   │       └── regulations.jsonl           # Regulation data
│   ├── manifests/              # Build manifests
│   │       ├── master_circulars.jsonl  # Master circular records
│   │       ├── master_exceptions.jsonl # Master exceptions
│   │       └── regulation_edges.jsonl  # Circular→regulation edges
│   └── index/                  # Persisted index
│       ├── dense.faiss         # FAISS dense store
│       ├── bm25/               # BM25 sparse index
│       ├── chunks.jsonl        # Enriched chunks (22k+ chunks)
│       ├── lineage.json        # Supersession graph (1,200+ edges)
│       ├── embeddings.npy      # Cached embeddings (incremental indexing)
│       ├── manifest.json       # Doc-level sha256 manifest
│       ├── meta.json           # Corpus metadata
│       ├── splade.npz          # SPLADE sidecar (eval-only, off by default)
│       └── splade_meta.json    # SPLADE index metadata
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
│       ├── ingest_pdf.py       # PDF ingestion: text extraction, metadata parsing, injection scan, corpus write
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
│       ├── acquire_missing_pdfs.py  # PDF acquisition
│       ├── analysis/           # Analysis tools
│       │       ├── extract_misses.py
│       │       ├── renumber_audit.py
│       │       ├── sweep_pool.py
│       │       └── trace_failure.py
│       ├── canary.sh           # Canary monitoring
│       ├── discover.sh         # Discovery script
│       ├── discover_new.py     # New content discovery
│       ├── generate_context_headers.py  # Context header generation
│       ├── notify.sh           # Notification script
│       ├── push_datasets.py    # Dataset push
│       ├── refresh.sh          # Refresh script
│       ├── splade_pilot.py     # SPLADE pilot
│       ├── upload_spaces_index.py  # HF Space index upload
│       └── select_targeted_headers.py  # Targeted header selection
├── tests/                      # 50+ test files (offline + integration)
│       ├── conftest.py         # Fixtures, env guards, mock models
│       ├── fixtures/           # Test fixtures (master appendix text, HTML listings)
│       └── test_*.py           # Unit + integration tests
├── eval/
│   ├── golden/                 # Labelled SEBI query→answer+citation sets
│   │       ├── golden_v1.jsonl … golden_v7.jsonl  # Evolving golden sets
│   │       ├── gate_v7.json  # v7 gate floors (recall, citation_recall, abstention)
│   │       └── v7_annotations/  # Human adjudication (arbitration_queue, candidates, pools, votes, adjudication)
│   ├── probes/                 # Probe queries (probes_v1.jsonl)
│   └── runs/                   # Eval run results (baseline, asof, fp16, SPLADE, 28+ intervention runs)
├── reports/                    # Intervention reports (golden_v7 agreement, master coverage, reg_edge_audit, …)
├── graphify-out/               # Generated knowledge graph (graph.json, GRAPH_REPORT.md, cache, cost.json)
├── logs/                       # Automation logs (canary, discover, refresh)
├── automation/                 # n8n workflow exports
│       └── n8n/                # n8n workflow JSON exports
├── dist/                       # Dataset exports (AIKO, Zenodo)
│       ├── datasets/           # Dataset exports (chunks, corpus, lineage, eval, …)
│       └── backups/            # HF Space backups (hf-sebi-circulars-pre-push)
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
