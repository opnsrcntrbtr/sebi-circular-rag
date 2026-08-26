# Graph Report - SEBI circular RAG  (2026-08-26)

## Corpus Check
- 224 files · ~209,037 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2782 nodes · 5880 edges · 166 communities (137 shown, 29 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 602 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `02a0ad0b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- per_query_recall
- export_datasets.py
- test_paraphrase_rescue.py
- Telemetry and Performance
- generate.py
- Run Archiving Utilities
- test_conformal.py
- test_golden_v7_gate.py
- Human Annotation Workflow
- SpacesSettings
- Regulation Citation Extraction
- Contextual Header Generation
- Regulation Identity Resolution
- Dataset Card Validation
- UI Logic Tests
- derive_validity
- Chunk
- test_spaces.py
- Regulation Edge Annotation
- test_golden_v7_gemini.py
- Domain Filtering Logic
- Export Pipeline Tests
- api.py
- Annotation Promotion Rules
- build_report
- test_gate.py
- Master Circular Verification
- Query Classification Utilities
- test_selective_citations.py
- Label Tier Normalization
- gemini_adjudicate.py
- test_rerank_jina_v3.py
- RAGPipeline
- Settings
- test_lineage.py
- test_export_integration.py
- Gradio UI Entrypoint
- sweep_rrf_k.py
- benchmark.py
- Corpus Validation
- ValueError
- agreement.py
- ingest_pdf.py
- HybridRetriever
- Local Model Adjudication
- SpladeIndex
- Hugging Face Publishing
- parse_meta
- MeasureResult
- backfill_escalations.py
- UI Citation Components
- write_dataset_cards
- Circular Scraper Tests
- Lineage
- Label Provenance Audit
- Qwen3MLXReranker
- NLI Attribution Scoring
- test_eval_harness_v7.py
- retrieve.py
- QueryRewriter
- Golden Set Schema
- local_adjudicate.py
- test_corpus.py
- Regulation Scraper Tests
- Supersession Precision Metrics
- resolve_chunk_spans
- .grounded
- WarrantJudge
- ZeroGPU Workaround Tests
- answer_with_abstention
- apply
- _unique
- Generator Factory Tests
- run_all_metrics
- run_judge
- test_ingest_refs.py
- measure.py
- MRR Evaluation
- Confidence Interval Utilities
- Dataset Hub Upload
- main
- read_trec_run
- Edge Precision Audit
- Retrieval Recall Metrics
- corpus_spaces.py
- test_context_recall.py
- scrape_regulations.py
- stats.py
- Operations Server
- test_benchmark.py
- adjudicate_draft.py
- test_golden_v7_pool.py
- Dataset Seeding
- scrape_sebi.py
- bootstrap_ci
- validate_corpus.py
- Retrieval Failure Tracing
- Regulation Edge Audit
- test_integration_e2e.py
- _provision_agree
- adjudicate
- main
- acquire_missing_pdfs.py
- Edge Driver Tests
- Canary Monitoring Tests
- sebi_rag/eval_asof.py
- main
- test_repair_corpus_text.py
- _bootstrap_ci
- Prompt Injection Scanning
- Regulatory Index Construction
- Regulatory Lineage Mapping
- Retrieval Artifact Tests
- Environment Configuration
- Governing Span Resolution
- main
- build_chunk_rows
- checks.sh
- Circular Reference Samples
- .encode
- Runtime Environment Configuration
- Query Reformulation Probing
- measure_temporal_accuracy
- Benchmark Export Utilities
- measure_context_precision
- test_golden_v7_agreement.py
- Environment Refresh Script
- measure_parsing_latency
- .load_spaces
- main
- discover_new.py
- UI Date Handling
- SubjectSimJudge
- Index Build Configuration
- _compute_kwargs
- Auto-research Execution Script
- build_citation_pairs
- test_acquire_missing.py
- faithfulness
- Pipeline Evaluation Summary
- _as_bool
- sebi-rag
- Golden Dataset Samples
- Label Provenance Analysis
- Hugging Face Deployment
- Discovery Execution Script
- Index Artifact Upload
- Measurement Execution Script
- Operations Execution Script
- Auto-research Driver Scripts
- Development Environment Script
- Notification Script
- Phoenix Observability Startup
- Auto-research Support Library
- Test Environment Configuration
- Mutual Fund Master Circulars
- main
- Derivative Regulations
- Slash Command Optimization
- Document Tracking
- Label Escalation Management
- Regulatory Gap Analysis
- Deployment Requirements
- Depository Master Appendix
- SEBI Regulations Directory

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 114 edges
2. `RAGPipeline` - 61 edges
3. `Settings` - 49 edges
4. `ExtractiveStubGenerator` - 46 edges
5. `HybridRetriever` - 46 edges
6. `hierarchical_chunk()` - 46 edges
7. `HashEmbedder` - 43 edges
8. `load_golden()` - 38 edges
9. `build_lineage()` - 38 edges
10. `build_default_pipeline()` - 33 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py
- `_chunk()` --uses--> `Chunk`  [INFERRED]
  tests/test_hyde.py → src/sebi_rag/segment.py
- `test_chunks_config_refuses_header_and_maps_fields()` --uses--> `Chunk`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/segment.py
- `get_pipeline()` --calls--> `build_spaces_pipeline()`  [INFERRED]
  app.py → src/sebi_rag/api_spaces.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Evaluation Run 2026-08-15** — eval_runs_eval_asof_2026_08_15_pipeline, eval_runs_eval_asof_2026_08_15_selector, eval_runs_eval_asof_2026_08_15_overall [EXTRACTED 1.00]
- **SEBI Regulatory Framework** — tests_fixtures_master_appendix_pre2015_sebi, tests_fixtures_master_appendix_pre2015_circulars, tests_fixtures_master_appendix_pre2015_communications [INFERRED 0.90]

## Communities (166 total, 29 thin omitted)

### Community 0 - "per_query_recall"
Cohesion: 0.11
Nodes (17): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, BenchmarkIssue, per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.…, validate_golden(), Ten chunks of one circular must not crowd the cutoff: the k applies to unique…, Answerable-but-unjudged rows are excluded from metrics, never scored 0.… (+9 more)

### Community 1 - "export_datasets.py"
Cohesion: 0.16
Nodes (30): build_eval_rows(), build_lineage_rows(), build_supersession_pairs(), _config_entry(), _emit(), export_all(), export_chunks(), export_citation_normalization() (+22 more)

### Community 2 - "test_paraphrase_rescue.py"
Cohesion: 0.11
Nodes (35): is_degenerate(), Paraphrase rescue for the cross-encoder score floor. Preregistered in…, Re-score `pool` with a rewritten query when `reranked` is below `floor`.…, Fixed rewrite, for tests and for replaying a preregistered rewrite., True when `rewritten` is unusable and the rescue should be abandoned.…, rescue_pool(), StaticQueryRewriter, _chunk() (+27 more)

### Community 3 - "Telemetry and Performance"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 4 - "generate.py"
Cohesion: 0.06
Nodes (47): Ground truth: what do the 4 CE_MISMATCH rows actually DO in production? The…, Preregistered cohort measurement for the CE paraphrase rescue. Spec:…, What does the 0.05 cross-encoder score floor actually catch?…, Capture-once margin sweep for B' selective citations. One pipeline pass over…, log(), Margin sweep for B' selective citations on the golden_v7 adjudicated set. One…, run(), Benchmark MLX generators on the golden set: faithfulness, groundedness,… (+39 more)

### Community 5 - "Run Archiving Utilities"
Cohesion: 0.07
Nodes (42): load_runs(), main(), Path, Assign epochs to the archived runs and write the epoch registry. Every run's…, _fmt(), guard_pair(), main(), Path (+34 more)

### Community 6 - "test_conformal.py"
Cohesion: 0.10
Nodes (32): _control_summary(), main(), phase_calibrate(), phase_generate(), phase_report(), R7 conformal abstention calibration: generate -> calibrate -> report phases.…, Current production behaviour, exactly as shipped -- no LOO recalibration, the…, Re-simulates each row's abstention decision under the CALIBRATED thresholds,… (+24 more)

### Community 7 - "test_golden_v7_gate.py"
Cohesion: 0.06
Nodes (48): derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the…, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,…, True iff every floor's metric is present in `report_gate` and meets it. Missing… (+40 more)

### Community 8 - "Human Annotation Workflow"
Cohesion: 0.07
Nodes (52): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+44 more)

### Community 9 - "SpacesSettings"
Cohesion: 0.15
Nodes (13): _grounded_prompt(), F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and the…, ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo. All classes implement…, External Space first; on ANY failure fall back to the local CPU model.…, Primary generator: calls a public LLM Space via gradio_client. Wired to… (+5 more)

### Community 10 - "Regulation Citation Extraction"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 11 - "Contextual Header Generation"
Cohesion: 0.05
Nodes (45): call(), main(), _norm(), Does answering a golden_v7 row require a circular the corpus does not hold?…, Uppercase, strip all whitespace — so 'CIR/MIRSD/5/ 2013' matches…, Returns (answer, reasoning). The judge is a reasoning model: the oMLX API…, windows(), main() (+37 more)

### Community 12 - "Regulation Identity Resolution"
Cohesion: 0.07
Nodes (39): _alias_keys(), _jaccard(), load_regulations(), name_tokens(), Path, Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6). Regulations…, Candidate alias lookup keys, most literal first. Both the raw normalised form…, Resolve a cited regulation name+year to a canonical reg_id. Returns (reg_id,… (+31 more)

### Community 13 - "Dataset Card Validation"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 14 - "UI Logic Tests"
Cohesion: 0.06
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 15 - "derive_validity"
Cohesion: 0.07
Nodes (28): annotate_corpus(), Update each corpus record's supersession_status + superseded_by + supersedes…, annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans… (+20 more)

### Community 16 - "Chunk"
Cohesion: 0.10
Nodes (10): MLXGenerator, OllamaGenerator, Apple-Silicon-native generation via MLX-LM (D6 preferred runtime). Loads a…, Grounded generation via local Ollama (D6 canonical runtime option).…, _extracts(), _LineageAwareReranker, Reranker wrapper that re-applies lineage handling to its output. The paraphrase…, JinaMLXReranker (+2 more)

### Community 17 - "test_spaces.py"
Cohesion: 0.14
Nodes (13): _Boom, _Canned, _hybrid(), fixture, HF Spaces path: corpus_spaces loader mapping + HybridGenerator fallback. Fully…, settings(), _stub_rows(), test_chunks_config_refuses_header_and_maps_fields() (+5 more)

### Community 18 - "Regulation Edge Annotation"
Cohesion: 0.12
Nodes (33): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+25 more)

### Community 19 - "test_golden_v7_gemini.py"
Cohesion: 0.12
Nodes (26): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply… (+18 more)

### Community 20 - "Domain Filtering Logic"
Cohesion: 0.10
Nodes (29): _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain. Case-…, The non-SEBI domain filter must match words, not substrings. Shipped 2026-07-30…, Any single-token keyword <= 5 chars is a substring hazard. Embedding it inside…, Query mentioning both SEBI and RBI should NOT abstain — SEBI intent wins., Empty query should not trigger the non-SEBI filter., FEMA keyword in a SEBI context should NOT abstain — SEBI intent wins., The exact query that exposed the bug. (+21 more)

### Community 21 - "Export Pipeline Tests"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 22 - "api.py"
Cohesion: 0.08
Nodes (25): BaseModel, FastAPI, integration, _citation_meta(), CitationMeta, create_app(), QueryRequest, QueryResponse (+17 more)

### Community 23 - "Annotation Promotion Rules"
Cohesion: 0.12
Nodes (27): decide(), Spec sec7 promotion rules for one row. `votes_by_annotator` is this row's votes…, Abstain rows have no explicit claude vote at all (Task 8 never judged them) -…, Both externals independently think something DOES govern (disputing the…, The LLM leg is whichever single non-claude/non-human annotator voted - "qwen"…, Amendment 2026-07-26 (user-approved): the promotion unit is the PROVISION, not…, External marked claude's chunk governing plus extras: claude's label is…, The abstain protocol can never emit non-empty governing (no letters are… (+19 more)

### Community 24 - "build_report"
Cohesion: 0.31
Nodes (10): build_report(), Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid measurement;…, The headline number must be the 10 pipeline cases alone — the whole point of…, _results(), test_pipeline_metrics_are_not_polluted_by_selector_cases(), test_pooled_overall_carries_no_interval() (+2 more)

### Community 25 - "test_gate.py"
Cohesion: 0.13
Nodes (23): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., rerank_top exactly at 0.85 overrides judge abstention (HYBRID_THRESHOLD=0.85)., rerank_top just below 0.85 does NOT override judge abstention., When no judge is present, hybrid gate logic must be inert (no crash)., Unrelated query vs context: subject_sim < 0.42 → grounded() returns False., SubjectSimJudge has a section_score method (second-tier gate)., Hybrid gate rescues when rerank_top >= 0.85 even if judge.grounded() is False. (+15 more)

### Community 26 - "Master Circular Verification"
Cohesion: 0.19
Nodes (20): diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13). Pure functions only:…, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows., render_markdown() (+12 more)

### Community 27 - "Query Classification Utilities"
Cohesion: 0.14
Nodes (22): classify_answer(), classify_query(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any…, Chunk IDs embed section headings containing spaces, so parse TREC fields… (+14 more)

### Community 28 - "test_selective_citations.py"
Cohesion: 0.05
Nodes (72): _doc(), _aggregate(), eligible(), main(), _measure(), phase_generate(), phase_report(), B' citation-scorer cohort measurement: control (bge, pointwise) vs J1 (jina,… (+64 more)

### Community 29 - "Label Tier Normalization"
Cohesion: 0.12
Nodes (20): classify_tier(), human_reviewed_ids(), main(), Path, Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.…, Map provenance to the controlled vocabulary. `human_reviewed` (row appears in…, Row ids present in the human labelling packet., Controlled-vocabulary label_tier over golden_v7 (spec A §8.3). (+12 more)

### Community 30 - "gemini_adjudicate.py"
Cohesion: 0.11
Nodes (22): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec… (+14 more)

### Community 31 - "test_rerank_jina_v3.py"
Cohesion: 0.14
Nodes (17): ADR-004: the single decision for which model orders the RETRIEVAL pool…, retrieval_reranker_for(), _chunk(), _FakeJinaBackend, Offline tests for the jina-reranker-v3-mlx wrapper (ADR-004) — translation…, Same bug, same fix, second script: eval_asof.py also builds its own RAGPipeline…, Stands in for the vendor's MLXReranker.rerank() — same return shape (list of…, Bypass __init__ (no snapshot_download / mlx / network). (+9 more)

### Community 32 - "RAGPipeline"
Cohesion: 0.06
Nodes (74): smoke_pipeline(), load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable…, RAGPipeline, LexicalReranker (+66 more)

### Community 33 - "Settings"
Cohesion: 0.30
Nodes (17): Settings, The prereg keeps the flag off until §6 and §7 pass., test_paraphrase_rescue_defaults_off_in_shipped_config(), _clear(), Settings: defaults, config.toml, and env-override precedence., ADR-001 D1/D2: bge-reranker-v2-m3 remains the baseline reranker unless…, test_citation_scorer_enabled_defaults_off(), test_citation_scorer_enabled_env_on() (+9 more)

### Community 34 - "test_lineage.py"
Cohesion: 0.09
Nodes (37): contexts_for(), demote_superseded(), detect_relations(), detect_relations_ex(), Down-weight reranked (chunk, score) pairs from superseded circulars and re-…, Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window() (+29 more)

### Community 35 - "test_export_integration.py"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 36 - "Gradio UI Entrypoint"
Cohesion: 0.13
Nodes (21): _append_message(), _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_citations_md(), get_pipeline(), _on_submit(), _parse_as_of() (+13 more)

### Community 37 - "sweep_rrf_k.py"
Cohesion: 0.27
Nodes (8): main(), mrr(), ndcg_at_k(), Sweep RRF k_const values on the golden set. No index rebuild needed., recall_at_k(), Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 38 - "benchmark.py"
Cohesion: 0.20
Nodes (23): beir_corpus_rows(), beir_query_rows(), build_golden_v6(), chunks_by_doc(), dir_fingerprint(), enrich_golden_item(), export_beir(), git_commit() (+15 more)

### Community 39 - "Corpus Validation"
Cohesion: 0.33
Nodes (14): validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the document's own…, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations(), test_duplicate_text_across_records_flagged(), test_empty_text_is_not_a_duplicate_cluster(), test_flags_bad_issue_date() (+6 more)

### Community 40 - "ValueError"
Cohesion: 0.06
Nodes (63): Rankings, _assert_fixed_tail(), convert_run_dir(), main(), Path, Back-convert archived runfiles into standards-compliant TREC artifacts. The…, Trailing field of the first line; also the whitespace precondition check., read_trec_run assumes qid and tag carry no whitespace. Verify per line. (+55 more)

### Community 41 - "agreement.py"
Cohesion: 0.15
Nodes (21): _claude_accuracy_ci(), gwet_ac1(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation…, Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a prevalence-… (+13 more)

### Community 42 - "ingest_pdf.py"
Cohesion: 0.15
Nodes (19): Re-derive circular number + dates from each record's stored text and rewrite…, _existing_numbers(), extract_text(), ingest(), main(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars. Drop a circular PDF into data/raw/ and… (+11 more)

### Community 43 - "HybridRetriever"
Cohesion: 0.10
Nodes (39): eligible(), main(), SPIKE — throwaway, not preregistered. Answers one question before any R6 design…, main(), SPIKE/GATE (throwaway, not preregistered) — R5's own precondition from the…, main(), main(), main() (+31 more)

### Community 44 - "Local Model Adjudication"
Cohesion: 0.15
Nodes (19): _extract_text(), Qwen-family models may emit <think>...</think> reasoning as inline text,…, Anthropic Messages response -> reply text: concatenates `text` content blocks,…, _strip_thinking(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external…, Five pilot rows from five strata measure more than five from one - the gemini…, Vote records must say annotator "qwen" (never reuse "gemini" - the agreement… (+11 more)

### Community 45 - "SpladeIndex"
Cohesion: 0.07
Nodes (28): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.…, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+20 more)

### Community 46 - "Hugging Face Publishing"
Cohesion: 0.19
Nodes (18): export_golden_v7_arrow(), log(), main(), Path, Run export_datasets.py then add golden_v7 Arrow config., Upload dist/datasets/ to HF dataset repo., Run make index to rebuild FAISS+BM25 before upload., Upload data/index/ to HF index repo. (+10 more)

### Community 47 - "parse_meta"
Cohesion: 0.15
Nodes (17): Pattern, _iso_date(), _labeled_date(), parse_meta(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash… (+9 more)

### Community 48 - "MeasureResult"
Cohesion: 0.19
Nodes (8): main(), metrics_to_markdown(), Format results as a markdown table., MeasureReport, MeasureResult, Unit tests for sebi_rag.measure — automated metric collection., TestCLI, TestDataClasses

### Community 49 - "backfill_escalations.py"
Cohesion: 0.09
Nodes (38): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+30 more)

### Community 50 - "UI Citation Components"
Cohesion: 0.16
Nodes (17): Human-readable regulation name. Year disambiguates same-short_name repeal pairs…, reg_display_name(), _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_outputs_md(), _parse_as_of(), Return empty markdown placeholder for streaming. (+9 more)

### Community 51 - "write_dataset_cards"
Cohesion: 0.17
Nodes (12): build_aikosh_pack(), build_hf_card(), build_kaggle_metadata(), build_zenodo_pack(), _compute_stats(), Corpus-derived numbers for the card prose (UNKNOWN fraction, date range) plus…, Build HuggingFace dataset card (README.md with YAML front matter)., Build Kaggle metadata.json. (+4 more)

### Community 52 - "Circular Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 53 - "Lineage"
Cohesion: 0.09
Nodes (16): Answer, Lineage, Path, Map any cited circular that is superseded -> the circular(s) superseding it.…, Connected component over supersedes/superseded_by (both tiers)., The circular in this family that governs on date as_of (ISO), or None when…, superseded_citations(), As-of exclusion or supersession demotion, applied to a reranked list. Extracted… (+8 more)

### Community 54 - "Label Provenance Audit"
Cohesion: 0.21
Nodes (15): audit(), collect_artifacts(), _ids_from_csv(), _ids_from_dir(), _ids_from_jsonl(), main(), Path, Report what the annotation artifacts can account for, before classifying.… (+7 more)

### Community 55 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 56 - "NLI Attribution Scoring"
Cohesion: 0.07
Nodes (33): entailment_index(), NLIAttributionScorer, NLI attribution scoring for B' citation selection. B' asks "does this context…, Index of the entailment class in a model's label map. Read from the checkpoint…, Scores each context by P(entailment) of the answer given that context.…, Wrap an already-constructed cross-encoder (also the test seam)., _softmax(), pick_device() (+25 more)

### Community 57 - "test_eval_harness_v7.py"
Cohesion: 0.49
Nodes (10): run_eval(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-…, _row(), test_as_of_is_passed_to_pipeline(), test_chunk_metrics_computed_for_span_rows(), test_gate_is_none_when_nothing_adjudicated(), test_gate_subreport_covers_only_adjudicated() (+2 more)

### Community 58 - "retrieve.py"
Cohesion: 0.07
Nodes (38): Embedder, Protocol, expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and…, DenseIndex, _doc_checksum(), ndarray (+30 more)

### Community 59 - "QueryRewriter"
Cohesion: 0.18
Nodes (9): MLXQueryRewriter, Protocol, query_rewriter_for(), QueryRewriter, Factory mirroring `generate.citation_scorer_for`: None when disabled., Rewrites a lay-vocabulary query into statutory vocabulary. Returns None when it…, Local MLX-LM rewriter. Greedy decoding -> deterministic., Disabled must not construct the rewriter — it would load an MLX model. (+1 more)

### Community 60 - "Golden Set Schema"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 61 - "local_adjudicate.py"
Cohesion: 0.18
Nodes (16): Rerun-safety for votes.jsonl itself (plan Task 10 decision #7): drops every…, Same per-row deterministic shuffle as make_packet.py's write_packet:…, _replace_annotator_votes(), _shuffled_candidates(), _current_model(), main(), pilot(), _pilot_ids() (+8 more)

### Community 62 - "test_corpus.py"
Cohesion: 0.13
Nodes (28): Path, corpus.load_circulars edge-case coverage. load_circulars reads a JSONL corpus…, Provided optional fields are passed through to CircularMeta., Multiple records produce multiple chunks., Blank lines between records are silently skipped., Malformed JSON raises ValueError (json.loads default)., load_circulars accepts both str and Path., load_circulars accepts a pathlib.Path. (+20 more)

### Community 64 - "Supersession Precision Metrics"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 65 - "resolve_chunk_spans"
Cohesion: 0.30
Nodes (11): _norm_ws(), Span {doc, quote} -> matching chunk ids (all overlap matches count). Legacy…, resolve_chunk_spans(), _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through(), test_qrels_span_rows_get_grade_2() (+3 more)

### Community 66 - ".grounded"
Cohesion: 0.14
Nodes (12): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), v2 protocol: closed-set identification instead of yes/no judgment. Naming which…, True iff the reply names a valid excerpt number. 'none' or anything unparseable…, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the gate… (+4 more)

### Community 67 - "WarrantJudge"
Cohesion: 0.20
Nodes (7): parse_warrant_scores(), Prompt for the warrant judge: evaluate each excerpt's warrant for the answer.…, Parse warrant scores from the judge's JSON output. Returns a list of n floats…, Warrant judge: single-call structured output evaluating each excerpt's warrant.…, Score each context's warrant for the answer. Returns a list of floats…, _warrant_prompt(), WarrantJudge

### Community 68 - "ZeroGPU Workaround Tests"
Cohesion: 0.14
Nodes (13): app_module(), fixture, Regression coverage for the ZeroGPU-hardware workaround in app.py. Background:…, Inject a fake `spaces` module so app.py's `import spaces` succeeds offline, and…, Static guard: if `import spaces` or the `@spaces.GPU` decorator is ever…, It must stay dead code: calling it would request a real ZeroGPU allocation (and…, The functions actually on the request path (get_pipeline, run_query_stream)…, `hardware:` in README-spaces.md is not a documented Spaces config key (only… (+5 more)

### Community 69 - "answer_with_abstention"
Cohesion: 0.44
Nodes (9): answer_with_abstention(), _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons,…, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful(), test_no_context_reason_when_top_k_zero(), test_score_floor_reason() (+1 more)

### Community 70 - "apply"
Cohesion: 0.29
Nodes (7): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions` (keyed by…, test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only(), test_apply_queue_decision_leaves_row_untouched(), test_apply_row_without_a_decision_is_never_touched()

### Community 71 - "_unique"
Cohesion: 0.16
Nodes (18): aggregate(), eligible(), main(), measure(), Preregistered cohort measurement for supersession confidence tiering. Spec:…, Answerable, non-as_of, with gold citations: the rows citation metrics exist for., cited_docs(), metrics() (+10 more)

### Community 72 - "Generator Factory Tests"
Cohesion: 0.18
Nodes (9): The eval stack's generator choice must be one shared decision.…, Uses an injected loader so the test stays offline., Silently falling back to the stub would derive floors under semantics the…, Must assert the factory is CALLED, not merely imported. Verified 2026-08-12 by…, A factory both call is not enough - they must pass the same setting, or the…, test_both_eval_scripts_read_the_same_setting(), test_eval_scripts_use_the_shared_factory(), test_mlx_kind_builds_the_production_generator() (+1 more)

### Community 73 - "run_all_metrics"
Cohesion: 0.29
Nodes (4): Run all (or specified) metrics sequentially., run_all_metrics(), Empty metrics list is falsy → defaults to ALL_METRICS., TestRegistry

### Community 74 - "run_judge"
Cohesion: 0.39
Nodes (7): _is_parseable(), _load_screen(), main(), R1 §3.3 degeneracy probe: does the warrant judge return a parseable reply?…, Mirrors generate.parse_warrant_scores' cleaning exactly, but reports whether…, run_answers(), run_judge()

### Community 75 - "test_ingest_refs.py"
Cohesion: 0.14
Nodes (12): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_dedup_uses_normalized_numbers() (+4 more)

### Community 76 - "measure.py"
Cohesion: 0.26
Nodes (12): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), Automated metric collection for the SEBI Circular RAG pipeline. Six on-demand…, test_retrieval_metrics(), _internal(), Prove the internal retrieval metrics are the standard ones. Skips unless the… (+4 more)

### Community 77 - "MRR Evaluation"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level. For each query, RR = 1/rank of first…, TestMRR

### Community 78 - "Confidence Interval Utilities"
Cohesion: 0.22
Nodes (5): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, test_render_report_includes_ac1_and_provision(), The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 79 - "Dataset Hub Upload"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default:…, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 80 - "main"
Cohesion: 0.67
Nodes (3): main(), P0 prep: price a larger MLX generator before committing to the R0 upgrade.…, rss_gb()

### Community 81 - "read_trec_run"
Cohesion: 0.29
Nodes (6): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), write_trec_run(), test_trec_run_and_research_judges_are_sidecar_only(), The archived runfiles embed section headings in the doc id., TestReadTrecRun

### Community 82 - "Edge Precision Audit"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 83 - "Retrieval Recall Metrics"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 84 - "corpus_spaces.py"
Cohesion: 0.29
Nodes (10): _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path). Loads the…, One HF dataset config as plain dicts (network; cached by `datasets`)., Full-circular records (dicts) for build_lineage() — always the "corpus" config… (+2 more)

### Community 85 - "test_context_recall.py"
Cohesion: 0.46
Nodes (7): _chunk(), The gate must measure the context window, not just the fusion list.…, An abstention still had a context window; measuring retrieval delivery must not…, _reranked(), test_answer_records_the_context_ids_it_used(), test_context_ids_populated_even_when_abstaining(), test_context_ids_respect_top_k()

### Community 86 - "scrape_regulations.py"
Cohesion: 0.20
Nodes (14): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY).…, (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'. Takes the LAST bracket group…, _record() (+6 more)

### Community 87 - "stats.py"
Cohesion: 0.13
Nodes (11): BootstrapCI, paired_delta(), PairedResult, ProportionCI, Uncertainty quantification for benchmark runs. The golden set is n=56…, Compare run `b` against run `a` on their shared queries. Returns mean_b -…, True when the randomization test rejects at 1 - confidence AND the paired…, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests). (+3 more)

### Community 88 - "Operations Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 89 - "test_benchmark.py"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

### Community 90 - "adjudicate_draft.py"
Cohesion: 0.23
Nodes (11): RuntimeError, adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response. (+3 more)

### Community 91 - "test_golden_v7_pool.py"
Cohesion: 0.31
Nodes (9): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, Regression (2026-07-25): a must_contain literal matching many gold-doc chunks…, _retriever(), test_bm25_leg_uses_raw_query_not_expansion(), test_deep_relevant_chunk_is_reachable_despite_a_common_literal(), test_gold_literal_chunks_lead_the_pool() (+1 more)

### Community 92 - "Dataset Seeding"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 93 - "scrape_sebi.py"
Cohesion: 0.26
Nodes (13): discover(), _listing_url(), main(), _page(), _parse_date(), parse_rows(), pdf_url_for(), date (+5 more)

### Community 94 - "bootstrap_ci"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 95 - "validate_corpus.py"
Cohesion: 0.38
Nodes (6): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair. Checks (per…, Every record's text must match the PDF its provenance names. Slow (re-extracts…, validate_deep()

### Community 96 - "Retrieval Failure Tracing"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 97 - "Regulation Edge Audit"
Cohesion: 0.33
Nodes (9): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+1 more)

### Community 98 - "test_integration_e2e.py"
Cohesion: 0.33
Nodes (4): _ollama_up(), pipeline(), fixture, Step 12 — end-to-end RAG integration test with the REAL stack. bge-m3 (MPS) +…

### Community 99 - "_provision_agree"
Cohesion: 0.20
Nodes (10): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using the…, Does this external vote confirm claude's label, at PROVISION level? Amendment…, Different chunk copies of the same quoted provision agree at provision level…, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction(), test_provision_agree_disjoint_without_pool_is_false() (+2 more)

### Community 100 - "adjudicate"
Cohesion: 0.22
Nodes (10): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt) -> str`…, Scans the per-row cache for `ids` and returns the ones flagged parse_error:…, A Gemini reply that disputes an abstain row (says YES, it IS answerable) writes…, Defensive: an id that was never adjudicated (no cache file at all) is not…, test_adjudicate_abstain_row_dispute_keeps_governing_empty() (+2 more)

### Community 101 - "main"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl()

### Community 102 - "acquire_missing_pdfs.py"
Cohesion: 0.26
Nodes (12): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+4 more)

### Community 103 - "Edge Driver Tests"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 104 - "Canary Monitoring Tests"
Cohesion: 0.27
Nodes (8): _canary_jscode(), _ops_timeout(), The eval canary must fit its timeout and alert on real regressions. Measured…, n8n gives up first if its budget is smaller, so the ops timeout is never…, A threshold above the healthy value fires every run. citation_precision was…, test_alert_thresholds_sit_below_measured_baselines(), test_n8n_timeout_not_tighter_than_the_ops_budget(), test_ops_timeout_fits_the_measured_runtime()

### Community 105 - "sebi_rag/eval_asof.py"
Cohesion: 0.20
Nodes (16): AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Aggregate case results with an exact confidence interval. Pure function of the…, run_pipeline_cases(), run_selector_cases(), summarize() (+8 more)

### Community 106 - "main"
Cohesion: 0.50
Nodes (4): build_screen(), main(), T-Screen: does the generator follow the citation instruction at all? Spec:…, 50 rows stratified proportionally to golden_v7's eight strata.

### Community 107 - "test_repair_corpus_text.py"
Cohesion: 0.22
Nodes (4): main(), Repair the 6 records whose body text was overwritten with one shared circular's…, The repair map must name a real orphan PDF that parses to the circular_number…, test_numbers_normalize_distinctly()

### Community 108 - "_bootstrap_ci"
Cohesion: 0.15
Nodes (10): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Path, Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict. (+2 more)

### Community 109 - "Prompt Injection Scanning"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 110 - "Regulatory Index Construction"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 111 - "Regulatory Lineage Mapping"
Cohesion: 0.29
Nodes (6): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus., derive_regulatory_basis(), Regulatory-basis status of one circular from its resolved regulations.…, test_derive_regulatory_basis_truth_table()

### Community 112 - "Retrieval Artifact Tests"
Cohesion: 0.18
Nodes (7): bench_retrieval must emit valid TREC alongside the legacy runfile., run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so every…, iv9/iv10 build a headered index beside data/index. Without an index override…, ADR-004: benchmarking jina-reranker-v3-mlx against the production cross-encoder…, test_bench_retrieval_can_bench_an_alternate_index(), test_bench_retrieval_can_measure_the_reranked_order(), test_bench_retrieval_exposes_and_records_the_reranker_choice()

### Community 113 - "Environment Configuration"
Cohesion: 0.25
Nodes (7): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, SEBI_RAG_EVAL_GENERATOR, canary.sh script, TOKENIZERS_PARALLELISM

### Community 114 - "Governing Span Resolution"
Cohesion: 0.36
Nodes (8): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote} spans, looked…, _resolve_governing_spans(), _pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool(), test_resolve_governing_spans_short_body_uses_whole_body(), test_resolve_governing_spans_uses_first_60_body_chars()

### Community 115 - "main"
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 116 - "build_chunk_rows"
Cohesion: 0.40
Nodes (5): build_chunk_rows(), build_corpus_rows(), _null(), Pure transform: corpus JSONL records -> publishable rows (CORPUS_SCHEMA)., Pure transform: chunks.jsonl records -> publishable rows (CHUNKS_SCHEMA).

### Community 118 - "Circular Reference Samples"
Cohesion: 0.25
Nodes (8): CIR/MRD/DP/19/2010, List of Circulars, List of Communications, MRD/DoP/Dep/Cir-29/2004, MRD/DoP/MAS – OW/16723/2010, Securities and Exchange Board of India, SEBI/MRD/SE/DEP/Cir-4/2005, SMDRP/NSDL/3055/1998

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

### Community 124 - "measure_context_precision"
Cohesion: 0.50
Nodes (3): measure_context_precision(), Fraction of top-k chunks from relevant circulars. Unlike recall@k (which is…, TestContextPrecision

### Community 125 - "test_golden_v7_agreement.py"
Cohesion: 0.19
Nodes (15): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw element is…, _min_agreement_fixture(), Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):…, The kappa base-rate paradox: one label dominates, raw agreement is high, yet…, _same_provision_fixture(), test_claude_accuracy_ci_returns_exact_and_provision(), test_cohen_kappa_both_constant_and_identical_is_one() (+7 more)

### Community 126 - "Environment Refresh Script"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 127 - "measure_parsing_latency"
Cohesion: 0.38
Nodes (4): measure_parsing_latency(), Measure PDF ingestion throughput (chars/sec, ms/PDF). Samples 20 PDFs…, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 128 - ".load_spaces"
Cohesion: 0.40
Nodes (4): _get(), Path, Settings.load() plus the [spaces] table as settings.spaces.* Load order per…, Resolve a setting: env var > config dict > default.

### Community 129 - "main"
Cohesion: 0.67
Nodes (3): is_master(), main(), Is the eval set measuring retrieval, or measuring its own construction? Read-…

### Community 131 - "UI Date Handling"
Cohesion: 0.29
Nodes (3): app_module(), fixture, As-of date plumbing in the Spaces UI (app.py).

### Community 132 - "SubjectSimJudge"
Cohesion: 0.20
Nodes (8): ADOPTED gate (eval_gate round 3): deterministic groundedness signal — max…, Max cosine(query, doc subject line) over contexts — the primary gate signal,…, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge, subject_sim == threshold (0.42) passes the gate (>= comparison)., section_score == section_threshold (0.60) passes via second tier., test_section_score_exactly_at_threshold_passes(), test_subject_sim_exactly_at_threshold_passes()

### Community 133 - "Index Build Configuration"
Cohesion: 0.29
Nodes (5): build_index must be able to target a scratch index directory. The iv9/iv10…, A --out flag that is parsed but ignored is worse than none: it reads as safe…, lineage.json lands next to the index it describes; writing it into data/index…, test_build_index_saves_to_the_resolved_out_dir_not_the_constant(), test_lineage_follows_the_out_dir()

### Community 134 - "_compute_kwargs"
Cohesion: 0.50
Nodes (4): _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker., test_compute_kwargs_cpu_disables_fp16(), test_compute_kwargs_mps_keeps_fp16()

### Community 135 - "Auto-research Execution Script"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 136 - "build_citation_pairs"
Cohesion: 0.67
Nodes (3): build_citation_pairs(), _format_family(), Pure transform: corpus text -> citation-normalization rows. Mines in-body…

### Community 138 - "faithfulness"
Cohesion: 0.67
Nodes (3): faithfulness(), Check that every circular id the answer cites (in square brackets) was actually…, test_faithfulness_scoring()

### Community 139 - "Pipeline Evaluation Summary"
Cohesion: 0.67
Nodes (4): Failure: asof-p2, Overall Evaluation Summary, Pipeline Evaluation Results, Selector Evaluation Results

### Community 142 - "Golden Dataset Samples"
Cohesion: 0.67
Nodes (3): Golden v7 Human Packet, SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026, SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122

## Knowledge Gaps
- **50 isolated node(s):** `checks.sh script`, `measure.sh script`, `autoresearch.sh script`, `PYTHONPATH`, `TOKENIZERS_PARALLELISM` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `test_paraphrase_rescue.py`, `generate.py`, `SubjectSimJudge`, `SpacesSettings`, `Contextual Header Generation`, `test_spaces.py`, `test_gate.py`, `test_selective_citations.py`, `test_rerank_jina_v3.py`, `RAGPipeline`, `test_lineage.py`, `sweep_rrf_k.py`, `benchmark.py`, `HybridRetriever`, `SpladeIndex`, `Lineage`, `Qwen3MLXReranker`, `NLI Attribution Scoring`, `retrieve.py`, `QueryRewriter`, `Golden Set Schema`, `resolve_chunk_spans`, `.grounded`, `WarrantJudge`, `answer_with_abstention`, `corpus_spaces.py`, `test_context_recall.py`, `test_benchmark.py`, `Prompt Injection Scanning`, `Benchmark Export Utilities`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `test_paraphrase_rescue.py`, `generate.py`, `Chunk`, `api.py`, `benchmark.py`, `HybridRetriever`, `Lineage`, `test_eval_harness_v7.py`, `retrieve.py`, `QueryRewriter`, `Supersession Precision Metrics`, `_unique`, `run_all_metrics`, `measure.py`, `MRR Evaluation`, `Retrieval Recall Metrics`, `test_integration_e2e.py`, `sebi_rag/eval_asof.py`, `measure_temporal_accuracy`, `measure_context_precision`, `measure_parsing_latency`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `main()` connect `HybridRetriever` to `RAGPipeline`, `per_query_recall`, `Settings`, `generate.py`, `benchmark.py`, `_compute_kwargs`, `ValueError`, `_unique`, `Contextual Header Generation`, `SpladeIndex`, `Chunk`, `read_trec_run`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 65 inferred relationships involving `Chunk` (e.g. with `dataset_quality()` and `NLIAttributionScorer`) actually correct?**
  _`Chunk` has 65 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `run()`) actually correct?**
  _`RAGPipeline` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `Settings` (e.g. with `main()` and `main()`) actually correct?**
  _`Settings` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `ExtractiveStubGenerator` (e.g. with `get_pipeline()` and `run()`) actually correct?**
  _`ExtractiveStubGenerator` has 38 INFERRED edges - model-reasoned connections that need verification._