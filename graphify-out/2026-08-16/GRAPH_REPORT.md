# Graph Report - SEBI circular RAG  (2026-08-16)

## Corpus Check
- 194 files · ~182,813 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2424 nodes · 5028 edges · 152 communities (120 shown, 32 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 327 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `301a8f53`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- export_datasets.py
- Telemetry and Performance Monitoring
- Human Annotation Workflow
- ExtractiveStubGenerator
- Regulation Lineage and Identity
- test_spaces.py
- scrape_sebi.py
- api_spaces.py
- Regulation Citation Extraction
- test_reg_lineage.py
- Dataset Card Validation
- benchmark.py
- ValueError
- derive_validity
- corpus.py
- Lineage
- test_golden_v7_gemini.py
- faithfulness
- Dataset Export Testing
- test_ingest_pdf.py
- validate_golden_v7
- Annotation Promotion Logic
- API Service and Integration
- backfill_escalations.py
- gemini_adjudicate.py
- test_selective_citations.py
- consolidation_edges
- test_attribution.py
- per_query_recall
- agreement.py
- normalize_circular_number
- Retrieval Error Classification
- Local Model Adjudication
- test_export_integration.py
- test_annotation_adds_no_circular_meta_field
- settings.py
- ingest_pdf.py
- RAGPipeline
- Web Scraper Testing
- Context Precision Metrics
- Label Provenance and Tiers
- Statistical and Hardware Helpers
- Chunk
- validate
- Local Model Inference
- test_hyde.py
- .build
- Regulation Scraper Testing
- test_trecio.py
- _doc
- MLXJudge
- trecio.py
- Hugging Face Spaces Deployment
- test_golden_v7_gate.py
- Hardware Device Selection
- build_regulatory_index
- Golden Set Seeding
- SpladeIndex
- clopper_pearson_ci
- acquire_missing_pdfs.py
- Dataset Hub Upload
- User Interface Components
- Regulation Edge Auditing
- UI Logic Testing
- Benchmark Schema Validation
- TestReadTrecRun
- sebi-rag
- paired_delta
- remap_doc_ids.py
- Operations Server Management
- Regulation Edge Precision Audit
- load_golden
- generate.py
- test_golden_v7_agreement.py
- bootstrap_ci
- Retrieval Failure Analysis
- apply
- test_incremental_index.py
- _is_non_sebi_domain
- adjudicate
- write_trec_qrels
- Regulation Edge Integration Testing
- .encode
- Frame
- Auto-research Driver Scripts
- Prompt Injection Security
- test_golden_v7_pool.py
- Auto-research Evaluation Support
- Qwen3MLXReranker
- bench_rerankers.py
- test_measure.py
- run_all_metrics
- test_context_recall.py
- _provision_agree
- SEBI Circular Identifiers
- .load
- Execution Shell Scripts
- canary.sh
- validate_corpus.py
- test_persistence.py
- Data Refresh Scripts
- test_persistence.py
- measure_supersession_precision
- Annotation Provenance Auditing
- Protocol
- Temporal UI Testing
- _paragraphs
- measure_parsing_latency
- Regulation Edge Construction
- test_bench_retrieval_artifacts.py
- Auto-research Environment Script
- Any
- test_pipeline.py
- RAG Demo Application
- Human Evaluation Packets
- hierarchical_chunk
- Hugging Face Deployment
- Discovery Execution Script
- Index Artifact Upload
- Measurement Execution Script
- Operations Execution Script
- Notification Script
- Phoenix Monitoring Script
- Test Environment Configuration
- Mutual Fund Master Circulars
- test_golden_v7_resolver.py
- SEBI Master Circulars
- Slash Command Optimization
- Circular ID Tracking
- Label Escalation Management
- test_measure.py
- Unresolved Regulation Tracking
- HF Spaces Dependencies
- Golden Dataset Initialization
- Depository Master Appendix
- SEBI Regulations Directory
- test_eval_generator.py
- sweep_rrf_k.py
- measure.py
- _alias_keys
- test_build_index_out_dir.py
- measure_mrr
- eval_harness.py
- test_canary_generator.py
- measure_retrieval_recall
- measure_temporal_accuracy
- _resolve_governing_spans
- sebi_rag/eval_asof.py
- test_annotation_adds_no_circular_meta_field
- GPU
- fixture
- fixture

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 56 edges
2. `RAGPipeline` - 47 edges
3. `ExtractiveStubGenerator` - 47 edges
4. `hierarchical_chunk()` - 45 edges
5. `CircularMeta` - 40 edges
6. `HashEmbedder` - 38 edges
7. `build_lineage()` - 32 edges
8. `LexicalReranker` - 30 edges
9. `Lineage` - 30 edges
10. `answer_with_abstention()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py
- `test_vectors_exposes_context_recall()` --calls--> `vectors()`  [INFERRED]
  tests/test_context_recall.py → scripts/golden_v7/score.py
- `test_gate_floors_context_recall()` --calls--> `derive_floors()`  [INFERRED]
  tests/test_context_recall.py → scripts/golden_v7/derive_thresholds.py
- `_CannedGenerator` --uses--> `RAGPipeline`  [INFERRED]
  tests/test_api.py → src/sebi_rag/pipeline.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **SEBI Regulatory Framework** — tests_fixtures_master_appendix_pre2015_sebi, tests_fixtures_master_appendix_pre2015_circulars, tests_fixtures_master_appendix_pre2015_communications [INFERRED 0.90]

## Communities (152 total, 32 thin omitted)

### Community 0 - "export_datasets.py"
Cohesion: 0.06
Nodes (66): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+58 more)

### Community 1 - "Telemetry and Performance Monitoring"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 2 - "Human Annotation Workflow"
Cohesion: 0.07
Nodes (52): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+44 more)

### Community 3 - "ExtractiveStubGenerator"
Cohesion: 0.19
Nodes (18): export_golden_v7_arrow(), log(), main(), Path, Run export_datasets.py then add golden_v7 Arrow config., Upload dist/datasets/ to HF dataset repo., Run make index to rebuild FAISS+BM25 before upload., Upload data/index/ to HF index repo. (+10 more)

### Community 4 - "Regulation Lineage and Identity"
Cohesion: 0.08
Nodes (35): _jaccard(), load_regulations(), name_tokens(), Path, Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6). Regulations…, Resolve a cited regulation name+year to a canonical reg_id. Returns (reg_id,…, Load data/corpus/regulations.jsonl into a list of regulation records. Thin…, Human-readable regulation name. Year disambiguates same-short_name repeal pairs… (+27 more)

### Community 5 - "test_spaces.py"
Cohesion: 0.17
Nodes (15): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo. All classes implement…, External Space first; on ANY failure fall back to the local CPU model.…, Primary generator: calls a public LLM Space via gradio_client. Wired to…, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus). Never… (+7 more)

### Community 6 - "scrape_sebi.py"
Cohesion: 0.05
Nodes (62): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+54 more)

### Community 7 - "api_spaces.py"
Cohesion: 0.22
Nodes (15): _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker., _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path). Loads the… (+7 more)

### Community 8 - "Regulation Citation Extraction"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 9 - "test_reg_lineage.py"
Cohesion: 0.14
Nodes (31): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+23 more)

### Community 10 - "Dataset Card Validation"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 11 - "benchmark.py"
Cohesion: 0.20
Nodes (22): Any, RAGPipeline, beir_corpus_rows(), beir_query_rows(), build_golden_v6(), dir_fingerprint(), enrich_golden_item(), export_beir() (+14 more)

### Community 12 - "ValueError"
Cohesion: 0.06
Nodes (63): Rankings, _assert_fixed_tail(), convert_run_dir(), main(), Path, Back-convert archived runfiles into standards-compliant TREC artifacts. The…, Trailing field of the first line; also the whitespace precondition check., read_trec_run assumes qid and tag carry no whitespace. Verify per line. (+55 more)

### Community 13 - "derive_validity"
Cohesion: 0.07
Nodes (28): annotate_corpus(), Update each corpus record's supersession_status + superseded_by + supersedes…, annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans… (+20 more)

### Community 14 - "corpus.py"
Cohesion: 0.08
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 15 - "Lineage"
Cohesion: 0.08
Nodes (33): build_lineage(), detect_relations(), detect_relations_ex(), Lineage, Path, Map any cited circular that is superseded -> the circular(s) superseding it.…, Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference. (+25 more)

### Community 16 - "test_golden_v7_gemini.py"
Cohesion: 0.12
Nodes (27): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply… (+19 more)

### Community 17 - "faithfulness"
Cohesion: 0.15
Nodes (15): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and…, BM25 lexical index (bm25s)., SparseIndex, Query-side lexical expansion (intervention #2, glossary variant).…, test_all_five_sparse_failure_queries_expand(), test_expanded_sparse_query_hits_statutory_chunk() (+7 more)

### Community 18 - "Dataset Export Testing"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 19 - "test_ingest_pdf.py"
Cohesion: 0.10
Nodes (24): Pattern, _iso_date(), _labeled_date(), parse_meta(), _primary_number(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF. (+16 more)

### Community 20 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden.      `chunks` is optio, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 21 - "Annotation Promotion Logic"
Cohesion: 0.12
Nodes (27): decide(), Spec sec7 promotion rules for one row. `votes_by_annotator` is this row's votes…, Abstain rows have no explicit claude vote at all (Task 8 never judged them) -…, Both externals independently think something DOES govern (disputing the…, The LLM leg is whichever single non-claude/non-human annotator voted - "qwen"…, Amendment 2026-07-26 (user-approved): the promotion unit is the PROVISION, not…, External marked claude's chunk governing plus extras: claude's label is…, The abstain protocol can never emit non-empty governing (no letters are… (+19 more)

### Community 22 - "API Service and Integration"
Cohesion: 0.09
Nodes (19): FastAPI, integration, _citation_meta(), create_app(), _offline_pipeline(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit,…, /ready should trigger pipeline build and return ready=true., _slow_pipeline() (+11 more)

### Community 23 - "backfill_escalations.py"
Cohesion: 0.09
Nodes (38): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+30 more)

### Community 24 - "gemini_adjudicate.py"
Cohesion: 0.12
Nodes (21): _current_model(), _daily_quota_exhausted(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec…, Letter-choice protocol: first non-blank line is the choice (comma or semicolon… (+13 more)

### Community 25 - "test_selective_citations.py"
Cohesion: 0.14
Nodes (28): citation_scorer_for(), The single enable/disable AND backend decision for B'.      Returns None when di, Context ids the answer rests on. Scores each context's answer-relevance     via, select_citations(), _chunk(), _FakeReranker, Tests for B' selective citations: select_citations() and its integration., The backend choice must go through the same single decision point as the enable… (+20 more)

### Community 26 - "consolidation_edges"
Cohesion: 0.17
Nodes (7): NLIAttributionScorer, NLI attribution scoring for B' citation selection. B' asks "does this context…, Scores each context by P(entailment) of the answer given that context.…, _softmax(), Protocol, Reranker, Chunk

### Community 27 - "test_attribution.py"
Cohesion: 0.14
Nodes (18): entailment_index(), Index of the entailment class in a model's label map. Read from the checkpoint…, Wrap an already-constructed cross-encoder (also the test seam)., _chunk(), _FakeNLI, NLI attribution scorer for B' citation selection. B' needs to know whether a…, Failing loudly beats scoring on an arbitrary class., Stands in for the cross-encoder: maps context text -> 3 class logits. (+10 more)

### Community 28 - "per_query_recall"
Cohesion: 0.12
Nodes (16): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.      A, validate_golden(), Ten chunks of one circular must not crowd the cutoff: the k applies to unique…, Answerable-but-unjudged rows are excluded from metrics, never scored 0.  golden_, A real, fully-populated golden row, so the fixture cannot drift out of     sync (+8 more)

### Community 29 - "agreement.py"
Cohesion: 0.15
Nodes (21): _claude_accuracy_ci(), gwet_ac1(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation…, Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a prevalence-… (+13 more)

### Community 31 - "Retrieval Error Classification"
Cohesion: 0.14
Nodes (23): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any… (+15 more)

### Community 32 - "Local Model Adjudication"
Cohesion: 0.15
Nodes (19): _extract_text(), Qwen-family models may emit <think>...</think> reasoning as inline text,…, Anthropic Messages response -> reply text: concatenates `text` content blocks,…, _strip_thinking(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external…, Five pilot rows from five strata measure more than five from one - the gemini…, Vote records must say annotator "qwen" (never reuse "gemini" - the agreement… (+11 more)

### Community 33 - "test_export_integration.py"
Cohesion: 0.19
Nodes (8): _hybrid(), fixture, HF Spaces path: corpus_spaces loader mapping + HybridGenerator fallback. Fully…, settings(), _stub_rows(), test_corpus_records_feed_build_lineage(), test_hybrid_falls_back_on_external_failure(), test_hybrid_skips_external_when_unconfigured()

### Community 34 - "test_annotation_adds_no_circular_meta_field"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

### Community 35 - "settings.py"
Cohesion: 0.11
Nodes (12): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped…, Build the dense+sparse index once and persist it (run after corpus changes).…, Emit one JSON line listing SEBI circulars newer than previously seen. Uses a…, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-…, _currency(), demote_superseded(), mc_topic() (+4 more)

### Community 36 - "ingest_pdf.py"
Cohesion: 0.12
Nodes (24): Re-derive circular number + dates from each record's stored text and rewrite…, main(), Repair the 6 records whose body text was overwritten with one shared circular's…, _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number() (+16 more)

### Community 37 - "RAGPipeline"
Cohesion: 0.13
Nodes (35): Answer, BaseModel, Build the full pipeline with real models., real_pipeline(), main(), main(), main(), main() (+27 more)

### Community 38 - "Web Scraper Testing"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 39 - "Context Precision Metrics"
Cohesion: 0.19
Nodes (7): MeasureReport, MeasureResult, Run all (or specified) metrics sequentially., run_all_metrics(), Empty metrics list is falsy → defaults to ALL_METRICS., TestDataClasses, TestRegistry

### Community 40 - "Label Provenance and Tiers"
Cohesion: 0.12
Nodes (20): classify_tier(), human_reviewed_ids(), main(), Path, Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.…, Map provenance to the controlled vocabulary. `human_reviewed` (row appears in…, Row ids present in the human labelling packet., Controlled-vocabulary label_tier over golden_v7 (spec A §8.3). (+12 more)

### Community 41 - "Statistical and Hardware Helpers"
Cohesion: 0.16
Nodes (9): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict., When torch+MPS available, returns memory stats dict. (+1 more)

### Community 42 - "Chunk"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 43 - "validate"
Cohesion: 0.29
Nodes (6): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus., derive_regulatory_basis(), Regulatory-basis status of one circular from its resolved regulations.…, test_derive_regulatory_basis_truth_table()

### Community 44 - "Local Model Inference"
Cohesion: 0.18
Nodes (16): Rerun-safety for votes.jsonl itself (plan Task 10 decision #7): drops every…, Same per-row deterministic shuffle as make_packet.py's write_packet:…, _replace_annotator_votes(), _shuffled_candidates(), _current_model(), main(), pilot(), _pilot_ids() (+8 more)

### Community 45 - "test_hyde.py"
Cohesion: 0.33
Nodes (3): Chunk, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier.

### Community 46 - ".build"
Cohesion: 0.18
Nodes (10): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —…, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_output_truncated_to_max_chars() (+2 more)

### Community 48 - "test_trecio.py"
Cohesion: 0.33
Nodes (14): validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the document's own…, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations(), test_duplicate_text_across_records_flagged(), test_empty_text_is_not_a_duplicate_cluster(), test_flags_bad_issue_date() (+6 more)

### Community 49 - "_doc"
Cohesion: 0.38
Nodes (10): Answer, answer_with_abstention(), _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful(), test_no_context_reason_when_top_k_zero() (+2 more)

### Community 50 - "MLXJudge"
Cohesion: 0.25
Nodes (12): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., Hybrid gate: rerank_top >= 0.85 overrides judge's abstention., _StubJudge, test_hybrid_gate_overrides_judge_when_rerank_top_high(), test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally() (+4 more)

### Community 51 - "trecio.py"
Cohesion: 0.15
Nodes (11): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), v2 protocol: closed-set identification instead of yes/no judgment.     Naming wh, True iff the reply names a valid excerpt number. 'none' or anything     unparsea, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the     gat (+3 more)

### Community 52 - "Hugging Face Spaces Deployment"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_stream), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 53 - "test_golden_v7_gate.py"
Cohesion: 0.07
Nodes (42): derive_floors(), metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the…, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,…, True iff every floor's metric is present in `report_gate` and meets it. Missing…, select_golden() (+34 more)

### Community 54 - "Hardware Device Selection"
Cohesion: 0.20
Nodes (11): pick_device(), Device + precision selection for Apple-Silicon inference. Centralizes the…, Resolve the compute device. A truthy explicit `pref` ("mps"/"cpu"/"cuda") wins.…, fp16 only on GPU-class devices; never on cpu. bf16 is never returned here by…, should_use_fp16(), Device + fp16 policy selection (no real torch/mps required)., test_pick_device_auto_cpu_when_no_mps(), test_pick_device_auto_mps_when_available() (+3 more)

### Community 55 - "build_regulatory_index"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 56 - "Golden Set Seeding"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 57 - "SpladeIndex"
Cohesion: 0.07
Nodes (28): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.…, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+20 more)

### Community 58 - "clopper_pearson_ci"
Cohesion: 0.22
Nodes (5): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, test_render_report_includes_ac1_and_provision(), The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 60 - "Dataset Hub Upload"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default:…, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 61 - "User Interface Components"
Cohesion: 0.21
Nodes (13): _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_outputs_md(), _parse_as_of(), Return empty markdown placeholder for streaming., Generator that streams the answer while updating chat history., Return a color-coded confidence badge string. (+5 more)

### Community 62 - "Regulation Edge Auditing"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 63 - "UI Logic Testing"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 64 - "Benchmark Schema Validation"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

### Community 65 - "TestReadTrecRun"
Cohesion: 0.29
Nodes (4): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}., read_trec_run(), write_trec_run(), The archived runfiles embed section headings in the doc id.

### Community 66 - "sebi-rag"
Cohesion: 0.40
Nodes (3): Protocol, Generator, Judge

### Community 67 - "paired_delta"
Cohesion: 0.19
Nodes (7): paired_delta(), PairedResult, Compare run `b` against run `a` on their shared queries. Returns mean_b -…, True when the randomization test rejects at 1 - confidence AND the paired…, Randomization p-values use the (count+1)/(n+1) estimator, so a p-value of…, One query flipping out of 56 is exactly the iv9-style verdict: the…, TestPairedDelta

### Community 68 - "remap_doc_ids.py"
Cohesion: 0.50
Nodes (4): Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge()

### Community 69 - "Operations Server Management"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 70 - "Regulation Edge Precision Audit"
Cohesion: 0.29
Nodes (10): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+2 more)

### Community 71 - "load_golden"
Cohesion: 0.21
Nodes (13): RuntimeError, adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response. (+5 more)

### Community 72 - "generate.py"
Cohesion: 0.11
Nodes (19): Benchmark MLX generators on the golden set: faithfulness, groundedness,…, Retrieval-only benchmark with TREC runfile and reproducibility metadata. Use…, scripts/eval_asof.py, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the…, False positive check — hybrid gate over abstain=True rows.  Runs the pipeline ov, Hybrid gate sweep — preregistered analysis (2026-08-13).  Runs the pipeline over, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.…, faithfulness() (+11 more)

### Community 73 - "test_golden_v7_agreement.py"
Cohesion: 0.19
Nodes (15): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw element is…, _min_agreement_fixture(), Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):…, The kappa base-rate paradox: one label dominates, raw agreement is high, yet…, _same_provision_fixture(), test_claude_accuracy_ci_returns_exact_and_provision(), test_cohen_kappa_both_constant_and_identical_is_one() (+7 more)

### Community 74 - "bootstrap_ci"
Cohesion: 0.19
Nodes (7): bootstrap_ci(), BootstrapCI, Uncertainty quantification for benchmark runs. The golden set is n=56…, Percentile bootstrap interval for the mean of per-query scores., Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests)., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 75 - "Retrieval Failure Analysis"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 76 - "apply"
Cohesion: 0.29
Nodes (7): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions` (keyed by…, test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only(), test_apply_queue_decision_leaves_row_untouched(), test_apply_row_without_a_decision_is_never_touched()

### Community 77 - "test_incremental_index.py"
Cohesion: 0.31
Nodes (7): evaluate(), _doc(), _eval_item(), _unique(), measure_context_precision(), Fraction of top-k chunks from relevant circulars. Unlike recall@k (which is…, TestContextPrecision

### Community 78 - "_is_non_sebi_domain"
Cohesion: 0.13
Nodes (23): _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain.      Cas, The non-SEBI domain filter must match words, not substrings. Shipped 2026-07-30…, Any single-token keyword <= 5 chars is a substring hazard. Embedding it inside…, The exact query that exposed the bug., Guard against false positives on cross-domain SEBI questions., Documented as a keyword since 2026-07-30 but never actually present in…, Also documented but absent from the code. RBI/FEMA territory. (+15 more)

### Community 79 - "adjudicate"
Cohesion: 0.22
Nodes (10): adjudicate(), main(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt) -> str`…, Scans the per-row cache for `ids` and returns the ones flagged parse_error:…, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct from a well-…, Defensive: an id that was never adjudicated (no cache file at all) is not… (+2 more)

### Community 80 - "write_trec_qrels"
Cohesion: 0.21
Nodes (11): log(), Margin sweep for B' selective citations on the golden_v7 adjudicated set. One…, run(), Emit one JSON line of retrieval/citation/abstention metrics using the persisted…, Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, One scoring path shared by `eval_json.py` (which measures) and…, Score one golden row through the production-shaped pipeline. Returns per-row…, Per-row records -> metric -> score vector, skipping rows where the metric was… (+3 more)

### Community 81 - "Regulation Edge Integration Testing"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 82 - ".encode"
Cohesion: 0.23
Nodes (10): _doc_checksum(), Path, F3 (ADR-001): encode only new/changed documents; reuse cached embedding rows…, Deterministic per-document checksum over its (enriched) chunk texts — captures…, _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are… (+2 more)

### Community 83 - "Frame"
Cohesion: 0.07
Nodes (38): load_runs(), main(), Path, Assign epochs to the archived runs and write the epoch registry. Every run's…, _fmt(), guard_pair(), main(), Path (+30 more)

### Community 85 - "Prompt Injection Security"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 86 - "test_golden_v7_pool.py"
Cohesion: 0.20
Nodes (15): Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)…, smoke_pipeline(), assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, LexicalReranker, Deterministic query-coverage reranker (test/fallback). Score = fraction of…, One gold doc with `n` chunks that ALL contain the word "broker", so a… (+7 more)

### Community 88 - "Qwen3MLXReranker"
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 89 - "bench_rerankers.py"
Cohesion: 0.22
Nodes (9): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,…, Calibrate top_k and the abstention threshold against the citation-precision…, sebi_rag/__init__.py (+1 more)

### Community 90 - "test_measure.py"
Cohesion: 0.31
Nodes (10): build_report(), Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid measurement;…, The headline number must be the 10 pipeline cases alone — the whole point of…, _results(), test_pipeline_metrics_are_not_polluted_by_selector_cases(), test_pooled_overall_carries_no_interval() (+2 more)

### Community 91 - "run_all_metrics"
Cohesion: 0.50
Nodes (3): cited_docs(), metrics(), Capture-once margin sweep for B' selective citations.  One pipeline pass over th

### Community 92 - "test_context_recall.py"
Cohesion: 0.33
Nodes (9): _chunk(), The gate must measure the context window, not just the fusion list.…, An abstention still had a context window; measuring retrieval delivery must not…, _reranked(), test_answer_records_the_context_ids_it_used(), test_context_ids_populated_even_when_abstaining(), test_context_ids_respect_top_k(), test_gate_floors_context_recall() (+1 more)

### Community 93 - "_provision_agree"
Cohesion: 0.20
Nodes (10): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using the…, Does this external vote confirm claude's label, at PROVISION level? Amendment…, Different chunk copies of the same quoted provision agree at provision level…, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction(), test_provision_agree_disjoint_without_pool_is_false() (+2 more)

### Community 94 - "SEBI Circular Identifiers"
Cohesion: 0.25
Nodes (8): CIR/MRD/DP/19/2010, List of Circulars, List of Communications, MRD/DoP/Dep/Cir-29/2004, MRD/DoP/MAS – OW/16723/2010, Securities and Exchange Board of India, SEBI/MRD/SE/DEP/Cir-4/2005, SMDRP/NSDL/3055/1998

### Community 95 - ".load"
Cohesion: 0.21
Nodes (17): _as_bool(), _get(), Path, Settings.load() plus the [spaces] table as settings.spaces.* Load order per…, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default may…, _clear(), Settings: defaults, config.toml, and env-override precedence. (+9 more)

### Community 96 - "Execution Shell Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 97 - "canary.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, SEBI_RAG_EVAL_GENERATOR, canary.sh script, TOKENIZERS_PARALLELISM

### Community 98 - "validate_corpus.py"
Cohesion: 0.38
Nodes (6): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair. Checks (per…, Every record's text must match the PDF its provenance names. Slow (re-extracts…, validate_deep()

### Community 99 - "test_persistence.py"
Cohesion: 0.11
Nodes (25): load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., hierarchical_chunk(), _paragraphs(), Segmentation: hierarchical chunking + metadata + stable citation IDs. Minimal,…, Split into units each <= max_chars. PDF-extracted text often lacks blank-line…, Document -> section -> paragraph chunks with stable IDs. A "section" is… (+17 more)

### Community 100 - "Data Refresh Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 101 - "test_persistence.py"
Cohesion: 0.15
Nodes (8): Embedder, ndarray, Protocol, _tokens(), DenseIndex, ndarray, Stage-1 hybrid retrieval: dense (FAISS) + sparse (BM25) fused by RRF. Mandatory…, FAISS IndexFlatIP over L2-normalized vectors (cosine).

### Community 102 - "measure_supersession_precision"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 103 - "Annotation Provenance Auditing"
Cohesion: 0.21
Nodes (15): audit(), collect_artifacts(), _ids_from_csv(), _ids_from_dir(), _ids_from_jsonl(), main(), Path, Report what the annotation artifacts can account for, before classifying.… (+7 more)

### Community 107 - "measure_parsing_latency"
Cohesion: 0.32
Nodes (5): measure_parsing_latency(), Path, Measure PDF ingestion throughput (chars/sec, ms/PDF). Samples 20 PDFs…, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 108 - "Regulation Edge Construction"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl()

### Community 109 - "test_bench_retrieval_artifacts.py"
Cohesion: 0.22
Nodes (5): bench_retrieval must emit valid TREC alongside the legacy runfile., run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so every…, iv9/iv10 build a headered index beside data/index. Without an index override…, test_bench_retrieval_can_bench_an_alternate_index(), test_bench_retrieval_can_measure_the_reranked_order()

### Community 110 - "Auto-research Environment Script"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 113 - "RAG Demo Application"
Cohesion: 0.14
Nodes (19): _append_message(), _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_citations_md(), get_pipeline(), _on_submit(), _parse_as_of() (+11 more)

### Community 114 - "Human Evaluation Packets"
Cohesion: 0.67
Nodes (3): Golden v7 Human Packet, SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026, SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122

### Community 115 - "hierarchical_chunk"
Cohesion: 0.08
Nodes (50): Embedder, Lineage, Reranker, smoke_pipeline(), IncomparableFramesError, Raised when a paired comparison spans two frames., HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable… (+42 more)

### Community 125 - "test_golden_v7_resolver.py"
Cohesion: 0.24
Nodes (14): BenchmarkIssue, chunks_by_doc(), _norm_ws(), Span {doc, quote} -> matching chunk ids (all overlap matches count).      Legacy, resolve_chunk_spans(), _span_resolution_issues(), _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud. (+6 more)

### Community 130 - "test_measure.py"
Cohesion: 0.28
Nodes (5): main(), metrics_to_markdown(), Format results as a markdown table., Unit tests for sebi_rag.measure — automated metric collection., TestCLI

### Community 137 - "test_eval_generator.py"
Cohesion: 0.17
Nodes (10): The eval stack's generator choice must be one shared decision.…, Uses an injected loader so the test stays offline., Silently falling back to the stub would derive floors under semantics the…, Must assert the factory is CALLED, not merely imported. Verified 2026-08-12 by…, A factory both call is not enough - they must pass the same setting, or the…, test_both_eval_scripts_read_the_same_setting(), test_eval_scripts_use_the_shared_factory(), test_mlx_kind_builds_the_production_generator() (+2 more)

### Community 138 - "sweep_rrf_k.py"
Cohesion: 0.27
Nodes (8): main(), mrr(), ndcg_at_k(), Sweep RRF k_const values on the golden set. No index rebuild needed., recall_at_k(), Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 139 - "measure.py"
Cohesion: 0.26
Nodes (12): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), Automated metric collection for the SEBI Circular RAG pipeline. Six on-demand…, test_retrieval_metrics(), _internal(), Prove the internal retrieval metrics are the standard ones. Skips unless the… (+4 more)

### Community 141 - "_alias_keys"
Cohesion: 0.29
Nodes (8): _alias_keys(), Candidate alias lookup keys, most literal first. Both the raw normalised form…, PMS/NCS/ILDS end in a literal S. Unconditional plural-stripping mapped them to…, reg_id resolved purely through the alias table, ignoring the corpus., A table key that no _alias_keys() output can produce is dead config., _resolved(), test_acronyms_ending_in_s_reach_their_own_entry(), test_every_alias_entry_is_reachable_from_some_spelling()

### Community 142 - "test_build_index_out_dir.py"
Cohesion: 0.29
Nodes (5): build_index must be able to target a scratch index directory. The iv9/iv10…, A --out flag that is parsed but ignored is worse than none: it reads as safe…, lineage.json lands next to the index it describes; writing it into data/index…, test_build_index_saves_to_the_resolved_out_dir_not_the_constant(), test_lineage_follows_the_out_dir()

### Community 143 - "measure_mrr"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level. For each query, RR = 1/rank of first…, TestMRR

### Community 144 - "eval_harness.py"
Cohesion: 0.28
Nodes (15): _aggregate(), EvalReport, _mean(), Golden-set evaluation harness (P1). Runs the pipeline over a labelled golden…, report_dict(), run_eval(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-… (+7 more)

### Community 145 - "test_canary_generator.py"
Cohesion: 0.27
Nodes (8): _canary_jscode(), _ops_timeout(), The eval canary must fit its timeout and alert on real regressions. Measured…, n8n gives up first if its budget is smaller, so the ops timeout is never…, A threshold above the healthy value fires every run. citation_precision was…, test_alert_thresholds_sit_below_measured_baselines(), test_n8n_timeout_not_tighter_than_the_ops_budget(), test_ops_timeout_fits_the_measured_runtime()

### Community 146 - "measure_retrieval_recall"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 147 - "measure_temporal_accuracy"
Cohesion: 0.43
Nodes (3): measure_temporal_accuracy(), Measure fraction of as_of queries returning correct pre-supersession circular…, TestTemporalAccuracy

### Community 151 - "_resolve_governing_spans"
Cohesion: 0.36
Nodes (8): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote} spans, looked…, _resolve_governing_spans(), _pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool(), test_resolve_governing_spans_short_body_uses_whole_body(), test_resolve_governing_spans_uses_first_60_body_chars()

### Community 155 - "sebi_rag/eval_asof.py"
Cohesion: 0.20
Nodes (17): sebi_rag/eval_asof.py, AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Aggregate case results with an exact confidence interval. Pure function of the…, run_pipeline_cases(), run_selector_cases() (+9 more)

## Knowledge Gaps
- **49 isolated node(s):** `HF_HUB_DISABLE_XET`, `OMP_NUM_THREADS`, `PYTHONPATH`, `PYTORCH_ENABLE_MPS_FALLBACK`, `refresh.sh script` (+44 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RAGPipeline` connect `RAGPipeline` to `measure_supersession_precision`, `Context Precision Metrics`, `generate.py`, `measure.py`, `measure_parsing_latency`, `test_incremental_index.py`, `measure_mrr`, `write_trec_qrels`, `eval_harness.py`, `measure_retrieval_recall`, `hierarchical_chunk`, `measure_temporal_accuracy`, `test_golden_v7_pool.py`, `API Service and Integration`, `sebi_rag/eval_asof.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `Chunk` connect `consolidation_edges` to `test_spaces.py`, `api_spaces.py`, `sweep_rrf_k.py`, `corpus.py`, `faithfulness`, `test_selective_citations.py`, `test_attribution.py`, `test_annotation_adds_no_circular_meta_field`, `settings.py`, `RAGPipeline`, `Chunk`, `.build`, `SpladeIndex`, `acquire_missing_pdfs.py`, `Benchmark Schema Validation`, `generate.py`, `.encode`, `Prompt Injection Security`, `test_golden_v7_pool.py`, `test_context_recall.py`, `test_persistence.py`, `test_persistence.py`, `hierarchical_chunk`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `main()` connect `RAGPipeline` to `TestReadTrecRun`, `api_spaces.py`, `generate.py`, `load_golden`, `benchmark.py`, `ValueError`, `.build`, `Lineage`, `hierarchical_chunk`, `SpladeIndex`, `per_query_recall`, `.load`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `Chunk` (e.g. with `NLIAttributionScorer` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `CitationMeta`) actually correct?**
  _`RAGPipeline` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `ExtractiveStubGenerator` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`ExtractiveStubGenerator` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `CircularMeta` (e.g. with `MeasureReport` and `MeasureResult`) actually correct?**
  _`CircularMeta` has 10 INFERRED edges - model-reasoned connections that need verification._