# Graph Report - SEBI circular RAG  (2026-07-15)

## Corpus Check
- 84 files · ~44,110 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 908 nodes · 1890 edges · 42 communities (32 shown, 10 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 378 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bfd4dab3`
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
- test_gate.py
- Corpus Validation
- Reranking
- ZeroGPU Tests
- Dataset Push
- Answer Generation
- Ops Server
- test_incremental_index.py
- .encode
- .load
- Build Scripts
- Canary Monitoring
- Index Refresh
- As-of UI Tests
- Space Deployment
- Discovery Scripts
- Index Upload
- UI Components
- Ops Scripts
- Notification Scripts
- Test Guards

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 73 edges
2. `HashEmbedder` - 29 edges
3. `RAGPipeline` - 28 edges
4. `hierarchical_chunk()` - 28 edges
5. `build_lineage()` - 26 edges
6. `ExtractiveStubGenerator` - 24 edges
7. `Lineage` - 23 edges
8. `CircularMeta` - 23 edges
9. `answer_with_abstention()` - 19 edges
10. `SpacesSettings` - 17 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py
- `test_chunks_config_refuses_header_and_maps_fields()` --indirect_call--> `Chunk`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/segment.py
- `run_query_spaces()` --calls--> `_citation_meta()`  [INFERRED]
  app.py → src/sebi_rag/api.py
- `_Boom` --uses--> `Settings`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/settings.py

## Import Cycles
- None detected.

## Communities (42 total, 10 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.05
Nodes (75): Answer, BaseModel, Chunk, Embedder, FastAPI, Reranker, smoke_pipeline(), Settings (+67 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.07
Nodes (55): Any, auroc(), best_threshold(), evaluate(), main(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t (+47 more)

### Community 2 - "Data Processing"
Cohesion: 0.05
Nodes (57): Pattern, Re-derive circular number + dates from each record's stored text and rewrite the, _existing_numbers(), extract_text(), _header(), ingest(), injection_scan(), _iso_date() (+49 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.07
Nodes (39): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces(), Path (+31 more)

### Community 4 - "Dataset Export"
Cohesion: 0.08
Nodes (50): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+42 more)

### Community 5 - "Utility Scripts"
Cohesion: 0.08
Nodes (28): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+20 more)

### Community 6 - "Spaces CPU Pipeline"
Cohesion: 0.13
Nodes (22): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).      Nev (+14 more)

### Community 7 - "Dataset Card Tests"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 8 - "Metadata Engine"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 9 - "Export Tests"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 10 - "API Server"
Cohesion: 0.12
Nodes (11): Protocol, Generator, _grounded_prompt(), Judge, MLXGenerator, OllamaGenerator, F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, Apple-Silicon-native generation via MLX-LM (D6 preferred runtime).      Loads a (+3 more)

### Community 11 - "Benchmark Scripts"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 12 - "Master Circular Verification"
Cohesion: 0.15
Nodes (22): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:, diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13).  Pure functions only: l (+14 more)

### Community 13 - "Lineage Tracking"
Cohesion: 0.05
Nodes (54): AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, run_pipeline_cases(), run_selector_cases(), summarize(), annotate_corpus() (+46 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.12
Nodes (15): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, Stage-2 reranking (mandatory, D4). Cross-encoder in production; a deterministic (+7 more)

### Community 15 - "HF Spaces"
Cohesion: 0.22
Nodes (6): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, demote_superseded(), P2 — cross-document supersession resolution.  Classifies each circular's referen, Down-weight reranked (chunk, score) pairs from superseded circulars and     re-s

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
Cohesion: 0.21
Nodes (13): answer_with_abstention(), ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge, _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested() (+5 more)

### Community 20 - "Gate Tests"
Cohesion: 0.13
Nodes (16): Answer, faithfulness(), _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), Generation with a hard abstention gate (D5).  If the top reranked score is below (+8 more)

### Community 21 - "test_gate.py"
Cohesion: 0.28
Nodes (10): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge() (+2 more)

### Community 22 - "Corpus Validation"
Cohesion: 0.29
Nodes (13): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations() (+5 more)

### Community 23 - "Reranking"
Cohesion: 0.22
Nodes (10): Embedder, DenseIndex, _doc_checksum(), HybridRetriever, ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding, Deterministic per-document checksum over its (enriched) chunk texts —     captur (+2 more)

### Community 24 - "ZeroGPU Tests"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 25 - "Dataset Push"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 26 - "Answer Generation"
Cohesion: 0.20
Nodes (5): BM25 lexical index (bm25s)., Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), SparseIndex, test_rrf_fusion_orders_by_reciprocal_rank()

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "test_incremental_index.py"
Cohesion: 0.39
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are e, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 32 - "Build Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 33 - "Canary Monitoring"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 34 - "Index Refresh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `API Server` to `Core RAG Pipeline`, `Benchmark Infrastructure`, `Data Processing`, `Index & Evaluation`, `Spaces CPU Pipeline`, `Benchmark Scripts`, `Lineage Tracking`, `As-of Evaluation`, `Generation & Judging`, `Gate Tests`, `test_gate.py`, `Reranking`, `Answer Generation`?**
  _High betweenness centrality (0.165) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `Core RAG Pipeline` to `Benchmark Infrastructure`, `Index & Evaluation`, `Lineage Tracking`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `normalize_circular_number()` connect `Data Processing` to `Benchmark Infrastructure`, `Dataset Export`, `Corpus Validation`, `Master Metadata`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `Answer`) actually correct?**
  _`Chunk` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_offline_pipeline()`) actually correct?**
  _`HashEmbedder` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `hierarchical_chunk()` (e.g. with `smoke_pipeline()` and `_slow_pipeline()`) actually correct?**
  _`hierarchical_chunk()` has 19 INFERRED edges - model-reasoned connections that need verification._