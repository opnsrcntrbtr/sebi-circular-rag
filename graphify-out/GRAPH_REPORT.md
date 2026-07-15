# Graph Report - SEBI circular RAG  (2026-07-15)

## Corpus Check
- 93 files · ~45,744 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 898 nodes · 1966 edges · 46 communities (37 shown, 9 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 410 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8adb208a`
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
- API Server
- Benchmark Scripts
- Master Circular Verification
- Lineage Tracking
- As-of Evaluation
- HF Spaces
- Scraper Tests
- Master Metadata
- Export Integration
- Generation & Judging
- Gate Tests
- embeddings.py
- Corpus Validation
- Reranking
- ZeroGPU Tests
- Dataset Push
- Answer Generation
- Ops Server
- Settings
- api_spaces.py
- Spaces UI
- .load
- Build Scripts
- Canary Monitoring
- Index Refresh
- As-of UI Tests
- app.py
- Space Deployment
- Discovery Scripts
- Index Upload
- bench_rerankers.py
- .encode
- UI Components
- Ops Scripts
- Notification Scripts
- Test Guards

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
- `test_governing_on_cycle_safe()` --calls--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_governing_on_parallel_branches_max_date_wins()` --calls--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py
- `test_chunks_config_refuses_header_and_maps_fields()` --indirect_call--> `Chunk`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/segment.py
- `get_pipeline()` --calls--> `build_spaces_pipeline()`  [INFERRED]
  app.py → src/sebi_rag/api_spaces.py

## Import Cycles
- None detected.

## Communities (46 total, 9 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.05
Nodes (55): load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), LexicalReranker (+47 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.10
Nodes (38): Any, main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation.  Outputs: (+30 more)

### Community 2 - "Data Processing"
Cohesion: 0.05
Nodes (57): Pattern, Re-derive circular number + dates from each record's stored text and rewrite the, _existing_numbers(), extract_text(), _header(), ingest(), injection_scan(), _iso_date() (+49 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.18
Nodes (13): BaseModel, FastAPI, _citation_meta(), CitationMeta, QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline.  Run (real stack; loads the, MLXGenerator (+5 more)

### Community 4 - "Dataset Export"
Cohesion: 0.08
Nodes (50): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+42 more)

### Community 5 - "Utility Scripts"
Cohesion: 0.08
Nodes (28): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+20 more)

### Community 6 - "Spaces CPU Pipeline"
Cohesion: 0.11
Nodes (22): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).      Nev (+14 more)

### Community 7 - "Dataset Card Tests"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 8 - "Metadata Engine"
Cohesion: 0.12
Nodes (8): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., TestClassifyCircularType, TestDeriveValidity

### Community 9 - "Export Tests"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 10 - "API Server"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 11 - "Benchmark Scripts"
Cohesion: 0.21
Nodes (13): AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, run_pipeline_cases(), run_selector_cases(), summarize(), _lin_chain() (+5 more)

### Community 12 - "Master Circular Verification"
Cohesion: 0.15
Nodes (22): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:, diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13).  Pure functions only: l (+14 more)

### Community 13 - "Lineage Tracking"
Cohesion: 0.08
Nodes (33): annotate_corpus(), build_lineage(), _currency(), detect_relations(), detect_relations_ex(), mc_topic(), Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None.      Us, Update each corpus record's supersession_status + superseded_by + supersedes (+25 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.16
Nodes (8): Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, End-to-end wiring: segment -> hybrid retrieve -> rerank -> generate/abstain., Stage-2 reranking (mandatory, D4). Cross-encoder in production; a deterministic, _HallucinatingGenerator, Faithfulness: catch answers that cite circulars not in the retrieved context., test_pipeline_flags_hallucinated_citation(), _ollama_up(), Step 12 — end-to-end RAG integration test with the REAL stack.  bge-m3 (MPS) + b

### Community 15 - "HF Spaces"
Cohesion: 0.17
Nodes (9): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, demote_superseded(), P2 — cross-document supersession resolution.  Classifies each circular's referen, Down-weight reranked (chunk, score) pairs from superseded circulars and     re-s, Map any cited circular that is superseded -> the circular(s) superseding it., superseded_citations() (+1 more)

### Community 16 - "Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "Master Metadata"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan, _master(), test_annotate_idempotent() (+7 more)

### Community 18 - "Export Integration"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 19 - "Generation & Judging"
Cohesion: 0.06
Nodes (50): Protocol, HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, Answer, answer_with_abstention(), ExtractiveStubGenerator, faithfulness(), Generator (+42 more)

### Community 20 - "Gate Tests"
Cohesion: 0.24
Nodes (10): evaluate(), Calibrate top_k and the abstention threshold against the citation-precision sign, run_retrieval_benchmark(), _doc(), EvalReport, Golden-set evaluation harness (P1).  Runs the pipeline over a labelled golden se, report_dict(), run_eval() (+2 more)

### Community 21 - "embeddings.py"
Cohesion: 0.23
Nodes (6): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Build the dense+sparse index once and persist it (run after corpus changes)., Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, Stage-1 hybrid retrieval: dense (FAISS) + sparse (BM25) fused by RRF.  Mandatory

### Community 22 - "Corpus Validation"
Cohesion: 0.29
Nodes (13): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations() (+5 more)

### Community 23 - "Reranking"
Cohesion: 0.15
Nodes (13): build_default_pipeline(), Embedder, DenseIndex, _doc_checksum(), HybridRetriever, ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding (+5 more)

### Community 24 - "ZeroGPU Tests"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 25 - "Dataset Push"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 26 - "Answer Generation"
Cohesion: 0.31
Nodes (5): Lineage, Path, Connected component over supersedes/superseded_by (both tiers)., The circular in this family that governs on date as_of (ISO), or         None wh, test_lineage_save_load_roundtrips_edges()

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "Settings"
Cohesion: 0.30
Nodes (11): _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path).  Loads the pu, One HF dataset config as plain dicts (network; cached by `datasets`)., Full-circular records (dicts) for build_lineage() — always the     "corpus" conf (+3 more)

### Community 29 - "api_spaces.py"
Cohesion: 0.25
Nodes (8): main(), build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t, BGEM3Embedder, Production dense embedder: BAAI/bge-m3 on Apple Silicon MPS (Step 10)., CrossEncoderReranker, Production reranker: bge-reranker-v2-m3 via sentence-transformers     CrossEncod

### Community 30 - "Spaces UI"
Cohesion: 0.17
Nodes (14): main(), smoke_pipeline(), create_app(), load_records(), RAGPipeline, _offline_pipeline(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, _slow_pipeline() (+6 more)

### Community 31 - ".load"
Cohesion: 0.35
Nodes (8): Path, Settings.load() plus the [spaces] table as settings.spaces.*          Load order, _clear(), Settings: defaults, config.toml, and env-override precedence., test_defaults_when_no_file(), test_env_overrides(), test_load_spaces_defaults_and_file(), test_toml_then_env_precedence()

### Community 32 - "Build Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 33 - "Canary Monitoring"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 34 - "Index Refresh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 36 - "app.py"
Cohesion: 0.31
Nodes (7): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces()

### Community 40 - "bench_rerankers.py"
Cohesion: 0.38
Nodes (6): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Generation & Judging` to `Core RAG Pipeline`, `Benchmark Infrastructure`, `Data Processing`, `Index & Evaluation`, `Spaces CPU Pipeline`, `API Server`, `As-of Evaluation`, `HF Spaces`, `embeddings.py`, `Reranking`, `Settings`, `api_spaces.py`, `Spaces UI`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `Spaces UI` to `Core RAG Pipeline`, `Benchmark Infrastructure`, `Index & Evaluation`, `Benchmark Scripts`, `As-of Evaluation`, `Generation & Judging`, `Gate Tests`, `Reranking`, `Answer Generation`, `api_spaces.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `normalize_circular_number()` connect `Data Processing` to `Benchmark Infrastructure`, `Dataset Export`, `Corpus Validation`, `Master Metadata`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `Answer`) actually correct?**
  _`Chunk` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Lineage` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`Lineage` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_offline_pipeline()`) actually correct?**
  _`HashEmbedder` has 25 INFERRED edges - model-reasoned connections that need verification._