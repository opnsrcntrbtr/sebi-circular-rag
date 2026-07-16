# Graph Report - SEBI circular RAG  (2026-07-16)

## Corpus Check
- 90 files · ~47,206 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 955 nodes · 2050 edges · 55 communities (40 shown, 15 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 422 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `40397157`
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
- build_lineage
- .load
- Build Scripts
- Canary Monitoring
- Index Refresh
- As-of UI Tests
- test_ingest_refs.py
- Space Deployment
- Discovery Scripts
- Index Upload
- trace_failure.py
- embeddings.py
- UI Components
- Ops Scripts
- Notification Scripts
- Test Guards
- generate.py
- app.py
- retrieve.py
- test_injection.py
- discover_new.py
- renumber.py
- _s_header_token
- _s_dept_only
- _s_dept_order

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 68 edges
2. `RAGPipeline` - 36 edges
3. `hierarchical_chunk()` - 31 edges
4. `Lineage` - 31 edges
5. `HashEmbedder` - 29 edges
6. `build_lineage()` - 28 edges
7. `ExtractiveStubGenerator` - 24 edges
8. `CircularMeta` - 23 edges
9. `SubjectSimJudge` - 22 edges
10. `answer_with_abstention()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `test_chunks_config_refuses_header_and_maps_fields()` --indirect_call--> `Chunk`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/segment.py
- `test_real_corpus_loads_with_provenance_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_eval_harness.py → src/sebi_rag/corpus.py
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_summarize_reports_accuracy_and_failures()` --calls--> `AsofCaseResult`  [INFERRED]
  tests/test_eval_asof.py → src/sebi_rag/eval_asof.py
- `test_parse_meta_dept_order_document_end_to_end()` --calls--> `parse_meta()`  [INFERRED]
  tests/test_ingest_refs.py → src/sebi_rag/ingest_pdf.py

## Import Cycles
- None detected.

## Communities (55 total, 15 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.05
Nodes (49): Protocol, answer_with_abstention(), Generator, _grounded_prompt(), Judge, _judge_prompt(), _judge_prompt_identify(), MLXJudge (+41 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.08
Nodes (48): Any, main(), main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, dataset_quality(), load_index_chunks(), main(), Path (+40 more)

### Community 2 - "Data Processing"
Cohesion: 0.14
Nodes (17): Pattern, _header(), _iso_date(), _labeled_date(), parse_meta(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars., _subject(), _make_pdf() (+9 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.17
Nodes (9): FastAPI, create_app(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, /ready should trigger pipeline build and return ready=true., test_auth_required_when_key_set(), test_citation_meta_reports_superseded(), test_query_exceeds_time_budget_returns_504(), test_rate_limit() (+1 more)

### Community 4 - "Dataset Export"
Cohesion: 0.08
Nodes (50): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+42 more)

### Community 5 - "Utility Scripts"
Cohesion: 0.09
Nodes (27): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+19 more)

### Community 6 - "Spaces CPU Pipeline"
Cohesion: 0.11
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
Cohesion: 0.25
Nodes (5): Build the dense+sparse index once and persist it (run after corpus changes)., Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., Segmentation: hierarchical chunking + metadata + stable citation IDs.  Minimal,, P1 evaluation-harness test (offline).  Loads the real seed corpus (data/corpus/c, test_real_corpus_loads_with_provenance_fields()

### Community 11 - "Benchmark Scripts"
Cohesion: 0.24
Nodes (14): build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row() (+6 more)

### Community 12 - "Master Circular Verification"
Cohesion: 0.15
Nodes (22): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:, diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13).  Pure functions only: l (+14 more)

### Community 13 - "Lineage Tracking"
Cohesion: 0.26
Nodes (11): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), _build_chunks(), _build_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline.  Runs fully offline (HashEmbed, test_abstention_on_out_of_domain_query() (+3 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.11
Nodes (26): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any (+18 more)

### Community 15 - "HF Spaces"
Cohesion: 0.25
Nodes (15): _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars.  Drop a circular PDF into data/raw/ and (+7 more)

### Community 16 - "Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "Master Metadata"
Cohesion: 0.24
Nodes (11): _get(), Path, Central configuration: config.toml defaults, overridden by SEBI_RAG_* env vars., Resolve a setting: env var > config dict > default., Settings.load() plus the [spaces] table as settings.spaces.*          Load order, _clear(), Settings: defaults, config.toml, and env-override precedence., test_defaults_when_no_file() (+3 more)

### Community 18 - "Export Integration"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 19 - "Generation & Judging"
Cohesion: 0.20
Nodes (6): Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, _currency(), P2 — cross-document supersession resolution.  Classifies each circular's referen, P4b: as-of golden evaluation runner tests (offline)., test_summarize_reports_accuracy_and_failures()

### Community 20 - "Gate Tests"
Cohesion: 0.25
Nodes (3): Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Stage-2 reranking (mandatory, D4). Cross-encoder in production; a deterministic, Step 12 — end-to-end RAG integration test with the REAL stack.  bge-m3 (MPS) + b

### Community 22 - "Corpus Validation"
Cohesion: 0.29
Nodes (13): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations() (+5 more)

### Community 23 - "Reranking"
Cohesion: 0.06
Nodes (28): Chunk, Embedder, ndarray, Path, expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic, DenseIndex (+20 more)

### Community 24 - "ZeroGPU Tests"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 25 - "Dataset Push"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 26 - "Answer Generation"
Cohesion: 0.07
Nodes (59): smoke_pipeline(), load_circulars(), Path, HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, AsofCaseResult, load_golden_asof(), Path (+51 more)

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 29 - ".encode"
Cohesion: 0.22
Nodes (9): contexts_for(), Answer, demote_superseded(), Down-weight reranked (chunk, score) pairs from superseded circulars and     re-s, Map any cited circular that is superseded -> the circular(s) superseding it., superseded_citations(), End-to-end wiring: segment -> hybrid retrieve -> rerank -> generate/abstain., test_demote_superseded_puts_in_force_on_top() (+1 more)

### Community 30 - "build_lineage"
Cohesion: 0.06
Nodes (45): annotate_corpus(), detect_relations(), detect_relations_ex(), Path, Update each corpus record's supersession_status + superseded_by + supersedes, Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window() (+37 more)

### Community 31 - ".load"
Cohesion: 0.16
Nodes (20): BaseModel, main(), build_default_pipeline(), _citation_meta(), CitationMeta, QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline.  Run (real stack; loads the (+12 more)

### Community 32 - "Build Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 33 - "Canary Monitoring"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 34 - "Index Refresh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 36 - "test_ingest_refs.py"
Cohesion: 0.17
Nodes (10): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104",     "HO/ (, References split across tokens: merge up to 4 tokens after the first     HO/CIR/, _rejoin_split(), _s_anchor_merge(), Regression matrix for SEBI reference-number extraction.  One case per known form, test_fulltext_fallback_returns_earliest_body_reference(), test_parse_meta_dept_order_document_end_to_end() (+2 more)

### Community 40 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 41 - "embeddings.py"
Cohesion: 0.24
Nodes (5): Calibrate top_k and the abstention threshold against the citation-precision sign, Embedder, ndarray, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, _tokens()

### Community 46 - "generate.py"
Cohesion: 0.22
Nodes (6): ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, faithfulness(), Generation with a hard abstention gate (D5).  If the top reranked score is below, Check that every circular id the answer cites (in square brackets) was     actua, Faithfulness: catch answers that cite circulars not in the retrieved context., test_faithfulness_scoring()

### Community 47 - "app.py"
Cohesion: 0.31
Nodes (7): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces()

### Community 48 - "retrieve.py"
Cohesion: 0.22
Nodes (6): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, Stage-1 hybrid retrieval: dense (FAISS) + sparse (BM25) fused by RRF.  Mandatory, Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 49 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Core RAG Pipeline` to `Benchmark Infrastructure`, `Spaces CPU Pipeline`, `API Server`, `Benchmark Scripts`, `generate.py`, `test_injection.py`, `Gate Tests`, `Answer Generation`, `.encode`, `.load`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `Answer Generation` to `Core RAG Pipeline`, `Benchmark Infrastructure`, `Index & Evaluation`, `embeddings.py`, `Benchmark Scripts`, `.encode`, `.load`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `normalize_circular_number()` connect `HF Spaces` to `Benchmark Infrastructure`, `Data Processing`, `Dataset Export`, `As-of Evaluation`, `Corpus Validation`, `build_lineage`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `Answer`) actually correct?**
  _`Chunk` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `hierarchical_chunk()` (e.g. with `smoke_pipeline()` and `_slow_pipeline()`) actually correct?**
  _`hierarchical_chunk()` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Lineage` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`Lineage` has 15 INFERRED edges - model-reasoned connections that need verification._