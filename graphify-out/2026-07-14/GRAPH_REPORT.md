# Graph Report - SEBI circular RAG  (2026-07-14)

## Corpus Check
- 93 files · ~45,579 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1000 nodes · 2067 edges · 63 communities (49 shown, 14 thin omitted)
- Extraction: 75% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 403 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `21065c04`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Evaluation & Benchmarking
- Embeddings & Grounding
- Indexing & Performance
- RAGPipeline
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
- embeddings.py
- Encoding Operations
- PDF Ingestion
- scrape_sebi.py
- Safety & Generation
- Discovery Scripts
- UI Dashboard
- Health Checks
- generate.py
- Operational Scripts
- Data Sourcing
- Notifications
- Data Renumbering
- Test Setup
- Model Strategy
- Chunk
- Runtime Environment
- test_export_datasets.py
- segment.py
- Qwen3MLXReranker
- hierarchical_chunk
- test_scrape_sebi.py
- test_acquire_missing.py
- test_ingest_refs.py
- pipeline.py
- test_ingest_pdf.py
- test_injection.py
- test_gate.py
- test_eval_asof.py
- validate
- .retrieve
- test_pipeline.py
- test_gate.py
- test_eval_harness.py
- hierarchical_chunk
- main
- Path
- SEBI Scraper
- api_spaces.py
- .load
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
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
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

## Communities (63 total, 14 thin omitted)

### Community 0 - "Evaluation & Benchmarking"
Cohesion: 0.07
Nodes (42): _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path).  Loads the pu, One HF dataset config as plain dicts (network; cached by `datasets`)., Full-circular records (dicts) for build_lineage() — always the     "corpus" conf (+34 more)

### Community 1 - "Embeddings & Grounding"
Cohesion: 0.16
Nodes (11): Embedder, DenseIndex, _doc_checksum(), HybridRetriever, ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding, Deterministic per-document checksum over its (enriched) chunk texts —     captur (+3 more)

### Community 2 - "Indexing & Performance"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 3 - "RAGPipeline"
Cohesion: 0.18
Nodes (10): FastAPI, create_app(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, _slow_pipeline(), _SlowGenerator, test_auth_required_when_key_set(), test_citation_meta_reports_superseded(), test_query_exceeds_time_budget_returns_504() (+2 more)

### Community 4 - "test_export_integration.py"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 5 - "Architecture & Design"
Cohesion: 0.14
Nodes (15): ADR-001 Architecture Review Findings, Chunk Enrichment, Corpus Ingestion, Corpus Metadata, Corpus Validation, Dataset Export Pipeline, Hierarchical Chunking, Ingest Hardening (+7 more)

### Community 6 - "Reranker Evaluation"
Cohesion: 0.07
Nodes (51): Any, auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t, main() (+43 more)

### Community 7 - "Configuration & Deployment"
Cohesion: 0.11
Nodes (19): Apple Silicon, Citation Generation, config.toml, Faithfulness Check, FastAPI Service, Gradio UI, HuggingFace Hub, launchd Agent (+11 more)

### Community 8 - "Judgement Models"
Cohesion: 0.20
Nodes (10): BEIR Export Format, Corpus Refresh Workflow, Eval Canary Workflow, golden_v5 Evaluation Set, Golden v6 Benchmark, Health Monitor Workflow, n8n Automation, Ops HTTP Server (+2 more)

### Community 9 - "RAGPipeline"
Cohesion: 0.12
Nodes (24): build_lineage(), _currency(), detect_relations(), detect_relations_ex(), mc_topic(), Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None.      Us, Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference. (+16 more)

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
Cohesion: 0.22
Nodes (11): answer_with_abstention(), Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful() (+3 more)

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
Cohesion: 0.05
Nodes (57): Pattern, Re-derive circular number + dates from each record's stored text and rewrite the, _existing_numbers(), extract_text(), _header(), ingest(), injection_scan(), _iso_date() (+49 more)

### Community 21 - "embeddings.py"
Cohesion: 0.09
Nodes (21): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Calibrate top_k and the abstention threshold against the citation-precision sign, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env (+13 more)

### Community 22 - "Encoding Operations"
Cohesion: 0.33
Nodes (6): BGE-M3 Embedder, Citation Precision, Contextual Chunk Enrichment, FAISS, Index Building, LanceDB

### Community 23 - "PDF Ingestion"
Cohesion: 0.08
Nodes (50): Path, build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata() (+42 more)

### Community 24 - "scrape_sebi.py"
Cohesion: 0.08
Nodes (28): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+20 more)

### Community 25 - "Safety & Generation"
Cohesion: 0.50
Nodes (4): Faithfulness Metric, Groundedness Gate, MLX Generator, Qwen 3B Model

### Community 29 - "generate.py"
Cohesion: 0.22
Nodes (12): AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, run_pipeline_cases(), run_selector_cases(), summarize(), _lin_chain() (+4 more)

### Community 33 - "Data Renumbering"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 36 - "Chunk"
Cohesion: 0.15
Nodes (22): BaseModel, build_default_pipeline(), _citation_meta(), CitationMeta, QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline.  Run (real stack; loads the, build_spaces_pipeline() (+14 more)

### Community 38 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 39 - "segment.py"
Cohesion: 0.15
Nodes (9): Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, Segmentation: hierarchical chunking + metadata + stable citation IDs.  Minimal,, Faithfulness: catch answers that cite circulars not in the retrieved context., test_faithfulness_scoring(), _ollama_up(), Step 12 — end-to-end RAG integration test with the REAL stack.  bge-m3 (MPS) + b, _chunks(), Index persistence round-trip (offline). (+1 more)

### Community 40 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 41 - "hierarchical_chunk"
Cohesion: 0.15
Nodes (22): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:, diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13).  Pure functions only: l (+14 more)

### Community 42 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 43 - "test_acquire_missing.py"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan, _master(), test_annotate_idempotent() (+7 more)

### Community 44 - "test_ingest_refs.py"
Cohesion: 0.24
Nodes (7): Protocol, Generator, _grounded_prompt(), Judge, F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, Reranker, Chunk

### Community 45 - "pipeline.py"
Cohesion: 0.31
Nodes (7): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces()

### Community 46 - "test_ingest_pdf.py"
Cohesion: 0.39
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are e, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 48 - "test_gate.py"
Cohesion: 0.14
Nodes (14): faithfulness(), _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), Generation with a hard abstention gate (D5).  If the top reranked score is below, True iff the reply names a valid excerpt number. 'none' or anything     unparsea (+6 more)

### Community 49 - "test_eval_asof.py"
Cohesion: 0.14
Nodes (12): annotate_corpus(), Lineage, Path, Update each corpus record's supersession_status + superseded_by + supersedes, Connected component over supersedes/superseded_by (both tiers)., The circular in this family that governs on date as_of (ISO), or         None wh, test_annotate_corpus_adds_master_fields_and_consolidates_edges(), test_annotate_corpus_writes_new_metadata_fields() (+4 more)

### Community 50 - "validate"
Cohesion: 0.29
Nodes (13): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations() (+5 more)

### Community 52 - "test_pipeline.py"
Cohesion: 0.26
Nodes (11): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), _build_chunks(), _build_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline.  Runs fully offline (HashEmbed, test_abstention_on_out_of_domain_query() (+3 more)

### Community 53 - "test_gate.py"
Cohesion: 0.28
Nodes (10): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge() (+2 more)

### Community 54 - "test_eval_harness.py"
Cohesion: 0.24
Nodes (8): Build the dense+sparse index once and persist it (run after corpus changes)., load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., _pipeline(), P1 evaluation-harness test (offline).  Loads the real seed corpus (data/corpus/c, test_eval_harness_metric_suite(), test_real_corpus_loads_with_provenance_fields()

### Community 55 - "hierarchical_chunk"
Cohesion: 0.24
Nodes (10): hierarchical_chunk(), _paragraphs(), Split into units each <= max_chars.      PDF-extracted text often lacks blank-li, Document -> section -> paragraph chunks with stable IDs.      A "section" is det, _body(), Chunker (segment.hierarchical_chunk) behaviour.  Regression guard for the "5. Nu, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_bare_parent_heading_folds_into_first_subsection() (+2 more)

### Community 56 - "main"
Cohesion: 0.50
Nodes (5): main(), main(), load_golden(), Path, load_records()

### Community 58 - "SEBI Scraper"
Cohesion: 0.29
Nodes (7): Missing PDF Recovery, Month-Window Derivation, POST Pagination, PDF Magic-Byte Guard, SEBI Scraper, SEBI Semantic Routing Migration, Viewer-Aware PDF Extraction

### Community 62 - "api_spaces.py"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 74 - "HybridRetriever"
Cohesion: 0.17
Nodes (23): smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., LexicalReranker, Deterministic query-coverage reranker (test/fallback).      Score = fraction of, CircularMeta (+15 more)

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `test_ingest_refs.py` to `Evaluation & Benchmarking`, `Embeddings & Grounding`, `Chunk`, `Reranker Evaluation`, `segment.py`, `Qwen3MLXReranker`, `HybridRetriever`, `RAGPipeline`, `test_gate.py`, `Injection Testing`, `embeddings.py`, `test_eval_harness.py`, `hierarchical_chunk`, `test_gate.py`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `Chunk` to `Embeddings & Grounding`, `RAGPipeline`, `Reranker Evaluation`, `HybridRetriever`, `test_ingest_refs.py`, `test_eval_asof.py`, `embeddings.py`, `main`, `generate.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `Lineage` connect `test_eval_asof.py` to `Chunk`, `RAGPipeline`, `HybridRetriever`, `embeddings.py`, `generate.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `Answer`) actually correct?**
  _`Chunk` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Lineage` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`Lineage` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_offline_pipeline()`) actually correct?**
  _`HashEmbedder` has 25 INFERRED edges - model-reasoned connections that need verification._