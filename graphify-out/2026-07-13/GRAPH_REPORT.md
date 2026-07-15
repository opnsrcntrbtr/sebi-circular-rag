# Graph Report - SEBI circular RAG  (2026-07-13)

## Corpus Check
- 87 files · ~37,726 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 936 nodes · 1956 edges · 52 communities (40 shown, 12 thin omitted)
- Extraction: 75% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 379 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `199ff2e9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Evaluation & Benchmarking
- Embeddings & Grounding
- Indexing & Performance
- embeddings.py
- test_export_integration.py
- Architecture & Design
- Reranker Evaluation
- Configuration & Deployment
- Judgement Models
- RAGPipeline
- api_spaces.py
- Operations Server
- Dataset Export
- Retrieval Enhancement
- Hybrid Search Infrastructure
- RAGPipeline
- Cross-encoder Ranking
- Environment Setup
- Health Monitoring
- Corpus Refresh
- Injection Testing
- api_spaces.py
- Encoding Operations
- PDF Ingestion
- scrape_sebi.py
- Safety & Generation
- Discovery Scripts
- UI Dashboard
- Health Checks
- test_api.py
- Operational Scripts
- Data Sourcing
- Notifications
- Data Renumbering
- Test Setup
- Model Strategy
- test_eval_asof.py
- Runtime Environment
- test_export_datasets.py
- .grounded
- Qwen3MLXReranker
- hierarchical_chunk
- test_scrape_sebi.py
- .load
- validate
- .retrieve
- SEBI Scraper
- api_spaces.py
- .load
- app.py
- HybridRetriever
- deploy_space.py

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 76 edges
2. `RAGPipeline` - 36 edges
3. `Lineage` - 31 edges
4. `HashEmbedder` - 29 edges
5. `build_lineage()` - 28 edges
6. `hierarchical_chunk()` - 28 edges
7. `ExtractiveStubGenerator` - 24 edges
8. `CircularMeta` - 23 edges
9. `SubjectSimJudge` - 22 edges
10. `answer_with_abstention()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `test_real_corpus_loads_with_provenance_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_eval_harness.py → src/sebi_rag/corpus.py
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_governing_on_cycle_safe()` --calls--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_governing_on_parallel_branches_max_date_wins()` --calls--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_build_lineage_edges_tiered()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py

## Import Cycles
- None detected.

## Communities (52 total, 12 thin omitted)

### Community 0 - "Evaluation & Benchmarking"
Cohesion: 0.06
Nodes (44): build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row() (+36 more)

### Community 1 - "Embeddings & Grounding"
Cohesion: 0.08
Nodes (26): Embedder, ndarray, _tokens(), DenseIndex, _doc_checksum(), HybridRetriever, ndarray, Path (+18 more)

### Community 2 - "Indexing & Performance"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 3 - "embeddings.py"
Cohesion: 0.11
Nodes (18): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, faithfulness(), Generation with a hard abstention gate (D5).  If the top reranked score is below, Check that every circular id the answer cites (in square brackets) was     actua (+10 more)

### Community 4 - "test_export_integration.py"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 5 - "Architecture & Design"
Cohesion: 0.14
Nodes (15): ADR-001 Architecture Review Findings, Chunk Enrichment, Corpus Ingestion, Corpus Metadata, Corpus Validation, Dataset Export Pipeline, Hierarchical Chunking, Ingest Hardening (+7 more)

### Community 6 - "Reranker Evaluation"
Cohesion: 0.06
Nodes (55): Any, auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t, main() (+47 more)

### Community 7 - "Configuration & Deployment"
Cohesion: 0.11
Nodes (19): Apple Silicon, Citation Generation, config.toml, Faithfulness Check, FastAPI Service, Gradio UI, HuggingFace Hub, launchd Agent (+11 more)

### Community 8 - "Judgement Models"
Cohesion: 0.20
Nodes (10): BEIR Export Format, Corpus Refresh Workflow, Eval Canary Workflow, golden_v5 Evaluation Set, Golden v6 Benchmark, Health Monitor Workflow, n8n Automation, Ops HTTP Server (+2 more)

### Community 9 - "RAGPipeline"
Cohesion: 0.05
Nodes (40): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Build the dense+sparse index once and persist it (run after corpus changes)., contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, annotate_corpus(), _currency(), demote_superseded(), detect_relations() (+32 more)

### Community 10 - "api_spaces.py"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

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

### Community 15 - "RAGPipeline"
Cohesion: 0.18
Nodes (8): Protocol, Generator, _grounded_prompt(), Judge, F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, Reranker, Chunk

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

### Community 21 - "api_spaces.py"
Cohesion: 0.17
Nodes (9): qwen3_rerank_prompt(), Qwen3MLXReranker, Stage-2 reranking (mandatory, D4). Cross-encoder in production; a deterministic, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card() (+1 more)

### Community 22 - "Encoding Operations"
Cohesion: 0.33
Nodes (6): BGE-M3 Embedder, Citation Precision, Contextual Chunk Enrichment, FAISS, Index Building, LanceDB

### Community 23 - "PDF Ingestion"
Cohesion: 0.09
Nodes (48): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+40 more)

### Community 24 - "scrape_sebi.py"
Cohesion: 0.08
Nodes (28): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+20 more)

### Community 25 - "Safety & Generation"
Cohesion: 0.50
Nodes (4): Faithfulness Metric, Groundedness Gate, MLX Generator, Qwen 3B Model

### Community 29 - "test_api.py"
Cohesion: 0.15
Nodes (11): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), True iff the reply names a valid excerpt number. 'none' or anything     unparsea, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the     gat, Deterministic groundedness judge on MLX (greedy decode, temp 0).      Pass share (+3 more)

### Community 33 - "Data Renumbering"
Cohesion: 0.07
Nodes (27): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+19 more)

### Community 36 - "test_eval_asof.py"
Cohesion: 0.33
Nodes (6): load_golden_asof(), Path, _lin_chain(), P4b: as-of golden evaluation runner tests (offline)., test_load_golden_asof_has_both_modes(), test_run_selector_cases_pass_and_fail()

### Community 38 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 39 - ".grounded"
Cohesion: 0.19
Nodes (14): Answer, answer_with_abstention(), ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge, _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid (+6 more)

### Community 40 - "Qwen3MLXReranker"
Cohesion: 0.28
Nodes (10): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge() (+2 more)

### Community 41 - "hierarchical_chunk"
Cohesion: 0.33
Nodes (6): _body(), Chunker (segment.hierarchical_chunk) behaviour.  Regression guard for the "5. Nu, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_bare_parent_heading_folds_into_first_subsection(), test_bare_parent_heading_not_emitted_as_standalone_chunk(), test_leaf_single_line_provision_is_preserved_not_overmerged()

### Community 42 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 44 - ".load"
Cohesion: 0.31
Nodes (7): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces()

### Community 50 - "validate"
Cohesion: 0.35
Nodes (10): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), _rec(), test_clean_corpus_has_no_violations(), test_flags_bad_issue_date(), test_flags_empty_and_malformed_numbers() (+2 more)

### Community 58 - "SEBI Scraper"
Cohesion: 0.29
Nodes (7): Missing PDF Recovery, Month-Window Derivation, POST Pagination, PDF Magic-Byte Guard, SEBI Scraper, SEBI Semantic Routing Migration, Viewer-Aware PDF Extraction

### Community 62 - "api_spaces.py"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 69 - "app.py"
Cohesion: 0.47
Nodes (5): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), test_retrieval_metrics()

### Community 74 - "HybridRetriever"
Cohesion: 0.06
Nodes (76): BaseModel, FastAPI, main(), main(), smoke_pipeline(), build_default_pipeline(), _citation_meta(), CitationMeta (+68 more)

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `RAGPipeline` to `Evaluation & Benchmarking`, `Embeddings & Grounding`, `embeddings.py`, `Reranker Evaluation`, `.grounded`, `Qwen3MLXReranker`, `RAGPipeline`, `HybridRetriever`, `Injection Testing`, `api_spaces.py`, `test_api.py`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `HybridRetriever` to `Evaluation & Benchmarking`, `Embeddings & Grounding`, `embeddings.py`, `Reranker Evaluation`, `.grounded`, `RAGPipeline`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `Lineage` connect `HybridRetriever` to `Evaluation & Benchmarking`, `RAGPipeline`, `embeddings.py`, `test_eval_asof.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `Answer`) actually correct?**
  _`Chunk` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Lineage` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`Lineage` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_offline_pipeline()`) actually correct?**
  _`HashEmbedder` has 25 INFERRED edges - model-reasoned connections that need verification._