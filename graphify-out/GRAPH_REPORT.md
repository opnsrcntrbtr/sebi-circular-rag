# Graph Report - SEBI circular RAG  (2026-07-30)

## Corpus Check
- 155 files · ~157,292 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2036 nodes · 4882 edges · 113 communities (102 shown, 11 thin omitted)
- Extraction: 73% EXTRACTED · 27% INFERRED · 0% AMBIGUOUS · INFERRED: 1297 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `644f384a`
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
- answer_with_abstention
- test_gate.py
- audit_reg_edges.py
- context_headers.py
- test_eval_harness_v7.py
- bootstrap_ci
- CircularMeta
- .encode
- load_golden
- test_repair_corpus_text.py
- test_injection.py
- TestReadTrecRun
- test_splade_leg.py
- main
- splade_encoder.py
- .test_mean_reproduces_the_archived_aggregate
- test_incremental_index.py
- corpus.py
- Chunk
- .load
- app.py
- _alias_keys
- .encode
- .retrieve
- filter_targeted_rows
- .test_mean_reproduces_the_archived_aggregate
- main
- str
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
- `test_legacy_string_entries_pass_through()` --calls--> `resolve_chunk_spans()`  [INFERRED]
  tests/test_golden_v7_resolver.py → src/sebi_rag/benchmark.py
- `test_sup04_override_generated_via_injected_callable()` --calls--> `HeaderGenerator`  [INFERRED]
  tests/test_select_targeted_headers.py → src/sebi_rag/context_headers.py
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py

## Import Cycles
- 1-file cycle: `src/sebi_rag/api.py -> src/sebi_rag/api.py`

## Communities (113 total, 11 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.07
Nodes (57): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), int, Path, str (+49 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.13
Nodes (40): main(), main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), chunks_by_doc() (+32 more)

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
Cohesion: 0.18
Nodes (42): BaseModel, FastAPI, bool, str, evaluate(), float, int, str (+34 more)

### Community 11 - "Benchmark Scripts"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 13 - "Lineage"
Cohesion: 0.19
Nodes (15): _pool(), int, str, Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external ann, Five pilot rows from five strata measure more than five from one -     the gemin, Vote records must say annotator "qwen" (never reuse "gemini" - the     agreement, Back-compat guard: the gemini leg (on hold, not removed) must keep     producing, Qwen-family models may emit <think>...</think> as inline text rather     than as (+7 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.10
Nodes (30): classify_answer(), classify_query(), _doc(), load_run(), main(), int, Path, str (+22 more)

### Community 15 - "Embedder"
Cohesion: 0.15
Nodes (26): CircularMeta, _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker., build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t, _keep(), load_circulars_from_hf() (+18 more)

### Community 16 - "Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "Master Metadata"
Cohesion: 0.22
Nodes (13): apply_context_headers(), HeaderGenerator, Chunk, Insert each chunk's header as a line below its breadcrumb line.      Pure and id, _chunk(), str, Contextual chunk headers (iv9): one lay+statutory sentence per deep chunk.  Offl, test_describe_cleans_markdown_and_newlines() (+5 more)

### Community 18 - "Export Integration"
Cohesion: 0.42
Nodes (8): _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through(), test_qrels_span_rows_get_grade_2(), test_resolves_normalized_whitespace_quote(), test_unresolvable_quote_returns_empty(), test_validator_flags_unresolvable_quote_when_chunks_given()

### Community 19 - "lineage.py"
Cohesion: 0.33
Nodes (5): main(), int, Dry-run audit of every circular_number renumber.py would change, with the docume, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 20 - "test_gate.py"
Cohesion: 0.09
Nodes (35): derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).  Write, metric -> per-query score vector, into gate-floor names -> floor value.      Met, floors_ok(), bool, Path, Which golden set gates CI, and whether its adjudicated subset clears the derived, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed     v7 gate, (+27 more)

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
Cohesion: 0.31
Nodes (10): build_report(), Assemble the persisted as-of run artifact.      Pipeline accuracy is the headlin, Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid     measureme, The headline number must be the 10 pipeline cases alone — the whole     point of, _results(), test_pipeline_metrics_are_not_polluted_by_selector_cases(), test_pooled_overall_carries_no_interval() (+2 more)

### Community 27 - "Ops Server"
Cohesion: 0.25
Nodes (7): BaseHTTPRequestHandler, Handler, bool, int, str, run_script(), smoketest()

### Community 28 - "trace_failure.py"
Cohesion: 0.29
Nodes (11): first_answer_rank(), first_gold_rank(), heading_only(), main(), int, str, Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no (+3 more)

### Community 29 - "test_gate.py"
Cohesion: 0.11
Nodes (18): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Emit one JSON line of retrieval/citation/abstention metrics using the persisted, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T (+10 more)

### Community 30 - "build_lineage"
Cohesion: 0.10
Nodes (39): Any, ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass() (+31 more)

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
Cohesion: 0.18
Nodes (13): csr_matrix, float, int, Path, str, SPLADE learned-sparse retrieval leg (iv11).  Non-destructive, opt-in third RRF l, SpladeIndex, _fake_encode() (+5 more)

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
Cohesion: 0.16
Nodes (15): HydeExpander, int, str, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), int, str, _rank() (+7 more)

### Community 47 - "bench_retrieval.py"
Cohesion: 0.16
Nodes (19): hierarchical_chunk(), _paragraphs(), int, str, Split into units each <= max_chars.      PDF-extracted text often lacks blank-li, Document -> section -> paragraph chunks with stable IDs.      A "section" is det, _body(), str (+11 more)

### Community 48 - ".encode"
Cohesion: 0.19
Nodes (15): Embedder, DenseIndex, _doc_checksum(), bool, Chunk, Embedder, ndarray, Path (+7 more)

### Community 49 - "answer_with_abstention"
Cohesion: 0.11
Nodes (13): _citation_meta(), create_app(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, /ready should trigger pipeline build and return ready=true., test_auth_required_when_key_set(), test_bge_fp16_encode_is_normalized(), test_citation_meta_defaults_when_circular_absent_from_index(), test_citation_meta_defaults_when_index_none() (+5 more)

### Community 50 - "bench_retrieval.py"
Cohesion: 0.33
Nodes (14): validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations(), test_duplicate_text_across_records_flagged(), test_empty_text_is_not_a_duplicate_cluster(), test_flags_bad_issue_date() (+6 more)

### Community 51 - "_compute_kwargs"
Cohesion: 0.06
Nodes (67): apply(), _body(), _claude_accuracy_ci(), cohen_kappa(), _confirms_claude(), decide(), _label(), _literals_by_row() (+59 more)

### Community 52 - "paired_delta"
Cohesion: 0.15
Nodes (19): expand_query(), str, Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic, _chunk(), int, str, Query-side lexical expansion (intervention #2, glossary variant).  Lay->statutor (+11 more)

### Community 53 - "bootstrap_ci"
Cohesion: 0.14
Nodes (22): fetch_manifest(), main(), float, int, str, Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:, diff_manifest(), _iso() (+14 more)

### Community 54 - "build_index.py"
Cohesion: 0.13
Nodes (16): bool, Chunk, float, int, str, qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2 (+8 more)

### Community 55 - "eval_harness.py"
Cohesion: 0.13
Nodes (22): Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, AsofCaseResult, load_golden_asof(), Lineage, Path, RAGPipeline, str, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde (+14 more)

### Community 56 - "SparseIndex"
Cohesion: 0.22
Nodes (12): auroc(), best_threshold(), evaluate(), main(), float, F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t (+4 more)

### Community 57 - "SparseIndex"
Cohesion: 0.14
Nodes (18): _build_chunks(), _build_pipeline(), _FixedReranker, Minimal end-to-end test of the SEBI RAG pipeline.  Runs fully offline (HashEmbed, Offline pipeline whose single circular rests on a repealed regulation., Deterministic reranker: score by doc_id lookup (test-only)., citations = all top_k contexts, so a demoted superseded chunk deep in     the co, Giant-family regression (golden asof-p8): OLD is superseded by two     same-day (+10 more)

### Community 58 - "discover_new.py"
Cohesion: 0.08
Nodes (44): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), int, str (+36 more)

### Community 59 - "corpus_spaces.py"
Cohesion: 0.42
Nodes (14): Answer, Protocol, Reranker, Answer, Generator, Judge, bool, Chunk (+6 more)

### Community 60 - "eval.py"
Cohesion: 0.19
Nodes (14): _mps_available(), pick_device(), bool, str, Device + precision selection for Apple-Silicon inference.  Centralizes the mps/c, Resolve the compute device.      A truthy explicit `pref` ("mps"/"cpu"/"cuda") w, fp16 only on GPU-class devices; never on cpu. bf16 is never returned     here by, should_use_fp16() (+6 more)

### Community 61 - "test_integration_e2e.py"
Cohesion: 0.42
Nodes (8): mrr(), ndcg_at_k(), float, int, str, Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), test_retrieval_metrics()

### Community 62 - "test_pipeline.py"
Cohesion: 0.17
Nodes (17): annotate_master_fields(), consolidation_edges(), master_series(), int, str, Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan (+9 more)

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
Cohesion: 0.22
Nodes (25): RAGPipeline, smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., build_lineage(), LexicalReranker (+17 more)

### Community 71 - "HybridRetriever"
Cohesion: 0.27
Nodes (9): main(), _plausible(), bool, int, Path, str, Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, Every record's text must match the PDF its provenance names.      Slow (re-extra (+1 more)

### Community 72 - "scrape_regulations.py"
Cohesion: 0.25
Nodes (14): main(), parse_last_amended(), parse_listing(), int, str, Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY)., (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none. (+6 more)

### Community 73 - "resolve_chunk_spans"
Cohesion: 0.15
Nodes (16): derive_regulatory_basis(), _jaccard(), load_regulations(), name_tokens(), float, Path, str, Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6).  Regulations (+8 more)

### Community 74 - "test_ingest_refs.py"
Cohesion: 0.20
Nodes (10): int, Human-readable regulation name. Year disambiguates same-short_name repeal     pa, Deterministic, stable identity slug. This is the edge target and join key., reg_display_name(), reg_id(), test_reg_display_name_composes_year(), test_reg_display_name_falls_back_without_year(), test_reg_id_is_a_deterministic_slug() (+2 more)

### Community 76 - "load_regulations"
Cohesion: 0.07
Nodes (41): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, annotate_corpus(), _currency(), detect_relations(), detect_relations_ex(), load_records(), mc_topic(), int (+33 more)

### Community 77 - "discover_new.py"
Cohesion: 0.50
Nodes (4): docid(), str, Emit one JSON line listing SEBI circulars newer than previously seen. Uses a sta, title()

### Community 78 - "_alias_keys"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

### Community 79 - "test_ingest_pdf.py"
Cohesion: 0.11
Nodes (20): parse_meta(), _primary_number(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic     en-d, The mirror of the kerning case above. When the en-dash has spaces on     BOTH si, 2011-era master circulars use "SEBI/<DEPT>/MC No.<n>/<serial>/<year>",     match (+12 more)

### Community 80 - "test_faithfulness.py"
Cohesion: 0.23
Nodes (12): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of, TREC-style pool: gold-doc literal matches lead, then round-robin over     [reran, int, One gold doc with `n` chunks that ALL contain the word "broker", so a     must_c, Regression (2026-07-25): a must_contain literal matching many gold-doc     chunk, _retriever(), _saturating_retriever() (+4 more)

### Community 81 - "paired_delta"
Cohesion: 0.21
Nodes (7): paired_delta(), float, str, Compare run `b` against run `a` on their shared queries.      Returns mean_b - m, Randomization p-values use the (count+1)/(n+1) estimator, so a         p-value o, One query flipping out of 56 is exactly the iv9-style verdict: the         rando, TestPairedDelta

### Community 82 - "answer_with_abstention"
Cohesion: 0.29
Nodes (12): answer_with_abstention(), faithfulness(), Check that every circular id the answer cites (in square brackets) was     actua, _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful() (+4 more)

### Community 83 - "test_gate.py"
Cohesion: 0.28
Nodes (10): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge() (+2 more)

### Community 84 - "audit_reg_edges.py"
Cohesion: 0.29
Nodes (14): ProportionCI, _emit(), main(), bool, int, Path, str, Precision audit for circular -> regulation edges (spec 2026-07-23 §7).  Emits a (+6 more)

### Community 85 - "context_headers.py"
Cohesion: 0.20
Nodes (10): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).  Resumable, in_scope(), load_headers(), bool, Path, Contextual chunk headers (iv9): one lay+statutory sentence per chunk.  Index-sid, Spec scope: depth>=3 numbered sub-clauses plus annex-family headings. (+2 more)

### Community 86 - "test_eval_harness_v7.py"
Cohesion: 0.20
Nodes (19): _aggregate(), _eval_item(), EvalReport, _mean(), int, RAGPipeline, Golden-set evaluation harness (P1).  Runs the pipeline over a labelled golden se, report_dict() (+11 more)

### Community 87 - "bootstrap_ci"
Cohesion: 0.26
Nodes (5): bootstrap_ci(), int, Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must         be, TestBootstrapCI

### Community 88 - "CircularMeta"
Cohesion: 0.25
Nodes (10): load_circulars(), Chunk, Path, str, CircularMeta, test_real_corpus_loads_with_provenance_fields(), _HallucinatingGenerator, test_pipeline_flags_hallucinated_citation() (+2 more)

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
Cohesion: 0.36
Nodes (4): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}., read_trec_run(), The archived runfiles embed section headings in the doc id., TestReadTrecRun

### Community 94 - "test_splade_leg.py"
Cohesion: 0.40
Nodes (8): _chunks(), _fake_encode(), Returns a fixed dense ranking regardless of query., _StubDense, _StubSparse, test_flag_off_is_unchanged_and_ignores_splade(), test_splade_leg_changes_fused_order_when_on(), test_use_splade_without_index_raises()

### Community 95 - "main"
Cohesion: 0.46
Nodes (7): dataset_quality(), load_index_chunks(), main(), Chunk, Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation.  Outputs:, write_card()

### Community 96 - "splade_encoder.py"
Cohesion: 0.28
Nodes (7): ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.  splad, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights., splade_pool(), SpladeEncoder, test_splade_pool_masked_positions_excluded(), test_splade_pool_max_over_sequence_with_log_relu_and_mask()

### Community 97 - ".test_mean_reproduces_the_archived_aggregate"
Cohesion: 0.40
Nodes (5): _parse_error_ids(), Path, Scans the per-row cache for `ids` and returns the ones flagged     parse_error:, Defensive: an id that was never adjudicated (no cache file at all)     is not re, test_parse_error_ids_skips_ids_with_no_cache_file()

### Community 98 - "test_incremental_index.py"
Cohesion: 0.39
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are e, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 99 - "corpus.py"
Cohesion: 0.25
Nodes (5): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).  Standalo, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10).  Pulls the i, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks.

### Community 101 - "Chunk"
Cohesion: 0.13
Nodes (21): _grounded_prompt(), _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), bool, Chunk (+13 more)

### Community 102 - ".load"
Cohesion: 0.25
Nodes (6): main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual, csr_matrix, float, int, str

### Community 103 - "app.py"
Cohesion: 0.27
Nodes (9): build_ui(), get_pipeline(), _parse_as_of(), float, str, Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY (+1 more)

### Community 104 - "_alias_keys"
Cohesion: 0.29
Nodes (8): _alias_keys(), Candidate alias lookup keys, most literal first.      Both the raw normalised fo, PMS/NCS/ILDS end in a literal S. Unconditional plural-stripping mapped     them, reg_id resolved purely through the alias table, ignoring the corpus., A table key that no _alias_keys() output can produce is dead config., _resolved(), test_acronyms_ending_in_s_reach_their_own_entry(), test_every_alias_entry_is_reachable_from_some_spelling()

### Community 105 - ".encode"
Cohesion: 0.29
Nodes (5): bool, int, ndarray, str, _tokens()

### Community 106 - ".retrieve"
Cohesion: 0.46
Nodes (5): float, int, Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 107 - "filter_targeted_rows"
Cohesion: 0.33
Nodes (6): filter_targeted_rows(), Keep only sidecar rows whose chunk belongs to a target document., Selection of targeted headers (iv10): filter iv9's reused headers down to 3 fail, test_filter_keeps_only_target_doc_rows(), test_filter_with_no_matches_returns_empty(), test_sup04_override_generated_via_injected_callable()

### Community 108 - ".test_mean_reproduces_the_archived_aggregate"
Cohesion: 0.38
Nodes (3): Ten chunks of one circular must not crowd the cutoff: the k applies         to u, End-to-end guarantee behind the re-scoring script: replaying a         runfile y, TestPerQueryRecall

### Community 109 - "main"
Cohesion: 0.60
Nodes (4): _load_items(), main(), Path, Pool-width sweep (intervention #3): answer-level rescue rate vs reranker latency

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

- **Why does `Chunk` connect `Chunk` to `Benchmark Infrastructure`, `.grounded`, `Embedder`, `Master Metadata`, `Chunk`, `test_gate.py`, `build_lineage`, `bench_rerankers.py`, `bench_retrieval.py`, `.encode`, `paired_delta`, `build_index.py`, `SparseIndex`, `corpus_spaces.py`, `validate_golden_v7`, `Chunk`, `_alias_keys`, `answer_with_abstention`, `test_gate.py`, `context_headers.py`, `CircularMeta`, `test_injection.py`, `test_splade_leg.py`, `main`, `corpus.py`, `.retrieve`, `str`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `.grounded` to `Benchmark Infrastructure`, `Chunk`, `Chunk`, `.test_mean_reproduces_the_archived_aggregate`, `Embedder`, `.encode`, `answer_with_abstention`, `TestReadTrecRun`, `test_eval_harness_v7.py`, `eval_harness.py`, `CircularMeta`, `SparseIndex`, `load_golden`, `corpus_spaces.py`, `test_gate.py`, `build_lineage`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `Random` connect `Core RAG Pipeline` to `faithfulness`, `Index & Evaluation`, `audit_reg_edges.py`, `Dataset Export`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 108 inferred relationships involving `Chunk` (e.g. with `Answer` and `Any`) actually correct?**
  _`Chunk` has 108 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `RAGPipeline` (e.g. with `Any` and `FastAPI`) actually correct?**
  _`RAGPipeline` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `HybridRetriever` (e.g. with `Answer` and `FastAPI`) actually correct?**
  _`HybridRetriever` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `HashEmbedder` (e.g. with `RAGPipeline` and `smoke_pipeline()`) actually correct?**
  _`HashEmbedder` has 49 INFERRED edges - model-reasoned connections that need verification._