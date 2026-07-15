# Graph Report - SEBI circular RAG  (2026-07-12)

## Corpus Check
- 83 files · ~35,773 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 898 nodes · 1870 edges · 51 communities (39 shown, 12 thin omitted)
- Extraction: 76% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 345 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8bb4ebc2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Evaluation & Benchmarking
- Embeddings & Grounding
- Indexing & Performance
- lineage.py
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
- generate.py
- Cross-encoder Ranking
- Environment Setup
- Health Monitoring
- Corpus Refresh
- Injection Testing
- Chunk
- Encoding Operations
- PDF Ingestion
- scrape_sebi.py
- Safety & Generation
- Discovery Scripts
- UI Dashboard
- Health Checks
- Operational Scripts
- Data Sourcing
- Notifications
- Data Renumbering
- Test Setup
- Model Strategy
- main
- Runtime Environment
- test_export_datasets.py
- detect_relations_ex
- app.py
- app.py
- test_scrape_sebi.py
- eval.py
- validate
- SEBI Scraper
- api_spaces.py
- .load
- app.py
- corpus_spaces.py
- HybridRetriever
- deploy_space.py
- ExtractiveStubGenerator

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 76 edges
2. `RAGPipeline` - 35 edges
3. `Lineage` - 27 edges
4. `build_lineage()` - 27 edges
5. `HashEmbedder` - 24 edges
6. `SubjectSimJudge` - 22 edges
7. `answer_with_abstention()` - 21 edges
8. `hierarchical_chunk()` - 21 edges
9. `ExtractiveStubGenerator` - 20 edges
10. `CircularMeta` - 18 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_governing_on_cycle_safe()` --calls--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_governing_on_parallel_branches_max_date_wins()` --calls--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_build_lineage_edges_tiered()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_build_lineage_inferred_master_topic_edge()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py

## Import Cycles
- None detected.

## Communities (51 total, 12 thin omitted)

### Community 0 - "Evaluation & Benchmarking"
Cohesion: 0.11
Nodes (21): ExternalSpaceGenerator, HFGenerator, HybridGenerator, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).      Nev, SpacesSettings (+13 more)

### Community 2 - "Indexing & Performance"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 3 - "lineage.py"
Cohesion: 0.13
Nodes (12): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env (+4 more)

### Community 5 - "Architecture & Design"
Cohesion: 0.14
Nodes (15): ADR-001 Architecture Review Findings, Chunk Enrichment, Corpus Ingestion, Corpus Metadata, Corpus Validation, Dataset Export Pipeline, Hierarchical Chunking, Ingest Hardening (+7 more)

### Community 6 - "Reranker Evaluation"
Cohesion: 0.07
Nodes (55): Any, auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t, main() (+47 more)

### Community 7 - "Configuration & Deployment"
Cohesion: 0.11
Nodes (19): Apple Silicon, Citation Generation, config.toml, Faithfulness Check, FastAPI Service, Gradio UI, HuggingFace Hub, launchd Agent (+11 more)

### Community 8 - "Judgement Models"
Cohesion: 0.20
Nodes (10): BEIR Export Format, Corpus Refresh Workflow, Eval Canary Workflow, golden_v5 Evaluation Set, Golden v6 Benchmark, Health Monitor Workflow, n8n Automation, Ops HTTP Server (+2 more)

### Community 9 - "RAGPipeline"
Cohesion: 0.06
Nodes (56): BaseModel, main(), build_default_pipeline(), _citation_meta(), CitationMeta, QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline.  Run (real stack; loads the (+48 more)

### Community 10 - "api_spaces.py"
Cohesion: 0.11
Nodes (20): Protocol, Generator, _grounded_prompt(), Judge, _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice() (+12 more)

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

### Community 15 - "generate.py"
Cohesion: 0.35
Nodes (8): Path, Settings.load() plus the [spaces] table as settings.spaces.*          Load order, _clear(), Settings: defaults, config.toml, and env-override precedence., test_defaults_when_no_file(), test_env_overrides(), test_load_spaces_defaults_and_file(), test_toml_then_env_precedence()

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

### Community 21 - "Chunk"
Cohesion: 0.15
Nodes (10): Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., Stage-2 reranking (mandatory, D4). Cross-encoder in production; a deterministic, Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), Segmentation: hierarchical chunking + metadata + stable citation IDs.  Minimal,, P4b: as-of golden evaluation runner tests (offline)., P1 evaluation-harness test (offline).  Loads the real seed corpus (data/corpus/c, Step 12 — end-to-end RAG integration test with the REAL stack.  bge-m3 (MPS) + b (+2 more)

### Community 22 - "Encoding Operations"
Cohesion: 0.33
Nodes (6): BGE-M3 Embedder, Citation Precision, Contextual Chunk Enrichment, FAISS, Index Building, LanceDB

### Community 23 - "PDF Ingestion"
Cohesion: 0.06
Nodes (64): Path, build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata() (+56 more)

### Community 24 - "scrape_sebi.py"
Cohesion: 0.08
Nodes (28): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+20 more)

### Community 25 - "Safety & Generation"
Cohesion: 0.50
Nodes (4): Faithfulness Metric, Groundedness Gate, MLX Generator, Qwen 3B Model

### Community 33 - "Data Renumbering"
Cohesion: 0.07
Nodes (27): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+19 more)

### Community 36 - "main"
Cohesion: 0.22
Nodes (9): contexts_for(), Answer, demote_superseded(), Down-weight reranked (chunk, score) pairs from superseded circulars and     re-s, Map any cited circular that is superseded -> the circular(s) superseding it., superseded_citations(), End-to-end wiring: segment -> hybrid retrieve -> rerank -> generate/abstain., test_demote_superseded_puts_in_force_on_top() (+1 more)

### Community 38 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 39 - "detect_relations_ex"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 40 - "app.py"
Cohesion: 0.40
Nodes (4): faithfulness(), Check that every circular id the answer cites (in square brackets) was     actua, Faithfulness: catch answers that cite circulars not in the retrieved context., test_faithfulness_scoring()

### Community 41 - "app.py"
Cohesion: 0.38
Nodes (5): build_ui(), get_pipeline(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., run_query_spaces()

### Community 42 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 45 - "eval.py"
Cohesion: 0.47
Nodes (5): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), test_retrieval_metrics()

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
Cohesion: 0.08
Nodes (44): FastAPI, smoke_pipeline(), create_app(), load_circulars(), Path, HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, ExtractiveStubGenerator (+36 more)

### Community 72 - "corpus_spaces.py"
Cohesion: 0.12
Nodes (20): detect_relations(), detect_relations_ex(), Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window(), _lin_chain(), P2 lineage / supersession resolution tests., test_build_lineage_edges_tiered() (+12 more)

### Community 74 - "HybridRetriever"
Cohesion: 0.09
Nodes (18): Embedder, ndarray, _tokens(), DenseIndex, _doc_checksum(), ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding (+10 more)

### Community 88 - "ExtractiveStubGenerator"
Cohesion: 0.13
Nodes (23): answer_with_abstention(), ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge, _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested() (+15 more)

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `api_spaces.py` to `Evaluation & Benchmarking`, `lineage.py`, `main`, `app.py`, `Reranker Evaluation`, `detect_relations_ex`, `RAGPipeline`, `HybridRetriever`, `Injection Testing`, `Chunk`, `ExtractiveStubGenerator`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `main`, `app.py`, `Reranker Evaluation`, `HybridRetriever`, `api_spaces.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Why does `derive_validity()` connect `api_spaces.py` to `RAGPipeline`, `lineage.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `Answer`) actually correct?**
  _`Chunk` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `Lineage` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`Lineage` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `build_lineage()` (e.g. with `main()` and `main()`) actually correct?**
  _`build_lineage()` has 18 INFERRED edges - model-reasoned connections that need verification._