# Graph Report - SEBI circular RAG  (2026-08-19)

## Corpus Check
- 205 files · ~191,400 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2618 nodes · 5424 edges · 169 communities (137 shown, 32 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 488 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7aac150d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- export_datasets.py
- ValueError
- generate.py
- telemetry_engine.py
- test_golden_v7_packet.py
- Frame
- SpladeIndex
- test_golden_v7_gate.py
- build_lineage
- backfill_escalations.py
- .grounded
- test_regulations.py
- RAGPipeline
- test_attribution.py
- test_spaces.py
- load_circulars
- test_selective_citations.py
- sebi_rag/eval_asof.py
- test_reg_lineage.py
- extract_citations
- test_dataset_cards.py
- test_ui.py
- derive_validity
- test_golden_v7_gemini.py
- _is_non_sebi_domain
- test_export_datasets.py
- validate
- answer_with_abstention
- test_paraphrase_rescue.py
- _row
- .build_incremental
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
- HybridRetriever
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
- .build
- test_hyde.py
- stats.py
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
- parse_meta
- Embedder
- test_golden_v7_agreement.py
- test_certainty.py
- Handler
- adjudicate_draft.py
- ce_query_reform_probe.py
- build_report
- validate_corpus.py
- paraphrase_rescue.py
- trace_failure.py
- audit_reg_edges.py
- _provision_agree
- adjudicate
- faithfulness
- test_build_reg_edges.py
- test_canary_generator.py
- MeasureResult
- _doc
- consolidation_edges
- test_repair_corpus_text.py
- test_injection.py
- build_golden.py
- build_regulatory_index
- test_acquire_missing.py
- test_bench_retrieval_artifacts.py
- _HallucinatingGenerator
- canary.sh
- _resolve_governing_spans
- read_trec_run
- List of Circulars
- build_spaces_pipeline
- run.sh
- acquire_missing_pdfs.py
- main
- hierarchical_chunk
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
- Embedder
- autoresearch.sh
- sweep_rrf_k.py
- reg_citations.py
- test_context_recall.py
- Overall Evaluation Summary
- discover_new.py
- test_ingest_refs.py
- Golden v7 Human Packet
- deploy_space.py
- discover.sh
- upload_spaces_index.py
- relabel_repooled.py
- measure.sh
- run_ops.sh
- scripts/autoresearch/__init__.py
- test_benchmark.py
- dev.sh
- notify.sh
- start_phoenix.sh
- sebi_rag/autoresearch/__init__.py
- remap_doc_ids.py
- conftest.py
- Master Appendix (Mutual Funds)
- test_integration_e2e.py
- _alias_keys
- SEBI Master Circular CIR/DNPD/1/2012
- Optimize Slash Command
- Seen Circular IDs
- Label Escalations
- supersession_tier_cohort.py
- Unresolved Regulations
- Hugging Face Spaces Requirements
- golden_v7/__init__.py
- Master Appendix (Depository)
- SEBI Regulations Listing
- bench_rerankers.py
- rescore_runs.py
- measure_context_precision
- load_regulations
- SparseIndex
- _rejoin_split
- reg_display_name
- _s_mc_no
- test_annotation_adds_no_circular_meta_field
- test_every_alias_target_is_in_force_or_has_a_succession_entry
- test_settings_citation_scorer_enabled_true
- test_settings_citation_scorer_enabled_false
- Path

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 97 edges
2. `RAGPipeline` - 44 edges
3. `HybridRetriever` - 40 edges
4. `Settings` - 37 edges
5. `hierarchical_chunk()` - 37 edges
6. `build_lineage()` - 36 edges
7. `ExtractiveStubGenerator` - 36 edges
8. `HashEmbedder` - 32 edges
9. `Lineage` - 31 edges
10. `answer_with_abstention()` - 30 edges

## Surprising Connections (you probably didn't know these)
- `test_build_lineage_edges_tiered()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_build_lineage_inferred_master_topic_edge()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_master_circular_reissue_supersession()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_supersession_detected_from_text()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Evaluation Run 2026-08-15** — eval_runs_eval_asof_2026_08_15_pipeline, eval_runs_eval_asof_2026_08_15_selector, eval_runs_eval_asof_2026_08_15_overall [EXTRACTED 1.00]
- **SEBI Regulatory Framework** — tests_fixtures_master_appendix_pre2015_sebi, tests_fixtures_master_appendix_pre2015_circulars, tests_fixtures_master_appendix_pre2015_communications [INFERRED 0.90]

## Communities (169 total, 32 thin omitted)

### Community 0 - "export_datasets.py"
Cohesion: 0.06
Nodes (70): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+62 more)

### Community 1 - "ValueError"
Cohesion: 0.06
Nodes (61): Rankings, _assert_fixed_tail(), convert_run_dir(), main(), Path, Back-convert archived runfiles into standards-compliant TREC artifacts. The…, Trailing field of the first line; also the whitespace precondition check., read_trec_run assumes qid and tag carry no whitespace. Verify per line. (+53 more)

### Community 2 - "generate.py"
Cohesion: 0.07
Nodes (35): Ground truth: what do the 4 CE_MISMATCH rows actually DO in production? The…, Preregistered cohort measurement for the CE paraphrase rescue. Spec:…, What does the 0.05 cross-encoder score floor actually catch?…, Capture-once margin sweep for B' selective citations. One pipeline pass over…, log(), Margin sweep for B' selective citations on the golden_v7 adjudicated set. One…, run(), Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)… (+27 more)

### Community 3 - "telemetry_engine.py"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 4 - "test_golden_v7_packet.py"
Cohesion: 0.07
Nodes (54): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+46 more)

### Community 5 - "Frame"
Cohesion: 0.15
Nodes (22): guard_pair(), Refuse any paired comparison that spans two frames. The archive covers four…, assert_comparable(), Frame, frame_of(), IncomparableFramesError, Epoch and frame identity for comparable measurement. The corpus drifts on a…, Raised when a paired comparison spans two frames. (+14 more)

### Community 6 - "SpladeIndex"
Cohesion: 0.07
Nodes (29): RuntimeError, main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.… (+21 more)

### Community 7 - "test_golden_v7_gate.py"
Cohesion: 0.07
Nodes (43): derive_floors(), metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the…, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,…, True iff every floor's metric is present in `report_gate` and meets it. Missing…, select_golden() (+35 more)

### Community 8 - "build_lineage"
Cohesion: 0.09
Nodes (38): contexts_for(), demote_superseded(), detect_relations(), detect_relations_ex(), Down-weight reranked (chunk, score) pairs from superseded circulars and     re-s, Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window() (+30 more)

### Community 9 - "backfill_escalations.py"
Cohesion: 0.09
Nodes (38): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+30 more)

### Community 10 - ".grounded"
Cohesion: 0.15
Nodes (11): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), v2 protocol: closed-set identification instead of yes/no judgment. Naming which…, True iff the reply names a valid excerpt number. 'none' or anything unparseable…, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the gate… (+3 more)

### Community 11 - "test_regulations.py"
Cohesion: 0.15
Nodes (16): name_tokens(), Resolve a cited regulation name+year to a canonical reg_id. Returns (reg_id,…, Comparison tokens: lowercased, punctuation-split, stopwords dropped, naively…, resolve_regulation(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6)., Singular/plural and dropped-stopword variants normalise to identical token…, A citation carrying a spurious extra token still resolves, but only via the…, test_acronym_aliases_resolve_as_explicit_text() (+8 more)

### Community 12 - "RAGPipeline"
Cohesion: 0.09
Nodes (31): Embedder, Reranker, _build_chunks(), _build_pipeline(), _FixedReranker, _master_reissue_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline.  Runs fully offline (HashEmbed, Offline pipeline whose single circular rests on a repealed regulation. (+23 more)

### Community 13 - "test_attribution.py"
Cohesion: 0.07
Nodes (33): entailment_index(), NLIAttributionScorer, NLI attribution scoring for B' citation selection. B' asks "does this context…, Index of the entailment class in a model's label map. Read from the checkpoint…, Scores each context by P(entailment) of the answer given that context.…, Wrap an already-constructed cross-encoder (also the test seam)., _softmax(), pick_device() (+25 more)

### Community 14 - "test_spaces.py"
Cohesion: 0.15
Nodes (15): _grounded_prompt(), F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and the…, ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo. All classes implement…, External Space first; on ANY failure fall back to the local CPU model.…, Primary generator: calls a public LLM Space via gradio_client. Wired to… (+7 more)

### Community 15 - "load_circulars"
Cohesion: 0.09
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 16 - "test_selective_citations.py"
Cohesion: 0.12
Nodes (32): citation_scorer_for(), The single enable/disable AND backend decision for B'. Returns None when…, Context ids the answer rests on. Scores each context's answer-relevance via…, select_citations(), _chunk(), _FakeReranker, Tests for B' selective citations: select_citations() and its integration., The backend choice must go through the same single decision point as the enable… (+24 more)

### Community 17 - "sebi_rag/eval_asof.py"
Cohesion: 0.06
Nodes (42): Path, Benchmark MLX generators on the golden set: faithfulness, groundedness,…, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped…, scripts/eval_asof.py, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the…, False positive check — hybrid gate over abstain=True rows. Runs the pipeline…, sebi_rag/eval_asof.py, AsofCaseResult (+34 more)

### Community 18 - "test_reg_lineage.py"
Cohesion: 0.15
Nodes (29): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+21 more)

### Community 19 - "extract_citations"
Cohesion: 0.13
Nodes (24): extract_citations(), All regulation citations in a circular, one per occurrence (not deduped).…, Citation extraction from circular text (spec 2026-07-23 §3.3)., Real corpus artefact: PDF table extraction interleaves columns, landing a…, The sole legitimate title ending in the word must survive the guard., test_alphanumeric_clause_is_captured(), test_circular_number_spliced_into_a_title_is_rejected(), test_citation_is_hashable() (+16 more)

### Community 20 - "test_dataset_cards.py"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 21 - "test_ui.py"
Cohesion: 0.06
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 22 - "derive_validity"
Cohesion: 0.12
Nodes (8): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation. Locked…, Validity of one circular from the tiered edge list (any scope: the function…, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., TestClassifyCircularType, TestDeriveValidity

### Community 23 - "test_golden_v7_gemini.py"
Cohesion: 0.12
Nodes (26): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply… (+18 more)

### Community 24 - "_is_non_sebi_domain"
Cohesion: 0.10
Nodes (29): _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain. Case-…, The non-SEBI domain filter must match words, not substrings. Shipped 2026-07-30…, Any single-token keyword <= 5 chars is a substring hazard. Embedding it inside…, Query mentioning both SEBI and RBI should NOT abstain — SEBI intent wins., Empty query should not trigger the non-SEBI filter., FEMA keyword in a SEBI context should NOT abstain — SEBI intent wins., The exact query that exposed the bug. (+21 more)

### Community 25 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 26 - "validate"
Cohesion: 0.13
Nodes (31): load_circulars(), Path, Path, corpus.load_circulars edge-case coverage. load_circulars reads a JSONL corpus…, Provided optional fields are passed through to CircularMeta., Multiple records produce multiple chunks., Blank lines between records are silently skipped., Malformed JSON raises ValueError (json.loads default). (+23 more)

### Community 27 - "answer_with_abstention"
Cohesion: 0.14
Nodes (24): ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., rerank_top exactly at 0.85 overrides judge abstention (HYBRID_THRESHOLD=0.85)., rerank_top just below 0.85 does NOT override judge abstention., When no judge is present, hybrid gate logic must be inert (no crash)., Unrelated query vs context: subject_sim < 0.42 → grounded() returns False. (+16 more)

### Community 28 - "test_paraphrase_rescue.py"
Cohesion: 0.11
Nodes (35): is_degenerate(), Paraphrase rescue for the cross-encoder score floor. Preregistered in…, Re-score `pool` with a rewritten query when `reranked` is below `floor`.…, Fixed rewrite, for tests and for replaying a preregistered rewrite., True when `rewritten` is unusable and the rescue should be abandoned.…, rescue_pool(), StaticQueryRewriter, _chunk() (+27 more)

### Community 29 - "_row"
Cohesion: 0.12
Nodes (27): decide(), Spec sec7 promotion rules for one row. `votes_by_annotator` is this row's votes…, Abstain rows have no explicit claude vote at all (Task 8 never judged them) -…, Both externals independently think something DOES govern (disputing the…, The LLM leg is whichever single non-claude/non-human annotator voted - "qwen"…, Amendment 2026-07-26 (user-approved): the promotion unit is the PROVISION, not…, External marked claude's chunk governing plus extras: claude's label is…, The abstain protocol can never emit non-empty governing (no letters are… (+19 more)

### Community 30 - ".build_incremental"
Cohesion: 0.36
Nodes (7): F3 (ADR-001): encode only new/changed documents; reuse cached embedding rows…, _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are…, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 31 - "per_query_recall"
Cohesion: 0.12
Nodes (17): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.…, validate_golden(), Ten chunks of one circular must not crowd the cutoff: the k applies to unique…, TestPerQueryRecall, Answerable-but-unjudged rows are excluded from metrics, never scored 0.… (+9 more)

### Community 32 - "test_label_tier.py"
Cohesion: 0.12
Nodes (20): classify_tier(), human_reviewed_ids(), main(), Path, Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.…, Map provenance to the controlled vocabulary. `human_reviewed` (row appears in…, Row ids present in the human labelling packet., Controlled-vocabulary label_tier over golden_v7 (spec A §8.3). (+12 more)

### Community 33 - "gemini_adjudicate.py"
Cohesion: 0.11
Nodes (23): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec… (+15 more)

### Community 34 - "scrape_sebi.py"
Cohesion: 0.26
Nodes (14): discover(), _listing_url(), main(), _page(), _parse_date(), parse_rows(), pdf_url_for(), date (+6 more)

### Community 35 - "app.py"
Cohesion: 0.13
Nodes (21): _append_message(), _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_citations_md(), get_pipeline(), _on_submit(), _parse_as_of() (+13 more)

### Community 36 - "api.py"
Cohesion: 0.07
Nodes (32): BaseModel, FastAPI, integration, Build the dense+sparse index once and persist it (run after corpus changes).…, _citation_meta(), CitationMeta, _compute_kwargs(), create_app() (+24 more)

### Community 37 - "benchmark.py"
Cohesion: 0.19
Nodes (22): main(), Emit TREC qrels for an eval set, keyed by its golden_sha256. .venv/bin/python…, beir_corpus_rows(), beir_query_rows(), build_golden_v6(), dir_fingerprint(), enrich_golden_item(), export_beir() (+14 more)

### Community 38 - "sebi_rag/verify_master.py"
Cohesion: 0.19
Nodes (21): sebi_rag/verify_master.py, diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13). Pure functions only:…, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows. (+13 more)

### Community 39 - "extract_misses.py"
Cohesion: 0.14
Nodes (23): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any… (+15 more)

### Community 40 - "agreement.py"
Cohesion: 0.15
Nodes (21): _claude_accuracy_ci(), gwet_ac1(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation…, Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a prevalence-… (+13 more)

### Community 41 - "test_golden_v7_local.py"
Cohesion: 0.15
Nodes (19): _extract_text(), Qwen-family models may emit <think>...</think> reasoning as inline text,…, Anthropic Messages response -> reply text: concatenates `text` content blocks,…, _strip_thinking(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external…, Five pilot rows from five strata measure more than five from one - the gemini…, Vote records must say annotator "qwen" (never reuse "gemini" - the agreement… (+11 more)

### Community 42 - "Settings"
Cohesion: 0.17
Nodes (22): Score-floor false-abstention diagnostics (hybrid-gate-prereg 2026-08-13, §10b).…, _as_bool(), _get(), Path, Central configuration: config.toml defaults, overridden by SEBI_RAG_* env vars.…, Settings.load() plus the [spaces] table as settings.spaces.* Load order per…, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default may… (+14 more)

### Community 43 - "test_golden_v7_pool.py"
Cohesion: 0.22
Nodes (13): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, LexicalReranker, Deterministic query-coverage reranker (test/fallback). Score = fraction of…, One gold doc with `n` chunks that ALL contain the word "broker", so a…, Regression (2026-07-25): a must_contain literal matching many gold-doc chunks…, _retriever() (+5 more)

### Community 44 - "HybridRetriever"
Cohesion: 0.15
Nodes (33): main(), main(), main(), Build the full pipeline with real models., real_pipeline(), main(), main(), smoke_pipeline() (+25 more)

### Community 45 - "publish_hf.py"
Cohesion: 0.19
Nodes (18): export_golden_v7_arrow(), log(), main(), Path, Run export_datasets.py then add golden_v7 Arrow config., Upload dist/datasets/ to HF dataset repo., Run make index to rebuild FAISS+BM25 before upload., Upload data/index/ to HF index repo. (+10 more)

### Community 46 - "ingest_pdf.py"
Cohesion: 0.17
Nodes (17): Re-derive circular number + dates from each record's stored text and rewrite…, _existing_numbers(), extract_text(), ingest(), main(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars. Drop a circular PDF into data/raw/ and… (+9 more)

### Community 47 - "ui.py"
Cohesion: 0.21
Nodes (13): _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_outputs_md(), _parse_as_of(), Return empty markdown placeholder for streaming., Generator that streams the answer while updating chat history., Return a color-coded confidence badge string. (+5 more)

### Community 48 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 49 - "Chunk"
Cohesion: 0.14
Nodes (11): Generator, Judge, MLXGenerator, Protocol, Apple-Silicon-native generation via MLX-LM (D6 preferred runtime). Loads a…, _extracts(), MLXQueryRewriter, Local MLX-LM rewriter. Greedy decoding -> deterministic. (+3 more)

### Community 50 - "audit_label_provenance.py"
Cohesion: 0.21
Nodes (15): audit(), collect_artifacts(), _ids_from_csv(), _ids_from_dir(), _ids_from_jsonl(), main(), Path, Report what the annotation artifacts can account for, before classifying.… (+7 more)

### Community 51 - "test_golden_v7_resolver.py"
Cohesion: 0.21
Nodes (16): BenchmarkIssue, chunks_by_doc(), _norm_ws(), Span {doc, quote} -> matching chunk ids (all overlap matches count). Legacy…, resolve_chunk_spans(), _span_resolution_issues(), normalize_circular_number(), Canonical COMPARISON key for a circular number: strip whitespace and trailing… (+8 more)

### Community 52 - "SubjectSimJudge"
Cohesion: 0.17
Nodes (10): ADOPTED gate (eval_gate round 3): deterministic groundedness signal — max…, Max cosine(query, doc subject line) over contexts — the primary gate signal,…, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge, subject_sim == threshold (0.42) passes the gate (>= comparison)., section_score == section_threshold (0.60) passes via second tier., test_section_score_exactly_at_threshold_passes(), test_subject_sim_exactly_at_threshold_passes() (+2 more)

### Community 53 - "bootstrap_ci"
Cohesion: 0.18
Nodes (8): bootstrap_ci(), BootstrapCI, ProportionCI, Uncertainty quantification for benchmark runs. The golden set is n=56…, Percentile bootstrap interval for the mean of per-query scores., Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests)., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 54 - "local_adjudicate.py"
Cohesion: 0.19
Nodes (15): Transient-failure predicate for the real Gemini call: rate limiting (429) and…, Same per-row deterministic shuffle as make_packet.py's write_packet:…, _should_retry(), _shuffled_candidates(), _current_model(), main(), pilot(), _pilot_ids() (+7 more)

### Community 55 - "_bootstrap_ci"
Cohesion: 0.15
Nodes (10): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Path, Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict. (+2 more)

### Community 56 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 57 - "test_eval_harness_v7.py"
Cohesion: 0.49
Nodes (10): run_eval(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-…, _row(), test_as_of_is_passed_to_pipeline(), test_chunk_metrics_computed_for_span_rows(), test_gate_is_none_when_nothing_adjudicated(), test_gate_subreport_covers_only_adjudicated() (+2 more)

### Community 58 - "apply"
Cohesion: 0.29
Nodes (7): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions` (keyed by…, test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only(), test_apply_queue_decision_leaves_row_untouched(), test_apply_row_without_a_decision_is_never_touched()

### Community 60 - ".build"
Cohesion: 0.22
Nodes (13): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and…, Query-side lexical expansion (intervention #2, glossary variant).…, test_all_five_sparse_failure_queries_expand(), test_expanded_sparse_query_hits_statutory_chunk(), test_lay_term_gains_statutory_synonym(), test_multiword_synonym_splits_into_tokens() (+5 more)

### Community 61 - "test_hyde.py"
Cohesion: 0.17
Nodes (11): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —…, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_none_and_empty_hyde_are_identical_to_baseline() (+3 more)

### Community 62 - "stats.py"
Cohesion: 0.19
Nodes (7): paired_delta(), PairedResult, Compare run `b` against run `a` on their shared queries. Returns mean_b -…, True when the randomization test rejects at 1 - confidence AND the paired…, Randomization p-values use the (count+1)/(n+1) estimator, so a p-value of…, One query flipping out of 56 is exactly the iv9-style verdict: the…, TestPairedDelta

### Community 63 - "test_app_zerogpu.py"
Cohesion: 0.14
Nodes (13): app_module(), fixture, Regression coverage for the ZeroGPU-hardware workaround in app.py. Background:…, Inject a fake `spaces` module so app.py's `import spaces` succeeds offline, and…, Static guard: if `import spaces` or the `@spaces.GPU` decorator is ever…, It must stay dead code: calling it would request a real ZeroGPU allocation (and…, The functions actually on the request path (get_pipeline, run_query_stream)…, `hardware:` in README-spaces.md is not a documented Spaces config key (only… (+5 more)

### Community 64 - "measure_parsing_latency"
Cohesion: 0.32
Nodes (5): measure_parsing_latency(), Measure PDF ingestion throughput (chars/sec, ms/PDF). Samples 20 PDFs…, CircularMeta, Test with a dummy PDF file — should not crash., TestParsingLatency

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
Cohesion: 0.26
Nodes (11): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), Automated metric collection for the SEBI Circular RAG pipeline. Six on-demand…, _internal(), Prove the internal retrieval metrics are the standard ones. Skips unless the…, _standard() (+3 more)

### Community 71 - "measure_supersession_precision"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 72 - "test_audit_reg_edges.py"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 73 - "parse_meta"
Cohesion: 0.17
Nodes (12): _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash…, The mirror of the kerning case above. When the en-dash has spaces on BOTH sides…, 2011-era master circulars use "SEBI/<DEPT>/MC No.<n>/<serial>/<year>", matching…, Old-format PDFs (e.g. CIR/MRD/DP/ 11 /2012) split the number with a space…, test_ingest_extracts_metadata_and_lineage(), test_parse_meta_handles_2011_mc_number_format() (+4 more)

### Community 75 - "test_golden_v7_agreement.py"
Cohesion: 0.19
Nodes (15): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw element is…, _min_agreement_fixture(), Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):…, The kappa base-rate paradox: one label dominates, raw agreement is high, yet…, _same_provision_fixture(), test_claude_accuracy_ci_returns_exact_and_provision(), test_cohen_kappa_both_constant_and_identical_is_one() (+7 more)

### Community 76 - "test_certainty.py"
Cohesion: 0.29
Nodes (12): Answer, answer_with_abstention(), _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons,…, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful(), test_no_context_reason_when_top_k_zero() (+4 more)

### Community 77 - "Handler"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 78 - "adjudicate_draft.py"
Cohesion: 0.29
Nodes (10): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+2 more)

### Community 79 - "ce_query_reform_probe.py"
Cohesion: 0.38
Nodes (6): main(), _pool(), Probe: does query-side reformulation lift the CE score on the 4 CE_MISMATCH…, Return (ce_top, best relevant score, chunk_id of argmax)., Top-8 pool plus every relevant chunk, de-duplicated on chunk_id., _score()

### Community 80 - "build_report"
Cohesion: 0.31
Nodes (10): build_report(), Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid measurement;…, The headline number must be the 10 pipeline cases alone — the whole point of…, _results(), test_pipeline_metrics_are_not_polluted_by_selector_cases(), test_pooled_overall_carries_no_interval() (+2 more)

### Community 81 - "validate_corpus.py"
Cohesion: 0.14
Nodes (15): load_runs(), main(), Path, Assign epochs to the archived runs and write the epoch registry. Every run's…, assign_epochs(), load_epoch_registry(), Path, Number corpora E1..En by earliest observed run timestamp. Deterministic and… (+7 more)

### Community 82 - "paraphrase_rescue.py"
Cohesion: 0.25
Nodes (7): Protocol, query_rewriter_for(), QueryRewriter, Factory mirroring `generate.citation_scorer_for`: None when disabled., Rewrites a lay-vocabulary query into statutory vocabulary. Returns None when it…, Disabled must not construct the rewriter — it would load an MLX model., test_factory_returns_none_when_disabled()

### Community 83 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 84 - "audit_reg_edges.py"
Cohesion: 0.33
Nodes (9): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+1 more)

### Community 85 - "_provision_agree"
Cohesion: 0.20
Nodes (10): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using the…, Does this external vote confirm claude's label, at PROVISION level? Amendment…, Different chunk copies of the same quoted provision agree at provision level…, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction(), test_provision_agree_disjoint_without_pool_is_false() (+2 more)

### Community 86 - "adjudicate"
Cohesion: 0.22
Nodes (10): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt) -> str`…, Scans the per-row cache for `ids` and returns the ones flagged parse_error:…, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct from a well-…, Defensive: an id that was never adjudicated (no cache file at all) is not…, test_adjudicate_marks_parse_error_for_garbled_abstain_protocol_reply() (+2 more)

### Community 87 - "faithfulness"
Cohesion: 0.29
Nodes (6): faithfulness(), Check that every circular id the answer cites (in square brackets) was actually…, _HallucinatingGenerator, Faithfulness: catch answers that cite circulars not in the retrieved context., test_faithfulness_scoring(), test_pipeline_flags_hallucinated_citation()

### Community 88 - "test_build_reg_edges.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 89 - "test_canary_generator.py"
Cohesion: 0.27
Nodes (8): _canary_jscode(), _ops_timeout(), The eval canary must fit its timeout and alert on real regressions. Measured…, n8n gives up first if its budget is smaller, so the ops timeout is never…, A threshold above the healthy value fires every run. citation_precision was…, test_alert_thresholds_sit_below_measured_baselines(), test_n8n_timeout_not_tighter_than_the_ops_budget(), test_ops_timeout_fits_the_measured_runtime()

### Community 90 - "MeasureResult"
Cohesion: 0.19
Nodes (8): main(), metrics_to_markdown(), Format results as a markdown table., MeasureReport, MeasureResult, Unit tests for sebi_rag.measure — automated metric collection., TestCLI, TestDataClasses

### Community 91 - "_doc"
Cohesion: 0.47
Nodes (6): cited_docs(), metrics(), evaluate(), _doc(), _eval_item(), _unique()

### Community 92 - "consolidation_edges"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans…, _master(), test_annotate_idempotent() (+7 more)

### Community 93 - "test_repair_corpus_text.py"
Cohesion: 0.22
Nodes (4): main(), Repair the 6 records whose body text was overwritten with one shared circular's…, The repair map must name a real orphan PDF that parses to the circular_number…, test_numbers_normalize_distinctly()

### Community 94 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 95 - "build_golden.py"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 96 - "build_regulatory_index"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 98 - "test_bench_retrieval_artifacts.py"
Cohesion: 0.22
Nodes (5): bench_retrieval must emit valid TREC alongside the legacy runfile., run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so every…, iv9/iv10 build a headered index beside data/index. Without an index override…, test_bench_retrieval_can_bench_an_alternate_index(), test_bench_retrieval_can_measure_the_reranked_order()

### Community 99 - "_HallucinatingGenerator"
Cohesion: 0.15
Nodes (11): _Boom, _Canned, _hybrid(), fixture, HF Spaces path: corpus_spaces loader mapping + HybridGenerator fallback. Fully…, settings(), _stub_rows(), test_chunks_config_refuses_header_and_maps_fields() (+3 more)

### Community 100 - "canary.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, SEBI_RAG_EVAL_GENERATOR, canary.sh script, TOKENIZERS_PARALLELISM

### Community 101 - "_resolve_governing_spans"
Cohesion: 0.36
Nodes (8): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote} spans, looked…, _resolve_governing_spans(), _pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool(), test_resolve_governing_spans_short_body_uses_whole_body(), test_resolve_governing_spans_uses_first_60_body_chars()

### Community 102 - "read_trec_run"
Cohesion: 0.27
Nodes (6): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), write_trec_run(), The archived runfiles embed section headings in the doc id., End-to-end guarantee behind the re-scoring script: replaying a runfile yields…, TestReadTrecRun

### Community 103 - "List of Circulars"
Cohesion: 0.25
Nodes (8): CIR/MRD/DP/19/2010, List of Circulars, List of Communications, MRD/DoP/Dep/Cir-29/2004, MRD/DoP/MAS – OW/16723/2010, Securities and Exchange Board of India, SEBI/MRD/SE/DEP/Cir-4/2005, SMDRP/NSDL/3055/1998

### Community 104 - "build_spaces_pipeline"
Cohesion: 0.29
Nodes (10): _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path). Loads the…, One HF dataset config as plain dicts (network; cached by `datasets`)., Full-circular records (dicts) for build_lineage() — always the "corpus" config… (+2 more)

### Community 105 - "run.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 106 - "acquire_missing_pdfs.py"
Cohesion: 0.26
Nodes (12): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+4 more)

### Community 107 - "main"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

### Community 108 - "hierarchical_chunk"
Cohesion: 0.13
Nodes (22): Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., hierarchical_chunk(), _paragraphs(), Segmentation: hierarchical chunking + metadata + stable citation IDs. Minimal,…, Split into units each <= max_chars. PDF-extracted text often lacks blank-line…, Document -> section -> paragraph chunks with stable IDs. A "section" is…, _pipeline(), P1 evaluation-harness test (offline). Loads the real seed corpus… (+14 more)

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
Cohesion: 0.15
Nodes (13): derive_regulatory_basis(), _jaccard(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6). Regulations…, Regulatory-basis status of one circular from its resolved regulations.…, Deterministic, stable identity slug. This is the edge target and join key., reg_id(), RegulationMeta, _slug() (+5 more)

### Community 115 - "test_app_asof.py"
Cohesion: 0.29
Nodes (3): app_module(), fixture, As-of date plumbing in the Spaces UI (app.py).

### Community 116 - ".query"
Cohesion: 0.31
Nodes (5): Answer, _LineageAwareReranker, Chunk, Reranker wrapper that re-applies lineage handling to its output.      The paraph, As-of exclusion or supersession demotion, applied to a reranked list.          E

### Community 117 - "test_build_index_out_dir.py"
Cohesion: 0.29
Nodes (5): build_index must be able to target a scratch index directory. The iv9/iv10…, A --out flag that is parsed but ignored is worse than none: it reads as safe…, lineage.json lands next to the index it describes; writing it into data/index…, test_build_index_saves_to_the_resolved_out_dir_not_the_constant(), test_lineage_follows_the_out_dir()

### Community 118 - "main"
Cohesion: 0.29
Nodes (8): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl(), _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus.

### Community 119 - "parse_meta"
Cohesion: 0.24
Nodes (9): Pattern, main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), _iso_date(), _labeled_date(), parse_meta(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars. (+1 more)

### Community 120 - "Embedder"
Cohesion: 0.28
Nodes (5): Embedder, Protocol, DenseIndex, ndarray, FAISS IndexFlatIP over L2-normalized vectors (cosine).

### Community 121 - "autoresearch.sh"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 122 - "sweep_rrf_k.py"
Cohesion: 0.31
Nodes (7): main(), mrr(), ndcg_at_k(), Sweep RRF k_const values on the golden set. No index rebuild needed., recall_at_k(), Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse()

### Community 123 - "reg_citations.py"
Cohesion: 0.33
Nodes (8): Citation, _clause_in(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations…, _scan(), _sentences()

### Community 124 - "test_context_recall.py"
Cohesion: 0.39
Nodes (8): _chunk(), The gate must measure the context window, not just the fusion list.…, An abstention still had a context window; measuring retrieval delivery must not…, _reranked(), test_answer_records_the_context_ids_it_used(), test_context_ids_populated_even_when_abstaining(), test_context_ids_respect_top_k(), test_vectors_exposes_context_recall()

### Community 125 - "Overall Evaluation Summary"
Cohesion: 0.67
Nodes (4): Failure: asof-p2, Overall Evaluation Summary, Pipeline Evaluation Results, Selector Evaluation Results

### Community 127 - "test_ingest_refs.py"
Cohesion: 0.20
Nodes (8): _primary_number(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_dedup_uses_normalized_numbers(), test_fulltext_fallback_returns_earliest_body_reference(), test_parse_meta_dept_order_document_end_to_end(), test_parse_meta_excludes_prefix_variant_self_reference(), test_primary_number_format_matrix()

### Community 128 - "Golden v7 Human Packet"
Cohesion: 0.67
Nodes (3): Golden v7 Human Packet, SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026, SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122

### Community 132 - "relabel_repooled.py"
Cohesion: 0.39
Nodes (6): HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable…, _chunk(), test_expand_sparse_off_routes_raw_query_to_sparse_leg(), test_retrieve_dense_leg_keeps_raw_query(), test_retrieve_routes_expanded_query_to_sparse_leg()

### Community 136 - "test_benchmark.py"
Cohesion: 0.36
Nodes (6): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields(), test_trec_run_and_research_judges_are_sidecar_only()

### Community 141 - "remap_doc_ids.py"
Cohesion: 0.29
Nodes (4): Run all (or specified) metrics sequentially., run_all_metrics(), Empty metrics list is falsy → defaults to ALL_METRICS., TestRegistry

### Community 144 - "test_integration_e2e.py"
Cohesion: 0.20
Nodes (6): OllamaGenerator, Grounded generation via local Ollama (D6 canonical runtime option).…, _ollama_up(), pipeline(), fixture, Step 12 — end-to-end RAG integration test with the REAL stack. bge-m3 (MPS) +…

### Community 145 - "_alias_keys"
Cohesion: 0.29
Nodes (8): _alias_keys(), Candidate alias lookup keys, most literal first. Both the raw normalised form…, PMS/NCS/ILDS end in a literal S. Unconditional plural-stripping mapped them to…, reg_id resolved purely through the alias table, ignoring the corpus., A table key that no _alias_keys() output can produce is dead config., _resolved(), test_acronyms_ending_in_s_reach_their_own_entry(), test_every_alias_entry_is_reachable_from_some_spelling()

### Community 150 - "supersession_tier_cohort.py"
Cohesion: 0.43
Nodes (6): aggregate(), eligible(), main(), measure(), Preregistered cohort measurement for supersession confidence tiering.  Spec: doc, Answerable, non-as_of, with gold citations: the rows citation metrics exist for.

### Community 156 - "bench_rerankers.py"
Cohesion: 0.38
Nodes (6): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,…

### Community 157 - "rescore_runs.py"
Cohesion: 0.53
Nodes (5): _fmt(), main(), Path, Re-score archived benchmark runs with bootstrap CIs and paired significance.…, score_run()

### Community 158 - "measure_context_precision"
Cohesion: 0.50
Nodes (3): measure_context_precision(), Fraction of top-k chunks from relevant circulars. Unlike recall@k (which is…, TestContextPrecision

### Community 159 - "load_regulations"
Cohesion: 0.40
Nodes (5): load_regulations(), Path, Load data/corpus/regulations.jsonl into a list of regulation records. Thin…, test_load_regulations_round_trips(), test_load_regulations_skips_blank_lines()

### Community 161 - "_rejoin_split"
Cohesion: 0.50
Nodes (4): Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge()

### Community 162 - "reg_display_name"
Cohesion: 0.50
Nodes (4): Human-readable regulation name. Year disambiguates same-short_name repeal pairs…, reg_display_name(), test_reg_display_name_composes_year(), test_reg_display_name_falls_back_without_year()

## Knowledge Gaps
- **51 isolated node(s):** `HF_HUB_DISABLE_XET`, `OMP_NUM_THREADS`, `PYTHONPATH`, `PYTORCH_ENABLE_MPS_FALLBACK`, `SEBI_RAG_EVAL_GENERATOR` (+46 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `generate.py`, `relabel_repooled.py`, `SpladeIndex`, `test_benchmark.py`, `.grounded`, `test_attribution.py`, `test_spaces.py`, `load_circulars`, `test_integration_e2e.py`, `test_selective_citations.py`, `validate`, `answer_with_abstention`, `test_paraphrase_rescue.py`, `.build_incremental`, `benchmark.py`, `test_golden_v7_pool.py`, `HybridRetriever`, `test_golden_v7_resolver.py`, `SubjectSimJudge`, `validate_golden_v7`, `test_hyde.py`, `Qwen3MLXReranker`, `test_certainty.py`, `paraphrase_rescue.py`, `test_injection.py`, `_HallucinatingGenerator`, `build_spaces_pipeline`, `main`, `hierarchical_chunk`, `sweep_rrf_k.py`, `test_context_recall.py`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `HybridRetriever` to `generate.py`, `RAGPipeline`, `remap_doc_ids.py`, `test_integration_e2e.py`, `sebi_rag/eval_asof.py`, `test_paraphrase_rescue.py`, `measure_context_precision`, `per_query_recall`, `api.py`, `benchmark.py`, `test_eval_harness_v7.py`, `measure_parsing_latency`, `measure.py`, `measure_supersession_precision`, `faithfulness`, `_doc`, `hierarchical_chunk`, `measure_mrr`, `measure_retrieval_recall`, `measure_temporal_accuracy`, `.query`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `sebi_rag/__init__.py` connect `generate.py` to `_HallucinatingGenerator`, `bench_rerankers.py`, `test_ui.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 57 inferred relationships involving `Chunk` (e.g. with `dataset_quality()` and `NLIAttributionScorer`) actually correct?**
  _`Chunk` has 57 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `run()`) actually correct?**
  _`RAGPipeline` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `HybridRetriever` (e.g. with `main()` and `main()`) actually correct?**
  _`HybridRetriever` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `Settings` (e.g. with `main()` and `main()`) actually correct?**
  _`Settings` has 31 INFERRED edges - model-reasoned connections that need verification._