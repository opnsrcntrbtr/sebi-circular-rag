# Graph Report - SEBI circular RAG  (2026-09-16)

## Corpus Check
- 255 files · ~246,876 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 275 file(s) not represented in the graph (top: .trec 138, .jsonl 66, .tsv 46)

## Summary
- 3525 nodes · 7217 edges · 211 communities (171 shown, 40 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 711 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `470b53ed`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- build_regulatory_index
- test_chunk_quality_metric.py
- .build
- generate.py
- telemetry_engine.py
- test_golden_v7_gate.py
- app.py
- Frame
- test_context_headers.py
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
- load_circulars
- reranker_interaction_check.py
- test_golden_v7_gemini.py
- test_golden_v7_local.py
- _row
- ingest_pdf.py
- main
- extract_misses.py
- benchmark.py
- test_finetune_holdout.py
- test_finetune_synthesize_queries.py
- export_datasets.py
- mine_structural_pairs.py
- gemini_adjudicate.py
- test_label_tier.py
- test_finetune_roundtrip_filter.py
- backfill_escalations.py
- local_adjudicate.py
- test_ingest_pdf.py
- agreement.py
- MeasureResult
- test_selective_citations.py
- hierarchical_chunk
- test_rerank_set_encoder.py
- test_rerank_jina_v3.py
- test_golden_v7_pool.py
- Path
- test_eval_harness_v7.py
- scrape_regulations.py
- draft_expansion_rows.py
- reg_lineage.py
- publish_hf.py
- SpladeIndex
- test_lineage.py
- sebi_rag/verify_master.py
- validate_golden
- sebi_rag/eval_asof.py
- test_reg_lineage.py
- test_scrape_sebi.py
- test_measure.py
- consolidation_edges
- audit_label_provenance.py
- mine_hard_negatives
- _bootstrap_ci
- test_hyde.py
- build_default_pipeline
- test_export_integration.py
- discover_new.py
- _provision_agree
- validate_golden_v7
- filter_targeted_rows
- demote_superseded
- test_scrape_regulations.py
- Lineage
- validate
- corpus_spaces.py
- measure.py
- test_expand.py
- bench_rerankers.py
- measure_supersession_precision
- clopper_pearson_ci
- _strip_context_header
- test_eval_generator.py
- test_ingest_refs.py
- Qwen3MLXReranker
- _FakeResponse
- cohen_kappa
- test_acquire_missing.py
- sha256_dir
- test_push_datasets.py
- test_repair_corpus_text.py
- stats.py
- test_audit_reg_edges.py
- test_bench_retrieval_artifacts.py
- derive_floors
- Handler
- remap_doc_ids.py
- hybrid_gate_sweep.py
- test_golden_v7_resolver.py
- paired_delta
- audit_reg_edges.py
- adjudicate_draft.py
- parse_reply
- .test_mean_reproduces_the_archived_aggregate
- .load
- test_app_asof.py
- rrf_fuse
- trace_failure.py
- normalize_circular_number
- validate_corpus.py
- test_build_reg_edges.py
- test_canary_generator.py
- main
- measure_mrr
- phase_judge
- corpus_integrity.py
- regression_detector.py
- doc_ids_deduped
- test_injection.py
- main
- run_judge
- canary.sh
- _resolve_governing_spans
- main
- test_context_recall.py
- _strip_thinking
- run.sh
- ce_query_reform_probe.py
- main
- test_golden_v7_agreement.py
- measure_parsing_latency
- measure_retrieval_recall
- seed_v7.py
- refresh.sh
- build_eval_rows
- measure_temporal_accuracy
- test_benchmark.py
- Chunk
- test_build_index_out_dir.py
- _FakeDenseIndex
- test_synthesize_stratum_never_reads_a_model_emitted_type_field
- segment.py
- lineage_anomaly.py
- scrape_sebi.py
- test_deploy_space.py
- autoresearch.sh
- Master Circular for Mutual Funds (2026)
- test_every_derived_floor_is_emitted_by_the_eval_report
- sebi-rag
- floors_ok
- validate_golden.py
- acquire_missing_pdfs.py
- build_report
- SEBI Master Circular for Mutual Funds (2020)
- detect_relations_ex
- stack_matches
- TestRegistry
- gwet_ac1
- SEBI Master Circular for LODR Compliance
- Master Circular for Alternative Investment Funds (AIFs) (2026)
- SEBI Circular on IRRA Platform
- stack_from_settings
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
- relabel_repooled.py
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
- test_integration_e2e.py
- main
- .encode
- measure_context_precision
- derive_thresholds.py

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
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_governing_on_cycle_safe()` --uses--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_governing_on_parallel_branches_max_date_wins()` --uses--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py
- `_chunk()` --uses--> `Chunk`  [INFERRED]
  tests/test_hyde.py → src/sebi_rag/segment.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **SEBI Regulatory Consolidation Pattern** — sebi_ho_imd_df2_cir_p_2020_156, eval_golden_v7_annotations_packet_human_packet_ho_19_34_11_6_2025_afd_pod1_i_12928_2026, eval_golden_v7_annotations_packet_human_packet_sebi_ho_ddhs_pod_2_p_cir_2025_99 [EXTRACTED 0.90]
- **Mutual Fund Offsite Inspection Reporting** — sebi_ho_imd_imd_pod_1_p_cir_2025_38, ho_24_13_11_1_2026_imd_pod_1_i_7602_2026, sebi_mutual_funds_regulations_2026 [EXTRACTED 0.95]
- **Angel Fund Regulatory Framework** — sebi_ho_afd_afd_pod_1_p_cir_2025_128, sebi_ho_afd_afd_pod_1_p_cir_2025_136, ho_19_34_11_6_2025_afd_pod1_i_12928_2026 [EXTRACTED 1.00]

## Communities (211 total, 40 thin omitted)

### Community 0 - "build_regulatory_index"
Cohesion: 0.29
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 1 - "test_chunk_quality_metric.py"
Cohesion: 0.08
Nodes (52): _body(), compute_rates(), is_interleaved_split(), is_orphan_fragment(), is_shredded_row_stub(), main(), Path, Chunk-quality-metric detector (2026-09-15). Preregistration:… (+44 more)

### Community 2 - ".build"
Cohesion: 0.07
Nodes (29): DenseIndex, _doc_checksum(), ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached embedding rows…, Deterministic per-document checksum over its (enriched) chunk texts — captures…, FAISS IndexFlatIP over L2-normalized vectors (cosine)., BM25 lexical index (bm25s). (+21 more)

### Community 3 - "generate.py"
Cohesion: 0.07
Nodes (40): Ground truth: what do the 4 CE_MISMATCH rows actually DO in production? The…, Preregistered cohort measurement for the CE paraphrase rescue. Spec:…, What does the 0.05 cross-encoder score floor actually catch?…, Capture-once margin sweep for B' selective citations. One pipeline pass over…, log(), Margin sweep for B' selective citations on the golden_v7 adjudicated set. One…, run(), Pool-width sweep (intervention #3): answer-level rescue rate vs reranker… (+32 more)

### Community 4 - "telemetry_engine.py"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 5 - "test_golden_v7_gate.py"
Cohesion: 0.22
Nodes (15): Path, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,…, select_golden(), _gate_file(), Offline tests for the golden-v7 CI gate flip (spec 2026-07-23 sec 8). The gate…, eval_json.py has no main() and boots real MPS models at import, so it cannot be…, A corrupt gate file must not arm the gate, and must not crash CI either - fall…, test_armed_gate_selects_v7() (+7 more)

### Community 6 - "app.py"
Cohesion: 0.05
Nodes (52): _append_message(), _blank_previews(), _build_citations_markdown(), build_ui(), _certainty_badge(), _cycle_messages_until_done(), _empty_citations_md(), _faithfulness_badge() (+44 more)

### Community 7 - "Frame"
Cohesion: 0.07
Nodes (43): RuntimeError, load_runs(), main(), Path, Assign epochs to the archived runs and write the epoch registry. Every run's…, _fmt(), guard_pair(), main() (+35 more)

### Community 8 - "test_context_headers.py"
Cohesion: 0.17
Nodes (11): apply_context_headers(), HeaderGenerator, Insert each chunk's header as a line below its breadcrumb line. Pure and id-…, _chunk(), Contextual chunk headers (iv9): one lay+statutory sentence per deep chunk.…, test_describe_cleans_markdown_and_newlines(), test_describe_error_or_empty_returns_empty(), test_describe_prompt_contains_inputs_and_constraints() (+3 more)

### Community 9 - "test_paraphrase_rescue.py"
Cohesion: 0.10
Nodes (36): is_degenerate(), Re-score `pool` with a rewritten query when `reranked` is below `floor`.…, Fixed rewrite, for tests and for replaying a preregistered rewrite., True when `rewritten` is unusable and the rescue should be abandoned.…, rescue_pool(), StaticQueryRewriter, _chunk(), _EchoGenerator (+28 more)

### Community 10 - "test_ui.py"
Cohesion: 0.05
Nodes (14): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., Every yielded tuple — loading, streaming chunks, final — must match the output…, Regression guard for the zip-misalignment class of bug (app.py:389): a…, _validate_api_url runs inside submit_query_stream's try block — a ValueError…, _Resp, test_submit_query_all_yields_share_arity(), test_submit_query_malformed_as_of_short_circuits(), _boom() (+6 more)

### Community 11 - "test_api.py"
Cohesion: 0.06
Nodes (38): BaseModel, FastAPI, integration, _citation_meta(), CitationMeta, create_app(), get_chunk_text(), health() (+30 more)

### Community 12 - "HybridRetriever"
Cohesion: 0.09
Nodes (43): main(), Phase 1 (systematic-debugging) evidence gathering for the 2026-09-03…, main(), main(), main(), ADR-004 adoption: calibrate abstain_threshold for jina-reranker-v3-mlx's score…, main(), _load_items() (+35 more)

### Community 13 - "test_finetune_train_lora.py"
Cohesion: 0.09
Nodes (38): apply_lora(), build_dataset(), check_trainable_ratio(), find_latest_checkpoint(), load_pairs(), main(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-… (+30 more)

### Community 14 - "test_regulations.py"
Cohesion: 0.06
Nodes (43): _alias_keys(), _jaccard(), load_regulations(), name_tokens(), Path, Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6). Regulations…, Candidate alias lookup keys, most literal first. Both the raw normalised form…, Resolve a cited regulation name+year to a canonical reg_id. Returns (reg_id,… (+35 more)

### Community 15 - "test_attribution.py"
Cohesion: 0.07
Nodes (31): entailment_index(), NLIAttributionScorer, Index of the entailment class in a model's label map. Read from the checkpoint…, Scores each context by P(entailment) of the answer given that context.…, Wrap an already-constructed cross-encoder (also the test seam)., pick_device(), Device + precision selection for Apple-Silicon inference. Centralizes the…, Resolve the compute device. A truthy explicit `pref` ("mps"/"cpu"/"cuda") wins.… (+23 more)

### Community 16 - "RAGPipeline"
Cohesion: 0.09
Nodes (50): Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)…, smoke_pipeline(), smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable…, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., RAGPipeline (+42 more)

### Community 17 - "test_finetune_eval_phase0.py"
Cohesion: 0.10
Nodes (36): compare(), group_stats(), gate_verdict(), main(), _mean(), parse_run_doc(), Path, Phase A eval (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-… (+28 more)

### Community 18 - "test_spaces.py"
Cohesion: 0.08
Nodes (23): ExternalSpaceGenerator, HFGenerator, HybridGenerator, External Space first; on ANY failure fall back to the local CPU model.…, Primary generator: calls a public LLM Space via gradio_client. Wired to…, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus). Never…, SpacesSettings (+15 more)

### Community 19 - "test_golden_v7_packet.py"
Cohesion: 0.06
Nodes (56): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+48 more)

### Community 20 - "test_conformal.py"
Cohesion: 0.10
Nodes (32): _control_summary(), main(), phase_calibrate(), phase_generate(), phase_report(), R7 conformal abstention calibration: generate -> calibrate -> report phases.…, Current production behaviour, exactly as shipped -- no LOO recalibration, the…, Re-simulates each row's abstention decision under the CALIBRATED thresholds,… (+24 more)

### Community 21 - "extract_citations"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 22 - "answer_with_abstention"
Cohesion: 0.08
Nodes (40): Answer, answer_with_abstention(), _abstain(), parse_excerpt_choice(), parse_yes_no(), True iff the reply names a valid excerpt number. 'none' or anything unparseable…, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the gate…, As-of exclusion or supersession demotion, applied to a reranked list. Extracted… (+32 more)

### Community 23 - "test_dataset_cards.py"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 24 - "derive_validity"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation. Locked…, Validity of one circular from the tiered edge list (any scope: the function…, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

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
Cohesion: 0.14
Nodes (28): is_master(), main(), Is the eval set measuring retrieval, or measuring its own construction? Read-…, main(), R3 §3.1 — mine cross-reference (A cites B) candidate pairs. Spec:…, _as_bool(), _get(), Path (+20 more)

### Community 29 - "_is_non_sebi_domain"
Cohesion: 0.10
Nodes (29): _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain. Case-…, The non-SEBI domain filter must match words, not substrings. Shipped 2026-07-30…, Any single-token keyword <= 5 chars is a substring hazard. Embedding it inside…, Query mentioning both SEBI and RBI should NOT abstain — SEBI intent wins., Empty query should not trigger the non-SEBI filter., FEMA keyword in a SEBI context should NOT abstain — SEBI intent wins., The exact query that exposed the bug. (+21 more)

### Community 30 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 31 - "test_trecio.py"
Cohesion: 0.05
Nodes (69): Rankings, _assert_fixed_tail(), convert_run_dir(), main(), Path, Back-convert archived runfiles into standards-compliant TREC artifacts. The…, Trailing field of the first line; also the whitespace precondition check., read_trec_run assumes qid and tag carry no whitespace. Verify per line. (+61 more)

### Community 32 - "load_circulars"
Cohesion: 0.13
Nodes (31): load_circulars(), Path, Path, corpus.load_circulars edge-case coverage. load_circulars reads a JSONL corpus…, Provided optional fields are passed through to CircularMeta., Multiple records produce multiple chunks., Blank lines between records are silently skipped., Malformed JSON raises ValueError (json.loads default). (+23 more)

### Community 33 - "reranker_interaction_check.py"
Cohesion: 0.15
Nodes (24): _unique(), main(), parse_args(), Namespace, Compare query-expansion arms (current prod / no-expand / HyDE) on a golden set.…, run_arm(), fmt(), mean_or_none() (+16 more)

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
Cohesion: 0.10
Nodes (24): Pattern, main(), Dry-run audit of every circular_number renumber.py would change, with the…, Re-derive circular number + dates from each record's stored text and rewrite…, _header(), _iso_date(), _labeled_date(), parse_meta() (+16 more)

### Community 38 - "main"
Cohesion: 0.22
Nodes (8): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, in_scope(), load_headers(), Path, Spec scope: depth>=3 numbered sub-clauses plus annex-family headings., test_load_headers_missing_file_returns_empty(), test_scope_predicate()

### Community 39 - "extract_misses.py"
Cohesion: 0.16
Nodes (19): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any… (+11 more)

### Community 40 - "benchmark.py"
Cohesion: 0.14
Nodes (33): cited_docs(), metrics(), evaluate(), beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), chunks_by_doc() (+25 more)

### Community 41 - "test_finetune_holdout.py"
Cohesion: 0.14
Nodes (24): build(), classify_rows(), gold_circulars(), main(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-…, Every distinct circular any golden_v7 row cites as relevant, sorted for…, Deterministic seeded sample. round(), not int(), so 159*0.30=47.7 lands on 48… (+16 more)

### Community 43 - "export_datasets.py"
Cohesion: 0.12
Nodes (22): build_aikosh_pack(), build_chunk_rows(), build_corpus_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows(), build_zenodo_pack(), _compute_stats() (+14 more)

### Community 44 - "mine_structural_pairs.py"
Cohesion: 0.10
Nodes (36): build_citation_pairs(), build_supersession_pairs(), _format_family(), Pure transform: corpus + lineage -> labeled circular pairs. label is…, Pure transform: corpus text -> citation-normalization rows. Mines in-body…, load_chunks_by_doc(), load_corpus_records(), load_minable_docs() (+28 more)

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
Cohesion: 0.16
Nodes (22): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+14 more)

### Community 49 - "local_adjudicate.py"
Cohesion: 0.12
Nodes (23): Transient-failure predicate for the real Gemini call: rate limiting (429) and…, Rerun-safety for votes.jsonl itself (plan Task 10 decision #7): drops every…, Same per-row deterministic shuffle as make_packet.py's write_packet:…, _replace_annotator_votes(), _should_retry(), _shuffled_candidates(), _current_model(), _extract_text() (+15 more)

### Community 50 - "test_ingest_pdf.py"
Cohesion: 0.17
Nodes (12): _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash…, The mirror of the kerning case above. When the en-dash has spaces on BOTH sides…, 2011-era master circulars use "SEBI/<DEPT>/MC No.<n>/<serial>/<year>", matching…, Old-format PDFs (e.g. CIR/MRD/DP/ 11 /2012) split the number with a space…, test_ingest_extracts_metadata_and_lineage(), test_parse_meta_handles_2011_mc_number_format() (+4 more)

### Community 51 - "agreement.py"
Cohesion: 0.15
Nodes (20): _claude_accuracy_ci(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation…, rid -> annotator -> expected_literal. Kept separate from `_votes_by_row` so…, As `_stratum_kappas`, grouped by label provenance tier rather than task_type.… (+12 more)

### Community 52 - "MeasureResult"
Cohesion: 0.39
Nodes (3): MeasureReport, MeasureResult, TestDataClasses

### Community 53 - "test_selective_citations.py"
Cohesion: 0.05
Nodes (63): _aggregate(), eligible(), main(), _measure(), phase_generate(), phase_report(), B' citation-scorer cohort measurement: control (bge, pointwise) vs J1 (jina,…, Answerable, non-as_of, with gold citations. Matches warrant_scorer_cohort.py's… (+55 more)

### Community 54 - "hierarchical_chunk"
Cohesion: 0.16
Nodes (23): hierarchical_chunk(), flush(), Document -> section -> paragraph chunks with stable IDs. A "section" is…, _body(), Chunker (segment.hierarchical_chunk) behaviour. Regression guard for the "5.…, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_absorption_respects_300_char_cap(), test_bare_parent_heading_folds_into_first_subsection() (+15 more)

### Community 55 - "test_rerank_set_encoder.py"
Cohesion: 0.11
Nodes (16): webis/set-encoder-base via lightning-ir, wrapped to this project's Reranker…, Score candidates with lightning-ir's CrossEncoderModule.score. Mirrors…, SetEncoderReranker, _chunk(), _FakeOutput, _FakeScores, _FakeSetEncoderModule, Offline tests for the webis/set-encoder-base wrapper (2026-08-26 Set-Encoder… (+8 more)

### Community 56 - "test_rerank_jina_v3.py"
Cohesion: 0.14
Nodes (17): ADR-004: the single decision for which model orders the RETRIEVAL pool…, retrieval_reranker_for(), _chunk(), _FakeJinaBackend, Offline tests for the jina-reranker-v3-mlx wrapper (ADR-004) — translation…, Same bug, same fix, second script: eval_asof.py also builds its own RAGPipeline…, Stands in for the vendor's MLXReranker.rerank() — same return shape (list of…, Bypass __init__ (no snapshot_download / mlx / network). (+9 more)

### Community 57 - "test_golden_v7_pool.py"
Cohesion: 0.21
Nodes (12): assemble_pool(), record(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, One gold doc with `n` chunks that ALL contain the word "broker", so a…, Regression (2026-07-25): a must_contain literal matching many gold-doc chunks…, _retriever(), _saturating_retriever() (+4 more)

### Community 58 - "Path"
Cohesion: 0.22
Nodes (21): _config_entry(), _emit(), export_all(), export_chunks(), export_citation_normalization(), export_corpus(), export_eval(), export_lineage() (+13 more)

### Community 59 - "test_eval_harness_v7.py"
Cohesion: 0.25
Nodes (16): _aggregate(), EvalReport, _mean(), report_dict(), run_eval(), test_eval_harness_metric_suite(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-… (+8 more)

### Community 60 - "scrape_regulations.py"
Cohesion: 0.23
Nodes (12): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY).…, (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'. Takes the LAST bracket group…, _record() (+4 more)

### Community 61 - "draft_expansion_rows.py"
Cohesion: 0.20
Nodes (17): build_body_paraphrase_prompt(), build_far_negative_prompt(), build_hard_negative_prompt(), build_lineage_supersession_prompt(), build_multi_hop_prompt(), build_numeric_table_prompt(), build_repealed_basis_prompt(), build_title_direct_prompt() (+9 more)

### Community 62 - "reg_lineage.py"
Cohesion: 0.19
Nodes (11): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl(), _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus. (+3 more)

### Community 63 - "publish_hf.py"
Cohesion: 0.17
Nodes (19): export_golden_v7_arrow(), log(), main(), Path, Run export_datasets.py then add golden_v7 Arrow config., Upload dist/datasets/ to HF dataset repo., Run make index to rebuild FAISS+BM25 before upload., Publish SEBI RAG artifacts to Hugging Face. Covers three repos in one… (+11 more)

### Community 64 - "SpladeIndex"
Cohesion: 0.06
Nodes (29): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.…, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+21 more)

### Community 65 - "test_lineage.py"
Cohesion: 0.14
Nodes (17): annotate_corpus(), Update each corpus record's supersession_status + superseded_by + supersedes…, _lin_chain(), P2 lineage / supersession resolution tests., test_annotate_corpus_adds_master_fields_and_consolidates_edges(), test_annotate_corpus_writes_new_metadata_fields(), test_build_lineage_edges_tiered(), test_build_lineage_inferred_master_topic_edge() (+9 more)

### Community 66 - "sebi_rag/verify_master.py"
Cohesion: 0.19
Nodes (20): diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13). Pure functions only:…, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows., render_markdown() (+12 more)

### Community 67 - "validate_golden"
Cohesion: 0.12
Nodes (16): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.…, validate_golden(), Ten chunks of one circular must not crowd the cutoff: the k applies to unique…, Answerable-but-unjudged rows are excluded from metrics, never scored 0.…, A real, fully-populated golden row, so the fixture cannot drift out of sync… (+8 more)

### Community 68 - "sebi_rag/eval_asof.py"
Cohesion: 0.20
Nodes (16): AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Aggregate case results with an exact confidence interval. Pure function of the…, run_pipeline_cases(), run_selector_cases(), summarize() (+8 more)

### Community 69 - "test_reg_lineage.py"
Cohesion: 0.12
Nodes (33): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+25 more)

### Community 70 - "test_scrape_sebi.py"
Cohesion: 0.13
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 71 - "test_measure.py"
Cohesion: 0.28
Nodes (5): main(), metrics_to_markdown(), Format results as a markdown table., Unit tests for sebi_rag.measure — automated metric collection., TestCLI

### Community 72 - "consolidation_edges"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans…, _master(), test_annotate_idempotent() (+7 more)

### Community 73 - "audit_label_provenance.py"
Cohesion: 0.21
Nodes (15): audit(), collect_artifacts(), _ids_from_csv(), _ids_from_dir(), _ids_from_jsonl(), main(), Path, Report what the annotation artifacts can account for, before classifying.… (+7 more)

### Community 74 - "mine_hard_negatives"
Cohesion: 0.24
Nodes (16): mine_hard_negatives(), One batched embed + one batched FAISS search for the whole set - not a per-…, _FakeChunk, _FakeEmbedder, _FakeRetriever, mine_hard_negatives only uses embed() to build the FAISS query vectors now (no…, Backward-compat: every mine_structural_pairs.py template has positive ==…, Phase 1's multi_hop rows: source_doc is the CITING document, but the positive… (+8 more)

### Community 75 - "_bootstrap_ci"
Cohesion: 0.15
Nodes (10): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Path, Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict. (+2 more)

### Community 76 - "test_hyde.py"
Cohesion: 0.17
Nodes (10): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —…, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_output_truncated_to_max_chars() (+2 more)

### Community 77 - "build_default_pipeline"
Cohesion: 0.09
Nodes (22): main(), SPIKE/GATE (throwaway, not preregistered) — R5's own precondition from the…, main(), What actually makes a context window large: chunk size, or chunk count? Read-…, main(), P0 prep: price a larger MLX generator before committing to the R0 upgrade.…, rss_gb(), build_screen() (+14 more)

### Community 78 - "test_export_integration.py"
Cohesion: 0.12
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 80 - "_provision_agree"
Cohesion: 0.20
Nodes (10): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using the…, Does this external vote confirm claude's label, at PROVISION level? Amendment…, Different chunk copies of the same quoted provision agree at provision level…, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction(), test_provision_agree_disjoint_without_pool_is_false() (+2 more)

### Community 81 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 82 - "filter_targeted_rows"
Cohesion: 0.29
Nodes (6): filter_targeted_rows(), Keep only sidecar rows whose chunk belongs to a target document., Selection of targeted headers (iv10): filter iv9's reused headers down to 3…, test_filter_keeps_only_target_doc_rows(), test_filter_with_no_matches_returns_empty(), test_sup04_override_generated_via_injected_callable()

### Community 83 - "demote_superseded"
Cohesion: 0.27
Nodes (15): contexts_for(), demote_superseded(), Down-weight reranked (chunk, score) pairs from superseded circulars and re-…, OLD_E superseded by an explicit clause; OLD_I only by a title heuristic., Backward compatibility: the default reproduces current behaviour exactly., An explicit clause anywhere outranks a heuristic edge — evidence wins., _score(), test_circular_with_both_edge_kinds_uses_the_explicit_penalty() (+7 more)

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
Cohesion: 0.31
Nodes (7): mrr(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), Automated metric collection for the SEBI Circular RAG pipeline. Six on-demand…, Run all (or specified) metrics sequentially., run_all_metrics(), test_retrieval_metrics()

### Community 89 - "test_expand.py"
Cohesion: 0.17
Nodes (17): expand_query(), Append statutory synonyms for lay tokens present in `query`. Deterministic and…, _chunk(), Query-side lexical expansion (intervention #2, glossary variant).…, test_all_five_sparse_failure_queries_expand(), test_expand_sparse_off_routes_raw_query_to_sparse_leg(), test_expanded_sparse_query_hits_statutory_chunk(), test_lay_term_gains_statutory_synonym() (+9 more)

### Community 90 - "bench_rerankers.py"
Cohesion: 0.38
Nodes (6): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,…

### Community 91 - "measure_supersession_precision"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 92 - "clopper_pearson_ci"
Cohesion: 0.24
Nodes (4): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 93 - "_strip_context_header"
Cohesion: 0.22
Nodes (9): Every chunk's text is `"{doc_id} | {subject[:120]} | {section}\\n{body}"` -…, _strip_context_header(), build_text_to_doc_map(), Reverse lookup for rows predating the positive_doc field. Header- stripped to…, Guards against accidentally stripping a citation to a DIFFERENT circular that…, test_strip_context_header_is_noop_for_a_different_docs_header(), test_strip_context_header_is_noop_when_first_line_is_not_the_header(), test_strip_context_header_removes_doc_id_subject_section_prefix() (+1 more)

### Community 94 - "test_eval_generator.py"
Cohesion: 0.17
Nodes (10): The eval stack's generator choice must be one shared decision.…, Uses an injected loader so the test stays offline., Silently falling back to the stub would derive floors under semantics the…, Must assert the factory is CALLED, not merely imported. Verified 2026-08-12 by…, A factory both call is not enough - they must pass the same setting, or the…, test_both_eval_scripts_read_the_same_setting(), test_eval_scripts_use_the_shared_factory(), test_mlx_kind_builds_the_production_generator() (+2 more)

### Community 95 - "test_ingest_refs.py"
Cohesion: 0.22
Nodes (6): parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_fulltext_fallback_returns_earliest_body_reference(), test_parse_meta_dept_order_document_end_to_end(), test_parse_meta_excludes_prefix_variant_self_reference(), test_primary_number_format_matrix()

### Community 96 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 97 - "_FakeResponse"
Cohesion: 0.21
Nodes (11): _FakeResponse, _ok_payload(), Security-relevant: base_url is CLI-configurable here (unlike…, test_call_omlx_never_reads_anthropic_auth_token(), _fake_post(), test_call_omlx_no_token_sends_no_auth_header(), _fake_post(), test_call_omlx_retries_on_5xx() (+3 more)

### Community 98 - "cohen_kappa"
Cohesion: 0.33
Nodes (6): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw element is…, test_cohen_kappa_both_constant_and_identical_is_one(), test_cohen_kappa_empty_input_is_one(), test_cohen_kappa_identical_lists_is_one(), test_cohen_kappa_independent_looking_lists_is_low()

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
Cohesion: 0.25
Nodes (3): Repair the 6 records whose body text was overwritten with one shared circular's…, The repair map must name a real orphan PDF that parses to the circular_number…, test_numbers_normalize_distinctly()

### Community 103 - "stats.py"
Cohesion: 0.18
Nodes (8): bootstrap_ci(), BootstrapCI, ProportionCI, Uncertainty quantification for benchmark runs. The golden set is n=56…, Percentile bootstrap interval for the mean of per-query scores., Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests)., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 104 - "test_audit_reg_edges.py"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 105 - "test_bench_retrieval_artifacts.py"
Cohesion: 0.15
Nodes (9): bench_retrieval must emit valid TREC alongside the legacy runfile., run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so every…, iv9/iv10 build a headered index beside data/index. Without an index override…, ADR-004: benchmarking jina-reranker-v3-mlx against the production cross-encoder…, 2026-08-26 Set-Encoder spec: benchmarking webis/set-encoder-base (via…, test_bench_retrieval_can_bench_an_alternate_index(), test_bench_retrieval_can_measure_the_reranked_order(), test_bench_retrieval_exposes_and_records_the_reranker_choice() (+1 more)

### Community 106 - "derive_floors"
Cohesion: 0.15
Nodes (13): derive_floors(), metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, test_gate_floors_context_recall(), The floor is a bootstrap lower bound minus a cushion, never the mean. Gating on…, A metric nobody scored must not be floored at 0 - a 0 floor is not a gate, it…, B' gates citation_precision alongside recall/recall_tradeoff/abstention. The…, recall_at_k is ceiling-limited (baseline 0.956 leaves ~9 failing queries of…, test_citation_precision_is_gated_after_B_prime() (+5 more)

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
Cohesion: 0.19
Nodes (7): paired_delta(), PairedResult, Compare run `b` against run `a` on their shared queries. Returns mean_b -…, True when the randomization test rejects at 1 - confidence AND the paired…, Randomization p-values use the (count+1)/(n+1) estimator, so a p-value of…, One query flipping out of 56 is exactly the iv9-style verdict: the…, TestPairedDelta

### Community 112 - "audit_reg_edges.py"
Cohesion: 0.27
Nodes (9): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+1 more)

### Community 113 - "adjudicate_draft.py"
Cohesion: 0.29
Nodes (10): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+2 more)

### Community 114 - "parse_reply"
Cohesion: 0.18
Nodes (11): parse_reply(), Full parse result including the parse_error flag cached per row. letters=[] is…, Public letter-choice-protocol parser: (chosen letters, expected literal).…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply…, test_parse_reply_empty_letters_dispatches_to_yes_no_protocol(), test_parse_reply_garbage_is_unparseable(), test_parse_reply_letters_and_expected() (+3 more)

### Community 115 - ".test_mean_reproduces_the_archived_aggregate"
Cohesion: 0.24
Nodes (7): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), write_trec_run(), test_trec_run_and_research_judges_are_sidecar_only(), The archived runfiles embed section headings in the doc id., End-to-end guarantee behind the re-scoring script: replaying a runfile yields…, TestReadTrecRun

### Community 117 - "test_app_asof.py"
Cohesion: 0.20
Nodes (6): app_module(), _expected_output_count(), fixture, As-of date plumbing in the Spaces UI (app.py)., 8 fixed fields + 2 per preview accordion + 4 meta badges. Matches the flat list…, test_run_query_yield_arity_matches_outputs_list_pipeline_free_paths()

### Community 118 - "rrf_fuse"
Cohesion: 0.50
Nodes (3): Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 119 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 120 - "normalize_circular_number"
Cohesion: 0.27
Nodes (13): main(), _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number(), _ocr_text(), Path (+5 more)

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

### Community 126 - "phase_judge"
Cohesion: 0.36
Nodes (9): _aggregate(), eligible(), main(), _measure(), phase_generate(), phase_judge(), phase_report(), R1 §4/§6 cohort measurement: control (cross-encoder) vs W1 (warrant judge).… (+1 more)

### Community 127 - "corpus_integrity.py"
Cohesion: 0.31
Nodes (8): check_meta_fields(), load_chunks(), load_corpus(), main(), Corpus integrity checker — verify chunks.jsonl matches corpus JSONL. Checks: 1.…, Load corpus into a dict keyed by circular_number., Load chunks and return (records, doc_ids)., Check that chunk meta has expected CircularMeta fields.

### Community 128 - "regression_detector.py"
Cohesion: 0.31
Nodes (8): extract_metrics(), load_floors(), load_latest_runs(), main(), Eval regression detector — flag when metrics drop below gate floors. Checks: 1.…, Load floors from gate_v7.json., Load most recent eval runs sorted by timestamp., Extract metric values from a run.

### Community 130 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 131 - "main"
Cohesion: 0.43
Nodes (6): aggregate(), eligible(), main(), measure(), Preregistered cohort measurement for supersession confidence tiering. Spec:…, Answerable, non-as_of, with gold citations: the rows citation metrics exist for.

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
Cohesion: 0.46
Nodes (7): _chunk(), The gate must measure the context window, not just the fusion list.…, An abstention still had a context window; measuring retrieval delivery must not…, _reranked(), test_answer_records_the_context_ids_it_used(), test_context_ids_populated_even_when_abstaining(), test_context_ids_respect_top_k()

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

### Community 141 - "test_golden_v7_agreement.py"
Cohesion: 0.26
Nodes (11): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions` (keyed by…, Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):…, _same_provision_fixture(), test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only(), test_apply_queue_decision_leaves_row_untouched() (+3 more)

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

### Community 149 - "test_benchmark.py"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

### Community 150 - "Chunk"
Cohesion: 0.04
Nodes (49): NLI attribution scoring for B' citation selection. B' asks "does this context…, _softmax(), Generator, _grounded_prompt(), Judge, _judge_prompt(), _judge_prompt_identify(), MLXGenerator (+41 more)

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
Cohesion: 0.08
Nodes (24): Contextual chunk headers (iv9): one lay+statutory sentence per chunk. Index-…, faithfulness(), Check that every circular id the answer cites (in square brackets) was actually…, _is_table_row_candidate(), _is_table_row_filler(), _is_toc_row_candidate(), _merge_table_rows(), is_candidate() (+16 more)

### Community 155 - "lineage_anomaly.py"
Cohesion: 0.47
Nodes (5): load_corpus(), load_lineage(), main(), Lineage anomaly detector — flag circulars with missing supersession edges.…, Load corpus keyed by circular_number.

### Community 156 - "scrape_sebi.py"
Cohesion: 0.26
Nodes (14): discover(), fetch(), _listing_url(), main(), _page(), _parse_date(), parse_rows(), pdf_url_for() (+6 more)

### Community 157 - "test_deploy_space.py"
Cohesion: 0.14
Nodes (9): _FakeRuntime, scripts/deploy_space.py: post-upload runtime read-back. Covers the…, Once the runtime's sha matches what was just pushed, a genuine BUILD_ERROR for…, The exact race this guards against: get_space_runtime called right after…, test_matching_sha_build_error_still_warns(), get_space_runtime(), test_runtime_read_back_failure_is_swallowed(), test_stale_runtime_sha_suppresses_warning() (+1 more)

### Community 158 - "autoresearch.sh"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 159 - "Master Circular for Mutual Funds (2026)"
Cohesion: 0.40
Nodes (5): Master Circular for Mutual Funds (2026), Circular on Development of Passive Funds, Extension of timelines for submission of offsite inspection data (Mutual Funds), SEBI (Mutual Funds) Regulations, 1996, SEBI (Mutual Funds) Regulations, 2026

### Community 162 - "floors_ok"
Cohesion: 0.17
Nodes (12): floors_ok(), True iff every floor's metric is present in `report_gate` and meets it. Missing…, Demotion or reranking can empty the context window while the fusion list is…, test_context_recall_floor_catches_a_regression_fusion_recall_misses(), derive_floors emits gate-report metric names, not the internal score_row names…, A floor naming a metric the report does not carry cannot be shown to hold, so…, test_floor_names_match_the_gate_report_keys(), test_floors_not_ok_when_one_metric_is_below() (+4 more)

### Community 163 - "validate_golden.py"
Cohesion: 0.60
Nodes (4): check_gate(), check_golden_set(), main(), Pre-commit validator for golden_v7 gate. Checks: 1. gate_v7.json exists and is…

### Community 164 - "acquire_missing_pdfs.py"
Cohesion: 0.20
Nodes (13): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+5 more)

### Community 165 - "build_report"
Cohesion: 0.31
Nodes (10): build_report(), Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid measurement;…, The headline number must be the 10 pipeline cases alone — the whole point of…, _results(), test_pipeline_metrics_are_not_polluted_by_selector_cases(), test_pooled_overall_carries_no_interval() (+2 more)

### Community 166 - "SEBI Master Circular for Mutual Funds (2020)"
Cohesion: 0.50
Nodes (4): SEBI Circular on Options Eligibility (2024), SEBI Master Circular for Mutual Funds (2020), SEBI Circular HO/24/13/12(4)2025-IMD-POD-1/I/2062/2026, SEBI Master Circular for Mutual Funds (2026)

### Community 167 - "detect_relations_ex"
Cohesion: 0.20
Nodes (10): detect_relations(), detect_relations_ex(), Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window(), A circular that names another circular BEFORE the supersede trigger word must…, test_detect_relations_delegates_unchanged(), test_detect_relations_ex_evidence_and_extractor() (+2 more)

### Community 168 - "stack_matches"
Cohesion: 0.31
Nodes (9): Names of axes where `gate`'s recorded stack differs from `live`'s current one -…, stack_matches(), bge-derived floor vs. jina-running production is the expected steady state, not…, Every gate_v7.json that exists today (including the currently-armed one) has no…, _stack(), test_stack_matches_ignores_production_reranker_model_difference(), test_stack_matches_reports_mismatched_axis_name(), test_stack_matches_returns_empty_when_all_axes_match() (+1 more)

### Community 170 - "gwet_ac1"
Cohesion: 0.29
Nodes (7): gwet_ac1(), Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a prevalence-…, The kappa base-rate paradox: one label dominates, raw agreement is high, yet…, test_gwet_ac1_both_constant_and_identical_is_one(), test_gwet_ac1_empty_input_is_one(), test_gwet_ac1_exceeds_kappa_on_skewed_high_agreement(), test_gwet_ac1_identical_lists_is_one()

### Community 171 - "SEBI Master Circular for LODR Compliance"
Cohesion: 0.67
Nodes (3): SEBI Master Circular for LODR Compliance, SEBI Operational Circular for Non-convertible Securities (2022), SEBI Master Circular for RTAs (2023)

### Community 172 - "Master Circular for Alternative Investment Funds (AIFs) (2026)"
Cohesion: 1.00
Nodes (3): Master Circular for Alternative Investment Funds (AIFs) (2026), Revised regulatory framework for Angel Funds, Relaxation in timeline for disclosure of allocation methodology by Angel Funds

### Community 173 - "SEBI Circular on IRRA Platform"
Cohesion: 0.67
Nodes (3): Investor Risk Reduction Access (IRRA), SEBI Circular on IRRA Platform, Master Circular for Stock Brokers (2025)

### Community 174 - "stack_from_settings"
Cohesion: 0.33
Nodes (7): Keys must match gate_select._STACK_AXES exactly, or stack_matches() silently…, stack_from_settings(), A stack block whose keys don't exactly match _STACK_AXES would make…, derivation_reranker is a constant (never read from config); production_…, _settings(), test_stack_from_settings_records_but_does_not_compare_reranker_split(), test_stack_from_settings_uses_exact_stack_matches_axis_names()

### Community 176 - "deploy_space.py"
Cohesion: 0.38
Nodes (6): _hardware_warning(), main(), Create/update the Gradio-SDK Hugging Face Space for the CPU demo and push…, Return a warning string if the just-deployed Space looks unhealthy, else None.…, Read back the Space's runtime after a deploy and print what CI was previously…, _report_runtime()

### Community 186 - "relabel_repooled.py"
Cohesion: 0.43
Nodes (6): _body(), main(), _norm(), pick(), Label the 7 rows re-pooled after the assemble_pool fix (2026-07-25 remediation…, (candidate, quote) pairs for this row: the answer_contains carrier first, then…

### Community 207 - "test_integration_e2e.py"
Cohesion: 0.33
Nodes (4): _ollama_up(), pipeline(), fixture, Step 12 — end-to-end RAG integration test with the REAL stack. bge-m3 (MPS) +…

### Community 208 - "main"
Cohesion: 0.50
Nodes (3): eligible(), main(), SPIKE — throwaway, not preregistered. Answers one question before any R6 design…

### Community 212 - "measure_context_precision"
Cohesion: 0.50
Nodes (3): measure_context_precision(), Fraction of top-k chunks from relevant circulars. Unlike recall@k (which is…, TestContextPrecision

### Community 221 - "derive_thresholds.py"
Cohesion: 0.18
Nodes (10): Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, Which golden set gates CI, and whether its adjudicated subset clears the…, One scoring path shared by `eval_json.py` (which measures) and…, Score one golden row through the production-shaped pipeline. Returns per-row…, Per-row records -> metric -> score vector, skipping rows where the metric was…, score_row(), vectors(), test_vectors_exposes_context_recall() (+2 more)

## Knowledge Gaps
- **59 isolated node(s):** `checks.sh script`, `measure.sh script`, `autoresearch.sh script`, `PYTHONPATH`, `TOKENIZERS_PARALLELISM` (+54 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1289 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **40 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `.build`, `generate.py`, `test_injection.py`, `test_context_headers.py`, `test_paraphrase_rescue.py`, `test_context_recall.py`, `main`, `HybridRetriever`, `test_attribution.py`, `RAGPipeline`, `test_spaces.py`, `test_benchmark.py`, `answer_with_abstention`, `segment.py`, `test_spaces_app.py`, `load_circulars`, `benchmark.py`, `test_selective_citations.py`, `hierarchical_chunk`, `test_rerank_set_encoder.py`, `test_rerank_jina_v3.py`, `SpladeIndex`, `test_lineage.py`, `test_hyde.py`, `validate_golden_v7`, `demote_superseded`, `corpus_spaces.py`, `test_expand.py`, `Qwen3MLXReranker`, `rrf_fuse`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Why does `load_golden()` connect `HybridRetriever` to `main`, `run_judge`, `generate.py`, `main`, `Frame`, `main`, `seed_v7.py`, `test_finetune_eval_phase0.py`, `test_golden_v7_packet.py`, `test_conformal.py`, `benchmark.py`, `test_finetune_holdout.py`, `gemini_adjudicate.py`, `backfill_escalations.py`, `local_adjudicate.py`, `agreement.py`, `test_selective_citations.py`, `relabel_repooled.py`, `test_eval_harness_v7.py`, `test_measure.py`, `build_default_pipeline`, `main`, `remap_doc_ids.py`, `hybrid_gate_sweep.py`, `adjudicate_draft.py`, `phase_judge`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `generate.py`, `test_paraphrase_rescue.py`, `test_api.py`, `HybridRetriever`, `measure_parsing_latency`, `measure_retrieval_recall`, `measure_temporal_accuracy`, `answer_with_abstention`, `Chunk`, `benchmark.py`, `test_eval_harness_v7.py`, `sebi_rag/eval_asof.py`, `build_default_pipeline`, `test_integration_e2e.py`, `measure_context_precision`, `Lineage`, `measure.py`, `measure_supersession_precision`, `hybrid_gate_sweep.py`, `measure_mrr`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 71 inferred relationships involving `Chunk` (e.g. with `dataset_quality()` and `load_index_chunks()`) actually correct?**
  _`Chunk` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `main()`) actually correct?**
  _`RAGPipeline` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `HybridRetriever` (e.g. with `main()` and `main()`) actually correct?**
  _`HybridRetriever` has 49 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `Settings` (e.g. with `main()` and `main()`) actually correct?**
  _`Settings` has 50 INFERRED edges - model-reasoned connections that need verification._