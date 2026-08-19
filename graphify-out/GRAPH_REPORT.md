# Graph Report - SEBI circular RAG  (2026-08-20)

## Corpus Check
- 206 files · ~191,521 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2613 nodes · 5519 edges · 155 communities (127 shown, 28 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 508 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d04b036c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- export_datasets.py
- ValueError
- eval_harness.py
- telemetry_engine.py
- test_golden_v7_packet.py
- Frame
- SpladeIndex
- test_golden_v7_gate.py
- test_lineage.py
- backfill_escalations.py
- parse_excerpt_choice
- test_regulations.py
- RAGPipeline
- test_attribution.py
- validate
- context_headers.py
- test_selective_citations.py
- .family
- test_reg_lineage.py
- extract_citations
- test_dataset_cards.py
- test_ui.py
- derive_validity
- test_golden_v7_gemini.py
- _is_non_sebi_domain
- test_export_datasets.py
- test_corpus.py
- ExtractiveStubGenerator
- test_paraphrase_rescue.py
- _row
- HybridRetriever
- per_query_recall
- test_label_tier.py
- gemini_adjudicate.py
- scrape_sebi.py
- app.py
- api.py
- benchmark.py
- sebi_rag/verify_master.py
- extract_misses.py
- agreement.py
- test_golden_v7_local.py
- Settings
- test_golden_v7_pool.py
- build_lineage
- publish_hf.py
- ingest_pdf.py
- ui.py
- test_scrape_sebi.py
- Chunk
- audit_label_provenance.py
- test_golden_v7_resolver.py
- SubjectSimJudge
- bootstrap_ci
- local_adjudicate.py
- _bootstrap_ci
- validate_golden_v7
- test_eval_harness_v7.py
- apply
- test_scrape_regulations.py
- test_expand.py
- test_hyde.py
- paired_delta
- test_app_zerogpu.py
- measure_parsing_latency
- eval_generator_for
- Qwen3MLXReranker
- clopper_pearson_ci
- test_push_datasets.py
- scrape_regulations.py
- measure.py
- measure_supersession_precision
- test_audit_reg_edges.py
- test_ingest_pdf.py
- .encode
- test_golden_v7_agreement.py
- answer_with_abstention
- Handler
- adjudicate_draft.py
- ce_query_reform_probe.py
- AsofCaseResult
- remap_doc_ids.py
- stats.py
- trace_failure.py
- audit_reg_edges.py
- _provision_agree
- relabel_repooled.py
- _HallucinatingGenerator
- test_build_reg_edges.py
- test_canary_generator.py
- MeasureResult
- validate_corpus.py
- parse_yes_no
- test_repair_corpus_text.py
- test_injection.py
- sebi-rag
- build_regulatory_index
- test_acquire_missing.py
- test_bench_retrieval_artifacts.py
- test_spaces.py
- canary.sh
- _resolve_governing_spans
- read_trec_run
- List of Circulars
- build_spaces_pipeline
- run.sh
- acquire_missing_pdfs.py
- main
- test_segment.py
- seed_v7.py
- refresh.sh
- measure_mrr
- measure_retrieval_recall
- measure_temporal_accuracy
- reg_lineage.py
- test_app_asof.py
- .query
- test_build_index_out_dir.py
- main
- parse_meta
- DenseIndex
- autoresearch.sh
- sweep_rrf_k.py
- test_context_recall.py
- Overall Evaluation Summary
- discover_new.py
- Golden v7 Human Packet
- deploy_space.py
- discover.sh
- upload_spaces_index.py
- measure.sh
- run_ops.sh
- scripts/autoresearch/__init__.py
- test_benchmark.py
- dev.sh
- notify.sh
- start_phoenix.sh
- sebi_rag/autoresearch/__init__.py
- TestRegistry
- conftest.py
- Master Appendix (Mutual Funds)
- test_integration_e2e.py
- SEBI Master Circular CIR/DNPD/1/2012
- Optimize Slash Command
- Seen Circular IDs
- Label Escalations
- _doc
- Unresolved Regulations
- Hugging Face Spaces Requirements
- Master Appendix (Depository)
- SEBI Regulations Listing
- bench_rerankers.py
- measure_context_precision
- _rejoin_split

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 105 edges
2. `RAGPipeline` - 60 edges
3. `hierarchical_chunk()` - 46 edges
4. `ExtractiveStubGenerator` - 44 edges
5. `HybridRetriever` - 42 edges
6. `HashEmbedder` - 41 edges
7. `Settings` - 38 edges
8. `build_lineage()` - 36 edges
9. `CircularMeta` - 33 edges
10. `answer_with_abstention()` - 32 edges

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

## Communities (155 total, 28 thin omitted)

### Community 0 - "export_datasets.py"
Cohesion: 0.06
Nodes (66): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+58 more)

### Community 1 - "ValueError"
Cohesion: 0.05
Nodes (69): Rankings, _assert_fixed_tail(), convert_run_dir(), main(), Path, Back-convert archived runfiles into standards-compliant TREC artifacts. The…, Trailing field of the first line; also the whitespace precondition check., read_trec_run assumes qid and tag carry no whitespace. Verify per line. (+61 more)

### Community 2 - "eval_harness.py"
Cohesion: 0.06
Nodes (42): Ground truth: what do the 4 CE_MISMATCH rows actually DO in production? The…, Preregistered cohort measurement for the CE paraphrase rescue. Spec:…, What does the 0.05 cross-encoder score floor actually catch?…, Capture-once margin sweep for B' selective citations. One pipeline pass over…, log(), Margin sweep for B' selective citations on the golden_v7 adjudicated set. One…, run(), Benchmark MLX generators on the golden set: faithfulness, groundedness,… (+34 more)

### Community 3 - "telemetry_engine.py"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 4 - "test_golden_v7_packet.py"
Cohesion: 0.07
Nodes (52): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+44 more)

### Community 5 - "Frame"
Cohesion: 0.07
Nodes (42): load_runs(), main(), Path, Assign epochs to the archived runs and write the epoch registry. Every run's…, _fmt(), guard_pair(), main(), Path (+34 more)

### Community 6 - "SpladeIndex"
Cohesion: 0.07
Nodes (28): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.…, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+20 more)

### Community 7 - "test_golden_v7_gate.py"
Cohesion: 0.06
Nodes (50): derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the…, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,…, True iff every floor's metric is present in `report_gate` and meets it. Missing… (+42 more)

### Community 8 - "test_lineage.py"
Cohesion: 0.05
Nodes (61): contexts_for(), annotate_corpus(), demote_superseded(), detect_relations(), detect_relations_ex(), Path, Down-weight reranked (chunk, score) pairs from superseded circulars and re-…, Update each corpus record's supersession_status + superseded_by + supersedes… (+53 more)

### Community 9 - "backfill_escalations.py"
Cohesion: 0.16
Nodes (22): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+14 more)

### Community 10 - "parse_excerpt_choice"
Cohesion: 0.67
Nodes (3): parse_excerpt_choice(), True iff the reply names a valid excerpt number. 'none' or anything unparseable…, test_parse_excerpt_choice_fails_closed()

### Community 11 - "test_regulations.py"
Cohesion: 0.07
Nodes (39): _alias_keys(), _jaccard(), load_regulations(), name_tokens(), Path, Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6). Regulations…, Candidate alias lookup keys, most literal first. Both the raw normalised form…, Resolve a cited regulation name+year to a canonical reg_id. Returns (reg_id,… (+31 more)

### Community 12 - "RAGPipeline"
Cohesion: 0.08
Nodes (58): Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)…, smoke_pipeline(), smoke_pipeline(), load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable… (+50 more)

### Community 13 - "test_attribution.py"
Cohesion: 0.07
Nodes (31): entailment_index(), NLIAttributionScorer, Index of the entailment class in a model's label map. Read from the checkpoint…, Scores each context by P(entailment) of the answer given that context.…, Wrap an already-constructed cross-encoder (also the test seam)., pick_device(), Device + precision selection for Apple-Silicon inference. Centralizes the…, Resolve the compute device. A truthy explicit `pref` ("mps"/"cpu"/"cuda") wins.… (+23 more)

### Community 14 - "validate"
Cohesion: 0.33
Nodes (14): validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the document's own…, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations(), test_duplicate_text_across_records_flagged(), test_empty_text_is_not_a_duplicate_cluster(), test_flags_bad_issue_date() (+6 more)

### Community 15 - "context_headers.py"
Cohesion: 0.09
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 16 - "test_selective_citations.py"
Cohesion: 0.10
Nodes (38): citation_scorer_for(), The single enable/disable AND backend decision for B'. Returns None when…, Context ids the answer rests on. Scores each context's answer-relevance via…, select_citations(), _chunk(), _FakeReranker, Tests for B' selective citations: select_citations() and its integration., When citation_scorer_enabled=True, Settings loads a non-None scorer. (+30 more)

### Community 18 - "test_reg_lineage.py"
Cohesion: 0.12
Nodes (33): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+25 more)

### Community 19 - "extract_citations"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 20 - "test_dataset_cards.py"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 21 - "test_ui.py"
Cohesion: 0.06
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 22 - "derive_validity"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation. Locked…, Validity of one circular from the tiered edge list (any scope: the function…, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 23 - "test_golden_v7_gemini.py"
Cohesion: 0.11
Nodes (29): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply… (+21 more)

### Community 24 - "_is_non_sebi_domain"
Cohesion: 0.10
Nodes (29): _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain. Case-…, The non-SEBI domain filter must match words, not substrings. Shipped 2026-07-30…, Any single-token keyword <= 5 chars is a substring hazard. Embedding it inside…, Query mentioning both SEBI and RBI should NOT abstain — SEBI intent wins., Empty query should not trigger the non-SEBI filter., FEMA keyword in a SEBI context should NOT abstain — SEBI intent wins., The exact query that exposed the bug. (+21 more)

### Community 25 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 26 - "test_corpus.py"
Cohesion: 0.13
Nodes (28): Path, corpus.load_circulars edge-case coverage. load_circulars reads a JSONL corpus…, Provided optional fields are passed through to CircularMeta., Multiple records produce multiple chunks., Blank lines between records are silently skipped., Malformed JSON raises ValueError (json.loads default)., load_circulars accepts both str and Path., load_circulars accepts a pathlib.Path. (+20 more)

### Community 27 - "ExtractiveStubGenerator"
Cohesion: 0.14
Nodes (24): ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., rerank_top exactly at 0.85 overrides judge abstention (HYBRID_THRESHOLD=0.85)., rerank_top just below 0.85 does NOT override judge abstention., When no judge is present, hybrid gate logic must be inert (no crash)., Unrelated query vs context: subject_sim < 0.42 → grounded() returns False. (+16 more)

### Community 28 - "test_paraphrase_rescue.py"
Cohesion: 0.10
Nodes (36): is_degenerate(), Re-score `pool` with a rewritten query when `reranked` is below `floor`.…, Fixed rewrite, for tests and for replaying a preregistered rewrite., True when `rewritten` is unusable and the rescue should be abandoned.…, rescue_pool(), StaticQueryRewriter, _chunk(), _EchoGenerator (+28 more)

### Community 29 - "_row"
Cohesion: 0.12
Nodes (27): decide(), Spec sec7 promotion rules for one row. `votes_by_annotator` is this row's votes…, Abstain rows have no explicit claude vote at all (Task 8 never judged them) -…, Both externals independently think something DOES govern (disputing the…, The LLM leg is whichever single non-claude/non-human annotator voted - "qwen"…, Amendment 2026-07-26 (user-approved): the promotion unit is the PROVISION, not…, External marked claude's chunk governing plus extras: claude's label is…, The abstain protocol can never emit non-empty governing (no letters are… (+19 more)

### Community 30 - "HybridRetriever"
Cohesion: 0.12
Nodes (21): _doc_checksum(), HybridRetriever, Path, F3 (ADR-001): encode only new/changed documents; reuse cached embedding rows…, Deterministic per-document checksum over its (enriched) chunk texts — captures…, BM25 lexical index (bm25s)., SparseIndex, _chunk() (+13 more)

### Community 31 - "per_query_recall"
Cohesion: 0.12
Nodes (16): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.…, validate_golden(), Ten chunks of one circular must not crowd the cutoff: the k applies to unique…, Answerable-but-unjudged rows are excluded from metrics, never scored 0.…, A real, fully-populated golden row, so the fixture cannot drift out of sync… (+8 more)

### Community 32 - "test_label_tier.py"
Cohesion: 0.12
Nodes (20): classify_tier(), human_reviewed_ids(), main(), Path, Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.…, Map provenance to the controlled vocabulary. `human_reviewed` (row appears in…, Row ids present in the human labelling packet., Controlled-vocabulary label_tier over golden_v7 (spec A §8.3). (+12 more)

### Community 33 - "gemini_adjudicate.py"
Cohesion: 0.11
Nodes (26): adjudicate(), _current_model(), _daily_quota_exhausted(), main(), _parse_error_ids(), _parse_letter_choice(), _parse_reply(), _parse_yes_no() (+18 more)

### Community 34 - "scrape_sebi.py"
Cohesion: 0.26
Nodes (13): discover(), _listing_url(), main(), _page(), _parse_date(), parse_rows(), pdf_url_for(), date (+5 more)

### Community 35 - "app.py"
Cohesion: 0.13
Nodes (21): _append_message(), _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_citations_md(), get_pipeline(), _on_submit(), _parse_as_of() (+13 more)

### Community 36 - "api.py"
Cohesion: 0.08
Nodes (22): BaseModel, FastAPI, _citation_meta(), CitationMeta, create_app(), QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline. Run (real stack; loads the… (+14 more)

### Community 37 - "benchmark.py"
Cohesion: 0.19
Nodes (24): beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), chunks_by_doc(), dir_fingerprint(), enrich_golden_item(), export_beir() (+16 more)

### Community 38 - "sebi_rag/verify_master.py"
Cohesion: 0.19
Nodes (20): diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13). Pure functions only:…, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows., render_markdown() (+12 more)

### Community 39 - "extract_misses.py"
Cohesion: 0.13
Nodes (22): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any… (+14 more)

### Community 40 - "agreement.py"
Cohesion: 0.15
Nodes (21): _claude_accuracy_ci(), gwet_ac1(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation…, Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a prevalence-… (+13 more)

### Community 41 - "test_golden_v7_local.py"
Cohesion: 0.15
Nodes (19): _extract_text(), Qwen-family models may emit <think>...</think> reasoning as inline text,…, Anthropic Messages response -> reply text: concatenates `text` content blocks,…, _strip_thinking(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external…, Five pilot rows from five strata measure more than five from one - the gemini…, Vote records must say annotator "qwen" (never reuse "gemini" - the agreement… (+11 more)

### Community 42 - "Settings"
Cohesion: 0.17
Nodes (24): _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker., _as_bool(), _get(), Path, Settings.load() plus the [spaces] table as settings.spaces.* Load order per…, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default may… (+16 more)

### Community 43 - "test_golden_v7_pool.py"
Cohesion: 0.31
Nodes (9): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, Regression (2026-07-25): a must_contain literal matching many gold-doc chunks…, _retriever(), test_bm25_leg_uses_raw_query_not_expansion(), test_deep_relevant_chunk_is_reachable_despite_a_common_literal(), test_gold_literal_chunks_lead_the_pool() (+1 more)

### Community 44 - "build_lineage"
Cohesion: 0.16
Nodes (28): integration, main(), main(), main(), main(), Build the full pipeline with real models., real_pipeline(), main() (+20 more)

### Community 45 - "publish_hf.py"
Cohesion: 0.19
Nodes (18): export_golden_v7_arrow(), log(), main(), Path, Run export_datasets.py then add golden_v7 Arrow config., Upload dist/datasets/ to HF dataset repo., Run make index to rebuild FAISS+BM25 before upload., Upload data/index/ to HF index repo. (+10 more)

### Community 46 - "ingest_pdf.py"
Cohesion: 0.14
Nodes (22): Re-derive circular number + dates from each record's stored text and rewrite…, _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number(), _ocr_text(), Path (+14 more)

### Community 47 - "ui.py"
Cohesion: 0.16
Nodes (17): Human-readable regulation name. Year disambiguates same-short_name repeal pairs…, reg_display_name(), _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_outputs_md(), _parse_as_of(), Return empty markdown placeholder for streaming. (+9 more)

### Community 48 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 49 - "Chunk"
Cohesion: 0.06
Nodes (36): NLI attribution scoring for B' citation selection. B' asks "does this context…, _softmax(), Generator, _grounded_prompt(), Judge, _judge_prompt(), _judge_prompt_identify(), MLXGenerator (+28 more)

### Community 50 - "audit_label_provenance.py"
Cohesion: 0.21
Nodes (15): audit(), collect_artifacts(), _ids_from_csv(), _ids_from_dir(), _ids_from_jsonl(), main(), Path, Report what the annotation artifacts can account for, before classifying.… (+7 more)

### Community 51 - "test_golden_v7_resolver.py"
Cohesion: 0.42
Nodes (8): _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through(), test_qrels_span_rows_get_grade_2(), test_resolves_normalized_whitespace_quote(), test_unresolvable_quote_returns_empty(), test_validator_flags_unresolvable_quote_when_chunks_given()

### Community 52 - "SubjectSimJudge"
Cohesion: 0.20
Nodes (8): ADOPTED gate (eval_gate round 3): deterministic groundedness signal — max…, Max cosine(query, doc subject line) over contexts — the primary gate signal,…, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge, subject_sim == threshold (0.42) passes the gate (>= comparison)., section_score == section_threshold (0.60) passes via second tier., test_section_score_exactly_at_threshold_passes(), test_subject_sim_exactly_at_threshold_passes()

### Community 53 - "bootstrap_ci"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 54 - "local_adjudicate.py"
Cohesion: 0.15
Nodes (19): Transient-failure predicate for the real Gemini call: rate limiting (429) and…, Rerun-safety for votes.jsonl itself (plan Task 10 decision #7): drops every…, Same per-row deterministic shuffle as make_packet.py's write_packet:…, _replace_annotator_votes(), _should_retry(), _shuffled_candidates(), _current_model(), main() (+11 more)

### Community 55 - "_bootstrap_ci"
Cohesion: 0.15
Nodes (10): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Path, Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict. (+2 more)

### Community 56 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 57 - "test_eval_harness_v7.py"
Cohesion: 0.30
Nodes (14): _aggregate(), EvalReport, _mean(), report_dict(), run_eval(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-…, _row() (+6 more)

### Community 58 - "apply"
Cohesion: 0.29
Nodes (7): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions` (keyed by…, test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only(), test_apply_queue_decision_leaves_row_untouched(), test_apply_row_without_a_decision_is_never_touched()

### Community 60 - "test_expand.py"
Cohesion: 0.22
Nodes (13): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and…, Query-side lexical expansion (intervention #2, glossary variant).…, test_all_five_sparse_failure_queries_expand(), test_expanded_sparse_query_hits_statutory_chunk(), test_lay_term_gains_statutory_synonym(), test_multiword_synonym_splits_into_tokens() (+5 more)

### Community 61 - "test_hyde.py"
Cohesion: 0.18
Nodes (10): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —…, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_output_truncated_to_max_chars() (+2 more)

### Community 62 - "paired_delta"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries. Returns mean_b -…, Randomization p-values use the (count+1)/(n+1) estimator, so a p-value of…, One query flipping out of 56 is exactly the iv9-style verdict: the…, TestPairedDelta

### Community 63 - "test_app_zerogpu.py"
Cohesion: 0.14
Nodes (13): app_module(), fixture, Regression coverage for the ZeroGPU-hardware workaround in app.py. Background:…, Inject a fake `spaces` module so app.py's `import spaces` succeeds offline, and…, Static guard: if `import spaces` or the `@spaces.GPU` decorator is ever…, It must stay dead code: calling it would request a real ZeroGPU allocation (and…, The functions actually on the request path (get_pipeline, run_query_stream)…, `hardware:` in README-spaces.md is not a documented Spaces config key (only… (+5 more)

### Community 64 - "measure_parsing_latency"
Cohesion: 0.38
Nodes (4): measure_parsing_latency(), Measure PDF ingestion throughput (chars/sec, ms/PDF). Samples 20 PDFs…, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 65 - "eval_generator_for"
Cohesion: 0.16
Nodes (12): eval_generator_for(), The single generator decision for the eval stack. `derive_thresholds.py` sets…, The eval stack's generator choice must be one shared decision.…, Uses an injected loader so the test stays offline., Silently falling back to the stub would derive floors under semantics the…, Must assert the factory is CALLED, not merely imported. Verified 2026-08-12 by…, A factory both call is not enough - they must pass the same setting, or the…, test_both_eval_scripts_read_the_same_setting() (+4 more)

### Community 66 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 67 - "clopper_pearson_ci"
Cohesion: 0.22
Nodes (5): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, test_render_report_includes_ac1_and_provision(), The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 68 - "test_push_datasets.py"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default:…, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 69 - "scrape_regulations.py"
Cohesion: 0.20
Nodes (14): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY).…, (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'. Takes the LAST bracket group…, _record() (+6 more)

### Community 70 - "measure.py"
Cohesion: 0.29
Nodes (8): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), Automated metric collection for the SEBI Circular RAG pipeline. Six on-demand…, Run all (or specified) metrics sequentially., run_all_metrics(), test_retrieval_metrics()

### Community 71 - "measure_supersession_precision"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 72 - "test_audit_reg_edges.py"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 73 - "test_ingest_pdf.py"
Cohesion: 0.17
Nodes (12): _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash…, The mirror of the kerning case above. When the en-dash has spaces on BOTH sides…, 2011-era master circulars use "SEBI/<DEPT>/MC No.<n>/<serial>/<year>", matching…, Old-format PDFs (e.g. CIR/MRD/DP/ 11 /2012) split the number with a space…, test_ingest_extracts_metadata_and_lineage(), test_parse_meta_handles_2011_mc_number_format() (+4 more)

### Community 75 - "test_golden_v7_agreement.py"
Cohesion: 0.19
Nodes (15): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw element is…, _min_agreement_fixture(), Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):…, The kappa base-rate paradox: one label dominates, raw agreement is high, yet…, _same_provision_fixture(), test_claude_accuracy_ci_returns_exact_and_provision(), test_cohen_kappa_both_constant_and_identical_is_one() (+7 more)

### Community 76 - "answer_with_abstention"
Cohesion: 0.29
Nodes (12): answer_with_abstention(), faithfulness(), Check that every circular id the answer cites (in square brackets) was actually…, _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons,…, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful() (+4 more)

### Community 77 - "Handler"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 78 - "adjudicate_draft.py"
Cohesion: 0.21
Nodes (11): RuntimeError, adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response. (+3 more)

### Community 79 - "ce_query_reform_probe.py"
Cohesion: 0.38
Nodes (6): main(), _pool(), Probe: does query-side reformulation lift the CE score on the 4 CE_MISMATCH…, Return (ce_top, best relevant score, chunk_id of argmax)., Top-8 pool plus every relevant chunk, de-duplicated on chunk_id., _score()

### Community 80 - "AsofCaseResult"
Cohesion: 0.19
Nodes (17): AsofCaseResult, build_report(), Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Aggregate case results with an exact confidence interval. Pure function of the…, summarize(), Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid measurement;…, The headline number must be the 10 pipeline cases alone — the whole point of… (+9 more)

### Community 81 - "remap_doc_ids.py"
Cohesion: 0.33
Nodes (10): main(), Rewrite golden_v7 doc references after the corpus renumbering (2026-07-25…, remap(), Doc-id remapping after the 2026-07-25 corpus renumbering (Task 4)., _row(), test_input_rows_are_not_mutated(), test_matching_is_normalization_insensitive(), test_remaps_must_not_cite() (+2 more)

### Community 82 - "stats.py"
Cohesion: 0.22
Nodes (6): BootstrapCI, PairedResult, ProportionCI, Uncertainty quantification for benchmark runs. The golden set is n=56…, True when the randomization test rejects at 1 - confidence AND the paired…, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 83 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 84 - "audit_reg_edges.py"
Cohesion: 0.29
Nodes (9): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+1 more)

### Community 85 - "_provision_agree"
Cohesion: 0.18
Nodes (11): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using the…, Does this external vote confirm claude's label, at PROVISION level? Amendment…, _norm_ws(), Different chunk copies of the same quoted provision agree at provision level…, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction() (+3 more)

### Community 86 - "relabel_repooled.py"
Cohesion: 0.43
Nodes (6): _body(), main(), _norm(), pick(), Label the 7 rows re-pooled after the assemble_pool fix (2026-07-25 remediation…, (candidate, quote) pairs for this row: the answer_contains carrier first, then…

### Community 88 - "test_build_reg_edges.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 89 - "test_canary_generator.py"
Cohesion: 0.27
Nodes (8): _canary_jscode(), _ops_timeout(), The eval canary must fit its timeout and alert on real regressions. Measured…, n8n gives up first if its budget is smaller, so the ops timeout is never…, A threshold above the healthy value fires every run. citation_precision was…, test_alert_thresholds_sit_below_measured_baselines(), test_n8n_timeout_not_tighter_than_the_ops_budget(), test_ops_timeout_fits_the_measured_runtime()

### Community 90 - "MeasureResult"
Cohesion: 0.19
Nodes (8): main(), metrics_to_markdown(), Format results as a markdown table., MeasureReport, MeasureResult, Unit tests for sebi_rag.measure — automated metric collection., TestCLI, TestDataClasses

### Community 91 - "validate_corpus.py"
Cohesion: 0.38
Nodes (6): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair. Checks (per…, Every record's text must match the PDF its provenance names. Slow (re-extracts…, validate_deep()

### Community 92 - "parse_yes_no"
Cohesion: 0.67
Nodes (3): parse_yes_no(), First yes/no in the reply; unparseable fails OPEN (grounded=True) so the gate…, test_parse_yes_no()

### Community 93 - "test_repair_corpus_text.py"
Cohesion: 0.22
Nodes (4): main(), Repair the 6 records whose body text was overwritten with one shared circular's…, The repair map must name a real orphan PDF that parses to the circular_number…, test_numbers_normalize_distinctly()

### Community 94 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 96 - "build_regulatory_index"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 98 - "test_bench_retrieval_artifacts.py"
Cohesion: 0.22
Nodes (5): bench_retrieval must emit valid TREC alongside the legacy runfile., run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so every…, iv9/iv10 build a headered index beside data/index. Without an index override…, test_bench_retrieval_can_bench_an_alternate_index(), test_bench_retrieval_can_measure_the_reranked_order()

### Community 99 - "test_spaces.py"
Cohesion: 0.10
Nodes (23): ExternalSpaceGenerator, HFGenerator, HybridGenerator, External Space first; on ANY failure fall back to the local CPU model.…, Primary generator: calls a public LLM Space via gradio_client. Wired to…, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus). Never…, SpacesSettings (+15 more)

### Community 100 - "canary.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, SEBI_RAG_EVAL_GENERATOR, canary.sh script, TOKENIZERS_PARALLELISM

### Community 101 - "_resolve_governing_spans"
Cohesion: 0.36
Nodes (8): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote} spans, looked…, _resolve_governing_spans(), _pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool(), test_resolve_governing_spans_short_body_uses_whole_body(), test_resolve_governing_spans_uses_first_60_body_chars()

### Community 102 - "read_trec_run"
Cohesion: 0.33
Nodes (5): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), write_trec_run(), The archived runfiles embed section headings in the doc id., TestReadTrecRun

### Community 103 - "List of Circulars"
Cohesion: 0.25
Nodes (8): CIR/MRD/DP/19/2010, List of Circulars, List of Communications, MRD/DoP/Dep/Cir-29/2004, MRD/DoP/MAS – OW/16723/2010, Securities and Exchange Board of India, SEBI/MRD/SE/DEP/Cir-4/2005, SMDRP/NSDL/3055/1998

### Community 104 - "build_spaces_pipeline"
Cohesion: 0.23
Nodes (13): build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux). Parallel…, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row() (+5 more)

### Community 105 - "run.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 106 - "acquire_missing_pdfs.py"
Cohesion: 0.26
Nodes (12): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+4 more)

### Community 107 - "main"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

### Community 108 - "test_segment.py"
Cohesion: 0.18
Nodes (12): _body(), Chunker (segment.hierarchical_chunk) behaviour. Regression guard for the "5.…, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_absorption_respects_300_char_cap(), test_bare_parent_heading_folds_into_first_subsection(), test_bare_parent_heading_not_emitted_as_standalone_chunk(), test_governing_clause_not_duplicated(), test_leaf_single_line_provision_is_preserved_not_overmerged() (+4 more)

### Community 109 - "seed_v7.py"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 110 - "refresh.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 111 - "measure_mrr"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level. For each query, RR = 1/rank of first…, TestMRR

### Community 112 - "measure_retrieval_recall"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 113 - "measure_temporal_accuracy"
Cohesion: 0.43
Nodes (3): measure_temporal_accuracy(), Measure fraction of as_of queries returning correct pre-supersession circular…, TestTemporalAccuracy

### Community 114 - "reg_lineage.py"
Cohesion: 0.29
Nodes (6): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus., derive_regulatory_basis(), Regulatory-basis status of one circular from its resolved regulations.…, test_derive_regulatory_basis_truth_table()

### Community 115 - "test_app_asof.py"
Cohesion: 0.29
Nodes (3): app_module(), fixture, As-of date plumbing in the Spaces UI (app.py).

### Community 116 - ".query"
Cohesion: 0.25
Nodes (4): Answer, _LineageAwareReranker, Reranker wrapper that re-applies lineage handling to its output. The paraphrase…, As-of exclusion or supersession demotion, applied to a reranked list. Extracted…

### Community 117 - "test_build_index_out_dir.py"
Cohesion: 0.29
Nodes (5): build_index must be able to target a scratch index directory. The iv9/iv10…, A --out flag that is parsed but ignored is worse than none: it reads as safe…, lineage.json lands next to the index it describes; writing it into data/index…, test_build_index_saves_to_the_resolved_out_dir_not_the_constant(), test_lineage_follows_the_out_dir()

### Community 118 - "main"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl()

### Community 119 - "parse_meta"
Cohesion: 0.13
Nodes (16): Pattern, main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), _iso_date(), _labeled_date(), parse_meta(), _primary_number() (+8 more)

### Community 120 - "DenseIndex"
Cohesion: 0.33
Nodes (3): DenseIndex, ndarray, FAISS IndexFlatIP over L2-normalized vectors (cosine).

### Community 121 - "autoresearch.sh"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 122 - "sweep_rrf_k.py"
Cohesion: 0.27
Nodes (8): main(), mrr(), ndcg_at_k(), Sweep RRF k_const values on the golden set. No index rebuild needed., recall_at_k(), Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 124 - "test_context_recall.py"
Cohesion: 0.46
Nodes (7): _chunk(), The gate must measure the context window, not just the fusion list.…, An abstention still had a context window; measuring retrieval delivery must not…, _reranked(), test_answer_records_the_context_ids_it_used(), test_context_ids_populated_even_when_abstaining(), test_context_ids_respect_top_k()

### Community 125 - "Overall Evaluation Summary"
Cohesion: 0.67
Nodes (4): Failure: asof-p2, Overall Evaluation Summary, Pipeline Evaluation Results, Selector Evaluation Results

### Community 128 - "Golden v7 Human Packet"
Cohesion: 0.67
Nodes (3): Golden v7 Human Packet, SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026, SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122

### Community 136 - "test_benchmark.py"
Cohesion: 0.36
Nodes (6): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields(), test_trec_run_and_research_judges_are_sidecar_only()

### Community 144 - "test_integration_e2e.py"
Cohesion: 0.33
Nodes (4): _ollama_up(), pipeline(), fixture, Step 12 — end-to-end RAG integration test with the REAL stack. bge-m3 (MPS) +…

### Community 150 - "_doc"
Cohesion: 0.23
Nodes (13): aggregate(), eligible(), main(), measure(), Preregistered cohort measurement for supersession confidence tiering. Spec:…, Answerable, non-as_of, with gold citations: the rows citation metrics exist for., cited_docs(), metrics() (+5 more)

### Community 156 - "bench_rerankers.py"
Cohesion: 0.38
Nodes (6): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,…

### Community 158 - "measure_context_precision"
Cohesion: 0.50
Nodes (3): measure_context_precision(), Fraction of top-k chunks from relevant circulars. Unlike recall@k (which is…, TestContextPrecision

### Community 161 - "_rejoin_split"
Cohesion: 0.50
Nodes (4): Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge()

## Knowledge Gaps
- **49 isolated node(s):** `measure.sh script`, `autoresearch.sh script`, `PYTHONPATH`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS` (+44 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `eval_harness.py`, `SpladeIndex`, `test_benchmark.py`, `test_lineage.py`, `RAGPipeline`, `test_attribution.py`, `context_headers.py`, `test_selective_citations.py`, `ExtractiveStubGenerator`, `test_paraphrase_rescue.py`, `HybridRetriever`, `benchmark.py`, `build_lineage`, `SubjectSimJudge`, `validate_golden_v7`, `test_hyde.py`, `Qwen3MLXReranker`, `answer_with_abstention`, `test_injection.py`, `test_spaces.py`, `build_spaces_pipeline`, `main`, `.query`, `sweep_rrf_k.py`, `test_context_recall.py`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `eval_harness.py`, `test_integration_e2e.py`, `_doc`, `test_paraphrase_rescue.py`, `HybridRetriever`, `measure_context_precision`, `api.py`, `benchmark.py`, `build_lineage`, `Chunk`, `test_eval_harness_v7.py`, `measure_parsing_latency`, `measure.py`, `measure_supersession_precision`, `build_spaces_pipeline`, `measure_mrr`, `measure_retrieval_recall`, `measure_temporal_accuracy`, `.query`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `main()` connect `build_lineage` to `ValueError`, `eval_harness.py`, `benchmark.py`, `read_trec_run`, `SpladeIndex`, `Settings`, `RAGPipeline`, `_doc`, `ExtractiveStubGenerator`, `test_hyde.py`, `HybridRetriever`, `per_query_recall`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 59 inferred relationships involving `Chunk` (e.g. with `dataset_quality()` and `NLIAttributionScorer`) actually correct?**
  _`Chunk` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 45 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `run()`) actually correct?**
  _`RAGPipeline` has 45 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `ExtractiveStubGenerator` (e.g. with `get_pipeline()` and `run()`) actually correct?**
  _`ExtractiveStubGenerator` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `HybridRetriever` (e.g. with `main()` and `main()`) actually correct?**
  _`HybridRetriever` has 32 INFERRED edges - model-reasoned connections that need verification._