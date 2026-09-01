# Graph Report - SEBI circular RAG  (2026-09-01)

## Corpus Check
- 249 files · ~233,719 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3251 nodes · 6763 edges · 200 communities (164 shown, 36 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 650 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f3a7312f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_context_headers.py
- export_datasets.py
- test_finetune_synthesize_queries.py
- _unique
- telemetry_engine.py
- test_golden_v7_packet.py
- Frame
- test_paraphrase_rescue.py
- generate.py
- Qwen3MLXReranker
- test_golden_v7_gate.py
- adjudicate
- extract_misses.py
- .grounded
- test_finetune_train_lora.py
- test_regulations.py
- test_attribution.py
- sebi_rag/verify_master.py
- test_reg_lineage.py
- test_conformal.py
- extract_citations
- measure_retrieval_recall
- ingest_pdf.py
- test_golden_v7_gemini.py
- backfill_escalations.py
- test_dataset_cards.py
- test_ui.py
- derive_validity
- sebi_rag/eval_asof.py
- test_rerank_set_encoder.py
- api.py
- .build
- _is_non_sebi_domain
- test_export_datasets.py
- validate
- _row
- gemini_adjudicate.py
- Path
- benchmark.py
- test_label_tier.py
- app.py
- agreement.py
- HybridRetriever
- test_spaces_app.py
- scrape_regulations.py
- test_golden_v7_local.py
- Hugging Face Publishing
- trace_failure.py
- corpus_integrity.py
- test_corpus.py
- ui.py
- test_scrape_sebi.py
- audit_label_provenance.py
- test_finetune_eval_phase0.py
- build_default_pipeline
- sha256_dir
- _provision_agree
- ValueError
- mine_strata.py
- hybrid_gate_sweep.py
- test_rerank_jina_v3.py
- scrape_sebi.py
- paired_delta
- Regulation Scraper Tests
- test_spaces.py
- test_trecio.py
- consolidation_edges
- context_headers.py
- ZeroGPU Workaround Tests
- adjudicate_draft.py
- acquire_missing_pdfs.py
- synthesize_queries.py
- MeasureResult
- test_finetune_roundtrip_filter.py
- test_push_datasets.py
- mine_structural_pairs.py
- Settings
- test_selective_citations.py
- test_ingest_refs.py
- test_acquire_missing.py
- test_segment.py
- measure_supersession_precision
- Handler
- test_golden_v7_agreement.py
- reranker_interaction_check.py
- ExtractiveStubGenerator
- test_finetune_holdout.py
- test_bench_retrieval_artifacts.py
- JinaMLXReranker
- SpladeIndex
- build_lineage
- phase_judge
- segment.py
- read_trec_run
- RAGPipeline
- test_build_reg_edges.py
- test_canary_generator.py
- parse_meta
- test_hyde.py
- test_measure.py
- test_injection.py
- mine_hard_negatives
- test_finetune_mine_structural.py
- run_all_metrics
- test_export_integration.py
- write_run_doc
- test_golden_v7_pool.py
- test_eval_harness_v7.py
- canary.sh
- clopper_pearson_ci
- run.sh
- validate_corpus.py
- main
- bootstrap_ci
- main
- refresh.sh
- validate_golden
- _bootstrap_ci
- test_audit_reg_edges.py
- paraphrase_rescue.py
- .query
- write_trec_qrels
- regression_detector.py
- test_app_asof.py
- validate_golden_v7
- test_build_index_out_dir.py
- filter_targeted_rows
- resolve_chunk_spans
- eval_generator_for
- autoresearch.sh
- Master Circular for Mutual Funds (2026)
- WarrantJudge
- detect_relations_ex
- measure_mrr
- SEBI Master Circular for Mutual Funds (2020)
- test_integration_e2e.py
- ce_query_reform_probe.py
- audit_reg_edges.py
- lineage_anomaly.py
- SEBI Master Circular for LODR Compliance
- Master Circular for Alternative Investment Funds (AIFs) (2026)
- SEBI Circular on IRRA Platform
- label_provenance.py
- deploy_space.py
- discover.sh
- upload_spaces_index.py
- checks.sh
- measure.sh
- Master Circular on Matters relating to Exchange Traded Derivatives (2012)
- SEBI Master Circular for Alternative Investment Funds (2026)
- run_ops.sh
- scripts/autoresearch/__init__.py
- Development Environment Script
- Notification Script
- Phoenix Observability Startup
- SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026
- SEBI Master Circular for Stock Brokers (2018)
- sebi_rag/autoresearch/__init__.py
- measure_parsing_latency
- measure_temporal_accuracy
- conftest.py
- remap_doc_ids.py
- corpus_spaces.py
- Optimize Slash Command
- Seen Circular IDs
- SEBI Master Circular on Exchange Traded Derivatives (2012)
- SEBI Master Circular for REITs (2025)
- SEBI Master Circular for Mutual Funds (2024)
- seed_v7.py
- Hugging Face Spaces Requirements
- Chunk
- SEBI Master Circular for Credit Rating Agencies
- SEBI Master Circular for ESG Rating Providers
- SEBI Master Circular for REITs
- SEBI Master Circular for RTAs
- SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122
- build_regulatory_index
- _resolve_governing_spans
- stats.py
- test_certainty.py
- validate_golden.py
- reg_lineage.py
- main
- _FakeDenseIndex
- run_judge
- test_context_recall.py
- apply
- relabel_repooled.py
- test_benchmark.py
- main
- TestRetrievalBenchmarkNdcg
- main
- measure_context_precision
- discover_new.py
- Embedder
- _FakeResponse
- doc_ids_deduped
- _HallucinatingGenerator
- normalize_circular_number
- sebi-rag

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 118 edges
2. `RAGPipeline` - 63 edges
3. `Settings` - 54 edges
4. `HybridRetriever` - 52 edges
5. `hierarchical_chunk()` - 51 edges
6. `ExtractiveStubGenerator` - 47 edges
7. `HashEmbedder` - 43 edges
8. `load_golden()` - 41 edges
9. `build_lineage()` - 39 edges
10. `BGEM3Embedder` - 35 edges

## Surprising Connections (you probably didn't know these)
- `test_sup04_override_generated_via_injected_callable()` --uses--> `HeaderGenerator`  [INFERRED]
  tests/test_select_targeted_headers.py → src/sebi_rag/context_headers.py
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py
- `_chunk()` --uses--> `Chunk`  [INFERRED]
  tests/test_hyde.py → src/sebi_rag/segment.py
- `test_get_chunk_text_builds_once_and_caches()` --uses--> `Chunk`  [INFERRED]
  tests/test_spaces_app.py → src/sebi_rag/segment.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **SEBI Regulatory Consolidation Pattern** — sebi_ho_imd_df2_cir_p_2020_156, eval_golden_v7_annotations_packet_human_packet_ho_19_34_11_6_2025_afd_pod1_i_12928_2026, eval_golden_v7_annotations_packet_human_packet_sebi_ho_ddhs_pod_2_p_cir_2025_99 [EXTRACTED 0.90]
- **Mutual Fund Offsite Inspection Reporting** — sebi_ho_imd_imd_pod_1_p_cir_2025_38, ho_24_13_11_1_2026_imd_pod_1_i_7602_2026, sebi_mutual_funds_regulations_2026 [EXTRACTED 0.95]
- **Angel Fund Regulatory Framework** — sebi_ho_afd_afd_pod_1_p_cir_2025_128, sebi_ho_afd_afd_pod_1_p_cir_2025_136, ho_19_34_11_6_2025_afd_pod1_i_12928_2026 [EXTRACTED 1.00]
- **SEBI Master Circulars Collection** — sebi_ho_ddhs_pod2_p_cir_2025_101, sebi_ho_ddhs_pod_2_p_cir_2025_99, sebi_ho_mirsd_mirsd_pod_p_cir_2025_91, sebi_ho_mirsd_mirsd_pod_1_p_cir_2024_110, sebi_ho_imd_pod_1_i_7602_2026 [EXTRACTED 1.00]

## Communities (200 total, 36 thin omitted)

### Community 0 - "test_context_headers.py"
Cohesion: 0.21
Nodes (11): apply_context_headers(), HeaderGenerator, Insert each chunk's header as a line below its breadcrumb line. Pure and id-…, _chunk(), Contextual chunk headers (iv9): one lay+statutory sentence per deep chunk.…, test_describe_cleans_markdown_and_newlines(), test_describe_error_or_empty_returns_empty(), test_describe_prompt_contains_inputs_and_constraints() (+3 more)

### Community 1 - "export_datasets.py"
Cohesion: 0.11
Nodes (24): build_aikosh_pack(), build_chunk_rows(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows(), build_zenodo_pack() (+16 more)

### Community 2 - "test_finetune_synthesize_queries.py"
Cohesion: 0.04
Nodes (10): _FakeResponse, Offline tests for scripts/finetune/synthesize_queries.py. The candidate…, Security-relevant: base_url is CLI-configurable here (unlike…, The plan's own finding: self-assigned stratum labels are unreliable. Even if…, A chunk that trails into a signature block or closing 'available on the…, Unlike _is_signoff_boilerplate (which only checks the OPENING, so it doesn't…, test_call_omlx_never_reads_anthropic_auth_token(), test_has_boilerplate_detects_signature_anywhere_not_just_at_start() (+2 more)

### Community 3 - "_unique"
Cohesion: 0.14
Nodes (20): aggregate(), eligible(), main(), measure(), Preregistered cohort measurement for supersession confidence tiering. Spec:…, Answerable, non-as_of, with gold citations: the rows citation metrics exist for., cited_docs(), metrics() (+12 more)

### Community 4 - "telemetry_engine.py"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 5 - "test_golden_v7_packet.py"
Cohesion: 0.11
Nodes (35): _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full…, Reads a human-filled labels_template.csv back into vote records (`annotator:… (+27 more)

### Community 6 - "Frame"
Cohesion: 0.07
Nodes (42): load_runs(), main(), Path, Assign epochs to the archived runs and write the epoch registry. Every run's…, _fmt(), guard_pair(), main(), Path (+34 more)

### Community 7 - "test_paraphrase_rescue.py"
Cohesion: 0.12
Nodes (34): is_degenerate(), Re-score `pool` with a rewritten query when `reranked` is below `floor`.…, Fixed rewrite, for tests and for replaying a preregistered rewrite., True when `rewritten` is unusable and the rescue should be abandoned.…, rescue_pool(), StaticQueryRewriter, _chunk(), _EchoGenerator (+26 more)

### Community 8 - "generate.py"
Cohesion: 0.07
Nodes (38): Ground truth: what do the 4 CE_MISMATCH rows actually DO in production? The…, Preregistered cohort measurement for the CE paraphrase rescue. Spec:…, What does the 0.05 cross-encoder score floor actually catch?…, Capture-once margin sweep for B' selective citations. One pipeline pass over…, Margin sweep for B' selective citations on the golden_v7 adjudicated set. One…, Benchmark MLX generators on the golden set: faithfulness, groundedness,…, F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, Retrieval-only benchmark with TREC runfile and reproducibility metadata. Use… (+30 more)

### Community 9 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 10 - "test_golden_v7_gate.py"
Cohesion: 0.06
Nodes (52): log(), run(), derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the… (+44 more)

### Community 11 - "adjudicate"
Cohesion: 0.18
Nodes (16): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt) -> str`…, Scans the per-row cache for `ids` and returns the ones flagged parse_error:…, _current_model(), main(), pilot() (+8 more)

### Community 12 - "extract_misses.py"
Cohesion: 0.14
Nodes (22): classify_answer(), classify_query(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any…, Chunk IDs embed section headings containing spaces, so parse TREC fields… (+14 more)

### Community 13 - ".grounded"
Cohesion: 0.15
Nodes (11): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), v2 protocol: closed-set identification instead of yes/no judgment. Naming which…, True iff the reply names a valid excerpt number. 'none' or anything unparseable…, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the gate… (+3 more)

### Community 14 - "test_finetune_train_lora.py"
Cohesion: 0.10
Nodes (35): apply_lora(), build_dataset(), check_trainable_ratio(), find_latest_checkpoint(), load_pairs(), main(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-… (+27 more)

### Community 15 - "test_regulations.py"
Cohesion: 0.07
Nodes (39): _alias_keys(), _jaccard(), load_regulations(), name_tokens(), Path, Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6). Regulations…, Candidate alias lookup keys, most literal first. Both the raw normalised form…, Resolve a cited regulation name+year to a canonical reg_id. Returns (reg_id,… (+31 more)

### Community 16 - "test_attribution.py"
Cohesion: 0.07
Nodes (33): entailment_index(), NLIAttributionScorer, NLI attribution scoring for B' citation selection. B' asks "does this context…, Index of the entailment class in a model's label map. Read from the checkpoint…, Scores each context by P(entailment) of the answer given that context.…, Wrap an already-constructed cross-encoder (also the test seam)., _softmax(), pick_device() (+25 more)

### Community 17 - "sebi_rag/verify_master.py"
Cohesion: 0.19
Nodes (20): diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13). Pure functions only:…, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows., render_markdown() (+12 more)

### Community 18 - "test_reg_lineage.py"
Cohesion: 0.12
Nodes (33): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+25 more)

### Community 19 - "test_conformal.py"
Cohesion: 0.10
Nodes (31): _control_summary(), main(), phase_calibrate(), phase_report(), R7 conformal abstention calibration: generate -> calibrate -> report phases.…, Current production behaviour, exactly as shipped -- no LOO recalibration, the…, Re-simulates each row's abstention decision under the CALIBRATED thresholds,…, _simulated_summary() (+23 more)

### Community 20 - "extract_citations"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 21 - "measure_retrieval_recall"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 22 - "ingest_pdf.py"
Cohesion: 0.15
Nodes (19): Re-derive circular number + dates from each record's stored text and rewrite…, _existing_numbers(), extract_text(), ingest(), main(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars. Drop a circular PDF into data/raw/ and… (+11 more)

### Community 23 - "test_golden_v7_gemini.py"
Cohesion: 0.11
Nodes (28): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply… (+20 more)

### Community 24 - "backfill_escalations.py"
Cohesion: 0.16
Nodes (22): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+14 more)

### Community 25 - "test_dataset_cards.py"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 26 - "test_ui.py"
Cohesion: 0.06
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 27 - "derive_validity"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation. Locked…, Validity of one circular from the tiered edge list (any scope: the function…, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 28 - "sebi_rag/eval_asof.py"
Cohesion: 0.13
Nodes (26): AsofCaseResult, build_report(), load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Aggregate case results with an exact confidence interval. Pure function of the…, run_pipeline_cases() (+18 more)

### Community 29 - "test_rerank_set_encoder.py"
Cohesion: 0.14
Nodes (13): _chunk(), _FakeOutput, _FakeScores, _FakeSetEncoderModule, Offline tests for the webis/set-encoder-base wrapper (2026-08-26 Set-Encoder…, Stands in for the torch.Tensor `CrossEncoderModule.score(...).scores` return…, Stands in for lightning_ir.CrossEncoderModule — records the query/docs it was…, Bypass __init__ (no lightning-ir import / model download / network). (+5 more)

### Community 30 - "api.py"
Cohesion: 0.06
Nodes (28): BaseModel, FastAPI, integration, _citation_meta(), CitationMeta, create_app(), QueryRequest, QueryResponse (+20 more)

### Community 31 - ".build"
Cohesion: 0.11
Nodes (22): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and…, BM25 lexical index (bm25s)., Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), SparseIndex, _chunk() (+14 more)

### Community 32 - "_is_non_sebi_domain"
Cohesion: 0.10
Nodes (29): _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain. Case-…, The non-SEBI domain filter must match words, not substrings. Shipped 2026-07-30…, Any single-token keyword <= 5 chars is a substring hazard. Embedding it inside…, Query mentioning both SEBI and RBI should NOT abstain — SEBI intent wins., Empty query should not trigger the non-SEBI filter., FEMA keyword in a SEBI context should NOT abstain — SEBI intent wins., The exact query that exposed the bug. (+21 more)

### Community 33 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 34 - "validate"
Cohesion: 0.33
Nodes (14): validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the document's own…, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations(), test_duplicate_text_across_records_flagged(), test_empty_text_is_not_a_duplicate_cluster(), test_flags_bad_issue_date() (+6 more)

### Community 35 - "_row"
Cohesion: 0.12
Nodes (27): decide(), Spec sec7 promotion rules for one row. `votes_by_annotator` is this row's votes…, Abstain rows have no explicit claude vote at all (Task 8 never judged them) -…, Both externals independently think something DOES govern (disputing the…, The LLM leg is whichever single non-claude/non-human annotator voted - "qwen"…, Amendment 2026-07-26 (user-approved): the promotion unit is the PROVISION, not…, External marked claude's chunk governing plus extras: claude's label is…, The abstain protocol can never emit non-empty governing (no letters are… (+19 more)

### Community 36 - "gemini_adjudicate.py"
Cohesion: 0.10
Nodes (26): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec… (+18 more)

### Community 37 - "Path"
Cohesion: 0.22
Nodes (21): _config_entry(), _emit(), export_all(), export_chunks(), export_citation_normalization(), export_corpus(), export_eval(), export_lineage() (+13 more)

### Community 38 - "benchmark.py"
Cohesion: 0.18
Nodes (23): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, beir_corpus_rows(), beir_query_rows(), build_golden_v6(), dir_fingerprint(), enrich_golden_item(), export_beir() (+15 more)

### Community 39 - "test_label_tier.py"
Cohesion: 0.12
Nodes (20): classify_tier(), human_reviewed_ids(), main(), Path, Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.…, Map provenance to the controlled vocabulary. `human_reviewed` (row appears in…, Row ids present in the human labelling packet., Controlled-vocabulary label_tier over golden_v7 (spec A §8.3). (+12 more)

### Community 40 - "app.py"
Cohesion: 0.08
Nodes (39): _append_message(), _blank_previews(), _build_citations_markdown(), build_ui(), _certainty_badge(), _cycle_messages_until_done(), _empty_citations_md(), _faithfulness_badge() (+31 more)

### Community 41 - "agreement.py"
Cohesion: 0.15
Nodes (21): _claude_accuracy_ci(), gwet_ac1(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation…, Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a prevalence-… (+13 more)

### Community 42 - "HybridRetriever"
Cohesion: 0.13
Nodes (33): eligible(), main(), SPIKE — throwaway, not preregistered. Answers one question before any R6 design…, main(), main(), main(), ADR-004 adoption: calibrate abstain_threshold for jina-reranker-v3-mlx's score…, main() (+25 more)

### Community 43 - "test_spaces_app.py"
Cohesion: 0.07
Nodes (6): app_module(), fixture, HF Spaces demo (root app.py): citations table + preview accordion logic. Fully…, app.py does `import spaces` (ZeroGPU) at module scope; stub it., _stub_spaces_package(), test_get_chunk_text_builds_once_and_caches()

### Community 44 - "scrape_regulations.py"
Cohesion: 0.19
Nodes (13): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY).…, (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'. Takes the LAST bracket group…, _record() (+5 more)

### Community 45 - "test_golden_v7_local.py"
Cohesion: 0.10
Nodes (27): _extract_text(), _post_local(), OpenAI chat-completions response -> reply text: the first choice's message…, One blind-protocol call to the oMLX server's OpenAI-compatible endpoint. Auth…, Qwen-family models may emit <think>...</think> reasoning as inline text,…, _strip_thinking(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external… (+19 more)

### Community 46 - "Hugging Face Publishing"
Cohesion: 0.19
Nodes (18): export_golden_v7_arrow(), log(), main(), Path, Run export_datasets.py then add golden_v7 Arrow config., Upload dist/datasets/ to HF dataset repo., Run make index to rebuild FAISS+BM25 before upload., Upload data/index/ to HF index repo. (+10 more)

### Community 47 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 48 - "corpus_integrity.py"
Cohesion: 0.36
Nodes (7): check_meta_fields(), load_chunks(), load_corpus(), main(), Load corpus into a dict keyed by circular_number., Load chunks and return (records, doc_ids)., Check that chunk meta has expected CircularMeta fields.

### Community 49 - "test_corpus.py"
Cohesion: 0.13
Nodes (28): Path, corpus.load_circulars edge-case coverage. load_circulars reads a JSONL corpus…, Provided optional fields are passed through to CircularMeta., Multiple records produce multiple chunks., Blank lines between records are silently skipped., Malformed JSON raises ValueError (json.loads default)., load_circulars accepts both str and Path., load_circulars accepts a pathlib.Path. (+20 more)

### Community 50 - "ui.py"
Cohesion: 0.16
Nodes (17): Human-readable regulation name. Year disambiguates same-short_name repeal pairs…, reg_display_name(), _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_outputs_md(), _parse_as_of(), Return empty markdown placeholder for streaming. (+9 more)

### Community 51 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 52 - "audit_label_provenance.py"
Cohesion: 0.21
Nodes (15): audit(), collect_artifacts(), _ids_from_csv(), _ids_from_dir(), _ids_from_jsonl(), main(), Path, Report what the annotation artifacts can account for, before classifying.… (+7 more)

### Community 53 - "test_finetune_eval_phase0.py"
Cohesion: 0.08
Nodes (39): compare(), gate_verdict(), main(), parse_run_doc(), Path, Phase A eval (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-…, Preregistered asymmetric directional screen (n=20-40/stratum is a directional…, run.doc.trec is a VALID 6-field TREC file at circular level… (+31 more)

### Community 54 - "build_default_pipeline"
Cohesion: 0.13
Nodes (16): main(), SPIKE/GATE (throwaway, not preregistered) — R5's own precondition from the…, main(), What actually makes a context window large: chunk size, or chunk count? Read-…, main(), P0 prep: price a larger MLX generator before committing to the R0 upgrade.…, rss_gb(), Build the full pipeline with real models. (+8 more)

### Community 55 - "sha256_dir"
Cohesion: 0.24
Nodes (11): main(), merge(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-…, Per-file sha256 of every file in the merged model dir - the plan's "sha256 into…, CPU by design, not MPS: this is a one-shot weight merge, not a training or…, sha256_dir(), Offline tests for scripts/finetune/merge_adapter.py's pure pieces. The actual… (+3 more)

### Community 56 - "_provision_agree"
Cohesion: 0.18
Nodes (11): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using the…, Does this external vote confirm claude's label, at PROVISION level? Amendment…, _norm_ws(), Different chunk copies of the same quoted provision agree at provision level…, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction() (+3 more)

### Community 57 - "ValueError"
Cohesion: 0.17
Nodes (20): _assert_fixed_tail(), convert_run_dir(), main(), Path, Back-convert archived runfiles into standards-compliant TREC artifacts. The…, Trailing field of the first line; also the whitespace precondition check., read_trec_run assumes qid and tag carry no whitespace. Verify per line., Write run.chunk.trec, run.doc.trec and docids.tsv for one archived run. (+12 more)

### Community 58 - "mine_strata.py"
Cohesion: 0.22
Nodes (16): _body(), main(), _mid(), mine_lineage_pairs(), mine_multi_hop(), mine_numeric(), mine_repealed_basis(), Deterministic candidate mining for golden_v7 drafting (spec Sec 4, Sec 5). Pure… (+8 more)

### Community 59 - "hybrid_gate_sweep.py"
Cohesion: 0.26
Nodes (11): current_gate_passes(), hybrid_gate_passes(), main(), parse_args(), Namespace, Hybrid abstention gate sweep — preregistered analysis. Preregistration:…, Reproduces the current production subject-gate OR (no hybrid override)., True if this row never reaches the subject-gate check at all (vetoed earlier by… (+3 more)

### Community 60 - "test_rerank_jina_v3.py"
Cohesion: 0.14
Nodes (17): ADR-004: the single decision for which model orders the RETRIEVAL pool…, retrieval_reranker_for(), _chunk(), _FakeJinaBackend, Offline tests for the jina-reranker-v3-mlx wrapper (ADR-004) — translation…, Same bug, same fix, second script: eval_asof.py also builds its own RAGPipeline…, Stands in for the vendor's MLXReranker.rerank() — same return shape (list of…, Bypass __init__ (no snapshot_download / mlx / network). (+9 more)

### Community 61 - "scrape_sebi.py"
Cohesion: 0.26
Nodes (13): discover(), _listing_url(), main(), _page(), _parse_date(), parse_rows(), pdf_url_for(), date (+5 more)

### Community 62 - "paired_delta"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries. Returns mean_b -…, Randomization p-values use the (count+1)/(n+1) estimator, so a p-value of…, One query flipping out of 56 is exactly the iv9-style verdict: the…, TestPairedDelta

### Community 64 - "test_spaces.py"
Cohesion: 0.08
Nodes (26): _grounded_prompt(), F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and the…, ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo. All classes implement…, External Space first; on ANY failure fall back to the local CPU model.…, Primary generator: calls a public LLM Space via gradio_client. Wired to… (+18 more)

### Community 65 - "test_trecio.py"
Cohesion: 0.20
Nodes (16): chunk_docid(), circular_docid(), MalformedChunkId, Standards-compliant TREC run and qrels emission. The archived runfiles are not…, Raised when an id cannot yield a whitespace-free TREC doc id., Percent-encode whitespace so a circular id is a single TREC field. Reversible…, Map a chunk id to a whitespace-free TREC doc id. `<circular>#<heading with…, Standards-compliant TREC artifact emission (spec A §3-4). (+8 more)

### Community 66 - "consolidation_edges"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans…, _master(), test_annotate_idempotent() (+7 more)

### Community 67 - "context_headers.py"
Cohesion: 0.22
Nodes (9): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, in_scope(), load_headers(), Path, Contextual chunk headers (iv9): one lay+statutory sentence per chunk. Index-…, Spec scope: depth>=3 numbered sub-clauses plus annex-family headings., test_load_headers_missing_file_returns_empty() (+1 more)

### Community 68 - "ZeroGPU Workaround Tests"
Cohesion: 0.14
Nodes (13): app_module(), fixture, Regression coverage for the ZeroGPU-hardware workaround in app.py. Background:…, Inject a fake `spaces` module so app.py's `import spaces` succeeds offline, and…, Static guard: if `import spaces` or the `@spaces.GPU` decorator is ever…, It must stay dead code: calling it would request a real ZeroGPU allocation (and…, The functions actually on the request path (get_pipeline, run_query_stream)…, `hardware:` in README-spaces.md is not a documented Spaces config key (only… (+5 more)

### Community 69 - "adjudicate_draft.py"
Cohesion: 0.24
Nodes (12): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+4 more)

### Community 70 - "acquire_missing_pdfs.py"
Cohesion: 0.22
Nodes (14): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+6 more)

### Community 71 - "synthesize_queries.py"
Cohesion: 0.11
Nodes (30): build_citation_pairs(), build_supersession_pairs(), _format_family(), Pure transform: corpus + lineage -> labeled circular pairs. label is…, Pure transform: corpus text -> citation-normalization rows. Mines in-body…, Every chunk's text is `"{doc_id} | {subject[:120]} | {section}\\n{body}"` -…, _strip_context_header(), cache_path() (+22 more)

### Community 72 - "MeasureResult"
Cohesion: 0.39
Nodes (3): MeasureReport, MeasureResult, TestDataClasses

### Community 73 - "test_finetune_roundtrip_filter.py"
Cohesion: 0.12
Nodes (29): build_text_to_doc_map(), filter_boilerplate(), load_rows(), Path, Phase 1 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-…, Prefer the row's own positive_doc field (future runs); fall back to the reverse…, Retrieves with each row's query against `retriever` (the frozen base index) and…, Returns (kept, n_dropped). (+21 more)

### Community 74 - "test_push_datasets.py"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default:…, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 75 - "mine_structural_pairs.py"
Cohesion: 0.22
Nodes (13): Random, load_chunks_by_doc(), load_corpus_records(), load_minable_docs(), main(), mine_lineage_pairs(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-… (+5 more)

### Community 76 - "Settings"
Cohesion: 0.16
Nodes (26): is_master(), main(), Is the eval set measuring retrieval, or measuring its own construction? Read-…, _as_bool(), _get(), Path, Settings.load() plus the [spaces] table as settings.spaces.* Load order per…, Resolve a setting: env var > config dict > default. (+18 more)

### Community 77 - "test_selective_citations.py"
Cohesion: 0.08
Nodes (54): citation_scorer_for(), The single enable/disable AND backend decision for B'. Returns None when…, Callable compatible with select_citations' scorer.rerank() signature. Wraps…, Context ids the answer rests on. Scores each context via `scorer`, keeps those…, select_citations(), warrant_scorer(), _chunk(), _FakeReranker (+46 more)

### Community 78 - "test_ingest_refs.py"
Cohesion: 0.15
Nodes (11): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_fulltext_fallback_returns_earliest_body_reference() (+3 more)

### Community 80 - "test_segment.py"
Cohesion: 0.15
Nodes (16): _body(), Chunker (segment.hierarchical_chunk) behaviour. Regression guard for the "5.…, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_absorption_respects_300_char_cap(), test_bare_parent_heading_folds_into_first_subsection(), test_bare_parent_heading_not_emitted_as_standalone_chunk(), test_flattened_table_row_not_emitted_as_lone_chunk(), test_flattened_table_rows_merge_into_one_chunk() (+8 more)

### Community 81 - "measure_supersession_precision"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 82 - "Handler"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 83 - "test_golden_v7_agreement.py"
Cohesion: 0.19
Nodes (15): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw element is…, _min_agreement_fixture(), Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):…, The kappa base-rate paradox: one label dominates, raw agreement is high, yet…, _same_provision_fixture(), test_claude_accuracy_ci_returns_exact_and_provision(), test_cohen_kappa_both_constant_and_identical_is_one() (+7 more)

### Community 84 - "reranker_interaction_check.py"
Cohesion: 0.17
Nodes (21): main(), parse_args(), Namespace, Compare query-expansion arms (current prod / no-expand / HyDE) on a golden set.…, run_arm(), fmt(), mean_or_none(), ndcg_at_k() (+13 more)

### Community 85 - "ExtractiveStubGenerator"
Cohesion: 0.16
Nodes (25): answer_with_abstention(), ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., rerank_top exactly at 0.85 overrides judge abstention (HYBRID_THRESHOLD=0.85)., rerank_top just below 0.85 does NOT override judge abstention., When no judge is present, hybrid gate logic must be inert (no crash). (+17 more)

### Community 86 - "test_finetune_holdout.py"
Cohesion: 0.14
Nodes (24): build(), classify_rows(), gold_circulars(), main(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-…, Every distinct circular any golden_v7 row cites as relevant, sorted for…, Deterministic seeded sample. round(), not int(), so 159*0.30=47.7 lands on 48… (+16 more)

### Community 87 - "test_bench_retrieval_artifacts.py"
Cohesion: 0.15
Nodes (9): bench_retrieval must emit valid TREC alongside the legacy runfile., run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so every…, iv9/iv10 build a headered index beside data/index. Without an index override…, ADR-004: benchmarking jina-reranker-v3-mlx against the production cross-encoder…, 2026-08-26 Set-Encoder spec: benchmarking webis/set-encoder-base (via…, test_bench_retrieval_can_bench_an_alternate_index(), test_bench_retrieval_can_measure_the_reranked_order(), test_bench_retrieval_exposes_and_records_the_reranker_choice() (+1 more)

### Community 88 - "JinaMLXReranker"
Cohesion: 0.14
Nodes (16): phase_generate(), _doc(), _aggregate(), eligible(), main(), _measure(), phase_generate(), phase_report() (+8 more)

### Community 89 - "SpladeIndex"
Cohesion: 0.07
Nodes (29): RuntimeError, main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.… (+21 more)

### Community 90 - "build_lineage"
Cohesion: 0.08
Nodes (43): contexts_for(), annotate_corpus(), build_lineage(), demote_superseded(), Lineage, mc_topic(), Path, Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None. Used… (+35 more)

### Community 91 - "phase_judge"
Cohesion: 0.36
Nodes (9): _aggregate(), eligible(), main(), _measure(), phase_generate(), phase_judge(), phase_report(), R1 §4/§6 cohort measurement: control (cross-encoder) vs W1 (warrant judge).… (+1 more)

### Community 92 - "segment.py"
Cohesion: 0.13
Nodes (14): _is_table_row_candidate(), _merge_table_rows(), _paragraphs(), Segmentation: hierarchical chunking + metadata + stable citation IDs. Minimal,…, Collapse a run of >=3 consecutive single-line, same-depth table-row candidates…, # NOTE: We intentionally DO NOT set carry here — flush() already, Split into units each <= max_chars. PDF-extracted text often lacks blank-line…, Nesting depth of a numbered line ("2.1.3" -> 2), or None if it isn't one at all. (+6 more)

### Community 93 - "read_trec_run"
Cohesion: 0.36
Nodes (4): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), The archived runfiles embed section headings in the doc id., TestReadTrecRun

### Community 94 - "RAGPipeline"
Cohesion: 0.09
Nodes (57): Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)…, smoke_pipeline(), smoke_pipeline(), load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable… (+49 more)

### Community 95 - "test_build_reg_edges.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 96 - "test_canary_generator.py"
Cohesion: 0.27
Nodes (8): _canary_jscode(), _ops_timeout(), The eval canary must fit its timeout and alert on real regressions. Measured…, n8n gives up first if its budget is smaller, so the ops timeout is never…, A threshold above the healthy value fires every run. citation_precision was…, test_alert_thresholds_sit_below_measured_baselines(), test_n8n_timeout_not_tighter_than_the_ops_budget(), test_ops_timeout_fits_the_measured_runtime()

### Community 97 - "parse_meta"
Cohesion: 0.15
Nodes (17): Pattern, _iso_date(), _labeled_date(), parse_meta(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash… (+9 more)

### Community 98 - "test_hyde.py"
Cohesion: 0.18
Nodes (11): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —…, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_none_and_empty_hyde_are_identical_to_baseline() (+3 more)

### Community 99 - "test_measure.py"
Cohesion: 0.28
Nodes (5): main(), metrics_to_markdown(), Format results as a markdown table., Unit tests for sebi_rag.measure — automated metric collection., TestCLI

### Community 100 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 101 - "mine_hard_negatives"
Cohesion: 0.24
Nodes (16): mine_hard_negatives(), One batched embed + one batched FAISS search for the whole set - not a per-…, _FakeChunk, _FakeEmbedder, _FakeRetriever, mine_hard_negatives only uses embed() to build the FAISS query vectors now (no…, Backward-compat: every mine_structural_pairs.py template has positive ==…, Phase 1's multi_hop rows: source_doc is the CITING document, but the positive… (+8 more)

### Community 102 - "test_finetune_mine_structural.py"
Cohesion: 0.10
Nodes (31): _is_signoff_boilerplate(), _leaks_metadata(), mine_citation_context(), mine_heading_section(), mine_subject_body(), First line matching the numbered-clause pattern -> (heading, rest). None if no…, _split_heading(), Offline tests for scripts/finetune/mine_structural_pairs.py's pure transforms.… (+23 more)

### Community 103 - "run_all_metrics"
Cohesion: 0.29
Nodes (4): Run all (or specified) metrics sequentially., run_all_metrics(), Empty metrics list is falsy → defaults to ALL_METRICS., TestRegistry

### Community 104 - "test_export_integration.py"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 105 - "write_run_doc"
Cohesion: 0.18
Nodes (15): Rankings, Path, Reverse map `docid -> full chunk id`, so nothing is lost., Valid 6-field TREC run at chunk granularity., Valid 6-field TREC run collapsed to circular level. Keeps each circular once,…, write_docids(), _write_lines(), write_run_chunk() (+7 more)

### Community 106 - "test_golden_v7_pool.py"
Cohesion: 0.31
Nodes (9): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, Regression (2026-07-25): a must_contain literal matching many gold-doc chunks…, _retriever(), test_bm25_leg_uses_raw_query_not_expansion(), test_deep_relevant_chunk_is_reachable_despite_a_common_literal(), test_gold_literal_chunks_lead_the_pool() (+1 more)

### Community 107 - "test_eval_harness_v7.py"
Cohesion: 0.30
Nodes (14): _aggregate(), EvalReport, _mean(), report_dict(), run_eval(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-…, _row() (+6 more)

### Community 108 - "canary.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, SEBI_RAG_EVAL_GENERATOR, canary.sh script, TOKENIZERS_PARALLELISM

### Community 109 - "clopper_pearson_ci"
Cohesion: 0.22
Nodes (5): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, test_render_report_includes_ac1_and_provision(), The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 110 - "run.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 111 - "validate_corpus.py"
Cohesion: 0.38
Nodes (6): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair. Checks (per…, Every record's text must match the PDF its provenance names. Slow (re-extracts…, validate_deep()

### Community 112 - "main"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

### Community 113 - "bootstrap_ci"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 114 - "main"
Cohesion: 0.31
Nodes (7): call(), main(), _norm(), Does answering a golden_v7 row require a circular the corpus does not hold?…, Uppercase, strip all whitespace — so 'CIR/MIRSD/5/ 2013' matches…, Returns (answer, reasoning). The judge is a reasoning model: the oMLX API…, windows()

### Community 115 - "refresh.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 116 - "validate_golden"
Cohesion: 0.14
Nodes (14): per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.…, validate_golden(), Ten chunks of one circular must not crowd the cutoff: the k applies to unique…, Answerable-but-unjudged rows are excluded from metrics, never scored 0.…, A real, fully-populated golden row, so the fixture cannot drift out of sync…, v7-ls-038/039/040 are answerable but unjudged; they carry…, _template() (+6 more)

### Community 117 - "_bootstrap_ci"
Cohesion: 0.15
Nodes (10): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Path, Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict. (+2 more)

### Community 118 - "test_audit_reg_edges.py"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 119 - "paraphrase_rescue.py"
Cohesion: 0.16
Nodes (11): _extracts(), MLXQueryRewriter, Protocol, query_rewriter_for(), QueryRewriter, Paraphrase rescue for the cross-encoder score floor. Preregistered in…, Factory mirroring `generate.citation_scorer_for`: None when disabled., Rewrites a lay-vocabulary query into statutory vocabulary. Returns None when it… (+3 more)

### Community 120 - ".query"
Cohesion: 0.33
Nodes (4): Answer, Map any cited circular that is superseded -> the circular(s) superseding it.…, superseded_citations(), As-of exclusion or supersession demotion, applied to a reranked list. Extracted…

### Community 121 - "write_trec_qrels"
Cohesion: 0.14
Nodes (13): main(), Emit TREC qrels for an eval set, keyed by its golden_sha256. .venv/bin/python…, Write TREC qrels (`qid 0 docid rel`) at circular level. Binary relevance:…, write_trec_qrels(), artifacts(), fixture, The encoding must agree across runs and qrels. If a run says…, test_qrels_docids_match_run_doc_docids_exactly() (+5 more)

### Community 122 - "regression_detector.py"
Cohesion: 0.36
Nodes (7): extract_metrics(), load_floors(), load_latest_runs(), main(), Load floors from gate_v7.json., Load most recent eval runs sorted by timestamp., Extract metric values from a run.

### Community 123 - "test_app_asof.py"
Cohesion: 0.20
Nodes (6): app_module(), _expected_output_count(), fixture, As-of date plumbing in the Spaces UI (app.py)., 8 fixed fields + 2 per preview accordion + 4 meta badges. Matches the flat list…, test_run_query_yield_arity_matches_outputs_list_pipeline_free_paths()

### Community 124 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 125 - "test_build_index_out_dir.py"
Cohesion: 0.29
Nodes (5): build_index must be able to target a scratch index directory. The iv9/iv10…, A --out flag that is parsed but ignored is worse than none: it reads as safe…, lineage.json lands next to the index it describes; writing it into data/index…, test_build_index_saves_to_the_resolved_out_dir_not_the_constant(), test_lineage_follows_the_out_dir()

### Community 126 - "filter_targeted_rows"
Cohesion: 0.33
Nodes (6): filter_targeted_rows(), Keep only sidecar rows whose chunk belongs to a target document., Selection of targeted headers (iv10): filter iv9's reused headers down to 3…, test_filter_keeps_only_target_doc_rows(), test_filter_with_no_matches_returns_empty(), test_sup04_override_generated_via_injected_callable()

### Community 127 - "resolve_chunk_spans"
Cohesion: 0.26
Nodes (13): BenchmarkIssue, chunks_by_doc(), Span {doc, quote} -> matching chunk ids (all overlap matches count). Legacy…, resolve_chunk_spans(), _span_resolution_issues(), _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row() (+5 more)

### Community 128 - "eval_generator_for"
Cohesion: 0.16
Nodes (12): eval_generator_for(), The single generator decision for the eval stack. `derive_thresholds.py` sets…, The eval stack's generator choice must be one shared decision.…, Uses an injected loader so the test stays offline., Silently falling back to the stub would derive floors under semantics the…, Must assert the factory is CALLED, not merely imported. Verified 2026-08-12 by…, A factory both call is not enough - they must pass the same setting, or the…, test_both_eval_scripts_read_the_same_setting() (+4 more)

### Community 129 - "autoresearch.sh"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 130 - "Master Circular for Mutual Funds (2026)"
Cohesion: 0.40
Nodes (5): Master Circular for Mutual Funds (2026), Circular on Development of Passive Funds, Extension of timelines for submission of offsite inspection data (Mutual Funds), SEBI (Mutual Funds) Regulations, 1996, SEBI (Mutual Funds) Regulations, 2026

### Community 131 - "WarrantJudge"
Cohesion: 0.20
Nodes (7): parse_warrant_scores(), Prompt for the warrant judge: evaluate each excerpt's warrant for the answer.…, Parse warrant scores from the judge's JSON output. Returns a list of n floats…, Warrant judge: single-call structured output evaluating each excerpt's warrant.…, Score each context's warrant for the answer. Returns a list of floats…, _warrant_prompt(), WarrantJudge

### Community 132 - "detect_relations_ex"
Cohesion: 0.15
Nodes (12): main(), R3 §3.1 — mine cross-reference (A cites B) candidate pairs. Spec:…, detect_relations(), detect_relations_ex(), Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window(), A circular that names another circular BEFORE the supersede trigger word must… (+4 more)

### Community 133 - "measure_mrr"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level. For each query, RR = 1/rank of first…, TestMRR

### Community 134 - "SEBI Master Circular for Mutual Funds (2020)"
Cohesion: 0.50
Nodes (4): SEBI Circular on Options Eligibility (2024), SEBI Master Circular for Mutual Funds (2020), SEBI Circular HO/24/13/12(4)2025-IMD-POD-1/I/2062/2026, SEBI Master Circular for Mutual Funds (2026)

### Community 135 - "test_integration_e2e.py"
Cohesion: 0.33
Nodes (4): _ollama_up(), pipeline(), fixture, Step 12 — end-to-end RAG integration test with the REAL stack. bge-m3 (MPS) +…

### Community 136 - "ce_query_reform_probe.py"
Cohesion: 0.38
Nodes (6): main(), _pool(), Probe: does query-side reformulation lift the CE score on the 4 CE_MISMATCH…, Return (ce_top, best relevant score, chunk_id of argmax)., Top-8 pool plus every relevant chunk, de-duplicated on chunk_id., _score()

### Community 137 - "audit_reg_edges.py"
Cohesion: 0.33
Nodes (9): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+1 more)

### Community 138 - "lineage_anomaly.py"
Cohesion: 0.60
Nodes (4): load_corpus(), load_lineage(), main(), Load corpus keyed by circular_number.

### Community 139 - "SEBI Master Circular for LODR Compliance"
Cohesion: 0.67
Nodes (3): SEBI Master Circular for LODR Compliance, SEBI Operational Circular for Non-convertible Securities (2022), SEBI Master Circular for RTAs (2023)

### Community 140 - "Master Circular for Alternative Investment Funds (AIFs) (2026)"
Cohesion: 1.00
Nodes (3): Master Circular for Alternative Investment Funds (AIFs) (2026), Revised regulatory framework for Angel Funds, Relaxation in timeline for disclosure of allocation methodology by Angel Funds

### Community 141 - "SEBI Circular on IRRA Platform"
Cohesion: 0.67
Nodes (3): Investor Risk Reduction Access (IRRA), SEBI Circular on IRRA Platform, Master Circular for Stock Brokers (2025)

### Community 158 - "measure_parsing_latency"
Cohesion: 0.38
Nodes (4): measure_parsing_latency(), Measure PDF ingestion throughput (chars/sec, ms/PDF). Samples 20 PDFs…, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 159 - "measure_temporal_accuracy"
Cohesion: 0.43
Nodes (3): measure_temporal_accuracy(), Measure fraction of as_of queries returning correct pre-supersession circular…, TestTemporalAccuracy

### Community 161 - "remap_doc_ids.py"
Cohesion: 0.33
Nodes (10): main(), Rewrite golden_v7 doc references after the corpus renumbering (2026-07-25…, remap(), Doc-id remapping after the 2026-07-25 corpus renumbering (Task 4)., _row(), test_input_rows_are_not_mutated(), test_matching_is_normalization_insensitive(), test_remaps_must_not_cite() (+2 more)

### Community 162 - "corpus_spaces.py"
Cohesion: 0.29
Nodes (10): _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path). Loads the…, One HF dataset config as plain dicts (network; cached by `datasets`)., Full-circular records (dicts) for build_lineage() — always the "corpus" config… (+2 more)

### Community 168 - "seed_v7.py"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 170 - "Chunk"
Cohesion: 0.08
Nodes (18): OllamaGenerator, ADOPTED gate (eval_gate round 3): deterministic groundedness signal — max…, Max cosine(query, doc subject line) over contexts — the primary gate signal,…, Max cosine(query, section heading) over contexts — the second tier., Grounded generation via local Ollama (D6 canonical runtime option).…, SubjectSimJudge, _LineageAwareReranker, Reranker wrapper that re-applies lineage handling to its output. The paraphrase… (+10 more)

### Community 176 - "build_regulatory_index"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 177 - "_resolve_governing_spans"
Cohesion: 0.36
Nodes (8): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote} spans, looked…, _resolve_governing_spans(), _pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool(), test_resolve_governing_spans_short_body_uses_whole_body(), test_resolve_governing_spans_uses_first_60_body_chars()

### Community 178 - "stats.py"
Cohesion: 0.22
Nodes (6): BootstrapCI, PairedResult, ProportionCI, Uncertainty quantification for benchmark runs. The golden set is n=56…, True when the randomization test rejects at 1 - confidence AND the paired…, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 179 - "test_certainty.py"
Cohesion: 0.39
Nodes (8): _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons,…, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful(), test_no_context_reason_when_top_k_zero(), test_score_floor_reason(), test_subject_gate_reason_and_subject_sim_recorded()

### Community 180 - "validate_golden.py"
Cohesion: 0.83
Nodes (3): check_gate(), check_golden_set(), main()

### Community 181 - "reg_lineage.py"
Cohesion: 0.29
Nodes (6): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus., derive_regulatory_basis(), Regulatory-basis status of one circular from its resolved regulations.…, test_derive_regulatory_basis_truth_table()

### Community 183 - "_FakeDenseIndex"
Cohesion: 0.29
Nodes (3): _FakeDense, _FakeDenseIndex, Deterministic stand-in for faiss.IndexFlatIP.search: returns a fixed ranking…

### Community 184 - "run_judge"
Cohesion: 0.39
Nodes (7): _is_parseable(), _load_screen(), main(), R1 §3.3 degeneracy probe: does the warrant judge return a parseable reply?…, Mirrors generate.parse_warrant_scores' cleaning exactly, but reports whether…, run_answers(), run_judge()

### Community 185 - "test_context_recall.py"
Cohesion: 0.46
Nodes (7): _chunk(), The gate must measure the context window, not just the fusion list.…, An abstention still had a context window; measuring retrieval delivery must not…, _reranked(), test_answer_records_the_context_ids_it_used(), test_context_ids_populated_even_when_abstaining(), test_context_ids_respect_top_k()

### Community 186 - "apply"
Cohesion: 0.29
Nodes (7): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions` (keyed by…, test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only(), test_apply_queue_decision_leaves_row_untouched(), test_apply_row_without_a_decision_is_never_touched()

### Community 187 - "relabel_repooled.py"
Cohesion: 0.43
Nodes (6): _body(), main(), _norm(), pick(), Label the 7 rows re-pooled after the assemble_pool fix (2026-07-25 remediation…, (candidate, quote) pairs for this row: the answer_contains carrier first, then…

### Community 188 - "test_benchmark.py"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

### Community 189 - "main"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl()

### Community 190 - "TestRetrievalBenchmarkNdcg"
Cohesion: 0.40
Nodes (4): _FixedOrderReranker, ADR-004: a reranker swap changes ORDER within top-10, which recall@10 (set…, Always returns the SAME doc order regardless of query — deterministic, so…, TestRetrievalBenchmarkNdcg

### Community 191 - "main"
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 192 - "measure_context_precision"
Cohesion: 0.50
Nodes (3): measure_context_precision(), Fraction of top-k chunks from relevant circulars. Unlike recall@k (which is…, TestContextPrecision

### Community 194 - "Embedder"
Cohesion: 0.10
Nodes (17): Embedder, ndarray, Protocol, _tokens(), DenseIndex, _doc_checksum(), ndarray, Path (+9 more)

### Community 198 - "normalize_circular_number"
Cohesion: 0.18
Nodes (7): main(), Repair the 6 records whose body text was overwritten with one shared circular's…, normalize_circular_number(), Canonical COMPARISON key for a circular number: strip whitespace and trailing…, test_dedup_uses_normalized_numbers(), The repair map must name a real orphan PDF that parses to the circular_number…, test_numbers_normalize_distinctly()

## Knowledge Gaps
- **60 isolated node(s):** `checks.sh script`, `measure.sh script`, `autoresearch.sh script`, `PYTHONPATH`, `TOKENIZERS_PARALLELISM` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1165 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **36 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `test_context_headers.py`, `WarrantJudge`, `test_paraphrase_rescue.py`, `generate.py`, `Qwen3MLXReranker`, `.grounded`, `test_attribution.py`, `test_rerank_set_encoder.py`, `api.py`, `.build`, `corpus_spaces.py`, `benchmark.py`, `HybridRetriever`, `test_spaces_app.py`, `scrape_regulations.py`, `test_certainty.py`, `test_context_recall.py`, `test_benchmark.py`, `test_rerank_jina_v3.py`, `TestRetrievalBenchmarkNdcg`, `test_spaces.py`, `Embedder`, `context_headers.py`, `test_selective_citations.py`, `ExtractiveStubGenerator`, `JinaMLXReranker`, `SpladeIndex`, `build_lineage`, `segment.py`, `RAGPipeline`, `test_hyde.py`, `test_injection.py`, `main`, `paraphrase_rescue.py`, `.query`, `validate_golden_v7`, `resolve_chunk_spans`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `load_golden()` connect `HybridRetriever` to `_unique`, `test_golden_v7_packet.py`, `Frame`, `generate.py`, `adjudicate`, `backfill_escalations.py`, `remap_doc_ids.py`, `gemini_adjudicate.py`, `benchmark.py`, `seed_v7.py`, `agreement.py`, `test_finetune_eval_phase0.py`, `build_default_pipeline`, `run_judge`, `hybrid_gate_sweep.py`, `relabel_repooled.py`, `adjudicate_draft.py`, `test_finetune_holdout.py`, `JinaMLXReranker`, `phase_judge`, `segment.py`, `test_measure.py`, `main`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `_unique`, `measure_mrr`, `test_integration_e2e.py`, `generate.py`, `test_paraphrase_rescue.py`, `test_golden_v7_gate.py`, `measure_retrieval_recall`, `sebi_rag/eval_asof.py`, `measure_parsing_latency`, `api.py`, `measure_temporal_accuracy`, `benchmark.py`, `HybridRetriever`, `Chunk`, `build_default_pipeline`, `hybrid_gate_sweep.py`, `TestRetrievalBenchmarkNdcg`, `measure_context_precision`, `Embedder`, `measure_supersession_precision`, `build_lineage`, `run_all_metrics`, `test_eval_harness_v7.py`, `paraphrase_rescue.py`, `.query`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 68 inferred relationships involving `Chunk` (e.g. with `dataset_quality()` and `NLIAttributionScorer`) actually correct?**
  _`Chunk` has 68 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `run()`) actually correct?**
  _`RAGPipeline` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `Settings` (e.g. with `main()` and `main()`) actually correct?**
  _`Settings` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `HybridRetriever` (e.g. with `main()` and `main()`) actually correct?**
  _`HybridRetriever` has 42 INFERRED edges - model-reasoned connections that need verification._