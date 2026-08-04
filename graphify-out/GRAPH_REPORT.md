# Graph Report - SEBI circular RAG  (2026-08-04)

## Corpus Check
- 166 files · ~168,773 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2070 nodes · 4463 edges · 129 communities (107 shown, 22 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 268 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f7bf7f93`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Dataset Export Pipeline
- Telemetry and Performance
- Human Annotation Management
- lineage.py
- Regulation Lineage Resolution
- test_spaces.py
- sweep_citation_margin.py
- app.py
- Regulation Citation Extraction
- Regulation Edge Annotation
- Dataset Card Validation
- benchmark.py
- load_golden
- Circular Metadata Classification
- context_headers.py
- Lineage
- LLM Adjudication Prompts
- SpladeIndex
- Dataset Export Testing
- sebi_rag/eval_asof.py
- RAGPipeline
- _row
- test_api.py
- backfill_escalations.py
- Gemini Annotation Adjudication
- load_circulars
- Master Circular Verification
- Settings
- .load
- agreement.py
- PDF Ingestion and Renumbering
- extract_misses.py
- Local Model Adjudication
- scrape_regulations.py
- scrape_sebi.py
- .build
- PDF Metadata Parsing
- hierarchical_chunk
- Scraper Logic Testing
- MeasureResult
- test_selective_citations.py
- Statistical and Hardware Helpers
- acquire_missing_pdfs.py
- Export Integration Testing
- Local Annotation Adjudication
- Golden Dataset Validation
- test_hyde.py
- Regulation Scraper Testing
- Decision Promotion Logic
- test_measure.py
- consolidation_edges
- test_expand.py
- ZeroGPU Deployment Testing
- test_golden_v7_gate.py
- _compute_kwargs
- Reference Number Extraction
- Alias Validation Tests
- Qwen MLX Reranker
- clopper_pearson_ci
- main
- Dataset Hub Upload
- UI Query Submission
- Regulation Edge Auditing
- UI Logic Testing
- answer_with_abstention
- Corpus Text Repair
- eval_harness.py
- paired_delta
- Operations Server
- Regulation Edge Audit
- Draft Row Adjudication
- test_acquire_missing.py
- stats.py
- run_all_metrics
- Retrieval Failure Tracing
- _pool
- _provision_agree
- Adjudication Error Handling
- Supersession Precision Measurement
- Regulation Edge Testing
- discover_new.py
- .grounded
- Embedder
- Prompt Injection Detection
- Regulatory Basis Indexing
- resolve_chunk_spans
- Inter-Annotator Agreement
- measure.py
- TestReadTrecRun
- Circular Reference Examples
- Execution Shell Scripts
- Canary Shell Scripts
- build_report
- Refresh Shell Scripts
- MRR Evaluation
- Parsing Latency Measurement
- Retrieval Recall Evaluation
- Temporal Accuracy Evaluation
- As-of Date Testing
- Benchmark Export Testing
- test_incremental_index.py
- Regulation Edge Construction
- Benchmark Rescoring
- Automated Research Script
- Circular Renumbering Audit
- _unique
- SEBI Circular Dataset
- ExtractiveStubGenerator
- Hugging Face Deployment
- Discovery Execution Script
- Index Upload Utilities
- Measurement Execution Script
- Operations Execution Script
- Notification Script
- Phoenix Service Startup
- Test Environment Configuration
- Mutual Fund Master Appendix
- SEBI Master Circulars
- Slash Command Optimization
- Circular ID Tracking
- Escalation Labeling
- Unresolved Regulation Tracking
- HF Spaces Requirements
- Golden Dataset Initialization
- Depository Master Appendix
- SEBI Regulation Listings
- seed_v7.py
- Chunk
- test_gate.py

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 90 edges
2. `RAGPipeline` - 57 edges
3. `hierarchical_chunk()` - 45 edges
4. `ExtractiveStubGenerator` - 44 edges
5. `HashEmbedder` - 42 edges
6. `CircularMeta` - 39 edges
7. `Lineage` - 33 edges
8. `build_lineage()` - 32 edges
9. `LexicalReranker` - 29 edges
10. `MeasureResult` - 26 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `get_pipeline()` --calls--> `build_spaces_pipeline()`  [INFERRED]
  app.py → src/sebi_rag/api_spaces.py
- `get_pipeline()` --calls--> `ExtractiveStubGenerator`  [INFERRED]
  app.py → src/sebi_rag/generate.py
- `run_query_spaces()` --calls--> `_citation_meta()`  [INFERRED]
  app.py → src/sebi_rag/api.py
- `test_candidate_miss_when_relevant_doc_absent()` --calls--> `classify_query()`  [INFERRED]
  tests/test_extract_misses.py → scripts/analysis/extract_misses.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **SEBI Regulatory Framework** — tests_fixtures_master_appendix_pre2015_sebi, tests_fixtures_master_appendix_pre2015_circulars, tests_fixtures_master_appendix_pre2015_communications [INFERRED 0.90]

## Communities (129 total, 22 thin omitted)

### Community 0 - "Dataset Export Pipeline"
Cohesion: 0.06
Nodes (70): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+62 more)

### Community 1 - "Telemetry and Performance"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 2 - "Human Annotation Management"
Cohesion: 0.07
Nodes (52): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+44 more)

### Community 3 - "lineage.py"
Cohesion: 0.08
Nodes (32): Capture-once margin sweep for B' selective citations. One pipeline pass over…, Benchmark MLX generators on the golden set: faithfulness, groundedness,…, F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, Retrieval-only benchmark with TREC runfile and reproducibility metadata. Use…, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped…, Build the dense+sparse index once and persist it (run after corpus changes).…, Calibrate top_k and the abstention threshold against the citation-precision…, scripts/eval_asof.py (+24 more)

### Community 4 - "Regulation Lineage Resolution"
Cohesion: 0.06
Nodes (45): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus., _alias_keys(), derive_regulatory_basis(), _jaccard(), load_regulations(), name_tokens() (+37 more)

### Community 5 - "test_spaces.py"
Cohesion: 0.12
Nodes (23): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo. All classes implement…, External Space first; on ANY failure fall back to the local CPU model.…, Primary generator: calls a public LLM Space via gradio_client. Wired to…, Fallback generator: small instruct model via transformers on CPU., Central configuration: config.toml defaults, overridden by SEBI_RAG_* env vars.… (+15 more)

### Community 6 - "sweep_citation_margin.py"
Cohesion: 0.27
Nodes (9): log(), Margin sweep for B' selective citations on the golden_v7 adjudicated set. One…, run(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, One scoring path shared by `eval_json.py` (which measures) and…, Score one golden row through the production-shaped pipeline. Returns per-row…, Per-row records -> metric -> score vector, skipping rows where the metric was…, score_row() (+1 more)

### Community 7 - "app.py"
Cohesion: 0.27
Nodes (9): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only). Gradio SDK…, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict ISO YYYY-…, run_query_spaces(), warm_up_gpu() (+1 more)

### Community 8 - "Regulation Citation Extraction"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 9 - "Regulation Edge Annotation"
Cohesion: 0.14
Nodes (31): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+23 more)

### Community 10 - "Dataset Card Validation"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 11 - "benchmark.py"
Cohesion: 0.18
Nodes (24): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), dir_fingerprint(), enrich_golden_item() (+16 more)

### Community 12 - "load_golden"
Cohesion: 0.14
Nodes (18): Build the full pipeline with real models., real_pipeline(), main(), main(), main(), main(), load_golden(), Path (+10 more)

### Community 13 - "Circular Metadata Classification"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation. Locked…, Validity of one circular from the tiered edge list (any scope: the function…, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 14 - "context_headers.py"
Cohesion: 0.08
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 15 - "Lineage"
Cohesion: 0.07
Nodes (38): contexts_for(), annotate_corpus(), build_lineage(), _currency(), demote_superseded(), detect_relations(), Lineage, mc_topic() (+30 more)

### Community 16 - "LLM Adjudication Prompts"
Cohesion: 0.12
Nodes (26): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply… (+18 more)

### Community 17 - "SpladeIndex"
Cohesion: 0.07
Nodes (28): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.…, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+20 more)

### Community 18 - "Dataset Export Testing"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 19 - "sebi_rag/eval_asof.py"
Cohesion: 0.21
Nodes (14): sebi_rag/eval_asof.py, AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Aggregate case results with an exact confidence interval. Pure function of the…, run_pipeline_cases(), run_selector_cases() (+6 more)

### Community 20 - "RAGPipeline"
Cohesion: 0.19
Nodes (21): BaseModel, build_default_pipeline(), CitationMeta, QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline. Run (real stack; loads the…, RegulationRef, RegulationSuccessor (+13 more)

### Community 21 - "_row"
Cohesion: 0.13
Nodes (25): decide(), Spec sec7 promotion rules for one row. `votes_by_annotator` is this row's votes…, Abstain rows have no explicit claude vote at all (Task 8 never judged them) -…, Both externals independently think something DOES govern (disputing the…, The LLM leg is whichever single non-claude/non-human annotator voted - "qwen"…, External marked claude's chunk governing plus extras: claude's label is…, The abstain protocol can never emit non-empty governing (no letters are…, Two externals both replying NONE on an answerable row must queue, not flip: a… (+17 more)

### Community 22 - "test_api.py"
Cohesion: 0.08
Nodes (17): FastAPI, integration, _citation_meta(), create_app(), _CannedGenerator, FastAPI service tests (offline pipelines): endpoints, auth, rate limit,…, /ready should trigger pipeline build and return ready=true., _SlowGenerator (+9 more)

### Community 23 - "backfill_escalations.py"
Cohesion: 0.09
Nodes (38): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+30 more)

### Community 24 - "Gemini Annotation Adjudication"
Cohesion: 0.11
Nodes (23): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec… (+15 more)

### Community 25 - "load_circulars"
Cohesion: 0.29
Nodes (6): load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., P1 evaluation-harness test (offline). Loads the real seed corpus…, test_eval_harness_metric_suite(), test_real_corpus_loads_with_provenance_fields()

### Community 26 - "Master Circular Verification"
Cohesion: 0.19
Nodes (21): sebi_rag/verify_master.py, diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13). Pure functions only:…, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows. (+13 more)

### Community 27 - "Settings"
Cohesion: 0.24
Nodes (14): build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux). Parallel…, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row() (+6 more)

### Community 28 - ".load"
Cohesion: 0.21
Nodes (17): _as_bool(), _get(), Path, Settings.load() plus the [spaces] table as settings.spaces.* Load order per…, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default may…, _clear(), Settings: defaults, config.toml, and env-override precedence. (+9 more)

### Community 29 - "agreement.py"
Cohesion: 0.14
Nodes (20): _claude_accuracy_ci(), gwet_ac1(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation…, Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a prevalence-… (+12 more)

### Community 30 - "PDF Ingestion and Renumbering"
Cohesion: 0.15
Nodes (19): Re-derive circular number + dates from each record's stored text and rewrite…, _existing_numbers(), extract_text(), ingest(), main(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars. Drop a circular PDF into data/raw/ and… (+11 more)

### Community 31 - "extract_misses.py"
Cohesion: 0.14
Nodes (23): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any… (+15 more)

### Community 32 - "Local Model Adjudication"
Cohesion: 0.15
Nodes (19): _extract_text(), Qwen-family models may emit <think>...</think> reasoning as inline text,…, Anthropic Messages response -> reply text: concatenates `text` content blocks,…, _strip_thinking(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external…, Five pilot rows from five strata measure more than five from one - the gemini…, Vote records must say annotator "qwen" (never reuse "gemini" - the agreement… (+11 more)

### Community 33 - "scrape_regulations.py"
Cohesion: 0.20
Nodes (14): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY).…, (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'. Takes the LAST bracket group…, _record() (+6 more)

### Community 34 - "scrape_sebi.py"
Cohesion: 0.26
Nodes (14): discover(), _listing_url(), main(), _page(), _parse_date(), parse_rows(), pdf_url_for(), date (+6 more)

### Community 35 - ".build"
Cohesion: 0.14
Nodes (18): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, _chunk(), test_retrieve_dense_leg_keeps_raw_query(), test_retrieve_routes_expanded_query_to_sparse_leg(), One gold doc with `n` chunks that ALL contain the word "broker", so a…, Regression (2026-07-25): a must_contain literal matching many gold-doc chunks… (+10 more)

### Community 36 - "PDF Metadata Parsing"
Cohesion: 0.15
Nodes (17): Pattern, _iso_date(), _labeled_date(), parse_meta(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash… (+9 more)

### Community 37 - "hierarchical_chunk"
Cohesion: 0.16
Nodes (18): hierarchical_chunk(), _paragraphs(), Split into units each <= max_chars. PDF-extracted text often lacks blank-line…, Document -> section -> paragraph chunks with stable IDs. A "section" is…, test_numeric_miner_requires_numeric_pattern(), test_paraphrase_skips_preamble_and_short_chunks(), _body(), Chunker (segment.hierarchical_chunk) behaviour. Regression guard for the "5.… (+10 more)

### Community 38 - "Scraper Logic Testing"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 39 - "MeasureResult"
Cohesion: 0.24
Nodes (6): measure_context_precision(), MeasureReport, MeasureResult, Fraction of top-k chunks from relevant circulars. Unlike recall@k (which is…, TestContextPrecision, TestDataClasses

### Community 40 - "test_selective_citations.py"
Cohesion: 0.15
Nodes (19): Context ids the answer rests on. Scores each context's answer-relevance via…, select_citations(), _chunk(), _FakeReranker, Tests for B' selective citations: select_citations() and its integration., Deterministic scorer: returns preset answer-relevance scores, sorted desc., When citation_scorer_enabled=True, Settings loads a non-None scorer., When citation_scorer_enabled=False, Settings loads scorer disabled. (+11 more)

### Community 41 - "Statistical and Hardware Helpers"
Cohesion: 0.15
Nodes (10): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Path, Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict. (+2 more)

### Community 42 - "acquire_missing_pdfs.py"
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

### Community 46 - "test_hyde.py"
Cohesion: 0.18
Nodes (10): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —…, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_output_truncated_to_max_chars() (+2 more)

### Community 48 - "Decision Promotion Logic"
Cohesion: 0.21
Nodes (14): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions` (keyed by…, _min_agreement_fixture(), Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):…, _same_provision_fixture(), test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only() (+6 more)

### Community 49 - "test_measure.py"
Cohesion: 0.28
Nodes (5): main(), metrics_to_markdown(), Format results as a markdown table., Unit tests for sebi_rag.measure — automated metric collection., TestCLI

### Community 50 - "consolidation_edges"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans…, _master(), test_annotate_idempotent() (+7 more)

### Community 51 - "test_expand.py"
Cohesion: 0.08
Nodes (26): main(), mrr(), ndcg_at_k(), Sweep RRF k_const values on the golden set. No index rebuild needed., recall_at_k(), expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and… (+18 more)

### Community 52 - "ZeroGPU Deployment Testing"
Cohesion: 0.14
Nodes (13): app_module(), fixture, Regression coverage for the ZeroGPU-hardware workaround in app.py. Background:…, Inject a fake `spaces` module so app.py's `import spaces` succeeds offline, and…, Static guard: if `import spaces` or the `@spaces.GPU` decorator is ever…, It must stay dead code: calling it would request a real ZeroGPU allocation (and…, The functions actually on the request path (get_pipeline, run_query_spaces)…, `hardware:` in README-spaces.md is not a documented Spaces config key (only… (+5 more)

### Community 53 - "test_golden_v7_gate.py"
Cohesion: 0.09
Nodes (33): derive_floors(), metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the…, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,…, True iff every floor's metric is present in `report_gate` and meets it. Missing…, select_golden() (+25 more)

### Community 54 - "_compute_kwargs"
Cohesion: 0.15
Nodes (15): _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker., pick_device(), Device + precision selection for Apple-Silicon inference. Centralizes the…, Resolve the compute device. A truthy explicit `pref` ("mps"/"cpu"/"cuda") wins.…, fp16 only on GPU-class devices; never on cpu. bf16 is never returned here by…, should_use_fp16(), test_compute_kwargs_cpu_disables_fp16() (+7 more)

### Community 55 - "Reference Number Extraction"
Cohesion: 0.15
Nodes (11): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_fulltext_fallback_returns_earliest_body_reference() (+3 more)

### Community 57 - "Qwen MLX Reranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 58 - "clopper_pearson_ci"
Cohesion: 0.24
Nodes (4): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 59 - "main"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

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

### Community 64 - "answer_with_abstention"
Cohesion: 0.19
Nodes (13): answer_with_abstention(), _is_non_sebi_domain(), Max cosine(query, doc subject line) over contexts — the primary gate signal,…, Max cosine(query, section heading) over contexts — the second tier., Return True if the query clearly targets a non-SEBI regulator's domain. Uses…, _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons,…, test_advisory_draft_on_gate_failure_only_when_requested() (+5 more)

### Community 65 - "Corpus Text Repair"
Cohesion: 0.18
Nodes (7): main(), Repair the 6 records whose body text was overwritten with one shared circular's…, normalize_circular_number(), Canonical COMPARISON key for a circular number: strip whitespace and trailing…, test_dedup_uses_normalized_numbers(), The repair map must name a real orphan PDF that parses to the circular_number…, test_numbers_normalize_distinctly()

### Community 66 - "eval_harness.py"
Cohesion: 0.28
Nodes (15): _aggregate(), EvalReport, _mean(), Golden-set evaluation harness (P1). Runs the pipeline over a labelled golden…, report_dict(), run_eval(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-… (+7 more)

### Community 67 - "paired_delta"
Cohesion: 0.19
Nodes (7): paired_delta(), PairedResult, Compare run `b` against run `a` on their shared queries. Returns mean_b -…, True when the randomization test rejects at 1 - confidence AND the paired…, Randomization p-values use the (count+1)/(n+1) estimator, so a p-value of…, One query flipping out of 56 is exactly the iv9-style verdict: the…, TestPairedDelta

### Community 69 - "Operations Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 70 - "Regulation Edge Audit"
Cohesion: 0.29
Nodes (10): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+2 more)

### Community 71 - "Draft Row Adjudication"
Cohesion: 0.29
Nodes (10): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+2 more)

### Community 73 - "stats.py"
Cohesion: 0.19
Nodes (7): bootstrap_ci(), BootstrapCI, Uncertainty quantification for benchmark runs. The golden set is n=56…, Percentile bootstrap interval for the mean of per-query scores., Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests)., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 74 - "run_all_metrics"
Cohesion: 0.29
Nodes (4): Run all (or specified) metrics sequentially., run_all_metrics(), Empty metrics list is falsy → defaults to ALL_METRICS., TestRegistry

### Community 75 - "Retrieval Failure Tracing"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 76 - "_pool"
Cohesion: 0.27
Nodes (10): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote} spans, looked…, _resolve_governing_spans(), _pool(), Amendment 2026-07-26 (user-approved): the promotion unit is the PROVISION, not…, test_decide_same_provision_other_chunk_promotes_with_pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool() (+2 more)

### Community 77 - "_provision_agree"
Cohesion: 0.20
Nodes (10): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using the…, Does this external vote confirm claude's label, at PROVISION level? Amendment…, Different chunk copies of the same quoted provision agree at provision level…, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction(), test_provision_agree_disjoint_without_pool_is_false() (+2 more)

### Community 79 - "Adjudication Error Handling"
Cohesion: 0.22
Nodes (10): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt) -> str`…, Scans the per-row cache for `ids` and returns the ones flagged parse_error:…, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct from a well-…, Defensive: an id that was never adjudicated (no cache file at all) is not…, test_adjudicate_marks_parse_error_for_garbled_abstain_protocol_reply() (+2 more)

### Community 80 - "Supersession Precision Measurement"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 81 - "Regulation Edge Testing"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 83 - ".grounded"
Cohesion: 0.15
Nodes (11): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), v2 protocol: closed-set identification instead of yes/no judgment. Naming which…, True iff the reply names a valid excerpt number. 'none' or anything unparseable…, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the gate… (+3 more)

### Community 84 - "Embedder"
Cohesion: 0.33
Nodes (4): Embedder, ndarray, Protocol, _tokens()

### Community 85 - "Prompt Injection Detection"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 86 - "Regulatory Basis Indexing"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 88 - "resolve_chunk_spans"
Cohesion: 0.27
Nodes (13): chunks_by_doc(), _norm_ws(), qrels_rows(), Span {doc, quote} -> matching chunk ids (all overlap matches count). Legacy…, resolve_chunk_spans(), _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row() (+5 more)

### Community 89 - "Inter-Annotator Agreement"
Cohesion: 0.25
Nodes (8): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw element is…, The kappa base-rate paradox: one label dominates, raw agreement is high, yet…, test_cohen_kappa_both_constant_and_identical_is_one(), test_cohen_kappa_empty_input_is_one(), test_cohen_kappa_identical_lists_is_one(), test_cohen_kappa_independent_looking_lists_is_low(), test_gwet_ac1_exceeds_kappa_on_skewed_high_agreement()

### Community 91 - "measure.py"
Cohesion: 0.19
Nodes (12): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), detect_relations_ex(), Like detect_relations, but returns dict records with evidence spans., _window(), Automated metric collection for the SEBI Circular RAG pipeline. Six on-demand… (+4 more)

### Community 92 - "TestReadTrecRun"
Cohesion: 0.36
Nodes (4): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), The archived runfiles embed section headings in the doc id., TestReadTrecRun

### Community 94 - "Circular Reference Examples"
Cohesion: 0.25
Nodes (8): CIR/MRD/DP/19/2010, List of Circulars, List of Communications, MRD/DoP/Dep/Cir-29/2004, MRD/DoP/MAS – OW/16723/2010, Securities and Exchange Board of India, SEBI/MRD/SE/DEP/Cir-4/2005, SMDRP/NSDL/3055/1998

### Community 96 - "Execution Shell Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 97 - "Canary Shell Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

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

### Community 107 - "test_incremental_index.py"
Cohesion: 0.46
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are…, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 108 - "Regulation Edge Construction"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl()

### Community 109 - "Benchmark Rescoring"
Cohesion: 0.53
Nodes (5): _fmt(), main(), Path, Re-score archived benchmark runs with bootstrap CIs and paired significance.…, score_run()

### Community 110 - "Automated Research Script"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 111 - "Circular Renumbering Audit"
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 112 - "_unique"
Cohesion: 0.15
Nodes (15): cited_docs(), metrics(), auroc(), best_threshold(), evaluate(), P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,…, evaluate() (+7 more)

### Community 114 - "SEBI Circular Dataset"
Cohesion: 0.67
Nodes (3): Golden v7 Human Packet, SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026, SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122

### Community 115 - "ExtractiveStubGenerator"
Cohesion: 0.11
Nodes (42): Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)…, smoke_pipeline(), smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable…, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., LexicalReranker (+34 more)

### Community 138 - "seed_v7.py"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 140 - "Chunk"
Cohesion: 0.15
Nodes (6): Generator, _grounded_prompt(), Judge, Protocol, F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and the…, Chunk

### Community 141 - "test_gate.py"
Cohesion: 0.28
Nodes (10): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge() (+2 more)

## Knowledge Gaps
- **46 isolated node(s):** `measure.sh script`, `autoresearch.sh script`, `PYTHONPATH`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `lineage.py`, `test_spaces.py`, `benchmark.py`, `load_golden`, `test_gate.py`, `context_headers.py`, `Lineage`, `SpladeIndex`, `RAGPipeline`, `load_circulars`, `Settings`, `.build`, `hierarchical_chunk`, `test_selective_citations.py`, `Golden Dataset Validation`, `test_hyde.py`, `test_expand.py`, `Qwen MLX Reranker`, `main`, `answer_with_abstention`, `.grounded`, `Prompt Injection Detection`, `resolve_chunk_spans`, `Benchmark Export Testing`, `ExtractiveStubGenerator`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `lineage.py`, `sweep_citation_margin.py`, `benchmark.py`, `load_golden`, `Chunk`, `Lineage`, `sebi_rag/eval_asof.py`, `test_api.py`, `Settings`, `MeasureResult`, `eval_harness.py`, `run_all_metrics`, `Supersession Precision Measurement`, `Embedder`, `measure.py`, `TestReadTrecRun`, `MRR Evaluation`, `Parsing Latency Measurement`, `Retrieval Recall Evaluation`, `Temporal Accuracy Evaluation`, `_unique`, `ExtractiveStubGenerator`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `sebi_rag/eval_asof.py` connect `sebi_rag/eval_asof.py` to `build_report`, `lineage.py`, `stats.py`, `Lineage`, `RAGPipeline`, `clopper_pearson_ci`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `CitationMeta`) actually correct?**
  _`RAGPipeline` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `ExtractiveStubGenerator` (e.g. with `get_pipeline()` and `main()`) actually correct?**
  _`ExtractiveStubGenerator` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `HashEmbedder` (e.g. with `_CannedGenerator` and `_SlowGenerator`) actually correct?**
  _`HashEmbedder` has 10 INFERRED edges - model-reasoned connections that need verification._