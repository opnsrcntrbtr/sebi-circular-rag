# Graph Report - SEBI circular RAG  (2026-07-30)

## Corpus Check
- 157 files · ~159,571 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2067 nodes · 4044 edges · 294 communities (82 shown, 212 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 244 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e3547699`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_golden_v7_packet.py
- benchmark.py
- test_reg_lineage.py
- test_golden_v7_gemini.py
- export_datasets.py
- test_export_integration.py
- clopper_pearson_ci
- test_dataset_cards.py
- derive_validity
- test_export_datasets.py
- api.py
- test_ui.py
- test_scrape_regulations.py
- test_golden_v7_local.py
- extract_misses.py
- Settings
- test_scrape_sebi.py
- context_headers.py
- test_golden_v7_resolver.py
- main
- test_golden_v7_gate.py
- test_spaces.py
- test_audit_reg_edges.py
- extract_citations
- test_app_zerogpu.py
- test_push_datasets.py
- lineage.py
- Handler
- trace_failure.py
- segment.py
- telemetry_engine.py
- scrape_sebi.py
- run.sh
- canary.sh
- refresh.sh
- test_app_asof.py
- HybridRetriever
- deploy_space.py
- discover.sh
- upload_spaces_index.py
- HashEmbedder
- ingest_pdf.py
- reg_display_name
- run_ops.sh
- notify.sh
- conftest.py
- test_hyde.py
- hierarchical_chunk
- .load
- test_api.py
- remap_doc_ids.py
- test_golden_v7_agreement.py
- retrieve.py
- build_regulatory_index
- Qwen3MLXReranker
- test_eval_asof.py
- float
- RAGPipeline
- backfill_escalations.py
- Answer
- pick_device
- test_pipeline.py
- consolidation_edges
- test_golden_v7_pool.py
- gemini_adjudicate.py
- test_regulations.py
- float
- validate_golden_v7
- Chunk
- eval_gate.py
- RAGPipeline
- bool
- test_every_alias_target_is_in_force_or_has_a_succession_entry
- regulations.py
- int
- sebi-rag
- Lineage
- test_benchmark.py
- parse_meta
- int
- float
- answer_with_abstention
- test_gate.py
- bool
- bool
- test_eval_harness_v7.py
- int
- adjudicate_draft.py
- local_adjudicate.py
- load_golden
- normalize_circular_number
- test_injection.py
- read_trec_run
- eval_harness.py
- main
- splade_encoder.py
- adjudicate
- test_ingest_refs.py
- float
- test_build_reg_edges.py
- write_jsonl
- .test_mean_reproduces_the_archived_aggregate
- int
- test_annotation_adds_no_circular_meta_field
- float
- str
- bytes
- CircularMeta
- float
- int
- str
- int
- str
- int
- bool
- bool
- int
- str
- int
- str
- str
- int
- str
- float
- int
- str
- str
- Chunk
- float
- int
- str
- bool
- float
- str
- int
- str
- int
- float
- str
- bool
- bool
- float
- int
- str
- int
- str
- int
- str
- str
- int
- str
- int
- str
- bool
- float
- int
- str
- bool
- int
- str
- str
- int
- str
- int
- str
- bool
- float
- int
- str
- int
- str
- float
- int
- str
- SpacesSettings
- Lineage
- RAGPipeline
- Settings
- str
- RAGPipeline
- str
- Chunk
- float
- int
- RAGPipeline
- str
- Chunk
- str
- Chunk
- str
- bool
- Chunk
- int
- object
- Settings
- str
- bool
- str
- bool
- int
- str
- Lineage
- RAGPipeline
- str
- int
- RAGPipeline
- str
- float
- int
- str
- str
- bool
- Chunk
- float
- int
- str
- Chunk
- object
- str
- int
- str
- bool
- int
- str
- float
- int
- str
- int
- str
- str
- bool
- Chunk
- Embedder
- float
- int
- Lineage
- str
- bool
- int
- str
- int
- str
- float
- str
- bool
- Chunk
- float
- int
- str
- bool
- Chunk
- Embedder
- float
- int
- str
- int
- str
- bool
- object
- str
- int
- str
- float
- int
- str
- str
- bool
- float
- str
- RAGPipeline
- str
- str
- int
- str
- str
- bool
- str
- int
- str
- int
- str
- int
- str
- str
- str
- bool
- float
- int
- str
- str
- str
- float
- str

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 89 edges
2. `RAGPipeline` - 44 edges
3. `hierarchical_chunk()` - 43 edges
4. `HashEmbedder` - 42 edges
5. `ExtractiveStubGenerator` - 38 edges
6. `CircularMeta` - 36 edges
7. `Lineage` - 33 edges
8. `build_lineage()` - 31 edges
9. `LexicalReranker` - 28 edges
10. `SubjectSimJudge` - 25 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py
- `test_chunks_config_refuses_header_and_maps_fields()` --indirect_call--> `Chunk`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/segment.py
- `get_pipeline()` --calls--> `build_spaces_pipeline()`  [INFERRED]
  app.py → src/sebi_rag/api_spaces.py
- `get_pipeline()` --calls--> `ExtractiveStubGenerator`  [INFERRED]
  app.py → src/sebi_rag/generate.py

## Import Cycles
- None detected.

## Communities (294 total, 212 thin omitted)

### Community 0 - "test_golden_v7_packet.py"
Cohesion: 0.07
Nodes (52): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+44 more)

### Community 1 - "benchmark.py"
Cohesion: 0.17
Nodes (25): main(), main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), dir_fingerprint() (+17 more)

### Community 2 - "test_reg_lineage.py"
Cohesion: 0.15
Nodes (29): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair. The merged edge carries the…, Set regulations / primary_regulation / regulatory_basis_status in place.…, Stub records for cited regulations absent from the Updated List. Returns NEW…, synthesise_repealed_stubs(), _circ(), parametrize (+21 more)

### Community 3 - "test_golden_v7_gemini.py"
Cohesion: 0.12
Nodes (26): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape). Non-abstain…, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing,…, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as "confirms…, A non-abstain row whose pool happens to have zero candidates can't offer any…, Decision #3: a valid letter alongside an unrecognized one invalidates the WHOLE…, letters=[] is how adjudicate signals an abstain/zero-candidate row; parse_reply… (+18 more)

### Community 4 - "export_datasets.py"
Cohesion: 0.06
Nodes (70): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+62 more)

### Community 5 - "test_export_integration.py"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 6 - "clopper_pearson_ci"
Cohesion: 0.06
Nodes (28): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+20 more)

### Community 7 - "test_dataset_cards.py"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 8 - "derive_validity"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation. Locked…, Validity of one circular from the tiered edge list (any scope: the function…, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 9 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 10 - "api.py"
Cohesion: 0.11
Nodes (32): BaseModel, FastAPI, main(), main(), main(), build_default_pipeline(), _citation_meta(), CitationMeta (+24 more)

### Community 11 - "test_ui.py"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 13 - "test_golden_v7_local.py"
Cohesion: 0.15
Nodes (19): _extract_text(), Qwen-family models may emit <think>...</think> reasoning as inline text,…, Anthropic Messages response -> reply text: concatenates `text` content blocks,…, _strip_thinking(), _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external…, Five pilot rows from five strata measure more than five from one - the gemini…, Vote records must say annotator "qwen" (never reuse "gemini" - the agreement… (+11 more)

### Community 14 - "extract_misses.py"
Cohesion: 0.14
Nodes (23): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).…, Answer-level classification: a candidate chunk qualifies if it contains any… (+15 more)

### Community 15 - "Settings"
Cohesion: 0.18
Nodes (18): _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker., build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux). Parallel…, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf() (+10 more)

### Community 16 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "context_headers.py"
Cohesion: 0.08
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 18 - "test_golden_v7_resolver.py"
Cohesion: 0.38
Nodes (9): chunks_by_doc(), _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through(), test_qrels_span_rows_get_grade_2(), test_resolves_normalized_whitespace_quote(), test_unresolvable_quote_returns_empty() (+1 more)

### Community 19 - "main"
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 20 - "test_golden_v7_gate.py"
Cohesion: 0.08
Nodes (40): Emit one JSON line of retrieval/citation/abstention metrics using the persisted…, derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the…, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,… (+32 more)

### Community 21 - "test_spaces.py"
Cohesion: 0.06
Nodes (49): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only). Gradio SDK…, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict ISO YYYY-…, run_query_spaces(), warm_up_gpu() (+41 more)

### Community 22 - "test_audit_reg_edges.py"
Cohesion: 0.21
Nodes (10): ProportionCI, _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected() (+2 more)

### Community 23 - "extract_citations"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).…, All regulation citations in a circular, one per occurrence (not deduped).…, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years. "Regulations… (+24 more)

### Community 24 - "test_app_zerogpu.py"
Cohesion: 0.14
Nodes (13): app_module(), fixture, Regression coverage for the ZeroGPU-hardware workaround in app.py. Background:…, Inject a fake `spaces` module so app.py's `import spaces` succeeds offline, and…, Static guard: if `import spaces` or the `@spaces.GPU` decorator is ever…, It must stay dead code: calling it would request a real ZeroGPU allocation (and…, The functions actually on the request path (get_pipeline, run_query_spaces)…, `hardware:` in README-spaces.md is not a documented Spaces config key (only… (+5 more)

### Community 25 - "test_push_datasets.py"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default:…, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 26 - "lineage.py"
Cohesion: 0.10
Nodes (16): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped…, Emit one JSON line listing SEBI circulars newer than previously seen. Uses a…, _currency(), detect_relations(), detect_relations_ex(), mc_topic(), P2 — cross-document supersession resolution. Classifies each circular's…, Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None. Used… (+8 more)

### Community 27 - "Handler"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 29 - "segment.py"
Cohesion: 0.14
Nodes (14): Reranker, Benchmark MLX generators on the golden set: faithfulness, groundedness,…, Retrieval-only benchmark with TREC runfile and reproducibility metadata. Use…, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the…, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.…, End-to-end wiring: segment -> hybrid retrieve -> rerank -> generate/abstain., Protocol, Stage-2 reranking (mandatory, D4). Cross-encoder in production; a deterministic… (+6 more)

### Community 30 - "telemetry_engine.py"
Cohesion: 0.10
Nodes (39): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+31 more)

### Community 31 - "scrape_sebi.py"
Cohesion: 0.05
Nodes (60): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+52 more)

### Community 32 - "run.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 33 - "canary.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 34 - "refresh.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 35 - "test_app_asof.py"
Cohesion: 0.29
Nodes (3): app_module(), fixture, As-of date plumbing in the Spaces UI (app.py).

### Community 36 - "HybridRetriever"
Cohesion: 0.13
Nodes (17): HybridRetriever, csr_matrix, Path, SPLADE learned-sparse retrieval leg (iv11). Non-destructive, opt-in third RRF…, SpladeIndex, _fake_encode(), _chunks(), _fake_encode() (+9 more)

### Community 40 - "HashEmbedder"
Cohesion: 0.15
Nodes (17): HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable…, CircularMeta, _HallucinatingGenerator, test_pipeline_flags_hallucinated_citation(), test_numeric_miner_requires_numeric_pattern(), test_paraphrase_skips_preamble_and_short_chunks(), _chunks() (+9 more)

### Community 41 - "ingest_pdf.py"
Cohesion: 0.15
Nodes (19): Re-derive circular number + dates from each record's stored text and rewrite…, _existing_numbers(), extract_text(), ingest(), main(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars. Drop a circular PDF into data/raw/ and… (+11 more)

### Community 42 - "reg_display_name"
Cohesion: 0.25
Nodes (10): Human-readable regulation name. Year disambiguates same-short_name repeal pairs…, reg_display_name(), build_ui(), _empty_outputs(), _parse_as_of(), Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO YYYY-MM-DD.…, submit_query() (+2 more)

### Community 46 - "test_hyde.py"
Cohesion: 0.17
Nodes (11): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —…, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_none_and_empty_hyde_are_identical_to_baseline() (+3 more)

### Community 47 - "hierarchical_chunk"
Cohesion: 0.14
Nodes (20): load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., hierarchical_chunk(), _paragraphs(), Split into units each <= max_chars. PDF-extracted text often lacks blank-line…, Document -> section -> paragraph chunks with stable IDs. A "section" is…, test_real_corpus_loads_with_provenance_fields() (+12 more)

### Community 48 - ".load"
Cohesion: 0.10
Nodes (19): Embedder, ndarray, Protocol, _tokens(), DenseIndex, _doc_checksum(), ndarray, Path (+11 more)

### Community 49 - "test_api.py"
Cohesion: 0.12
Nodes (10): integration, create_app(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit,…, /ready should trigger pipeline build and return ready=true., test_auth_required_when_key_set(), test_bge_fp16_encode_is_normalized(), test_citation_meta_reports_superseded(), test_query_exceeds_time_budget_returns_504() (+2 more)

### Community 50 - "remap_doc_ids.py"
Cohesion: 0.33
Nodes (10): main(), Rewrite golden_v7 doc references after the corpus renumbering (2026-07-25…, remap(), Doc-id remapping after the 2026-07-25 corpus renumbering (Task 4)., _row(), test_input_rows_are_not_mutated(), test_matching_is_normalization_insensitive(), test_remaps_must_not_cite() (+2 more)

### Community 51 - "test_golden_v7_agreement.py"
Cohesion: 0.06
Nodes (64): apply(), _body(), _claude_accuracy_ci(), cohen_kappa(), _confirms_claude(), decide(), _label(), _literals_by_row() (+56 more)

### Community 52 - "retrieve.py"
Cohesion: 0.09
Nodes (23): Build the dense+sparse index once and persist it (run after corpus changes).…, expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and…, Stage-1 hybrid retrieval: dense (FAISS) + sparse (BM25) fused by RRF. Mandatory…, BM25 lexical index (bm25s)., Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse() (+15 more)

### Community 53 - "build_regulatory_index"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer. Read-only…, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 54 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 55 - "test_eval_asof.py"
Cohesion: 0.13
Nodes (26): AsofCaseResult, build_report(), load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Aggregate case results with an exact confidence interval. Pure function of the…, run_pipeline_cases() (+18 more)

### Community 57 - "RAGPipeline"
Cohesion: 0.22
Nodes (18): smoke_pipeline(), ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., build_lineage(), RAGPipeline, LexicalReranker, Deterministic query-coverage reranker (test/fallback). Score = fraction of…, _CannedGenerator (+10 more)

### Community 58 - "backfill_escalations.py"
Cohesion: 0.12
Nodes (28): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+20 more)

### Community 60 - "pick_device"
Cohesion: 0.20
Nodes (11): pick_device(), Device + precision selection for Apple-Silicon inference. Centralizes the…, Resolve the compute device. A truthy explicit `pref` ("mps"/"cpu"/"cuda") wins.…, fp16 only on GPU-class devices; never on cpu. bf16 is never returned here by…, should_use_fp16(), Device + fp16 policy selection (no real torch/mps required)., test_pick_device_auto_cpu_when_no_mps(), test_pick_device_auto_mps_when_available() (+3 more)

### Community 61 - "test_pipeline.py"
Cohesion: 0.18
Nodes (16): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), _build_chunks(), _build_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline. Runs fully offline…, Offline pipeline whose single circular rests on a repealed regulation. (+8 more)

### Community 62 - "consolidation_edges"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans…, _master(), test_annotate_idempotent() (+7 more)

### Community 63 - "test_golden_v7_pool.py"
Cohesion: 0.26
Nodes (11): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, One gold doc with `n` chunks that ALL contain the word "broker", so a…, Regression (2026-07-25): a must_contain literal matching many gold-doc chunks…, _retriever(), _saturating_retriever(), test_bm25_leg_uses_raw_query_not_expansion() (+3 more)

### Community 64 - "gemini_adjudicate.py"
Cohesion: 0.11
Nodes (23): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec… (+15 more)

### Community 65 - "test_regulations.py"
Cohesion: 0.09
Nodes (29): _alias_keys(), load_regulations(), name_tokens(), Path, Candidate alias lookup keys, most literal first. Both the raw normalised form…, Resolve a cited regulation name+year to a canonical reg_id. Returns (reg_id,…, Load data/corpus/regulations.jsonl into a list of regulation records. Thin…, Comparison tokens: lowercased, punctuation-split, stopwords dropped, naively… (+21 more)

### Community 67 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 68 - "Chunk"
Cohesion: 0.13
Nodes (18): Generator, _grounded_prompt(), Judge, _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no() (+10 more)

### Community 69 - "eval_gate.py"
Cohesion: 0.29
Nodes (5): contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-…, demote_superseded(), Down-weight reranked (chunk, score) pairs from superseded circulars and re-…, test_demote_superseded_puts_in_force_on_top()

### Community 73 - "regulations.py"
Cohesion: 0.13
Nodes (16): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7).…, Yield (circular, Citation) for every citation occurrence in the corpus., derive_regulatory_basis(), _jaccard(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6). Regulations…, Regulatory-basis status of one circular from its resolved regulations.…, Deterministic, stable identity slug. This is the edge target and join key. (+8 more)

### Community 76 - "Lineage"
Cohesion: 0.11
Nodes (22): annotate_corpus(), Lineage, Path, Update each corpus record's supersession_status + superseded_by + supersedes…, Connected component over supersedes/superseded_by (both tiers)., The circular in this family that governs on date as_of (ISO), or None when…, _lin_chain(), P2 lineage / supersession resolution tests. (+14 more)

### Community 78 - "test_benchmark.py"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

### Community 79 - "parse_meta"
Cohesion: 0.15
Nodes (17): Pattern, _iso_date(), _labeled_date(), parse_meta(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash… (+9 more)

### Community 82 - "answer_with_abstention"
Cohesion: 0.13
Nodes (18): Answer, answer_with_abstention(), faithfulness(), Max cosine(query, doc subject line) over contexts — the primary gate signal,…, Check that every circular id the answer cites (in square brackets) was actually…, Max cosine(query, section heading) over contexts — the second tier., Map any cited circular that is superseded -> the circular(s) superseding it.…, superseded_citations() (+10 more)

### Community 83 - "test_gate.py"
Cohesion: 0.28
Nodes (10): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge() (+2 more)

### Community 86 - "test_eval_harness_v7.py"
Cohesion: 0.42
Nodes (11): run_eval(), test_eval_harness_metric_suite(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-…, _row(), test_as_of_is_passed_to_pipeline(), test_chunk_metrics_computed_for_span_rows(), test_gate_is_none_when_nothing_adjudicated() (+3 more)

### Community 88 - "adjudicate_draft.py"
Cohesion: 0.29
Nodes (10): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX. Reads draft rows from…, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+2 more)

### Community 89 - "local_adjudicate.py"
Cohesion: 0.19
Nodes (15): Transient-failure predicate for the real Gemini call: rate limiting (429) and…, Same per-row deterministic shuffle as make_packet.py's write_packet:…, _should_retry(), _shuffled_candidates(), _current_model(), main(), pilot(), _pilot_ids() (+7 more)

### Community 90 - "load_golden"
Cohesion: 0.28
Nodes (6): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).…, load_golden(), Path, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 91 - "normalize_circular_number"
Cohesion: 0.18
Nodes (7): main(), Repair the 6 records whose body text was overwritten with one shared circular's…, normalize_circular_number(), Canonical COMPARISON key for a circular number: strip whitespace and trailing…, test_dedup_uses_normalized_numbers(), The repair map must name a real orphan PDF that parses to the circular_number…, test_numbers_normalize_distinctly()

### Community 92 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 93 - "read_trec_run"
Cohesion: 0.17
Nodes (10): _fmt(), main(), Path, Re-score archived benchmark runs with bootstrap CIs and paired significance.…, score_run(), Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), write_trec_run() (+2 more)

### Community 94 - "eval_harness.py"
Cohesion: 0.12
Nodes (23): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,…, evaluate(), Calibrate top_k and the abstention threshold against the citation-precision… (+15 more)

### Community 95 - "main"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

### Community 96 - "splade_encoder.py"
Cohesion: 0.15
Nodes (12): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.…, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+4 more)

### Community 97 - "adjudicate"
Cohesion: 0.22
Nodes (10): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt) -> str`…, Scans the per-row cache for `ids` and returns the ones flagged parse_error:…, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct from a well-…, Defensive: an id that was never adjudicated (no cache file at all) is not…, test_adjudicate_marks_parse_error_for_garbled_abstain_protocol_reply() (+2 more)

### Community 99 - "test_ingest_refs.py"
Cohesion: 0.15
Nodes (11): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_fulltext_fallback_returns_earliest_body_reference() (+3 more)

### Community 104 - "test_build_reg_edges.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 107 - "write_jsonl"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl()

### Community 108 - ".test_mean_reproduces_the_archived_aggregate"
Cohesion: 0.38
Nodes (3): Ten chunks of one circular must not crowd the cutoff: the k applies to unique…, End-to-end guarantee behind the re-scoring script: replaying a runfile yields…, TestPerQueryRecall

## Knowledge Gaps
- **226 isolated node(s):** `sebi-rag`, `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS` (+221 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **212 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `benchmark.py`, `api.py`, `Settings`, `context_headers.py`, `test_golden_v7_resolver.py`, `test_spaces.py`, `segment.py`, `HybridRetriever`, `test_hyde.py`, `hierarchical_chunk`, `.load`, `retrieve.py`, `Qwen3MLXReranker`, `RAGPipeline`, `validate_golden_v7`, `eval_gate.py`, `test_benchmark.py`, `answer_with_abstention`, `test_gate.py`, `test_injection.py`, `eval_harness.py`, `main`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `hierarchical_chunk()` connect `hierarchical_chunk` to `Chunk`, `HashEmbedder`, `api.py`, `.test_mean_reproduces_the_archived_aggregate`, `Settings`, `.load`, `test_golden_v7_resolver.py`, `test_pipeline.py`, `test_eval_harness_v7.py`, `RAGPipeline`, `segment.py`, `test_golden_v7_pool.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAGPipeline` to `benchmark.py`, `Chunk`, `HybridRetriever`, `HashEmbedder`, `api.py`, `Lineage`, `.test_mean_reproduces_the_archived_aggregate`, `Settings`, `.load`, `test_api.py`, `answer_with_abstention`, `test_eval_harness_v7.py`, `test_eval_asof.py`, `segment.py`, `eval_harness.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `CitationMeta`) actually correct?**
  _`RAGPipeline` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `HashEmbedder` (e.g. with `_CannedGenerator` and `_SlowGenerator`) actually correct?**
  _`HashEmbedder` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `ExtractiveStubGenerator` (e.g. with `get_pipeline()` and `main()`) actually correct?**
  _`ExtractiveStubGenerator` has 14 INFERRED edges - model-reasoned connections that need verification._