# Graph Report - SEBI circular RAG  (2026-07-10)

## Corpus Check
- 106 files · ~63,384 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1068 nodes · 1854 edges · 80 communities (65 shown, 15 thin omitted)
- Extraction: 79% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 275 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b3734737`
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
- main
- README.md
- Status — SEBI Circular RAG
- Published Datasets
- 5. Running the service
- SEBI Circular RAG — Hugging Face Spaces demo
- 4. The data pipeline
- Next Steps — Structured Plans
- bench_rerankers.py
- Path
- test_benchmark.py

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 64 edges
2. `RAGPipeline` - 30 edges
3. `HashEmbedder` - 22 edges
4. `answer_with_abstention()` - 21 edges
5. `SubjectSimJudge` - 20 edges
6. `build_lineage()` - 20 edges
7. `ExtractiveStubGenerator` - 17 edges
8. `hierarchical_chunk()` - 17 edges
9. `HybridRetriever` - 16 edges
10. `build_default_pipeline()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `test_run_metadata_has_reproducibility_fields()` --calls--> `run_metadata()`  [INFERRED]
  tests/test_benchmark.py → src/sebi_rag/benchmark.py
- `main()` --calls--> `ingest()`  [INFERRED]
  scripts/acquire_missing_pdfs.py → src/sebi_rag/ingest_pdf.py
- `evaluate()` --calls--> `_doc()`  [INFERRED]
  scripts/bench_rerankers.py → src/sebi_rag/eval_harness.py
- `evaluate()` --calls--> `_unique()`  [INFERRED]
  scripts/bench_rerankers.py → src/sebi_rag/eval_harness.py
- `main()` --calls--> `load_golden()`  [INFERRED]
  scripts/bench_rerankers.py → src/sebi_rag/eval_harness.py

## Import Cycles
- None detected.

## Communities (80 total, 15 thin omitted)

### Community 0 - "Evaluation & Benchmarking"
Cohesion: 0.10
Nodes (17): Chunk, SpacesSettings, ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Raises on an (+9 more)

### Community 1 - "Embeddings & Grounding"
Cohesion: 0.09
Nodes (23): Embedder, ndarray, _tokens(), DenseIndex, _doc_checksum(), HybridRetriever, ndarray, Path (+15 more)

### Community 2 - "Indexing & Performance"
Cohesion: 0.26
Nodes (12): CircularMeta, Settings, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path).  Loads the pu (+4 more)

### Community 3 - "API & Data Ingestion"
Cohesion: 0.06
Nodes (52): FastAPI, smoke_pipeline(), create_app(), load_circulars(), Path, HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, mrr() (+44 more)

### Community 4 - "Safety Gates & Abstention"
Cohesion: 0.10
Nodes (15): _grounded_prompt(), _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), True iff the reply names a valid excerpt number. 'none' or anything     unparsea, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the     gat (+7 more)

### Community 5 - "Architecture & Design"
Cohesion: 0.14
Nodes (15): ADR-001 Architecture Review Findings, Chunk Enrichment, Corpus Ingestion, Corpus Metadata, Corpus Validation, Dataset Export Pipeline, Hierarchical Chunking, Ingest Hardening (+7 more)

### Community 6 - "Reranker Evaluation"
Cohesion: 0.22
Nodes (21): Any, beir_corpus_rows(), beir_query_rows(), build_golden_v6(), dir_fingerprint(), enrich_golden_item(), export_beir(), git_commit() (+13 more)

### Community 7 - "Configuration & Deployment"
Cohesion: 0.11
Nodes (19): Apple Silicon, Citation Generation, config.toml, Faithfulness Check, FastAPI Service, Gradio UI, HuggingFace Hub, launchd Agent (+11 more)

### Community 8 - "Judgement Models"
Cohesion: 0.20
Nodes (10): BEIR Export Format, Corpus Refresh Workflow, Eval Canary Workflow, golden_v5 Evaluation Set, Golden v6 Benchmark, Health Monitor Workflow, n8n Automation, Ops HTTP Server (+2 more)

### Community 9 - "Qwen3 Reranking"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 10 - "pipeline.py"
Cohesion: 0.47
Nodes (5): build_ui(), get_pipeline(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., run_query_spaces()

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
Cohesion: 0.09
Nodes (27): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+19 more)

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

### Community 46 - "generate.py"
Cohesion: 0.10
Nodes (20): Protocol, Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build the dense+sparse index once and persist it (run after corpus changes)., ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T (+12 more)

### Community 47 - "ADR-001: June-2026 Architecture Review — Findings F1–F5 and D1/D2 Amendments"
Cohesion: 0.15
Nodes (12): Action Items, ADR-001: June-2026 Architecture Review — Findings F1–F5 and D1/D2 Amendments, Amendments to Design Decisions, Consequences, Context, F1 — Contextual chunk enrichment (retrieval quality, HIGH impact), F2 — MLX-native reranker benchmark candidate (quality + Apple Silicon), F3 — Incremental indexing before corpus growth (scalability, CRITICAL) (+4 more)

### Community 48 - "Design"
Cohesion: 0.17
Nodes (11): Alignment assessment of the current system, Background: what SEBI changed (verified live, 2026-07-09), Component 1: `extract_pdf_urls(html: str, base_url: str) -> list[str]`, Component 2: recovery of the 14 missing PDFs (`scripts/acquire_missing_pdfs.py` v2), Component 3: hardening & compliance, Design, Error handling, Out of scope (+3 more)

### Community 49 - "answer_with_abstention"
Cohesion: 0.17
Nodes (16): answer_with_abstention(), faithfulness(), ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Check that every circular id the answer cites (in square brackets) was     actua, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge, _chunk() (+8 more)

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
Cohesion: 0.17
Nodes (16): main(), evaluate(), Calibrate top_k and the abstention threshold against the citation-precision sign, run_retrieval_benchmark(), _doc(), EvalReport, load_golden(), Path (+8 more)

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
Cohesion: 0.33
Nodes (5): 00:14-01:09 | main, 01:34 | main, 15:48 | main, 23:25-23:46 | main, 23:48 | main

### Community 61 - "today-2026-07-08.done.md"
Cohesion: 0.40
Nodes (4): 01:22 | main, 17:30 | main, 17:47-20:44 | main, 23:26 | main

### Community 62 - "api_spaces.py"
Cohesion: 0.50
Nodes (4): RAGPipeline, build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t

### Community 63 - "faithfulness"
Cohesion: 0.05
Nodes (56): BaseModel, Path, main(), Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Emit one JSON line listing SEBI circulars newer than previously seen. Uses a sta, contexts_for(), build_default_pipeline(), _citation_meta() (+48 more)

### Community 69 - "main"
Cohesion: 0.24
Nodes (10): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation.  Outputs:, write_card() (+2 more)

### Community 71 - "Status — SEBI Circular RAG"
Cohesion: 0.29
Nodes (7): Completed, Current Snapshot, Current Validation Step, Known Blockers, Last Updated, Pending, Status — SEBI Circular RAG

### Community 72 - "Published Datasets"
Cohesion: 0.29
Nodes (7): Citation, Dataset Configurations, Disclaimers, Licensing & Compliance, Published Datasets, Schema Details, Suggested Use Cases

### Community 73 - "5. Running the service"
Cohesion: 0.33
Nodes (6): 5. Running the service, Endpoints, Errors, Example, Query request, Query response

### Community 74 - "SEBI Circular RAG — Hugging Face Spaces demo"
Cohesion: 0.29
Nodes (5): Data, licensing and citation, Deploying, How this demo differs from the full local system, SEBI Circular RAG — Hugging Face Spaces demo, UI modes

### Community 75 - "4. The data pipeline"
Cohesion: 0.40
Nodes (5): 4.1 Scrape circulars (runs on your machine), 4.2 Ingest a single PDF, 4.3 Resolve supersession + rebuild the index, 4.4 Maintenance helpers, 4. The data pipeline

### Community 76 - "Next Steps — Structured Plans"
Cohesion: 0.33
Nodes (4): (a) Quality bump — larger MLX model  — DONE (2026-07-01), (b) Packaging / deployment  — DONE (2026-07-01), (c) Grow the corpus via the scraper  — IMPLEMENTED (2026-07-01), Next Steps — Structured Plans

### Community 77 - "bench_rerankers.py"
Cohesion: 0.38
Nodes (6): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t

### Community 79 - "test_benchmark.py"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

## Knowledge Gaps
- **223 isolated node(s):** `How this demo differs from the full local system`, `UI modes`, `Deploying`, `Data, licensing and citation`, `Current State` (+218 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Safety Gates & Abstention` to `Embeddings & Grounding`, `API & Data Ingestion`, `main`, `Reranker Evaluation`, `Qwen3 Reranking`, `generate.py`, `test_benchmark.py`, `answer_with_abstention`, `Injection Testing`, `RAGPipeline`, `faithfulness`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `Embeddings & Grounding`, `API & Data Ingestion`, `Safety Gates & Abstention`, `main`, `Reranker Evaluation`, `generate.py`, `faithfulness`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `HashEmbedder` connect `API & Data Ingestion` to `Embeddings & Grounding`, `generate.py`, `answer_with_abstention`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `Answer`) actually correct?**
  _`Chunk` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_offline_pipeline()`) actually correct?**
  _`HashEmbedder` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `answer_with_abstention()` (e.g. with `.score()` and `.section_score()`) actually correct?**
  _`answer_with_abstention()` has 12 INFERRED edges - model-reasoned connections that need verification._