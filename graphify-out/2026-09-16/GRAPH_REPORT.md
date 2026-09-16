# Graph Report - SEBI circular RAG  (2026-09-16)

## Corpus Check
- 254 files · ~245,960 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 275 file(s) not represented in the graph (top: .trec 138, .jsonl 66, .tsv 46)

## Summary
- 3505 nodes · 7194 edges · 202 communities (163 shown, 39 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 711 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e14b2027`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Chunk
- test_chunk_quality_metric.py
- .build
- generate.py
- telemetry_engine.py
- test_golden_v7_gate.py
- app.py
- Frame
- context_headers.py
- test_paraphrase_rescue.py
- test_ui.py
- test_api.py
- HybridRetriever
- test_finetune_train_lora.py
- test_regulations.py
- test_attribution.py
- RAGPipeline
- test_finetune_eval_phase0.py
- test_spaces.py
- test_golden_v7_packet.py
- test_conformal.py
- extract_citations
- answer_with_abstention
- test_dataset_cards.py
- derive_validity
- test_finetune_mine_structural.py
- test_spaces_app.py
- ui.py
- Settings
- _is_non_sebi_domain
- test_export_datasets.py
- test_trecio.py
- test_corpus.py
- reranker_interaction_check.py
- test_golden_v7_gemini.py
- test_golden_v7_local.py
- _row
- ingest_pdf.py
- Embedder
- extract_misses.py
- benchmark.py
- test_finetune_holdout.py
- test_finetune_synthesize_queries.py
- export_datasets.py
- _strip_context_header
- gemini_adjudicate.py
- test_label_tier.py
- test_finetune_roundtrip_filter.py
- backfill_escalations.py
- local_adjudicate.py
- parse_meta
- agreement.py
- WarrantJudge
- test_selective_citations.py
- hierarchical_chunk
- test_rerank_set_encoder.py
- test_rerank_jina_v3.py
- test_golden_v7_pool.py
- Path
- eval_harness.py
- scrape_regulations.py
- draft_expansion_rows.py
- build_reg_edges.py
- publish_hf.py
- test_splade_leg.py
- _chunk
- sebi_rag/verify_master.py
- validate_golden
- sebi_rag/eval_asof.py
- test_reg_lineage.py
- test_scrape_sebi.py
- MeasureResult
- JinaMLXReranker
- audit_label_provenance.py
- mine_hard_negatives
- _bootstrap_ci
- main
- api.py
- test_export_integration.py
- settings.py
- _provision_agree
- validate_golden_v7
- test_pipeline.py
- test_lineage.py
- test_scrape_regulations.py
- Lineage
- validate
- corpus_spaces.py
- measure.py
- retrieve.py
- bench_rerankers.py
- measure_supersession_precision
- clopper_pearson_ci
- mine_structural_pairs.py
- test_eval_generator.py
- test_ingest_refs.py
- Qwen3MLXReranker
- _FakeResponse
- test_golden_v7_agreement.py
- test_acquire_missing.py
- sha256_dir
- test_push_datasets.py
- test_repair_corpus_text.py
- bootstrap_ci
- test_audit_reg_edges.py
- test_bench_retrieval_artifacts.py
- test_select_citations_routes_through_the_warrant_backend
- Handler
- remap_doc_ids.py
- hybrid_gate_sweep.py
- test_golden_v7_resolver.py
- paired_delta
- audit_reg_edges.py
- adjudicate_draft.py
- parse_reply
- read_trec_run
- stats.py
- test_app_asof.py
- _alias_keys
- trace_failure.py
- warrant_scorer
- validate_corpus.py
- test_build_reg_edges.py
- test_canary_generator.py
- main
- measure_mrr
- warrant_scorer_cohort.py
- corpus_integrity.py
- regression_detector.py
- sweep_rrf_k.py
- test_injection.py
- _doc
- run_judge
- canary.sh
- _resolve_governing_spans
- main
- test_context_recall.py
- _strip_thinking
- run.sh
- ce_query_reform_probe.py
- main
- apply
- measure_parsing_latency
- measure_retrieval_recall
- seed_v7.py
- refresh.sh
- build_eval_rows
- measure_temporal_accuracy
- .query
- test_benchmark.py
- SetEncoderReranker
- test_build_index_out_dir.py
- _FakeDenseIndex
- test_synthesize_stratum_never_reads_a_model_emitted_type_field
- segment.py
- lineage_anomaly.py
- scrape_sebi.py
- main
- autoresearch.sh
- Master Circular for Mutual Funds (2026)
- test_annotation_adds_no_circular_meta_field
- test_every_alias_target_is_in_force_or_has_a_succession_entry
- test_settings_citation_scorer_enabled_true
- validate_golden.py
- resolve_stems
- .rerank
- SEBI Master Circular for Mutual Funds (2020)
- sebi-rag
- test_settings_citation_scorer_enabled_false
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
- notify.sh
- start_phoenix.sh
- SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026
- SEBI Master Circular for Stock Brokers (2018)
- sebi_rag/autoresearch/__init__.py
- conftest.py
- test_numeric_table_candidates_excludes_boilerplate_trailing_chunk
- test_has_boilerplate_detects_signature_anywhere_not_just_at_start
- test_synthesize_stratum_uses_cache_when_present
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

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 118 edges
2. `RAGPipeline` - 64 edges
3. `HybridRetriever` - 59 edges
4. `hierarchical_chunk()` - 56 edges
5. `Settings` - 56 edges
6. `HashEmbedder` - 48 edges
7. `ExtractiveStubGenerator` - 48 edges
8. `load_golden()` - 43 edges
9. `build_lineage()` - 41 edges
10. `BGEM3Embedder` - 37 edges

## Surprising Connections (you probably didn't know these)
- `test_vectors_exposes_context_recall()` --calls--> `vectors()`  [INFERRED]
  tests/test_context_recall.py → scripts/golden_v7/score.py
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_governing_on_cycle_safe()` --uses--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_governing_on_parallel_branches_max_date_wins()` --uses--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **SEBI Regulatory Consolidation Pattern** — sebi_ho_imd_df2_cir_p_2020_156, eval_golden_v7_annotations_packet_human_packet_ho_19_34_11_6_2025_afd_pod1_i_12928_2026, eval_golden_v7_annotations_packet_human_packet_sebi_ho_ddhs_pod_2_p_cir_2025_99 [EXTRACTED 0.90]
- **Mutual Fund Offsite Inspection Reporting** — sebi_ho_imd_imd_pod_1_p_cir_2025_38, ho_24_13_11_1_2026_imd_pod_1_i_7602_2026, sebi_mutual_funds_regulations_2026 [EXTRACTED 0.95]
- **Angel Fund Regulatory Framework** — sebi_ho_afd_afd_pod_1_p_cir_2025_128, sebi_ho_afd_afd_pod_1_p_cir_2025_136, ho_19_34_11_6_2025_afd_pod1_i_12928_2026 [EXTRACTED 1.00]

## Communities (202 total, 39 thin omitted)

### Community 0 - "Chunk"
Cohesion: 0.06
Nodes (26): Generator, Judge, MLXGenerator, OllamaGenerator, Protocol, ADOPTED gate (eval_gate round 3): deterministic groundedness signal — max…, Max cosine(query, doc subject line) over contexts — the primary gate signal,…, Max cosine(query, section heading) over contexts — the second tier. (+18 more)

### Community 1 - "test_chunk_quality_metric.py"
Cohesion: 0.08
Nodes (52): _body(), compute_rates(), is_interleaved_split(), is_orphan_fragment(), is_shredded_row_stub(), main(), Path, Chunk-quality-metric detector (2026-09-15). Preregistration:… (+44 more)

### Community 2 - ".build"
Cohesion: 0.12
Nodes (18): BM25 lexical index (bm25s)., SparseIndex, _chunk(), test_expand_sparse_off_routes_raw_query_to_sparse_leg(), test_retrieve_dense_leg_keeps_raw_query(), test_retrieve_routes_expanded_query_to_sparse_leg(), spy(), _chunks() (+10 more)

### Community 3 - "generate.py"
Cohesion: 0.08
Nodes (28): Ground truth: what do the 4 CE_MISMATCH rows actually DO in production? The…, Preregistered cohort measurement for the CE paraphrase rescue. Spec:…, What does the 0.05 cross-encoder score floor actually catch?…, Capture-once margin sweep for B' selective citations. One pipeline pass over…, Benchmark MLX generators on the golden set: faithfulness, groundedness,…, CLI for automated metric collection via sebi_rag.measure. Usage: python…, Retrieval-only benchmark with TREC runfile and reproducibility metadata. Use…, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped… (+20 more)

### Community 4 - "telemetry_engine.py"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 5 - "test_golden_v7_gate.py"
Cohesion: 0.05
Nodes (59): derive_floors(), metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the…, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,…, Names of axes where `gate`'s recorded stack differs from `live`'s current one -…, True iff every floor's metric is present in `report_gate` and meets it. Missing… (+51 more)

### Community 6 - "app.py"
Cohesion: 0.05
Nodes (52): _append_message(), _blank_previews(), _build_citations_markdown(), build_ui(), _certainty_badge(), _cycle_messages_until_done(), _empty_citations_md(), _faithfulness_badge() (+44 more)

### Community 7 - "Frame"
Cohesion: 0.07
Nodes (43): RuntimeError, load_runs(), main(), Path, Assign epochs to the archived runs and write the epoch registry. Every run's…, _fmt(), guard_pair(), main() (+35 more)

### Community 8 - "context_headers.py"
Cohesion: 0.08
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 9 - "test_paraphrase_rescue.py"
Cohesion: 0.09
Nodes (37): is_degenerate(), Paraphrase rescue for the cross-encoder score floor. Preregistered in…, Re-score `pool` with a rewritten query when `reranked` is below `floor`.…, Fixed rewrite, for tests and for replaying a preregistered rewrite., True when `rewritten` is unusable and the rescue should be abandoned.…, rescue_pool(), StaticQueryRewriter, _chunk() (+29 more)

### Community 10 - "test_ui.py"
Cohesion: 0.05
Nodes (14): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., Every yielded tuple — loading, streaming chunks, final — must match the output…, Regression guard for the zip-misalignment class of bug (app.py:389): a…, _validate_api_url runs inside submit_query_stream's try block — a ValueError…, _Resp, test_submit_query_all_yields_share_arity(), test_submit_query_malformed_as_of_short_circuits(), _boom() (+6 more)

### Community 11 - "test_api.py"
Cohesion: 0.08
Nodes (17): integration, _citation_meta(), Truncate chunk text for a response payload; append an ellipsis if cut., Build one CitationMeta per unique circular (first-seen chunk wins).…, _truncate_preview(), _CannedGenerator, FastAPI service tests (offline pipelines): endpoints, auth, rate limit,…, Regression guard for the zip-misalignment class of bug: with two chunks cited… (+9 more)

### Community 12 - "HybridRetriever"
Cohesion: 0.09
Nodes (44): main(), SPIKE/GATE (throwaway, not preregistered) — R5's own precondition from the…, main(), Phase 1 (systematic-debugging) evidence gathering for the 2026-09-03…, main(), main(), main(), What actually makes a context window large: chunk size, or chunk count? Read-… (+36 more)

### Community 13 - "test_finetune_train_lora.py"
Cohesion: 0.09
Nodes (38): apply_lora(), build_dataset(), check_trainable_ratio(), find_latest_checkpoint(), load_pairs(), main(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-… (+30 more)

### Community 14 - "test_regulations.py"
Cohesion: 0.07
Nodes (41): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus., derive_regulatory_basis(), _jaccard(), load_regulations(), name_tokens(), Path (+33 more)

### Community 15 - "test_attribution.py"
Cohesion: 0.07
Nodes (33): entailment_index(), NLIAttributionScorer, NLI attribution scoring for B' citation selection. B' asks "does this context…, Index of the entailment class in a model's label map. Read from the checkpoint…, Scores each context by P(entailment) of the answer given that context.…, Wrap an already-constructed cross-encoder (also the test seam)., _softmax(), pick_device() (+25 more)

### Community 16 - "RAGPipeline"
Cohesion: 0.11
Nodes (44): Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)…, smoke_pipeline(), smoke_pipeline(), run_retrieval_benchmark(), load_circulars(), Path, HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable… (+36 more)

### Community 17 - "test_finetune_eval_phase0.py"
Cohesion: 0.10
Nodes (36): compare(), group_stats(), gate_verdict(), main(), _mean(), parse_run_doc(), Path, Phase A eval (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-… (+28 more)

### Community 18 - "test_spaces.py"
Cohesion: 0.08
Nodes (26): _grounded_prompt(), F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and the…, ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo. All classes implement…, External Space first; on ANY failure fall back to the local CPU model.…, Primary generator: calls a public LLM Space via gradio_client. Wired to… (+18 more)

### Community 19 - "test_golden_v7_packet.py"
Cohesion: 0.06
Nodes (59): Random, build_screen(), T-Screen: does the generator follow the citation instruction at all? Spec:…, 50 rows stratified proportionally to golden_v7's eight strata., _apportion(), ingest_packet(), _ingest_to_votes(), main() (+51 more)

### Community 20 - "test_conformal.py"
Cohesion: 0.10
Nodes (32): _control_summary(), main(), phase_calibrate(), phase_generate(), phase_report(), R7 conformal abstention calibration: generate -> calibrate -> report phases.…, Current production behaviour, exactly as shipped -- no LOO recalibration, the…, Re-simulates each row's abstention decision under the CALIBRATED thresholds,… (+24 more)

### Community 21 - "extract_citations"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 22 - "answer_with_abstention"
Cohesion: 0.11
Nodes (33): Answer, answer_with_abstention(), _abstain(), _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons,…, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful() (+25 more)

### Community 23 - "test_dataset_cards.py"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 24 - "derive_validity"
Cohesion: 0.07
Nodes (28): annotate_corpus(), Update each corpus record's supersession_status + superseded_by + supersedes…, annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans… (+20 more)

### Community 25 - "test_finetune_mine_structural.py"
Cohesion: 0.10
Nodes (31): _is_signoff_boilerplate(), _leaks_metadata(), mine_citation_context(), mine_heading_section(), mine_subject_body(), First line matching the numbered-clause pattern -> (heading, rest). None if no…, _split_heading(), Offline tests for scripts/finetune/mine_structural_pairs.py's pure transforms.… (+23 more)

### Community 26 - "test_spaces_app.py"
Cohesion: 0.06
Nodes (6): app_module(), fixture, HF Spaces demo (root app.py): citations table + preview accordion logic. Fully…, app.py does `import spaces` (ZeroGPU) at module scope; stub it., _stub_spaces_package(), test_get_chunk_text_builds_once_and_caches()

### Community 27 - "ui.py"
Cohesion: 0.11
Nodes (30): _append_message(), _blank_previews(), _build_citations_markdown(), build_ui(), _certainty_badge(), _cycle_messages_until_done(), _empty_citations_md(), _faithfulness_badge() (+22 more)

### Community 28 - "Settings"
Cohesion: 0.10
Nodes (33): eligible(), main(), SPIKE — throwaway, not preregistered. Answers one question before any R6 design…, is_master(), main(), Is the eval set measuring retrieval, or measuring its own construction? Read-…, main(), P0 prep: price a larger MLX generator before committing to the R0 upgrade.… (+25 more)

### Community 29 - "_is_non_sebi_domain"
Cohesion: 0.10
Nodes (29): _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain. Case-…, The non-SEBI domain filter must match words, not substrings. Shipped 2026-07-30…, Any single-token keyword <= 5 chars is a substring hazard. Embedding it inside…, Query mentioning both SEBI and RBI should NOT abstain — SEBI intent wins., Empty query should not trigger the non-SEBI filter., FEMA keyword in a SEBI context should NOT abstain — SEBI intent wins., The exact query that exposed the bug. (+21 more)

### Community 30 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 31 - "test_trecio.py"
Cohesion: 0.06
Nodes (63): Rankings, _assert_fixed_tail(), convert_run_dir(), main(), Path, Back-convert archived runfiles into standards-compliant TREC artifacts. The…, Trailing field of the first line; also the whitespace precondition check., read_trec_run assumes qid and tag carry no whitespace. Verify per line. (+55 more)

### Community 32 - "test_corpus.py"
Cohesion: 0.13
Nodes (28): Path, corpus.load_circulars edge-case coverage. load_circulars reads a JSONL corpus…, Provided optional fields are passed through to CircularMeta., Multiple records produce multiple chunks., Blank lines between records are silently skipped., Malformed JSON raises ValueError (json.loads default)., load_circulars accepts both str and Path., load_circulars accepts a pathlib.Path. (+20 more)

### Community 33 - "reranker_interaction_check.py"
Cohesion: 0.17
Nodes (22): _unique(), main(), parse_args(), Namespace, Compare query-expansion arms (current prod / no-expand / HyDE) on a golden set.…, run_arm(), fmt(), mean_or_none() (+14 more)

### Community 34 - "test_golden_v7_gemini.py"
Cohesion: 0.15
Nodes (26): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct from a well-…, A Gemini reply that disputes an abstain row (says YES, it IS answerable) writes… (+18 more)

### Community 35 - "test_golden_v7_local.py"
Cohesion: 0.13
Nodes (23): _FakeResponse, _ok_payload(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external…, oMLX's skip_api_key_verification is on: an unset token is not an error, it just…, Five pilot rows from five strata measure more than five from one - the gemini…, Vote records must say annotator "qwen" (never reuse "gemini" - the agreement…, Back-compat guard: the gemini leg (on hold, not removed) must keep producing… (+15 more)

### Community 36 - "_row"
Cohesion: 0.12
Nodes (27): decide(), Spec sec7 promotion rules for one row. `votes_by_annotator` is this row's votes…, Abstain rows have no explicit claude vote at all (Task 8 never judged them) -…, Both externals independently think something DOES govern (disputing the…, The LLM leg is whichever single non-claude/non-human annotator voted - "qwen"…, Amendment 2026-07-26 (user-approved): the promotion unit is the PROVISION, not…, External marked claude's chunk governing plus extras: claude's label is…, The abstain protocol can never emit non-empty governing (no letters are… (+19 more)

### Community 37 - "ingest_pdf.py"
Cohesion: 0.15
Nodes (19): Re-derive circular number + dates from each record's stored text and rewrite…, _existing_numbers(), extract_text(), ingest(), main(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars. Drop a circular PDF into data/raw/ and… (+11 more)

### Community 38 - "Embedder"
Cohesion: 0.09
Nodes (21): Embedder, ndarray, Protocol, _tokens(), DenseIndex, _doc_checksum(), _embedder_identity(), ndarray (+13 more)

### Community 39 - "extract_misses.py"
Cohesion: 0.16
Nodes (19): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any… (+11 more)

### Community 40 - "benchmark.py"
Cohesion: 0.17
Nodes (27): beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), chunks_by_doc(), dir_fingerprint(), enrich_golden_item(), export_beir() (+19 more)

### Community 41 - "test_finetune_holdout.py"
Cohesion: 0.14
Nodes (24): build(), classify_rows(), gold_circulars(), main(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-…, Every distinct circular any golden_v7 row cites as relevant, sorted for…, Deterministic seeded sample. round(), not int(), so 159*0.30=47.7 lands on 48… (+16 more)

### Community 43 - "export_datasets.py"
Cohesion: 0.12
Nodes (22): build_aikosh_pack(), build_chunk_rows(), build_corpus_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows(), build_zenodo_pack(), _compute_stats() (+14 more)

### Community 44 - "_strip_context_header"
Cohesion: 0.22
Nodes (9): Every chunk's text is `"{doc_id} | {subject[:120]} | {section}\\n{body}"` -…, _strip_context_header(), build_text_to_doc_map(), Reverse lookup for rows predating the positive_doc field. Header- stripped to…, Guards against accidentally stripping a citation to a DIFFERENT circular that…, test_strip_context_header_is_noop_for_a_different_docs_header(), test_strip_context_header_is_noop_when_first_line_is_not_the_header(), test_strip_context_header_removes_doc_id_subject_section_prefix() (+1 more)

### Community 45 - "gemini_adjudicate.py"
Cohesion: 0.12
Nodes (24): adjudicate(), _current_model(), _daily_quota_exhausted(), main(), _parse_error_ids(), _parse_letter_choice(), _parse_reply(), _parse_yes_no() (+16 more)

### Community 46 - "test_label_tier.py"
Cohesion: 0.12
Nodes (20): classify_tier(), human_reviewed_ids(), main(), Path, Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.…, Map provenance to the controlled vocabulary. `human_reviewed` (row appears in…, Row ids present in the human labelling packet., Controlled-vocabulary label_tier over golden_v7 (spec A §8.3). (+12 more)

### Community 47 - "test_finetune_roundtrip_filter.py"
Cohesion: 0.14
Nodes (26): filter_boilerplate(), load_rows(), Path, Phase 1 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-…, Prefer the row's own positive_doc field (future runs); fall back to the reverse…, Retrieves with each row's query against `retriever` (the frozen base index) and…, Returns (kept, n_dropped)., resolve_positive_doc() (+18 more)

### Community 48 - "backfill_escalations.py"
Cohesion: 0.12
Nodes (28): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+20 more)

### Community 49 - "local_adjudicate.py"
Cohesion: 0.12
Nodes (23): Transient-failure predicate for the real Gemini call: rate limiting (429) and…, Rerun-safety for votes.jsonl itself (plan Task 10 decision #7): drops every…, Same per-row deterministic shuffle as make_packet.py's write_packet:…, _replace_annotator_votes(), _should_retry(), _shuffled_candidates(), _current_model(), _extract_text() (+15 more)

### Community 50 - "parse_meta"
Cohesion: 0.15
Nodes (17): Pattern, _iso_date(), _labeled_date(), parse_meta(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash… (+9 more)

### Community 51 - "agreement.py"
Cohesion: 0.15
Nodes (21): _claude_accuracy_ci(), gwet_ac1(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation…, Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a prevalence-… (+13 more)

### Community 52 - "WarrantJudge"
Cohesion: 0.09
Nodes (18): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_warrant_scores(), parse_yes_no(), Prompt for the warrant judge: evaluate each excerpt's warrant for the answer.…, Parse warrant scores from the judge's JSON output. Returns a list of n floats… (+10 more)

### Community 53 - "test_selective_citations.py"
Cohesion: 0.14
Nodes (22): citation_scorer_for(), The single enable/disable AND backend decision for B'. Returns None when…, _FakeReranker, Tests for B' selective citations: select_citations() and its integration., The backend choice must go through the same single decision point as the enable…, Deterministic scorer: returns preset answer-relevance scores, sorted desc., The `reranker` positional is the bge instance used by backend="reranker";…, Empty context list returns empty citation list. (+14 more)

### Community 54 - "hierarchical_chunk"
Cohesion: 0.16
Nodes (23): hierarchical_chunk(), flush(), Document -> section -> paragraph chunks with stable IDs. A "section" is…, _body(), Chunker (segment.hierarchical_chunk) behaviour. Regression guard for the "5.…, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_absorption_respects_300_char_cap(), test_bare_parent_heading_folds_into_first_subsection() (+15 more)

### Community 55 - "test_rerank_set_encoder.py"
Cohesion: 0.14
Nodes (13): _chunk(), _FakeOutput, _FakeScores, _FakeSetEncoderModule, Offline tests for the webis/set-encoder-base wrapper (2026-08-26 Set-Encoder…, Stands in for the torch.Tensor `CrossEncoderModule.score(...).scores` return…, Stands in for lightning_ir.CrossEncoderModule — records the query/docs it was…, Bypass __init__ (no lightning-ir import / model download / network). (+5 more)

### Community 56 - "test_rerank_jina_v3.py"
Cohesion: 0.14
Nodes (17): ADR-004: the single decision for which model orders the RETRIEVAL pool…, retrieval_reranker_for(), _chunk(), _FakeJinaBackend, Offline tests for the jina-reranker-v3-mlx wrapper (ADR-004) — translation…, Same bug, same fix, second script: eval_asof.py also builds its own RAGPipeline…, Stands in for the vendor's MLXReranker.rerank() — same return shape (list of…, Bypass __init__ (no snapshot_download / mlx / network). (+9 more)

### Community 57 - "test_golden_v7_pool.py"
Cohesion: 0.21
Nodes (12): assemble_pool(), record(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, One gold doc with `n` chunks that ALL contain the word "broker", so a…, Regression (2026-07-25): a must_contain literal matching many gold-doc chunks…, _retriever(), _saturating_retriever() (+4 more)

### Community 58 - "Path"
Cohesion: 0.22
Nodes (21): _config_entry(), _emit(), export_all(), export_chunks(), export_citation_normalization(), export_corpus(), export_eval(), export_lineage() (+13 more)

### Community 59 - "eval_harness.py"
Cohesion: 0.26
Nodes (16): _aggregate(), EvalReport, _mean(), Golden-set evaluation harness (P1). Runs the pipeline over a labelled golden…, report_dict(), run_eval(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-… (+8 more)

### Community 60 - "scrape_regulations.py"
Cohesion: 0.21
Nodes (12): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY).…, (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'. Takes the LAST bracket group…, _record() (+4 more)

### Community 61 - "draft_expansion_rows.py"
Cohesion: 0.20
Nodes (17): build_body_paraphrase_prompt(), build_far_negative_prompt(), build_hard_negative_prompt(), build_lineage_supersession_prompt(), build_multi_hop_prompt(), build_numeric_table_prompt(), build_repealed_basis_prompt(), build_title_direct_prompt() (+9 more)

### Community 62 - "build_reg_edges.py"
Cohesion: 0.53
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl()

### Community 63 - "publish_hf.py"
Cohesion: 0.17
Nodes (19): export_golden_v7_arrow(), log(), main(), Path, Run export_datasets.py then add golden_v7 Arrow config., Upload dist/datasets/ to HF dataset repo., Run make index to rebuild FAISS+BM25 before upload., Publish SEBI RAG artifacts to Hugging Face. Covers three repos in one… (+11 more)

### Community 64 - "test_splade_leg.py"
Cohesion: 0.08
Nodes (21): Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.…, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights., splade_pool(), encode(), SPLADE learned-sparse retrieval leg (iv11). Non-destructive, opt-in third RRF… (+13 more)

### Community 65 - "_chunk"
Cohesion: 0.17
Nodes (17): Context ids the answer rests on. Scores each context via `scorer`, keeps those…, select_citations(), _chunk(), Looser margin (0.45) keeps more contexts than tight margin (0.35)., When citation scorer is None, all contexts are cited (legacy behavior)., Measured 2026-08-12: on 206 rows where retrieval found every relevant doc, B'…, Default must not change the pure function's contract; the wider operating point…, test_always_keeps_at_least_one_when_all_below_margin() (+9 more)

### Community 66 - "sebi_rag/verify_master.py"
Cohesion: 0.19
Nodes (20): diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13). Pure functions only:…, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows., render_markdown() (+12 more)

### Community 67 - "validate_golden"
Cohesion: 0.12
Nodes (16): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.…, validate_golden(), Ten chunks of one circular must not crowd the cutoff: the k applies to unique…, Answerable-but-unjudged rows are excluded from metrics, never scored 0.…, A real, fully-populated golden row, so the fixture cannot drift out of sync… (+8 more)

### Community 68 - "sebi_rag/eval_asof.py"
Cohesion: 0.13
Nodes (26): AsofCaseResult, build_report(), load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Aggregate case results with an exact confidence interval. Pure function of the…, run_pipeline_cases() (+18 more)

### Community 69 - "test_reg_lineage.py"
Cohesion: 0.11
Nodes (38): annotate_regulation_fields(), build_regulation_edges(), build_regulatory_index(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs() (+30 more)

### Community 70 - "test_scrape_sebi.py"
Cohesion: 0.13
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 71 - "MeasureResult"
Cohesion: 0.13
Nodes (12): main(), metrics_to_markdown(), Format results as a markdown table., MeasureReport, MeasureResult, Run all (or specified) metrics sequentially., run_all_metrics(), Unit tests for sebi_rag.measure — automated metric collection. (+4 more)

### Community 72 - "JinaMLXReranker"
Cohesion: 0.22
Nodes (10): _aggregate(), eligible(), main(), _measure(), phase_generate(), phase_report(), B' citation-scorer cohort measurement: control (bge, pointwise) vs J1 (jina,…, Answerable, non-as_of, with gold citations. Matches warrant_scorer_cohort.py's… (+2 more)

### Community 73 - "audit_label_provenance.py"
Cohesion: 0.21
Nodes (15): audit(), collect_artifacts(), _ids_from_csv(), _ids_from_dir(), _ids_from_jsonl(), main(), Path, Report what the annotation artifacts can account for, before classifying.… (+7 more)

### Community 74 - "mine_hard_negatives"
Cohesion: 0.24
Nodes (16): mine_hard_negatives(), One batched embed + one batched FAISS search for the whole set - not a per-…, _FakeChunk, _FakeEmbedder, _FakeRetriever, mine_hard_negatives only uses embed() to build the FAISS query vectors now (no…, Backward-compat: every mine_structural_pairs.py template has positive ==…, Phase 1's multi_hop rows: source_doc is the CITING document, but the positive… (+8 more)

### Community 75 - "_bootstrap_ci"
Cohesion: 0.15
Nodes (10): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Path, Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict. (+2 more)

### Community 76 - "main"
Cohesion: 0.07
Nodes (20): main(), main(), main(), HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, csr_matrix, SpladeEncoder, csr_matrix (+12 more)

### Community 77 - "api.py"
Cohesion: 0.08
Nodes (30): BaseModel, FastAPI, CitationMeta, _compute_kwargs(), create_app(), get_chunk_text(), health(), pipe() (+22 more)

### Community 78 - "test_export_integration.py"
Cohesion: 0.12
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 79 - "settings.py"
Cohesion: 0.11
Nodes (17): log(), Margin sweep for B' selective citations on the golden_v7 adjudicated set. One…, run(), CE_MISMATCH false-abstention investigation (score-floor-diagnostic 2026-08-18).…, Emit one JSON line listing SEBI circulars newer than previously seen. Uses a…, Emit one JSON line of retrieval/citation/abstention metrics using the persisted…, Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, Keys must match gate_select._STACK_AXES exactly, or stack_matches() silently… (+9 more)

### Community 80 - "_provision_agree"
Cohesion: 0.20
Nodes (10): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using the…, Does this external vote confirm claude's label, at PROVISION level? Amendment…, Different chunk copies of the same quoted provision agree at provision level…, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction(), test_provision_agree_disjoint_without_pool_is_false() (+2 more)

### Community 81 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 82 - "test_pipeline.py"
Cohesion: 0.12
Nodes (14): _ollama_up(), Step 12 — end-to-end RAG integration test with the REAL stack. bge-m3 (MPS) +…, _build_chunks(), Minimal end-to-end test of the SEBI RAG pipeline. Runs fully offline…, Current behaviour: the heuristic edge demotes OLD below NEW., With tiering on, an unevidenced supersession no longer demotes., test_abstention_on_out_of_domain_query(), test_hybrid_retrieval_finds_relevant_circular() (+6 more)

### Community 83 - "test_lineage.py"
Cohesion: 0.09
Nodes (37): contexts_for(), demote_superseded(), detect_relations(), detect_relations_ex(), Down-weight reranked (chunk, score) pairs from superseded circulars and re-…, Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window() (+29 more)

### Community 85 - "Lineage"
Cohesion: 0.22
Nodes (7): Lineage, Path, Connected component over supersedes/superseded_by (both tiers)., The circular in this family that governs on date as_of (ISO), or None when…, test_lineage_load_old_file_defaults_empty_edges(), test_lineage_save_load_roundtrip(), test_lineage_save_load_roundtrips_edges()

### Community 86 - "validate"
Cohesion: 0.33
Nodes (14): validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the document's own…, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations(), test_duplicate_text_across_records_flagged(), test_empty_text_is_not_a_duplicate_cluster(), test_flags_bad_issue_date() (+6 more)

### Community 87 - "corpus_spaces.py"
Cohesion: 0.29
Nodes (10): _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path). Loads the…, One HF dataset config as plain dicts (network; cached by `datasets`)., Full-circular records (dicts) for build_lineage() — always the "corpus" config… (+2 more)

### Community 88 - "measure.py"
Cohesion: 0.26
Nodes (12): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), Automated metric collection for the SEBI Circular RAG pipeline. Six on-demand…, test_retrieval_metrics(), _internal(), Prove the internal retrieval metrics are the standard ones. Skips unless the… (+4 more)

### Community 89 - "retrieve.py"
Cohesion: 0.11
Nodes (21): _load_items(), Path, Pool-width sweep (intervention #3): answer-level rescue rate vs reranker…, Score-floor false-abstention diagnostics (hybrid-gate-prereg 2026-08-13, §10b).…, expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and…, Stage-1 hybrid retrieval: dense (FAISS) + sparse (BM25) fused by RRF. Mandatory… (+13 more)

### Community 90 - "bench_rerankers.py"
Cohesion: 0.22
Nodes (8): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,…, Calibrate top_k and the abstention threshold against the citation-precision…, SEBI Circular RAG — local-first, Apple Silicon. Pipeline: ingest -> segment ->…

### Community 91 - "measure_supersession_precision"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 92 - "clopper_pearson_ci"
Cohesion: 0.22
Nodes (5): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, test_render_report_includes_ac1_and_provision(), The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 93 - "mine_structural_pairs.py"
Cohesion: 0.10
Nodes (36): build_citation_pairs(), build_supersession_pairs(), _format_family(), Pure transform: corpus + lineage -> labeled circular pairs. label is…, Pure transform: corpus text -> citation-normalization rows. Mines in-body…, load_chunks_by_doc(), load_corpus_records(), load_minable_docs() (+28 more)

### Community 94 - "test_eval_generator.py"
Cohesion: 0.18
Nodes (9): The eval stack's generator choice must be one shared decision.…, Uses an injected loader so the test stays offline., Silently falling back to the stub would derive floors under semantics the…, Must assert the factory is CALLED, not merely imported. Verified 2026-08-12 by…, A factory both call is not enough - they must pass the same setting, or the…, test_both_eval_scripts_read_the_same_setting(), test_eval_scripts_use_the_shared_factory(), test_mlx_kind_builds_the_production_generator() (+1 more)

### Community 95 - "test_ingest_refs.py"
Cohesion: 0.14
Nodes (12): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_dedup_uses_normalized_numbers() (+4 more)

### Community 96 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 97 - "_FakeResponse"
Cohesion: 0.21
Nodes (11): _FakeResponse, _ok_payload(), Security-relevant: base_url is CLI-configurable here (unlike…, test_call_omlx_never_reads_anthropic_auth_token(), _fake_post(), test_call_omlx_no_token_sends_no_auth_header(), _fake_post(), test_call_omlx_retries_on_5xx() (+3 more)

### Community 98 - "test_golden_v7_agreement.py"
Cohesion: 0.19
Nodes (15): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw element is…, _min_agreement_fixture(), Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):…, The kappa base-rate paradox: one label dominates, raw agreement is high, yet…, _same_provision_fixture(), test_claude_accuracy_ci_returns_exact_and_provision(), test_cohen_kappa_both_constant_and_identical_is_one() (+7 more)

### Community 99 - "test_acquire_missing.py"
Cohesion: 0.18
Nodes (3): Offline tests for the missing-PDF recovery logic (no network)., test_resolve_stems_matches_by_stem(), test_resolve_stems_survives_detail_fetch_error()

### Community 100 - "sha256_dir"
Cohesion: 0.23
Nodes (11): main(), merge(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-…, Per-file sha256 of every file in the merged model dir - the plan's "sha256 into…, CPU by design, not MPS: this is a one-shot weight merge, not a training or…, sha256_dir(), Offline tests for scripts/finetune/merge_adapter.py's pure pieces. The actual… (+3 more)

### Community 101 - "test_push_datasets.py"
Cohesion: 0.21
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default:…, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 102 - "test_repair_corpus_text.py"
Cohesion: 0.22
Nodes (4): main(), Repair the 6 records whose body text was overwritten with one shared circular's…, The repair map must name a real orphan PDF that parses to the circular_number…, test_numbers_normalize_distinctly()

### Community 103 - "bootstrap_ci"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 104 - "test_audit_reg_edges.py"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 105 - "test_bench_retrieval_artifacts.py"
Cohesion: 0.15
Nodes (9): bench_retrieval must emit valid TREC alongside the legacy runfile., run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so every…, iv9/iv10 build a headered index beside data/index. Without an index override…, ADR-004: benchmarking jina-reranker-v3-mlx against the production cross-encoder…, 2026-08-26 Set-Encoder spec: benchmarking webis/set-encoder-base (via…, test_bench_retrieval_can_bench_an_alternate_index(), test_bench_retrieval_can_measure_the_reranked_order(), test_bench_retrieval_exposes_and_records_the_reranker_choice() (+1 more)

### Community 106 - "test_select_citations_routes_through_the_warrant_backend"
Cohesion: 0.18
Nodes (8): warrant_model/warrant_shared default to None. Forwarding None explicitly would…, Omitted, not forwarded as None — warrant_scorer's own default applies., End-to-end: citation_scorer_for's warrant branch plugs into select_citations'…, test_citation_scorer_for_selects_the_warrant_backend(), _fake_warrant_scorer(), test_citation_scorer_for_warrant_max_tokens_defaults_unset(), test_citation_scorer_for_warrant_omits_unset_kwargs(), test_select_citations_routes_through_the_warrant_backend()

### Community 107 - "Handler"
Cohesion: 0.30
Nodes (5): BaseHTTPRequestHandler, Handler, Local ops HTTP server so n8n can drive the pipeline via HTTP (no Execute…, run_script(), smoketest()

### Community 108 - "remap_doc_ids.py"
Cohesion: 0.33
Nodes (10): main(), Rewrite golden_v7 doc references after the corpus renumbering (2026-07-25…, remap(), Doc-id remapping after the 2026-07-25 corpus renumbering (Task 4)., _row(), test_input_rows_are_not_mutated(), test_matching_is_normalization_insensitive(), test_remaps_must_not_cite() (+2 more)

### Community 109 - "hybrid_gate_sweep.py"
Cohesion: 0.26
Nodes (11): current_gate_passes(), hybrid_gate_passes(), main(), parse_args(), Namespace, Hybrid abstention gate sweep — preregistered analysis. Preregistration:…, Reproduces the current production subject-gate OR (no hybrid override)., True if this row never reaches the subject-gate check at all (vetoed earlier by… (+3 more)

### Community 110 - "test_golden_v7_resolver.py"
Cohesion: 0.42
Nodes (8): _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through(), test_qrels_span_rows_get_grade_2(), test_resolves_normalized_whitespace_quote(), test_unresolvable_quote_returns_empty(), test_validator_flags_unresolvable_quote_when_chunks_given()

### Community 111 - "paired_delta"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries. Returns mean_b -…, Randomization p-values use the (count+1)/(n+1) estimator, so a p-value of…, One query flipping out of 56 is exactly the iv9-style verdict: the…, TestPairedDelta

### Community 112 - "audit_reg_edges.py"
Cohesion: 0.27
Nodes (9): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+1 more)

### Community 113 - "adjudicate_draft.py"
Cohesion: 0.29
Nodes (10): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+2 more)

### Community 114 - "parse_reply"
Cohesion: 0.18
Nodes (11): parse_reply(), Full parse result including the parse_error flag cached per row. letters=[] is…, Public letter-choice-protocol parser: (chosen letters, expected literal).…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply…, test_parse_reply_empty_letters_dispatches_to_yes_no_protocol(), test_parse_reply_garbage_is_unparseable(), test_parse_reply_letters_and_expected() (+3 more)

### Community 115 - "read_trec_run"
Cohesion: 0.29
Nodes (6): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), write_trec_run(), test_trec_run_and_research_judges_are_sidecar_only(), The archived runfiles embed section headings in the doc id., TestReadTrecRun

### Community 116 - "stats.py"
Cohesion: 0.22
Nodes (6): BootstrapCI, PairedResult, ProportionCI, Uncertainty quantification for benchmark runs. The golden set is n=56…, True when the randomization test rejects at 1 - confidence AND the paired…, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 117 - "test_app_asof.py"
Cohesion: 0.20
Nodes (6): app_module(), _expected_output_count(), fixture, As-of date plumbing in the Spaces UI (app.py)., 8 fixed fields + 2 per preview accordion + 4 meta badges. Matches the flat list…, test_run_query_yield_arity_matches_outputs_list_pipeline_free_paths()

### Community 118 - "_alias_keys"
Cohesion: 0.29
Nodes (8): _alias_keys(), Candidate alias lookup keys, most literal first. Both the raw normalised form…, PMS/NCS/ILDS end in a literal S. Unconditional plural-stripping mapped them to…, reg_id resolved purely through the alias table, ignoring the corpus., A table key that no _alias_keys() output can produce is dead config., _resolved(), test_acronyms_ending_in_s_reach_their_own_entry(), test_every_alias_entry_is_reachable_from_some_spelling()

### Community 119 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 120 - "warrant_scorer"
Cohesion: 0.33
Nodes (4): Callable compatible with select_citations' scorer.rerank() signature. Wraps…, warrant_scorer(), 2026-08-23 measured WarrantJudge's max_tokens=512 default giving 38.1%…, test_warrant_scorer_forwards_max_tokens_to_the_judge()

### Community 121 - "validate_corpus.py"
Cohesion: 0.33
Nodes (6): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair. Checks (per…, Every record's text must match the PDF its provenance names. Slow (re-extracts…, validate_deep()

### Community 122 - "test_build_reg_edges.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 123 - "test_canary_generator.py"
Cohesion: 0.27
Nodes (8): _canary_jscode(), _ops_timeout(), The eval canary must fit its timeout and alert on real regressions. Measured…, n8n gives up first if its budget is smaller, so the ops timeout is never…, A threshold above the healthy value fires every run. citation_precision was…, test_alert_thresholds_sit_below_measured_baselines(), test_n8n_timeout_not_tighter_than_the_ops_budget(), test_ops_timeout_fits_the_measured_runtime()

### Community 124 - "main"
Cohesion: 0.31
Nodes (7): call(), main(), _norm(), Does answering a golden_v7 row require a circular the corpus does not hold?…, Uppercase, strip all whitespace — so 'CIR/MIRSD/5/ 2013' matches…, Returns (answer, reasoning). The judge is a reasoning model: the oMLX API…, windows()

### Community 125 - "measure_mrr"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level. For each query, RR = 1/rank of first…, TestMRR

### Community 126 - "warrant_scorer_cohort.py"
Cohesion: 0.39
Nodes (8): _aggregate(), eligible(), main(), _measure(), phase_generate(), phase_report(), R1 §4/§6 cohort measurement: control (cross-encoder) vs W1 (warrant judge).…, Answerable, non-as_of, with gold citations: the rows citation metrics exist…

### Community 127 - "corpus_integrity.py"
Cohesion: 0.31
Nodes (8): check_meta_fields(), load_chunks(), load_corpus(), main(), Corpus integrity checker — verify chunks.jsonl matches corpus JSONL. Checks: 1.…, Load corpus into a dict keyed by circular_number., Load chunks and return (records, doc_ids)., Check that chunk meta has expected CircularMeta fields.

### Community 128 - "regression_detector.py"
Cohesion: 0.31
Nodes (8): extract_metrics(), load_floors(), load_latest_runs(), main(), Eval regression detector — flag when metrics drop below gate floors. Checks: 1.…, Load floors from gate_v7.json., Load most recent eval runs sorted by timestamp., Extract metric values from a run.

### Community 129 - "sweep_rrf_k.py"
Cohesion: 0.50
Nodes (3): parse_args(), Namespace, Sweep RRF k_const values on a golden set. No index rebuild needed. Turn 1 of…

### Community 130 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 131 - "_doc"
Cohesion: 0.13
Nodes (19): doc_ids_deduped(), [(chunk_idx, score), ...] -> distinct doc_ids in rank order., aggregate(), eligible(), main(), measure(), Preregistered cohort measurement for supersession confidence tiering. Spec:…, Answerable, non-as_of, with gold citations: the rows citation metrics exist for. (+11 more)

### Community 132 - "run_judge"
Cohesion: 0.39
Nodes (7): _is_parseable(), _load_screen(), main(), R1 §3.3 degeneracy probe: does the warrant judge return a parseable reply?…, Mirrors generate.parse_warrant_scores' cleaning exactly, but reports whether…, run_answers(), run_judge()

### Community 133 - "canary.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, SEBI_RAG_EVAL_GENERATOR, canary.sh script, TOKENIZERS_PARALLELISM

### Community 134 - "_resolve_governing_spans"
Cohesion: 0.36
Nodes (8): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote} spans, looked…, _resolve_governing_spans(), _pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool(), test_resolve_governing_spans_short_body_uses_whole_body(), test_resolve_governing_spans_uses_first_60_body_chars()

### Community 135 - "main"
Cohesion: 0.43
Nodes (6): _chunk_id(), _doc(), load_pre_expansion_ids(), main(), Path, W1.3 diagnostic (2026-09-03 architecture review): does the 730->1,490 corpus…

### Community 136 - "test_context_recall.py"
Cohesion: 0.39
Nodes (8): _chunk(), The gate must measure the context window, not just the fusion list.…, An abstention still had a context window; measuring retrieval delivery must not…, _reranked(), test_answer_records_the_context_ids_it_used(), test_context_ids_populated_even_when_abstaining(), test_context_ids_respect_top_k(), test_vectors_exposes_context_recall()

### Community 137 - "_strip_thinking"
Cohesion: 0.40
Nodes (5): Qwen-family models may emit <think>...</think> reasoning as inline text,…, _strip_thinking(), Qwen-family models may emit <think>...</think> as inline text rather than as…, test_strip_thinking_leaves_plain_replies_untouched(), test_strip_thinking_removes_inline_think_tags()

### Community 138 - "run.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 139 - "ce_query_reform_probe.py"
Cohesion: 0.38
Nodes (6): main(), _pool(), Probe: does query-side reformulation lift the CE score on the 4 CE_MISMATCH…, Return (ce_top, best relevant score, chunk_id of argmax)., Top-8 pool plus every relevant chunk, de-duplicated on chunk_id., _score()

### Community 140 - "main"
Cohesion: 0.48
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

### Community 141 - "apply"
Cohesion: 0.29
Nodes (7): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions` (keyed by…, test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only(), test_apply_queue_decision_leaves_row_untouched(), test_apply_row_without_a_decision_is_never_touched()

### Community 142 - "measure_parsing_latency"
Cohesion: 0.38
Nodes (4): measure_parsing_latency(), Measure PDF ingestion throughput (chars/sec, ms/PDF). Samples 20 PDFs…, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 143 - "measure_retrieval_recall"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 144 - "seed_v7.py"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 145 - "refresh.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 147 - "measure_temporal_accuracy"
Cohesion: 0.43
Nodes (3): measure_temporal_accuracy(), Measure fraction of as_of queries returning correct pre-supersession circular…, TestTemporalAccuracy

### Community 148 - ".query"
Cohesion: 0.29
Nodes (3): _LineageAwareReranker, Reranker wrapper that re-applies lineage handling to its output. The paraphrase…, As-of exclusion or supersession demotion, applied to a reranked list. Extracted…

### Community 149 - "test_benchmark.py"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

### Community 150 - "SetEncoderReranker"
Cohesion: 0.40
Nodes (3): webis/set-encoder-base via lightning-ir, wrapped to this project's Reranker…, Score candidates with lightning-ir's CrossEncoderModule.score. Mirrors…, SetEncoderReranker

### Community 151 - "test_build_index_out_dir.py"
Cohesion: 0.29
Nodes (5): build_index must be able to target a scratch index directory. The iv9/iv10…, A --out flag that is parsed but ignored is worse than none: it reads as safe…, lineage.json lands next to the index it describes; writing it into data/index…, test_build_index_saves_to_the_resolved_out_dir_not_the_constant(), test_lineage_follows_the_out_dir()

### Community 152 - "_FakeDenseIndex"
Cohesion: 0.29
Nodes (3): _FakeDense, _FakeDenseIndex, Deterministic stand-in for faiss.IndexFlatIP.search: returns a fixed ranking…

### Community 153 - "test_synthesize_stratum_never_reads_a_model_emitted_type_field"
Cohesion: 0.29
Nodes (5): The plan's own finding: self-assigned stratum labels are unreliable. Even if…, test_synthesize_stratum_drops_leak_filtered_and_parse_failed(), test_synthesize_stratum_never_reads_a_model_emitted_type_field(), test_synthesize_stratum_stops_at_target(), _fake_call()

### Community 154 - "segment.py"
Cohesion: 0.10
Nodes (22): Build the dense+sparse index once and persist it (run after corpus changes).…, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., _is_table_row_candidate(), _is_table_row_filler(), _is_toc_row_candidate(), _merge_table_rows(), is_candidate(), _paragraphs() (+14 more)

### Community 155 - "lineage_anomaly.py"
Cohesion: 0.47
Nodes (5): load_corpus(), load_lineage(), main(), Lineage anomaly detector — flag circulars with missing supersession edges.…, Load corpus keyed by circular_number.

### Community 156 - "scrape_sebi.py"
Cohesion: 0.18
Nodes (20): check_robots(), main(), Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, Log-only re-verification that our paths are still crawlable., discover(), fetch(), _listing_url(), looks_like_pdf() (+12 more)

### Community 157 - "main"
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 158 - "autoresearch.sh"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 159 - "Master Circular for Mutual Funds (2026)"
Cohesion: 0.40
Nodes (5): Master Circular for Mutual Funds (2026), Circular on Development of Passive Funds, Extension of timelines for submission of offsite inspection data (Mutual Funds), SEBI (Mutual Funds) Regulations, 1996, SEBI (Mutual Funds) Regulations, 2026

### Community 163 - "validate_golden.py"
Cohesion: 0.60
Nodes (4): check_gate(), check_golden_set(), main(), Pre-commit validator for golden_v7 gate. Checks: 1. gate_v7.json exists and is…

### Community 164 - "resolve_stems"
Cohesion: 0.33
Nodes (7): _add_months(), month_window(), date, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps., resolve_stems(), stem_of()

### Community 166 - "SEBI Master Circular for Mutual Funds (2020)"
Cohesion: 0.50
Nodes (4): SEBI Circular on Options Eligibility (2024), SEBI Master Circular for Mutual Funds (2020), SEBI Circular HO/24/13/12(4)2025-IMD-POD-1/I/2062/2026, SEBI Master Circular for Mutual Funds (2026)

### Community 171 - "SEBI Master Circular for LODR Compliance"
Cohesion: 0.67
Nodes (3): SEBI Master Circular for LODR Compliance, SEBI Operational Circular for Non-convertible Securities (2022), SEBI Master Circular for RTAs (2023)

### Community 172 - "Master Circular for Alternative Investment Funds (AIFs) (2026)"
Cohesion: 1.00
Nodes (3): Master Circular for Alternative Investment Funds (AIFs) (2026), Revised regulatory framework for Angel Funds, Relaxation in timeline for disclosure of allocation methodology by Angel Funds

### Community 173 - "SEBI Circular on IRRA Platform"
Cohesion: 0.67
Nodes (3): Investor Risk Reduction Access (IRRA), SEBI Circular on IRRA Platform, Master Circular for Stock Brokers (2025)

## Knowledge Gaps
- **59 isolated node(s):** `checks.sh script`, `measure.sh script`, `autoresearch.sh script`, `PYTHONPATH`, `TOKENIZERS_PARALLELISM` (+54 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1279 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `.build`, `generate.py`, `test_injection.py`, `context_headers.py`, `test_paraphrase_rescue.py`, `test_context_recall.py`, `main`, `HybridRetriever`, `test_attribution.py`, `RAGPipeline`, `test_spaces.py`, `.query`, `test_benchmark.py`, `answer_with_abstention`, `SetEncoderReranker`, `segment.py`, `test_spaces_app.py`, `.rerank`, `Embedder`, `benchmark.py`, `WarrantJudge`, `hierarchical_chunk`, `test_rerank_set_encoder.py`, `test_rerank_jina_v3.py`, `test_splade_leg.py`, `_chunk`, `JinaMLXReranker`, `main`, `validate_golden_v7`, `test_lineage.py`, `corpus_spaces.py`, `retrieve.py`, `Qwen3MLXReranker`, `warrant_scorer`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `Chunk`, `_doc`, `generate.py`, `test_paraphrase_rescue.py`, `HybridRetriever`, `measure_parsing_latency`, `measure_retrieval_recall`, `measure_temporal_accuracy`, `.query`, `answer_with_abstention`, `Embedder`, `benchmark.py`, `eval_harness.py`, `sebi_rag/eval_asof.py`, `MeasureResult`, `main`, `api.py`, `settings.py`, `Lineage`, `measure.py`, `measure_supersession_precision`, `hybrid_gate_sweep.py`, `measure_mrr`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `load_golden()` connect `HybridRetriever` to `_doc`, `run_judge`, `main`, `Frame`, `main`, `seed_v7.py`, `test_finetune_eval_phase0.py`, `RAGPipeline`, `test_golden_v7_packet.py`, `test_conformal.py`, `Settings`, `benchmark.py`, `test_finetune_holdout.py`, `gemini_adjudicate.py`, `backfill_escalations.py`, `local_adjudicate.py`, `agreement.py`, `eval_harness.py`, `MeasureResult`, `JinaMLXReranker`, `main`, `remap_doc_ids.py`, `hybrid_gate_sweep.py`, `adjudicate_draft.py`, `warrant_scorer_cohort.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 71 inferred relationships involving `Chunk` (e.g. with `dataset_quality()` and `load_index_chunks()`) actually correct?**
  _`Chunk` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `main()`) actually correct?**
  _`RAGPipeline` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `HybridRetriever` (e.g. with `main()` and `main()`) actually correct?**
  _`HybridRetriever` has 49 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `Settings` (e.g. with `main()` and `main()`) actually correct?**
  _`Settings` has 50 INFERRED edges - model-reasoned connections that need verification._