# Graph Report - SEBI circular RAG  (2026-07-30)

## Corpus Check
- 155 files · ~156,716 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2030 nodes · 4868 edges · 98 communities (88 shown, 10 thin omitted)
- Extraction: 73% EXTRACTED · 27% INFERRED · 0% AMBIGUOUS · INFERRED: 1297 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `05146bc6`
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
- audit_reg_edges.py
- test_eval_harness_v7.py
- bootstrap_ci
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
- `test_citation_meta_defaults_when_circular_absent_from_index()` --calls--> `_citation_meta()`  [INFERRED]
  tests/test_api.py → src/sebi_rag/api.py
- `test_citation_meta_defaults_when_index_none()` --calls--> `_citation_meta()`  [INFERRED]
  tests/test_api.py → src/sebi_rag/api.py
- `test_citation_meta_fills_regulatory_fields()` --calls--> `_citation_meta()`  [INFERRED]
  tests/test_api.py → src/sebi_rag/api.py
- `test_run_metadata_has_reproducibility_fields()` --calls--> `run_metadata()`  [INFERRED]
  tests/test_benchmark.py → src/sebi_rag/benchmark.py

## Import Cycles
- 1-file cycle: `src/sebi_rag/api.py -> src/sebi_rag/api.py`

## Communities (98 total, 10 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.11
Nodes (38): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), int, Path, str (+30 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.17
Nodes (33): Any, main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), chunks_by_doc() (+25 more)

### Community 2 - "Data Processing"
Cohesion: 0.13
Nodes (33): annotate_regulation_fields(), build_regulation_edges(), int, One `cites` edge per (circular, regulation) pair.      The merged edge carries t, Set regulations / primary_regulation / regulatory_basis_status in place.      Re, Stub records for cited regulations absent from the Updated List.      Returns NE, synthesise_repealed_stubs(), _circ() (+25 more)

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
Cohesion: 0.13
Nodes (59): BaseModel, FastAPI, bool, str, evaluate(), float, int, str (+51 more)

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
Cohesion: 0.19
Nodes (17): CircularMeta, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), bool, Chunk (+9 more)

### Community 16 - "Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "Master Metadata"
Cohesion: 0.08
Nodes (33): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).  Resumable, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10).  Pulls the i, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+25 more)

### Community 18 - "Export Integration"
Cohesion: 0.42
Nodes (8): _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through(), test_qrels_span_rows_get_grade_2(), test_resolves_normalized_whitespace_quote(), test_unresolvable_quote_returns_empty(), test_validator_flags_unresolvable_quote_when_chunks_given()

### Community 19 - "lineage.py"
Cohesion: 0.33
Nodes (5): main(), int, Dry-run audit of every circular_number renumber.py would change, with the docume, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 20 - "test_gate.py"
Cohesion: 0.06
Nodes (44): derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).  Write, metric -> per-query score vector, into gate-floor names -> floor value.      Met, floors_ok(), bool, Path, Which golden set gates CI, and whether its adjudicated subset clears the derived, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed     v7 gate, (+36 more)

### Community 21 - "Chunk"
Cohesion: 0.11
Nodes (27): SpacesSettings, ExternalSpaceGenerator, HFGenerator, HybridGenerator, Chunk, object, str, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement (+19 more)

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
Cohesion: 0.18
Nodes (16): AsofCaseResult, build_report(), Assemble the persisted as-of run artifact.      Pipeline accuracy is the headlin, Aggregate case results with an exact confidence interval.      Pure function of, summarize(), Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid     measureme, The headline number must be the 10 pipeline cases alone — the whole     point of (+8 more)

### Community 27 - "Ops Server"
Cohesion: 0.25
Nodes (7): BaseHTTPRequestHandler, Handler, bool, int, str, run_script(), smoketest()

### Community 28 - "trace_failure.py"
Cohesion: 0.29
Nodes (11): first_answer_rank(), first_gold_rank(), heading_only(), main(), int, str, Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no (+3 more)

### Community 29 - "test_gate.py"
Cohesion: 0.07
Nodes (37): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Emit one JSON line of retrieval/citation/abstention metrics using the persisted (+29 more)

### Community 30 - "build_lineage"
Cohesion: 0.10
Nodes (32): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_safety_limit(), correction_pass(), fetch_omlx_metrics(), get_hardware_state() (+24 more)

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
Nodes (43): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).  Standalo, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual, csr_matrix, float, int, ndarray (+35 more)

### Community 40 - "test_incremental_index.py"
Cohesion: 0.19
Nodes (18): _as_bool(), _get(), bool, object, Path, str, Settings.load() plus the [spaces] table as settings.spaces.*          Load order, Resolve a setting: env var > config dict > default. (+10 more)

### Community 41 - "test_integration_e2e.py"
Cohesion: 0.12
Nodes (17): Pattern, Re-derive circular number + dates from each record's stored text and rewrite the, _iso_date(), _labeled_date(), Local PDF ingestion for SEBI circulars.  Drop a circular PDF into data/raw/ and, Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104",     "HO/ (, Standard formats (old CIR, new SEBI/HO, free-form 2026): first     slash-heavy H, Department-only prefixes without HO/CIR anchor,     e.g. AFD/P/CIR/2022/125. (+9 more)

### Community 42 - "UI Components"
Cohesion: 0.31
Nodes (9): build_ui(), _empty_outputs(), _parse_as_of(), bool, float, str, Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO     YYYY-MM-D (+1 more)

### Community 46 - "bench_rerankers.py"
Cohesion: 0.22
Nodes (9): HydeExpander, int, str, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, HyDE expander (Part B): query -> hypothetical statutory passage.  Offline only —, test_generation_error_returns_empty(), test_output_truncated_to_max_chars(), test_prompt_contains_query_and_style_cue() (+1 more)

### Community 47 - "bench_retrieval.py"
Cohesion: 0.07
Nodes (49): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of, TREC-style pool: gold-doc literal matches lead, then round-robin over     [reran, _body(), main(), _mid(), mine_lineage_pairs(), mine_multi_hop() (+41 more)

### Community 48 - ".encode"
Cohesion: 0.09
Nodes (27): DenseIndex, _doc_checksum(), bool, Chunk, Embedder, float, int, ndarray (+19 more)

### Community 49 - "answer_with_abstention"
Cohesion: 0.10
Nodes (11): FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, /ready should trigger pipeline build and return ready=true., test_auth_required_when_key_set(), test_bge_fp16_encode_is_normalized(), test_citation_meta_defaults_when_circular_absent_from_index(), test_citation_meta_defaults_when_index_none(), test_citation_meta_fills_regulatory_fields(), test_citation_meta_reports_superseded() (+3 more)

### Community 50 - "bench_retrieval.py"
Cohesion: 0.33
Nodes (14): validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations(), test_duplicate_text_across_records_flagged(), test_empty_text_is_not_a_duplicate_cluster(), test_flags_bad_issue_date() (+6 more)

### Community 51 - "_compute_kwargs"
Cohesion: 0.06
Nodes (67): apply(), _body(), _claude_accuracy_ci(), cohen_kappa(), _confirms_claude(), decide(), _label(), _literals_by_row() (+59 more)

### Community 52 - "paired_delta"
Cohesion: 0.20
Nodes (14): expand_query(), str, Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic, Query-side lexical expansion (intervention #2, glossary variant).  Lay->statutor, test_all_five_sparse_failure_queries_expand(), test_expanded_sparse_query_hits_statutory_chunk(), test_lay_term_gains_statutory_synonym() (+6 more)

### Community 53 - "bootstrap_ci"
Cohesion: 0.21
Nodes (14): fetch_manifest(), main(), float, int, str, Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:, _iso(), parse_listing() (+6 more)

### Community 54 - "build_index.py"
Cohesion: 0.15
Nodes (12): bool, Chunk, float, int, str, qwen3_rerank_prompt(), int, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran (+4 more)

### Community 55 - "eval_harness.py"
Cohesion: 0.33
Nodes (8): diff_manifest(), Assign exactly one status to every listed row + extra_in_corpus rows., _rec(), _row(), test_coverage_pct_excludes_unfetchable(), test_diff_statuses(), test_summarize_and_markdown(), test_write_reports()

### Community 56 - "SparseIndex"
Cohesion: 0.20
Nodes (10): main(), contexts_for(), demote_superseded(), float, Down-weight reranked (chunk, score) pairs from superseded circulars and     re-s, Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, test_demote_superseded_puts_in_force_on_top() (+2 more)

### Community 57 - "SparseIndex"
Cohesion: 0.29
Nodes (10): build_regulatory_index(), str, Per-circular regulatory-basis lookup for the query/citation layer.      Read-onl, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present() (+2 more)

### Community 58 - "discover_new.py"
Cohesion: 0.08
Nodes (44): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), int, str (+36 more)

### Community 59 - "corpus_spaces.py"
Cohesion: 0.45
Nodes (15): Answer, Protocol, Reranker, Embedder, Answer, Generator, Judge, bool (+7 more)

### Community 60 - "eval.py"
Cohesion: 0.19
Nodes (14): _mps_available(), pick_device(), bool, str, Device + precision selection for Apple-Silicon inference.  Centralizes the mps/c, Resolve the compute device.      A truthy explicit `pref` ("mps"/"cpu"/"cuda") w, fp16 only on GPU-class devices; never on cpu. bf16 is never returned     here by, should_use_fp16() (+6 more)

### Community 61 - "test_integration_e2e.py"
Cohesion: 0.42
Nodes (8): mrr(), ndcg_at_k(), float, int, str, Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), test_retrieval_metrics()

### Community 62 - "test_pipeline.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 63 - "test_persistence.py"
Cohesion: 0.24
Nodes (17): main(), int, _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number(), _ocr_text() (+9 more)

### Community 64 - "faithfulness"
Cohesion: 0.13
Nodes (28): adjudicate(), _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini() (+20 more)

### Community 65 - "LexicalReranker"
Cohesion: 0.09
Nodes (29): _alias_keys(), load_regulations(), name_tokens(), Path, Candidate alias lookup keys, most literal first.      Both the raw normalised fo, Resolve a cited regulation name+year to a canonical reg_id.      Returns (reg_id, Load data/corpus/regulations.jsonl into a list of regulation records.      Thin, Comparison tokens: lowercased, punctuation-split, stopwords dropped,     naively (+21 more)

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
Nodes (51): RAGPipeline, smoke_pipeline(), load_circulars(), Chunk, Path, str, HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a (+43 more)

### Community 71 - "HybridRetriever"
Cohesion: 0.27
Nodes (9): main(), _plausible(), bool, int, Path, str, Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, Every record's text must match the PDF its provenance names.      Slow (re-extra (+1 more)

### Community 72 - "scrape_regulations.py"
Cohesion: 0.25
Nodes (14): main(), parse_last_amended(), parse_listing(), int, str, Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY)., (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none. (+6 more)

### Community 73 - "resolve_chunk_spans"
Cohesion: 0.46
Nodes (7): load_jsonl(), main(), int, Path, str, Build circular -> regulation edges and annotate the corpus (offline).  No networ, write_jsonl()

### Community 74 - "test_ingest_refs.py"
Cohesion: 0.12
Nodes (21): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7)., Yield (circular, Citation) for every citation occurrence in the corpus., derive_regulatory_basis(), _jaccard(), float, int, str (+13 more)

### Community 76 - "load_regulations"
Cohesion: 0.05
Nodes (57): annotate_corpus(), build_lineage(), _currency(), detect_relations(), detect_relations_ex(), load_records(), mc_topic(), int (+49 more)

### Community 77 - "discover_new.py"
Cohesion: 0.50
Nodes (4): docid(), str, Emit one JSON line listing SEBI circulars newer than previously seen. Uses a sta, title()

### Community 78 - "_alias_keys"
Cohesion: 0.36
Nodes (6): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields(), test_trec_run_and_research_judges_are_sidecar_only()

### Community 79 - "test_ingest_pdf.py"
Cohesion: 0.11
Nodes (20): parse_meta(), _primary_number(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic     en-d, The mirror of the kerning case above. When the en-dash has spaces on     BOTH si, 2011-era master circulars use "SEBI/<DEPT>/MC No.<n>/<serial>/<year>",     match (+12 more)

### Community 80 - "test_faithfulness.py"
Cohesion: 0.50
Nodes (5): _chunk(), int, str, _rank(), test_hyde_leg_improves_paraphrase_gap_rank()

### Community 81 - "paired_delta"
Cohesion: 0.21
Nodes (7): paired_delta(), float, str, Compare run `b` against run `a` on their shared queries.      Returns mean_b - m, Randomization p-values use the (count+1)/(n+1) estimator, so a         p-value o, One query flipping out of 56 is exactly the iv9-style verdict: the         rando, TestPairedDelta

### Community 84 - "audit_reg_edges.py"
Cohesion: 0.29
Nodes (14): ProportionCI, _emit(), main(), bool, int, Path, str, Precision audit for circular -> regulation edges (spec 2026-07-23 §7).  Emits a (+6 more)

### Community 86 - "test_eval_harness_v7.py"
Cohesion: 0.18
Nodes (21): _aggregate(), _doc(), _eval_item(), EvalReport, _mean(), int, RAGPipeline, str (+13 more)

### Community 87 - "bootstrap_ci"
Cohesion: 0.26
Nodes (5): bootstrap_ci(), int, Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must         be, TestBootstrapCI

### Community 89 - ".encode"
Cohesion: 0.19
Nodes (18): _current_model(), _extract_text(), main(), pilot(), _pilot_ids(), _post_local(), int, Path (+10 more)

### Community 90 - "load_golden"
Cohesion: 0.24
Nodes (7): main(), carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).  C, load_golden(), Path, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 91 - "test_repair_corpus_text.py"
Cohesion: 0.25
Nodes (3): Repair the 6 records whose body text was overwritten with one shared circular's, The repair map must name a real orphan PDF that parses to the circular_number it, test_numbers_normalize_distinctly()

### Community 92 - "test_injection.py"
Cohesion: 0.24
Nodes (9): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), str, Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns() (+1 more)

### Community 93 - "TestReadTrecRun"
Cohesion: 0.17
Nodes (11): per_query_recall(), float, Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}., Per-query recall@k at circular level, matching `run_retrieval_benchmark`.      A, read_trec_run(), write_trec_run(), The archived runfiles embed section headings in the doc id., Ten chunks of one circular must not crowd the cutoff: the k applies         to u (+3 more)

### Community 95 - "main"
Cohesion: 0.46
Nodes (7): dataset_quality(), load_index_chunks(), main(), Chunk, Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation.  Outputs:, write_card()

### Community 97 - ".test_mean_reproduces_the_archived_aggregate"
Cohesion: 0.40
Nodes (5): _parse_error_ids(), Path, Scans the per-row cache for `ids` and returns the ones flagged     parse_error:, Defensive: an id that was never adjudicated (no cache file at all)     is not re, test_parse_error_ids_skips_ids_with_no_cache_file()

### Community 101 - "Chunk"
Cohesion: 0.09
Nodes (37): RAGPipeline, answer_with_abstention(), faithfulness(), _grounded_prompt(), _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice() (+29 more)

### Community 103 - "app.py"
Cohesion: 0.27
Nodes (9): build_ui(), get_pipeline(), _parse_as_of(), float, str, Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY (+1 more)

### Community 105 - ".encode"
Cohesion: 0.29
Nodes (5): bool, int, ndarray, str, _tokens()

### Community 126 - "Community 126"
Cohesion: 0.22
Nodes (6): BootstrapCI, PairedResult, bool, Uncertainty quantification for benchmark runs.  The golden set is n=56 answerabl, True when the randomization test rejects at 1 - confidence AND the         paire, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 127 - "Community 127"
Cohesion: 0.50
Nodes (4): Rerun-safety for votes.jsonl itself (plan Task 10 decision #7): drops     every, _replace_annotator_votes(), test_replace_annotator_votes_drops_old_gemini_keeps_others_untouched(), test_replace_annotator_votes_on_empty_existing_just_returns_fresh()

## Knowledge Gaps
- **77 isolated node(s):** `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK`, `PYTHONPATH` (+72 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `Benchmark Infrastructure`, `.grounded`, `Embedder`, `Master Metadata`, `Chunk`, `test_gate.py`, `annotate_corpus`, `bench_retrieval.py`, `.encode`, `build_index.py`, `SparseIndex`, `corpus_spaces.py`, `validate_golden_v7`, `Chunk`, `_alias_keys`, `test_faithfulness.py`, `test_injection.py`, `TestReadTrecRun`, `main`?**
  _High betweenness centrality (0.169) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `.grounded` to `Benchmark Infrastructure`, `Answer Generation`, `Chunk`, `Chunk`, `test_gate.py`, `test_eval_harness_v7.py`, `load_golden`, `corpus_spaces.py`, `TestReadTrecRun`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `Random` connect `Core RAG Pipeline` to `faithfulness`, `Index & Evaluation`, `Dataset Export`, `bench_retrieval.py`, `audit_reg_edges.py`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 108 inferred relationships involving `Chunk` (e.g. with `Answer` and `Any`) actually correct?**
  _`Chunk` has 108 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `RAGPipeline` (e.g. with `Any` and `FastAPI`) actually correct?**
  _`RAGPipeline` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `HybridRetriever` (e.g. with `Answer` and `FastAPI`) actually correct?**
  _`HybridRetriever` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `HashEmbedder` (e.g. with `RAGPipeline` and `smoke_pipeline()`) actually correct?**
  _`HashEmbedder` has 49 INFERRED edges - model-reasoned connections that need verification._