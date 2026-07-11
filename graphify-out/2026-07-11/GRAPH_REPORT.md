# Graph Report - SEBI circular RAG  (2026-07-11)

## Corpus Check
- 109 files · ~64,664 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1087 nodes · 1946 edges · 76 communities (59 shown, 17 thin omitted)
- Extraction: 79% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 299 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a5e139b7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Evaluation & Benchmarking
- Embeddings & Grounding
- Indexing & Performance
- API & Data Ingestion
- Safety Gates & Abstention
- Architecture & Design
- Reranker Evaluation
- Configuration & Deployment
- Judgement Models
- Qwen3 Reranking
- pipeline.py
- Operations Server
- Dataset Export
- Retrieval Enhancement
- Hybrid Search Infrastructure
- Settings Management
- Cross-encoder Ranking
- Environment Setup
- Health Monitoring
- Corpus Refresh
- Injection Testing
- Confidence & Advisory
- Encoding Operations
- PDF Ingestion
- scrape_sebi.py
- Safety & Generation
- Discovery Scripts
- UI Dashboard
- Health Checks
- SEBI Circular RAG
- Operational Scripts
- Data Sourcing
- Notifications
- Data Renumbering
- Test Setup
- Model Strategy
- Project Root
- Runtime Environment
- test_export_datasets.py
- SEBI Circular RAG — Usage Guide
- Global Constraints
- SEBI Public Datasets — Extraction & Publication Design
- test_scrape_sebi.py
- Dataset Extraction Implementation — Model Allocation Plan
- test_export_integration.py
- Project Context — SEBI Circular RAG
- generate.py
- ADR-001: June-2026 Architecture Review — Findings F1–F5 and D1/D2 Amendments
- Design
- answer_with_abstention
- validate
- n8n Automation Plan — SEBI Circular RAG
- Claude Desktop Engineering Handbook (v2)
- Benchmark Evaluation Handoff — 2026-07-09
- SEBI Circular Scraping & Ingestion Plan
- RAGPipeline
- Global Constraints
- ADR-002: Certainty Signals, Abstention Reasons, and Advisory Mode
- SEBI Scraper
- today-2026-07-09.done.md
- today-2026-07-10.md
- today-2026-07-08.done.md
- api_spaces.py
- faithfulness
- archive.md
- recent.md
- .load
- app.py
- SEBI Circular RAG — Hugging Face Spaces demo
- today-2026-07-10.done.md
- 5. Running the service
- 4. The data pipeline
- _paragraphs
- today-2026-07-11.md

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 76 edges
2. `RAGPipeline` - 32 edges
3. `build_lineage()` - 23 edges
4. `HashEmbedder` - 22 edges
5. `SubjectSimJudge` - 22 edges
6. `answer_with_abstention()` - 21 edges
7. `hierarchical_chunk()` - 19 edges
8. `ExtractiveStubGenerator` - 18 edges
9. `HybridRetriever` - 17 edges
10. `SpacesSettings` - 17 edges

## Surprising Connections (you probably didn't know these)
- `contexts_for()` --calls--> `demote_superseded()`  [INFERRED]
  scripts/eval_gate.py → src/sebi_rag/lineage.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py
- `test_chunks_config_refuses_header_and_maps_fields()` --indirect_call--> `Chunk`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/segment.py
- `get_pipeline()` --calls--> `build_spaces_pipeline()`  [INFERRED]
  app.py → src/sebi_rag/api_spaces.py
- `get_pipeline()` --calls--> `ExtractiveStubGenerator`  [INFERRED]
  app.py → src/sebi_rag/generate.py

## Import Cycles
- None detected.

## Communities (76 total, 17 thin omitted)

### Community 0 - "Evaluation & Benchmarking"
Cohesion: 0.08
Nodes (28): build_ui(), get_pipeline(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., run_query_spaces(), ExternalSpaceGenerator, HFGenerator, HybridGenerator (+20 more)

### Community 1 - "Embeddings & Grounding"
Cohesion: 0.06
Nodes (32): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Build the dense+sparse index once and persist it (run after corpus changes)., contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Embedder, ndarray, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T (+24 more)

### Community 2 - "Indexing & Performance"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 3 - "API & Data Ingestion"
Cohesion: 0.06
Nodes (47): FastAPI, smoke_pipeline(), Calibrate top_k and the abstention threshold against the citation-precision sign, create_app(), load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., HashEmbedder (+39 more)

### Community 4 - "Safety Gates & Abstention"
Cohesion: 0.26
Nodes (11): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+3 more)

### Community 5 - "Architecture & Design"
Cohesion: 0.14
Nodes (15): ADR-001 Architecture Review Findings, Chunk Enrichment, Corpus Ingestion, Corpus Metadata, Corpus Validation, Dataset Export Pipeline, Hierarchical Chunking, Ingest Hardening (+7 more)

### Community 6 - "Reranker Evaluation"
Cohesion: 0.06
Nodes (61): Any, Protocol, auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t (+53 more)

### Community 7 - "Configuration & Deployment"
Cohesion: 0.11
Nodes (19): Apple Silicon, Citation Generation, config.toml, Faithfulness Check, FastAPI Service, Gradio UI, HuggingFace Hub, launchd Agent (+11 more)

### Community 8 - "Judgement Models"
Cohesion: 0.20
Nodes (10): BEIR Export Format, Corpus Refresh Workflow, Eval Canary Workflow, golden_v5 Evaluation Set, Golden v6 Benchmark, Health Monitor Workflow, n8n Automation, Ops HTTP Server (+2 more)

### Community 9 - "Qwen3 Reranking"
Cohesion: 0.24
Nodes (6): (a) Quality bump — larger MLX model  — DONE (2026-07-01), (b) Packaging / deployment  — DONE (2026-07-01), (c) Grow the corpus via the scraper  — IMPLEMENTED (2026-07-01), Next Steps — Structured Plans, Rules, Validation Roadmap — SEBI Circular RAG

### Community 10 - "pipeline.py"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 11 - "Operations Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 12 - "Dataset Export"
Cohesion: 0.20
Nodes (10): AIKosh Submission, CC-BY-4.0 License, Chunks Config, Citation-Normalization Dataset, Export Pipeline, Hugging Face Dataset, Kaggle Dataset, Lineage Config (+2 more)

### Community 13 - "Retrieval Enhancement"
Cohesion: 0.25
Nodes (8): BGE-M3 Embedding Model, BM25 Sparse Index, FAISS Dense Index, Incremental Encode, Incremental Indexing, PyTorch MPS, Retrieval Quality Ceiling, Validation Roadmap

### Community 14 - "Hybrid Search Infrastructure"
Cohesion: 0.17
Nodes (13): BM25, Cross-encoder Reranking, Ground Truth Answer Generation, Hybrid Retrieval, Lineage Graph, Per-Chunk Cross-References, Query Endpoint, Qwen3-Reranker (+5 more)

### Community 15 - "Settings Management"
Cohesion: 0.22
Nodes (7): Current Handoffs, Environment, graphify, Graphify (Optional), Project, Quick Start, Source Structure (`src/sebi_rag/`)

### Community 16 - "Cross-encoder Ranking"
Cohesion: 0.40
Nodes (5): Abstention Gate, Advisory Mode, Confidence Bands, Subject-Similarity Threshold, SubjectSimJudge

### Community 17 - "Environment Setup"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 18 - "Health Monitoring"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 19 - "Corpus Refresh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 20 - "Injection Testing"
Cohesion: 0.06
Nodes (49): Pattern, Re-derive circular number + dates from each record's stored text and rewrite the, _existing_numbers(), extract_text(), _header(), ingest(), injection_scan(), _iso_date() (+41 more)

### Community 21 - "Confidence & Advisory"
Cohesion: 0.25
Nodes (7): Current Handoffs, Environment, graphify, Graphify (Optional), Project, Quick Start, Source Structure (`src/sebi_rag/`)

### Community 22 - "Encoding Operations"
Cohesion: 0.33
Nodes (6): BGE-M3 Embedder, Citation Precision, Contextual Chunk Enrichment, FAISS, Index Building, LanceDB

### Community 23 - "PDF Ingestion"
Cohesion: 0.09
Nodes (48): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+40 more)

### Community 24 - "scrape_sebi.py"
Cohesion: 0.23
Nodes (15): discover(), extract_pdf_urls(), fetch(), _listing_url(), looks_like_pdf(), main(), _page(), _parse_date() (+7 more)

### Community 25 - "Safety & Generation"
Cohesion: 0.50
Nodes (4): Faithfulness Metric, Groundedness Gate, MLX Generator, Qwen 3B Model

### Community 29 - "SEBI Circular RAG"
Cohesion: 0.17
Nodes (12): Completed, Current State, Hugging Face Spaces Demo, In Progress / Remaining, Longer-Term Direction, Notes, Quick Start, Recommended Usage (+4 more)

### Community 33 - "Data Renumbering"
Cohesion: 0.07
Nodes (27): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+19 more)

### Community 38 - "test_export_datasets.py"
Cohesion: 0.12
Nodes (22): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+14 more)

### Community 39 - "SEBI Circular RAG — Usage Guide"
Cohesion: 0.17
Nodes (12): 10. Extending, 11. Troubleshooting, 12. Testing, 13. Legal & safety notes, 1. Concepts at a glance, 2. Requirements & setup, 3. Directory structure, 6. Configuration (+4 more)

### Community 40 - "Global Constraints"
Cohesion: 0.09
Nodes (21): B.1 Why this module is load-bearing, B.2 The format inconsistency problem, B.3 Fix history (what recent commits changed and why), B.4 Residual risks (each maps to a task below), Background (comparison findings), Execution Status & Model Delegation, Explicitly out of scope (decided during planning), Global Constraints (+13 more)

### Community 41 - "SEBI Public Datasets — Extraction & Publication Design"
Cohesion: 0.11
Nodes (17): Config 1: `corpus` (flagship), Config 2: `chunks`, Config 3: `lineage`, Config 4: `eval` / benchmark configs, Config 5: `citation-normalization` (transformed task), Config 6: `supersession-pairs` (transformed task), Dataset Design — repo `sebi-circulars` (multi-config), Deferred (documented, not built): `embeddings` (+9 more)

### Community 42 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 43 - "Dataset Extraction Implementation — Model Allocation Plan"
Cohesion: 0.12
Nodes (16): Dataset Extraction Implementation — Model Allocation Plan, Execution Sequence, For Fable 5 (Task 1): ✅ DONE 2026-07-09 (commit c9878d1, branch `dataset-export`), For Haiku 4.5 (Tasks 4 & 5): ✅ DONE 2026-07-09 (commit ed1f13f, branch `dataset-export`), For Sonnet 5 (Tasks 2 & 3): ✅ DONE 2026-07-09 (commits 2cfc921, 77b9dff, branch `dataset-export`), Handoff Notes for Each Model, Outcome, Quality Checkpoints (+8 more)

### Community 44 - "test_export_integration.py"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 45 - "Project Context — SEBI Circular RAG"
Cohesion: 0.14
Nodes (13): 10. Directory Structure (target), 11. Reproducibility Requirements, 12. Known Architectural Prerequisites (tracked in status.md), 1. Purpose, 2. Hardware, 3. Operating System, 4. Target Architecture, 5. Dependency Versions (+5 more)

### Community 47 - "ADR-001: June-2026 Architecture Review — Findings F1–F5 and D1/D2 Amendments"
Cohesion: 0.15
Nodes (12): Action Items, ADR-001: June-2026 Architecture Review — Findings F1–F5 and D1/D2 Amendments, Amendments to Design Decisions, Consequences, Context, F1 — Contextual chunk enrichment (retrieval quality, HIGH impact), F2 — MLX-native reranker benchmark candidate (quality + Apple Silicon), F3 — Incremental indexing before corpus growth (scalability, CRITICAL) (+4 more)

### Community 48 - "Design"
Cohesion: 0.17
Nodes (11): Alignment assessment of the current system, Background: what SEBI changed (verified live, 2026-07-09), Component 1: `extract_pdf_urls(html: str, base_url: str) -> list[str]`, Component 2: recovery of the 14 missing PDFs (`scripts/acquire_missing_pdfs.py` v2), Component 3: hardening & compliance, Design, Error handling, Out of scope (+3 more)

### Community 49 - "answer_with_abstention"
Cohesion: 0.07
Nodes (45): Answer, answer_with_abstention(), ExtractiveStubGenerator, faithfulness(), _grounded_prompt(), Judge, _judge_prompt(), _judge_prompt_identify() (+37 more)

### Community 50 - "validate"
Cohesion: 0.35
Nodes (10): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), _rec(), test_clean_corpus_has_no_violations(), test_flags_bad_issue_date(), test_flags_empty_and_malformed_numbers() (+2 more)

### Community 51 - "n8n Automation Plan — SEBI Circular RAG"
Cohesion: 0.18
Nodes (10): 1. What is automated (and why it suits n8n), 2. Architecture, 3. Repo pieces added (already created & tested), 4. Prerequisites, 5. Setup steps (n8n UI), 6. Alert thresholds (Code nodes) — updated 2026-07-02 for golden_v5 + gate, 7. Security & safety, 8. Operational notes & troubleshooting (+2 more)

### Community 52 - "Claude Desktop Engineering Handbook (v2)"
Cohesion: 0.18
Nodes (10): Blockers, Claude Desktop Engineering Handbook (v2), Code Review, Core Principles, Debugging, Performance, Persistent Context, Purpose (+2 more)

### Community 53 - "Benchmark Evaluation Handoff — 2026-07-09"
Cohesion: 0.20
Nodes (9): Artifact Layout, Benchmark Evaluation Handoff — 2026-07-09, Current State, Design Decisions To Preserve, Files Changed In This Slice, Important Commands, Purpose, Recommended Next Tasks (+1 more)

### Community 54 - "SEBI Circular Scraping & Ingestion Plan"
Cohesion: 0.22
Nodes (8): 1. Legality & compliance, 2. Execution model (important), 3. Pipeline, 4. Scope (configurable CLI args), 5. Commands, 6. Risks & mitigations, 7. Verification after each batch, SEBI Circular Scraping & Ingestion Plan

### Community 55 - "RAGPipeline"
Cohesion: 0.29
Nodes (7): Completed, Current Snapshot, Current Validation Step, Known Blockers, Last Updated, Pending, Status — SEBI Circular RAG

### Community 56 - "Global Constraints"
Cohesion: 0.25
Nodes (7): Global Constraints, SEBI Semantic-Routing Alignment Implementation Plan, Task 1: `extract_pdf_urls()` — viewer-aware PDF URL extraction, Task 2: PDF magic-byte guard + docstring legality note, Task 3: recovery helpers — month windows and stem resolution, Task 4: recovery `main()` — download, verify, ingest, robots check, Task 5: live verification, corpus recovery run, docs, merge

### Community 57 - "ADR-002: Certainty Signals, Abstention Reasons, and Advisory Mode"
Cohesion: 0.29
Nodes (6): Action Items, ADR-002: Certainty Signals, Abstention Reasons, and Advisory Mode, Amendment (2026-07-02): two-tier subject/section gate, Consequences, Context, Decision

### Community 58 - "SEBI Scraper"
Cohesion: 0.29
Nodes (7): Missing PDF Recovery, Month-Window Derivation, POST Pagination, PDF Magic-Byte Guard, SEBI Scraper, SEBI Semantic Routing Migration, Viewer-Aware PDF Extraction

### Community 59 - "today-2026-07-09.done.md"
Cohesion: 0.29
Nodes (6): 01:24 | main, 13:53 | main, 14:26 | main, 18:45 | main, 23:19 | dataset-export, 23:54 | acquire-missing-pdfs

### Community 60 - "today-2026-07-10.md"
Cohesion: 0.29
Nodes (7): Citation, Dataset Configurations, Disclaimers, Licensing & Compliance, Published Datasets, Schema Details, Suggested Use Cases

### Community 61 - "today-2026-07-08.done.md"
Cohesion: 0.40
Nodes (4): 01:22 | main, 17:30 | main, 17:47-20:44 | main, 23:26 | main

### Community 62 - "api_spaces.py"
Cohesion: 0.35
Nodes (8): Path, Settings.load() plus the [spaces] table as settings.spaces.*          Load order, _clear(), Settings: defaults, config.toml, and env-override precedence., test_defaults_when_no_file(), test_env_overrides(), test_load_spaces_defaults_and_file(), test_toml_then_env_precedence()

### Community 63 - "faithfulness"
Cohesion: 0.06
Nodes (56): BaseModel, main(), Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, build_default_pipeline(), _citation_meta(), CitationMeta, QueryRequest, QueryResponse (+48 more)

### Community 70 - "SEBI Circular RAG — Hugging Face Spaces demo"
Cohesion: 0.29
Nodes (6): Data, licensing and citation, Deploying, How this demo differs from the full local system, SEBI Circular RAG — Hugging Face Spaces demo, UI modes, ZeroGPU-hardware workaround

### Community 71 - "today-2026-07-10.done.md"
Cohesion: 0.29
Nodes (6): 00:14-01:09 | main, 01:34 | main, 15:48 | main, 21:22 | spaces, 23:25-23:46 | main, 23:48 | main

### Community 72 - "5. Running the service"
Cohesion: 0.33
Nodes (6): 5. Running the service, Endpoints, Errors, Example, Query request, Query response

### Community 73 - "4. The data pipeline"
Cohesion: 0.40
Nodes (5): 4.1 Scrape circulars (runs on your machine), 4.2 Ingest a single PDF, 4.3 Resolve supersession + rebuild the index, 4.4 Maintenance helpers, 4. The data pipeline

## Knowledge Gaps
- **226 isolated node(s):** `sebi-rag`, `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS` (+221 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `answer_with_abstention` to `Evaluation & Benchmarking`, `Embeddings & Grounding`, `API & Data Ingestion`, `Reranker Evaluation`, `pipeline.py`, `Injection Testing`, `faithfulness`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `Reranker Evaluation` to `Embeddings & Grounding`, `API & Data Ingestion`, `answer_with_abstention`, `faithfulness`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `normalize_circular_number()` connect `Injection Testing` to `validate`, `Reranker Evaluation`, `PDF Ingestion`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `Answer`) actually correct?**
  _`Chunk` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `build_lineage()` (e.g. with `main()` and `main()`) actually correct?**
  _`build_lineage()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_offline_pipeline()`) actually correct?**
  _`HashEmbedder` has 18 INFERRED edges - model-reasoned connections that need verification._