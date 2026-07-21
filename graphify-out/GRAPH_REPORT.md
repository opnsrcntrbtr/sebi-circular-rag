# Graph Report - SEBI circular RAG  (2026-07-21)

## Corpus Check
- 108 files · ~54,397 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1117 nodes · 2368 edges · 49 communities (40 shown, 9 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 523 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5f462de4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Core RAG Pipeline
- Benchmark Infrastructure
- Data Processing
- Index & Evaluation
- Dataset Export
- Utility Scripts
- Spaces CPU Pipeline
- Dataset Card Tests
- Metadata Engine
- Export Tests
- .grounded
- Benchmark Scripts
- Qwen3MLXReranker
- test_integration_e2e.py
- As-of Evaluation
- Embedder
- Scraper Tests
- Master Metadata
- Export Integration
- answer_with_abstention
- test_gate.py
- Chunk
- Corpus Validation
- Reranking
- ZeroGPU Tests
- Dataset Push
- Answer Generation
- Ops Server
- SubjectSimJudge
- test_gate.py
- build_lineage
- main
- Build Scripts
- Canary Monitoring
- Index Refresh
- As-of UI Tests
- .grounded
- Space Deployment
- Discovery Scripts
- Index Upload
- HybridGenerator
- test_integration_e2e.py
- UI Components
- Ops Scripts
- Notification Scripts
- Test Guards
- bench_rerankers.py
- bench_retrieval.py
- app.py

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 80 edges
2. `hierarchical_chunk()` - 34 edges
3. `HashEmbedder` - 33 edges
4. `RAGPipeline` - 33 edges
5. `Lineage` - 31 edges
6. `build_lineage()` - 28 edges
7. `ExtractiveStubGenerator` - 24 edges
8. `HybridRetriever` - 23 edges
9. `CircularMeta` - 23 edges
10. `SubjectSimJudge` - 22 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_governing_on_cycle_safe()` --calls--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_governing_on_parallel_branches_max_date_wins()` --calls--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py
- `_chunk()` --calls--> `Chunk`  [INFERRED]
  tests/test_hyde.py → src/sebi_rag/segment.py

## Import Cycles
- None detected.

## Communities (49 total, 9 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.28
Nodes (10): _get(), Path, Resolve a setting: env var > config dict > default., Settings.load() plus the [spaces] table as settings.spaces.*          Load order, _clear(), Settings: defaults, config.toml, and env-override precedence., test_defaults_when_no_file(), test_env_overrides() (+2 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.07
Nodes (49): Any, Chunk, RAGPipeline, main(), main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, dataset_quality(), load_index_chunks() (+41 more)

### Community 2 - "Data Processing"
Cohesion: 0.05
Nodes (57): Pattern, Re-derive circular number + dates from each record's stored text and rewrite the, _existing_numbers(), extract_text(), _header(), ingest(), injection_scan(), _iso_date() (+49 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.18
Nodes (13): build_default_pipeline(), Embedder, DenseIndex, _doc_checksum(), HybridRetriever, ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding (+5 more)

### Community 4 - "Dataset Export"
Cohesion: 0.08
Nodes (50): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+42 more)

### Community 5 - "Utility Scripts"
Cohesion: 0.05
Nodes (50): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+42 more)

### Community 6 - "Spaces CPU Pipeline"
Cohesion: 0.09
Nodes (19): _fmt(), main(), Path, Re-score archived benchmark runs with bootstrap CIs and paired significance.  Re, score_run(), bootstrap_ci(), BootstrapCI, paired_delta() (+11 more)

### Community 7 - "Dataset Card Tests"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 8 - "Metadata Engine"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 9 - "Export Tests"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 10 - ".grounded"
Cohesion: 0.19
Nodes (16): hierarchical_chunk(), _paragraphs(), Split into units each <= max_chars.      PDF-extracted text often lacks blank-li, Document -> section -> paragraph chunks with stable IDs.      A "section" is det, _body(), Chunker (segment.hierarchical_chunk) behaviour.  Regression guard for the "5. Nu, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_absorption_respects_300_char_cap() (+8 more)

### Community 11 - "Benchmark Scripts"
Cohesion: 0.15
Nodes (12): main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10).  Pulls the i, load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., CircularMeta, Segmentation: hierarchical chunking + metadata + stable citation IDs.  Minimal,, P1 evaluation-harness test (offline).  Loads the real seed corpus (data/corpus/c (+4 more)

### Community 12 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (10): FastAPI, create_app(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, /ready should trigger pipeline build and return ready=true., test_auth_required_when_key_set(), test_citation_meta_reports_superseded(), test_query_exceeds_time_budget_returns_504(), test_rate_limit() (+2 more)

### Community 13 - "test_integration_e2e.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.07
Nodes (40): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any (+32 more)

### Community 15 - "Embedder"
Cohesion: 0.07
Nodes (28): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).  Standalo, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.  splad, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+20 more)

### Community 16 - "Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "Master Metadata"
Cohesion: 0.09
Nodes (26): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).  Resumable, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope(), load_headers(), Path (+18 more)

### Community 18 - "Export Integration"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 19 - "answer_with_abstention"
Cohesion: 0.05
Nodes (53): Protocol, answer_with_abstention(), faithfulness(), Generator, _grounded_prompt(), Judge, _judge_prompt(), _judge_prompt_identify() (+45 more)

### Community 20 - "test_gate.py"
Cohesion: 0.26
Nodes (11): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), _build_chunks(), _build_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline.  Runs fully offline (HashEmbed, test_abstention_on_out_of_domain_query() (+3 more)

### Community 21 - "Chunk"
Cohesion: 0.11
Nodes (22): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).      Nev (+14 more)

### Community 22 - "Corpus Validation"
Cohesion: 0.29
Nodes (13): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations() (+5 more)

### Community 23 - "Reranking"
Cohesion: 0.46
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are e, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 24 - "ZeroGPU Tests"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 25 - "Dataset Push"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 26 - "Answer Generation"
Cohesion: 0.16
Nodes (23): smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., LexicalReranker, Deterministic query-coverage reranker (test/fallback).      Score = fraction of, _offline_pipeline() (+15 more)

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "SubjectSimJudge"
Cohesion: 0.20
Nodes (14): BaseModel, main(), _citation_meta(), CitationMeta, QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline.  Run (real stack; loads the, MLXGenerator (+6 more)

### Community 29 - "test_gate.py"
Cohesion: 0.40
Nodes (3): _ollama_up(), pipeline(), Step 12 — end-to-end RAG integration test with the REAL stack.  bge-m3 (MPS) + b

### Community 30 - "build_lineage"
Cohesion: 0.06
Nodes (48): annotate_corpus(), build_lineage(), _currency(), detect_relations(), detect_relations_ex(), mc_topic(), Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None.      Us, Update each corpus record's supersession_status + superseded_by + supersedes (+40 more)

### Community 31 - "main"
Cohesion: 0.13
Nodes (19): AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, run_pipeline_cases(), run_selector_cases(), summarize(), Lineage (+11 more)

### Community 32 - "Build Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 33 - "Canary Monitoring"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 34 - "Index Refresh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 36 - ".grounded"
Cohesion: 0.17
Nodes (11): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage.  Offline only —, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_none_and_empty_hyde_are_identical_to_baseline() (+3 more)

### Community 40 - "HybridGenerator"
Cohesion: 0.18
Nodes (17): build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row() (+9 more)

### Community 46 - "bench_rerankers.py"
Cohesion: 0.10
Nodes (21): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic, BM25 lexical index (bm25s)., Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), SparseIndex, _chunk() (+13 more)

### Community 47 - "bench_retrieval.py"
Cohesion: 0.10
Nodes (20): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A (+12 more)

### Community 48 - "app.py"
Cohesion: 0.31
Nodes (7): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces()

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `answer_with_abstention` to `Benchmark Infrastructure`, `Data Processing`, `Index & Evaluation`, `.grounded`, `HybridGenerator`, `.grounded`, `Benchmark Scripts`, `bench_rerankers.py`, `bench_retrieval.py`, `Embedder`, `Master Metadata`, `Chunk`, `Answer Generation`, `SubjectSimJudge`, `main`?**
  _High betweenness centrality (0.153) - this node is a cross-community bridge._
- **Why does `main()` connect `Benchmark Infrastructure` to `Index & Evaluation`, `.grounded`, `HybridGenerator`, `As-of Evaluation`, `bench_retrieval.py`, `Embedder`, `Answer Generation`, `SubjectSimJudge`, `build_lineage`, `main`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `consolidation_edges()` connect `build_lineage` to `Data Processing`, `bench_retrieval.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 39 inferred relationships involving `Chunk` (e.g. with `HeaderGenerator` and `Answer`) actually correct?**
  _`Chunk` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `hierarchical_chunk()` (e.g. with `smoke_pipeline()` and `_slow_pipeline()`) actually correct?**
  _`hierarchical_chunk()` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_offline_pipeline()`) actually correct?**
  _`HashEmbedder` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 16 INFERRED edges - model-reasoned connections that need verification._