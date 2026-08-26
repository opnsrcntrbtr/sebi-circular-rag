# Graph Report - SEBI circular RAG  (2026-08-26)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2794 nodes · 5884 edges · 179 communities (142 shown, 37 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 606 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `02a0ad0b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- scrape_sebi.py
- export_datasets.py
- ValueError
- Chunk
- telemetry_engine.py
- test_golden_v7_packet.py
- Frame
- test_paraphrase_rescue.py
- eval_harness.py
- SpladeIndex
- test_golden_v7_gate.py
- test_selective_citations.py
- phase_generate
- RAGPipeline
- backfill_escalations.py
- test_regulations.py
- test_attribution.py
- context_headers.py
- Regulation Edge Annotation
- test_conformal.py
- extract_citations
- load_golden
- Settings
- test_golden_v7_gemini.py
- test_spaces.py
- test_dataset_cards.py
- test_ui.py
- derive_validity
- lineage.py
- load_circulars
- test_api.py
- HybridRetriever
- _is_non_sebi_domain
- test_export_datasets.py
- ExtractiveStubGenerator
- _row
- gemini_adjudicate.py
- api.py
- benchmark.py
- test_label_tier.py
- app.py
- agreement.py
- test_rerank_jina_v3.py
- settings.py
- local_adjudicate.py
- test_golden_v7_local.py
- Hugging Face Publishing
- ingest_pdf.py
- segment.py
- test_expand.py
- UI Citation Components
- test_scrape_sebi.py
- audit_label_provenance.py
- per_query_recall
- consolidation_edges
- test_export_integration.py
- test_golden_v7_agreement.py
- LexicalReranker
- _bootstrap_ci
- validate_golden_v7
- SubjectSimJudge
- Lineage
- test_pipeline.py
- Regulation Scraper Tests
- demote_superseded
- build_spaces_pipeline
- answer_with_abstention
- clopper_pearson_ci
- ZeroGPU Workaround Tests
- adjudicate_draft.py
- measure_supersession_precision
- eval_generator_for
- test_hyde.py
- Qwen3MLXReranker
- test_push_datasets.py
- test_trec_parity.py
- test_audit_reg_edges.py
- test_ingest_pdf.py
- test_segment.py
- resolve_chunk_spans
- test_eval_harness_v7.py
- paired_delta
- Handler
- audit_reg_edges.py
- build_report
- test_ingest_refs.py
- bootstrap_ci
- test_bench_retrieval_artifacts.py
- test_lineage.py
- parse_meta
- trace_failure.py
- _confirms_claude
- sweep_rrf_k.py
- read_trec_run
- detect_relations_ex
- test_build_reg_edges.py
- test_canary_generator.py
- main
- bench_rerankers.py
- test_repair_corpus_text.py
- test_injection.py
- MeasureResult
- build_regulatory_index
- stats.py
- test_context_recall.py
- _unique
- run_judge
- test_measure.py
- canary.sh
- _resolve_governing_spans
- run.sh
- ce_query_reform_probe.py
- main
- apply
- seed_v7.py
- refresh.sh
- Embedder
- measure_mrr
- measure_parsing_latency
- measure_retrieval_recall
- measure_temporal_accuracy
- reg_lineage.py
- DenseIndex
- test_app_asof.py
- test_benchmark.py
- test_build_index_out_dir.py
- main
- TestRegistry
- TestRetrievalBenchmarkNdcg
- autoresearch.sh
- Master Circular for Mutual Funds (2026)
- main
- measure_context_precision
- TestPerQueryRecall
- SEBI Master Circular for Mutual Funds (2020)
- main
- warrant_scorer
- _rejoin_split
- annotate_corpus
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
- _s_mc_no
- _paragraphs
- conftest.py
- test_settings_citation_scorer_enabled_true
- test_settings_citation_scorer_enabled_false
- Optimize Slash Command
- Seen Circular IDs
- SEBI Master Circular on Exchange Traded Derivatives (2012)
- SEBI Master Circular for REITs (2025)
- SEBI Master Circular for Mutual Funds (2024)
- sebi-rag
- Hugging Face Spaces Requirements
- SEBI Master Circular for Credit Rating Agencies
- SEBI Master Circular for ESG Rating Providers
- SEBI Master Circular for REITs
- SEBI Master Circular for RTAs
- SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122
- .query
- gwet_ac1
- main

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 114 edges
2. `RAGPipeline` - 61 edges
3. `Settings` - 49 edges
4. `HybridRetriever` - 46 edges
5. `ExtractiveStubGenerator` - 46 edges
6. `hierarchical_chunk()` - 46 edges
7. `HashEmbedder` - 43 edges
8. `load_golden()` - 38 edges
9. `build_lineage()` - 38 edges
10. `CircularMeta` - 33 edges

## Surprising Connections (you probably didn't know these)
- `_chunk()` --uses--> `Chunk`  [INFERRED]
  tests/test_hyde.py → src/sebi_rag/segment.py
- `test_chunks_config_refuses_header_and_maps_fields()` --uses--> `Chunk`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/segment.py
- `test_vectors_exposes_context_recall()` --calls--> `vectors()`  [INFERRED]
  tests/test_context_recall.py → scripts/golden_v7/score.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **SEBI Regulatory Consolidation Pattern** — sebi_ho_imd_df2_cir_p_2020_156, eval_golden_v7_annotations_packet_human_packet_ho_19_34_11_6_2025_afd_pod1_i_12928_2026, eval_golden_v7_annotations_packet_human_packet_sebi_ho_ddhs_pod_2_p_cir_2025_99 [EXTRACTED 0.90]
- **Mutual Fund Offsite Inspection Reporting** — sebi_ho_imd_imd_pod_1_p_cir_2025_38, ho_24_13_11_1_2026_imd_pod_1_i_7602_2026, sebi_mutual_funds_regulations_2026 [EXTRACTED 0.95]
- **Angel Fund Regulatory Framework** — sebi_ho_afd_afd_pod_1_p_cir_2025_128, sebi_ho_afd_afd_pod_1_p_cir_2025_136, ho_19_34_11_6_2025_afd_pod1_i_12928_2026 [EXTRACTED 1.00]
- **SEBI Master Circulars Collection** — sebi_ho_ddhs_pod2_p_cir_2025_101, sebi_ho_ddhs_pod_2_p_cir_2025_99, sebi_ho_mirsd_mirsd_pod_p_cir_2025_91, sebi_ho_mirsd_mirsd_pod_1_p_cir_2024_110, sebi_ho_imd_pod_1_i_7602_2026 [EXTRACTED 1.00]

## Communities (179 total, 37 thin omitted)

### Community 0 - "scrape_sebi.py"
Cohesion: 0.05
Nodes (61): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+53 more)

### Community 1 - "export_datasets.py"
Cohesion: 0.06
Nodes (70): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+62 more)

### Community 2 - "ValueError"
Cohesion: 0.06
Nodes (63): Rankings, _assert_fixed_tail(), convert_run_dir(), main(), Path, Back-convert archived runfiles into standards-compliant TREC artifacts. The…, Trailing field of the first line; also the whitespace precondition check., read_trec_run assumes qid and tag carry no whitespace. Verify per line. (+55 more)

### Community 3 - "Chunk"
Cohesion: 0.06
Nodes (32): Generator, _grounded_prompt(), Judge, _judge_prompt(), _judge_prompt_identify(), MLXJudge, OllamaGenerator, parse_excerpt_choice() (+24 more)

### Community 4 - "telemetry_engine.py"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 5 - "test_golden_v7_packet.py"
Cohesion: 0.07
Nodes (52): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+44 more)

### Community 6 - "Frame"
Cohesion: 0.07
Nodes (42): load_runs(), main(), Path, Assign epochs to the archived runs and write the epoch registry. Every run's…, _fmt(), guard_pair(), main(), Path (+34 more)

### Community 7 - "test_paraphrase_rescue.py"
Cohesion: 0.09
Nodes (40): is_degenerate(), Protocol, QueryRewriter, Paraphrase rescue for the cross-encoder score floor. Preregistered in…, Re-score `pool` with a rewritten query when `reranked` is below `floor`.…, Rewrites a lay-vocabulary query into statutory vocabulary. Returns None when it…, Fixed rewrite, for tests and for replaying a preregistered rewrite., True when `rewritten` is unusable and the rescue should be abandoned.… (+32 more)

### Community 8 - "eval_harness.py"
Cohesion: 0.08
Nodes (24): Ground truth: what do the 4 CE_MISMATCH rows actually DO in production? The…, Preregistered cohort measurement for the CE paraphrase rescue. Spec:…, What does the 0.05 cross-encoder score floor actually catch?…, Capture-once margin sweep for B' selective citations. One pipeline pass over…, Benchmark MLX generators on the golden set: faithfulness, groundedness,…, Retrieval-only benchmark with TREC runfile and reproducibility metadata. Use…, Build the dense+sparse index once and persist it (run after corpus changes).…, Calibrate top_k and the abstention threshold against the citation-precision… (+16 more)

### Community 9 - "SpladeIndex"
Cohesion: 0.07
Nodes (28): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.…, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+20 more)

### Community 10 - "test_golden_v7_gate.py"
Cohesion: 0.07
Nodes (43): derive_floors(), metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the…, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,…, True iff every floor's metric is present in `report_gate` and meets it. Missing…, select_golden() (+35 more)

### Community 11 - "test_selective_citations.py"
Cohesion: 0.11
Nodes (41): citation_scorer_for(), The single enable/disable AND backend decision for B'. Returns None when…, Context ids the answer rests on. Scores each context via `scorer`, keeps those…, select_citations(), _chunk(), _FakeReranker, Tests for B' selective citations: select_citations() and its integration., The backend choice must go through the same single decision point as the enable… (+33 more)

### Community 12 - "phase_generate"
Cohesion: 0.08
Nodes (39): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any… (+31 more)

### Community 13 - "RAGPipeline"
Cohesion: 0.12
Nodes (36): smoke_pipeline(), Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable…, run_pipeline_cases(), RAGPipeline, CircularMeta, hierarchical_chunk() (+28 more)

### Community 14 - "backfill_escalations.py"
Cohesion: 0.09
Nodes (38): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+30 more)

### Community 15 - "test_regulations.py"
Cohesion: 0.07
Nodes (39): _alias_keys(), _jaccard(), load_regulations(), name_tokens(), Path, Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6). Regulations…, Candidate alias lookup keys, most literal first. Both the raw normalised form…, Resolve a cited regulation name+year to a canonical reg_id. Returns (reg_id,… (+31 more)

### Community 16 - "test_attribution.py"
Cohesion: 0.07
Nodes (31): entailment_index(), NLIAttributionScorer, Index of the entailment class in a model's label map. Read from the checkpoint…, Scores each context by P(entailment) of the answer given that context.…, Wrap an already-constructed cross-encoder (also the test seam)., pick_device(), Device + precision selection for Apple-Silicon inference. Centralizes the…, Resolve the compute device. A truthy explicit `pref` ("mps"/"cpu"/"cuda") wins.… (+23 more)

### Community 17 - "context_headers.py"
Cohesion: 0.09
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 18 - "Regulation Edge Annotation"
Cohesion: 0.12
Nodes (33): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+25 more)

### Community 19 - "test_conformal.py"
Cohesion: 0.10
Nodes (32): _control_summary(), main(), phase_calibrate(), phase_generate(), phase_report(), R7 conformal abstention calibration: generate -> calibrate -> report phases.…, Current production behaviour, exactly as shipped -- no LOO recalibration, the…, Re-simulates each row's abstention decision under the CALIBRATED thresholds,… (+24 more)

### Community 20 - "extract_citations"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 21 - "load_golden"
Cohesion: 0.17
Nodes (26): main(), main(), main(), ADR-004 adoption: calibrate abstain_threshold for jina-reranker-v3-mlx's score…, main(), Build the full pipeline with real models., real_pipeline(), main() (+18 more)

### Community 22 - "Settings"
Cohesion: 0.13
Nodes (29): is_master(), main(), Is the eval set measuring retrieval, or measuring its own construction? Read-…, main(), R3 §3.1 — mine cross-reference (A cites B) candidate pairs. Spec:…, phase_judge(), _as_bool(), _get() (+21 more)

### Community 23 - "test_golden_v7_gemini.py"
Cohesion: 0.11
Nodes (29): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply… (+21 more)

### Community 24 - "test_spaces.py"
Cohesion: 0.10
Nodes (24): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo. All classes implement…, External Space first; on ANY failure fall back to the local CPU model.…, Primary generator: calls a public LLM Space via gradio_client. Wired to…, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus). Never… (+16 more)

### Community 25 - "test_dataset_cards.py"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 26 - "test_ui.py"
Cohesion: 0.06
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 27 - "derive_validity"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation. Locked…, Validity of one circular from the tiered edge list (any scope: the function…, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 28 - "lineage.py"
Cohesion: 0.10
Nodes (24): Build a lightweight pipeline for --smoke mode. Uses a stub retriever (no FAISS)…, smoke_pipeline(), Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped…, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the…, AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from… (+16 more)

### Community 29 - "load_circulars"
Cohesion: 0.13
Nodes (31): load_circulars(), Path, Path, corpus.load_circulars edge-case coverage. load_circulars reads a JSONL corpus…, Provided optional fields are passed through to CircularMeta., Multiple records produce multiple chunks., Blank lines between records are silently skipped., Malformed JSON raises ValueError (json.loads default). (+23 more)

### Community 30 - "test_api.py"
Cohesion: 0.08
Nodes (19): FastAPI, integration, _citation_meta(), CitationMeta, create_app(), _CannedGenerator, FastAPI service tests (offline pipelines): endpoints, auth, rate limit,…, /ready should trigger pipeline build and return ready=true. (+11 more)

### Community 31 - "HybridRetriever"
Cohesion: 0.12
Nodes (22): main(), SPIKE/GATE (throwaway, not preregistered) — R5's own precondition from the…, main(), What actually makes a context window large: chunk size, or chunk count? Read-…, build_default_pipeline(), _doc_checksum(), HybridRetriever, Path (+14 more)

### Community 32 - "_is_non_sebi_domain"
Cohesion: 0.10
Nodes (29): _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain. Case-…, The non-SEBI domain filter must match words, not substrings. Shipped 2026-07-30…, Any single-token keyword <= 5 chars is a substring hazard. Embedding it inside…, Query mentioning both SEBI and RBI should NOT abstain — SEBI intent wins., Empty query should not trigger the non-SEBI filter., FEMA keyword in a SEBI context should NOT abstain — SEBI intent wins., The exact query that exposed the bug. (+21 more)

### Community 33 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 34 - "ExtractiveStubGenerator"
Cohesion: 0.14
Nodes (24): ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., rerank_top exactly at 0.85 overrides judge abstention (HYBRID_THRESHOLD=0.85)., rerank_top just below 0.85 does NOT override judge abstention., When no judge is present, hybrid gate logic must be inert (no crash)., Unrelated query vs context: subject_sim < 0.42 → grounded() returns False. (+16 more)

### Community 35 - "_row"
Cohesion: 0.12
Nodes (27): decide(), Spec sec7 promotion rules for one row. `votes_by_annotator` is this row's votes…, Abstain rows have no explicit claude vote at all (Task 8 never judged them) -…, Both externals independently think something DOES govern (disputing the…, The LLM leg is whichever single non-claude/non-human annotator voted - "qwen"…, Amendment 2026-07-26 (user-approved): the promotion unit is the PROVISION, not…, External marked claude's chunk governing plus extras: claude's label is…, The abstain protocol can never emit non-empty governing (no letters are… (+19 more)

### Community 36 - "gemini_adjudicate.py"
Cohesion: 0.11
Nodes (26): adjudicate(), _current_model(), _daily_quota_exhausted(), main(), _parse_error_ids(), _parse_letter_choice(), _parse_reply(), _parse_yes_no() (+18 more)

### Community 37 - "api.py"
Cohesion: 0.10
Nodes (21): BaseModel, aggregate(), eligible(), main(), Preregistered cohort measurement for supersession confidence tiering. Spec:…, Answerable, non-as_of, with gold citations: the rows citation metrics exist for., _compute_kwargs(), QueryRequest (+13 more)

### Community 38 - "benchmark.py"
Cohesion: 0.19
Nodes (24): beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), chunks_by_doc(), dir_fingerprint(), enrich_golden_item(), export_beir() (+16 more)

### Community 39 - "test_label_tier.py"
Cohesion: 0.12
Nodes (20): classify_tier(), human_reviewed_ids(), main(), Path, Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.…, Map provenance to the controlled vocabulary. `human_reviewed` (row appears in…, Row ids present in the human labelling packet., Controlled-vocabulary label_tier over golden_v7 (spec A §8.3). (+12 more)

### Community 40 - "app.py"
Cohesion: 0.13
Nodes (21): _append_message(), _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_citations_md(), get_pipeline(), _on_submit(), _parse_as_of() (+13 more)

### Community 41 - "agreement.py"
Cohesion: 0.14
Nodes (22): _claude_accuracy_ci(), cohen_kappa(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation…, Categorical Cohen's kappa over paired labels (row-aligned). Each raw element is… (+14 more)

### Community 42 - "test_rerank_jina_v3.py"
Cohesion: 0.14
Nodes (17): ADR-004: the single decision for which model orders the RETRIEVAL pool…, retrieval_reranker_for(), _chunk(), _FakeJinaBackend, Offline tests for the jina-reranker-v3-mlx wrapper (ADR-004) — translation…, Same bug, same fix, second script: eval_asof.py also builds its own RAGPipeline…, Stands in for the vendor's MLXReranker.rerank() — same return shape (list of…, Bypass __init__ (no snapshot_download / mlx / network). (+9 more)

### Community 43 - "settings.py"
Cohesion: 0.15
Nodes (12): log(), Margin sweep for B' selective citations on the golden_v7 adjudicated set. One…, run(), Emit one JSON line listing SEBI circulars newer than previously seen. Uses a…, Emit one JSON line of retrieval/citation/abstention metrics using the persisted…, Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, One scoring path shared by `eval_json.py` (which measures) and…, Score one golden row through the production-shaped pipeline. Returns per-row… (+4 more)

### Community 44 - "local_adjudicate.py"
Cohesion: 0.15
Nodes (19): Transient-failure predicate for the real Gemini call: rate limiting (429) and…, Rerun-safety for votes.jsonl itself (plan Task 10 decision #7): drops every…, Same per-row deterministic shuffle as make_packet.py's write_packet:…, _replace_annotator_votes(), _should_retry(), _shuffled_candidates(), _current_model(), main() (+11 more)

### Community 45 - "test_golden_v7_local.py"
Cohesion: 0.15
Nodes (19): _extract_text(), Qwen-family models may emit <think>...</think> reasoning as inline text,…, Anthropic Messages response -> reply text: concatenates `text` content blocks,…, _strip_thinking(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external…, Five pilot rows from five strata measure more than five from one - the gemini…, Vote records must say annotator "qwen" (never reuse "gemini" - the agreement… (+11 more)

### Community 46 - "Hugging Face Publishing"
Cohesion: 0.19
Nodes (18): export_golden_v7_arrow(), log(), main(), Path, Run export_datasets.py then add golden_v7 Arrow config., Upload dist/datasets/ to HF dataset repo., Run make index to rebuild FAISS+BM25 before upload., Upload data/index/ to HF index repo. (+10 more)

### Community 47 - "ingest_pdf.py"
Cohesion: 0.17
Nodes (17): Re-derive circular number + dates from each record's stored text and rewrite…, _existing_numbers(), extract_text(), ingest(), main(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars. Drop a circular PDF into data/raw/ and… (+9 more)

### Community 48 - "segment.py"
Cohesion: 0.11
Nodes (10): NLI attribution scoring for B' citation selection. B' asks "does this context…, _softmax(), faithfulness(), Check that every circular id the answer cites (in square brackets) was actually…, Segmentation: hierarchical chunking + metadata + stable citation IDs. Minimal,…, # NOTE: We intentionally DO NOT set carry here — flush() already, Faithfulness: catch answers that cite circulars not in the retrieved context., test_faithfulness_scoring() (+2 more)

### Community 49 - "test_expand.py"
Cohesion: 0.16
Nodes (14): expand_query(), Append statutory synonyms for lay tokens present in `query`. Deterministic and…, BM25 lexical index (bm25s)., SparseIndex, Query-side lexical expansion (intervention #2, glossary variant).…, test_all_five_sparse_failure_queries_expand(), test_expanded_sparse_query_hits_statutory_chunk(), test_lay_term_gains_statutory_synonym() (+6 more)

### Community 50 - "UI Citation Components"
Cohesion: 0.16
Nodes (17): Human-readable regulation name. Year disambiguates same-short_name repeal pairs…, reg_display_name(), _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_outputs_md(), _parse_as_of(), Return empty markdown placeholder for streaming. (+9 more)

### Community 51 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 52 - "audit_label_provenance.py"
Cohesion: 0.21
Nodes (15): audit(), collect_artifacts(), _ids_from_csv(), _ids_from_dir(), _ids_from_jsonl(), main(), Path, Report what the annotation artifacts can account for, before classifying.… (+7 more)

### Community 53 - "per_query_recall"
Cohesion: 0.15
Nodes (15): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.…, validate_golden(), Answerable-but-unjudged rows are excluded from metrics, never scored 0.…, A real, fully-populated golden row, so the fixture cannot drift out of sync…, v7-ls-038/039/040 are answerable but unjudged; they carry… (+7 more)

### Community 54 - "consolidation_edges"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans…, _master(), test_annotate_idempotent() (+7 more)

### Community 55 - "test_export_integration.py"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 56 - "test_golden_v7_agreement.py"
Cohesion: 0.19
Nodes (15): _provision_agree(), Symmetric provision-level agreement between two governing labels, using the…, _min_agreement_fixture(), Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7):…, Different chunk copies of the same quoted provision agree at provision level…, _same_provision_fixture(), test_claude_accuracy_ci_returns_exact_and_provision(), test_main_default_rewrites_golden_and_queue() (+7 more)

### Community 57 - "LexicalReranker"
Cohesion: 0.22
Nodes (13): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, LexicalReranker, Deterministic query-coverage reranker (test/fallback). Score = fraction of…, One gold doc with `n` chunks that ALL contain the word "broker", so a…, Regression (2026-07-25): a must_contain literal matching many gold-doc chunks…, _retriever() (+5 more)

### Community 58 - "_bootstrap_ci"
Cohesion: 0.16
Nodes (9): skip, _bootstrap_ci(), _git_commit(), _mps_memory(), Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict., When torch+MPS available, returns memory stats dict. (+1 more)

### Community 59 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 60 - "SubjectSimJudge"
Cohesion: 0.17
Nodes (10): ADOPTED gate (eval_gate round 3): deterministic groundedness signal — max…, Max cosine(query, doc subject line) over contexts — the primary gate signal,…, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge, subject_sim == threshold (0.42) passes the gate (>= comparison)., section_score == section_threshold (0.60) passes via second tier., test_section_score_exactly_at_threshold_passes(), test_subject_sim_exactly_at_threshold_passes() (+2 more)

### Community 61 - "Lineage"
Cohesion: 0.17
Nodes (10): Lineage, Path, Connected component over supersedes/superseded_by (both tiers)., The circular in this family that governs on date as_of (ISO), or None when…, test_demote_superseded_puts_in_force_on_top(), test_governing_on_cycle_safe(), test_governing_on_parallel_branches_max_date_wins(), test_lineage_load_old_file_defaults_empty_edges() (+2 more)

### Community 62 - "test_pipeline.py"
Cohesion: 0.18
Nodes (15): _build_chunks(), _build_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline. Runs fully offline…, Offline pipeline whose single circular rests on a repealed regulation., Current behaviour: the heuristic edge demotes OLD below NEW., With tiering on, an unevidenced supersession no longer demotes., _repealed_basis_pipeline(), test_abstention_on_out_of_domain_query() (+7 more)

### Community 64 - "demote_superseded"
Cohesion: 0.27
Nodes (15): contexts_for(), demote_superseded(), Down-weight reranked (chunk, score) pairs from superseded circulars and re-…, OLD_E superseded by an explicit clause; OLD_I only by a title heuristic., Backward compatibility: the default reproduces current behaviour exactly., An explicit clause anywhere outranks a heuristic edge — evidence wins., _score(), test_circular_with_both_edge_kinds_uses_the_explicit_penalty() (+7 more)

### Community 65 - "build_spaces_pipeline"
Cohesion: 0.23
Nodes (13): build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux). Parallel…, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row() (+5 more)

### Community 66 - "answer_with_abstention"
Cohesion: 0.25
Nodes (14): answer_with_abstention(), _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons,…, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful(), test_no_context_reason_when_top_k_zero(), test_score_floor_reason() (+6 more)

### Community 67 - "clopper_pearson_ci"
Cohesion: 0.22
Nodes (5): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion. Use this for strictly…, test_render_report_includes_ac1_and_provision(), The reason for the switch. On 9/10 the percentile bootstrap returns [0.70,…, TestClopperPearson

### Community 68 - "ZeroGPU Workaround Tests"
Cohesion: 0.14
Nodes (13): app_module(), fixture, Regression coverage for the ZeroGPU-hardware workaround in app.py. Background:…, Inject a fake `spaces` module so app.py's `import spaces` succeeds offline, and…, Static guard: if `import spaces` or the `@spaces.GPU` decorator is ever…, It must stay dead code: calling it would request a real ZeroGPU allocation (and…, The functions actually on the request path (get_pipeline, run_query_stream)…, `hardware:` in README-spaces.md is not a documented Spaces config key (only… (+5 more)

### Community 69 - "adjudicate_draft.py"
Cohesion: 0.21
Nodes (11): RuntimeError, adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response. (+3 more)

### Community 70 - "measure_supersession_precision"
Cohesion: 0.16
Nodes (11): main(), measure_supersession_precision(), Path, Measure fraction of detected supersession edges that are genuine. Samples…, Verify a supersession edge by cross-referencing corpus records. Returns "true",…, Run all (or specified) metrics sequentially., run_all_metrics(), _verify_supersession_edge() (+3 more)

### Community 71 - "eval_generator_for"
Cohesion: 0.16
Nodes (12): eval_generator_for(), The single generator decision for the eval stack. `derive_thresholds.py` sets…, The eval stack's generator choice must be one shared decision.…, Uses an injected loader so the test stays offline., Silently falling back to the stub would derive floors under semantics the…, Must assert the factory is CALLED, not merely imported. Verified 2026-08-12 by…, A factory both call is not enough - they must pass the same setting, or the…, test_both_eval_scripts_read_the_same_setting() (+4 more)

### Community 72 - "test_hyde.py"
Cohesion: 0.20
Nodes (10): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —…, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_output_truncated_to_max_chars() (+2 more)

### Community 73 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 74 - "test_push_datasets.py"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default:…, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 75 - "test_trec_parity.py"
Cohesion: 0.29
Nodes (11): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), test_retrieval_metrics(), _internal(), Prove the internal retrieval metrics are the standard ones. Skips unless the…, _standard() (+3 more)

### Community 76 - "test_audit_reg_edges.py"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 77 - "test_ingest_pdf.py"
Cohesion: 0.17
Nodes (12): _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash…, The mirror of the kerning case above. When the en-dash has spaces on BOTH sides…, 2011-era master circulars use "SEBI/<DEPT>/MC No.<n>/<serial>/<year>", matching…, Old-format PDFs (e.g. CIR/MRD/DP/ 11 /2012) split the number with a space…, test_ingest_extracts_metadata_and_lineage(), test_parse_meta_handles_2011_mc_number_format() (+4 more)

### Community 78 - "test_segment.py"
Cohesion: 0.18
Nodes (12): _body(), Chunker (segment.hierarchical_chunk) behaviour. Regression guard for the "5.…, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_absorption_respects_300_char_cap(), test_bare_parent_heading_folds_into_first_subsection(), test_bare_parent_heading_not_emitted_as_standalone_chunk(), test_governing_clause_not_duplicated(), test_leaf_single_line_provision_is_preserved_not_overmerged() (+4 more)

### Community 79 - "resolve_chunk_spans"
Cohesion: 0.30
Nodes (11): _norm_ws(), Span {doc, quote} -> matching chunk ids (all overlap matches count). Legacy…, resolve_chunk_spans(), _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through(), test_qrels_span_rows_get_grade_2() (+3 more)

### Community 80 - "test_eval_harness_v7.py"
Cohesion: 0.42
Nodes (11): run_eval(), test_eval_harness_metric_suite(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-…, _row(), test_as_of_is_passed_to_pipeline(), test_chunk_metrics_computed_for_span_rows(), test_gate_is_none_when_nothing_adjudicated() (+3 more)

### Community 81 - "paired_delta"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries. Returns mean_b -…, Randomization p-values use the (count+1)/(n+1) estimator, so a p-value of…, One query flipping out of 56 is exactly the iv9-style verdict: the…, TestPairedDelta

### Community 82 - "Handler"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 83 - "audit_reg_edges.py"
Cohesion: 0.29
Nodes (9): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+1 more)

### Community 84 - "build_report"
Cohesion: 0.31
Nodes (10): build_report(), Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid measurement;…, The headline number must be the 10 pipeline cases alone — the whole point of…, _results(), test_pipeline_metrics_are_not_polluted_by_selector_cases(), test_pooled_overall_carries_no_interval() (+2 more)

### Community 85 - "test_ingest_refs.py"
Cohesion: 0.20
Nodes (8): _primary_number(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_dedup_uses_normalized_numbers(), test_fulltext_fallback_returns_earliest_body_reference(), test_parse_meta_dept_order_document_end_to_end(), test_parse_meta_excludes_prefix_variant_self_reference(), test_primary_number_format_matrix()

### Community 86 - "bootstrap_ci"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must be wide…, TestBootstrapCI

### Community 87 - "test_bench_retrieval_artifacts.py"
Cohesion: 0.18
Nodes (7): bench_retrieval must emit valid TREC alongside the legacy runfile., run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so every…, iv9/iv10 build a headered index beside data/index. Without an index override…, ADR-004: benchmarking jina-reranker-v3-mlx against the production cross-encoder…, test_bench_retrieval_can_bench_an_alternate_index(), test_bench_retrieval_can_measure_the_reranked_order(), test_bench_retrieval_exposes_and_records_the_reranker_choice()

### Community 88 - "test_lineage.py"
Cohesion: 0.24
Nodes (10): _lin_chain(), P2 lineage / supersession resolution tests., test_build_lineage_edges_tiered(), test_build_lineage_inferred_master_topic_edge(), test_governing_on_before_family_exists(), test_governing_on_linear_chain(), test_governing_on_unknown_dates_excluded(), test_master_circular_reissue_supersession() (+2 more)

### Community 89 - "parse_meta"
Cohesion: 0.24
Nodes (9): Pattern, main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), _iso_date(), _labeled_date(), parse_meta(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars. (+1 more)

### Community 90 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 92 - "sweep_rrf_k.py"
Cohesion: 0.27
Nodes (8): main(), mrr(), ndcg_at_k(), Sweep RRF k_const values on the golden set. No index rebuild needed., recall_at_k(), Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 93 - "read_trec_run"
Cohesion: 0.29
Nodes (6): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), write_trec_run(), test_trec_run_and_research_judges_are_sidecar_only(), The archived runfiles embed section headings in the doc id., TestReadTrecRun

### Community 94 - "detect_relations_ex"
Cohesion: 0.20
Nodes (10): detect_relations(), detect_relations_ex(), Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window(), A circular that names another circular BEFORE the supersede trigger word must…, test_detect_relations_delegates_unchanged(), test_detect_relations_ex_evidence_and_extractor() (+2 more)

### Community 95 - "test_build_reg_edges.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 96 - "test_canary_generator.py"
Cohesion: 0.27
Nodes (8): _canary_jscode(), _ops_timeout(), The eval canary must fit its timeout and alert on real regressions. Measured…, n8n gives up first if its budget is smaller, so the ops timeout is never…, A threshold above the healthy value fires every run. citation_precision was…, test_alert_thresholds_sit_below_measured_baselines(), test_n8n_timeout_not_tighter_than_the_ops_budget(), test_ops_timeout_fits_the_measured_runtime()

### Community 97 - "main"
Cohesion: 0.31
Nodes (7): call(), main(), _norm(), Does answering a golden_v7 row require a circular the corpus does not hold?…, Uppercase, strip all whitespace — so 'CIR/MIRSD/5/ 2013' matches…, Returns (answer, reasoning). The judge is a reasoning model: the oMLX API…, windows()

### Community 98 - "bench_rerankers.py"
Cohesion: 0.28
Nodes (7): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,…, SEBI Circular RAG — local-first, Apple Silicon. Pipeline: ingest -> segment ->…

### Community 99 - "test_repair_corpus_text.py"
Cohesion: 0.22
Nodes (4): main(), Repair the 6 records whose body text was overwritten with one shared circular's…, The repair map must name a real orphan PDF that parses to the circular_number…, test_numbers_normalize_distinctly()

### Community 100 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 101 - "MeasureResult"
Cohesion: 0.39
Nodes (3): MeasureReport, MeasureResult, TestDataClasses

### Community 102 - "build_regulatory_index"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 103 - "stats.py"
Cohesion: 0.22
Nodes (6): BootstrapCI, PairedResult, ProportionCI, Uncertainty quantification for benchmark runs. The golden set is n=56…, True when the randomization test rejects at 1 - confidence AND the paired…, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 104 - "test_context_recall.py"
Cohesion: 0.39
Nodes (8): _chunk(), The gate must measure the context window, not just the fusion list.…, An abstention still had a context window; measuring retrieval delivery must not…, _reranked(), test_answer_records_the_context_ids_it_used(), test_context_ids_populated_even_when_abstaining(), test_context_ids_respect_top_k(), test_vectors_exposes_context_recall()

### Community 105 - "_unique"
Cohesion: 0.39
Nodes (8): measure(), cited_docs(), metrics(), evaluate(), run_retrieval_benchmark(), _doc(), _eval_item(), _unique()

### Community 106 - "run_judge"
Cohesion: 0.39
Nodes (7): _is_parseable(), _load_screen(), main(), R1 §3.3 degeneracy probe: does the warrant judge return a parseable reply?…, Mirrors generate.parse_warrant_scores' cleaning exactly, but reports whether…, run_answers(), run_judge()

### Community 107 - "test_measure.py"
Cohesion: 0.29
Nodes (4): metrics_to_markdown(), Format results as a markdown table., Unit tests for sebi_rag.measure — automated metric collection., TestCLI

### Community 108 - "canary.sh"
Cohesion: 0.25
Nodes (7): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, SEBI_RAG_EVAL_GENERATOR, canary.sh script, TOKENIZERS_PARALLELISM

### Community 109 - "_resolve_governing_spans"
Cohesion: 0.36
Nodes (8): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote} spans, looked…, _resolve_governing_spans(), _pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool(), test_resolve_governing_spans_short_body_uses_whole_body(), test_resolve_governing_spans_uses_first_60_body_chars()

### Community 110 - "run.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 111 - "ce_query_reform_probe.py"
Cohesion: 0.38
Nodes (6): main(), _pool(), Probe: does query-side reformulation lift the CE score on the 4 CE_MISMATCH…, Return (ce_top, best relevant score, chunk_id of argmax)., Top-8 pool plus every relevant chunk, de-duplicated on chunk_id., _score()

### Community 112 - "main"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

### Community 113 - "apply"
Cohesion: 0.29
Nodes (7): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions` (keyed by…, test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only(), test_apply_queue_decision_leaves_row_untouched(), test_apply_row_without_a_decision_is_never_touched()

### Community 114 - "seed_v7.py"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 115 - "refresh.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 116 - "Embedder"
Cohesion: 0.29
Nodes (4): Embedder, ndarray, Protocol, _tokens()

### Community 117 - "measure_mrr"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level. For each query, RR = 1/rank of first…, TestMRR

### Community 118 - "measure_parsing_latency"
Cohesion: 0.38
Nodes (4): measure_parsing_latency(), Measure PDF ingestion throughput (chars/sec, ms/PDF). Samples 20 PDFs…, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 119 - "measure_retrieval_recall"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 120 - "measure_temporal_accuracy"
Cohesion: 0.43
Nodes (3): measure_temporal_accuracy(), Measure fraction of as_of queries returning correct pre-supersession circular…, TestTemporalAccuracy

### Community 121 - "reg_lineage.py"
Cohesion: 0.29
Nodes (6): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus., derive_regulatory_basis(), Regulatory-basis status of one circular from its resolved regulations.…, test_derive_regulatory_basis_truth_table()

### Community 122 - "DenseIndex"
Cohesion: 0.33
Nodes (3): DenseIndex, ndarray, FAISS IndexFlatIP over L2-normalized vectors (cosine).

### Community 123 - "test_app_asof.py"
Cohesion: 0.29
Nodes (3): app_module(), fixture, As-of date plumbing in the Spaces UI (app.py).

### Community 124 - "test_benchmark.py"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

### Community 125 - "test_build_index_out_dir.py"
Cohesion: 0.29
Nodes (5): build_index must be able to target a scratch index directory. The iv9/iv10…, A --out flag that is parsed but ignored is worse than none: it reads as safe…, lineage.json lands next to the index it describes; writing it into data/index…, test_build_index_saves_to_the_resolved_out_dir_not_the_constant(), test_lineage_follows_the_out_dir()

### Community 126 - "main"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl()

### Community 128 - "TestRetrievalBenchmarkNdcg"
Cohesion: 0.40
Nodes (4): _FixedOrderReranker, ADR-004: a reranker swap changes ORDER within top-10, which recall@10 (set…, Always returns the SAME doc order regardless of query — deterministic, so…, TestRetrievalBenchmarkNdcg

### Community 129 - "autoresearch.sh"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 130 - "Master Circular for Mutual Funds (2026)"
Cohesion: 0.40
Nodes (5): Master Circular for Mutual Funds (2026), Circular on Development of Passive Funds, Extension of timelines for submission of offsite inspection data (Mutual Funds), SEBI (Mutual Funds) Regulations, 1996, SEBI (Mutual Funds) Regulations, 2026

### Community 131 - "main"
Cohesion: 0.50
Nodes (4): build_screen(), main(), T-Screen: does the generator follow the citation instruction at all? Spec:…, 50 rows stratified proportionally to golden_v7's eight strata.

### Community 132 - "measure_context_precision"
Cohesion: 0.50
Nodes (3): measure_context_precision(), Fraction of top-k chunks from relevant circulars. Unlike recall@k (which is…, TestContextPrecision

### Community 134 - "SEBI Master Circular for Mutual Funds (2020)"
Cohesion: 0.50
Nodes (4): SEBI Circular on Options Eligibility (2024), SEBI Master Circular for Mutual Funds (2020), SEBI Circular HO/24/13/12(4)2025-IMD-POD-1/I/2062/2026, SEBI Master Circular for Mutual Funds (2026)

### Community 135 - "main"
Cohesion: 0.67
Nodes (3): main(), P0 prep: price a larger MLX generator before committing to the R0 upgrade.…, rss_gb()

### Community 136 - "warrant_scorer"
Cohesion: 0.50
Nodes (4): Callable compatible with select_citations' scorer.rerank() signature. Wraps…, warrant_scorer(), 2026-08-23 measured WarrantJudge's max_tokens=512 default giving 38.1%…, test_warrant_scorer_forwards_max_tokens_to_the_judge()

### Community 137 - "_rejoin_split"
Cohesion: 0.50
Nodes (4): Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge()

### Community 138 - "annotate_corpus"
Cohesion: 0.50
Nodes (4): annotate_corpus(), Update each corpus record's supersession_status + superseded_by + supersedes…, test_annotate_corpus_adds_master_fields_and_consolidates_edges(), test_annotate_corpus_writes_new_metadata_fields()

### Community 139 - "SEBI Master Circular for LODR Compliance"
Cohesion: 0.67
Nodes (3): SEBI Master Circular for LODR Compliance, SEBI Operational Circular for Non-convertible Securities (2022), SEBI Master Circular for RTAs (2023)

### Community 140 - "Master Circular for Alternative Investment Funds (AIFs) (2026)"
Cohesion: 1.00
Nodes (3): Master Circular for Alternative Investment Funds (AIFs) (2026), Revised regulatory framework for Angel Funds, Relaxation in timeline for disclosure of allocation methodology by Angel Funds

### Community 141 - "SEBI Circular on IRRA Platform"
Cohesion: 0.67
Nodes (3): Investor Risk Reduction Access (IRRA), SEBI Circular on IRRA Platform, Master Circular for Stock Brokers (2025)

### Community 176 - ".query"
Cohesion: 0.25
Nodes (4): Answer, _LineageAwareReranker, Reranker wrapper that re-applies lineage handling to its output. The paraphrase…, As-of exclusion or supersession demotion, applied to a reranked list. Extracted…

### Community 177 - "gwet_ac1"
Cohesion: 0.29
Nodes (7): gwet_ac1(), Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a prevalence-…, The kappa base-rate paradox: one label dominates, raw agreement is high, yet…, test_gwet_ac1_both_constant_and_identical_is_one(), test_gwet_ac1_empty_input_is_one(), test_gwet_ac1_exceeds_kappa_on_skewed_high_agreement(), test_gwet_ac1_identical_lists_is_one()

### Community 178 - "main"
Cohesion: 0.67
Nodes (3): eligible(), main(), SPIKE — throwaway, not preregistered. Answers one question before any R6 design…

## Knowledge Gaps
- **60 isolated node(s):** `HF_HUB_DISABLE_XET`, `OMP_NUM_THREADS`, `PYTHONPATH`, `PYTORCH_ENABLE_MPS_FALLBACK`, `SEBI_RAG_EVAL_GENERATOR` (+55 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **37 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `scrape_sebi.py`, `TestRetrievalBenchmarkNdcg`, `test_paraphrase_rescue.py`, `warrant_scorer`, `eval_harness.py`, `SpladeIndex`, `test_selective_citations.py`, `RAGPipeline`, `test_attribution.py`, `context_headers.py`, `load_golden`, `test_spaces.py`, `lineage.py`, `load_circulars`, `HybridRetriever`, `ExtractiveStubGenerator`, `api.py`, `benchmark.py`, `test_rerank_jina_v3.py`, `segment.py`, `.query`, `LexicalReranker`, `validate_golden_v7`, `SubjectSimJudge`, `Lineage`, `demote_superseded`, `build_spaces_pipeline`, `answer_with_abstention`, `test_hyde.py`, `Qwen3MLXReranker`, `resolve_chunk_spans`, `sweep_rrf_k.py`, `test_injection.py`, `test_context_recall.py`, `main`, `test_benchmark.py`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `TestRetrievalBenchmarkNdcg`, `Chunk`, `measure_context_precision`, `TestPerQueryRecall`, `test_paraphrase_rescue.py`, `eval_harness.py`, `load_golden`, `lineage.py`, `test_api.py`, `HybridRetriever`, `api.py`, `benchmark.py`, `settings.py`, `.query`, `Lineage`, `test_pipeline.py`, `build_spaces_pipeline`, `measure_supersession_precision`, `test_eval_harness_v7.py`, `_unique`, `Embedder`, `measure_mrr`, `measure_parsing_latency`, `measure_retrieval_recall`, `measure_temporal_accuracy`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `load_golden()` connect `load_golden` to `main`, `test_golden_v7_packet.py`, `Frame`, `main`, `eval_harness.py`, `phase_generate`, `backfill_escalations.py`, `test_conformal.py`, `HybridRetriever`, `gemini_adjudicate.py`, `api.py`, `benchmark.py`, `agreement.py`, `local_adjudicate.py`, `main`, `adjudicate_draft.py`, `measure_supersession_precision`, `test_eval_harness_v7.py`, `run_judge`, `main`, `seed_v7.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 65 inferred relationships involving `Chunk` (e.g. with `dataset_quality()` and `NLIAttributionScorer`) actually correct?**
  _`Chunk` has 65 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `run()`) actually correct?**
  _`RAGPipeline` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `Settings` (e.g. with `main()` and `main()`) actually correct?**
  _`Settings` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `HybridRetriever` (e.g. with `main()` and `main()`) actually correct?**
  _`HybridRetriever` has 36 INFERRED edges - model-reasoned connections that need verification._