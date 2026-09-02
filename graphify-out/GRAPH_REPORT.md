# Graph Report - SEBI circular RAG  (2026-09-03)

## Corpus Check
- 249 files · ~239,107 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3316 nodes · 6897 edges · 205 communities (165 shown, 40 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 661 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `36fe9cd1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- load_golden
- test_golden_v7_packet.py
- test_selective_citations.py
- telemetry_engine.py
- RAGPipeline
- test_golden_v7_gate.py
- derive_validity
- Frame
- test_finetune_mine_structural.py
- test_api.py
- segment.py
- SpladeIndex
- export_datasets.py
- test_finetune_synthesize_queries.py
- test_paraphrase_rescue.py
- test_attribution.py
- test_regulations.py
- Settings
- mine_structural_pairs.py
- test_spaces.py
- app.py
- test_finetune_train_lora.py
- SubjectSimJudge
- extract_misses.py
- context_headers.py
- demote_superseded
- test_finetune_eval_phase0.py
- test_reg_lineage.py
- test_conformal.py
- extract_citations
- test_finetune_roundtrip_filter.py
- test_dataset_cards.py
- test_ui.py
- test_golden_v7_gemini.py
- answer_with_abstention
- backfill_escalations.py
- test_spaces_app.py
- test_golden_v7_local.py
- _is_non_sebi_domain
- test_export_datasets.py
- Chunk
- sebi_rag/eval_asof.py
- test_corpus.py
- parse_meta
- test_trecio.py
- test_rerank_set_encoder.py
- _unique
- _row
- gemini_adjudicate.py
- test_hyde.py
- benchmark.py
- test_finetune_holdout.py
- test_label_tier.py
- scrape_sebi.py
- agreement.py
- hierarchical_chunk
- HybridRetriever
- Lineage
- test_rerank_jina_v3.py
- sebi_rag/verify_master.py
- generate.py
- validate_golden
- api.py
- test_pipeline.py
- build_default_pipeline
- publish_hf.py
- test_export_integration.py
- MeasureResult
- ui.py
- test_scrape_sebi.py
- ValueError
- test_lineage.py
- audit_label_provenance.py
- adjudicate
- test_expand.py
- _bootstrap_ci
- test_eval_harness_v7.py
- Path
- test_golden_v7_agreement.py
- validate_golden_v7
- read_trec_run
- test_scrape_regulations.py
- eval_harness.py
- validate
- measure.py
- _strip_context_header
- test_app_zerogpu.py
- Qwen3MLXReranker
- sha256_dir
- adjudicate_draft.py
- test_golden_v7_pool.py
- test_push_datasets.py
- scrape_regulations.py
- build_spaces_pipeline
- stats.py
- test_bench_retrieval_artifacts.py
- ingest_pdf.py
- hybrid_gate_sweep.py
- paired_delta
- Handler
- clopper_pearson_ci
- test_audit_reg_edges.py
- test_app_asof.py
- eval_generator_for
- Embedder
- trace_failure.py
- remap_doc_ids.py
- measure_supersession_precision
- test_build_reg_edges.py
- test_canary_generator.py
- test_injection.py
- build_regulatory_index
- phase_judge
- test_acquire_missing.py
- resolve_chunk_spans
- pipeline
- canary.sh
- corpus_integrity.py
- _resolve_governing_spans
- regression_detector.py
- mine_hard_negatives
- consolidation_edges
- run.sh
- write_run_doc
- ce_query_reform_probe.py
- main
- measure_context_precision
- audit_reg_edges.py
- seed_v7.py
- refresh.sh
- run_judge
- eval_json.py
- measure_mrr
- measure_parsing_latency
- _alias_keys
- measure_temporal_accuracy
- relabel_repooled.py
- test_build_index_out_dir.py
- _FakeDenseIndex
- apply
- sweep_rrf_k.py
- normalize_circular_number
- autoresearch.sh
- Master Circular for Mutual Funds (2026)
- build_report
- lineage_anomaly.py
- SEBI Master Circular for Mutual Funds (2020)
- validate_golden.py
- test_ingest_refs.py
- measure_retrieval_recall
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
- dev.sh
- _provision_agree
- notify.sh
- start_phoenix.sh
- SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026
- SEBI Master Circular for Stock Brokers (2018)
- sebi_rag/autoresearch/__init__.py
- conftest.py
- Optimize Slash Command
- Seen Circular IDs
- SEBI Master Circular on Exchange Traded Derivatives (2012)
- SEBI Master Circular for REITs (2025)
- SEBI Master Circular for Mutual Funds (2024)
- Hugging Face Spaces Requirements
- SEBI Master Circular for Credit Rating Agencies
- SEBI Master Circular for ESG Rating Providers
- SEBI Master Circular for REITs
- SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122
- reg_lineage.py
- main
- test_certainty.py
- TestPerQueryRecall
- scripts/verify_master.py
- _FakeResponse
- discover_new.py
- test_context_recall.py
- test_measure.py
- test_benchmark.py
- resolve_stems
- validate_corpus.py
- main
- SetEncoderReranker
- OllamaGenerator
- faithfulness
- parse_excerpt_choice
- _FixedOrderReranker
- build_golden.py
- .encode
- mc_topic
- _as_bool
- _HallucinatingGenerator
- sebi-rag

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 118 edges
2. `RAGPipeline` - 63 edges
3. `HybridRetriever` - 57 edges
4. `hierarchical_chunk()` - 55 edges
5. `Settings` - 54 edges
6. `HashEmbedder` - 48 edges
7. `ExtractiveStubGenerator` - 47 edges
8. `load_golden()` - 41 edges
9. `build_lineage()` - 39 edges
10. `BGEM3Embedder` - 35 edges

## Surprising Connections (you probably didn't know these)
- `test_vectors_exposes_context_recall()` --calls--> `vectors()`  [INFERRED]
  tests/test_context_recall.py → scripts/golden_v7/score.py
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

## Communities (205 total, 40 thin omitted)

### Community 0 - "load_golden"
Cohesion: 0.13
Nodes (30): eligible(), main(), SPIKE — throwaway, not preregistered. Answers one question before any R6 design…, main(), main(), main(), ADR-004 adoption: calibrate abstain_threshold for jina-reranker-v3-mlx's score…, main() (+22 more)

### Community 1 - "test_golden_v7_packet.py"
Cohesion: 0.07
Nodes (54): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+46 more)

### Community 2 - "test_selective_citations.py"
Cohesion: 0.08
Nodes (54): citation_scorer_for(), The single enable/disable AND backend decision for B'. Returns None when…, Callable compatible with select_citations' scorer.rerank() signature. Wraps…, Context ids the answer rests on. Scores each context via `scorer`, keeps those…, select_citations(), warrant_scorer(), _chunk(), _FakeReranker (+46 more)

### Community 3 - "telemetry_engine.py"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 4 - "RAGPipeline"
Cohesion: 0.15
Nodes (33): Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)…, smoke_pipeline(), smoke_pipeline(), run_retrieval_benchmark(), load_circulars(), Path, HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable… (+25 more)

### Community 5 - "test_golden_v7_gate.py"
Cohesion: 0.07
Nodes (43): derive_floors(), metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the…, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,…, True iff every floor's metric is present in `report_gate` and meets it. Missing…, select_golden() (+35 more)

### Community 6 - "derive_validity"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation. Locked…, Validity of one circular from the tiered edge list (any scope: the function…, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 7 - "Frame"
Cohesion: 0.07
Nodes (42): load_runs(), main(), Path, Assign epochs to the archived runs and write the epoch registry. Every run's…, _fmt(), guard_pair(), main(), Path (+34 more)

### Community 8 - "test_finetune_mine_structural.py"
Cohesion: 0.10
Nodes (31): _is_signoff_boilerplate(), _leaks_metadata(), mine_citation_context(), mine_heading_section(), mine_subject_body(), First line matching the numbered-clause pattern -> (heading, rest). None if no…, _split_heading(), Offline tests for scripts/finetune/mine_structural_pairs.py's pure transforms.… (+23 more)

### Community 9 - "test_api.py"
Cohesion: 0.07
Nodes (26): FastAPI, integration, _citation_meta(), create_app(), Truncate chunk text for a response payload; append an ellipsis if cut., Build one CitationMeta per unique circular (first-seen chunk wins).…, _truncate_preview(), _CannedGenerator (+18 more)

### Community 10 - "segment.py"
Cohesion: 0.11
Nodes (16): Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., _is_table_row_candidate(), _is_table_row_filler(), _is_toc_row_candidate(), _merge_table_rows(), Segmentation: hierarchical chunking + metadata + stable citation IDs. Minimal,…, Nesting depth of a numbered line ("2.1.3" -> 2), or None if it isn't one at all., A numbered line whose own trailing text is short and does NOT end in a clause… (+8 more)

### Community 11 - "SpladeIndex"
Cohesion: 0.07
Nodes (29): RuntimeError, main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.… (+21 more)

### Community 12 - "export_datasets.py"
Cohesion: 0.11
Nodes (24): build_aikosh_pack(), build_chunk_rows(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows(), build_zenodo_pack() (+16 more)

### Community 13 - "test_finetune_synthesize_queries.py"
Cohesion: 0.04
Nodes (10): _FakeResponse, Offline tests for scripts/finetune/synthesize_queries.py. The candidate…, Security-relevant: base_url is CLI-configurable here (unlike…, The plan's own finding: self-assigned stratum labels are unreliable. Even if…, A chunk that trails into a signature block or closing 'available on the…, Unlike _is_signoff_boilerplate (which only checks the OPENING, so it doesn't…, test_call_omlx_never_reads_anthropic_auth_token(), test_has_boilerplate_detects_signature_anywhere_not_just_at_start() (+2 more)

### Community 14 - "test_paraphrase_rescue.py"
Cohesion: 0.09
Nodes (40): is_degenerate(), Protocol, QueryRewriter, Paraphrase rescue for the cross-encoder score floor. Preregistered in…, Re-score `pool` with a rewritten query when `reranked` is below `floor`.…, Rewrites a lay-vocabulary query into statutory vocabulary. Returns None when it…, Fixed rewrite, for tests and for replaying a preregistered rewrite., True when `rewritten` is unusable and the rescue should be abandoned.… (+32 more)

### Community 15 - "test_attribution.py"
Cohesion: 0.07
Nodes (33): entailment_index(), NLIAttributionScorer, NLI attribution scoring for B' citation selection. B' asks "does this context…, Index of the entailment class in a model's label map. Read from the checkpoint…, Scores each context by P(entailment) of the answer given that context.…, Wrap an already-constructed cross-encoder (also the test seam)., _softmax(), pick_device() (+25 more)

### Community 16 - "test_regulations.py"
Cohesion: 0.08
Nodes (35): _jaccard(), load_regulations(), name_tokens(), Path, Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6). Regulations…, Resolve a cited regulation name+year to a canonical reg_id. Returns (reg_id,…, Load data/corpus/regulations.jsonl into a list of regulation records. Thin…, Human-readable regulation name. Year disambiguates same-short_name repeal pairs… (+27 more)

### Community 17 - "Settings"
Cohesion: 0.15
Nodes (27): is_master(), main(), Is the eval set measuring retrieval, or measuring its own construction? Read-…, main(), R3 §3.1 — mine cross-reference (A cites B) candidate pairs. Spec:…, main(), _get(), Path (+19 more)

### Community 18 - "mine_structural_pairs.py"
Cohesion: 0.13
Nodes (27): build_supersession_pairs(), Pure transform: corpus + lineage -> labeled circular pairs. label is…, load_chunks_by_doc(), load_corpus_records(), load_minable_docs(), main(), mine_lineage_pairs(), Path (+19 more)

### Community 19 - "test_spaces.py"
Cohesion: 0.08
Nodes (26): _grounded_prompt(), F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and the…, ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo. All classes implement…, External Space first; on ANY failure fall back to the local CPU model.…, Primary generator: calls a public LLM Space via gradio_client. Wired to… (+18 more)

### Community 20 - "app.py"
Cohesion: 0.08
Nodes (39): _append_message(), _blank_previews(), _build_citations_markdown(), build_ui(), _certainty_badge(), _cycle_messages_until_done(), _empty_citations_md(), _faithfulness_badge() (+31 more)

### Community 21 - "test_finetune_train_lora.py"
Cohesion: 0.09
Nodes (38): apply_lora(), build_dataset(), check_trainable_ratio(), find_latest_checkpoint(), load_pairs(), main(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-… (+30 more)

### Community 22 - "SubjectSimJudge"
Cohesion: 0.17
Nodes (10): ADOPTED gate (eval_gate round 3): deterministic groundedness signal — max…, Max cosine(query, doc subject line) over contexts — the primary gate signal,…, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge, subject_sim == threshold (0.42) passes the gate (>= comparison)., section_score == section_threshold (0.60) passes via second tier., test_section_score_exactly_at_threshold_passes(), test_subject_sim_exactly_at_threshold_passes() (+2 more)

### Community 23 - "extract_misses.py"
Cohesion: 0.14
Nodes (22): classify_answer(), classify_query(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any…, Chunk IDs embed section headings containing spaces, so parse TREC fields… (+14 more)

### Community 24 - "context_headers.py"
Cohesion: 0.09
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 25 - "demote_superseded"
Cohesion: 0.20
Nodes (17): contexts_for(), demote_superseded(), Down-weight reranked (chunk, score) pairs from superseded circulars and re-…, As-of exclusion or supersession demotion, applied to a reranked list. Extracted…, OLD_E superseded by an explicit clause; OLD_I only by a title heuristic., Backward compatibility: the default reproduces current behaviour exactly., An explicit clause anywhere outranks a heuristic edge — evidence wins., _score() (+9 more)

### Community 26 - "test_finetune_eval_phase0.py"
Cohesion: 0.10
Nodes (34): compare(), gate_verdict(), main(), parse_run_doc(), Path, Phase A eval (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-…, Statistical replacement for the original asymmetric directional screen…, run.doc.trec is a VALID 6-field TREC file at circular level… (+26 more)

### Community 27 - "test_reg_lineage.py"
Cohesion: 0.12
Nodes (33): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+25 more)

### Community 28 - "test_conformal.py"
Cohesion: 0.10
Nodes (31): _control_summary(), main(), phase_calibrate(), phase_report(), R7 conformal abstention calibration: generate -> calibrate -> report phases.…, Current production behaviour, exactly as shipped -- no LOO recalibration, the…, Re-simulates each row's abstention decision under the CALIBRATED thresholds,…, _simulated_summary() (+23 more)

### Community 29 - "extract_citations"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 30 - "test_finetune_roundtrip_filter.py"
Cohesion: 0.14
Nodes (26): filter_boilerplate(), load_rows(), Path, Phase 1 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-…, Prefer the row's own positive_doc field (future runs); fall back to the reverse…, Retrieves with each row's query against `retriever` (the frozen base index) and…, Returns (kept, n_dropped)., resolve_positive_doc() (+18 more)

### Community 31 - "test_dataset_cards.py"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 32 - "test_ui.py"
Cohesion: 0.05
Nodes (10): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., Every yielded tuple — loading, streaming chunks, final — must match the output…, Regression guard for the zip-misalignment class of bug (app.py:389): a…, _validate_api_url runs inside submit_query_stream's try block — a ValueError…, _Resp, test_submit_query_all_yields_share_arity(), test_submit_query_preview_matches_own_circular(), test_submit_query_retrieval_only_prepends_banner() (+2 more)

### Community 33 - "test_golden_v7_gemini.py"
Cohesion: 0.11
Nodes (28): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply… (+20 more)

### Community 34 - "answer_with_abstention"
Cohesion: 0.13
Nodes (26): answer_with_abstention(), parse_yes_no(), First yes/no in the reply; unparseable fails OPEN (grounded=True) so the gate…, _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., rerank_top exactly at 0.85 overrides judge abstention (HYBRID_THRESHOLD=0.85)., rerank_top just below 0.85 does NOT override judge abstention., When no judge is present, hybrid gate logic must be inert (no crash). (+18 more)

### Community 35 - "backfill_escalations.py"
Cohesion: 0.16
Nodes (22): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+14 more)

### Community 36 - "test_spaces_app.py"
Cohesion: 0.07
Nodes (6): app_module(), fixture, HF Spaces demo (root app.py): citations table + preview accordion logic. Fully…, app.py does `import spaces` (ZeroGPU) at module scope; stub it., _stub_spaces_package(), test_get_chunk_text_builds_once_and_caches()

### Community 37 - "test_golden_v7_local.py"
Cohesion: 0.10
Nodes (27): _extract_text(), _post_local(), OpenAI chat-completions response -> reply text: the first choice's message…, One blind-protocol call to the oMLX server's OpenAI-compatible endpoint. Auth…, Qwen-family models may emit <think>...</think> reasoning as inline text,…, _strip_thinking(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external… (+19 more)

### Community 38 - "_is_non_sebi_domain"
Cohesion: 0.10
Nodes (29): _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain. Case-…, The non-SEBI domain filter must match words, not substrings. Shipped 2026-07-30…, Any single-token keyword <= 5 chars is a substring hazard. Embedding it inside…, Query mentioning both SEBI and RBI should NOT abstain — SEBI intent wins., Empty query should not trigger the non-SEBI filter., FEMA keyword in a SEBI context should NOT abstain — SEBI intent wins., The exact query that exposed the bug. (+21 more)

### Community 39 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 40 - "Chunk"
Cohesion: 0.07
Nodes (23): Generator, Judge, _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_warrant_scores(), Protocol, Prompt for the warrant judge: evaluate each excerpt's warrant for the answer.… (+15 more)

### Community 41 - "sebi_rag/eval_asof.py"
Cohesion: 0.20
Nodes (16): AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Aggregate case results with an exact confidence interval. Pure function of the…, run_pipeline_cases(), run_selector_cases(), summarize() (+8 more)

### Community 42 - "test_corpus.py"
Cohesion: 0.13
Nodes (28): Path, corpus.load_circulars edge-case coverage. load_circulars reads a JSONL corpus…, Provided optional fields are passed through to CircularMeta., Multiple records produce multiple chunks., Blank lines between records are silently skipped., Malformed JSON raises ValueError (json.loads default)., load_circulars accepts both str and Path., load_circulars accepts a pathlib.Path. (+20 more)

### Community 43 - "parse_meta"
Cohesion: 0.15
Nodes (17): Pattern, _iso_date(), _labeled_date(), parse_meta(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash… (+9 more)

### Community 44 - "test_trecio.py"
Cohesion: 0.12
Nodes (25): main(), Emit TREC qrels for an eval set, keyed by its golden_sha256. .venv/bin/python…, chunk_docid(), circular_docid(), MalformedChunkId, Standards-compliant TREC run and qrels emission. The archived runfiles are not…, Write TREC qrels (`qid 0 docid rel`) at circular level. Binary relevance:…, Raised when an id cannot yield a whitespace-free TREC doc id. (+17 more)

### Community 45 - "test_rerank_set_encoder.py"
Cohesion: 0.14
Nodes (13): _chunk(), _FakeOutput, _FakeScores, _FakeSetEncoderModule, Offline tests for the webis/set-encoder-base wrapper (2026-08-26 Set-Encoder…, Stands in for the torch.Tensor `CrossEncoderModule.score(...).scores` return…, Stands in for lightning_ir.CrossEncoderModule — records the query/docs it was…, Bypass __init__ (no lightning-ir import / model download / network). (+5 more)

### Community 46 - "_unique"
Cohesion: 0.15
Nodes (24): main(), parse_args(), Namespace, Compare query-expansion arms (current prod / no-expand / HyDE) on a golden set.…, run_arm(), doc_ids_deduped(), fmt(), mean_or_none() (+16 more)

### Community 47 - "_row"
Cohesion: 0.12
Nodes (27): decide(), Spec sec7 promotion rules for one row. `votes_by_annotator` is this row's votes…, Abstain rows have no explicit claude vote at all (Task 8 never judged them) -…, Both externals independently think something DOES govern (disputing the…, The LLM leg is whichever single non-claude/non-human annotator voted - "qwen"…, Amendment 2026-07-26 (user-approved): the promotion unit is the PROVISION, not…, External marked claude's chunk governing plus extras: claude's label is…, The abstain protocol can never emit non-empty governing (no letters are… (+19 more)

### Community 48 - "gemini_adjudicate.py"
Cohesion: 0.10
Nodes (26): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec… (+18 more)

### Community 49 - "test_hyde.py"
Cohesion: 0.12
Nodes (17): call(), main(), _norm(), Does answering a golden_v7 row require a circular the corpus does not hold?…, Uppercase, strip all whitespace — so 'CIR/MIRSD/5/ 2013' matches…, Returns (answer, reasoning). The judge is a reasoning model: the oMLX API…, windows(), HydeExpander (+9 more)

### Community 50 - "benchmark.py"
Cohesion: 0.20
Nodes (20): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, beir_corpus_rows(), beir_query_rows(), build_golden_v6(), dir_fingerprint(), enrich_golden_item(), export_beir() (+12 more)

### Community 51 - "test_finetune_holdout.py"
Cohesion: 0.14
Nodes (24): build(), classify_rows(), gold_circulars(), main(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-…, Every distinct circular any golden_v7 row cites as relevant, sorted for…, Deterministic seeded sample. round(), not int(), so 159*0.30=47.7 lands on 48… (+16 more)

### Community 52 - "test_label_tier.py"
Cohesion: 0.12
Nodes (20): classify_tier(), human_reviewed_ids(), main(), Path, Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.…, Map provenance to the controlled vocabulary. `human_reviewed` (row appears in…, Row ids present in the human labelling packet., Controlled-vocabulary label_tier over golden_v7 (spec A §8.3). (+12 more)

### Community 53 - "scrape_sebi.py"
Cohesion: 0.22
Nodes (16): check_robots(), main(), Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, Log-only re-verification that our paths are still crawlable., discover(), fetch(), _listing_url(), looks_like_pdf() (+8 more)

### Community 54 - "agreement.py"
Cohesion: 0.15
Nodes (21): _claude_accuracy_ci(), gwet_ac1(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation…, Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a prevalence-… (+13 more)

### Community 55 - "hierarchical_chunk"
Cohesion: 0.15
Nodes (24): hierarchical_chunk(), _paragraphs(), Split into units each <= max_chars. PDF-extracted text often lacks blank-line…, Document -> section -> paragraph chunks with stable IDs. A "section" is…, _body(), Chunker (segment.hierarchical_chunk) behaviour. Regression guard for the "5.…, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_absorption_respects_300_char_cap() (+16 more)

### Community 56 - "HybridRetriever"
Cohesion: 0.09
Nodes (33): _doc_checksum(), _embedder_identity(), HybridRetriever, Path, F3 (ADR-001): encode only new/changed documents; reuse cached embedding rows…, Deterministic per-document checksum over its (enriched) chunk texts — captures…, The embedder's own identity stamp (BGEM3Embedder/HashEmbedder set `.model_id`),…, BM25 lexical index (bm25s). (+25 more)

### Community 57 - "Lineage"
Cohesion: 0.18
Nodes (9): Lineage, Path, Connected component over supersedes/superseded_by (both tiers)., The circular in this family that governs on date as_of (ISO), or None when…, test_governing_on_cycle_safe(), test_governing_on_parallel_branches_max_date_wins(), test_lineage_load_old_file_defaults_empty_edges(), test_lineage_save_load_roundtrip() (+1 more)

### Community 58 - "test_rerank_jina_v3.py"
Cohesion: 0.14
Nodes (17): ADR-004: the single decision for which model orders the RETRIEVAL pool…, retrieval_reranker_for(), _chunk(), _FakeJinaBackend, Offline tests for the jina-reranker-v3-mlx wrapper (ADR-004) — translation…, Same bug, same fix, second script: eval_asof.py also builds its own RAGPipeline…, Stands in for the vendor's MLXReranker.rerank() — same return shape (list of…, Bypass __init__ (no snapshot_download / mlx / network). (+9 more)

### Community 59 - "sebi_rag/verify_master.py"
Cohesion: 0.19
Nodes (20): diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13). Pure functions only:…, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows., render_markdown() (+12 more)

### Community 60 - "generate.py"
Cohesion: 0.09
Nodes (28): Ground truth: what do the 4 CE_MISMATCH rows actually DO in production? The…, Preregistered cohort measurement for the CE paraphrase rescue. Spec:…, What does the 0.05 cross-encoder score floor actually catch?…, cited_docs(), metrics(), Capture-once margin sweep for B' selective citations. One pipeline pass over…, Benchmark MLX generators on the golden set: faithfulness, groundedness,…, Retrieval-only benchmark with TREC runfile and reproducibility metadata. Use… (+20 more)

### Community 61 - "validate_golden"
Cohesion: 0.19
Nodes (13): per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.…, validate_golden(), Answerable-but-unjudged rows are excluded from metrics, never scored 0.…, A real, fully-populated golden row, so the fixture cannot drift out of sync…, v7-ls-038/039/040 are answerable but unjudged; they carry…, _template(), test_abstain_rows_still_excluded() (+5 more)

### Community 62 - "api.py"
Cohesion: 0.12
Nodes (19): BaseModel, CitationMeta, _compute_kwargs(), _embed_kwargs(), QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline. Run (real stack; loads the…, _compute_kwargs() plus model_path - BGEM3Embedder-only, never spread into… (+11 more)

### Community 63 - "test_pipeline.py"
Cohesion: 0.13
Nodes (19): _build_chunks(), _build_pipeline(), _FixedReranker, _master_reissue_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline. Runs fully offline…, Offline pipeline whose single circular rests on a repealed regulation., Deterministic reranker: score by doc_id lookup (test-only)., Two master circulars on one topic: `mc_topic` infers supersession. Neither text… (+11 more)

### Community 64 - "build_default_pipeline"
Cohesion: 0.10
Nodes (22): main(), SPIKE/GATE (throwaway, not preregistered) — R5's own precondition from the…, phase_generate(), main(), What actually makes a context window large: chunk size, or chunk count? Read-…, _doc(), main(), P0 prep: price a larger MLX generator before committing to the R0 upgrade.… (+14 more)

### Community 65 - "publish_hf.py"
Cohesion: 0.19
Nodes (18): export_golden_v7_arrow(), log(), main(), Path, Run export_datasets.py then add golden_v7 Arrow config., Upload dist/datasets/ to HF dataset repo., Run make index to rebuild FAISS+BM25 before upload., Upload data/index/ to HF index repo. (+10 more)

### Community 66 - "test_export_integration.py"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 67 - "MeasureResult"
Cohesion: 0.18
Nodes (8): main(), MeasureReport, MeasureResult, Run all (or specified) metrics sequentially., run_all_metrics(), Empty metrics list is falsy → defaults to ALL_METRICS., TestDataClasses, TestRegistry

### Community 68 - "ui.py"
Cohesion: 0.11
Nodes (30): _append_message(), _blank_previews(), _build_citations_markdown(), build_ui(), _certainty_badge(), _cycle_messages_until_done(), _empty_citations_md(), _faithfulness_badge() (+22 more)

### Community 69 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 70 - "ValueError"
Cohesion: 0.17
Nodes (20): _assert_fixed_tail(), convert_run_dir(), main(), Path, Back-convert archived runfiles into standards-compliant TREC artifacts. The…, Trailing field of the first line; also the whitespace precondition check., read_trec_run assumes qid and tag carry no whitespace. Verify per line., Write run.chunk.trec, run.doc.trec and docids.tsv for one archived run. (+12 more)

### Community 71 - "test_lineage.py"
Cohesion: 0.12
Nodes (20): annotate_corpus(), detect_relations(), Update each corpus record's supersession_status + superseded_by + supersedes…, Return (relation, referenced_circular) for each distinct reference., _lin_chain(), P2 lineage / supersession resolution tests., A circular that names another circular BEFORE the supersede trigger word must…, test_annotate_corpus_adds_master_fields_and_consolidates_edges() (+12 more)

### Community 72 - "audit_label_provenance.py"
Cohesion: 0.21
Nodes (15): audit(), collect_artifacts(), _ids_from_csv(), _ids_from_dir(), _ids_from_jsonl(), main(), Path, Report what the annotation artifacts can account for, before classifying.… (+7 more)

### Community 73 - "adjudicate"
Cohesion: 0.18
Nodes (16): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt) -> str`…, Scans the per-row cache for `ids` and returns the ones flagged parse_error:…, _current_model(), main(), pilot() (+8 more)

### Community 74 - "test_expand.py"
Cohesion: 0.16
Nodes (16): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and…, Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), Query-side lexical expansion (intervention #2, glossary variant).…, test_all_five_sparse_failure_queries_expand(), test_expanded_sparse_query_hits_statutory_chunk() (+8 more)

### Community 75 - "_bootstrap_ci"
Cohesion: 0.16
Nodes (9): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict., When torch+MPS available, returns memory stats dict. (+1 more)

### Community 76 - "test_eval_harness_v7.py"
Cohesion: 0.42
Nodes (11): run_eval(), test_eval_harness_metric_suite(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-…, _row(), test_as_of_is_passed_to_pipeline(), test_chunk_metrics_computed_for_span_rows(), test_gate_is_none_when_nothing_adjudicated() (+3 more)

### Community 77 - "Path"
Cohesion: 0.22
Nodes (21): _config_entry(), _emit(), export_all(), export_chunks(), export_citation_normalization(), export_corpus(), export_eval(), export_lineage() (+13 more)

### Community 78 - "test_golden_v7_agreement.py"
Cohesion: 0.19
Nodes (15): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw element is…, _min_agreement_fixture(), Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):…, The kappa base-rate paradox: one label dominates, raw agreement is high, yet…, _same_provision_fixture(), test_claude_accuracy_ci_returns_exact_and_provision(), test_cohen_kappa_both_constant_and_identical_is_one() (+7 more)

### Community 79 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 80 - "read_trec_run"
Cohesion: 0.33
Nodes (5): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), write_trec_run(), The archived runfiles embed section headings in the doc id., TestReadTrecRun

### Community 82 - "eval_harness.py"
Cohesion: 0.11
Nodes (22): aggregate(), eligible(), main(), measure(), Preregistered cohort measurement for supersession confidence tiering. Spec:…, Answerable, non-as_of, with gold citations: the rows citation metrics exist for., auroc(), best_threshold() (+14 more)

### Community 83 - "validate"
Cohesion: 0.33
Nodes (14): validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the document's own…, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations(), test_duplicate_text_across_records_flagged(), test_empty_text_is_not_a_duplicate_cluster(), test_flags_bad_issue_date() (+6 more)

### Community 84 - "measure.py"
Cohesion: 0.26
Nodes (12): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), Automated metric collection for the SEBI Circular RAG pipeline. Six on-demand…, test_retrieval_metrics(), _internal(), Prove the internal retrieval metrics are the standard ones. Skips unless the… (+4 more)

### Community 85 - "_strip_context_header"
Cohesion: 0.12
Nodes (18): build_citation_pairs(), _format_family(), Pure transform: corpus text -> citation-normalization rows. Mines in-body…, Every chunk's text is `"{doc_id} | {subject[:120]} | {section}\\n{body}"` -…, _strip_context_header(), build_text_to_doc_map(), Reverse lookup for rows predating the positive_doc field. Header- stripped to…, _has_boilerplate() (+10 more)

### Community 86 - "test_app_zerogpu.py"
Cohesion: 0.14
Nodes (13): app_module(), fixture, Regression coverage for the ZeroGPU-hardware workaround in app.py. Background:…, Inject a fake `spaces` module so app.py's `import spaces` succeeds offline, and…, Static guard: if `import spaces` or the `@spaces.GPU` decorator is ever…, It must stay dead code: calling it would request a real ZeroGPU allocation (and…, The functions actually on the request path (get_pipeline, run_query_stream)…, `hardware:` in README-spaces.md is not a documented Spaces config key (only… (+5 more)

### Community 87 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 88 - "sha256_dir"
Cohesion: 0.24
Nodes (11): main(), merge(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-…, Per-file sha256 of every file in the merged model dir - the plan's "sha256 into…, CPU by design, not MPS: this is a one-shot weight merge, not a training or…, sha256_dir(), Offline tests for scripts/finetune/merge_adapter.py's pure pieces. The actual… (+3 more)

### Community 89 - "adjudicate_draft.py"
Cohesion: 0.24
Nodes (12): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+4 more)

### Community 90 - "test_golden_v7_pool.py"
Cohesion: 0.26
Nodes (11): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, One gold doc with `n` chunks that ALL contain the word "broker", so a…, Regression (2026-07-25): a must_contain literal matching many gold-doc chunks…, _retriever(), _saturating_retriever(), test_bm25_leg_uses_raw_query_not_expansion() (+3 more)

### Community 91 - "test_push_datasets.py"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default:…, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 92 - "scrape_regulations.py"
Cohesion: 0.19
Nodes (13): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY).…, (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'. Takes the LAST bracket group…, _record() (+5 more)

### Community 93 - "build_spaces_pipeline"
Cohesion: 0.23
Nodes (13): build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux). Parallel…, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row() (+5 more)

### Community 94 - "stats.py"
Cohesion: 0.18
Nodes (8): bootstrap_ci(), BootstrapCI, ProportionCI, Uncertainty quantification for benchmark runs. The golden set is n=56…, Percentile bootstrap interval for the mean of per-query scores., Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests)., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 95 - "test_bench_retrieval_artifacts.py"
Cohesion: 0.15
Nodes (9): bench_retrieval must emit valid TREC alongside the legacy runfile., run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so every…, iv9/iv10 build a headered index beside data/index. Without an index override…, ADR-004: benchmarking jina-reranker-v3-mlx against the production cross-encoder…, 2026-08-26 Set-Encoder spec: benchmarking webis/set-encoder-base (via…, test_bench_retrieval_can_bench_an_alternate_index(), test_bench_retrieval_can_measure_the_reranked_order(), test_bench_retrieval_exposes_and_records_the_reranker_choice() (+1 more)

### Community 96 - "ingest_pdf.py"
Cohesion: 0.15
Nodes (19): Re-derive circular number + dates from each record's stored text and rewrite…, _existing_numbers(), extract_text(), ingest(), main(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars. Drop a circular PDF into data/raw/ and… (+11 more)

### Community 97 - "hybrid_gate_sweep.py"
Cohesion: 0.26
Nodes (11): current_gate_passes(), hybrid_gate_passes(), main(), parse_args(), Namespace, Hybrid abstention gate sweep — preregistered analysis. Preregistration:…, Reproduces the current production subject-gate OR (no hybrid override)., True if this row never reaches the subject-gate check at all (vetoed earlier by… (+3 more)

### Community 98 - "paired_delta"
Cohesion: 0.19
Nodes (7): paired_delta(), PairedResult, Compare run `b` against run `a` on their shared queries. Returns mean_b -…, True when the randomization test rejects at 1 - confidence AND the paired…, Randomization p-values use the (count+1)/(n+1) estimator, so a p-value of…, One query flipping out of 56 is exactly the iv9-style verdict: the…, TestPairedDelta

### Community 99 - "Handler"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 100 - "clopper_pearson_ci"
Cohesion: 0.22
Nodes (5): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, test_render_report_includes_ac1_and_provision(), The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 101 - "test_audit_reg_edges.py"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 102 - "test_app_asof.py"
Cohesion: 0.20
Nodes (6): app_module(), _expected_output_count(), fixture, As-of date plumbing in the Spaces UI (app.py)., 8 fixed fields + 2 per preview accordion + 4 meta badges. Matches the flat list…, test_run_query_yield_arity_matches_outputs_list_pipeline_free_paths()

### Community 103 - "eval_generator_for"
Cohesion: 0.16
Nodes (12): eval_generator_for(), The single generator decision for the eval stack. `derive_thresholds.py` sets…, The eval stack's generator choice must be one shared decision.…, Uses an injected loader so the test stays offline., Silently falling back to the stub would derive floors under semantics the…, Must assert the factory is CALLED, not merely imported. Verified 2026-08-12 by…, A factory both call is not enough - they must pass the same setting, or the…, test_both_eval_scripts_read_the_same_setting() (+4 more)

### Community 104 - "Embedder"
Cohesion: 0.20
Nodes (6): Embedder, ndarray, Protocol, DenseIndex, ndarray, FAISS IndexFlatIP over L2-normalized vectors (cosine).

### Community 105 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 106 - "remap_doc_ids.py"
Cohesion: 0.33
Nodes (10): main(), Rewrite golden_v7 doc references after the corpus renumbering (2026-07-25…, remap(), Doc-id remapping after the 2026-07-25 corpus renumbering (Task 4)., _row(), test_input_rows_are_not_mutated(), test_matching_is_normalization_insensitive(), test_remaps_must_not_cite() (+2 more)

### Community 107 - "measure_supersession_precision"
Cohesion: 0.16
Nodes (11): detect_relations_ex(), Like detect_relations, but returns dict records with evidence spans., _window(), measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, _verify_supersession_edge(), test_detect_relations_ex_evidence_and_extractor() (+3 more)

### Community 108 - "test_build_reg_edges.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 109 - "test_canary_generator.py"
Cohesion: 0.27
Nodes (8): _canary_jscode(), _ops_timeout(), The eval canary must fit its timeout and alert on real regressions. Measured…, n8n gives up first if its budget is smaller, so the ops timeout is never…, A threshold above the healthy value fires every run. citation_precision was…, test_alert_thresholds_sit_below_measured_baselines(), test_n8n_timeout_not_tighter_than_the_ops_budget(), test_ops_timeout_fits_the_measured_runtime()

### Community 110 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 111 - "build_regulatory_index"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 112 - "phase_judge"
Cohesion: 0.36
Nodes (9): _aggregate(), eligible(), main(), _measure(), phase_generate(), phase_judge(), phase_report(), R1 §4/§6 cohort measurement: control (cross-encoder) vs W1 (warrant judge).… (+1 more)

### Community 114 - "resolve_chunk_spans"
Cohesion: 0.23
Nodes (15): BenchmarkIssue, chunks_by_doc(), _norm_ws(), qrels_rows(), Span {doc, quote} -> matching chunk ids (all overlap matches count). Legacy…, resolve_chunk_spans(), _span_resolution_issues(), _chunks() (+7 more)

### Community 115 - "pipeline"
Cohesion: 0.67
Nodes (3): _ollama_up(), pipeline(), fixture

### Community 116 - "canary.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, SEBI_RAG_EVAL_GENERATOR, canary.sh script, TOKENIZERS_PARALLELISM

### Community 117 - "corpus_integrity.py"
Cohesion: 0.36
Nodes (7): check_meta_fields(), load_chunks(), load_corpus(), main(), Load corpus into a dict keyed by circular_number., Load chunks and return (records, doc_ids)., Check that chunk meta has expected CircularMeta fields.

### Community 118 - "_resolve_governing_spans"
Cohesion: 0.36
Nodes (8): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote} spans, looked…, _resolve_governing_spans(), _pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool(), test_resolve_governing_spans_short_body_uses_whole_body(), test_resolve_governing_spans_uses_first_60_body_chars()

### Community 119 - "regression_detector.py"
Cohesion: 0.36
Nodes (7): extract_metrics(), load_floors(), load_latest_runs(), main(), Load floors from gate_v7.json., Load most recent eval runs sorted by timestamp., Extract metric values from a run.

### Community 120 - "mine_hard_negatives"
Cohesion: 0.24
Nodes (16): mine_hard_negatives(), One batched embed + one batched FAISS search for the whole set - not a per-…, _FakeChunk, _FakeEmbedder, _FakeRetriever, mine_hard_negatives only uses embed() to build the FAISS query vectors now (no…, Backward-compat: every mine_structural_pairs.py template has positive ==…, Phase 1's multi_hop rows: source_doc is the CITING document, but the positive… (+8 more)

### Community 121 - "consolidation_edges"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans…, _master(), test_annotate_idempotent() (+7 more)

### Community 122 - "run.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 123 - "write_run_doc"
Cohesion: 0.13
Nodes (19): Rankings, Path, Reverse map `docid -> full chunk id`, so nothing is lost., Valid 6-field TREC run at chunk granularity., Valid 6-field TREC run collapsed to circular level. Keeps each circular once,…, write_docids(), _write_lines(), write_run_chunk() (+11 more)

### Community 124 - "ce_query_reform_probe.py"
Cohesion: 0.38
Nodes (6): main(), _pool(), Probe: does query-side reformulation lift the CE score on the 4 CE_MISMATCH…, Return (ce_top, best relevant score, chunk_id of argmax)., Top-8 pool plus every relevant chunk, de-duplicated on chunk_id., _score()

### Community 125 - "main"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

### Community 126 - "measure_context_precision"
Cohesion: 0.50
Nodes (3): measure_context_precision(), Fraction of top-k chunks from relevant circulars. Unlike recall@k (which is…, TestContextPrecision

### Community 127 - "audit_reg_edges.py"
Cohesion: 0.33
Nodes (9): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+1 more)

### Community 128 - "seed_v7.py"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 129 - "refresh.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 130 - "run_judge"
Cohesion: 0.39
Nodes (7): _is_parseable(), _load_screen(), main(), R1 §3.3 degeneracy probe: does the warrant judge return a parseable reply?…, Mirrors generate.parse_warrant_scores' cleaning exactly, but reports whether…, run_answers(), run_judge()

### Community 131 - "eval_json.py"
Cohesion: 0.24
Nodes (10): log(), Margin sweep for B' selective citations on the golden_v7 adjudicated set. One…, run(), Emit one JSON line of retrieval/citation/abstention metrics using the persisted…, Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, One scoring path shared by `eval_json.py` (which measures) and…, Score one golden row through the production-shaped pipeline. Returns per-row…, Per-row records -> metric -> score vector, skipping rows where the metric was… (+2 more)

### Community 132 - "measure_mrr"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level. For each query, RR = 1/rank of first…, TestMRR

### Community 133 - "measure_parsing_latency"
Cohesion: 0.32
Nodes (5): measure_parsing_latency(), Path, Measure PDF ingestion throughput (chars/sec, ms/PDF). Samples 20 PDFs…, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 134 - "_alias_keys"
Cohesion: 0.29
Nodes (8): _alias_keys(), Candidate alias lookup keys, most literal first. Both the raw normalised form…, PMS/NCS/ILDS end in a literal S. Unconditional plural-stripping mapped them to…, reg_id resolved purely through the alias table, ignoring the corpus., A table key that no _alias_keys() output can produce is dead config., _resolved(), test_acronyms_ending_in_s_reach_their_own_entry(), test_every_alias_entry_is_reachable_from_some_spelling()

### Community 135 - "measure_temporal_accuracy"
Cohesion: 0.43
Nodes (3): measure_temporal_accuracy(), Measure fraction of as_of queries returning correct pre-supersession circular…, TestTemporalAccuracy

### Community 136 - "relabel_repooled.py"
Cohesion: 0.43
Nodes (6): _body(), main(), _norm(), pick(), Label the 7 rows re-pooled after the assemble_pool fix (2026-07-25 remediation…, (candidate, quote) pairs for this row: the answer_contains carrier first, then…

### Community 137 - "test_build_index_out_dir.py"
Cohesion: 0.29
Nodes (5): build_index must be able to target a scratch index directory. The iv9/iv10…, A --out flag that is parsed but ignored is worse than none: it reads as safe…, lineage.json lands next to the index it describes; writing it into data/index…, test_build_index_saves_to_the_resolved_out_dir_not_the_constant(), test_lineage_follows_the_out_dir()

### Community 138 - "_FakeDenseIndex"
Cohesion: 0.29
Nodes (3): _FakeDense, _FakeDenseIndex, Deterministic stand-in for faiss.IndexFlatIP.search: returns a fixed ranking…

### Community 139 - "apply"
Cohesion: 0.29
Nodes (7): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions` (keyed by…, test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only(), test_apply_queue_decision_leaves_row_untouched(), test_apply_row_without_a_decision_is_never_touched()

### Community 140 - "sweep_rrf_k.py"
Cohesion: 0.38
Nodes (6): main(), parse_args(), Namespace, Sweep RRF k_const values on a golden set. No index rebuild needed. Turn 1 of…, Retrieve+refuse at a single k_const. Returns per-query score dicts., run_one_k()

### Community 141 - "normalize_circular_number"
Cohesion: 0.18
Nodes (7): main(), Repair the 6 records whose body text was overwritten with one shared circular's…, normalize_circular_number(), Canonical COMPARISON key for a circular number: strip whitespace and trailing…, test_dedup_uses_normalized_numbers(), The repair map must name a real orphan PDF that parses to the circular_number…, test_numbers_normalize_distinctly()

### Community 142 - "autoresearch.sh"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 143 - "Master Circular for Mutual Funds (2026)"
Cohesion: 0.40
Nodes (5): Master Circular for Mutual Funds (2026), Circular on Development of Passive Funds, Extension of timelines for submission of offsite inspection data (Mutual Funds), SEBI (Mutual Funds) Regulations, 1996, SEBI (Mutual Funds) Regulations, 2026

### Community 144 - "build_report"
Cohesion: 0.31
Nodes (10): build_report(), Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid measurement;…, The headline number must be the 10 pipeline cases alone — the whole point of…, _results(), test_pipeline_metrics_are_not_polluted_by_selector_cases(), test_pooled_overall_carries_no_interval() (+2 more)

### Community 145 - "lineage_anomaly.py"
Cohesion: 0.60
Nodes (4): load_corpus(), load_lineage(), main(), Load corpus keyed by circular_number.

### Community 146 - "SEBI Master Circular for Mutual Funds (2020)"
Cohesion: 0.50
Nodes (4): SEBI Circular on Options Eligibility (2024), SEBI Master Circular for Mutual Funds (2020), SEBI Circular HO/24/13/12(4)2025-IMD-POD-1/I/2062/2026, SEBI Master Circular for Mutual Funds (2026)

### Community 147 - "validate_golden.py"
Cohesion: 0.83
Nodes (3): check_gate(), check_golden_set(), main()

### Community 148 - "test_ingest_refs.py"
Cohesion: 0.15
Nodes (11): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_fulltext_fallback_returns_earliest_body_reference() (+3 more)

### Community 149 - "measure_retrieval_recall"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 150 - "SEBI Master Circular for LODR Compliance"
Cohesion: 0.67
Nodes (3): SEBI Master Circular for LODR Compliance, SEBI Operational Circular for Non-convertible Securities (2022), SEBI Master Circular for RTAs (2023)

### Community 151 - "Master Circular for Alternative Investment Funds (AIFs) (2026)"
Cohesion: 1.00
Nodes (3): Master Circular for Alternative Investment Funds (AIFs) (2026), Revised regulatory framework for Angel Funds, Relaxation in timeline for disclosure of allocation methodology by Angel Funds

### Community 152 - "SEBI Circular on IRRA Platform"
Cohesion: 0.67
Nodes (3): Investor Risk Reduction Access (IRRA), SEBI Circular on IRRA Platform, Master Circular for Stock Brokers (2025)

### Community 164 - "_provision_agree"
Cohesion: 0.20
Nodes (10): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using the…, Does this external vote confirm claude's label, at PROVISION level? Amendment…, Different chunk copies of the same quoted provision agree at provision level…, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction(), test_provision_agree_disjoint_without_pool_is_false() (+2 more)

### Community 181 - "reg_lineage.py"
Cohesion: 0.29
Nodes (6): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus., derive_regulatory_basis(), Regulatory-basis status of one circular from its resolved regulations.…, test_derive_regulatory_basis_truth_table()

### Community 182 - "main"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl()

### Community 183 - "test_certainty.py"
Cohesion: 0.39
Nodes (8): _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons,…, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful(), test_no_context_reason_when_top_k_zero(), test_score_floor_reason(), test_subject_gate_reason_and_subject_sim_recorded()

### Community 185 - "scripts/verify_master.py"
Cohesion: 0.60
Nodes (4): pdf_url_for(), fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist. Usage:…

### Community 188 - "test_context_recall.py"
Cohesion: 0.39
Nodes (8): _chunk(), The gate must measure the context window, not just the fusion list.…, An abstention still had a context window; measuring retrieval delivery must not…, _reranked(), test_answer_records_the_context_ids_it_used(), test_context_ids_populated_even_when_abstaining(), test_context_ids_respect_top_k(), test_vectors_exposes_context_recall()

### Community 189 - "test_measure.py"
Cohesion: 0.29
Nodes (4): metrics_to_markdown(), Format results as a markdown table., Unit tests for sebi_rag.measure — automated metric collection., TestCLI

### Community 190 - "test_benchmark.py"
Cohesion: 0.36
Nodes (6): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields(), test_trec_run_and_research_judges_are_sidecar_only()

### Community 191 - "resolve_stems"
Cohesion: 0.33
Nodes (7): _add_months(), month_window(), date, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps., resolve_stems(), stem_of()

### Community 192 - "validate_corpus.py"
Cohesion: 0.38
Nodes (6): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair. Checks (per…, Every record's text must match the PDF its provenance names. Slow (re-extracts…, validate_deep()

### Community 193 - "main"
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 194 - "SetEncoderReranker"
Cohesion: 0.40
Nodes (3): webis/set-encoder-base via lightning-ir, wrapped to this project's Reranker…, Score candidates with lightning-ir's CrossEncoderModule.score. Mirrors…, SetEncoderReranker

### Community 196 - "faithfulness"
Cohesion: 0.67
Nodes (3): faithfulness(), Check that every circular id the answer cites (in square brackets) was actually…, test_faithfulness_scoring()

### Community 197 - "parse_excerpt_choice"
Cohesion: 0.67
Nodes (3): parse_excerpt_choice(), True iff the reply names a valid excerpt number. 'none' or anything unparseable…, test_parse_excerpt_choice_fails_closed()

## Knowledge Gaps
- **59 isolated node(s):** `checks.sh script`, `measure.sh script`, `autoresearch.sh script`, `PYTHONPATH`, `TOKENIZERS_PARALLELISM` (+54 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1194 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **40 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `load_golden`, `test_selective_citations.py`, `RAGPipeline`, `segment.py`, `SpladeIndex`, `test_paraphrase_rescue.py`, `test_attribution.py`, `test_spaces.py`, `SubjectSimJudge`, `context_headers.py`, `demote_superseded`, `answer_with_abstention`, `test_spaces_app.py`, `test_rerank_set_encoder.py`, `test_hyde.py`, `benchmark.py`, `hierarchical_chunk`, `HybridRetriever`, `test_certainty.py`, `test_rerank_jina_v3.py`, `generate.py`, `test_context_recall.py`, `api.py`, `test_benchmark.py`, `SetEncoderReranker`, `OllamaGenerator`, `test_expand.py`, `validate_golden_v7`, `Qwen3MLXReranker`, `scrape_regulations.py`, `build_spaces_pipeline`, `test_injection.py`, `resolve_chunk_spans`, `main`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `load_golden`, `eval_json.py`, `measure_mrr`, `measure_parsing_latency`, `measure_temporal_accuracy`, `test_api.py`, `test_paraphrase_rescue.py`, `measure_retrieval_recall`, `demote_superseded`, `Chunk`, `sebi_rag/eval_asof.py`, `benchmark.py`, `HybridRetriever`, `Lineage`, `TestPerQueryRecall`, `generate.py`, `api.py`, `test_pipeline.py`, `build_default_pipeline`, `MeasureResult`, `test_eval_harness_v7.py`, `eval_harness.py`, `measure.py`, `build_spaces_pipeline`, `hybrid_gate_sweep.py`, `Embedder`, `measure_supersession_precision`, `pipeline`, `measure_context_precision`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `load_golden()` connect `load_golden` to `seed_v7.py`, `test_golden_v7_packet.py`, `run_judge`, `Frame`, `relabel_repooled.py`, `test_finetune_eval_phase0.py`, `backfill_escalations.py`, `gemini_adjudicate.py`, `benchmark.py`, `test_finetune_holdout.py`, `agreement.py`, `build_default_pipeline`, `MeasureResult`, `adjudicate`, `test_eval_harness_v7.py`, `eval_harness.py`, `adjudicate_draft.py`, `hybrid_gate_sweep.py`, `remap_doc_ids.py`, `phase_judge`, `main`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 68 inferred relationships involving `Chunk` (e.g. with `dataset_quality()` and `NLIAttributionScorer`) actually correct?**
  _`Chunk` has 68 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `run()`) actually correct?**
  _`RAGPipeline` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `HybridRetriever` (e.g. with `main()` and `main()`) actually correct?**
  _`HybridRetriever` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `Settings` (e.g. with `main()` and `main()`) actually correct?**
  _`Settings` has 48 INFERRED edges - model-reasoned connections that need verification._