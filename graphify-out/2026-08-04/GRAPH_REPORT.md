# Graph Report - SEBI circular RAG  (2026-08-03)

## Corpus Check
- 163 files · ~167,321 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2034 nodes · 4356 edges · 130 communities (106 shown, 24 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 304 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `741a854d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- export_datasets.py
- test_golden_v7_agreement.py
- lineage.py
- telemetry_engine.py
- test_golden_v7_packet.py
- test_regulations.py
- .load
- RAGPipeline
- HashEmbedder
- context_headers.py
- test_spaces.py
- extract_citations
- test_reg_lineage.py
- test_dataset_cards.py
- derive_validity
- hierarchical_chunk
- test_api.py
- backfill_escalations.py
- test_golden_v7_gemini.py
- HybridRetriever
- test_export_datasets.py
- sebi_rag/eval_asof.py
- Chunk
- build_lineage
- benchmark.py
- extract_misses.py
- LexicalReranker
- gemini_adjudicate.py
- eval_harness.py
- sebi_rag/verify_master.py
- ingest_pdf.py
- test_golden_v7_local.py
- answer_with_abstention
- test_gate.py
- parse_meta
- .load
- test_scrape_sebi.py
- splade_encoder.py
- TestHelpers
- consolidation_edges
- test_export_integration.py
- test_golden_v7_gate.py
- local_adjudicate.py
- Settings
- validate_golden_v7
- read_trec_run
- test_hyde.py
- test_scrape_regulations.py
- scrape_regulations.py
- scrape_sebi.py
- test_expand.py
- test_app_zerogpu.py
- pick_device
- test_ingest_refs.py
- MeasureResult
- Qwen3MLXReranker
- clopper_pearson_ci
- acquire_missing_pdfs.py
- test_push_datasets.py
- reg_display_name
- test_audit_reg_edges.py
- test_ui.py
- remap_doc_ids.py
- normalize_circular_number
- sweep_rrf_k.py
- resolve_chunk_spans
- paired_delta
- Handler
- audit_reg_edges.py
- adjudicate_draft.py
- test_eval_harness_v7.py
- bootstrap_ci
- app.py
- trace_failure.py
- floors_ok
- adjudicate
- load_golden
- detect_relations_ex
- measure_supersession_precision
- test_build_reg_edges.py
- derive_thresholds.py
- test_measure.py
- derive_floors
- test_injection.py
- build_regulatory_index
- test_acquire_missing.py
- measure.py
- run_all_metrics
- stats.py
- List of Circulars
- run.sh
- canary.sh
- main
- refresh.sh
- measure_mrr
- measure_parsing_latency
- measure_retrieval_recall
- measure_temporal_accuracy
- test_app_asof.py
- main
- rescore_runs.py
- autoresearch.sh
- main
- discover_new.py
- Golden v7 Human Packet
- deploy_space.py
- discover.sh
- upload_spaces_index.py
- measure.sh
- run_ops.sh
- notify.sh
- start_phoenix.sh
- conftest.py
- Master Appendix (Mutual Funds)
- test_every_alias_target_is_in_force_or_has_a_succession_entry
- SEBI Master Circular CIR/DNPD/1/2012
- Optimize Slash Command
- Seen Circular IDs
- Label Escalations
- sebi-rag
- Unresolved Regulations
- Hugging Face Spaces Requirements
- golden_v7/__init__.py
- Master Appendix (Depository)
- SEBI Regulations Listing
- _s_mc_no
- relabel_repooled.py
- .encode
- TestPerQueryRecall
- main

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
- `test_cohen_kappa_both_constant_and_identical_is_one()` --calls--> `cohen_kappa()`  [INFERRED]
  tests/test_golden_v7_agreement.py → scripts/golden_v7/agreement.py
- `test_cohen_kappa_empty_input_is_one()` --calls--> `cohen_kappa()`  [INFERRED]
  tests/test_golden_v7_agreement.py → scripts/golden_v7/agreement.py
- `test_cohen_kappa_identical_lists_is_one()` --calls--> `cohen_kappa()`  [INFERRED]
  tests/test_golden_v7_agreement.py → scripts/golden_v7/agreement.py
- `test_cohen_kappa_independent_looking_lists_is_low()` --calls--> `cohen_kappa()`  [INFERRED]
  tests/test_golden_v7_agreement.py → scripts/golden_v7/agreement.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **SEBI Regulatory Framework** — tests_fixtures_master_appendix_pre2015_sebi, tests_fixtures_master_appendix_pre2015_circulars, tests_fixtures_master_appendix_pre2015_communications [INFERRED 0.90]

## Communities (130 total, 24 thin omitted)

### Community 0 - "export_datasets.py"
Cohesion: 0.06
Nodes (70): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+62 more)

### Community 1 - "test_golden_v7_agreement.py"
Cohesion: 0.14
Nodes (20): _claude_accuracy_ci(), gwet_ac1(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation slic, Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a     prevalen (+12 more)

### Community 2 - "lineage.py"
Cohesion: 0.08
Nodes (32): Pool-width sweep (intervention #3): answer-level rescue rate vs reranker…, Benchmark MLX generators on the golden set: faithfulness, groundedness,…, Retrieval-only benchmark with TREC runfile and reproducibility metadata. Use…, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped…, Build the dense+sparse index once and persist it (run after corpus changes).…, Calibrate top_k and the abstention threshold against the citation-precision…, scripts/eval_asof.py, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the… (+24 more)

### Community 3 - "telemetry_engine.py"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 4 - "test_golden_v7_packet.py"
Cohesion: 0.07
Nodes (52): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+44 more)

### Community 5 - "test_regulations.py"
Cohesion: 0.06
Nodes (45): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus., _alias_keys(), derive_regulatory_basis(), _jaccard(), load_regulations(), name_tokens() (+37 more)

### Community 6 - ".load"
Cohesion: 0.12
Nodes (19): Embedder, Protocol, DenseIndex, _doc_checksum(), HybridRetriever, ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached embedding rows… (+11 more)

### Community 7 - "RAGPipeline"
Cohesion: 0.11
Nodes (37): BaseModel, Build the full pipeline with real models., real_pipeline(), main(), main(), main(), build_default_pipeline(), CitationMeta (+29 more)

### Community 8 - "HashEmbedder"
Cohesion: 0.10
Nodes (42): Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)…, smoke_pipeline(), smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable…, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., LexicalReranker (+34 more)

### Community 9 - "context_headers.py"
Cohesion: 0.08
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 10 - "test_spaces.py"
Cohesion: 0.07
Nodes (33): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only). Gradio SDK…, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict ISO YYYY-…, run_query_spaces(), warm_up_gpu() (+25 more)

### Community 11 - "extract_citations"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 12 - "test_reg_lineage.py"
Cohesion: 0.14
Nodes (31): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+23 more)

### Community 13 - "test_dataset_cards.py"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 14 - "derive_validity"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation. Locked…, Validity of one circular from the tiered edge list (any scope: the function…, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 15 - "hierarchical_chunk"
Cohesion: 0.14
Nodes (20): load_circulars(), Path, hierarchical_chunk(), Document -> section -> paragraph chunks with stable IDs. A "section" is…, test_real_corpus_loads_with_provenance_fields(), test_numeric_miner_requires_numeric_pattern(), test_paraphrase_skips_preamble_and_short_chunks(), _chunks() (+12 more)

### Community 16 - "test_api.py"
Cohesion: 0.10
Nodes (16): FastAPI, integration, _citation_meta(), create_app(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit,…, /ready should trigger pipeline build and return ready=true., test_auth_required_when_key_set(), test_bge_fp16_encode_is_normalized() (+8 more)

### Community 17 - "backfill_escalations.py"
Cohesion: 0.16
Nodes (22): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+14 more)

### Community 18 - "test_golden_v7_gemini.py"
Cohesion: 0.12
Nodes (26): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply… (+18 more)

### Community 19 - "HybridRetriever"
Cohesion: 0.11
Nodes (18): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, csr_matrix, Path, SPLADE learned-sparse retrieval leg (iv11). Non-destructive, opt-in third RRF…, SpladeIndex, _fake_encode(), _chunks() (+10 more)

### Community 20 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 21 - "sebi_rag/eval_asof.py"
Cohesion: 0.13
Nodes (27): sebi_rag/eval_asof.py, AsofCaseResult, build_report(), load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Aggregate case results with an exact confidence interval. Pure function of the… (+19 more)

### Community 22 - "Chunk"
Cohesion: 0.13
Nodes (13): Generator, Judge, _judge_prompt(), _judge_prompt_identify(), MLXJudge, Protocol, v2 protocol: closed-set identification instead of yes/no judgment. Naming which…, Deterministic groundedness judge on MLX (greedy decode, temp 0). Pass… (+5 more)

### Community 23 - "build_lineage"
Cohesion: 0.07
Nodes (39): annotate_corpus(), build_lineage(), _currency(), detect_relations(), detect_relations_ex(), Lineage, mc_topic(), Path (+31 more)

### Community 24 - "benchmark.py"
Cohesion: 0.14
Nodes (31): main(), main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), chunks_by_doc() (+23 more)

### Community 25 - "extract_misses.py"
Cohesion: 0.17
Nodes (18): classify_answer(), classify_query(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any…, Chunk IDs embed section headings containing spaces, so parse TREC fields… (+10 more)

### Community 26 - "LexicalReranker"
Cohesion: 0.23
Nodes (12): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, _norm_ws(), One gold doc with `n` chunks that ALL contain the word "broker", so a…, Regression (2026-07-25): a must_contain literal matching many gold-doc chunks…, _retriever(), _saturating_retriever() (+4 more)

### Community 27 - "gemini_adjudicate.py"
Cohesion: 0.11
Nodes (23): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec… (+15 more)

### Community 28 - "eval_harness.py"
Cohesion: 0.15
Nodes (19): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,…, evaluate(), Span {doc, quote} -> matching chunk ids (all overlap matches count). Legacy… (+11 more)

### Community 29 - "sebi_rag/verify_master.py"
Cohesion: 0.19
Nodes (21): sebi_rag/verify_master.py, diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13). Pure functions only:…, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows. (+13 more)

### Community 30 - "ingest_pdf.py"
Cohesion: 0.15
Nodes (19): Re-derive circular number + dates from each record's stored text and rewrite…, _existing_numbers(), extract_text(), ingest(), main(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars. Drop a circular PDF into data/raw/ and… (+11 more)

### Community 31 - "test_golden_v7_local.py"
Cohesion: 0.15
Nodes (19): _extract_text(), Qwen-family models may emit <think>...</think> reasoning as inline text,…, Anthropic Messages response -> reply text: concatenates `text` content blocks,…, _strip_thinking(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external…, Five pilot rows from five strata measure more than five from one - the gemini…, Vote records must say annotator "qwen" (never reuse "gemini" - the agreement… (+11 more)

### Community 32 - "answer_with_abstention"
Cohesion: 0.16
Nodes (16): parse_excerpt_choice(), parse_yes_no(), True iff the reply names a valid excerpt number. 'none' or anything unparseable…, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the gate…, _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts() (+8 more)

### Community 33 - "test_gate.py"
Cohesion: 0.13
Nodes (25): decide(), Spec sec7 promotion rules for one row.      `votes_by_annotator` is this row's v, Abstain rows have no explicit claude vote at all (Task 8 never judged     them), Both externals independently think something DOES govern (disputing     the auth, The LLM leg is whichever single non-claude/non-human annotator voted -     "qwen, External marked claude's chunk governing plus extras: claude's label     is conf, The abstain protocol can never emit non-empty governing (no letters     are offe, Two externals both replying NONE on an answerable row must queue,     not flip: (+17 more)

### Community 34 - "parse_meta"
Cohesion: 0.15
Nodes (17): Pattern, _iso_date(), _labeled_date(), parse_meta(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash… (+9 more)

### Community 35 - ".load"
Cohesion: 0.22
Nodes (15): _as_bool(), _get(), Path, Settings.load() plus the [spaces] table as settings.spaces.* Load order per…, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default may…, _clear(), Settings: defaults, config.toml, and env-override precedence. (+7 more)

### Community 36 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 37 - "splade_encoder.py"
Cohesion: 0.21
Nodes (14): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions`     (keyed, _min_agreement_fixture(), Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7): Cohen's, _same_provision_fixture(), test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only() (+6 more)

### Community 38 - "TestHelpers"
Cohesion: 0.15
Nodes (10): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Path, Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict. (+2 more)

### Community 39 - "consolidation_edges"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans…, _master(), test_annotate_idempotent() (+7 more)

### Community 40 - "test_export_integration.py"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 41 - "test_golden_v7_gate.py"
Cohesion: 0.26
Nodes (13): Path, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,…, select_golden(), _gate_file(), Offline tests for the golden-v7 CI gate flip (spec 2026-07-23 sec 8). The gate…, A corrupt gate file must not arm the gate, and must not crash CI either - fall…, test_armed_gate_selects_v7(), test_below_threshold_falls_back_to_v5() (+5 more)

### Community 42 - "local_adjudicate.py"
Cohesion: 0.19
Nodes (15): Transient-failure predicate for the real Gemini call: rate limiting (429) and…, Same per-row deterministic shuffle as make_packet.py's write_packet:…, _should_retry(), _shuffled_candidates(), _current_model(), main(), pilot(), _pilot_ids() (+7 more)

### Community 43 - "Settings"
Cohesion: 0.29
Nodes (10): _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path). Loads the…, One HF dataset config as plain dicts (network; cached by `datasets`)., Full-circular records (dicts) for build_lineage() — always the "corpus" config… (+2 more)

### Community 44 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 45 - "read_trec_run"
Cohesion: 0.36
Nodes (4): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), The archived runfiles embed section headings in the doc id., TestReadTrecRun

### Community 46 - "test_hyde.py"
Cohesion: 0.17
Nodes (11): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —…, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_none_and_empty_hyde_are_identical_to_baseline() (+3 more)

### Community 48 - "scrape_regulations.py"
Cohesion: 0.20
Nodes (14): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY).…, (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'. Takes the LAST bracket group…, _record() (+6 more)

### Community 49 - "scrape_sebi.py"
Cohesion: 0.26
Nodes (14): discover(), _listing_url(), main(), _page(), _parse_date(), parse_rows(), pdf_url_for(), date (+6 more)

### Community 50 - "test_expand.py"
Cohesion: 0.18
Nodes (16): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and…, _chunk(), Query-side lexical expansion (intervention #2, glossary variant).…, test_all_five_sparse_failure_queries_expand(), test_expanded_sparse_query_hits_statutory_chunk(), test_lay_term_gains_statutory_synonym() (+8 more)

### Community 51 - "test_app_zerogpu.py"
Cohesion: 0.14
Nodes (13): app_module(), fixture, Regression coverage for the ZeroGPU-hardware workaround in app.py. Background:…, Inject a fake `spaces` module so app.py's `import spaces` succeeds offline, and…, Static guard: if `import spaces` or the `@spaces.GPU` decorator is ever…, It must stay dead code: calling it would request a real ZeroGPU allocation (and…, The functions actually on the request path (get_pipeline, run_query_spaces)…, `hardware:` in README-spaces.md is not a documented Spaces config key (only… (+5 more)

### Community 52 - "pick_device"
Cohesion: 0.20
Nodes (11): pick_device(), Device + precision selection for Apple-Silicon inference. Centralizes the…, Resolve the compute device. A truthy explicit `pref` ("mps"/"cpu"/"cuda") wins.…, fp16 only on GPU-class devices; never on cpu. bf16 is never returned here by…, should_use_fp16(), Device + fp16 policy selection (no real torch/mps required)., test_pick_device_auto_cpu_when_no_mps(), test_pick_device_auto_mps_when_available() (+3 more)

### Community 53 - "test_ingest_refs.py"
Cohesion: 0.15
Nodes (11): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_fulltext_fallback_returns_earliest_body_reference() (+3 more)

### Community 54 - "MeasureResult"
Cohesion: 0.11
Nodes (15): main(), metrics_to_markdown(), Format results as a markdown table., measure_context_precision(), MeasureReport, MeasureResult, Fraction of top-k chunks from relevant circulars. Unlike recall@k (which is…, Run all (or specified) metrics sequentially. (+7 more)

### Community 55 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 56 - "clopper_pearson_ci"
Cohesion: 0.24
Nodes (4): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 57 - "acquire_missing_pdfs.py"
Cohesion: 0.26
Nodes (12): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+4 more)

### Community 58 - "test_push_datasets.py"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default:…, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 59 - "reg_display_name"
Cohesion: 0.22
Nodes (12): Human-readable regulation name. Year disambiguates same-short_name repeal pairs…, reg_display_name(), build_ui(), _empty_outputs(), _parse_as_of(), Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO YYYY-MM-DD.…, SSRF guard: reject URLs pointing to private/internal/reserved addresses. Blocks… (+4 more)

### Community 60 - "test_audit_reg_edges.py"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 61 - "test_ui.py"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 62 - "remap_doc_ids.py"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

### Community 63 - "normalize_circular_number"
Cohesion: 0.18
Nodes (7): main(), Repair the 6 records whose body text was overwritten with one shared circular's…, normalize_circular_number(), Canonical COMPARISON key for a circular number: strip whitespace and trailing…, test_dedup_uses_normalized_numbers(), The repair map must name a real orphan PDF that parses to the circular_number…, test_numbers_normalize_distinctly()

### Community 64 - "sweep_rrf_k.py"
Cohesion: 0.24
Nodes (14): answer_with_abstention(), faithfulness(), _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain. Uses…, Check that every circular id the answer cites (in square brackets) was actually…, _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons,…, test_advisory_draft_on_gate_failure_only_when_requested() (+6 more)

### Community 65 - "resolve_chunk_spans"
Cohesion: 0.42
Nodes (8): _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through(), test_qrels_span_rows_get_grade_2(), test_resolves_normalized_whitespace_quote(), test_unresolvable_quote_returns_empty(), test_validator_flags_unresolvable_quote_when_chunks_given()

### Community 66 - "paired_delta"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries. Returns mean_b -…, Randomization p-values use the (count+1)/(n+1) estimator, so a p-value of…, One query flipping out of 56 is exactly the iv9-style verdict: the…, TestPairedDelta

### Community 67 - "Handler"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 68 - "audit_reg_edges.py"
Cohesion: 0.29
Nodes (10): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+2 more)

### Community 69 - "adjudicate_draft.py"
Cohesion: 0.29
Nodes (10): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+2 more)

### Community 70 - "test_eval_harness_v7.py"
Cohesion: 0.42
Nodes (11): run_eval(), test_eval_harness_metric_suite(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-…, _row(), test_as_of_is_passed_to_pipeline(), test_chunk_metrics_computed_for_span_rows(), test_gate_is_none_when_nothing_adjudicated() (+3 more)

### Community 71 - "bootstrap_ci"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 72 - "app.py"
Cohesion: 0.18
Nodes (10): main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.…, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights., splade_pool(), SpladeEncoder (+2 more)

### Community 73 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 74 - "floors_ok"
Cohesion: 0.33
Nodes (10): main(), Rewrite golden_v7 doc references after the corpus renumbering (2026-07-25…, remap(), Doc-id remapping after the 2026-07-25 corpus renumbering (Task 4)., _row(), test_input_rows_are_not_mutated(), test_matching_is_normalization_insensitive(), test_remaps_must_not_cite() (+2 more)

### Community 75 - "adjudicate"
Cohesion: 0.22
Nodes (10): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt) -> str`…, Scans the per-row cache for `ids` and returns the ones flagged parse_error:…, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct from a well-…, Defensive: an id that was never adjudicated (no cache file at all) is not…, test_adjudicate_marks_parse_error_for_garbled_abstain_protocol_reply() (+2 more)

### Community 76 - "load_golden"
Cohesion: 0.28
Nodes (6): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, load_golden(), Path, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 77 - "detect_relations_ex"
Cohesion: 0.18
Nodes (11): derive_floors(), metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, The floor is a bootstrap lower bound minus a cushion, never the mean. Gating on…, A metric nobody scored must not be floored at 0 - a 0 floor is not a gate, it…, It trades off against citation_recall, so flooring both pins the retriever's…, derive_floors emits gate-report metric names, not the internal score_row names…, test_citation_precision_is_reported_but_never_floored(), test_derive_floors_skips_metrics_with_no_scored_queries() (+3 more)

### Community 78 - "measure_supersession_precision"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 79 - "test_build_reg_edges.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 80 - "derive_thresholds.py"
Cohesion: 0.27
Nodes (10): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote}     spans, look, _resolve_governing_spans(), _pool(), Amendment 2026-07-26 (user-approved): the promotion unit is the     PROVISION, n, test_decide_same_provision_other_chunk_promotes_with_pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool() (+2 more)

### Community 81 - "test_measure.py"
Cohesion: 0.20
Nodes (10): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using     the, Does this external vote confirm claude's label, at PROVISION level?      Amendme, Different chunk copies of the same quoted provision agree at provision     level, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction(), test_provision_agree_disjoint_without_pool_is_false() (+2 more)

### Community 82 - "derive_floors"
Cohesion: 0.20
Nodes (9): floors_ok(), Which golden set gates CI, and whether its adjudicated subset clears the…, True iff every floor's metric is present in `report_gate` and meets it. Missing…, A floor naming a metric the report does not carry cannot be shown to hold, so…, test_floors_not_ok_when_one_metric_is_below(), test_floors_ok_is_inclusive_at_the_boundary(), test_floors_ok_when_every_metric_meets_its_floor(), test_missing_metric_fails_closed() (+1 more)

### Community 83 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 84 - "build_regulatory_index"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 86 - "measure.py"
Cohesion: 0.39
Nodes (6): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), Automated metric collection for the SEBI Circular RAG pipeline. Six on-demand…, test_retrieval_metrics()

### Community 87 - "run_all_metrics"
Cohesion: 0.28
Nodes (7): _doc(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, One scoring path shared by `eval_json.py` (which measures) and…, Score one golden row through the production-shaped pipeline. Returns per-row…, Per-row records -> metric -> score vector, skipping rows where the metric was…, score_row(), vectors()

### Community 88 - "stats.py"
Cohesion: 0.25
Nodes (5): BootstrapCI, PairedResult, Uncertainty quantification for benchmark runs. The golden set is n=56…, True when the randomization test rejects at 1 - confidence AND the paired…, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 89 - "List of Circulars"
Cohesion: 0.25
Nodes (8): CIR/MRD/DP/19/2010, List of Circulars, List of Communications, MRD/DoP/Dep/Cir-29/2004, MRD/DoP/MAS – OW/16723/2010, Securities and Exchange Board of India, SEBI/MRD/SE/DEP/Cir-4/2005, SMDRP/NSDL/3055/1998

### Community 90 - "run.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 91 - "canary.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 92 - "main"
Cohesion: 0.31
Nodes (8): main(), mrr(), ndcg_at_k(), Sweep RRF k_const values on the golden set. No index rebuild needed., recall_at_k(), Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 93 - "refresh.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 94 - "measure_mrr"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level. For each query, RR = 1/rank of first…, TestMRR

### Community 95 - "measure_parsing_latency"
Cohesion: 0.38
Nodes (4): measure_parsing_latency(), Measure PDF ingestion throughput (chars/sec, ms/PDF). Samples 20 PDFs…, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 96 - "measure_retrieval_recall"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 97 - "measure_temporal_accuracy"
Cohesion: 0.43
Nodes (3): measure_temporal_accuracy(), Measure fraction of as_of queries returning correct pre-supersession circular…, TestTemporalAccuracy

### Community 98 - "test_app_asof.py"
Cohesion: 0.29
Nodes (3): app_module(), fixture, As-of date plumbing in the Spaces UI (app.py).

### Community 99 - "main"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl()

### Community 100 - "rescore_runs.py"
Cohesion: 0.53
Nodes (5): _fmt(), main(), Path, Re-score archived benchmark runs with bootstrap CIs and paired significance.…, score_run()

### Community 101 - "autoresearch.sh"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 102 - "main"
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 104 - "Golden v7 Human Packet"
Cohesion: 0.67
Nodes (3): Golden v7 Human Packet, SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026, SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122

### Community 119 - "sebi-rag"
Cohesion: 0.25
Nodes (8): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw     element, The kappa base-rate paradox: one label dominates, raw agreement is high,     yet, test_cohen_kappa_both_constant_and_identical_is_one(), test_cohen_kappa_empty_input_is_one(), test_cohen_kappa_identical_lists_is_one(), test_cohen_kappa_independent_looking_lists_is_low(), test_gwet_ac1_exceeds_kappa_on_skewed_high_agreement()

### Community 125 - "_s_mc_no"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

### Community 126 - "relabel_repooled.py"
Cohesion: 0.43
Nodes (6): _body(), main(), _norm(), pick(), Label the 7 rows re-pooled after the assemble_pool fix (2026-07-25 remediation…, (candidate, quote) pairs for this row: the answer_contains carrier first, then…

### Community 129 - "main"
Cohesion: 1.00
Nodes (3): _load_items(), main(), Path

## Knowledge Gaps
- **46 isolated node(s):** `measure.sh script`, `autoresearch.sh script`, `PYTHONPATH`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `lineage.py`, `.load`, `RAGPipeline`, `HashEmbedder`, `context_headers.py`, `test_spaces.py`, `hierarchical_chunk`, `HybridRetriever`, `benchmark.py`, `eval_harness.py`, `answer_with_abstention`, `Settings`, `validate_golden_v7`, `test_hyde.py`, `test_expand.py`, `Qwen3MLXReranker`, `remap_doc_ids.py`, `sweep_rrf_k.py`, `test_injection.py`, `_s_mc_no`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `TestPerQueryRecall`, `lineage.py`, `.load`, `HashEmbedder`, `test_api.py`, `sebi_rag/eval_asof.py`, `Chunk`, `build_lineage`, `benchmark.py`, `eval_harness.py`, `read_trec_run`, `MeasureResult`, `test_eval_harness_v7.py`, `measure_supersession_precision`, `measure.py`, `measure_mrr`, `measure_parsing_latency`, `measure_retrieval_recall`, `measure_temporal_accuracy`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `sebi_rag/eval_asof.py` connect `sebi_rag/eval_asof.py` to `lineage.py`, `RAGPipeline`, `build_lineage`, `stats.py`, `clopper_pearson_ci`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `CitationMeta`) actually correct?**
  _`RAGPipeline` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `HashEmbedder` (e.g. with `_CannedGenerator` and `_SlowGenerator`) actually correct?**
  _`HashEmbedder` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `ExtractiveStubGenerator` (e.g. with `get_pipeline()` and `main()`) actually correct?**
  _`ExtractiveStubGenerator` has 14 INFERRED edges - model-reasoned connections that need verification._