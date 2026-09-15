# Graph Report - SEBI circular RAG  (2026-09-15)

## Corpus Check
- 251 files · ~243,248 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3450 nodes · 7129 edges · 196 communities (162 shown, 34 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 732 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `aea5949e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Chunk
- sebi_rag/verify_master.py
- ValueError
- eval_harness.py
- telemetry_engine.py
- test_golden_v7_gate.py
- app.py
- Frame
- test_context_headers.py
- test_paraphrase_rescue.py
- test_ui.py
- test_api.py
- load_golden
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
- scripts/verify_master.py
- load_circulars
- reranker_interaction_check.py
- test_golden_v7_gemini.py
- test_golden_v7_local.py
- _row
- ingest_pdf.py
- HybridRetriever
- extract_misses.py
- benchmark.py
- test_finetune_holdout.py
- test_finetune_synthesize_queries.py
- export_datasets.py
- synthesize_queries.py
- gemini_adjudicate.py
- test_label_tier.py
- test_finetune_roundtrip_filter.py
- backfill_escalations.py
- local_adjudicate.py
- parse_meta
- agreement.py
- generate.py
- test_selective_citations.py
- hierarchical_chunk
- test_rerank_set_encoder.py
- test_rerank_jina_v3.py
- test_golden_v7_pool.py
- Path
- mine_strata.py
- scrape_sebi.py
- draft_expansion_rows.py
- main
- publish_hf.py
- test_pipeline.py
- test_annotation_adds_no_circular_meta_field
- api.py
- validate_golden
- sebi_rag/eval_asof.py
- test_reg_lineage.py
- test_scrape_sebi.py
- MeasureResult
- SpladeIndex
- audit_label_provenance.py
- mine_hard_negatives
- _bootstrap_ci
- test_hyde.py
- consolidation_edges
- test_export_integration.py
- settings.py
- _provision_agree
- validate_golden_v7
- test_eval_harness_v7.py
- test_lineage.py
- test_scrape_regulations.py
- scrape_regulations.py
- validate
- build_spaces_pipeline
- measure.py
- test_expand.py
- _doc
- corpus.py
- clopper_pearson_ci
- mine_structural_pairs.py
- test_eval_generator.py
- test_ingest_refs.py
- Qwen3MLXReranker
- _FakeResponse
- cohen_kappa
- test_acquire_missing.py
- sha256_dir
- test_push_datasets.py
- main
- stats.py
- test_audit_reg_edges.py
- test_bench_retrieval_artifacts.py
- build_report
- Handler
- remap_doc_ids.py
- hybrid_gate_sweep.py
- test_golden_v7_resolver.py
- paired_delta
- audit_reg_edges.py
- RuntimeError
- parse_reply
- read_trec_run
- Embedder
- test_app_asof.py
- main
- trace_failure.py
- filter_targeted_rows
- measure_supersession_precision
- test_build_reg_edges.py
- test_canary_generator.py
- main
- .query
- phase_judge
- corpus_integrity.py
- regression_detector.py
- test_benchmark.py
- test_injection.py
- bench_rerankers.py
- run_judge
- canary.sh
- _resolve_governing_spans
- main
- test_context_recall.py
- _alias_keys
- run.sh
- ce_query_reform_probe.py
- main
- test_golden_v7_agreement.py
- _parse_error_ids
- main
- seed_v7.py
- refresh.sh
- validate_corpus.py
- measure_mrr
- measure_parsing_latency
- measure_retrieval_recall
- measure_temporal_accuracy
- test_build_index_out_dir.py
- _FakeDenseIndex
- test_synthesize_stratum_never_reads_a_model_emitted_type_field
- segment.py
- lineage_anomaly.py
- faithfulness
- normalize_circular_number
- autoresearch.sh
- Master Circular for Mutual Funds (2026)
- main
- validate_golden.py
- SEBI Master Circular for Mutual Funds (2020)
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
1. `Chunk` - 119 edges
2. `RAGPipeline` - 63 edges
3. `HybridRetriever` - 58 edges
4. `hierarchical_chunk()` - 56 edges
5. `Settings` - 55 edges
6. `HashEmbedder` - 48 edges
7. `ExtractiveStubGenerator` - 48 edges
8. `load_golden()` - 42 edges
9. `build_lineage()` - 40 edges
10. `BGEM3Embedder` - 36 edges

## Surprising Connections (you probably didn't know these)
- `test_gate_floors_context_recall()` --calls--> `derive_floors()`  [INFERRED]
  tests/test_context_recall.py → scripts/golden_v7/derive_thresholds.py
- `_chunk()` --uses--> `Chunk`  [INFERRED]
  tests/test_hyde.py → src/sebi_rag/segment.py
- `test_get_chunk_text_builds_once_and_caches()` --uses--> `Chunk`  [INFERRED]
  tests/test_spaces_app.py → src/sebi_rag/segment.py
- `test_chunks_config_refuses_header_and_maps_fields()` --uses--> `Chunk`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/segment.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **SEBI Regulatory Consolidation Pattern** — sebi_ho_imd_df2_cir_p_2020_156, eval_golden_v7_annotations_packet_human_packet_ho_19_34_11_6_2025_afd_pod1_i_12928_2026, eval_golden_v7_annotations_packet_human_packet_sebi_ho_ddhs_pod_2_p_cir_2025_99 [EXTRACTED 0.90]
- **Mutual Fund Offsite Inspection Reporting** — sebi_ho_imd_imd_pod_1_p_cir_2025_38, ho_24_13_11_1_2026_imd_pod_1_i_7602_2026, sebi_mutual_funds_regulations_2026 [EXTRACTED 0.95]
- **Angel Fund Regulatory Framework** — sebi_ho_afd_afd_pod_1_p_cir_2025_128, sebi_ho_afd_afd_pod_1_p_cir_2025_136, ho_19_34_11_6_2025_afd_pod1_i_12928_2026 [EXTRACTED 1.00]

## Communities (196 total, 34 thin omitted)

### Community 0 - "Chunk"
Cohesion: 0.06
Nodes (23): Generator, Judge, MLXGenerator, OllamaGenerator, Protocol, ADOPTED gate (eval_gate round 3): deterministic groundedness signal — max…, Max cosine(query, doc subject line) over contexts — the primary gate signal,…, Max cosine(query, section heading) over contexts — the second tier. (+15 more)

### Community 1 - "sebi_rag/verify_master.py"
Cohesion: 0.17
Nodes (14): _doc_checksum(), _embedder_identity(), Path, F3 (ADR-001): encode only new/changed documents; reuse cached embedding rows…, Deterministic per-document checksum over its (enriched) chunk texts — captures…, The embedder's own identity stamp (BGEM3Embedder/HashEmbedder set `.model_id`),…, _corpus_v1(), CountingEmbedder (+6 more)

### Community 2 - "ValueError"
Cohesion: 0.17
Nodes (20): _assert_fixed_tail(), convert_run_dir(), main(), Path, Back-convert archived runfiles into standards-compliant TREC artifacts. The…, Trailing field of the first line; also the whitespace precondition check., read_trec_run assumes qid and tag carry no whitespace. Verify per line., Write run.chunk.trec, run.doc.trec and docids.tsv for one archived run. (+12 more)

### Community 3 - "eval_harness.py"
Cohesion: 0.09
Nodes (29): Ground truth: what do the 4 CE_MISMATCH rows actually DO in production? The…, Preregistered cohort measurement for the CE paraphrase rescue. Spec:…, What does the 0.05 cross-encoder score floor actually catch?…, Capture-once margin sweep for B' selective citations. One pipeline pass over…, Benchmark MLX generators on the golden set: faithfulness, groundedness,…, CLI for automated metric collection via sebi_rag.measure. Usage: python…, Retrieval-only benchmark with TREC runfile and reproducibility metadata. Use…, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped… (+21 more)

### Community 4 - "telemetry_engine.py"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 5 - "test_golden_v7_gate.py"
Cohesion: 0.17
Nodes (19): Path, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed     v7 gate,, select_golden(), _gate_file(), Offline tests for the golden-v7 CI gate flip (spec 2026-07-23 sec 8).  The gate, derive_floors reads its vectors from score.vectors(); a metric absent     there, floors_ok fails closed on a metric the report does not carry, so a     floor nam, eval_json.py has no main() and boots real MPS models at import, so it     cannot (+11 more)

### Community 6 - "app.py"
Cohesion: 0.05
Nodes (52): _append_message(), _blank_previews(), _build_citations_markdown(), build_ui(), _certainty_badge(), _cycle_messages_until_done(), _empty_citations_md(), _faithfulness_badge() (+44 more)

### Community 7 - "Frame"
Cohesion: 0.07
Nodes (42): load_runs(), main(), Path, Assign epochs to the archived runs and write the epoch registry. Every run's…, _fmt(), guard_pair(), main(), Path (+34 more)

### Community 8 - "test_context_headers.py"
Cohesion: 0.07
Nodes (31): Build the dense+sparse index once and persist it (run after corpus changes).…, main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), filter_targeted_rows(), HeaderGenerator (+23 more)

### Community 9 - "test_paraphrase_rescue.py"
Cohesion: 0.10
Nodes (35): is_degenerate(), Paraphrase rescue for the cross-encoder score floor. Preregistered in…, Re-score `pool` with a rewritten query when `reranked` is below `floor`.…, Fixed rewrite, for tests and for replaying a preregistered rewrite., True when `rewritten` is unusable and the rescue should be abandoned.…, rescue_pool(), StaticQueryRewriter, _chunk() (+27 more)

### Community 10 - "test_ui.py"
Cohesion: 0.05
Nodes (14): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., Every yielded tuple — loading, streaming chunks, final — must match the output…, Regression guard for the zip-misalignment class of bug (app.py:389): a…, _validate_api_url runs inside submit_query_stream's try block — a ValueError…, _Resp, test_submit_query_all_yields_share_arity(), test_submit_query_malformed_as_of_short_circuits(), _boom() (+6 more)

### Community 11 - "test_api.py"
Cohesion: 0.06
Nodes (37): BaseModel, FastAPI, integration, _citation_meta(), CitationMeta, create_app(), get_chunk_text(), health() (+29 more)

### Community 12 - "load_golden"
Cohesion: 0.11
Nodes (33): main(), SPIKE/GATE (throwaway, not preregistered) — R5's own precondition from the…, main(), Phase 1 (systematic-debugging) evidence gathering for the 2026-09-03…, main(), main(), main(), What actually makes a context window large: chunk size, or chunk count? Read-… (+25 more)

### Community 13 - "test_finetune_train_lora.py"
Cohesion: 0.09
Nodes (38): apply_lora(), build_dataset(), check_trainable_ratio(), find_latest_checkpoint(), load_pairs(), main(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-… (+30 more)

### Community 14 - "test_regulations.py"
Cohesion: 0.07
Nodes (37): _alias_keys(), _jaccard(), load_regulations(), name_tokens(), Path, Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6). Regulations…, Candidate alias lookup keys, most literal first. Both the raw normalised form…, Resolve a cited regulation name+year to a canonical reg_id. Returns (reg_id,… (+29 more)

### Community 15 - "test_attribution.py"
Cohesion: 0.07
Nodes (33): entailment_index(), NLIAttributionScorer, NLI attribution scoring for B' citation selection. B' asks "does this context…, Index of the entailment class in a model's label map. Read from the checkpoint…, Scores each context by P(entailment) of the answer given that context.…, Wrap an already-constructed cross-encoder (also the test seam)., _softmax(), pick_device() (+25 more)

### Community 16 - "RAGPipeline"
Cohesion: 0.08
Nodes (56): Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)…, smoke_pipeline(), smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable…, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., RAGPipeline (+48 more)

### Community 17 - "test_finetune_eval_phase0.py"
Cohesion: 0.10
Nodes (36): compare(), group_stats(), gate_verdict(), main(), _mean(), parse_run_doc(), Path, Phase A eval (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-… (+28 more)

### Community 18 - "test_spaces.py"
Cohesion: 0.08
Nodes (26): _grounded_prompt(), F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and the…, ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo. All classes implement…, External Space first; on ANY failure fall back to the local CPU model.…, Primary generator: calls a public LLM Space via gradio_client. Wired to… (+18 more)

### Community 19 - "test_golden_v7_packet.py"
Cohesion: 0.07
Nodes (56): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+48 more)

### Community 20 - "test_conformal.py"
Cohesion: 0.10
Nodes (32): _control_summary(), main(), phase_calibrate(), phase_generate(), phase_report(), R7 conformal abstention calibration: generate -> calibrate -> report phases.…, Current production behaviour, exactly as shipped -- no LOO recalibration, the…, Re-simulates each row's abstention decision under the CALIBRATED thresholds,… (+24 more)

### Community 21 - "extract_citations"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 22 - "answer_with_abstention"
Cohesion: 0.14
Nodes (25): Answer, answer_with_abstention(), _abstain(), _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., rerank_top exactly at 0.15 overrides judge abstention (HYBRID_THRESHOLD=0.15,…, rerank_top just below 0.15 does NOT override judge abstention., When no judge is present, hybrid gate logic must be inert (no crash). (+17 more)

### Community 23 - "test_dataset_cards.py"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 24 - "derive_validity"
Cohesion: 0.07
Nodes (28): annotate_corpus(), Update each corpus record's supersession_status + superseded_by + supersedes…, annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans… (+20 more)

### Community 25 - "test_finetune_mine_structural.py"
Cohesion: 0.11
Nodes (28): _is_signoff_boilerplate(), _leaks_metadata(), mine_heading_section(), mine_subject_body(), First line matching the numbered-clause pattern -> (heading, rest). None if no…, _split_heading(), Offline tests for scripts/finetune/mine_structural_pairs.py's pure transforms.…, A passage that merely MENTIONS a manager's title mid-paragraph is substantive… (+20 more)

### Community 26 - "test_spaces_app.py"
Cohesion: 0.07
Nodes (6): app_module(), fixture, HF Spaces demo (root app.py): citations table + preview accordion logic. Fully…, app.py does `import spaces` (ZeroGPU) at module scope; stub it., _stub_spaces_package(), test_get_chunk_text_builds_once_and_caches()

### Community 27 - "ui.py"
Cohesion: 0.11
Nodes (30): _append_message(), _blank_previews(), _build_citations_markdown(), build_ui(), _certainty_badge(), _cycle_messages_until_done(), _empty_citations_md(), _faithfulness_badge() (+22 more)

### Community 28 - "Settings"
Cohesion: 0.15
Nodes (26): is_master(), main(), Is the eval set measuring retrieval, or measuring its own construction? Read-…, main(), R3 §3.1 — mine cross-reference (A cites B) candidate pairs. Spec:…, _get(), Path, Settings.load() plus the [spaces] table as settings.spaces.* Load order per… (+18 more)

### Community 29 - "_is_non_sebi_domain"
Cohesion: 0.10
Nodes (29): _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain. Case-…, The non-SEBI domain filter must match words, not substrings. Shipped 2026-07-30…, Any single-token keyword <= 5 chars is a substring hazard. Embedding it inside…, Query mentioning both SEBI and RBI should NOT abstain — SEBI intent wins., Empty query should not trigger the non-SEBI filter., FEMA keyword in a SEBI context should NOT abstain — SEBI intent wins., The exact query that exposed the bug. (+21 more)

### Community 30 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 31 - "scripts/verify_master.py"
Cohesion: 0.20
Nodes (16): chunk_docid(), circular_docid(), MalformedChunkId, Standards-compliant TREC run and qrels emission. The archived runfiles are not…, Raised when an id cannot yield a whitespace-free TREC doc id., Percent-encode whitespace so a circular id is a single TREC field. Reversible…, Map a chunk id to a whitespace-free TREC doc id. `<circular>#<heading with…, Standards-compliant TREC artifact emission (spec A §3-4). (+8 more)

### Community 32 - "load_circulars"
Cohesion: 0.14
Nodes (30): load_circulars(), Path, Path, corpus.load_circulars edge-case coverage. load_circulars reads a JSONL corpus…, Provided optional fields are passed through to CircularMeta., Multiple records produce multiple chunks., Blank lines between records are silently skipped., Malformed JSON raises ValueError (json.loads default). (+22 more)

### Community 33 - "reranker_interaction_check.py"
Cohesion: 0.15
Nodes (24): _unique(), main(), parse_args(), Namespace, Compare query-expansion arms (current prod / no-expand / HyDE) on a golden set.…, run_arm(), doc_ids_deduped(), fmt() (+16 more)

### Community 34 - "test_golden_v7_gemini.py"
Cohesion: 0.15
Nodes (26): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct from a well-…, A Gemini reply that disputes an abstain row (says YES, it IS answerable) writes… (+18 more)

### Community 35 - "test_golden_v7_local.py"
Cohesion: 0.13
Nodes (24): golden_v7/__init__.py, _FakeResponse, _ok_payload(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external…, oMLX's skip_api_key_verification is on: an unset token is not an error, it just…, Five pilot rows from five strata measure more than five from one - the gemini…, Vote records must say annotator "qwen" (never reuse "gemini" - the agreement… (+16 more)

### Community 36 - "_row"
Cohesion: 0.12
Nodes (27): decide(), Spec sec7 promotion rules for one row. `votes_by_annotator` is this row's votes…, Abstain rows have no explicit claude vote at all (Task 8 never judged them) -…, Both externals independently think something DOES govern (disputing the…, The LLM leg is whichever single non-claude/non-human annotator voted - "qwen"…, Amendment 2026-07-26 (user-approved): the promotion unit is the PROVISION, not…, External marked claude's chunk governing plus extras: claude's label is…, The abstain protocol can never emit non-empty governing (no letters are… (+19 more)

### Community 37 - "ingest_pdf.py"
Cohesion: 0.10
Nodes (26): Re-derive circular number + dates from each record's stored text and rewrite…, main(), Repair the 6 records whose body text was overwritten with one shared circular's…, _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number() (+18 more)

### Community 38 - "HybridRetriever"
Cohesion: 0.09
Nodes (30): expand_query(), Append statutory synonyms for lay tokens present in `query`. Deterministic and…, BM25 lexical index (bm25s)., SparseIndex, _chunk(), Query-side lexical expansion (intervention #2, glossary variant).…, test_all_five_sparse_failure_queries_expand(), test_expand_sparse_off_routes_raw_query_to_sparse_leg() (+22 more)

### Community 39 - "extract_misses.py"
Cohesion: 0.14
Nodes (23): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any… (+15 more)

### Community 40 - "benchmark.py"
Cohesion: 0.14
Nodes (33): cited_docs(), metrics(), evaluate(), beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), chunks_by_doc() (+25 more)

### Community 41 - "test_finetune_holdout.py"
Cohesion: 0.14
Nodes (24): build(), classify_rows(), gold_circulars(), main(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-…, Every distinct circular any golden_v7 row cites as relevant, sorted for…, Deterministic seeded sample. round(), not int(), so 159*0.30=47.7 lands on 48… (+16 more)

### Community 43 - "export_datasets.py"
Cohesion: 0.17
Nodes (12): build_aikosh_pack(), build_hf_card(), build_kaggle_metadata(), build_zenodo_pack(), _compute_stats(), Corpus-derived numbers for the card prose (UNKNOWN fraction, date range) plus…, Build HuggingFace dataset card (README.md with YAML front matter)., Build Kaggle metadata.json. (+4 more)

### Community 44 - "synthesize_queries.py"
Cohesion: 0.12
Nodes (24): Every chunk's text is `"{doc_id} | {subject[:120]} | {section}\\n{body}"` -…, _strip_context_header(), cache_path(), call_omlx(), _extract_json_query(), _has_boilerplate(), lineage_supersession_candidates(), multi_hop_candidates() (+16 more)

### Community 45 - "gemini_adjudicate.py"
Cohesion: 0.12
Nodes (24): adjudicate(), _current_model(), _daily_quota_exhausted(), main(), _parse_error_ids(), _parse_letter_choice(), _parse_reply(), _parse_yes_no() (+16 more)

### Community 46 - "test_label_tier.py"
Cohesion: 0.12
Nodes (20): classify_tier(), human_reviewed_ids(), main(), Path, Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.…, Map provenance to the controlled vocabulary. `human_reviewed` (row appears in…, Row ids present in the human labelling packet., Controlled-vocabulary label_tier over golden_v7 (spec A §8.3). (+12 more)

### Community 47 - "test_finetune_roundtrip_filter.py"
Cohesion: 0.12
Nodes (29): build_text_to_doc_map(), filter_boilerplate(), load_rows(), Path, Phase 1 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-…, Prefer the row's own positive_doc field (future runs); fall back to the reverse…, Retrieves with each row's query against `retriever` (the frozen base index) and…, Returns (kept, n_dropped). (+21 more)

### Community 48 - "backfill_escalations.py"
Cohesion: 0.16
Nodes (22): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+14 more)

### Community 49 - "local_adjudicate.py"
Cohesion: 0.12
Nodes (23): Transient-failure predicate for the real Gemini call: rate limiting (429) and…, Rerun-safety for votes.jsonl itself (plan Task 10 decision #7): drops every…, Same per-row deterministic shuffle as make_packet.py's write_packet:…, _replace_annotator_votes(), _should_retry(), _shuffled_candidates(), _current_model(), _extract_text() (+15 more)

### Community 50 - "parse_meta"
Cohesion: 0.11
Nodes (21): Pattern, main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), _iso_date(), _labeled_date(), parse_meta(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars. (+13 more)

### Community 51 - "agreement.py"
Cohesion: 0.15
Nodes (20): _claude_accuracy_ci(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation…, rid -> annotator -> expected_literal. Kept separate from `_votes_by_row` so…, As `_stratum_kappas`, grouped by label provenance tier rather than task_type.… (+12 more)

### Community 52 - "generate.py"
Cohesion: 0.09
Nodes (18): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_warrant_scores(), parse_yes_no(), Prompt for the warrant judge: evaluate each excerpt's warrant for the answer.…, Parse warrant scores from the judge's JSON output. Returns a list of n floats… (+10 more)

### Community 53 - "test_selective_citations.py"
Cohesion: 0.06
Nodes (63): _aggregate(), eligible(), main(), _measure(), phase_generate(), phase_report(), B' citation-scorer cohort measurement: control (bge, pointwise) vs J1 (jina,…, Answerable, non-as_of, with gold citations. Matches warrant_scorer_cohort.py's… (+55 more)

### Community 54 - "hierarchical_chunk"
Cohesion: 0.12
Nodes (29): hierarchical_chunk(), flush(), _paragraphs(), add(), Split into units each <= max_chars. PDF-extracted text often lacks blank-line…, Document -> section -> paragraph chunks with stable IDs. A "section" is…, _ollama_up(), pipeline() (+21 more)

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
Cohesion: 0.14
Nodes (33): build_chunk_rows(), build_corpus_rows(), build_eval_rows(), build_lineage_rows(), _config_entry(), _emit(), export_all(), export_chunks() (+25 more)

### Community 59 - "mine_strata.py"
Cohesion: 0.20
Nodes (8): csr_matrix, Path, SPLADE learned-sparse retrieval leg (iv11). Non-destructive, opt-in third RRF…, SpladeIndex, _fake_encode(), Return an encode fn mapping known texts to known dense weight rows., test_save_load_roundtrip_and_guard(), test_search_ranks_by_sparse_dot_product()

### Community 60 - "scrape_sebi.py"
Cohesion: 0.06
Nodes (61): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+53 more)

### Community 61 - "draft_expansion_rows.py"
Cohesion: 0.20
Nodes (17): build_body_paraphrase_prompt(), build_far_negative_prompt(), build_hard_negative_prompt(), build_lineage_supersession_prompt(), build_multi_hop_prompt(), build_numeric_table_prompt(), build_repealed_basis_prompt(), build_title_direct_prompt() (+9 more)

### Community 62 - "main"
Cohesion: 0.13
Nodes (18): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl(), _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus. (+10 more)

### Community 63 - "publish_hf.py"
Cohesion: 0.18
Nodes (19): export_golden_v7_arrow(), log(), main(), Path, Run export_datasets.py then add golden_v7 Arrow config., Upload dist/datasets/ to HF dataset repo., Run make index to rebuild FAISS+BM25 before upload., Publish SEBI RAG artifacts to Hugging Face. Covers three repos in one… (+11 more)

### Community 64 - "test_pipeline.py"
Cohesion: 0.25
Nodes (8): _chunks(), _fake_encode(), Returns a fixed dense ranking regardless of query., _StubDense, _StubSparse, test_flag_off_is_unchanged_and_ignores_splade(), test_splade_leg_changes_fused_order_when_on(), test_use_splade_without_index_raises()

### Community 65 - "test_annotation_adds_no_circular_meta_field"
Cohesion: 0.15
Nodes (16): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), parametrize, Regulation edges + corpus annotation (spec 2026-07-23 §3.3, §3.4, §3.7)., Index-invariance guard (spec §3.1): the new fields must never be ones…, An alias pointing at a slug that is neither a scraped in-force regulation nor a…, test_annotation_adds_no_circular_meta_field() (+8 more)

### Community 66 - "api.py"
Cohesion: 0.33
Nodes (6): _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker. Shared verbatim…, _embed_kwargs is _compute_kwargs + model_path, and must never mutate or widen…, test_compute_kwargs_cpu_disables_fp16(), test_compute_kwargs_mps_keeps_fp16(), test_embed_kwargs_adds_model_path_without_touching_compute_kwargs()

### Community 67 - "validate_golden"
Cohesion: 0.15
Nodes (15): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.…, validate_golden(), Answerable-but-unjudged rows are excluded from metrics, never scored 0.…, A real, fully-populated golden row, so the fixture cannot drift out of sync…, v7-ls-038/039/040 are answerable but unjudged; they carry… (+7 more)

### Community 68 - "sebi_rag/eval_asof.py"
Cohesion: 0.14
Nodes (24): sebi_rag/eval_asof.py, AsofCaseResult, build_report(), load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Aggregate case results with an exact confidence interval. Pure function of the… (+16 more)

### Community 69 - "test_reg_lineage.py"
Cohesion: 0.22
Nodes (19): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, _circ(), test_annotate_is_idempotent(), test_annotate_orders_regulations_by_count_descending(), test_annotate_sets_the_three_additive_fields() (+11 more)

### Community 70 - "test_scrape_sebi.py"
Cohesion: 0.13
Nodes (7): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), fake_page(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 71 - "MeasureResult"
Cohesion: 0.10
Nodes (14): main(), metrics_to_markdown(), Format results as a markdown table., measure_temporal_accuracy(), MeasureReport, MeasureResult, Measure fraction of as_of queries returning correct pre-supersession circular…, Run all (or specified) metrics sequentially. (+6 more)

### Community 72 - "SpladeIndex"
Cohesion: 0.16
Nodes (13): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.…, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+5 more)

### Community 73 - "audit_label_provenance.py"
Cohesion: 0.21
Nodes (15): audit(), collect_artifacts(), _ids_from_csv(), _ids_from_dir(), _ids_from_jsonl(), main(), Path, Report what the annotation artifacts can account for, before classifying.… (+7 more)

### Community 74 - "mine_hard_negatives"
Cohesion: 0.24
Nodes (16): mine_hard_negatives(), One batched embed + one batched FAISS search for the whole set - not a per-…, _FakeChunk, _FakeEmbedder, _FakeRetriever, mine_hard_negatives only uses embed() to build the FAISS query vectors now (no…, Backward-compat: every mine_structural_pairs.py template has positive ==…, Phase 1's multi_hop rows: source_doc is the CITING document, but the positive… (+8 more)

### Community 75 - "_bootstrap_ci"
Cohesion: 0.05
Nodes (36): skip, mrr(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), _bootstrap_ci(), _git_commit(), measure_context_precision(), measure_mrr() (+28 more)

### Community 76 - "test_hyde.py"
Cohesion: 0.14
Nodes (12): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —…, test_generation_error_returns_empty(), boom(), test_hyde_leg_improves_paraphrase_gap_rank() (+4 more)

### Community 77 - "consolidation_edges"
Cohesion: 0.15
Nodes (10): _extracts(), MLXQueryRewriter, Protocol, query_rewriter_for(), QueryRewriter, Factory mirroring `generate.citation_scorer_for`: None when disabled., Rewrites a lay-vocabulary query into statutory vocabulary. Returns None when it…, Local MLX-LM rewriter. Greedy decoding -> deterministic. (+2 more)

### Community 78 - "test_export_integration.py"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 79 - "settings.py"
Cohesion: 0.31
Nodes (8): log(), Margin sweep for B' selective citations on the golden_v7 adjudicated set. One…, run(), One scoring path shared by `eval_json.py` (which measures) and…, Score one golden row through the production-shaped pipeline. Returns per-row…, Per-row records -> metric -> score vector, skipping rows where the metric was…, score_row(), vectors()

### Community 80 - "_provision_agree"
Cohesion: 0.20
Nodes (10): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using the…, Does this external vote confirm claude's label, at PROVISION level? Amendment…, Different chunk copies of the same quoted provision agree at provision level…, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction(), test_provision_agree_disjoint_without_pool_is_false() (+2 more)

### Community 81 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 82 - "test_eval_harness_v7.py"
Cohesion: 0.23
Nodes (16): EvalReport, report_dict(), run_eval(), P1 evaluation-harness test (offline). Loads the real seed corpus…, test_eval_harness_metric_suite(), test_real_corpus_loads_with_provenance_fields(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-… (+8 more)

### Community 83 - "test_lineage.py"
Cohesion: 0.06
Nodes (53): contexts_for(), build_lineage(), _currency(), demote_superseded(), detect_relations(), detect_relations_ex(), Lineage, mc_topic() (+45 more)

### Community 85 - "scrape_regulations.py"
Cohesion: 0.17
Nodes (12): derive_floors(), metric -> per-query score vector, into gate-floor names -> floor value.      Met, The floor is a bootstrap lower bound minus a cushion, never the mean.     Gating, A metric nobody scored must not be floored at 0 - a 0 floor is not a     gate, i, B' gates citation_precision alongside recall/recall_tradeoff/abstention.     The, recall_at_k is ceiling-limited (baseline 0.956 leaves ~9 failing     queries of, test_citation_precision_is_gated_after_B_prime(), test_derive_floors_skips_metrics_with_no_scored_queries() (+4 more)

### Community 86 - "validate"
Cohesion: 0.20
Nodes (20): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair. Checks (per…, Every record's text must match the PDF its provenance names. Slow (re-extracts…, validate(), validate_deep(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the document's own… (+12 more)

### Community 87 - "build_spaces_pipeline"
Cohesion: 0.23
Nodes (13): build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux). Parallel…, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row() (+5 more)

### Community 88 - "measure.py"
Cohesion: 0.57
Nodes (6): _internal(), Prove the internal retrieval metrics are the standard ones. Skips unless the…, _standard(), test_mrr_matches_ir_measures(), test_ndcg_at_10_matches_ir_measures(), test_recall_at_10_matches_ir_measures()

### Community 89 - "test_expand.py"
Cohesion: 0.25
Nodes (6): RuntimeError, Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_resolve_stems_survives_detail_fetch_error(), bad_fetch(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 90 - "_doc"
Cohesion: 0.43
Nodes (6): aggregate(), eligible(), main(), measure(), Preregistered cohort measurement for supersession confidence tiering. Spec:…, Answerable, non-as_of, with gold citations: the rows citation metrics exist for.

### Community 91 - "corpus.py"
Cohesion: 0.17
Nodes (12): floors_ok(), True iff every floor's metric is present in `report_gate` and meets it.      Mis, Demotion or reranking can empty the context window while the fusion list is…, test_context_recall_floor_catches_a_regression_fusion_recall_misses(), derive_floors emits gate-report metric names, not the internal     score_row nam, A floor naming a metric the report does not carry cannot be shown to     hold, s, test_floor_names_match_the_gate_report_keys(), test_floors_not_ok_when_one_metric_is_below() (+4 more)

### Community 92 - "clopper_pearson_ci"
Cohesion: 0.24
Nodes (4): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 93 - "mine_structural_pairs.py"
Cohesion: 0.14
Nodes (21): build_citation_pairs(), build_supersession_pairs(), _format_family(), Pure transform: corpus + lineage -> labeled circular pairs. label is…, Pure transform: corpus text -> citation-normalization rows. Mines in-body…, load_chunks_by_doc(), load_corpus_records(), load_minable_docs() (+13 more)

### Community 94 - "test_eval_generator.py"
Cohesion: 0.16
Nodes (12): eval_generator_for(), The single generator decision for the eval stack. `derive_thresholds.py` sets…, The eval stack's generator choice must be one shared decision.…, Uses an injected loader so the test stays offline., Silently falling back to the stub would derive floors under semantics the…, Must assert the factory is CALLED, not merely imported. Verified 2026-08-12 by…, A factory both call is not enough - they must pass the same setting, or the…, test_both_eval_scripts_read_the_same_setting() (+4 more)

### Community 95 - "test_ingest_refs.py"
Cohesion: 0.15
Nodes (11): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_fulltext_fallback_returns_earliest_body_reference() (+3 more)

### Community 96 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 97 - "_FakeResponse"
Cohesion: 0.21
Nodes (11): _FakeResponse, _ok_payload(), Security-relevant: base_url is CLI-configurable here (unlike…, test_call_omlx_never_reads_anthropic_auth_token(), _fake_post(), test_call_omlx_no_token_sends_no_auth_header(), _fake_post(), test_call_omlx_retries_on_5xx() (+3 more)

### Community 98 - "cohen_kappa"
Cohesion: 0.33
Nodes (6): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw element is…, test_cohen_kappa_both_constant_and_identical_is_one(), test_cohen_kappa_empty_input_is_one(), test_cohen_kappa_identical_lists_is_one(), test_cohen_kappa_independent_looking_lists_is_low()

### Community 100 - "sha256_dir"
Cohesion: 0.24
Nodes (11): main(), merge(), Path, Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-…, Per-file sha256 of every file in the merged model dir - the plan's "sha256 into…, CPU by design, not MPS: this is a one-shot weight merge, not a training or…, sha256_dir(), Offline tests for scripts/finetune/merge_adapter.py's pure pieces. The actual… (+3 more)

### Community 101 - "test_push_datasets.py"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default:…, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 102 - "main"
Cohesion: 0.24
Nodes (10): Which golden set gates CI, and whether its adjudicated subset clears the derived, Names of axes where `gate`'s recorded stack differs from `live`'s current     on, stack_matches(), bge-derived floor vs. jina-running production is the expected steady     state,, Every gate_v7.json that exists today (including the currently-armed     one) has, _stack(), test_stack_matches_ignores_production_reranker_model_difference(), test_stack_matches_reports_mismatched_axis_name() (+2 more)

### Community 103 - "stats.py"
Cohesion: 0.14
Nodes (10): bootstrap_ci(), BootstrapCI, PairedResult, ProportionCI, Uncertainty quantification for benchmark runs. The golden set is n=56…, True when the randomization test rejects at 1 - confidence AND the paired…, Percentile bootstrap interval for the mean of per-query scores., Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests). (+2 more)

### Community 104 - "test_audit_reg_edges.py"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 105 - "test_bench_retrieval_artifacts.py"
Cohesion: 0.15
Nodes (9): bench_retrieval must emit valid TREC alongside the legacy runfile., run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so every…, iv9/iv10 build a headered index beside data/index. Without an index override…, ADR-004: benchmarking jina-reranker-v3-mlx against the production cross-encoder…, 2026-08-26 Set-Encoder spec: benchmarking webis/set-encoder-base (via…, test_bench_retrieval_can_bench_an_alternate_index(), test_bench_retrieval_can_measure_the_reranked_order(), test_bench_retrieval_exposes_and_records_the_reranker_choice() (+1 more)

### Community 106 - "build_report"
Cohesion: 0.27
Nodes (10): Rankings, Path, Reverse map `docid -> full chunk id`, so nothing is lost., Valid 6-field TREC run at chunk granularity., write_docids(), _write_lines(), write_run_chunk(), test_docids_maps_docid_back_to_full_chunk_id() (+2 more)

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
Cohesion: 0.31
Nodes (10): _emit(), main(), _load(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score() (+2 more)

### Community 113 - "RuntimeError"
Cohesion: 0.29
Nodes (10): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+2 more)

### Community 114 - "parse_reply"
Cohesion: 0.18
Nodes (11): parse_reply(), Full parse result including the parse_error flag cached per row. letters=[] is…, Public letter-choice-protocol parser: (chosen letters, expected literal).…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply…, test_parse_reply_empty_letters_dispatches_to_yes_no_protocol(), test_parse_reply_garbage_is_unparseable(), test_parse_reply_letters_and_expected() (+3 more)

### Community 115 - "read_trec_run"
Cohesion: 0.17
Nodes (11): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), write_trec_run(), _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields() (+3 more)

### Community 116 - "Embedder"
Cohesion: 0.16
Nodes (7): Embedder, ndarray, Protocol, _tokens(), DenseIndex, ndarray, FAISS IndexFlatIP over L2-normalized vectors (cosine).

### Community 117 - "test_app_asof.py"
Cohesion: 0.20
Nodes (6): app_module(), _expected_output_count(), fixture, As-of date plumbing in the Spaces UI (app.py)., 8 fixed fields + 2 per preview accordion + 4 meta badges. Matches the flat list…, test_run_query_yield_arity_matches_outputs_list_pipeline_free_paths()

### Community 118 - "main"
Cohesion: 0.20
Nodes (9): main(), Emit TREC qrels for an eval set, keyed by its golden_sha256. .venv/bin/python…, Write TREC qrels (`qid 0 docid rel`) at circular level. Binary relevance:…, write_trec_qrels(), test_qrels_excludes_abstain_rows(), test_qrels_expands_relevant_circulars(), test_qrels_has_no_header(), test_qrels_lines_are_four_space_separated_fields() (+1 more)

### Community 119 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 120 - "filter_targeted_rows"
Cohesion: 0.24
Nodes (9): main(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).  Write, Keys must match gate_select._STACK_AXES exactly, or stack_matches() silently, stack_from_settings(), A stack block whose keys don't exactly match _STACK_AXES would make     stack_ma, derivation_reranker is a constant (never read from config); production_     rera, _settings(), test_stack_from_settings_records_but_does_not_compare_reranker_split() (+1 more)

### Community 121 - "measure_supersession_precision"
Cohesion: 0.22
Nodes (9): Valid 6-field TREC run collapsed to circular level. Keeps each circular once,…, write_run_doc(), artifacts(), fixture, The encoding must agree across runs and qrels. If a run says…, test_qrels_docids_match_run_doc_docids_exactly(), test_run_doc_dedupes_to_best_rank(), test_run_doc_encodes_space_bearing_circulars() (+1 more)

### Community 122 - "test_build_reg_edges.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 123 - "test_canary_generator.py"
Cohesion: 0.27
Nodes (8): _canary_jscode(), _ops_timeout(), The eval canary must fit its timeout and alert on real regressions. Measured…, n8n gives up first if its budget is smaller, so the ops timeout is never…, A threshold above the healthy value fires every run. citation_precision was…, test_alert_thresholds_sit_below_measured_baselines(), test_n8n_timeout_not_tighter_than_the_ops_budget(), test_ops_timeout_fits_the_measured_runtime()

### Community 124 - "main"
Cohesion: 0.31
Nodes (7): call(), main(), _norm(), Does answering a golden_v7 row require a circular the corpus does not hold?…, Uppercase, strip all whitespace — so 'CIR/MIRSD/5/ 2013' matches…, Returns (answer, reasoning). The judge is a reasoning model: the oMLX API…, windows()

### Community 125 - ".query"
Cohesion: 0.39
Nodes (8): _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons,…, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful(), test_no_context_reason_when_top_k_zero(), test_score_floor_reason(), test_subject_gate_reason_and_subject_sim_recorded()

### Community 126 - "phase_judge"
Cohesion: 0.36
Nodes (9): _aggregate(), eligible(), main(), _measure(), phase_generate(), phase_judge(), phase_report(), R1 §4/§6 cohort measurement: control (cross-encoder) vs W1 (warrant judge).… (+1 more)

### Community 127 - "corpus_integrity.py"
Cohesion: 0.31
Nodes (8): check_meta_fields(), load_chunks(), load_corpus(), main(), Corpus integrity checker — verify chunks.jsonl matches corpus JSONL. Checks: 1.…, Load corpus into a dict keyed by circular_number., Load chunks and return (records, doc_ids)., Check that chunk meta has expected CircularMeta fields.

### Community 128 - "regression_detector.py"
Cohesion: 0.31
Nodes (8): extract_metrics(), load_floors(), load_latest_runs(), main(), Eval regression detector — flag when metrics drop below gate floors. Checks: 1.…, Load floors from gate_v7.json., Load most recent eval runs sorted by timestamp., Extract metric values from a run.

### Community 129 - "test_benchmark.py"
Cohesion: 0.32
Nodes (6): main(), parse_args(), Namespace, Sweep RRF k_const values on a golden set. No index rebuild needed. Turn 1 of…, Retrieve+refuse at a single k_const. Returns per-query score dicts., run_one_k()

### Community 130 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 131 - "bench_rerankers.py"
Cohesion: 0.28
Nodes (8): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,…, sebi_rag/__init__.py, SEBI Circular RAG — local-first, Apple Silicon. Pipeline: ingest -> segment ->…

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
Cohesion: 0.48
Nodes (6): _chunk_id(), _doc(), load_pre_expansion_ids(), main(), Path, W1.3 diagnostic (2026-09-03 architecture review): does the 730->1,490 corpus…

### Community 136 - "test_context_recall.py"
Cohesion: 0.33
Nodes (9): _chunk(), The gate must measure the context window, not just the fusion list.…, An abstention still had a context window; measuring retrieval delivery must not…, _reranked(), test_answer_records_the_context_ids_it_used(), test_context_ids_populated_even_when_abstaining(), test_context_ids_respect_top_k(), test_gate_floors_context_recall() (+1 more)

### Community 137 - "_alias_keys"
Cohesion: 0.29
Nodes (7): gwet_ac1(), Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a prevalence-…, The kappa base-rate paradox: one label dominates, raw agreement is high, yet…, test_gwet_ac1_both_constant_and_identical_is_one(), test_gwet_ac1_empty_input_is_one(), test_gwet_ac1_exceeds_kappa_on_skewed_high_agreement(), test_gwet_ac1_identical_lists_is_one()

### Community 138 - "run.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 139 - "ce_query_reform_probe.py"
Cohesion: 0.38
Nodes (6): main(), _pool(), Probe: does query-side reformulation lift the CE score on the 4 CE_MISMATCH…, Return (ce_top, best relevant score, chunk_id of argmax)., Top-8 pool plus every relevant chunk, de-duplicated on chunk_id., _score()

### Community 140 - "main"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

### Community 141 - "test_golden_v7_agreement.py"
Cohesion: 0.26
Nodes (11): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions` (keyed by…, Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):…, _same_provision_fixture(), test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only(), test_apply_queue_decision_leaves_row_untouched() (+3 more)

### Community 142 - "_parse_error_ids"
Cohesion: 0.43
Nodes (6): _body(), main(), _norm(), pick(), Label the 7 rows re-pooled after the assemble_pool fix (2026-07-25 remediation…, (candidate, quote) pairs for this row: the answer_contains carrier first, then…

### Community 143 - "main"
Cohesion: 0.67
Nodes (3): main(), P0 prep: price a larger MLX generator before committing to the R0 upgrade.…, rss_gb()

### Community 144 - "seed_v7.py"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 145 - "refresh.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 146 - "validate_corpus.py"
Cohesion: 0.27
Nodes (3): Emit one JSON line listing SEBI circulars newer than previously seen. Uses a…, _as_bool(), Coerce a config/env value to bool. Env vars arrive as strings; toml/default may…

### Community 147 - "measure_mrr"
Cohesion: 0.33
Nodes (6): Deterministic, stable identity slug. This is the edge target and join key., reg_id(), _slug(), test_reg_id_is_a_deterministic_slug(), test_reg_id_is_stable_across_punctuation_and_case_variants(), test_reg_ids_from_the_fixture_are_unique()

### Community 148 - "measure_parsing_latency"
Cohesion: 0.50
Nodes (4): build_screen(), main(), T-Screen: does the generator follow the citation instruction at all? Spec:…, 50 rows stratified proportionally to golden_v7's eight strata.

### Community 149 - "measure_retrieval_recall"
Cohesion: 0.40
Nodes (5): Qwen-family models may emit <think>...</think> reasoning as inline text,…, _strip_thinking(), Qwen-family models may emit <think>...</think> as inline text rather than as…, test_strip_thinking_leaves_plain_replies_untouched(), test_strip_thinking_removes_inline_think_tags()

### Community 150 - "measure_temporal_accuracy"
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
Cohesion: 0.11
Nodes (19): _is_table_row_candidate(), _is_table_row_filler(), _is_toc_row_candidate(), _merge_table_rows(), is_candidate(), Segmentation: hierarchical chunking + metadata + stable citation IDs. Minimal,…, Nesting depth of a numbered line ("2.1.3" -> 2), or None if it isn't one at all., A numbered line whose own trailing text is short and does NOT end in a clause… (+11 more)

### Community 155 - "lineage_anomaly.py"
Cohesion: 0.47
Nodes (5): load_corpus(), load_lineage(), main(), Lineage anomaly detector — flag circulars with missing supersession edges.…, Load corpus keyed by circular_number.

### Community 156 - "faithfulness"
Cohesion: 0.67
Nodes (3): faithfulness(), Check that every circular id the answer cites (in square brackets) was actually…, test_faithfulness_scoring()

### Community 158 - "autoresearch.sh"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 159 - "Master Circular for Mutual Funds (2026)"
Cohesion: 0.40
Nodes (5): Master Circular for Mutual Funds (2026), Circular on Development of Passive Funds, Extension of timelines for submission of offsite inspection data (Mutual Funds), SEBI (Mutual Funds) Regulations, 1996, SEBI (Mutual Funds) Regulations, 2026

### Community 160 - "main"
Cohesion: 0.50
Nodes (3): eligible(), main(), SPIKE — throwaway, not preregistered. Answers one question before any R6 design…

### Community 163 - "validate_golden.py"
Cohesion: 0.60
Nodes (4): check_gate(), check_golden_set(), main(), Pre-commit validator for golden_v7 gate. Checks: 1. gate_v7.json exists and is…

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
- **62 isolated node(s):** `HF_HUB_DISABLE_XET`, `OMP_NUM_THREADS`, `PYTHONPATH`, `PYTORCH_ENABLE_MPS_FALLBACK`, `SEBI_RAG_EVAL_GENERATOR` (+57 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `sebi_rag/verify_master.py`, `test_injection.py`, `eval_harness.py`, `test_context_headers.py`, `test_paraphrase_rescue.py`, `test_context_recall.py`, `main`, `load_golden`, `test_attribution.py`, `RAGPipeline`, `test_spaces.py`, `answer_with_abstention`, `measure_temporal_accuracy`, `segment.py`, `test_spaces_app.py`, `load_circulars`, `HybridRetriever`, `benchmark.py`, `generate.py`, `test_selective_citations.py`, `hierarchical_chunk`, `test_rerank_set_encoder.py`, `test_rerank_jina_v3.py`, `test_pipeline.py`, `test_hyde.py`, `consolidation_edges`, `validate_golden_v7`, `test_lineage.py`, `build_spaces_pipeline`, `test_expand.py`, `Qwen3MLXReranker`, `read_trec_run`, `.query`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `Chunk`, `eval_harness.py`, `sebi_rag/eval_asof.py`, `MeasureResult`, `benchmark.py`, `test_paraphrase_rescue.py`, `test_api.py`, `load_golden`, `hybrid_gate_sweep.py`, `_bootstrap_ci`, `settings.py`, `consolidation_edges`, `test_eval_harness_v7.py`, `test_lineage.py`, `Embedder`, `answer_with_abstention`, `build_spaces_pipeline`, `hierarchical_chunk`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `pick_device()` connect `test_attribution.py` to `api.py`, `test_api.py`, `test_finetune_train_lora.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 68 inferred relationships involving `Chunk` (e.g. with `dataset_quality()` and `NLIAttributionScorer`) actually correct?**
  _`Chunk` has 68 INFERRED edges - model-reasoned connections that need verification._
- **Are the 47 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `main()`) actually correct?**
  _`RAGPipeline` has 47 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `HybridRetriever` (e.g. with `main()` and `main()`) actually correct?**
  _`HybridRetriever` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `Settings` (e.g. with `main()` and `main()`) actually correct?**
  _`Settings` has 49 INFERRED edges - model-reasoned connections that need verification._