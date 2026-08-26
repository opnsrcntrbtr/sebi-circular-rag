# Graph Report - SEBI circular RAG  (2026-08-26)

## Corpus Check
- 219 files · ~204,564 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2747 nodes · 5662 edges · 179 communities (140 shown, 39 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 567 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `455facea`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Retrieval Recall Metrics
- Dataset Export Pipeline
- Query Rewriting Logic
- Telemetry and Performance
- Evaluation Benchmarks
- Run Archiving Utilities
- Regulation Scraper
- Evaluation Gate Selection
- Human Annotation Workflow
- Hugging Face Generators
- Regulation Citation Extraction
- Contextual Header Generation
- Regulation Identity Resolution
- Dataset Card Validation
- UI Logic Tests
- Circular Metadata Annotation
- Legacy Run Conversion
- MLX Groundedness Judge
- Regulation Edge Annotation
- Adjudication Protocol Tests
- Domain Filtering Logic
- Export Pipeline Tests
- FastAPI Service Integration
- Annotation Promotion Rules
- As-Of Date Evaluation
- Abstention Gate Tests
- Master Circular Verification
- Query Classification Utilities
- Cohort Measurement Logic
- Label Tier Normalization
- Gemini Adjudication Interface
- Reranker Integration Tests
- Circular Scraper
- Coverage and Cost Probes
- Circular Lineage Model
- Spaces Integration Tests
- Gradio UI Entrypoint
- Lineage and Supersession
- Golden Set Enrichment
- Corpus Validation
- TREC Format Export
- Annotator Agreement Analysis
- Corpus Repair Utilities
- Pipeline Construction
- Local Model Adjudication
- SPLADE Indexing
- Hugging Face Publishing
- PDF Ingestion Validation
- Performance Metrics Reporting
- Chunk Ranking Utilities
- UI Citation Components
- Document Ranking Utilities
- Circular Scraper Tests
- Lightweight Pipeline Components
- Label Provenance Audit
- PDF Recovery Utilities
- NLI Attribution Scoring
- Metric Harness Tests
- End-to-End Integration
- Grounded Generation Judges
- Golden Set Schema
- Local Adjudication Logic
- Text Chunking Utilities
- Regulation Scraper Tests
- Supersession Precision Metrics
- Span Resolution Tests
- Certainty Architecture Tests
- Retrieval Optimization Sweeps
- ZeroGPU Workaround Tests
- Circular Renumbering Audit
- Corpus Validation
- Reranker Benchmarking
- Generator Factory Tests
- PDF Recovery Tests
- Warrant Score Probes
- Text Normalization
- Qwen Reranker Integration
- MRR Evaluation
- Confidence Interval Utilities
- Dataset Hub Upload
- As-Of Report Assembly
- TREC Run Utilities
- Edge Precision Audit
- Retrieval Recall Metrics
- Citation Margin Sweeps
- Token Encoding
- Corpus Text Repair
- Paired Significance Testing
- Operations Server
- MLX Model Generation
- Draft Adjudication Workflow
- Candidate Pool Construction
- Dataset Seeding
- Label Confirmation Logic
- Statistical Uncertainty Analysis
- detect_relations_ex
- Retrieval Failure Tracing
- Regulation Edge Audit
- Incremental Indexing Tests
- Provision Agreement Tests
- Adjudication Error Handling
- Adjudication Logic
- MeasureResult
- Edge Driver Tests
- Canary Monitoring Tests
- stats.py
- Supersession Confidence Metrics
- run_all_metrics
- Context Precision Metrics
- Prompt Injection Scanning
- Regulatory Index Construction
- Regulatory Lineage Mapping
- Retrieval Artifact Tests
- Environment Configuration
- Governing Span Resolution
- is_degenerate
- _alias_keys
- relabel_repooled.py
- Circular Reference Samples
- Citation Faithfulness Scoring
- Runtime Environment Configuration
- Query Reformulation Probing
- measure_temporal_accuracy
- Benchmark Export Utilities
- Regulation Edge Construction
- cohen_kappa
- Environment Refresh Script
- Retrieval Metric Parity
- Project Root
- measure_context_precision
- main
- UI Date Handling
- main
- Index Build Configuration
- Inter-rater Reliability Metrics
- Auto-research Execution Script
- .query
- annotate_corpus
- test_subject_sim_exactly_at_threshold_passes
- Pipeline Evaluation Summary
- New Document Discovery
- test_annotation_adds_no_circular_meta_field
- Golden Dataset Samples
- Label Provenance Analysis
- Hugging Face Deployment
- Discovery Execution Script
- Index Artifact Upload
- test_every_alias_target_is_in_force_or_has_a_succession_entry
- Measurement Execution Script
- Operations Execution Script
- Auto-research Driver Scripts
- Protocol
- Development Environment Script
- Notification Script
- Phoenix Observability Startup
- Auto-research Support Library
- Any
- Test Environment Configuration
- Mutual Fund Master Circulars
- Protocol
- filter_targeted_rows
- detect_relations_ex
- .build
- Derivative Regulations
- Slash Command Optimization
- Document Tracking
- Label Escalation Management
- Regulatory Gap Analysis
- Deployment Requirements
- Golden Dataset Package
- _FixedOrderReranker
- Depository Master Appendix
- SEBI Regulations Directory
- SparseIndex
- TestFrameGuard
- build_golden.py
- _HallucinatingGenerator
- RAGPipeline
- Path

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 65 edges
2. `RAGPipeline` - 52 edges
3. `ExtractiveStubGenerator` - 45 edges
4. `hierarchical_chunk()` - 44 edges
5. `HybridRetriever` - 39 edges
6. `Settings` - 38 edges
7. `HashEmbedder` - 38 edges
8. `answer_with_abstention()` - 34 edges
9. `build_lineage()` - 34 edges
10. `_FakeReranker` - 31 edges

## Surprising Connections (you probably didn't know these)
- `test_sup04_override_generated_via_injected_callable()` --uses--> `HeaderGenerator`  [INFERRED]
  tests/test_select_targeted_headers.py → src/sebi_rag/context_headers.py
- `_chunk()` --uses--> `Chunk`  [INFERRED]
  tests/test_hyde.py → src/sebi_rag/segment.py
- `test_chunks_config_refuses_header_and_maps_fields()` --uses--> `Chunk`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/segment.py
- `test_reg_ids_from_the_fixture_are_unique()` --calls--> `reg_id()`  [INFERRED]
  tests/test_scrape_regulations.py → src/sebi_rag/regulations.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Evaluation Run 2026-08-15** — eval_runs_eval_asof_2026_08_15_pipeline, eval_runs_eval_asof_2026_08_15_selector, eval_runs_eval_asof_2026_08_15_overall [EXTRACTED 1.00]
- **SEBI Regulatory Framework** — tests_fixtures_master_appendix_pre2015_sebi, tests_fixtures_master_appendix_pre2015_circulars, tests_fixtures_master_appendix_pre2015_communications [INFERRED 0.90]

## Communities (179 total, 39 thin omitted)

### Community 0 - "Retrieval Recall Metrics"
Cohesion: 0.11
Nodes (18): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, BenchmarkIssue, per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.      A, validate_golden(), Ten chunks of one circular must not crowd the cutoff: the k applies         to u, TestPerQueryRecall (+10 more)

### Community 1 - "Dataset Export Pipeline"
Cohesion: 0.06
Nodes (66): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+58 more)

### Community 2 - "Query Rewriting Logic"
Cohesion: 0.16
Nodes (26): Re-score `pool` with a rewritten query when `reranked` is below `floor`.…, Fixed rewrite, for tests and for replaying a preregistered rewrite., rescue_pool(), StaticQueryRewriter, _chunk(), _EchoGenerator, _FakeRetriever, _KeywordReranker (+18 more)

### Community 3 - "Telemetry and Performance"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 4 - "Evaluation Benchmarks"
Cohesion: 0.09
Nodes (32): Protocol, Ground truth: what do the 4 CE_MISMATCH rows actually DO in production? The…, Preregistered cohort measurement for the CE paraphrase rescue. Spec:…, What does the 0.05 cross-encoder score floor actually catch?…, Capture-once margin sweep for B' selective citations. One pipeline pass over…, Pool-width sweep (intervention #3): answer-level rescue rate vs reranker…, Benchmark MLX generators on the golden set: faithfulness, groundedness,…, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use -- (+24 more)

### Community 5 - "Run Archiving Utilities"
Cohesion: 0.08
Nodes (40): load_runs(), main(), Path, Assign epochs to the archived runs and write the epoch registry. Every run's…, _fmt(), guard_pair(), main(), Path (+32 more)

### Community 6 - "Regulation Scraper"
Cohesion: 0.23
Nodes (12): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY).…, (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'. Takes the LAST bracket group…, _record() (+4 more)

### Community 7 - "Evaluation Gate Selection"
Cohesion: 0.07
Nodes (43): derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the…, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,…, True iff every floor's metric is present in `report_gate` and meets it. Missing… (+35 more)

### Community 8 - "Human Annotation Workflow"
Cohesion: 0.09
Nodes (39): Random, build_screen(), T-Screen: does the generator follow the citation instruction at all? Spec:…, 50 rows stratified proportionally to golden_v7's eight strata., _apportion(), ingest_packet(), _ingest_to_votes(), main() (+31 more)

### Community 9 - "Hugging Face Generators"
Cohesion: 0.17
Nodes (13): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo. All classes implement…, External Space first; on ANY failure fall back to the local CPU model.…, Primary generator: calls a public LLM Space via gradio_client. Wired to…, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).      Nev (+5 more)

### Community 10 - "Regulation Citation Extraction"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 11 - "Contextual Header Generation"
Cohesion: 0.11
Nodes (22): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), HeaderGenerator, in_scope(), load_headers() (+14 more)

### Community 12 - "Regulation Identity Resolution"
Cohesion: 0.09
Nodes (30): _alias_keys(), load_regulations(), name_tokens(), Path, Candidate alias lookup keys, most literal first. Both the raw normalised form…, Resolve a cited regulation name+year to a canonical reg_id. Returns (reg_id,…, Load data/corpus/regulations.jsonl into a list of regulation records. Thin…, Comparison tokens: lowercased, punctuation-split, stopwords dropped, naively… (+22 more)

### Community 13 - "Dataset Card Validation"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 14 - "UI Logic Tests"
Cohesion: 0.06
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 15 - "Circular Metadata Annotation"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation. Locked…, Validity of one circular from the tiered edge list (any scope: the function…, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 16 - "Legacy Run Conversion"
Cohesion: 0.13
Nodes (14): _extracts(), MLXQueryRewriter, Protocol, query_rewriter_for(), QueryRewriter, Paraphrase rescue for the cross-encoder score floor. Preregistered in…, Factory mirroring `generate.citation_scorer_for`: None when disabled., Rewrites a lay-vocabulary query into statutory vocabulary. Returns None when it… (+6 more)

### Community 17 - "MLX Groundedness Judge"
Cohesion: 0.13
Nodes (20): Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., hierarchical_chunk(), _paragraphs(), Segmentation: hierarchical chunking + metadata + stable citation IDs. Minimal,…, Split into units each <= max_chars. PDF-extracted text often lacks blank-line…, Document -> section -> paragraph chunks with stable IDs. A "section" is…, _chunks(), Index persistence round-trip (offline). (+12 more)

### Community 18 - "Regulation Edge Annotation"
Cohesion: 0.15
Nodes (29): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+21 more)

### Community 19 - "Adjudication Protocol Tests"
Cohesion: 0.12
Nodes (26): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply… (+18 more)

### Community 20 - "Domain Filtering Logic"
Cohesion: 0.10
Nodes (29): _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain.      Cas, The non-SEBI domain filter must match words, not substrings. Shipped 2026-07-30…, Any single-token keyword <= 5 chars is a substring hazard. Embedding it inside…, Query mentioning both SEBI and RBI should NOT abstain — SEBI intent wins., Empty query should not trigger the non-SEBI filter., FEMA keyword in a SEBI context should NOT abstain — SEBI intent wins., The exact query that exposed the bug. (+21 more)

### Community 21 - "Export Pipeline Tests"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 22 - "FastAPI Service Integration"
Cohesion: 0.08
Nodes (18): FastAPI, integration, Lineage, _citation_meta(), create_app(), _CannedGenerator, FastAPI service tests (offline pipelines): endpoints, auth, rate limit,…, /ready should trigger pipeline build and return ready=true. (+10 more)

### Community 23 - "Annotation Promotion Rules"
Cohesion: 0.12
Nodes (27): decide(), Spec sec7 promotion rules for one row. `votes_by_annotator` is this row's votes…, Abstain rows have no explicit claude vote at all (Task 8 never judged them) -…, Both externals independently think something DOES govern (disputing the…, The LLM leg is whichever single non-claude/non-human annotator voted - "qwen"…, Amendment 2026-07-26 (user-approved): the promotion unit is the PROVISION, not…, External marked claude's chunk governing plus extras: claude's label is…, The abstain protocol can never emit non-empty governing (no letters are… (+19 more)

### Community 24 - "As-Of Date Evaluation"
Cohesion: 0.20
Nodes (17): sebi_rag/eval_asof.py, AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Aggregate case results with an exact confidence interval. Pure function of the…, run_pipeline_cases(), run_selector_cases() (+9 more)

### Community 25 - "Abstention Gate Tests"
Cohesion: 0.05
Nodes (57): answer_with_abstention(), _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), v2 protocol: closed-set identification instead of yes/no judgment.     Naming wh, True iff the reply names a valid excerpt number. 'none' or anything     unparsea (+49 more)

### Community 26 - "Master Circular Verification"
Cohesion: 0.19
Nodes (21): sebi_rag/verify_master.py, diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13). Pure functions only:…, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows. (+13 more)

### Community 27 - "Query Classification Utilities"
Cohesion: 0.16
Nodes (19): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any… (+11 more)

### Community 28 - "Cohort Measurement Logic"
Cohesion: 0.05
Nodes (71): _aggregate(), eligible(), main(), _measure(), phase_generate(), phase_report(), B' citation-scorer cohort measurement: control (bge, pointwise) vs J1 (jina, lis, Answerable, non-as_of, with gold citations. Matches warrant_scorer_cohort.py's (+63 more)

### Community 29 - "Label Tier Normalization"
Cohesion: 0.12
Nodes (20): classify_tier(), human_reviewed_ids(), main(), Path, Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.…, Map provenance to the controlled vocabulary. `human_reviewed` (row appears in…, Row ids present in the human labelling packet., Controlled-vocabulary label_tier over golden_v7 (spec A §8.3). (+12 more)

### Community 30 - "Gemini Adjudication Interface"
Cohesion: 0.11
Nodes (23): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec… (+15 more)

### Community 31 - "Reranker Integration Tests"
Cohesion: 0.06
Nodes (31): main(), ADR-004 adoption: calibrate abstain_threshold for jina-reranker-v3-mlx's score s, JinaMLXReranker, Chunk, qwen3_rerank_prompt(), Qwen3MLXReranker, jina-reranker-v3-mlx wrapped to this project's Reranker protocol.      The vendo, ADR-004: the single decision for which model orders the RETRIEVAL pool     (pipe (+23 more)

### Community 32 - "Circular Scraper"
Cohesion: 0.22
Nodes (16): check_robots(), main(), Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, Log-only re-verification that our paths are still crawlable., discover(), fetch(), _listing_url(), looks_like_pdf() (+8 more)

### Community 33 - "Coverage and Cost Probes"
Cohesion: 0.13
Nodes (24): Path, main(), R3 §3.1 — mine cross-reference (A cites B) candidate pairs. Spec:…, _as_bool(), _get(), Settings.load() plus the [spaces] table as settings.spaces.*          Load order, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default (+16 more)

### Community 34 - "Circular Lineage Model"
Cohesion: 0.11
Nodes (32): contexts_for(), demote_superseded(), detect_relations(), Down-weight reranked (chunk, score) pairs from superseded circulars and re-…, Return (relation, referenced_circular) for each distinct reference., _lin_chain(), P2 lineage / supersession resolution tests., OLD_E superseded by an explicit clause; OLD_I only by a title heuristic. (+24 more)

### Community 35 - "Spaces Integration Tests"
Cohesion: 0.15
Nodes (11): _Boom, _Canned, _hybrid(), fixture, HF Spaces path: corpus_spaces loader mapping + HybridGenerator fallback. Fully…, settings(), _stub_rows(), test_chunks_config_refuses_header_and_maps_fields() (+3 more)

### Community 36 - "Gradio UI Entrypoint"
Cohesion: 0.13
Nodes (21): _append_message(), _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_citations_md(), get_pipeline(), _on_submit(), _parse_as_of() (+13 more)

### Community 37 - "Lineage and Supersession"
Cohesion: 0.20
Nodes (10): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —…, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_output_truncated_to_max_chars() (+2 more)

### Community 38 - "Golden Set Enrichment"
Cohesion: 0.21
Nodes (23): Any, beir_corpus_rows(), beir_query_rows(), build_golden_v6(), chunks_by_doc(), dir_fingerprint(), enrich_golden_item(), export_beir() (+15 more)

### Community 39 - "Corpus Validation"
Cohesion: 0.20
Nodes (20): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair. Checks (per…, Every record's text must match the PDF its provenance names. Slow (re-extracts…, validate(), validate_deep(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the document's own… (+12 more)

### Community 40 - "TREC Format Export"
Cohesion: 0.18
Nodes (19): _assert_fixed_tail(), convert_run_dir(), main(), Path, Back-convert archived runfiles into standards-compliant TREC artifacts. The…, Trailing field of the first line; also the whitespace precondition check., read_trec_run assumes qid and tag carry no whitespace. Verify per line., Write run.chunk.trec, run.doc.trec and docids.tsv for one archived run. (+11 more)

### Community 41 - "Annotator Agreement Analysis"
Cohesion: 0.15
Nodes (20): _claude_accuracy_ci(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation…, rid -> annotator -> expected_literal. Kept separate from `_votes_by_row` so…, As `_stratum_kappas`, grouped by label provenance tier rather than task_type.… (+12 more)

### Community 42 - "Corpus Repair Utilities"
Cohesion: 0.12
Nodes (24): Re-derive circular number + dates from each record's stored text and rewrite…, main(), Repair the 6 records whose body text was overwritten with one shared circular's…, _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number() (+16 more)

### Community 43 - "Pipeline Construction"
Cohesion: 0.16
Nodes (27): main(), main(), main(), _load_items(), main(), Path, Build the full pipeline with real models., real_pipeline() (+19 more)

### Community 44 - "Local Model Adjudication"
Cohesion: 0.15
Nodes (19): _extract_text(), Qwen-family models may emit <think>...</think> reasoning as inline text,…, Anthropic Messages response -> reply text: concatenates `text` content blocks,…, _strip_thinking(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external…, Five pilot rows from five strata measure more than five from one - the gemini…, Vote records must say annotator "qwen" (never reuse "gemini" - the agreement… (+11 more)

### Community 45 - "SPLADE Indexing"
Cohesion: 0.06
Nodes (32): RuntimeError, main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), csr_matrix (+24 more)

### Community 46 - "Hugging Face Publishing"
Cohesion: 0.19
Nodes (18): export_golden_v7_arrow(), log(), main(), Path, Run export_datasets.py then add golden_v7 Arrow config., Upload dist/datasets/ to HF dataset repo., Run make index to rebuild FAISS+BM25 before upload., Upload data/index/ to HF index repo. (+10 more)

### Community 47 - "PDF Ingestion Validation"
Cohesion: 0.11
Nodes (21): Pattern, main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), _iso_date(), _labeled_date(), parse_meta(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars. (+13 more)

### Community 48 - "Performance Metrics Reporting"
Cohesion: 0.28
Nodes (5): main(), metrics_to_markdown(), Format results as a markdown table., Unit tests for sebi_rag.measure — automated metric collection., TestCLI

### Community 49 - "Chunk Ranking Utilities"
Cohesion: 0.09
Nodes (38): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+30 more)

### Community 50 - "UI Citation Components"
Cohesion: 0.16
Nodes (17): Human-readable regulation name. Year disambiguates same-short_name repeal pairs…, reg_display_name(), _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_outputs_md(), _parse_as_of(), Return empty markdown placeholder for streaming. (+9 more)

### Community 51 - "Document Ranking Utilities"
Cohesion: 0.15
Nodes (19): annotate_corpus(), Update each corpus record's supersession_status + superseded_by + supersedes…, annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans… (+11 more)

### Community 52 - "Circular Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 53 - "Lightweight Pipeline Components"
Cohesion: 0.11
Nodes (47): Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)…, smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable…, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., build_lineage(), _currency() (+39 more)

### Community 54 - "Label Provenance Audit"
Cohesion: 0.21
Nodes (15): audit(), collect_artifacts(), _ids_from_csv(), _ids_from_dir(), _ids_from_jsonl(), main(), Path, Report what the annotation artifacts can account for, before classifying.… (+7 more)

### Community 55 - "PDF Recovery Utilities"
Cohesion: 0.33
Nodes (7): _add_months(), month_window(), date, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps., resolve_stems(), stem_of()

### Community 56 - "NLI Attribution Scoring"
Cohesion: 0.07
Nodes (33): entailment_index(), NLIAttributionScorer, NLI attribution scoring for B' citation selection. B' asks "does this context…, Index of the entailment class in a model's label map. Read from the checkpoint…, Scores each context by P(entailment) of the answer given that context.…, Wrap an already-constructed cross-encoder (also the test seam)., _softmax(), pick_device() (+25 more)

### Community 57 - "Metric Harness Tests"
Cohesion: 0.30
Nodes (14): _aggregate(), EvalReport, _mean(), report_dict(), run_eval(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-…, _row() (+6 more)

### Community 59 - "Grounded Generation Judges"
Cohesion: 0.14
Nodes (9): Chunk, main(), What actually makes a context window large: chunk size, or chunk count? Read-…, _grounded_prompt(), ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the (+1 more)

### Community 60 - "Golden Set Schema"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden.      `chunks` is optio, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 61 - "Local Adjudication Logic"
Cohesion: 0.19
Nodes (15): Transient-failure predicate for the real Gemini call: rate limiting (429) and…, Same per-row deterministic shuffle as make_packet.py's write_packet:…, _should_retry(), _shuffled_candidates(), _current_model(), main(), pilot(), _pilot_ids() (+7 more)

### Community 62 - "Text Chunking Utilities"
Cohesion: 0.13
Nodes (31): load_circulars(), Path, Path, corpus.load_circulars edge-case coverage. load_circulars reads a JSONL corpus…, Provided optional fields are passed through to CircularMeta., Multiple records produce multiple chunks., Blank lines between records are silently skipped., Malformed JSON raises ValueError (json.loads default). (+23 more)

### Community 64 - "Supersession Precision Metrics"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 65 - "Span Resolution Tests"
Cohesion: 0.19
Nodes (16): main(), mrr(), ndcg_at_k(), Sweep RRF k_const values on the golden set. No index rebuild needed., recall_at_k(), _norm_ws(), Span {doc, quote} -> matching chunk ids (all overlap matches count).      Legacy, resolve_chunk_spans() (+8 more)

### Community 66 - "Certainty Architecture Tests"
Cohesion: 0.67
Nodes (3): faithfulness(), Check that every circular id the answer cites (in square brackets) was     actua, test_faithfulness_scoring()

### Community 67 - "Retrieval Optimization Sweeps"
Cohesion: 0.22
Nodes (13): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and…, Query-side lexical expansion (intervention #2, glossary variant).…, test_all_five_sparse_failure_queries_expand(), test_expanded_sparse_query_hits_statutory_chunk(), test_lay_term_gains_statutory_synonym(), test_multiword_synonym_splits_into_tokens() (+5 more)

### Community 68 - "ZeroGPU Workaround Tests"
Cohesion: 0.14
Nodes (13): app_module(), fixture, Regression coverage for the ZeroGPU-hardware workaround in app.py. Background:…, Inject a fake `spaces` module so app.py's `import spaces` succeeds offline, and…, Static guard: if `import spaces` or the `@spaces.GPU` decorator is ever…, It must stay dead code: calling it would request a real ZeroGPU allocation (and…, The functions actually on the request path (get_pipeline, run_query_stream)…, `hardware:` in README-spaces.md is not a documented Spaces config key (only… (+5 more)

### Community 69 - "Circular Renumbering Audit"
Cohesion: 0.19
Nodes (18): _body(), main(), _mid(), mine_lineage_pairs(), mine_multi_hop(), mine_numeric(), mine_repealed_basis(), Deterministic candidate mining for golden_v7 drafting (spec Sec 4, Sec 5). Pure… (+10 more)

### Community 70 - "Corpus Validation"
Cohesion: 0.20
Nodes (16): chunk_docid(), circular_docid(), MalformedChunkId, Standards-compliant TREC run and qrels emission. The archived runfiles are not…, Raised when an id cannot yield a whitespace-free TREC doc id., Percent-encode whitespace so a circular id is a single TREC field. Reversible…, Map a chunk id to a whitespace-free TREC doc id. `<circular>#<heading with…, Standards-compliant TREC artifact emission (spec A §3-4). (+8 more)

### Community 71 - "Reranker Benchmarking"
Cohesion: 0.16
Nodes (15): cited_docs(), metrics(), auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,… (+7 more)

### Community 72 - "Generator Factory Tests"
Cohesion: 0.16
Nodes (12): eval_generator_for(), The single generator decision for the eval stack.      `derive_thresholds.py` se, The eval stack's generator choice must be one shared decision.…, Uses an injected loader so the test stays offline., Silently falling back to the stub would derive floors under semantics the…, Must assert the factory is CALLED, not merely imported. Verified 2026-08-12 by…, A factory both call is not enough - they must pass the same setting, or the…, test_both_eval_scripts_read_the_same_setting() (+4 more)

### Community 74 - "Warrant Score Probes"
Cohesion: 0.14
Nodes (14): _is_parseable(), _load_screen(), main(), R1 §3.3 degeneracy probe: does the warrant judge return a parseable reply?  Spec, Mirrors generate.parse_warrant_scores' cleaning exactly, but reports     whether, run_answers(), run_judge(), parse_warrant_scores() (+6 more)

### Community 75 - "Text Normalization"
Cohesion: 0.15
Nodes (11): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_fulltext_fallback_returns_earliest_body_reference() (+3 more)

### Community 76 - "Qwen Reranker Integration"
Cohesion: 0.29
Nodes (11): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), test_retrieval_metrics(), _internal(), Prove the internal retrieval metrics are the standard ones. Skips unless the…, _standard() (+3 more)

### Community 77 - "MRR Evaluation"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level. For each query, RR = 1/rank of first…, TestMRR

### Community 78 - "Confidence Interval Utilities"
Cohesion: 0.24
Nodes (4): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 79 - "Dataset Hub Upload"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default:…, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 80 - "As-Of Report Assembly"
Cohesion: 0.31
Nodes (10): build_report(), Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid measurement;…, The headline number must be the 10 pipeline cases alone — the whole point of…, _results(), test_pipeline_metrics_are_not_polluted_by_selector_cases(), test_pooled_overall_carries_no_interval() (+2 more)

### Community 81 - "TREC Run Utilities"
Cohesion: 0.18
Nodes (11): main(), RAGPipeline, smoke_pipeline(), RAGPipeline, Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}., read_trec_run(), run_retrieval_benchmark(), write_trec_run() (+3 more)

### Community 82 - "Edge Precision Audit"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 83 - "Retrieval Recall Metrics"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 84 - "Citation Margin Sweeps"
Cohesion: 0.23
Nodes (13): build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux). Parallel…, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row() (+5 more)

### Community 85 - "Token Encoding"
Cohesion: 0.27
Nodes (10): Rankings, Path, Reverse map `docid -> full chunk id`, so nothing is lost., Valid 6-field TREC run at chunk granularity., write_docids(), _write_lines(), write_run_chunk(), test_docids_maps_docid_back_to_full_chunk_id() (+2 more)

### Community 87 - "Paired Significance Testing"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries. Returns mean_b -…, Randomization p-values use the (count+1)/(n+1) estimator, so a p-value of…, One query flipping out of 56 is exactly the iv9-style verdict: the…, TestPairedDelta

### Community 88 - "Operations Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 89 - "MLX Model Generation"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

### Community 90 - "Draft Adjudication Workflow"
Cohesion: 0.29
Nodes (10): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+2 more)

### Community 91 - "Candidate Pool Construction"
Cohesion: 0.26
Nodes (11): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, One gold doc with `n` chunks that ALL contain the word "broker", so a…, Regression (2026-07-25): a must_contain literal matching many gold-doc chunks…, _retriever(), _saturating_retriever(), test_bm25_leg_uses_raw_query_not_expansion() (+3 more)

### Community 92 - "Dataset Seeding"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 93 - "Label Confirmation Logic"
Cohesion: 0.31
Nodes (8): log(), Margin sweep for B' selective citations on the golden_v7 adjudicated set. One…, run(), One scoring path shared by `eval_json.py` (which measures) and…, Score one golden row through the production-shaped pipeline. Returns per-row…, Per-row records -> metric -> score vector, skipping rows where the metric was…, score_row(), vectors()

### Community 94 - "Statistical Uncertainty Analysis"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 95 - "detect_relations_ex"
Cohesion: 0.33
Nodes (3): DenseIndex, ndarray, FAISS IndexFlatIP over L2-normalized vectors (cosine).

### Community 96 - "Retrieval Failure Tracing"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 97 - "Regulation Edge Audit"
Cohesion: 0.33
Nodes (9): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+1 more)

### Community 98 - "Incremental Indexing Tests"
Cohesion: 0.27
Nodes (9): _doc_checksum(), F3 (ADR-001): encode only new/changed documents; reuse cached embedding rows…, Deterministic per-document checksum over its (enriched) chunk texts — captures…, _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are…, test_incremental_encodes_only_delta() (+1 more)

### Community 99 - "Provision Agreement Tests"
Cohesion: 0.20
Nodes (10): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using the…, Does this external vote confirm claude's label, at PROVISION level? Amendment…, Different chunk copies of the same quoted provision agree at provision level…, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction(), test_provision_agree_disjoint_without_pool_is_false() (+2 more)

### Community 100 - "Adjudication Error Handling"
Cohesion: 0.22
Nodes (10): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt) -> str`…, Scans the per-row cache for `ids` and returns the ones flagged parse_error:…, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct from a well-…, Defensive: an id that was never adjudicated (no cache file at all) is not…, test_adjudicate_marks_parse_error_for_garbled_abstain_protocol_reply() (+2 more)

### Community 101 - "Adjudication Logic"
Cohesion: 0.26
Nodes (11): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions` (keyed by…, Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):…, _same_provision_fixture(), test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only(), test_apply_queue_decision_leaves_row_untouched() (+3 more)

### Community 102 - "MeasureResult"
Cohesion: 0.39
Nodes (3): MeasureReport, MeasureResult, TestDataClasses

### Community 103 - "Edge Driver Tests"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 104 - "Canary Monitoring Tests"
Cohesion: 0.27
Nodes (8): _canary_jscode(), _ops_timeout(), The eval canary must fit its timeout and alert on real regressions. Measured…, n8n gives up first if its budget is smaller, so the ops timeout is never…, A threshold above the healthy value fires every run. citation_precision was…, test_alert_thresholds_sit_below_measured_baselines(), test_n8n_timeout_not_tighter_than_the_ops_budget(), test_ops_timeout_fits_the_measured_runtime()

### Community 105 - "stats.py"
Cohesion: 0.22
Nodes (6): BootstrapCI, PairedResult, ProportionCI, Uncertainty quantification for benchmark runs. The golden set is n=56…, True when the randomization test rejects at 1 - confidence AND the paired…, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 106 - "Supersession Confidence Metrics"
Cohesion: 0.43
Nodes (6): aggregate(), eligible(), main(), measure(), Preregistered cohort measurement for supersession confidence tiering. Spec:…, Answerable, non-as_of, with gold citations: the rows citation metrics exist for.

### Community 107 - "run_all_metrics"
Cohesion: 0.25
Nodes (5): Path, Run all (or specified) metrics sequentially., run_all_metrics(), Empty metrics list is falsy → defaults to ALL_METRICS., TestRegistry

### Community 108 - "Context Precision Metrics"
Cohesion: 0.16
Nodes (9): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict., When torch+MPS available, returns memory stats dict. (+1 more)

### Community 109 - "Prompt Injection Scanning"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 110 - "Regulatory Index Construction"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 111 - "Regulatory Lineage Mapping"
Cohesion: 0.15
Nodes (14): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus., derive_regulatory_basis(), _jaccard(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6). Regulations…, Regulatory-basis status of one circular from its resolved regulations.…, Deterministic, stable identity slug. This is the edge target and join key. (+6 more)

### Community 112 - "Retrieval Artifact Tests"
Cohesion: 0.18
Nodes (7): bench_retrieval must emit valid TREC alongside the legacy runfile., run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so     every, iv9/iv10 build a headered index beside data/index. Without an index     override, ADR-004: benchmarking jina-reranker-v3-mlx against the production     cross-enco, test_bench_retrieval_can_bench_an_alternate_index(), test_bench_retrieval_can_measure_the_reranked_order(), test_bench_retrieval_exposes_and_records_the_reranker_choice()

### Community 113 - "Environment Configuration"
Cohesion: 0.25
Nodes (7): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, SEBI_RAG_EVAL_GENERATOR, canary.sh script, TOKENIZERS_PARALLELISM

### Community 114 - "Governing Span Resolution"
Cohesion: 0.36
Nodes (8): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote} spans, looked…, _resolve_governing_spans(), _pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool(), test_resolve_governing_spans_short_body_uses_whole_body(), test_resolve_governing_spans_uses_first_60_body_chars()

### Community 115 - "is_degenerate"
Cohesion: 0.25
Nodes (8): is_degenerate(), True when `rewritten` is unusable and the rescue should be abandoned.…, parametrize, test_empty_rewrite_is_degenerate(), test_overlong_rewrite_is_degenerate(), test_plausible_rewrite_is_not_degenerate(), test_rewrite_at_the_word_limit_is_accepted(), test_unchanged_rewrite_is_degenerate()

### Community 116 - "_alias_keys"
Cohesion: 0.20
Nodes (9): main(), Emit TREC qrels for an eval set, keyed by its golden_sha256. .venv/bin/python…, Write TREC qrels (`qid 0 docid rel`) at circular level. Binary relevance:…, write_trec_qrels(), test_qrels_excludes_abstain_rows(), test_qrels_expands_relevant_circulars(), test_qrels_has_no_header(), test_qrels_lines_are_four_space_separated_fields() (+1 more)

### Community 117 - "relabel_repooled.py"
Cohesion: 0.31
Nodes (7): call(), main(), _norm(), Does answering a golden_v7 row require a circular the corpus does not hold?…, Uppercase, strip all whitespace — so 'CIR/MIRSD/5/ 2013' matches…, Returns (answer, reasoning). The judge is a reasoning model: the oMLX API…, windows()

### Community 118 - "Circular Reference Samples"
Cohesion: 0.25
Nodes (8): CIR/MRD/DP/19/2010, List of Circulars, List of Communications, MRD/DoP/Dep/Cir-29/2004, MRD/DoP/MAS – OW/16723/2010, Securities and Exchange Board of India, SEBI/MRD/SE/DEP/Cir-4/2005, SMDRP/NSDL/3055/1998

### Community 119 - "Citation Faithfulness Scoring"
Cohesion: 0.60
Nodes (5): pdf_url_for(), scripts/verify_master.py, fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist. Usage:…

### Community 120 - "Runtime Environment Configuration"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 121 - "Query Reformulation Probing"
Cohesion: 0.38
Nodes (6): main(), _pool(), Probe: does query-side reformulation lift the CE score on the 4 CE_MISMATCH…, Return (ce_top, best relevant score, chunk_id of argmax)., Top-8 pool plus every relevant chunk, de-duplicated on chunk_id., _score()

### Community 122 - "measure_temporal_accuracy"
Cohesion: 0.43
Nodes (3): measure_temporal_accuracy(), Measure fraction of as_of queries returning correct pre-supersession circular…, TestTemporalAccuracy

### Community 123 - "Benchmark Export Utilities"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

### Community 124 - "Regulation Edge Construction"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl()

### Community 125 - "cohen_kappa"
Cohesion: 0.33
Nodes (6): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw element is…, test_cohen_kappa_both_constant_and_identical_is_one(), test_cohen_kappa_empty_input_is_one(), test_cohen_kappa_identical_lists_is_one(), test_cohen_kappa_independent_looking_lists_is_low()

### Community 126 - "Environment Refresh Script"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 127 - "Retrieval Metric Parity"
Cohesion: 0.38
Nodes (4): measure_parsing_latency(), Measure PDF ingestion throughput (chars/sec, ms/PDF). Samples 20 PDFs…, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 128 - "Project Root"
Cohesion: 0.29
Nodes (4): Embedder, ndarray, Protocol, _tokens()

### Community 129 - "measure_context_precision"
Cohesion: 0.50
Nodes (3): measure_context_precision(), Fraction of top-k chunks from relevant circulars. Unlike recall@k (which is…, TestContextPrecision

### Community 130 - "main"
Cohesion: 0.67
Nodes (3): is_master(), main(), Is the eval set measuring retrieval, or measuring its own construction? Read-…

### Community 131 - "UI Date Handling"
Cohesion: 0.29
Nodes (3): app_module(), fixture, As-of date plumbing in the Spaces UI (app.py).

### Community 132 - "main"
Cohesion: 0.17
Nodes (22): BaseModel, RAGPipeline, main(), P0 prep: price a larger MLX generator before committing to the R0 upgrade.…, rss_gb(), main(), build_default_pipeline(), CitationMeta (+14 more)

### Community 133 - "Index Build Configuration"
Cohesion: 0.29
Nodes (5): build_index must be able to target a scratch index directory. The iv9/iv10…, A --out flag that is parsed but ignored is worse than none: it reads as safe…, lineage.json lands next to the index it describes; writing it into data/index…, test_build_index_saves_to_the_resolved_out_dir_not_the_constant(), test_lineage_follows_the_out_dir()

### Community 134 - "Inter-rater Reliability Metrics"
Cohesion: 0.29
Nodes (7): gwet_ac1(), Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a prevalence-…, The kappa base-rate paradox: one label dominates, raw agreement is high, yet…, test_gwet_ac1_both_constant_and_identical_is_one(), test_gwet_ac1_empty_input_is_one(), test_gwet_ac1_exceeds_kappa_on_skewed_high_agreement(), test_gwet_ac1_identical_lists_is_one()

### Community 135 - "Auto-research Execution Script"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 136 - ".query"
Cohesion: 0.13
Nodes (12): Answer, Lineage, Path, Map any cited circular that is superseded -> the circular(s) superseding it.…, Connected component over supersedes/superseded_by (both tiers)., The circular in this family that governs on date as_of (ISO), or None when…, superseded_citations(), As-of exclusion or supersession demotion, applied to a reranked list. Extracted… (+4 more)

### Community 137 - "annotate_corpus"
Cohesion: 0.22
Nodes (9): Valid 6-field TREC run collapsed to circular level. Keeps each circular once,…, write_run_doc(), artifacts(), fixture, The encoding must agree across runs and qrels. If a run says…, test_qrels_docids_match_run_doc_docids_exactly(), test_run_doc_dedupes_to_best_rank(), test_run_doc_encodes_space_bearing_circulars() (+1 more)

### Community 139 - "Pipeline Evaluation Summary"
Cohesion: 0.67
Nodes (4): Failure: asof-p2, Overall Evaluation Summary, Pipeline Evaluation Results, Selector Evaluation Results

### Community 142 - "Golden Dataset Samples"
Cohesion: 0.67
Nodes (3): Golden v7 Human Packet, SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026, SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122

### Community 160 - "filter_targeted_rows"
Cohesion: 0.33
Nodes (6): filter_targeted_rows(), Keep only sidecar rows whose chunk belongs to a target document., Selection of targeted headers (iv10): filter iv9's reused headers down to 3…, test_filter_keeps_only_target_doc_rows(), test_filter_with_no_matches_returns_empty(), test_sup04_override_generated_via_injected_callable()

### Community 161 - "detect_relations_ex"
Cohesion: 0.33
Nodes (6): detect_relations_ex(), Like detect_relations, but returns dict records with evidence spans., _window(), A circular that names another circular BEFORE the supersede trigger word must…, test_detect_relations_ex_evidence_and_extractor(), test_detect_relations_ex_supersedes_when_ref_before_trigger()

### Community 162 - ".build"
Cohesion: 0.47
Nodes (5): _chunk(), test_expand_sparse_off_routes_raw_query_to_sparse_leg(), test_retrieve_dense_leg_keeps_raw_query(), test_retrieve_routes_expanded_query_to_sparse_leg(), test_none_and_empty_hyde_are_identical_to_baseline()

### Community 170 - "_FixedOrderReranker"
Cohesion: 0.33
Nodes (4): _FixedOrderReranker, ADR-004: a reranker swap changes ORDER within top-10, which recall@10     (set m, Always returns the SAME doc order regardless of query — deterministic,         s, TestRetrievalBenchmarkNdcg

## Knowledge Gaps
- **51 isolated node(s):** `HF_HUB_DISABLE_XET`, `OMP_NUM_THREADS`, `PYTHONPATH`, `PYTORCH_ENABLE_MPS_FALLBACK`, `SEBI_RAG_EVAL_GENERATOR` (+46 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RAGPipeline` connect `Lightweight Pipeline Components` to `Supersession Precision Metrics`, `measure_context_precision`, `Project Root`, `Query Rewriting Logic`, `Evaluation Benchmarks`, `Reranker Benchmarking`, `.query`, `Pipeline Construction`, `run_all_metrics`, `MRR Evaluation`, `Legacy Run Conversion`, `Retrieval Recall Metrics`, `Citation Margin Sweeps`, `As-Of Date Evaluation`, `Metric Harness Tests`, `measure_temporal_accuracy`, `Label Confirmation Logic`, `Retrieval Metric Parity`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `Chunk` connect `Legacy Run Conversion` to `Query Rewriting Logic`, `Evaluation Benchmarks`, `.query`, `Hugging Face Generators`, `Contextual Header Generation`, `MLX Groundedness Judge`, `Abstention Gate Tests`, `Reranker Integration Tests`, `.build`, `Circular Lineage Model`, `Spaces Integration Tests`, `Lineage and Supersession`, `Pipeline Construction`, `SPLADE Indexing`, `Lightweight Pipeline Components`, `NLI Attribution Scoring`, `Text Chunking Utilities`, `Citation Margin Sweeps`, `MLX Model Generation`, `Incremental Indexing Tests`, `Prompt Injection Scanning`, `Benchmark Export Utilities`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `sebi_rag/eval_asof.py` connect `As-Of Date Evaluation` to `Evaluation Benchmarks`, `.query`, `stats.py`, `Confidence Interval Utilities`, `As-Of Report Assembly`, `Lightweight Pipeline Components`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `Chunk` (e.g. with `dataset_quality()` and `NLIAttributionScorer`) actually correct?**
  _`Chunk` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 41 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `run()`) actually correct?**
  _`RAGPipeline` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `ExtractiveStubGenerator` (e.g. with `get_pipeline()` and `run()`) actually correct?**
  _`ExtractiveStubGenerator` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `HybridRetriever` (e.g. with `main()` and `main()`) actually correct?**
  _`HybridRetriever` has 30 INFERRED edges - model-reasoned connections that need verification._