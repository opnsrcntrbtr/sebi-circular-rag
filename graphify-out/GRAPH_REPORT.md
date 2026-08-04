# Graph Report - SEBI circular RAG  (2026-08-04)

## Corpus Check
- 164 files · ~167,974 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2070 nodes · 4286 edges · 149 communities (123 shown, 26 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 231 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e1f78598`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Dataset Export Pipeline
- Telemetry and Performance
- Human Annotation Management
- Benchmarking and Indexing
- Regulation Lineage Resolution
- Web UI and Demo
- Chunking and Embedding
- LLM Grounding and Judging
- Regulation Citation Extraction
- Regulation Edge Annotation
- Dataset Card Validation
- Benchmark Dataset Generation
- Hybrid Retrieval Indexing
- Circular Metadata Classification
- Contextual Header Generation
- Document Lineage Tracking
- LLM Adjudication Prompts
- SPLADE Sparse Retrieval
- Dataset Export Testing
- Temporal Evaluation Runner
- RAG Pipeline API
- Annotation Decision Logic
- API Integration Testing
- Escalated Row Backfilling
- Gemini Annotation Adjudication
- Hugging Face Pipeline
- Master Circular Verification
- Reranker Evaluation Harness
- Faithfulness and Abstention
- Annotator Agreement Metrics
- PDF Ingestion and Renumbering
- Retrieval Failure Classification
- Local Model Adjudication
- Supersession Reranking Logic
- Token Encoding Utilities
- Lexical Reranking and Pooling
- PDF Metadata Parsing
- Configuration and Settings
- Scraper Logic Testing
- Evaluation Metrics Reporting
- SPLADE Encoder Implementation
- Statistical and Hardware Helpers
- Master Circular Metadata
- Export Integration Testing
- Local Annotation Adjudication
- Golden Dataset Validation
- HyDE Query Expansion
- Regulation Scraper Testing
- Decision Promotion Logic
- Regulation Web Scraper
- Circular Web Scraper
- Query Lexical Expansion
- ZeroGPU Deployment Testing
- CI Gate Selection
- Hardware Device Selection
- Reference Number Extraction
- Alias Validation Tests
- Qwen MLX Reranker
- Binomial Confidence Intervals
- PDF Recovery Tool
- Dataset Hub Upload
- UI Query Submission
- Regulation Edge Auditing
- UI Logic Testing
- Document ID Remapping
- Corpus Text Repair
- Evaluation Harness Testing
- Statistical Significance Testing
- .family
- Operations Server
- Regulation Edge Audit
- Draft Row Adjudication
- splade_encoder.py
- Bootstrap Confidence Intervals
- .grounded
- Retrieval Failure Tracing
- Governing Span Resolution
- Provision Agreement Logic
- test_gate.py
- Adjudication Error Handling
- Supersession Precision Measurement
- Regulation Edge Testing
- answer_with_abstention
- Golden Dataset Seeding
- RRF Parameter Sweeping
- Prompt Injection Detection
- Regulatory Basis Indexing
- answer_with_abstention
- Span to Chunk Resolution
- Inter-Annotator Agreement
- test_gate.py
- Retrieval Metric Evaluation
- TestReadTrecRun
- Benchmark Uncertainty Quantification
- Circular Reference Examples
- validate_golden
- Execution Shell Scripts
- Canary Shell Scripts
- Benchmark Artifact Export
- build_report
- Refresh Shell Scripts
- MRR Evaluation
- Parsing Latency Measurement
- Retrieval Recall Evaluation
- Temporal Accuracy Evaluation
- As-of Date Testing
- Benchmark Export Testing
- Retrieval Recall Evaluation
- Regulation Edge Construction
- Benchmark Rescoring
- Automated Research Script
- Circular Renumbering Audit
- _grounded_prompt
- .encode
- SEBI Circular Dataset
- _rejoin_split
- Hugging Face Deployment
- Discovery Execution Script
- Index Upload Utilities
- Measurement Execution Script
- Operations Execution Script
- Notification Script
- Phoenix Service Startup
- Test Environment Configuration
- Mutual Fund Master Appendix
- _s_mc_no
- SEBI Master Circulars
- Slash Command Optimization
- Circular ID Tracking
- Escalation Labeling
- Path
- Unresolved Regulation Tracking
- HF Spaces Requirements
- Golden Dataset Initialization
- Depository Master Appendix
- SEBI Regulation Listings
- test_integration_e2e.py
- CrossEncoderReranker
- seed_v7.py
- eval_json.py
- test_persistence.py
- TestPerQueryRecall
- .query
- _s_mc_no
- CrossEncoderReranker
- BGEM3Embedder
- _alias_keys
- load_circulars
- test_annotation_adds_no_circular_meta_field

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 62 edges
2. `hierarchical_chunk()` - 45 edges
3. `ExtractiveStubGenerator` - 42 edges
4. `HashEmbedder` - 42 edges
5. `RAGPipeline` - 39 edges
6. `CircularMeta` - 39 edges
7. `build_lineage()` - 29 edges
8. `LexicalReranker` - 29 edges
9. `MeasureResult` - 26 edges
10. `extract_citations()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_derived_floor_never_goes_negative()` --calls--> `derive_floors()`  [INFERRED]
  tests/test_golden_v7_gate.py → scripts/golden_v7/derive_thresholds.py
- `main()` --calls--> `SubjectSimJudge`  [INFERRED]
  scripts/golden_v7/derive_thresholds.py → src/sebi_rag/generate.py
- `main()` --calls--> `_compute_kwargs()`  [INFERRED]
  scripts/bench_retrieval.py → src/sebi_rag/api.py
- `run_query_spaces()` --calls--> `_citation_meta()`  [INFERRED]
  app.py → src/sebi_rag/api.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **SEBI Regulatory Framework** — tests_fixtures_master_appendix_pre2015_sebi, tests_fixtures_master_appendix_pre2015_circulars, tests_fixtures_master_appendix_pre2015_communications [INFERRED 0.90]

## Communities (149 total, 26 thin omitted)

### Community 0 - "Dataset Export Pipeline"
Cohesion: 0.06
Nodes (70): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+62 more)

### Community 1 - "Telemetry and Performance"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 2 - "Human Annotation Management"
Cohesion: 0.11
Nodes (36): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+28 more)

### Community 3 - "Benchmarking and Indexing"
Cohesion: 0.16
Nodes (10): Benchmark MLX generators on the golden set: faithfulness, groundedness,…, Build the dense+sparse index once and persist it (run after corpus changes).…, scripts/eval_asof.py, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the…, ADR-002 follow-up: compare the production subject-sim gate against the SECTION-…, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.…, Stage-1 hybrid retrieval: dense (FAISS) + sparse (BM25) fused by RRF. Mandatory…, _chunks() (+2 more)

### Community 4 - "Regulation Lineage Resolution"
Cohesion: 0.09
Nodes (31): _jaccard(), load_regulations(), name_tokens(), Path, Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6). Regulations…, Resolve a cited regulation name+year to a canonical reg_id. Returns (reg_id,…, Load data/corpus/regulations.jsonl into a list of regulation records. Thin…, Deterministic, stable identity slug. This is the edge target and join key. (+23 more)

### Community 5 - "Web UI and Demo"
Cohesion: 0.13
Nodes (18): Generator, ExternalSpaceGenerator, Primary generator: calls a public LLM Space via gradio_client. Wired to…, [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).      Nev, SpacesSettings, _Boom, _Canned, _hybrid() (+10 more)

### Community 6 - "Chunking and Embedding"
Cohesion: 0.27
Nodes (11): _build_chunks(), _build_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline. Runs fully offline…, Offline pipeline whose single circular rests on a repealed regulation., _repealed_basis_pipeline(), test_abstention_on_out_of_domain_query(), test_hybrid_retrieval_finds_relevant_circular(), test_note_absent_when_index_is_none() (+3 more)

### Community 8 - "Regulation Citation Extraction"
Cohesion: 0.09
Nodes (34): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+26 more)

### Community 9 - "Regulation Edge Annotation"
Cohesion: 0.15
Nodes (29): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+21 more)

### Community 10 - "Dataset Card Validation"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 11 - "Benchmark Dataset Generation"
Cohesion: 0.16
Nodes (27): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), chunks_by_doc(), dir_fingerprint() (+19 more)

### Community 12 - "Hybrid Retrieval Indexing"
Cohesion: 0.13
Nodes (13): Embedder, Protocol, DenseIndex, _doc_checksum(), HybridRetriever, ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached embedding rows… (+5 more)

### Community 13 - "Circular Metadata Classification"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation. Locked…, Validity of one circular from the tiered edge list (any scope: the function…, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 14 - "Contextual Header Generation"
Cohesion: 0.07
Nodes (31): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+23 more)

### Community 15 - "Document Lineage Tracking"
Cohesion: 0.18
Nodes (13): _lin_chain(), P2 lineage / supersession resolution tests., A circular that names another circular BEFORE the supersede trigger word must…, test_detect_relations_delegates_unchanged(), test_detect_relations_ex_evidence_and_extractor(), test_detect_relations_ex_supersedes_when_ref_before_trigger(), test_governing_on_before_family_exists(), test_governing_on_linear_chain() (+5 more)

### Community 16 - "LLM Adjudication Prompts"
Cohesion: 0.12
Nodes (26): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply… (+18 more)

### Community 17 - "SPLADE Sparse Retrieval"
Cohesion: 0.15
Nodes (12): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.…, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+4 more)

### Community 18 - "Dataset Export Testing"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 19 - "Temporal Evaluation Runner"
Cohesion: 0.19
Nodes (18): sebi_rag/eval_asof.py, AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Aggregate case results with an exact confidence interval. Pure function of the…, run_pipeline_cases(), run_selector_cases() (+10 more)

### Community 20 - "RAG Pipeline API"
Cohesion: 0.20
Nodes (20): BaseModel, FastAPI, RAGPipeline, main(), build_default_pipeline(), CitationMeta, create_app(), QueryRequest (+12 more)

### Community 21 - "Annotation Decision Logic"
Cohesion: 0.13
Nodes (25): decide(), Spec sec7 promotion rules for one row. `votes_by_annotator` is this row's votes…, Abstain rows have no explicit claude vote at all (Task 8 never judged them) -…, Both externals independently think something DOES govern (disputing the…, The LLM leg is whichever single non-claude/non-human annotator voted - "qwen"…, External marked claude's chunk governing plus extras: claude's label is…, The abstain protocol can never emit non-empty governing (no letters are…, Two externals both replying NONE on an answerable row must queue, not flip: a… (+17 more)

### Community 22 - "API Integration Testing"
Cohesion: 0.09
Nodes (18): integration, Lineage, _citation_meta(), _offline_pipeline(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit,…, /ready should trigger pipeline build and return ready=true., _slow_pipeline(), _SlowGenerator (+10 more)

### Community 23 - "Escalated Row Backfilling"
Cohesion: 0.12
Nodes (28): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+20 more)

### Community 24 - "Gemini Annotation Adjudication"
Cohesion: 0.11
Nodes (23): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec… (+15 more)

### Community 25 - "Hugging Face Pipeline"
Cohesion: 0.24
Nodes (14): build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux). Parallel…, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row() (+6 more)

### Community 26 - "Master Circular Verification"
Cohesion: 0.19
Nodes (21): sebi_rag/verify_master.py, diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13). Pure functions only:…, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows. (+13 more)

### Community 27 - "Reranker Evaluation Harness"
Cohesion: 0.13
Nodes (22): Answer, main(), Retrieval-only benchmark with TREC runfile and reproducibility metadata. Use…, smoke_pipeline(), evaluate(), Emit one JSON line of retrieval/citation/abstention metrics using the persisted, _norm_ws(), per_query_recall() (+14 more)

### Community 28 - "Faithfulness and Abstention"
Cohesion: 0.30
Nodes (11): _clear(), Settings: defaults, config.toml, and env-override precedence., test_citation_scorer_enabled_defaults_off(), test_citation_scorer_enabled_env_on(), test_compute_defaults(), test_compute_env_overrides(), test_compute_from_file(), test_defaults_when_no_file() (+3 more)

### Community 29 - "Annotator Agreement Metrics"
Cohesion: 0.15
Nodes (19): _claude_accuracy_ci(), gwet_ac1(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation…, Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a prevalence-… (+11 more)

### Community 30 - "PDF Ingestion and Renumbering"
Cohesion: 0.17
Nodes (17): Re-derive circular number + dates from each record's stored text and rewrite…, _existing_numbers(), extract_text(), ingest(), main(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars. Drop a circular PDF into data/raw/ and… (+9 more)

### Community 31 - "Retrieval Failure Classification"
Cohesion: 0.12
Nodes (25): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any… (+17 more)

### Community 32 - "Local Model Adjudication"
Cohesion: 0.15
Nodes (19): _extract_text(), Qwen-family models may emit <think>...</think> reasoning as inline text,…, Anthropic Messages response -> reply text: concatenates `text` content blocks,…, _strip_thinking(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external…, Five pilot rows from five strata measure more than five from one - the gemini…, Vote records must say annotator "qwen" (never reuse "gemini" - the agreement… (+11 more)

### Community 33 - "Supersession Reranking Logic"
Cohesion: 0.20
Nodes (14): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY).…, (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'. Takes the LAST bracket group…, _record() (+6 more)

### Community 34 - "Token Encoding Utilities"
Cohesion: 0.26
Nodes (14): discover(), _listing_url(), main(), _page(), _parse_date(), parse_rows(), pdf_url_for(), date (+6 more)

### Community 35 - "Lexical Reranking and Pooling"
Cohesion: 0.17
Nodes (16): Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)…, smoke_pipeline(), assemble_pool(), TREC-style pool: gold-doc literal matches lead, then round-robin over…, LexicalReranker, Stage-2 reranking (mandatory, D4). Cross-encoder in production; a deterministic…, Deterministic query-coverage reranker (test/fallback). Score = fraction of…, One gold doc with `n` chunks that ALL contain the word "broker", so a… (+8 more)

### Community 36 - "PDF Metadata Parsing"
Cohesion: 0.17
Nodes (12): _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash…, The mirror of the kerning case above. When the en-dash has spaces on BOTH sides…, 2011-era master circulars use "SEBI/<DEPT>/MC No.<n>/<serial>/<year>", matching…, Old-format PDFs (e.g. CIR/MRD/DP/ 11 /2012) split the number with a space…, test_ingest_extracts_metadata_and_lineage(), test_parse_meta_handles_2011_mc_number_format() (+4 more)

### Community 37 - "Configuration and Settings"
Cohesion: 0.23
Nodes (14): hierarchical_chunk(), Document -> section -> paragraph chunks with stable IDs. A "section" is…, _body(), Chunker (segment.hierarchical_chunk) behaviour. Regression guard for the "5.…, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_absorption_respects_300_char_cap(), test_bare_parent_heading_folds_into_first_subsection(), test_bare_parent_heading_not_emitted_as_standalone_chunk() (+6 more)

### Community 38 - "Scraper Logic Testing"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 39 - "Evaluation Metrics Reporting"
Cohesion: 0.24
Nodes (6): measure_context_precision(), MeasureReport, MeasureResult, Fraction of top-k chunks from relevant circulars. Unlike recall@k (which is…, TestContextPrecision, TestDataClasses

### Community 40 - "SPLADE Encoder Implementation"
Cohesion: 0.15
Nodes (20): Settings, Context ids the answer rests on. Scores each context's answer-relevance     via, select_citations(), _chunk(), _FakeReranker, Tests for B' selective citations: select_citations() and its integration., Deterministic scorer: returns preset answer-relevance scores, sorted desc., When citation_scorer_enabled=True, Settings loads a non-None scorer. (+12 more)

### Community 41 - "Statistical and Hardware Helpers"
Cohesion: 0.15
Nodes (10): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Path, Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict. (+2 more)

### Community 42 - "Master Circular Metadata"
Cohesion: 0.26
Nodes (12): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+4 more)

### Community 43 - "Export Integration Testing"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 44 - "Local Annotation Adjudication"
Cohesion: 0.19
Nodes (15): Transient-failure predicate for the real Gemini call: rate limiting (429) and…, Same per-row deterministic shuffle as make_packet.py's write_packet:…, _should_retry(), _shuffled_candidates(), _current_model(), main(), pilot(), _pilot_ids() (+7 more)

### Community 45 - "Golden Dataset Validation"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 46 - "HyDE Query Expansion"
Cohesion: 0.14
Nodes (14): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), test_retrieve_dense_leg_keeps_raw_query(), test_retrieve_routes_expanded_query_to_sparse_leg(), _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —… (+6 more)

### Community 48 - "Decision Promotion Logic"
Cohesion: 0.21
Nodes (14): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions` (keyed by…, _min_agreement_fixture(), Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):…, _same_provision_fixture(), test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only() (+6 more)

### Community 49 - "Regulation Web Scraper"
Cohesion: 0.27
Nodes (5): main(), metrics_to_markdown(), Format results as a markdown table., Unit tests for sebi_rag.measure — automated metric collection., TestCLI

### Community 50 - "Circular Web Scraper"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans…, _master(), test_annotate_idempotent() (+7 more)

### Community 51 - "Query Lexical Expansion"
Cohesion: 0.23
Nodes (12): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and…, Query-side lexical expansion (intervention #2, glossary variant).…, test_all_five_sparse_failure_queries_expand(), test_lay_term_gains_statutory_synonym(), test_multiword_synonym_splits_into_tokens(), test_pull_maps_to_withdraw() (+4 more)

### Community 52 - "ZeroGPU Deployment Testing"
Cohesion: 0.14
Nodes (13): app_module(), fixture, Regression coverage for the ZeroGPU-hardware workaround in app.py. Background:…, Inject a fake `spaces` module so app.py's `import spaces` succeeds offline, and…, Static guard: if `import spaces` or the `@spaces.GPU` decorator is ever…, It must stay dead code: calling it would request a real ZeroGPU allocation (and…, The functions actually on the request path (get_pipeline, run_query_spaces)…, `hardware:` in README-spaces.md is not a documented Spaces config key (only… (+5 more)

### Community 53 - "CI Gate Selection"
Cohesion: 0.06
Nodes (32): derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).  Write, metric -> per-query score vector, into gate-floor names -> floor value.      Met, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the…, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,…, True iff every floor's metric is present in `report_gate` and meets it. Missing… (+24 more)

### Community 54 - "Hardware Device Selection"
Cohesion: 0.20
Nodes (11): pick_device(), Device + precision selection for Apple-Silicon inference. Centralizes the…, Resolve the compute device. A truthy explicit `pref` ("mps"/"cpu"/"cuda") wins.…, fp16 only on GPU-class devices; never on cpu. bf16 is never returned here by…, should_use_fp16(), Device + fp16 policy selection (no real torch/mps required)., test_pick_device_auto_cpu_when_no_mps(), test_pick_device_auto_mps_when_available() (+3 more)

### Community 55 - "Reference Number Extraction"
Cohesion: 0.20
Nodes (8): _primary_number(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_dedup_uses_normalized_numbers(), test_fulltext_fallback_returns_earliest_body_reference(), test_parse_meta_dept_order_document_end_to_end(), test_parse_meta_excludes_prefix_variant_self_reference(), test_primary_number_format_matrix()

### Community 57 - "Qwen MLX Reranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 58 - "Binomial Confidence Intervals"
Cohesion: 0.22
Nodes (5): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, test_render_report_includes_ac1_and_provision(), The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 59 - "PDF Recovery Tool"
Cohesion: 0.27
Nodes (9): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only). Gradio SDK…, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict ISO YYYY-…, run_query_spaces(), warm_up_gpu() (+1 more)

### Community 60 - "Dataset Hub Upload"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default:…, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 61 - "UI Query Submission"
Cohesion: 0.22
Nodes (12): Human-readable regulation name. Year disambiguates same-short_name repeal pairs…, reg_display_name(), build_ui(), _empty_outputs(), _parse_as_of(), Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO YYYY-MM-DD.…, SSRF guard: reject URLs pointing to private/internal/reserved addresses. Blocks… (+4 more)

### Community 62 - "Regulation Edge Auditing"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 63 - "UI Logic Testing"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 64 - "Document ID Remapping"
Cohesion: 0.24
Nodes (13): Protocol, answer_with_abstention(), _is_non_sebi_domain(), Judge, Return True if the query clearly targets a non-SEBI regulator's domain.      Use, _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons,…, test_advisory_draft_on_gate_failure_only_when_requested() (+5 more)

### Community 65 - "Corpus Text Repair"
Cohesion: 0.22
Nodes (4): main(), Repair the 6 records whose body text was overwritten with one shared circular's…, The repair map must name a real orphan PDF that parses to the circular_number…, test_numbers_normalize_distinctly()

### Community 66 - "Evaluation Harness Testing"
Cohesion: 0.49
Nodes (10): run_eval(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-…, _row(), test_as_of_is_passed_to_pipeline(), test_chunk_metrics_computed_for_span_rows(), test_gate_is_none_when_nothing_adjudicated(), test_gate_subreport_covers_only_adjudicated() (+2 more)

### Community 67 - "Statistical Significance Testing"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries. Returns mean_b -…, Randomization p-values use the (count+1)/(n+1) estimator, so a p-value of…, One query flipping out of 56 is exactly the iv9-style verdict: the…, TestPairedDelta

### Community 68 - ".family"
Cohesion: 0.12
Nodes (16): csr_matrix, Path, SPLADE learned-sparse retrieval leg (iv11). Non-destructive, opt-in third RRF…, SpladeIndex, _fake_encode(), _chunks(), _fake_encode(), Returns a fixed dense ranking regardless of query. (+8 more)

### Community 69 - "Operations Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 70 - "Regulation Edge Audit"
Cohesion: 0.29
Nodes (10): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+2 more)

### Community 71 - "Draft Row Adjudication"
Cohesion: 0.29
Nodes (10): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+2 more)

### Community 73 - "Bootstrap Confidence Intervals"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 74 - ".grounded"
Cohesion: 0.29
Nodes (4): Run all (or specified) metrics sequentially., run_all_metrics(), Empty metrics list is falsy → defaults to ALL_METRICS., TestRegistry

### Community 75 - "Retrieval Failure Tracing"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 76 - "Governing Span Resolution"
Cohesion: 0.27
Nodes (10): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote} spans, looked…, _resolve_governing_spans(), _pool(), Amendment 2026-07-26 (user-approved): the promotion unit is the PROVISION, not…, test_decide_same_provision_other_chunk_promotes_with_pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool() (+2 more)

### Community 77 - "Provision Agreement Logic"
Cohesion: 0.20
Nodes (10): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using the…, Does this external vote confirm claude's label, at PROVISION level? Amendment…, Different chunk copies of the same quoted provision agree at provision level…, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction(), test_provision_agree_disjoint_without_pool_is_false() (+2 more)

### Community 78 - "test_gate.py"
Cohesion: 0.22
Nodes (7): annotate_corpus(), load_records(), Path, Update each corpus record's supersession_status + superseded_by + supersedes…, test_annotate_corpus_adds_master_fields_and_consolidates_edges(), test_annotate_corpus_writes_new_metadata_fields(), test_real_corpus_oiae_supersedes_listed_circulars()

### Community 79 - "Adjudication Error Handling"
Cohesion: 0.22
Nodes (10): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt) -> str`…, Scans the per-row cache for `ids` and returns the ones flagged parse_error:…, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct from a well-…, Defensive: an id that was never adjudicated (no cache file at all) is not…, test_adjudicate_marks_parse_error_for_garbled_abstain_protocol_reply() (+2 more)

### Community 80 - "Supersession Precision Measurement"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 81 - "Regulation Edge Testing"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 83 - "Golden Dataset Seeding"
Cohesion: 0.13
Nodes (16): Answer, faithfulness(), _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), Generation with a hard abstention gate (D5).  If the top reranked score is below (+8 more)

### Community 84 - "RRF Parameter Sweeping"
Cohesion: 0.31
Nodes (8): main(), mrr(), ndcg_at_k(), Sweep RRF k_const values on the golden set. No index rebuild needed., recall_at_k(), Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 85 - "Prompt Injection Detection"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 86 - "Regulatory Basis Indexing"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 87 - "answer_with_abstention"
Cohesion: 0.19
Nodes (18): _body(), main(), _mid(), mine_lineage_pairs(), mine_multi_hop(), mine_numeric(), mine_repealed_basis(), Deterministic candidate mining for golden_v7 drafting (spec Sec 4, Sec 5). Pure… (+10 more)

### Community 88 - "Span to Chunk Resolution"
Cohesion: 0.42
Nodes (8): _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through(), test_qrels_span_rows_get_grade_2(), test_resolves_normalized_whitespace_quote(), test_unresolvable_quote_returns_empty(), test_validator_flags_unresolvable_quote_when_chunks_given()

### Community 89 - "Inter-Annotator Agreement"
Cohesion: 0.25
Nodes (8): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw element is…, The kappa base-rate paradox: one label dominates, raw agreement is high, yet…, test_cohen_kappa_both_constant_and_identical_is_one(), test_cohen_kappa_empty_input_is_one(), test_cohen_kappa_identical_lists_is_one(), test_cohen_kappa_independent_looking_lists_is_low(), test_gwet_ac1_exceeds_kappa_on_skewed_high_agreement()

### Community 90 - "test_gate.py"
Cohesion: 0.28
Nodes (7): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped…, detect_relations(), detect_relations_ex(), P2 — cross-document supersession resolution. Classifies each circular's…, Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window()

### Community 91 - "Retrieval Metric Evaluation"
Cohesion: 0.39
Nodes (6): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), Automated metric collection for the SEBI Circular RAG pipeline. Six on-demand…, test_retrieval_metrics()

### Community 92 - "TestReadTrecRun"
Cohesion: 0.16
Nodes (9): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), write_trec_run(), Re-scoring archived runfiles: round-trip and agreement with the live metric., The archived runfiles embed section headings in the doc id., Ten chunks of one circular must not crowd the cutoff: the k applies to unique…, End-to-end guarantee behind the re-scoring script: replaying a runfile yields…, TestPerQueryRecall (+1 more)

### Community 93 - "Benchmark Uncertainty Quantification"
Cohesion: 0.25
Nodes (5): BootstrapCI, PairedResult, Uncertainty quantification for benchmark runs. The golden set is n=56…, True when the randomization test rejects at 1 - confidence AND the paired…, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 94 - "Circular Reference Examples"
Cohesion: 0.25
Nodes (8): CIR/MRD/DP/19/2010, List of Circulars, List of Communications, MRD/DoP/Dep/Cir-29/2004, MRD/DoP/MAS – OW/16723/2010, Securities and Exchange Board of India, SEBI/MRD/SE/DEP/Cir-4/2005, SMDRP/NSDL/3055/1998

### Community 95 - "validate_golden"
Cohesion: 0.47
Nodes (8): remap(), Doc-id remapping after the 2026-07-25 corpus renumbering (Task 4)., _row(), test_input_rows_are_not_mutated(), test_matching_is_normalization_insensitive(), test_remaps_must_not_cite(), test_remaps_relevant_circulars_and_span_docs(), test_unmapped_rows_untouched()

### Community 96 - "Execution Shell Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 97 - "Canary Shell Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 98 - "Benchmark Artifact Export"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

### Community 99 - "build_report"
Cohesion: 0.31
Nodes (10): build_report(), Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid measurement;…, The headline number must be the 10 pipeline cases alone — the whole point of…, _results(), test_pipeline_metrics_are_not_polluted_by_selector_cases(), test_pooled_overall_carries_no_interval() (+2 more)

### Community 100 - "Refresh Shell Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 101 - "MRR Evaluation"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level. For each query, RR = 1/rank of first…, TestMRR

### Community 102 - "Parsing Latency Measurement"
Cohesion: 0.38
Nodes (4): measure_parsing_latency(), Measure PDF ingestion throughput (chars/sec, ms/PDF). Samples 20 PDFs…, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 103 - "Retrieval Recall Evaluation"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 104 - "Temporal Accuracy Evaluation"
Cohesion: 0.43
Nodes (3): measure_temporal_accuracy(), Measure fraction of as_of queries returning correct pre-supersession circular…, TestTemporalAccuracy

### Community 105 - "As-of Date Testing"
Cohesion: 0.29
Nodes (3): app_module(), fixture, As-of date plumbing in the Spaces UI (app.py).

### Community 106 - "Benchmark Export Testing"
Cohesion: 0.36
Nodes (6): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields(), test_trec_run_and_research_judges_are_sidecar_only()

### Community 107 - "Retrieval Recall Evaluation"
Cohesion: 0.46
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are…, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 108 - "Regulation Edge Construction"
Cohesion: 0.25
Nodes (9): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, derive_regulatory_basis(), Regulatory-basis status of one circular from its resolved regulations.… (+1 more)

### Community 109 - "Benchmark Rescoring"
Cohesion: 0.53
Nodes (5): _fmt(), main(), Path, Re-score archived benchmark runs with bootstrap CIs and paired significance.…, score_run()

### Community 110 - "Automated Research Script"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 111 - "Circular Renumbering Audit"
Cohesion: 0.24
Nodes (9): Pattern, main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), _iso_date(), _labeled_date(), parse_meta(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars. (+1 more)

### Community 112 - "_grounded_prompt"
Cohesion: 0.18
Nodes (11): auroc(), best_threshold(), evaluate(), main(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,…, Calibrate top_k and the abstention threshold against the citation-precision… (+3 more)

### Community 113 - ".encode"
Cohesion: 0.50
Nodes (4): Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge()

### Community 114 - "SEBI Circular Dataset"
Cohesion: 0.67
Nodes (3): Golden v7 Human Packet, SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026, SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122

### Community 115 - "_rejoin_split"
Cohesion: 0.14
Nodes (20): Embedder, Reranker, HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable…, CircularMeta, _CannedGenerator, _distinct_pipeline(), _HallucinatingGenerator (+12 more)

### Community 125 - "_s_mc_no"
Cohesion: 0.20
Nodes (9): contexts_for(), demote_superseded(), Lineage, Down-weight reranked (chunk, score) pairs from superseded circulars and re-…, Connected component over supersedes/superseded_by (both tiers)., The circular in this family that governs on date as_of (ISO), or None when…, test_demote_superseded_puts_in_force_on_top(), test_governing_on_cycle_safe() (+1 more)

### Community 136 - "test_integration_e2e.py"
Cohesion: 0.33
Nodes (4): _ollama_up(), pipeline(), fixture, Step 12 — end-to-end RAG integration test with the REAL stack. bge-m3 (MPS) +…

### Community 137 - "CrossEncoderReranker"
Cohesion: 0.23
Nodes (8): HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo. All classes implement…, External Space first; on ANY failure fall back to the local CPU model.…, Fallback generator: small instruct model via transformers on CPU., Protocol, Reranker, Chunk

### Community 138 - "seed_v7.py"
Cohesion: 0.15
Nodes (10): main(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, main(), Rewrite golden_v7 doc references after the corpus renumbering (2026-07-25…, carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, load_golden() (+2 more)

### Community 139 - "eval_json.py"
Cohesion: 0.17
Nodes (12): build_lineage(), _currency(), mc_topic(), Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None. Used…, Map any cited circular that is superseded -> the circular(s) superseding it.…, superseded_citations(), test_build_lineage_edges_tiered(), test_build_lineage_inferred_master_topic_edge() (+4 more)

### Community 140 - "test_persistence.py"
Cohesion: 0.19
Nodes (7): Chunk, _grounded_prompt(), ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, SubjectSimJudge

### Community 141 - "TestPerQueryRecall"
Cohesion: 0.28
Nodes (10): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge() (+2 more)

### Community 142 - ".query"
Cohesion: 0.27
Nodes (7): Path, _as_bool(), _get(), Central configuration: config.toml defaults, overridden by SEBI_RAG_* env vars., Settings.load() plus the [spaces] table as settings.spaces.*          Load order, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default

### Community 144 - "CrossEncoderReranker"
Cohesion: 0.20
Nodes (8): Build the full pipeline with real models., real_pipeline(), _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker., CrossEncoderReranker, Production reranker: bge-reranker-v2-m3 via sentence-transformers CrossEncoder…, test_compute_kwargs_cpu_disables_fp16(), test_compute_kwargs_mps_keeps_fp16()

### Community 145 - "BGEM3Embedder"
Cohesion: 0.29
Nodes (4): BGEM3Embedder, ndarray, Production dense embedder: BAAI/bge-m3 on Apple Silicon MPS (Step 10)., _tokens()

### Community 146 - "_alias_keys"
Cohesion: 0.29
Nodes (8): _alias_keys(), Candidate alias lookup keys, most literal first. Both the raw normalised form…, PMS/NCS/ILDS end in a literal S. Unconditional plural-stripping mapped them to…, reg_id resolved purely through the alias table, ignoring the corpus., A table key that no _alias_keys() output can produce is dead config., _resolved(), test_acronyms_ending_in_s_reach_their_own_entry(), test_every_alias_entry_is_reachable_from_some_spelling()

### Community 147 - "load_circulars"
Cohesion: 0.38
Nodes (6): load_circulars(), Path, _pipeline(), P1 evaluation-harness test (offline). Loads the real seed corpus…, test_eval_harness_metric_suite(), test_real_corpus_loads_with_provenance_fields()

## Knowledge Gaps
- **46 isolated node(s):** `measure.sh script`, `autoresearch.sh script`, `PYTHONPATH`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RAGPipeline` connect `Reranker Evaluation Harness` to `Evaluation Harness Testing`, `Lexical Reranking and Pooling`, `MRR Evaluation`, `Parsing Latency Measurement`, `Evaluation Metrics Reporting`, `Retrieval Recall Evaluation`, `Temporal Accuracy Evaluation`, `.grounded`, `Benchmark Dataset Generation`, `CrossEncoderReranker`, `Supersession Precision Measurement`, `Temporal Evaluation Runner`, `_rejoin_split`, `API Integration Testing`, `Hugging Face Pipeline`, `Retrieval Metric Evaluation`, `TestReadTrecRun`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `Chunk` connect `CrossEncoderReranker` to `Benchmarking and Indexing`, `Web UI and Demo`, `Benchmark Dataset Generation`, `Hybrid Retrieval Indexing`, `TestPerQueryRecall`, `Contextual Header Generation`, `CrossEncoderReranker`, `load_circulars`, `Hugging Face Pipeline`, `Reranker Evaluation Harness`, `Lexical Reranking and Pooling`, `Configuration and Settings`, `Golden Dataset Validation`, `HyDE Query Expansion`, `Qwen MLX Reranker`, `Document ID Remapping`, `.family`, `Prompt Injection Detection`, `Benchmark Artifact Export`, `Benchmark Export Testing`, `_grounded_prompt`, `_s_mc_no`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `sebi_rag/eval_asof.py` connect `Temporal Evaluation Runner` to `build_report`, `Benchmarking and Indexing`, `Binomial Confidence Intervals`, `Benchmark Uncertainty Quantification`, `test_gate.py`, `Reranker Evaluation Harness`, `_s_mc_no`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `ExtractiveStubGenerator` (e.g. with `get_pipeline()` and `main()`) actually correct?**
  _`ExtractiveStubGenerator` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `HashEmbedder` (e.g. with `_CannedGenerator` and `_SlowGenerator`) actually correct?**
  _`HashEmbedder` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `RAGPipeline` (e.g. with `BenchmarkIssue` and `AsofCaseResult`) actually correct?**
  _`RAGPipeline` has 11 INFERRED edges - model-reasoned connections that need verification._