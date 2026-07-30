# Graph Report - SEBI circular RAG  (2026-07-30)

## Corpus Check
- 155 files · ~156,027 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2022 nodes · 4852 edges · 101 communities (90 shown, 11 thin omitted)
- Extraction: 73% EXTRACTED · 27% INFERRED · 0% AMBIGUOUS · INFERRED: 1297 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `297bc334`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Core RAG Pipeline
- Benchmark Infrastructure
- Data Processing
- Index & Evaluation
- Dataset Export
- Utility Scripts
- Spaces CPU Pipeline
- Dataset Card Tests
- Metadata Engine
- Export Tests
- .grounded
- Benchmark Scripts
- Qwen3MLXReranker
- Lineage
- As-of Evaluation
- Embedder
- Scraper Tests
- Master Metadata
- Export Integration
- lineage.py
- test_gate.py
- Chunk
- Corpus Validation
- Reranking
- ZeroGPU Tests
- Dataset Push
- Answer Generation
- Ops Server
- trace_failure.py
- test_gate.py
- build_lineage
- detect_relations_ex
- Build Scripts
- Canary Monitoring
- Index Refresh
- As-of UI Tests
- annotate_corpus
- Space Deployment
- Discovery Scripts
- Index Upload
- test_incremental_index.py
- test_integration_e2e.py
- UI Components
- Ops Scripts
- Notification Scripts
- Test Guards
- bench_rerankers.py
- bench_retrieval.py
- .encode
- answer_with_abstention
- bench_retrieval.py
- _compute_kwargs
- paired_delta
- bootstrap_ci
- build_index.py
- eval_harness.py
- SparseIndex
- SparseIndex
- discover_new.py
- corpus_spaces.py
- eval.py
- test_integration_e2e.py
- test_pipeline.py
- test_persistence.py
- faithfulness
- LexicalReranker
- eval_harness.py
- validate_golden_v7
- SpladeIndex
- acquire_missing_pdfs.py
- Chunk
- HybridRetriever
- scrape_regulations.py
- resolve_chunk_spans
- test_ingest_refs.py
- test_acquire_missing.py
- load_regulations
- discover_new.py
- _alias_keys
- test_ingest_pdf.py
- test_faithfulness.py
- paired_delta
- load_regulations
- audit_reg_edges.py
- test_eval_harness_v7.py
- bootstrap_ci
- load_golden_asof
- .encode
- load_golden
- test_repair_corpus_text.py
- test_injection.py
- TestReadTrecRun
- main
- .test_mean_reproduces_the_archived_aggregate
- Chunk
- app.py
- .encode
- Community 107
- Community 126
- Community 127

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 157 edges
2. `RAGPipeline` - 71 edges
3. `HybridRetriever` - 60 edges
4. `HashEmbedder` - 53 edges
5. `Lineage` - 53 edges
6. `ExtractiveStubGenerator` - 52 edges
7. `CircularMeta` - 51 edges
8. `BGEM3Embedder` - 46 edges
9. `CrossEncoderReranker` - 46 edges
10. `Settings` - 46 edges

## Surprising Connections (you probably didn't know these)
- `test_strip_thinking_leaves_plain_replies_untouched()` --calls--> `_strip_thinking()`  [INFERRED]
  tests/test_golden_v7_local.py → scripts/golden_v7/local_adjudicate.py
- `test_run_metadata_has_reproducibility_fields()` --calls--> `run_metadata()`  [INFERRED]
  tests/test_benchmark.py → src/sebi_rag/benchmark.py
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_bge_fp16_encode_is_normalized()` --calls--> `BGEM3Embedder`  [INFERRED]
  tests/test_api.py → src/sebi_rag/embeddings.py
- `test_numbers_normalize_distinctly()` --calls--> `normalize_circular_number()`  [INFERRED]
  tests/test_repair_corpus_text.py → src/sebi_rag/ingest_pdf.py

## Import Cycles
- 1-file cycle: `src/sebi_rag/api.py -> src/sebi_rag/api.py`

## Communities (101 total, 11 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.07
Nodes (55): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), int, Path, str (+47 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.20
Nodes (27): Any, beir_corpus_rows(), beir_query_rows(), build_golden_v6(), dir_fingerprint(), enrich_golden_item(), export_beir(), git_commit() (+19 more)

### Community 2 - "Data Processing"
Cohesion: 0.06
Nodes (60): load_jsonl(), main(), int, Path, str, Build circular -> regulation edges and annotate the corpus (offline).  No networ, write_jsonl(), annotate_regulation_fields() (+52 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.10
Nodes (31): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape).     Non-abst, _pool(), int, str, Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing, a, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as     "confirms abs, A non-abstain row whose pool happens to have zero candidates can't     offer any (+23 more)

### Community 4 - "Dataset Export"
Cohesion: 0.09
Nodes (53): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+45 more)

### Community 5 - "Utility Scripts"
Cohesion: 0.15
Nodes (18): Path, file_sha256(), Path, str, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file. (+10 more)

### Community 6 - "Spaces CPU Pipeline"
Cohesion: 0.27
Nodes (4): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion.      Use this for stri, The reason for the switch. On 9/10 the percentile bootstrap returns         [0.7, TestClopperPearson

### Community 7 - "Dataset Card Tests"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 8 - "Metadata Engine"
Cohesion: 0.12
Nodes (10): classify_circular_type(), derive_validity(), str, Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields() (+2 more)

### Community 9 - "Export Tests"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 10 - ".grounded"
Cohesion: 0.14
Nodes (53): BaseModel, FastAPI, bool, str, evaluate(), float, int, str (+45 more)

### Community 11 - "Benchmark Scripts"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 13 - "Lineage"
Cohesion: 0.19
Nodes (15): _pool(), int, str, Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external ann, Five pilot rows from five strata measure more than five from one -     the gemin, Vote records must say annotator "qwen" (never reuse "gemini" - the     agreement, Back-compat guard: the gemini leg (on hold, not removed) must keep     producing, Qwen-family models may emit <think>...</think> as inline text rather     than as (+7 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.10
Nodes (32): classify_answer(), classify_query(), _doc(), load_run(), main(), int, Path, str (+24 more)

### Community 15 - "Embedder"
Cohesion: 0.14
Nodes (26): CircularMeta, load_circulars(), Chunk, Path, str, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf() (+18 more)

### Community 16 - "Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "Master Metadata"
Cohesion: 0.08
Nodes (33): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).  Resumable, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10).  Pulls the i, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+25 more)

### Community 18 - "Export Integration"
Cohesion: 0.29
Nodes (14): chunks_by_doc(), Chunk, qrels_rows(), Span {doc, quote} -> matching chunk ids (all overlap matches count).      Legacy, resolve_chunk_spans(), _span_resolution_issues(), _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud. (+6 more)

### Community 19 - "lineage.py"
Cohesion: 0.33
Nodes (5): main(), int, Dry-run audit of every circular_number renumber.py would change, with the docume, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 20 - "test_gate.py"
Cohesion: 0.06
Nodes (44): derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).  Write, metric -> per-query score vector, into gate-floor names -> floor value.      Met, floors_ok(), bool, Path, Which golden set gates CI, and whether its adjudicated subset clears the derived, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed     v7 gate, (+36 more)

### Community 21 - "Chunk"
Cohesion: 0.07
Nodes (46): SpacesSettings, ExternalSpaceGenerator, HFGenerator, HybridGenerator, Chunk, object, str, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement (+38 more)

### Community 22 - "Corpus Validation"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 23 - "Reranking"
Cohesion: 0.10
Nodes (35): Citation, _clause_in(), extract_citations(), _is_table_artefact(), bool, int, str, Extract regulation citations from circular text (spec 2026-07-23 §3.3).  Deliber (+27 more)

### Community 24 - "ZeroGPU Tests"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 25 - "Dataset Push"
Cohesion: 0.20
Nodes (12): main(), Path, str, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path (+4 more)

### Community 26 - "Answer Generation"
Cohesion: 0.31
Nodes (10): build_report(), Assemble the persisted as-of run artifact.      Pipeline accuracy is the headlin, Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid     measureme, The headline number must be the 10 pipeline cases alone — the whole     point of, _results(), test_pipeline_metrics_are_not_polluted_by_selector_cases(), test_pooled_overall_carries_no_interval() (+2 more)

### Community 27 - "Ops Server"
Cohesion: 0.25
Nodes (7): BaseHTTPRequestHandler, Handler, bool, int, str, run_script(), smoketest()

### Community 28 - "trace_failure.py"
Cohesion: 0.29
Nodes (11): first_answer_rank(), first_gold_rank(), heading_only(), main(), int, str, Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no (+3 more)

### Community 29 - "test_gate.py"
Cohesion: 0.08
Nodes (20): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Emit one JSON line of retrieval/citation/abstention metrics using the persisted (+12 more)

### Community 30 - "build_lineage"
Cohesion: 0.13
Nodes (24): ArgumentParser, build_parser(), capture_live_performance(), check_safety_limit(), fetch_omlx_metrics(), get_hardware_state(), load_history(), main() (+16 more)

### Community 31 - "detect_relations_ex"
Cohesion: 0.23
Nodes (20): bytes, discover(), extract_pdf_urls(), fetch(), _listing_url(), looks_like_pdf(), main(), _page() (+12 more)

### Community 32 - "Build Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 33 - "Canary Monitoring"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 34 - "Index Refresh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 36 - "annotate_corpus"
Cohesion: 0.06
Nodes (42): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).  Standalo, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual, csr_matrix, float, int, ndarray (+34 more)

### Community 40 - "test_incremental_index.py"
Cohesion: 0.15
Nodes (16): derive_regulatory_basis(), _jaccard(), load_regulations(), name_tokens(), float, Path, str, Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6).  Regulations (+8 more)

### Community 41 - "test_integration_e2e.py"
Cohesion: 0.12
Nodes (17): Pattern, Re-derive circular number + dates from each record's stored text and rewrite the, _iso_date(), _labeled_date(), Local PDF ingestion for SEBI circulars.  Drop a circular PDF into data/raw/ and, Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104",     "HO/ (, Standard formats (old CIR, new SEBI/HO, free-form 2026): first     slash-heavy H, Department-only prefixes without HO/CIR anchor,     e.g. AFD/P/CIR/2022/125. (+9 more)

### Community 42 - "UI Components"
Cohesion: 0.31
Nodes (9): build_ui(), _empty_outputs(), _parse_as_of(), bool, float, str, Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO     YYYY-MM-D (+1 more)

### Community 46 - "bench_rerankers.py"
Cohesion: 0.16
Nodes (15): HydeExpander, int, str, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), int, str, _rank() (+7 more)

### Community 47 - "bench_retrieval.py"
Cohesion: 0.16
Nodes (19): hierarchical_chunk(), _paragraphs(), int, str, Split into units each <= max_chars.      PDF-extracted text often lacks blank-li, Document -> section -> paragraph chunks with stable IDs.      A "section" is det, _body(), str (+11 more)

### Community 48 - ".encode"
Cohesion: 0.12
Nodes (20): DenseIndex, _doc_checksum(), bool, Chunk, Embedder, float, int, ndarray (+12 more)

### Community 49 - "answer_with_abstention"
Cohesion: 0.10
Nodes (19): _citation_meta(), create_app(), _CannedGenerator, _distinct_pipeline(), RAGPipeline, FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, /ready should trigger pipeline build and return ready=true., _slow_pipeline() (+11 more)

### Community 50 - "bench_retrieval.py"
Cohesion: 0.33
Nodes (14): validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations(), test_duplicate_text_across_records_flagged(), test_empty_text_is_not_a_duplicate_cluster(), test_flags_bad_issue_date() (+6 more)

### Community 51 - "_compute_kwargs"
Cohesion: 0.06
Nodes (67): apply(), _body(), _claude_accuracy_ci(), cohen_kappa(), _confirms_claude(), decide(), _label(), _literals_by_row() (+59 more)

### Community 52 - "paired_delta"
Cohesion: 0.14
Nodes (20): expand_query(), str, Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic, Stage-1 hybrid retrieval: dense (FAISS) + sparse (BM25) fused by RRF.  Mandatory, _chunk(), int, str (+12 more)

### Community 53 - "bootstrap_ci"
Cohesion: 0.14
Nodes (22): fetch_manifest(), main(), float, int, str, Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:, diff_manifest(), _iso() (+14 more)

### Community 54 - "build_index.py"
Cohesion: 0.12
Nodes (17): bool, Chunk, float, int, str, qwen3_rerank_prompt(), Qwen3MLXReranker, Stage-2 reranking (mandatory, D4). Cross-encoder in production; a deterministic (+9 more)

### Community 55 - "eval_harness.py"
Cohesion: 0.25
Nodes (10): _build_chunks(), _build_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline.  Runs fully offline (HashEmbed, test_abstention_on_out_of_domain_query(), test_hybrid_retrieval_finds_relevant_circular(), test_note_absent_when_index_is_none(), test_note_absent_when_status_not_repealed_basis(), test_note_fires_and_disambiguates_year() (+2 more)

### Community 56 - "SparseIndex"
Cohesion: 0.22
Nodes (17): answer_with_abstention(), _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful(), test_no_context_reason_when_top_k_zero(), test_score_floor_reason() (+9 more)

### Community 57 - "SparseIndex"
Cohesion: 0.29
Nodes (8): _alias_keys(), Candidate alias lookup keys, most literal first.      Both the raw normalised fo, PMS/NCS/ILDS end in a literal S. Unconditional plural-stripping mapped     them, reg_id resolved purely through the alias table, ignoring the corpus., A table key that no _alias_keys() output can produce is dead config., _resolved(), test_acronyms_ending_in_s_reach_their_own_entry(), test_every_alias_entry_is_reachable_from_some_spelling()

### Community 58 - "discover_new.py"
Cohesion: 0.08
Nodes (44): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), int, str (+36 more)

### Community 59 - "corpus_spaces.py"
Cohesion: 0.25
Nodes (22): Answer, Protocol, Reranker, Embedder, Answer, Generator, Judge, demote_superseded() (+14 more)

### Community 60 - "eval.py"
Cohesion: 0.19
Nodes (14): _mps_available(), pick_device(), bool, str, Device + precision selection for Apple-Silicon inference.  Centralizes the mps/c, Resolve the compute device.      A truthy explicit `pref` ("mps"/"cpu"/"cuda") w, fp16 only on GPU-class devices; never on cpu. bf16 is never returned     here by, should_use_fp16() (+6 more)

### Community 61 - "test_integration_e2e.py"
Cohesion: 0.42
Nodes (8): mrr(), ndcg_at_k(), float, int, str, Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), test_retrieval_metrics()

### Community 62 - "test_pipeline.py"
Cohesion: 0.17
Nodes (17): assemble_pool(), main(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of, TREC-style pool: gold-doc literal matches lead, then round-robin over     [reran, LexicalReranker, Deterministic query-coverage reranker (test/fallback).      Score = fraction of, _HallucinatingGenerator, test_pipeline_flags_hallucinated_citation() (+9 more)

### Community 63 - "test_persistence.py"
Cohesion: 0.24
Nodes (17): main(), int, _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number(), _ocr_text() (+9 more)

### Community 64 - "faithfulness"
Cohesion: 0.13
Nodes (28): adjudicate(), _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini() (+20 more)

### Community 65 - "LexicalReranker"
Cohesion: 0.18
Nodes (13): Resolve a cited regulation name+year to a canonical reg_id.      Returns (reg_id, resolve_regulation(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6)., Singular/plural and dropped-stopword variants normalise to identical     token s, A citation carrying a spurious extra token still resolves, but only via     the, test_acronym_aliases_resolve_as_explicit_text(), test_alias_year_matters(), test_exact_name_resolves_as_explicit_text() (+5 more)

### Community 66 - "eval_harness.py"
Cohesion: 0.36
Nodes (7): _fmt(), main(), float, Path, str, Re-score archived benchmark runs with bootstrap CIs and paired significance.  Re, score_run()

### Community 67 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden.      `chunks` is optio, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 69 - "acquire_missing_pdfs.py"
Cohesion: 0.24
Nodes (14): _add_months(), check_robots(), main(), month_window(), date, float, int, str (+6 more)

### Community 70 - "Chunk"
Cohesion: 0.10
Nodes (36): main(), main(), RAGPipeline, smoke_pipeline(), main(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, RAGPipeline (+28 more)

### Community 71 - "HybridRetriever"
Cohesion: 0.27
Nodes (9): main(), _plausible(), bool, int, Path, str, Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, Every record's text must match the PDF its provenance names.      Slow (re-extra (+1 more)

### Community 72 - "scrape_regulations.py"
Cohesion: 0.25
Nodes (14): main(), parse_last_amended(), parse_listing(), int, str, Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY)., (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none. (+6 more)

### Community 73 - "resolve_chunk_spans"
Cohesion: 0.15
Nodes (15): _lin_chain(), P2 lineage / supersession resolution tests., test_build_lineage_edges_tiered(), test_build_lineage_inferred_master_topic_edge(), test_governing_on_before_family_exists(), test_governing_on_cycle_safe(), test_governing_on_linear_chain(), test_governing_on_parallel_branches_max_date_wins() (+7 more)

### Community 74 - "test_ingest_refs.py"
Cohesion: 0.20
Nodes (10): int, Human-readable regulation name. Year disambiguates same-short_name repeal     pa, Deterministic, stable identity slug. This is the edge target and join key., reg_display_name(), reg_id(), test_reg_display_name_composes_year(), test_reg_display_name_falls_back_without_year(), test_reg_id_is_a_deterministic_slug() (+2 more)

### Community 76 - "load_regulations"
Cohesion: 0.17
Nodes (17): annotate_master_fields(), consolidation_edges(), master_series(), int, str, Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan (+9 more)

### Community 77 - "discover_new.py"
Cohesion: 0.50
Nodes (4): docid(), str, Emit one JSON line listing SEBI circulars newer than previously seen. Uses a sta, title()

### Community 78 - "_alias_keys"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

### Community 79 - "test_ingest_pdf.py"
Cohesion: 0.11
Nodes (20): parse_meta(), _primary_number(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic     en-d, The mirror of the kerning case above. When the en-dash has spaces on     BOTH si, 2011-era master circulars use "SEBI/<DEPT>/MC No.<n>/<serial>/<year>",     match (+12 more)

### Community 81 - "paired_delta"
Cohesion: 0.21
Nodes (7): paired_delta(), float, str, Compare run `b` against run `a` on their shared queries.      Returns mean_b - m, Randomization p-values use the (count+1)/(n+1) estimator, so a         p-value o, One query flipping out of 56 is exactly the iv9-style verdict: the         rando, TestPairedDelta

### Community 83 - "load_regulations"
Cohesion: 0.16
Nodes (11): annotate_corpus(), _currency(), mc_topic(), Path, str, Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None.      Us, Update each corpus record's supersession_status + superseded_by + supersedes, Connected component over supersedes/superseded_by (both tiers). (+3 more)

### Community 84 - "audit_reg_edges.py"
Cohesion: 0.29
Nodes (14): ProportionCI, _emit(), main(), bool, int, Path, str, Precision audit for circular -> regulation edges (spec 2026-07-23 §7).  Emits a (+6 more)

### Community 86 - "test_eval_harness_v7.py"
Cohesion: 0.20
Nodes (19): _aggregate(), _eval_item(), EvalReport, _mean(), int, RAGPipeline, Golden-set evaluation harness (P1).  Runs the pipeline over a labelled golden se, report_dict() (+11 more)

### Community 87 - "bootstrap_ci"
Cohesion: 0.26
Nodes (5): bootstrap_ci(), int, Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must         be, TestBootstrapCI

### Community 88 - "load_golden_asof"
Cohesion: 0.18
Nodes (13): Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, AsofCaseResult, load_golden_asof(), As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, Aggregate case results with an exact confidence interval.      Pure function of, summarize(), _lin_chain(), P4b: as-of golden evaluation runner tests (offline). (+5 more)

### Community 89 - ".encode"
Cohesion: 0.19
Nodes (18): _current_model(), _extract_text(), main(), pilot(), _pilot_ids(), _post_local(), int, Path (+10 more)

### Community 90 - "load_golden"
Cohesion: 0.22
Nodes (8): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).  C, load_golden(), Path, str, test_eval_harness_metric_suite(), test_carry_preserves_ids_and_adds_v7_defaults()

### Community 91 - "test_repair_corpus_text.py"
Cohesion: 0.25
Nodes (3): Repair the 6 records whose body text was overwritten with one shared circular's, The repair map must name a real orphan PDF that parses to the circular_number it, test_numbers_normalize_distinctly()

### Community 92 - "test_injection.py"
Cohesion: 0.24
Nodes (9): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), str, Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns() (+1 more)

### Community 93 - "TestReadTrecRun"
Cohesion: 0.27
Nodes (7): float, Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}., read_trec_run(), write_trec_run(), test_trec_run_and_research_judges_are_sidecar_only(), The archived runfiles embed section headings in the doc id., TestReadTrecRun

### Community 95 - "main"
Cohesion: 0.23
Nodes (11): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, dataset_quality(), load_index_chunks(), main(), Chunk, Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation.  Outputs: (+3 more)

### Community 97 - ".test_mean_reproduces_the_archived_aggregate"
Cohesion: 0.40
Nodes (5): _parse_error_ids(), Path, Scans the per-row cache for `ids` and returns the ones flagged     parse_error:, Defensive: an id that was never adjudicated (no cache file at all)     is not re, test_parse_error_ids_skips_ids_with_no_cache_file()

### Community 101 - "Chunk"
Cohesion: 0.13
Nodes (21): _grounded_prompt(), _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), bool, Chunk (+13 more)

### Community 103 - "app.py"
Cohesion: 0.27
Nodes (9): build_ui(), get_pipeline(), _parse_as_of(), float, str, Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY (+1 more)

### Community 105 - ".encode"
Cohesion: 0.29
Nodes (5): bool, int, ndarray, str, _tokens()

### Community 107 - "Community 107"
Cohesion: 0.18
Nodes (11): detect_relations(), detect_relations_ex(), int, Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window(), A circular that names another circular BEFORE the supersede trigger     word mus, test_detect_relations_delegates_unchanged() (+3 more)

### Community 126 - "Community 126"
Cohesion: 0.22
Nodes (6): BootstrapCI, PairedResult, bool, Uncertainty quantification for benchmark runs.  The golden set is n=56 answerabl, True when the randomization test rejects at 1 - confidence AND the         paire, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 127 - "Community 127"
Cohesion: 0.50
Nodes (4): Rerun-safety for votes.jsonl itself (plan Task 10 decision #7): drops     every, _replace_annotator_votes(), test_replace_annotator_votes_drops_old_gemini_keeps_others_untouched(), test_replace_annotator_votes_on_empty_existing_just_returns_fresh()

## Knowledge Gaps
- **77 isolated node(s):** `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK`, `PYTHONPATH` (+72 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `Benchmark Infrastructure`, `.grounded`, `Embedder`, `Master Metadata`, `Export Integration`, `Chunk`, `test_gate.py`, `annotate_corpus`, `bench_rerankers.py`, `bench_retrieval.py`, `.encode`, `paired_delta`, `build_index.py`, `SparseIndex`, `corpus_spaces.py`, `test_pipeline.py`, `validate_golden_v7`, `Chunk`, `_alias_keys`, `test_injection.py`, `TestReadTrecRun`, `main`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Why does `Random` connect `Core RAG Pipeline` to `faithfulness`, `Index & Evaluation`, `audit_reg_edges.py`, `Dataset Export`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `.grounded` to `Benchmark Infrastructure`, `Chunk`, `Chunk`, `test_faithfulness.py`, `answer_with_abstention`, `Export Integration`, `test_eval_harness_v7.py`, `load_golden_asof`, `load_golden`, `corpus_spaces.py`, `TestReadTrecRun`, `test_pipeline.py`, `main`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 108 inferred relationships involving `Chunk` (e.g. with `Answer` and `Any`) actually correct?**
  _`Chunk` has 108 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `RAGPipeline` (e.g. with `Any` and `FastAPI`) actually correct?**
  _`RAGPipeline` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `HybridRetriever` (e.g. with `Answer` and `FastAPI`) actually correct?**
  _`HybridRetriever` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `HashEmbedder` (e.g. with `RAGPipeline` and `smoke_pipeline()`) actually correct?**
  _`HashEmbedder` has 49 INFERRED edges - model-reasoned connections that need verification._