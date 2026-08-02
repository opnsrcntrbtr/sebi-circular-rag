# Graph Report - SEBI circular RAG  (2026-08-03)

## Corpus Check
- 163 files · ~165,859 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2166 nodes · 4191 edges · 297 communities (100 shown, 197 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 968 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `418faa74`
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
- Chunk
- Qwen3MLXReranker
- test_eval_asof.py
- float
- hierarchical_chunk
- backfill_escalations.py
- Answer
- pick_device
- .load
- consolidation_edges
- test_pipeline.py
- gemini_adjudicate.py
- test_regulations.py
- float
- validate_golden_v7
- Chunk
- HybridRetriever
- RAGPipeline
- bool
- remap_doc_ids.py
- regulations.py
- int
- validate_golden
- Lineage
- app.py
- segment.py
- seed_v7.py
- int
- float
- answer_with_abstention
- test_build_reg_edges.py
- bool
- bool
- test_eval_harness_v7.py
- int
- adjudicate_draft.py
- local_adjudicate.py
- build_regulatory_index
- normalize_circular_number
- test_injection.py
- autoresearch.sh
- corpus.py
- main
- splade_encoder.py
- adjudicate
- build_report
- test_ingest_refs.py
- bootstrap_ci
- float
- write_jsonl
- test_annotation_adds_no_circular_meta_field
- test_every_alias_target_is_in_force_or_has_a_succession_entry
- acquire_missing_pdfs.py
- measure.py
- generate.py
- main
- int
- test_measure.py
- rescore_runs.py
- TestReadTrecRun
- MeasureResult
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
- discover_new.py
- sweep_rrf_k.py
- measure_mrr
- measure_parsing_latency
- measure_retrieval_recall
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
- .encode
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
- int
- str
- float
- int
- str
- str
- measure_temporal_accuracy
- RAGPipeline
- str
- str
- int
- str
- TestPerQueryRecall
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
- _rejoin_split
- measure.sh
- start_phoenix.sh

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 63 edges
2. `RAGPipeline` - 48 edges
3. `hierarchical_chunk()` - 44 edges
4. `HashEmbedder` - 41 edges
5. `CircularMeta` - 40 edges
6. `ExtractiveStubGenerator` - 38 edges
7. `build_lineage()` - 32 edges
8. `Lineage` - 30 edges
9. `LexicalReranker` - 28 edges
10. `MeasureResult` - 26 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_bge_fp16_encode_is_normalized()` --calls--> `BGEM3Embedder`  [INFERRED]
  tests/test_api.py → src/sebi_rag/embeddings.py
- `test_numbers_normalize_distinctly()` --calls--> `normalize_circular_number()`  [INFERRED]
  tests/test_repair_corpus_text.py → src/sebi_rag/ingest_pdf.py
- `test_parse_meta_dept_order_document_end_to_end()` --calls--> `parse_meta()`  [INFERRED]
  tests/test_ingest_refs.py → src/sebi_rag/ingest_pdf.py
- `test_parse_meta_excludes_prefix_variant_self_reference()` --calls--> `parse_meta()`  [INFERRED]
  tests/test_ingest_refs.py → src/sebi_rag/ingest_pdf.py

## Import Cycles
- None detected.

## Communities (297 total, 197 thin omitted)

### Community 0 - "test_golden_v7_packet.py"
Cohesion: 0.07
Nodes (52): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV ingest, Writes the blind human packet for `human_ids` (a subset of `ids`, the     full e (+44 more)

### Community 1 - "benchmark.py"
Cohesion: 0.16
Nodes (27): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), chunks_by_doc(), dir_fingerprint() (+19 more)

### Community 2 - "test_reg_lineage.py"
Cohesion: 0.16
Nodes (28): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair.      The merged edge carries t, Set regulations / primary_regulation / regulatory_basis_status in place.      Re, Stub records for cited regulations absent from the Updated List.      Returns NE, synthesise_repealed_stubs(), _circ(), Regulation edges + corpus annotation (spec 2026-07-23 §3.3, §3.4, §3.7). (+20 more)

### Community 3 - "test_golden_v7_gemini.py"
Cohesion: 0.12
Nodes (26): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape).     Non-abst, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing, a, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as     "confirms abs, A non-abstain row whose pool happens to have zero candidates can't     offer any, Decision #3: a valid letter alongside an unrecognized one invalidates     the WH, letters=[] is how adjudicate signals an abstain/zero-candidate row;     parse_re (+18 more)

### Community 4 - "export_datasets.py"
Cohesion: 0.08
Nodes (50): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+42 more)

### Community 5 - "test_export_integration.py"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 6 - "clopper_pearson_ci"
Cohesion: 0.24
Nodes (4): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion.      Use this for stri, The reason for the switch. On 9/10 the percentile bootstrap returns         [0.7, TestClopperPearson

### Community 7 - "test_dataset_cards.py"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 8 - "derive_validity"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 9 - "test_export_datasets.py"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 10 - "api.py"
Cohesion: 0.20
Nodes (16): Path, main(), _as_bool(), _get(), Settings.load() plus the [spaces] table as settings.spaces.*          Load order, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default, _clear() (+8 more)

### Community 11 - "test_ui.py"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 13 - "test_golden_v7_local.py"
Cohesion: 0.19
Nodes (12): _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external ann, Five pilot rows from five strata measure more than five from one -     the gemin, Vote records must say annotator "qwen" (never reuse "gemini" - the     agreement, Back-compat guard: the gemini leg (on hold, not removed) must keep     producing, Qwen-family models may emit <think>...</think> as inline text rather     than as, _row(), test_adjudicate_default_annotator_stays_gemini() (+4 more)

### Community 14 - "extract_misses.py"
Cohesion: 0.08
Nodes (35): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any (+27 more)

### Community 15 - "Settings"
Cohesion: 0.29
Nodes (10): _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path).  Loads the pu, One HF dataset config as plain dicts (network; cached by `datasets`)., Full-circular records (dicts) for build_lineage() — always the     "corpus" conf (+2 more)

### Community 16 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "context_headers.py"
Cohesion: 0.08
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).  Resumable, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10).  Pulls the i, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 18 - "test_golden_v7_resolver.py"
Cohesion: 0.10
Nodes (41): Answer, get_pipeline(), Cache one pipeline per mode; both share retriever/reranker/lineage., BaseModel, Build the full pipeline with real models., real_pipeline(), main(), main() (+33 more)

### Community 19 - "main"
Cohesion: 0.19
Nodes (20): run_retrieval_benchmark(), _aggregate(), _doc(), _eval_item(), EvalReport, _mean(), Golden-set evaluation harness (P1).  Runs the pipeline over a labelled golden se, report_dict() (+12 more)

### Community 20 - "test_golden_v7_gate.py"
Cohesion: 0.09
Nodes (34): derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).  Write, metric -> per-query score vector, into gate-floor names -> floor value.      Met, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the derived, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed     v7 gate,, True iff every floor's metric is present in `report_gate` and meets it.      Mis (+26 more)

### Community 21 - "test_spaces.py"
Cohesion: 0.10
Nodes (23): Generator, ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, Fallback generator: small instruct model via transformers on CPU. (+15 more)

### Community 22 - "test_audit_reg_edges.py"
Cohesion: 0.21
Nodes (10): ProportionCI, _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected() (+2 more)

### Community 23 - "extract_citations"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).  Deliber, All regulation citations in a circular, one per occurrence (not deduped).      S, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years.      "Regulations (+24 more)

### Community 24 - "test_app_zerogpu.py"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 25 - "test_push_datasets.py"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 26 - "lineage.py"
Cohesion: 0.15
Nodes (12): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).  Standalo, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.  splad, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+4 more)

### Community 27 - "Handler"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 29 - "segment.py"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan, _master(), test_annotate_idempotent() (+7 more)

### Community 30 - "telemetry_engine.py"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 31 - "scrape_sebi.py"
Cohesion: 0.16
Nodes (16): diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13).  Pure functions only: l, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows., render_markdown() (+8 more)

### Community 32 - "run.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 33 - "canary.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 34 - "refresh.sh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 36 - "HybridRetriever"
Cohesion: 0.21
Nodes (14): _current_model(), _extract_text(), main(), pilot(), _pilot_ids(), _post_local(), Path, External annotation slice: local-model leg via oMLX - the PRIMARY leg since 2026 (+6 more)

### Community 40 - "HashEmbedder"
Cohesion: 0.10
Nodes (43): Embedder, Lineage, smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., LexicalReranker (+35 more)

### Community 41 - "ingest_pdf.py"
Cohesion: 0.12
Nodes (24): Re-derive circular number + dates from each record's stored text and rewrite the, main(), Repair the 6 records whose body text was overwritten with one shared circular's, _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number() (+16 more)

### Community 42 - "reg_display_name"
Cohesion: 0.33
Nodes (8): build_ui(), _empty_outputs(), _parse_as_of(), Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO     YYYY-MM-D, SSRF guard: reject URLs pointing to private/internal/reserved addresses.      Bl, submit_query(), _validate_api_url()

### Community 46 - "test_hyde.py"
Cohesion: 0.17
Nodes (11): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage.  Offline only —, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_none_and_empty_hyde_are_identical_to_baseline() (+3 more)

### Community 47 - "hierarchical_chunk"
Cohesion: 0.18
Nodes (8): csr_matrix, Path, SPLADE learned-sparse retrieval leg (iv11).  Non-destructive, opt-in third RRF l, SpladeIndex, _fake_encode(), Return an encode fn mapping known texts to known dense weight rows., test_save_load_roundtrip_and_guard(), test_search_ranks_by_sparse_dot_product()

### Community 48 - ".load"
Cohesion: 0.12
Nodes (18): Protocol, Embedder, Reranker, DenseIndex, _doc_checksum(), ndarray, Path, Stage-1 hybrid retrieval: dense (FAISS) + sparse (BM25) fused by RRF.  Mandatory (+10 more)

### Community 49 - "test_api.py"
Cohesion: 0.11
Nodes (15): FastAPI, _citation_meta(), create_app(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, /ready should trigger pipeline build and return ready=true., test_auth_required_when_key_set(), test_bge_fp16_encode_is_normalized(), test_citation_meta_defaults_when_circular_absent_from_index() (+7 more)

### Community 50 - "remap_doc_ids.py"
Cohesion: 0.39
Nodes (6): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), Automated metric collection for the SEBI Circular RAG pipeline.  Six on-demand m, test_retrieval_metrics()

### Community 51 - "test_golden_v7_agreement.py"
Cohesion: 0.06
Nodes (64): apply(), _body(), _claude_accuracy_ci(), cohen_kappa(), _confirms_claude(), decide(), _label(), _literals_by_row() (+56 more)

### Community 52 - "retrieve.py"
Cohesion: 0.22
Nodes (13): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic, Query-side lexical expansion (intervention #2, glossary variant).  Lay->statutor, test_all_five_sparse_failure_queries_expand(), test_expanded_sparse_query_hits_statutory_chunk(), test_lay_term_gains_statutory_synonym(), test_multiword_synonym_splits_into_tokens() (+5 more)

### Community 53 - "Chunk"
Cohesion: 0.30
Nodes (11): _norm_ws(), Span {doc, quote} -> matching chunk ids (all overlap matches count).      Legacy, resolve_chunk_spans(), _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through(), test_qrels_span_rows_get_grade_2() (+3 more)

### Community 54 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 55 - "test_eval_asof.py"
Cohesion: 0.17
Nodes (15): AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, Aggregate case results with an exact confidence interval.      Pure function of, run_pipeline_cases(), run_selector_cases(), summarize() (+7 more)

### Community 57 - "hierarchical_chunk"
Cohesion: 0.10
Nodes (25): Build the dense+sparse index once and persist it (run after corpus changes)., load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., hierarchical_chunk(), _paragraphs(), Segmentation: hierarchical chunking + metadata + stable citation IDs.  Minimal,, Split into units each <= max_chars.      PDF-extracted text often lacks blank-li (+17 more)

### Community 58 - "backfill_escalations.py"
Cohesion: 0.11
Nodes (32): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate (2026-07-25 (+24 more)

### Community 59 - "Answer"
Cohesion: 0.30
Nodes (9): HybridRetriever, _chunks(), _fake_encode(), Returns a fixed dense ranking regardless of query., _StubDense, _StubSparse, test_flag_off_is_unchanged_and_ignores_splade(), test_splade_leg_changes_fused_order_when_on() (+1 more)

### Community 60 - "pick_device"
Cohesion: 0.20
Nodes (11): pick_device(), Device + precision selection for Apple-Silicon inference.  Centralizes the mps/c, Resolve the compute device.      A truthy explicit `pref` ("mps"/"cpu"/"cuda") w, fp16 only on GPU-class devices; never on cpu. bf16 is never returned     here by, should_use_fp16(), Device + fp16 policy selection (no real torch/mps required)., test_pick_device_auto_cpu_when_no_mps(), test_pick_device_auto_mps_when_available() (+3 more)

### Community 61 - ".load"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries.      Returns mean_b - m, Randomization p-values use the (count+1)/(n+1) estimator, so a         p-value o, One query flipping out of 56 is exactly the iv9-style verdict: the         rando, TestPairedDelta

### Community 62 - "consolidation_edges"
Cohesion: 0.17
Nodes (8): _bootstrap_ci(), _git_commit(), _mps_memory(), Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict., When torch+MPS available, returns memory stats dict., TestHelpers

### Community 63 - "test_pipeline.py"
Cohesion: 0.29
Nodes (10): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7).  Emits a, Up to `n` edges, spread as evenly as possible across evidence tiers.      Tiers, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+2 more)

### Community 64 - "gemini_adjudicate.py"
Cohesion: 0.10
Nodes (26): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec 2026-0 (+18 more)

### Community 65 - "test_regulations.py"
Cohesion: 0.10
Nodes (25): load_regulations(), name_tokens(), Path, Resolve a cited regulation name+year to a canonical reg_id.      Returns (reg_id, Load data/corpus/regulations.jsonl into a list of regulation records.      Thin, Human-readable regulation name. Year disambiguates same-short_name repeal     pa, Comparison tokens: lowercased, punctuation-split, stopwords dropped,     naively, reg_display_name() (+17 more)

### Community 67 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden.      `chunks` is optio, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 68 - "Chunk"
Cohesion: 0.46
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are e, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 69 - "HybridRetriever"
Cohesion: 0.26
Nodes (11): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of, TREC-style pool: gold-doc literal matches lead, then round-robin over     [reran, One gold doc with `n` chunks that ALL contain the word "broker", so a     must_c, Regression (2026-07-25): a must_contain literal matching many gold-doc     chunk, _retriever(), _saturating_retriever(), test_bm25_leg_uses_raw_query_not_expansion() (+3 more)

### Community 72 - "remap_doc_ids.py"
Cohesion: 0.27
Nodes (10): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY)., (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'.      Takes the LAST bracket group, _record() (+2 more)

### Community 73 - "regulations.py"
Cohesion: 0.09
Nodes (24): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7)., Yield (circular, Citation) for every citation occurrence in the corpus., _alias_keys(), derive_regulatory_basis(), _jaccard(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6).  Regulations, Candidate alias lookup keys, most literal first.      Both the raw normalised fo (+16 more)

### Community 75 - "validate_golden"
Cohesion: 0.53
Nodes (4): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails()

### Community 76 - "Lineage"
Cohesion: 0.06
Nodes (43): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, contexts_for(), annotate_corpus(), build_lineage(), _currency(), demote_superseded(), detect_relations(), Lineage (+35 more)

### Community 77 - "app.py"
Cohesion: 0.67
Nodes (3): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:

### Community 78 - "segment.py"
Cohesion: 0.09
Nodes (20): Reranker, Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Build a lightweight pipeline for --smoke mode.      Uses a stub retriever (no FA, smoke_pipeline(), Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Calibrate top_k and the abstention threshold against the citation-precision sign, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A (+12 more)

### Community 79 - "seed_v7.py"
Cohesion: 0.28
Nodes (6): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).  C, load_golden(), Path, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 82 - "answer_with_abstention"
Cohesion: 0.06
Nodes (40): Chunk, Answer, answer_with_abstention(), faithfulness(), _grounded_prompt(), _is_non_sebi_domain(), Judge, _judge_prompt() (+32 more)

### Community 83 - "test_build_reg_edges.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 86 - "test_eval_harness_v7.py"
Cohesion: 0.31
Nodes (10): build_report(), Assemble the persisted as-of run artifact.      Pipeline accuracy is the headlin, Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid     measureme, The headline number must be the 10 pipeline cases alone — the whole     point of, _results(), test_pipeline_metrics_are_not_polluted_by_selector_cases(), test_pooled_overall_carries_no_interval() (+2 more)

### Community 88 - "adjudicate_draft.py"
Cohesion: 0.23
Nodes (12): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX.  Reads draft rows from golden_v7.json, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+4 more)

### Community 89 - "local_adjudicate.py"
Cohesion: 0.23
Nodes (15): discover(), extract_pdf_urls(), fetch(), _listing_url(), looks_like_pdf(), main(), _page(), _parse_date() (+7 more)

### Community 90 - "build_regulatory_index"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer.      Read-onl, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 92 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 93 - "autoresearch.sh"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 94 - "corpus.py"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must         be, TestBootstrapCI

### Community 95 - "main"
Cohesion: 0.33
Nodes (14): validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations(), test_duplicate_text_across_records_flagged(), test_empty_text_is_not_a_duplicate_cluster(), test_flags_bad_issue_date() (+6 more)

### Community 96 - "splade_encoder.py"
Cohesion: 0.38
Nodes (5): build_ui(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces()

### Community 97 - "adjudicate"
Cohesion: 0.22
Nodes (10): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt)     -> str, Scans the per-row cache for `ids` and returns the ones flagged     parse_error:, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct     from a we, Defensive: an id that was never adjudicated (no cache file at all)     is not re, test_adjudicate_marks_parse_error_for_garbled_abstain_protocol_reply() (+2 more)

### Community 98 - "build_report"
Cohesion: 0.33
Nodes (3): Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 99 - "test_ingest_refs.py"
Cohesion: 0.11
Nodes (21): Pattern, main(), Dry-run audit of every circular_number renumber.py would change, with the docume, _header(), _iso_date(), _labeled_date(), parse_meta(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars. (+13 more)

### Community 101 - "bootstrap_ci"
Cohesion: 0.25
Nodes (5): BootstrapCI, PairedResult, Uncertainty quantification for benchmark runs.  The golden set is n=56 answerabl, True when the randomization test rejects at 1 - confidence AND the         paire, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 103 - "write_jsonl"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline).  No networ, write_jsonl()

### Community 106 - "acquire_missing_pdfs.py"
Cohesion: 0.26
Nodes (11): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+3 more)

### Community 107 - "measure.py"
Cohesion: 0.18
Nodes (10): detect_relations_ex(), Like detect_relations, but returns dict records with evidence spans., _window(), measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine.      Samples c, Verify a supersession edge by cross-referencing corpus records.      Returns "tr, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference. (+2 more)

### Community 108 - "generate.py"
Cohesion: 0.43
Nodes (6): _body(), main(), _norm(), pick(), Label the 7 rows re-pooled after the assemble_pool fix (2026-07-25 remediation T, (candidate, quote) pairs for this row: the answer_contains carrier     first, th

### Community 109 - "main"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation.  Outputs:, write_card()

### Community 111 - "test_measure.py"
Cohesion: 0.28
Nodes (5): main(), metrics_to_markdown(), Format results as a markdown table., Unit tests for sebi_rag.measure — automated metric collection., TestCLI

### Community 112 - "rescore_runs.py"
Cohesion: 0.38
Nodes (6): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, Every record's text must match the PDF its provenance names.      Slow (re-extra, validate_deep()

### Community 113 - "TestReadTrecRun"
Cohesion: 0.29
Nodes (4): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}., read_trec_run(), write_trec_run(), The archived runfiles embed section headings in the doc id.

### Community 114 - "MeasureResult"
Cohesion: 0.24
Nodes (6): measure_context_precision(), MeasureReport, MeasureResult, Fraction of top-k chunks from relevant circulars.      Unlike recall@k (which is, TestContextPrecision, TestDataClasses

### Community 155 - "int"
Cohesion: 0.25
Nodes (5): Path, Run all (or specified) metrics sequentially., run_all_metrics(), Empty metrics list is falsy → defaults to ALL_METRICS., TestRegistry

### Community 223 - "sweep_rrf_k.py"
Cohesion: 0.53
Nodes (5): main(), mrr(), ndcg_at_k(), Sweep RRF k_const values on the golden set. No index rebuild needed., recall_at_k()

### Community 224 - "measure_mrr"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level.      For each query, RR = 1/rank of firs, TestMRR

### Community 225 - "measure_parsing_latency"
Cohesion: 0.38
Nodes (4): measure_parsing_latency(), Measure PDF ingestion throughput (chars/sec, ms/PDF).      Samples 20 PDFs strat, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 226 - "measure_retrieval_recall"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 277 - "measure_temporal_accuracy"
Cohesion: 0.43
Nodes (3): measure_temporal_accuracy(), Measure fraction of as_of queries returning correct pre-supersession     circula, TestTemporalAccuracy

### Community 285 - "TestPerQueryRecall"
Cohesion: 0.23
Nodes (8): _fmt(), main(), Path, Re-score archived benchmark runs with bootstrap CIs and paired significance.  Re, score_run(), per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.      A, Ten chunks of one circular must not crowd the cutoff: the k applies         to u

### Community 304 - "_rejoin_split"
Cohesion: 0.17
Nodes (10): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104",     "HO/ (, References split across tokens: merge up to 4 tokens after the first     HO/CIR/, _rejoin_split(), _s_anchor_merge(), Regression matrix for SEBI reference-number extraction.  One case per known form, test_fulltext_fallback_returns_earliest_body_reference(), test_parse_meta_dept_order_document_end_to_end() (+2 more)

## Knowledge Gaps
- **209 isolated node(s):** `autoresearch.sh script`, `PYTHONPATH`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `measure.sh script` (+204 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **197 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `.load` to `benchmark.py`, `Settings`, `context_headers.py`, `test_golden_v7_resolver.py`, `test_spaces.py`, `HashEmbedder`, `test_hyde.py`, `Chunk`, `Qwen3MLXReranker`, `hierarchical_chunk`, `Answer`, `validate_golden_v7`, `validate_golden`, `Lineage`, `segment.py`, `answer_with_abstention`, `test_injection.py`, `build_report`, `main`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `test_golden_v7_resolver.py` to `measure_mrr`, `benchmark.py`, `measure_parsing_latency`, `measure_retrieval_recall`, `HashEmbedder`, `measure.py`, `segment.py`, `test_api.py`, `remap_doc_ids.py`, `main`, `MeasureResult`, `measure_temporal_accuracy`, `test_eval_asof.py`, `int`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `build_regulatory_index()` connect `build_regulatory_index` to `regulations.py`, `test_golden_v7_resolver.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `CitationMeta`) actually correct?**
  _`RAGPipeline` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `hierarchical_chunk()` (e.g. with `smoke_pipeline()` and `_distinct_pipeline()`) actually correct?**
  _`hierarchical_chunk()` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_CannedGenerator`) actually correct?**
  _`HashEmbedder` has 37 INFERRED edges - model-reasoned connections that need verification._