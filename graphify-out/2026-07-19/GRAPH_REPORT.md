# Graph Report - SEBI circular RAG  (2026-07-19)

## Corpus Check
- 95 files · ~49,528 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1006 nodes · 2171 edges · 47 communities (38 shown, 9 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 466 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5e97151a`
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
- Lineage
- Benchmark Scripts
- Master Circular Verification
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
- eval_gate.py
- build_lineage
- Build Scripts
- Canary Monitoring
- Index Refresh
- As-of UI Tests
- .grounded
- Space Deployment
- Discovery Scripts
- Index Upload
- app.py
- test_injection.py
- UI Components
- Ops Scripts
- Notification Scripts
- Test Guards
- bench_rerankers.py
- renumber.py

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 78 edges
2. `RAGPipeline` - 36 edges
3. `hierarchical_chunk()` - 34 edges
4. `HashEmbedder` - 33 edges
5. `Lineage` - 31 edges
6. `build_lineage()` - 28 edges
7. `ExtractiveStubGenerator` - 24 edges
8. `CircularMeta` - 23 edges
9. `SubjectSimJudge` - 22 edges
10. `answer_with_abstention()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `_chunk()` --calls--> `Chunk`  [INFERRED]
  tests/test_hyde.py → src/sebi_rag/segment.py
- `test_chunks_config_refuses_header_and_maps_fields()` --indirect_call--> `Chunk`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/segment.py
- `test_describe_cleans_markdown_and_newlines()` --calls--> `HeaderGenerator`  [INFERRED]
  tests/test_context_headers.py → src/sebi_rag/context_headers.py
- `test_describe_error_or_empty_returns_empty()` --calls--> `HeaderGenerator`  [INFERRED]
  tests/test_context_headers.py → src/sebi_rag/context_headers.py

## Import Cycles
- None detected.

## Communities (47 total, 9 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.15
Nodes (11): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, _currency(), mc_topic(), P2 — cross-document supersession resolution.  Classifies each circular's referen, Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None.      Us, Map any cited circular that is superseded -> the circular(s) superseding it. (+3 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.08
Nodes (49): Any, main(), main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, dataset_quality(), load_index_chunks(), main(), Path (+41 more)

### Community 2 - "Data Processing"
Cohesion: 0.05
Nodes (57): Pattern, Re-derive circular number + dates from each record's stored text and rewrite the, _existing_numbers(), extract_text(), _header(), ingest(), injection_scan(), _iso_date() (+49 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.22
Nodes (12): AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, run_pipeline_cases(), run_selector_cases(), summarize(), _lin_chain() (+4 more)

### Community 4 - "Dataset Export"
Cohesion: 0.08
Nodes (50): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+42 more)

### Community 5 - "Utility Scripts"
Cohesion: 0.08
Nodes (28): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+20 more)

### Community 6 - "Spaces CPU Pipeline"
Cohesion: 0.09
Nodes (24): Generator, _grounded_prompt(), F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte (+16 more)

### Community 7 - "Dataset Card Tests"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 8 - "Metadata Engine"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 9 - "Export Tests"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 10 - "Lineage"
Cohesion: 0.17
Nodes (11): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage.  Offline only —, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_none_and_empty_hyde_are_identical_to_baseline() (+3 more)

### Community 11 - "Benchmark Scripts"
Cohesion: 0.16
Nodes (10): annotate_corpus(), Lineage, Path, Update each corpus record's supersession_status + superseded_by + supersedes, Connected component over supersedes/superseded_by (both tiers)., The circular in this family that governs on date as_of (ISO), or         None wh, test_annotate_corpus_adds_master_fields_and_consolidates_edges(), test_annotate_corpus_writes_new_metadata_fields() (+2 more)

### Community 12 - "Master Circular Verification"
Cohesion: 0.15
Nodes (22): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:, diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13).  Pure functions only: l (+14 more)

### Community 13 - "test_integration_e2e.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.09
Nodes (30): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any (+22 more)

### Community 15 - "Embedder"
Cohesion: 0.05
Nodes (49): Protocol, Embedder, expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic, qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2 (+41 more)

### Community 16 - "Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "Master Metadata"
Cohesion: 0.11
Nodes (21): Chunk, Path, main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).  Resumable, apply_context_headers(), HeaderGenerator, in_scope(), load_headers() (+13 more)

### Community 18 - "Export Integration"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 19 - "answer_with_abstention"
Cohesion: 0.09
Nodes (16): Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, Stage-2 reranking (mandatory, D4). Cross-encoder in production; a deterministic, Segmentation: hierarchical chunking + metadata + stable citation IDs.  Minimal, (+8 more)

### Community 20 - "test_gate.py"
Cohesion: 0.67
Nodes (3): load_circulars(), Path, test_real_corpus_loads_with_provenance_fields()

### Community 21 - "Chunk"
Cohesion: 0.06
Nodes (52): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces(), BaseModel (+44 more)

### Community 22 - "Corpus Validation"
Cohesion: 0.29
Nodes (13): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations() (+5 more)

### Community 24 - "ZeroGPU Tests"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 25 - "Dataset Push"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 26 - "Answer Generation"
Cohesion: 0.18
Nodes (23): smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., LexicalReranker, Deterministic query-coverage reranker (test/fallback).      Score = fraction of, CircularMeta (+15 more)

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "SubjectSimJudge"
Cohesion: 0.19
Nodes (16): hierarchical_chunk(), _paragraphs(), Split into units each <= max_chars.      PDF-extracted text often lacks blank-li, Document -> section -> paragraph chunks with stable IDs.      A "section" is det, _body(), Chunker (segment.hierarchical_chunk) behaviour.  Regression guard for the "5. Nu, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_absorption_respects_300_char_cap() (+8 more)

### Community 29 - "eval_gate.py"
Cohesion: 0.07
Nodes (40): Answer, answer_with_abstention(), faithfulness(), Judge, _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice() (+32 more)

### Community 30 - "build_lineage"
Cohesion: 0.19
Nodes (15): build_lineage(), _lin_chain(), P2 lineage / supersession resolution tests., test_build_lineage_edges_tiered(), test_build_lineage_inferred_master_topic_edge(), test_governing_on_before_family_exists(), test_governing_on_linear_chain(), test_governing_on_unknown_dates_excluded() (+7 more)

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
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan, _master(), test_annotate_idempotent() (+7 more)

### Community 40 - "app.py"
Cohesion: 0.18
Nodes (11): FastAPI, create_app(), _offline_pipeline(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, /ready should trigger pipeline build and return ready=true., test_auth_required_when_key_set(), test_citation_meta_reports_superseded(), test_query_exceeds_time_budget_returns_504() (+3 more)

### Community 41 - "test_injection.py"
Cohesion: 0.20
Nodes (10): detect_relations(), detect_relations_ex(), Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window(), A circular that names another circular BEFORE the supersede trigger     word mus, test_detect_relations_delegates_unchanged(), test_detect_relations_ex_evidence_and_extractor() (+2 more)

### Community 46 - "bench_rerankers.py"
Cohesion: 0.26
Nodes (11): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), _build_chunks(), _build_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline.  Runs fully offline (HashEmbed, test_abstention_on_out_of_domain_query() (+3 more)

### Community 47 - "renumber.py"
Cohesion: 0.29
Nodes (5): contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, demote_superseded(), Down-weight reranked (chunk, score) pairs from superseded circulars and     re-s, test_demote_superseded_puts_in_force_on_top()

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Embedder` to `Core RAG Pipeline`, `Benchmark Infrastructure`, `Data Processing`, `Spaces CPU Pipeline`, `Lineage`, `renumber.py`, `answer_with_abstention`, `test_gate.py`, `Chunk`, `Answer Generation`, `SubjectSimJudge`, `eval_gate.py`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Why does `normalize_circular_number()` connect `Data Processing` to `Benchmark Infrastructure`, `Dataset Export`, `.grounded`, `As-of Evaluation`, `Corpus Validation`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `derive_validity()` connect `Metadata Engine` to `Core RAG Pipeline`, `Benchmark Scripts`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `Answer`) actually correct?**
  _`Chunk` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `hierarchical_chunk()` (e.g. with `smoke_pipeline()` and `_slow_pipeline()`) actually correct?**
  _`hierarchical_chunk()` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_offline_pipeline()`) actually correct?**
  _`HashEmbedder` has 29 INFERRED edges - model-reasoned connections that need verification._