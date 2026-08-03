# Graph Report - .  (2026-08-03)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2002 nodes · 4302 edges · 116 communities (95 shown, 21 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 262 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d9b0cb12`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- scrape_sebi.py
- export_datasets.py
- test_spaces.py
- test_golden_v7_agreement.py
- telemetry_engine.py
- test_golden_v7_packet.py
- HashEmbedder
- test_regulations.py
- RAGPipeline
- SpladeIndex
- lineage.py
- test_golden_v7_gate.py
- backfill_escalations.py
- context_headers.py
- extract_citations
- test_reg_lineage.py
- test_dataset_cards.py
- Chunk
- derive_validity
- benchmark.py
- test_golden_v7_gemini.py
- test_expand.py
- test_export_datasets.py
- sebi_rag/eval_asof.py
- test_api.py
- extract_misses.py
- gemini_adjudicate.py
- .load
- test_lineage.py
- ingest_pdf.py
- hierarchical_chunk
- test_golden_v7_local.py
- answer_with_abstention
- eval_harness.py
- Lineage
- parse_meta
- test_scrape_sebi.py
- consolidation_edges
- test_export_integration.py
- local_adjudicate.py
- TestHelpers
- validate_golden_v7
- test_gate.py
- test_scrape_regulations.py
- test_hyde.py
- test_app_zerogpu.py
- pick_device
- test_ingest_refs.py
- MeasureResult
- Qwen3MLXReranker
- clopper_pearson_ci
- LexicalReranker
- test_push_datasets.py
- reg_display_name
- test_audit_reg_edges.py
- test_ui.py
- main
- normalize_circular_number
- paired_delta
- Handler
- audit_reg_edges.py
- adjudicate_draft.py
- corpus_spaces.py
- test_eval_harness_v7.py
- bootstrap_ci
- trace_failure.py
- adjudicate
- test_golden_v7_resolver.py
- measure_supersession_precision
- test_build_reg_edges.py
- test_measure.py
- test_injection.py
- build_regulatory_index
- measure.py
- measure_parsing_latency
- run_all_metrics
- stats.py
- run.sh
- canary.sh
- seed_v7.py
- refresh.sh
- measure_mrr
- measure_retrieval_recall
- measure_temporal_accuracy
- test_app_asof.py
- test_benchmark.py
- main
- rescore_runs.py
- per_query_recall
- annotate_corpus
- autoresearch.sh
- main
- demote_superseded
- Golden v7 Human Packet
- deploy_space.py
- discover.sh
- _norm_ws
- upload_spaces_index.py
- measure.sh
- run_ops.sh
- build_golden.py
- notify.sh
- start_phoenix.sh
- mc_topic
- _paragraphs
- conftest.py
- Master Appendix (Mutual Funds)
- test_every_alias_target_is_in_force_or_has_a_succession_entry
- SEBI Master Circular CIR/DNPD/1/2012
- Optimize Slash Command
- Seen Circular IDs
- sebi-rag
- Hugging Face Spaces Requirements
- Master Appendix (Depository)
- SEBI Regulations Listing

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 88 edges
2. `RAGPipeline` - 56 edges
3. `hierarchical_chunk()` - 45 edges
4. `HashEmbedder` - 42 edges
5. `ExtractiveStubGenerator` - 40 edges
6. `CircularMeta` - 39 edges
7. `Lineage` - 33 edges
8. `build_lineage()` - 32 edges
9. `LexicalReranker` - 29 edges
10. `MeasureResult` - 26 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py
- `run_query_spaces()` --calls--> `_citation_meta()`  [INFERRED]
  app.py → src/sebi_rag/api.py
- `test_candidate_miss_when_relevant_doc_absent()` --calls--> `classify_query()`  [INFERRED]
  tests/test_extract_misses.py → scripts/analysis/extract_misses.py
- `test_doc_matching_is_normalized()` --calls--> `classify_query()`  [INFERRED]
  tests/test_extract_misses.py → scripts/analysis/extract_misses.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **SEBI Regulatory Framework** — sebi_ho_afd_pod2_i_2703_2026, sebi_ho_mrd_tpd_cir_p_2025_122, cir_dnpd_1_2012, tests_fixtures_regulation_listing [INFERRED 0.90]

## Communities (116 total, 21 thin omitted)

### Community 0 - "scrape_sebi.py"
Cohesion: 0.05
Nodes (60): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+52 more)

### Community 1 - "export_datasets.py"
Cohesion: 0.06
Nodes (70): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+62 more)

### Community 2 - "test_spaces.py"
Cohesion: 0.05
Nodes (47): build_ui(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only). Gradio SDK…, Normalise the optional as-of date field: empty -> None, else strict ISO YYYY-…, run_query_spaces(), warm_up_gpu(), GPU, Emit one JSON line listing SEBI circulars newer than previously seen. Uses a… (+39 more)

### Community 3 - "test_golden_v7_agreement.py"
Cohesion: 0.07
Nodes (62): apply(), _body(), _claude_accuracy_ci(), cohen_kappa(), decide(), _label(), _literals_by_row(), _llm_annotator() (+54 more)

### Community 4 - "telemetry_engine.py"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 5 - "test_golden_v7_packet.py"
Cohesion: 0.07
Nodes (52): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+44 more)

### Community 6 - "HashEmbedder"
Cohesion: 0.09
Nodes (39): HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable…, CircularMeta, _CannedGenerator, _distinct_pipeline(), test_run_pipeline_cases_pass_and_avoid(), _HallucinatingGenerator, test_pipeline_flags_hallucinated_citation() (+31 more)

### Community 7 - "test_regulations.py"
Cohesion: 0.06
Nodes (45): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus., _alias_keys(), derive_regulatory_basis(), _jaccard(), load_regulations(), name_tokens() (+37 more)

### Community 8 - "RAGPipeline"
Cohesion: 0.11
Nodes (47): get_pipeline(), Cache one pipeline per mode; both share retriever/reranker/lineage., BaseModel, Build the full pipeline with real models., real_pipeline(), main(), main(), smoke_pipeline() (+39 more)

### Community 9 - "SpladeIndex"
Cohesion: 0.07
Nodes (28): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.…, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+20 more)

### Community 10 - "lineage.py"
Cohesion: 0.10
Nodes (22): Benchmark MLX generators on the golden set: faithfulness, groundedness,…, Retrieval-only benchmark with TREC runfile and reproducibility metadata. Use…, Build the dense+sparse index once and persist it (run after corpus changes).…, Calibrate top_k and the abstention threshold against the citation-precision…, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the…, ADR-002 follow-up: compare the production subject-sim gate against the SECTION-…, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.… (+14 more)

### Community 11 - "test_golden_v7_gate.py"
Cohesion: 0.08
Nodes (40): Emit one JSON line of retrieval/citation/abstention metrics using the persisted…, derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the…, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,… (+32 more)

### Community 12 - "backfill_escalations.py"
Cohesion: 0.09
Nodes (38): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+30 more)

### Community 13 - "context_headers.py"
Cohesion: 0.08
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 14 - "extract_citations"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 15 - "test_reg_lineage.py"
Cohesion: 0.14
Nodes (31): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+23 more)

### Community 16 - "test_dataset_cards.py"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 17 - "Chunk"
Cohesion: 0.09
Nodes (15): Generator, _grounded_prompt(), Judge, _judge_prompt(), _judge_prompt_identify(), MLXJudge, Protocol, v2 protocol: closed-set identification instead of yes/no judgment. Naming which… (+7 more)

### Community 18 - "derive_validity"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation. Locked…, Validity of one circular from the tiered edge list (any scope: the function…, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 19 - "benchmark.py"
Cohesion: 0.14
Nodes (27): beir_corpus_rows(), beir_query_rows(), build_golden_v6(), dir_fingerprint(), enrich_golden_item(), export_beir(), git_commit(), Any (+19 more)

### Community 20 - "test_golden_v7_gemini.py"
Cohesion: 0.12
Nodes (26): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply… (+18 more)

### Community 21 - "test_expand.py"
Cohesion: 0.09
Nodes (23): main(), mrr(), ndcg_at_k(), Sweep RRF k_const values on the golden set. No index rebuild needed., recall_at_k(), expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and… (+15 more)

### Community 22 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 23 - "sebi_rag/eval_asof.py"
Cohesion: 0.13
Nodes (26): AsofCaseResult, build_report(), load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Aggregate case results with an exact confidence interval. Pure function of the…, run_pipeline_cases() (+18 more)

### Community 24 - "test_api.py"
Cohesion: 0.09
Nodes (18): FastAPI, integration, _citation_meta(), create_app(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit,…, /ready should trigger pipeline build and return ready=true., _slow_pipeline(), _SlowGenerator (+10 more)

### Community 25 - "extract_misses.py"
Cohesion: 0.14
Nodes (23): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any… (+15 more)

### Community 26 - "gemini_adjudicate.py"
Cohesion: 0.11
Nodes (23): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec… (+15 more)

### Community 27 - ".load"
Cohesion: 0.09
Nodes (23): Embedder, ndarray, Protocol, _tokens(), DenseIndex, _doc_checksum(), ndarray, Path (+15 more)

### Community 28 - "test_lineage.py"
Cohesion: 0.12
Nodes (21): detect_relations(), detect_relations_ex(), Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window(), _lin_chain(), P2 lineage / supersession resolution tests., A circular that names another circular BEFORE the supersede trigger word must… (+13 more)

### Community 29 - "ingest_pdf.py"
Cohesion: 0.15
Nodes (19): Re-derive circular number + dates from each record's stored text and rewrite…, _existing_numbers(), extract_text(), ingest(), main(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars. Drop a circular PDF into data/raw/ and… (+11 more)

### Community 30 - "hierarchical_chunk"
Cohesion: 0.18
Nodes (17): load_circulars(), Path, hierarchical_chunk(), Document -> section -> paragraph chunks with stable IDs. A "section" is…, _pipeline(), _body(), Chunker (segment.hierarchical_chunk) behaviour. Regression guard for the "5.…, Chunk text is 'breadcrumb-header\\nbody'; return the body. (+9 more)

### Community 31 - "test_golden_v7_local.py"
Cohesion: 0.15
Nodes (19): _extract_text(), Qwen-family models may emit <think>...</think> reasoning as inline text,…, Anthropic Messages response -> reply text: concatenates `text` content blocks,…, _strip_thinking(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external…, Five pilot rows from five strata measure more than five from one - the gemini…, Vote records must say annotator "qwen" (never reuse "gemini" - the agreement… (+11 more)

### Community 32 - "answer_with_abstention"
Cohesion: 0.16
Nodes (18): Answer, answer_with_abstention(), faithfulness(), _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain. Uses…, Check that every circular id the answer cites (in square brackets) was actually…, Map any cited circular that is superseded -> the circular(s) superseding it.…, superseded_citations() (+10 more)

### Community 33 - "eval_harness.py"
Cohesion: 0.16
Nodes (16): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,…, evaluate(), _aggregate() (+8 more)

### Community 34 - "Lineage"
Cohesion: 0.24
Nodes (7): Lineage, Path, Connected component over supersedes/superseded_by (both tiers)., The circular in this family that governs on date as_of (ISO), or None when…, test_lineage_load_old_file_defaults_empty_edges(), test_lineage_save_load_roundtrip(), test_lineage_save_load_roundtrips_edges()

### Community 35 - "parse_meta"
Cohesion: 0.15
Nodes (17): Pattern, _iso_date(), _labeled_date(), parse_meta(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash… (+9 more)

### Community 36 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 37 - "consolidation_edges"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans…, _master(), test_annotate_idempotent() (+7 more)

### Community 38 - "test_export_integration.py"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 39 - "local_adjudicate.py"
Cohesion: 0.19
Nodes (15): Transient-failure predicate for the real Gemini call: rate limiting (429) and…, Same per-row deterministic shuffle as make_packet.py's write_packet:…, _should_retry(), _shuffled_candidates(), _current_model(), main(), pilot(), _pilot_ids() (+7 more)

### Community 40 - "TestHelpers"
Cohesion: 0.16
Nodes (9): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict., When torch+MPS available, returns memory stats dict. (+1 more)

### Community 41 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 42 - "test_gate.py"
Cohesion: 0.19
Nodes (14): parse_excerpt_choice(), parse_yes_no(), True iff the reply names a valid excerpt number. 'none' or anything unparseable…, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the gate…, _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts() (+6 more)

### Community 44 - "test_hyde.py"
Cohesion: 0.18
Nodes (10): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —…, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_output_truncated_to_max_chars() (+2 more)

### Community 45 - "test_app_zerogpu.py"
Cohesion: 0.14
Nodes (13): app_module(), fixture, Regression coverage for the ZeroGPU-hardware workaround in app.py. Background:…, Inject a fake `spaces` module so app.py's `import spaces` succeeds offline, and…, Static guard: if `import spaces` or the `@spaces.GPU` decorator is ever…, It must stay dead code: calling it would request a real ZeroGPU allocation (and…, The functions actually on the request path (get_pipeline, run_query_spaces)…, `hardware:` in README-spaces.md is not a documented Spaces config key (only… (+5 more)

### Community 47 - "pick_device"
Cohesion: 0.20
Nodes (11): pick_device(), Device + precision selection for Apple-Silicon inference. Centralizes the…, Resolve the compute device. A truthy explicit `pref` ("mps"/"cpu"/"cuda") wins.…, fp16 only on GPU-class devices; never on cpu. bf16 is never returned here by…, should_use_fp16(), Device + fp16 policy selection (no real torch/mps required)., test_pick_device_auto_cpu_when_no_mps(), test_pick_device_auto_mps_when_available() (+3 more)

### Community 48 - "test_ingest_refs.py"
Cohesion: 0.15
Nodes (11): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_fulltext_fallback_returns_earliest_body_reference() (+3 more)

### Community 49 - "MeasureResult"
Cohesion: 0.24
Nodes (6): measure_context_precision(), MeasureReport, MeasureResult, Fraction of top-k chunks from relevant circulars. Unlike recall@k (which is…, TestContextPrecision, TestDataClasses

### Community 50 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 51 - "clopper_pearson_ci"
Cohesion: 0.24
Nodes (4): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 52 - "LexicalReranker"
Cohesion: 0.20
Nodes (15): Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)…, smoke_pipeline(), assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, LexicalReranker, Deterministic query-coverage reranker (test/fallback). Score = fraction of…, One gold doc with `n` chunks that ALL contain the word "broker", so a… (+7 more)

### Community 53 - "test_push_datasets.py"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default:…, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 54 - "reg_display_name"
Cohesion: 0.22
Nodes (12): Human-readable regulation name. Year disambiguates same-short_name repeal pairs…, reg_display_name(), build_ui(), _empty_outputs(), _parse_as_of(), Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO YYYY-MM-DD.…, SSRF guard: reject URLs pointing to private/internal/reserved addresses. Blocks… (+4 more)

### Community 55 - "test_audit_reg_edges.py"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 56 - "test_ui.py"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 57 - "main"
Cohesion: 0.24
Nodes (10): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card() (+2 more)

### Community 58 - "normalize_circular_number"
Cohesion: 0.18
Nodes (7): main(), Repair the 6 records whose body text was overwritten with one shared circular's…, normalize_circular_number(), Canonical COMPARISON key for a circular number: strip whitespace and trailing…, test_dedup_uses_normalized_numbers(), The repair map must name a real orphan PDF that parses to the circular_number…, test_numbers_normalize_distinctly()

### Community 59 - "paired_delta"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries. Returns mean_b -…, Randomization p-values use the (count+1)/(n+1) estimator, so a p-value of…, One query flipping out of 56 is exactly the iv9-style verdict: the…, TestPairedDelta

### Community 60 - "Handler"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 61 - "audit_reg_edges.py"
Cohesion: 0.29
Nodes (10): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+2 more)

### Community 62 - "adjudicate_draft.py"
Cohesion: 0.29
Nodes (10): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+2 more)

### Community 63 - "corpus_spaces.py"
Cohesion: 0.29
Nodes (10): _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path). Loads the…, One HF dataset config as plain dicts (network; cached by `datasets`)., Full-circular records (dicts) for build_lineage() — always the "corpus" config… (+2 more)

### Community 64 - "test_eval_harness_v7.py"
Cohesion: 0.49
Nodes (10): run_eval(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-…, _row(), test_as_of_is_passed_to_pipeline(), test_chunk_metrics_computed_for_span_rows(), test_gate_is_none_when_nothing_adjudicated(), test_gate_subreport_covers_only_adjudicated() (+2 more)

### Community 65 - "bootstrap_ci"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 66 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 67 - "adjudicate"
Cohesion: 0.22
Nodes (10): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt) -> str`…, Scans the per-row cache for `ids` and returns the ones flagged parse_error:…, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct from a well-…, Defensive: an id that was never adjudicated (no cache file at all) is not…, test_adjudicate_marks_parse_error_for_garbled_abstain_protocol_reply() (+2 more)

### Community 68 - "test_golden_v7_resolver.py"
Cohesion: 0.38
Nodes (9): chunks_by_doc(), _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through(), test_qrels_span_rows_get_grade_2(), test_resolves_normalized_whitespace_quote(), test_unresolvable_quote_returns_empty() (+1 more)

### Community 69 - "measure_supersession_precision"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 70 - "test_build_reg_edges.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 71 - "test_measure.py"
Cohesion: 0.28
Nodes (5): main(), metrics_to_markdown(), Format results as a markdown table., Unit tests for sebi_rag.measure — automated metric collection., TestCLI

### Community 72 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 73 - "build_regulatory_index"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 74 - "measure.py"
Cohesion: 0.39
Nodes (6): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), Automated metric collection for the SEBI Circular RAG pipeline. Six on-demand…, test_retrieval_metrics()

### Community 75 - "measure_parsing_latency"
Cohesion: 0.32
Nodes (5): measure_parsing_latency(), Path, Measure PDF ingestion throughput (chars/sec, ms/PDF). Samples 20 PDFs…, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 76 - "run_all_metrics"
Cohesion: 0.29
Nodes (4): Run all (or specified) metrics sequentially., run_all_metrics(), Empty metrics list is falsy → defaults to ALL_METRICS., TestRegistry

### Community 77 - "stats.py"
Cohesion: 0.25
Nodes (5): BootstrapCI, PairedResult, Uncertainty quantification for benchmark runs. The golden set is n=56…, True when the randomization test rejects at 1 - confidence AND the paired…, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 78 - "run.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 79 - "canary.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 80 - "seed_v7.py"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 81 - "refresh.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 82 - "measure_mrr"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level. For each query, RR = 1/rank of first…, TestMRR

### Community 83 - "measure_retrieval_recall"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 84 - "measure_temporal_accuracy"
Cohesion: 0.43
Nodes (3): measure_temporal_accuracy(), Measure fraction of as_of queries returning correct pre-supersession circular…, TestTemporalAccuracy

### Community 85 - "test_app_asof.py"
Cohesion: 0.29
Nodes (3): app_module(), fixture, As-of date plumbing in the Spaces UI (app.py).

### Community 86 - "test_benchmark.py"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

### Community 87 - "main"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl()

### Community 88 - "rescore_runs.py"
Cohesion: 0.53
Nodes (5): _fmt(), main(), Path, Re-score archived benchmark runs with bootstrap CIs and paired significance.…, score_run()

### Community 89 - "per_query_recall"
Cohesion: 0.40
Nodes (3): per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.…, Ten chunks of one circular must not crowd the cutoff: the k applies to unique…

### Community 90 - "annotate_corpus"
Cohesion: 0.33
Nodes (4): annotate_corpus(), Update each corpus record's supersession_status + superseded_by + supersedes…, test_annotate_corpus_adds_master_fields_and_consolidates_edges(), test_annotate_corpus_writes_new_metadata_fields()

### Community 91 - "autoresearch.sh"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 92 - "main"
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 93 - "demote_superseded"
Cohesion: 0.50
Nodes (4): contexts_for(), demote_superseded(), Down-weight reranked (chunk, score) pairs from superseded circulars and re-…, test_demote_superseded_puts_in_force_on_top()

### Community 94 - "Golden v7 Human Packet"
Cohesion: 0.67
Nodes (3): Golden v7 Human Packet, SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026, SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122

### Community 97 - "_norm_ws"
Cohesion: 0.67
Nodes (3): _confirms_claude(), Does this external vote confirm claude's label, at PROVISION level? Amendment…, _norm_ws()

## Knowledge Gaps
- **39 isolated node(s):** `measure.sh script`, `autoresearch.sh script`, `PYTHONPATH`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `test_spaces.py`, `HashEmbedder`, `RAGPipeline`, `SpladeIndex`, `lineage.py`, `context_headers.py`, `benchmark.py`, `test_expand.py`, `.load`, `hierarchical_chunk`, `answer_with_abstention`, `validate_golden_v7`, `test_gate.py`, `test_hyde.py`, `Qwen3MLXReranker`, `LexicalReranker`, `main`, `corpus_spaces.py`, `test_golden_v7_resolver.py`, `test_injection.py`, `test_benchmark.py`, `demote_superseded`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `HashEmbedder`, `lineage.py`, `Chunk`, `benchmark.py`, `sebi_rag/eval_asof.py`, `test_api.py`, `.load`, `answer_with_abstention`, `eval_harness.py`, `Lineage`, `MeasureResult`, `LexicalReranker`, `main`, `test_eval_harness_v7.py`, `measure_supersession_precision`, `measure.py`, `measure_parsing_latency`, `run_all_metrics`, `measure_mrr`, `measure_retrieval_recall`, `measure_temporal_accuracy`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Why does `build_regulatory_index()` connect `build_regulatory_index` to `RAGPipeline`, `test_regulations.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `CitationMeta`) actually correct?**
  _`RAGPipeline` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `HashEmbedder` (e.g. with `_CannedGenerator` and `_SlowGenerator`) actually correct?**
  _`HashEmbedder` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `ExtractiveStubGenerator` (e.g. with `get_pipeline()` and `main()`) actually correct?**
  _`ExtractiveStubGenerator` has 14 INFERRED edges - model-reasoned connections that need verification._