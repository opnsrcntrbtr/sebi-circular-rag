# Graph Report - SEBI circular RAG  (2026-07-31)

## Corpus Check
- 156 files · ~160,089 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2064 nodes · 4038 edges · 292 communities (86 shown, 206 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 236 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a7235032`
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
- acquire_missing_pdfs.py
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
- build_report
- test_ingest_refs.py
- golden_v7/__init__.py
- bootstrap_ci
- float
- app.py
- test_build_reg_edges.py
- floors_ok
- derive_thresholds.py
- .test_mean_reproduces_the_archived_aggregate
- int
- test_acquire_missing.py
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
1. `Chunk` - 66 edges
2. `RAGPipeline` - 44 edges
3. `hierarchical_chunk()` - 43 edges
4. `HashEmbedder` - 42 edges
5. `ExtractiveStubGenerator` - 37 edges
6. `CircularMeta` - 36 edges
7. `Lineage` - 33 edges
8. `build_lineage()` - 31 edges
9. `LexicalReranker` - 28 edges
10. `extract_citations()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py
- `_Boom` --uses--> `Generator`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/generate.py
- `_Canned` --uses--> `Generator`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/generate.py
- `get_pipeline()` --calls--> `ExtractiveStubGenerator`  [INFERRED]
  app.py → src/sebi_rag/generate.py

## Import Cycles
- None detected.

## Communities (292 total, 206 thin omitted)

### Community 0 - "test_golden_v7_packet.py"
Cohesion: 0.07
Nodes (52): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV…, Writes the blind human packet for `human_ids` (a subset of `ids`, the full… (+44 more)

### Community 1 - "benchmark.py"
Cohesion: 0.18
Nodes (24): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5. This does…, beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), dir_fingerprint(), enrich_golden_item() (+16 more)

### Community 2 - "test_reg_lineage.py"
Cohesion: 0.06
Nodes (57): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline). No…, write_jsonl(), annotate_regulation_fields(), build_regulation_edges(), build_regulatory_index() (+49 more)

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
Cohesion: 0.05
Nodes (33): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7). Emits a…, Up to `n` edges, spread as evenly as possible across evidence tiers. Tiers with…, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+25 more)

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
Cohesion: 0.13
Nodes (35): BaseModel, main(), main(), main(), main(), build_default_pipeline(), CitationMeta, QueryRequest (+27 more)

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
Cohesion: 0.22
Nodes (15): _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker., _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path). Loads the… (+7 more)

### Community 16 - "test_scrape_sebi.py"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "context_headers.py"
Cohesion: 0.08
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).…, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10). Pulls the…, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 18 - "test_golden_v7_resolver.py"
Cohesion: 0.27
Nodes (13): chunks_by_doc(), _norm_ws(), qrels_rows(), Span {doc, quote} -> matching chunk ids (all overlap matches count). Legacy…, resolve_chunk_spans(), _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row() (+5 more)

### Community 19 - "main"
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the…, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 20 - "test_golden_v7_gate.py"
Cohesion: 0.08
Nodes (39): derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).…, metric -> per-query score vector, into gate-floor names -> floor value. Metrics…, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the…, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed v7 gate,…, True iff every floor's metric is present in `report_gate` and meets it. Missing… (+31 more)

### Community 21 - "test_spaces.py"
Cohesion: 0.20
Nodes (12): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo. All classes implement…, External Space first; on ANY failure fall back to the local CPU model.…, Primary generator: calls a public LLM Space via gradio_client. Wired to…, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus). Never… (+4 more)

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
Cohesion: 0.13
Nodes (11): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped…, Build the dense+sparse index once and persist it (run after corpus changes).…, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-…, _currency(), demote_superseded(), mc_topic(), P2 — cross-document supersession resolution. Classifies each circular's… (+3 more)

### Community 27 - "Handler"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).…, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation (the…, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 29 - "segment.py"
Cohesion: 0.10
Nodes (23): Protocol, Reranker, Benchmark MLX generators on the golden set: faithfulness, groundedness,…, Retrieval-only benchmark with TREC runfile and reproducibility metadata. Use…, scripts/eval_asof.py, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the…, Emit one JSON line of retrieval/citation/abstention metrics using the persisted…, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.… (+15 more)

### Community 30 - "telemetry_engine.py"
Cohesion: 0.10
Nodes (39): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+31 more)

### Community 31 - "scrape_sebi.py"
Cohesion: 0.19
Nodes (21): sebi_rag/verify_master.py, diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13). Pure functions only:…, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows. (+13 more)

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
Cohesion: 0.07
Nodes (28): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).…, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual…, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.…, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+20 more)

### Community 40 - "HashEmbedder"
Cohesion: 0.13
Nodes (34): smoke_pipeline(), load_circulars(), Path, HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network. Stable…, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., LexicalReranker (+26 more)

### Community 41 - "ingest_pdf.py"
Cohesion: 0.15
Nodes (19): Re-derive circular number + dates from each record's stored text and rewrite…, _existing_numbers(), extract_text(), ingest(), main(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars. Drop a circular PDF into data/raw/ and… (+11 more)

### Community 42 - "reg_display_name"
Cohesion: 0.33
Nodes (8): build_ui(), _empty_outputs(), _parse_as_of(), Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO     YYYY-MM-D, SSRF guard: reject URLs pointing to private/internal/reserved addresses.      Bl, submit_query(), _validate_api_url()

### Community 46 - "test_hyde.py"
Cohesion: 0.18
Nodes (10): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage. Part B of…, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage. Offline only —…, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_output_truncated_to_max_chars() (+2 more)

### Community 47 - "hierarchical_chunk"
Cohesion: 0.19
Nodes (16): hierarchical_chunk(), Document -> section -> paragraph chunks with stable IDs. A "section" is…, test_numeric_miner_requires_numeric_pattern(), test_paraphrase_skips_preamble_and_short_chunks(), _body(), Chunker (segment.hierarchical_chunk) behaviour. Regression guard for the "5.…, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_absorption_respects_300_char_cap() (+8 more)

### Community 48 - ".load"
Cohesion: 0.12
Nodes (16): Embedder, ndarray, Protocol, _tokens(), DenseIndex, _doc_checksum(), ndarray, F3 (ADR-001): encode only new/changed documents; reuse cached embedding rows… (+8 more)

### Community 49 - "test_api.py"
Cohesion: 0.10
Nodes (16): FastAPI, integration, _citation_meta(), create_app(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit,…, /ready should trigger pipeline build and return ready=true., test_auth_required_when_key_set(), test_bge_fp16_encode_is_normalized() (+8 more)

### Community 50 - "remap_doc_ids.py"
Cohesion: 0.33
Nodes (10): main(), Rewrite golden_v7 doc references after the corpus renumbering (2026-07-25…, remap(), Doc-id remapping after the 2026-07-25 corpus renumbering (Task 4)., _row(), test_input_rows_are_not_mutated(), test_matching_is_normalization_insensitive(), test_remaps_must_not_cite() (+2 more)

### Community 51 - "test_golden_v7_agreement.py"
Cohesion: 0.06
Nodes (64): apply(), _body(), _claude_accuracy_ci(), cohen_kappa(), _confirms_claude(), decide(), _label(), _literals_by_row() (+56 more)

### Community 52 - "retrieve.py"
Cohesion: 0.11
Nodes (19): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant). SEBI…, Append statutory synonyms for lay tokens present in `query`. Deterministic and…, Stage-1 hybrid retrieval: dense (FAISS) + sparse (BM25) fused by RRF. Mandatory…, BM25 lexical index (bm25s)., Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), SparseIndex (+11 more)

### Community 53 - "build_regulatory_index"
Cohesion: 0.18
Nodes (11): _Canned, _hybrid(), fixture, HF Spaces path: corpus_spaces loader mapping + HybridGenerator fallback. Fully…, ExternalSpaceGenerator must call huggingface-projects/llama-2-7b-chat's…, settings(), _stub_rows(), test_corpus_records_feed_build_lineage() (+3 more)

### Community 54 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only (D2 as…, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and…, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 55 - "test_eval_asof.py"
Cohesion: 0.13
Nodes (26): sebi_rag/eval_asof.py, AsofCaseResult, build_report(), load_golden_asof(), Path, As-of-date golden evaluation runner (P4b). Two case modes drawn from…, Assemble the persisted as-of run artifact. Pipeline accuracy is the headline…, Aggregate case results with an exact confidence interval. Pure function of the… (+18 more)

### Community 57 - "RAGPipeline"
Cohesion: 0.19
Nodes (16): _as_bool(), _get(), Path, Central configuration: config.toml defaults, overridden by SEBI_RAG_* env vars.…, Settings.load() plus the [spaces] table as settings.spaces.* Load order per…, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default may…, _clear() (+8 more)

### Community 58 - "backfill_escalations.py"
Cohesion: 0.12
Nodes (28): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate… (+20 more)

### Community 60 - "pick_device"
Cohesion: 0.20
Nodes (11): pick_device(), Device + precision selection for Apple-Silicon inference. Centralizes the…, Resolve the compute device. A truthy explicit `pref` ("mps"/"cpu"/"cuda") wins.…, fp16 only on GPU-class devices; never on cpu. bf16 is never returned here by…, should_use_fp16(), Device + fp16 policy selection (no real torch/mps required)., test_pick_device_auto_cpu_when_no_mps(), test_pick_device_auto_mps_when_available() (+3 more)

### Community 61 - "test_pipeline.py"
Cohesion: 0.19
Nodes (14): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).…, recall_at_k(), _build_chunks(), _build_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline. Runs fully offline…, test_abstention_on_out_of_domain_query() (+6 more)

### Community 62 - "consolidation_edges"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3). Additive fields only…, Set is_master/master_series/master_edition/previous_edition in place. Returns…, Edges for circulars listed in a master circular's rescission appendix. Scans…, _master(), test_annotate_idempotent() (+7 more)

### Community 63 - "test_golden_v7_pool.py"
Cohesion: 0.18
Nodes (15): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of…, TREC-style pool: gold-doc literal matches lead, then round-robin over…, _chunk(), test_retrieve_dense_leg_keeps_raw_query(), test_retrieve_routes_expanded_query_to_sparse_leg(), One gold doc with `n` chunks that ALL contain the word "broker", so a…, Regression (2026-07-25): a must_contain literal matching many gold-doc chunks… (+7 more)

### Community 64 - "gemini_adjudicate.py"
Cohesion: 0.11
Nodes (23): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec… (+15 more)

### Community 65 - "test_regulations.py"
Cohesion: 0.18
Nodes (13): Resolve a cited regulation name+year to a canonical reg_id. Returns (reg_id,…, resolve_regulation(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6)., Singular/plural and dropped-stopword variants normalise to identical token…, A citation carrying a spurious extra token still resolves, but only via the…, test_acronym_aliases_resolve_as_explicit_text(), test_alias_year_matters(), test_exact_name_resolves_as_explicit_text() (+5 more)

### Community 67 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden. `chunks` is optional:…, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 69 - "eval_gate.py"
Cohesion: 0.20
Nodes (14): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY).…, (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'. Takes the LAST bracket group…, _record() (+6 more)

### Community 72 - "test_every_alias_target_is_in_force_or_has_a_succession_entry"
Cohesion: 0.18
Nodes (8): Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., _paragraphs(), Segmentation: hierarchical chunking + metadata + stable citation IDs. Minimal,…, Split into units each <= max_chars. PDF-extracted text often lacks blank-line…, P1 evaluation-harness test (offline). Loads the real seed corpus…, test_eval_harness_metric_suite(), test_real_corpus_loads_with_provenance_fields(), Index persistence round-trip (offline).

### Community 73 - "regulations.py"
Cohesion: 0.20
Nodes (10): _jaccard(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6). Regulations…, Deterministic, stable identity slug. This is the edge target and join key., reg_id(), RegulationMeta, _slug(), test_reg_id_is_a_deterministic_slug(), test_reg_id_is_stable_across_punctuation_and_case_variants() (+2 more)

### Community 75 - "sebi-rag"
Cohesion: 0.26
Nodes (14): discover(), _listing_url(), main(), _page(), _parse_date(), parse_rows(), pdf_url_for(), date (+6 more)

### Community 76 - "Lineage"
Cohesion: 0.08
Nodes (35): annotate_corpus(), build_lineage(), detect_relations(), detect_relations_ex(), Lineage, Path, Update each corpus record's supersession_status + superseded_by + supersedes…, Like detect_relations, but returns dict records with evidence spans. (+27 more)

### Community 77 - "acquire_missing_pdfs.py"
Cohesion: 0.26
Nodes (12): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their…, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+4 more)

### Community 78 - "test_benchmark.py"
Cohesion: 0.36
Nodes (6): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields(), test_trec_run_and_research_judges_are_sidecar_only()

### Community 79 - "parse_meta"
Cohesion: 0.15
Nodes (17): Pattern, _iso_date(), _labeled_date(), parse_meta(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic en-dash… (+9 more)

### Community 82 - "answer_with_abstention"
Cohesion: 0.07
Nodes (35): Chunk, answer_with_abstention(), _grounded_prompt(), _is_non_sebi_domain(), _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice() (+27 more)

### Community 83 - "test_gate.py"
Cohesion: 0.24
Nodes (4): Protocol, Reranker, Chunk, test_chunks_config_refuses_header_and_maps_fields()

### Community 86 - "test_eval_harness_v7.py"
Cohesion: 0.28
Nodes (15): _aggregate(), EvalReport, _mean(), Golden-set evaluation harness (P1). Runs the pipeline over a labelled golden…, report_dict(), run_eval(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-… (+7 more)

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
Cohesion: 0.36
Nodes (4): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}.…, read_trec_run(), The archived runfiles embed section headings in the doc id., TestReadTrecRun

### Community 94 - "eval_harness.py"
Cohesion: 0.22
Nodes (9): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics.…, P(pos_score > neg_score); ties count half. pos = answerable top-scores, neg =…, Threshold maximising abstention accuracy: answer if score >= thr. Returns (thr,…, Calibrate top_k and the abstention threshold against the citation-precision…, sebi_rag/__init__.py (+1 more)

### Community 95 - "main"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation. Outputs:…, write_card()

### Community 96 - "splade_encoder.py"
Cohesion: 0.29
Nodes (8): _alias_keys(), Candidate alias lookup keys, most literal first. Both the raw normalised form…, PMS/NCS/ILDS end in a literal S. Unconditional plural-stripping mapped them to…, reg_id resolved purely through the alias table, ignoring the corpus., A table key that no _alias_keys() output can produce is dead config., _resolved(), test_acronyms_ending_in_s_reach_their_own_entry(), test_every_alias_entry_is_reachable_from_some_spelling()

### Community 97 - "adjudicate"
Cohesion: 0.22
Nodes (10): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt) -> str`…, Scans the per-row cache for `ids` and returns the ones flagged parse_error:…, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct from a well-…, Defensive: an id that was never adjudicated (no cache file at all) is not…, test_adjudicate_marks_parse_error_for_garbled_abstain_protocol_reply() (+2 more)

### Community 98 - "build_report"
Cohesion: 0.40
Nodes (5): load_regulations(), Path, Load data/corpus/regulations.jsonl into a list of regulation records. Thin…, test_load_regulations_round_trips(), test_load_regulations_skips_blank_lines()

### Community 99 - "test_ingest_refs.py"
Cohesion: 0.15
Nodes (11): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104", "HO/…, References split across tokens: merge up to 4 tokens after the first…, _rejoin_split(), _s_anchor_merge(), parametrize, Regression matrix for SEBI reference-number extraction. One case per known…, test_fulltext_fallback_returns_earliest_body_reference() (+3 more)

### Community 101 - "bootstrap_ci"
Cohesion: 0.50
Nodes (4): Human-readable regulation name. Year disambiguates same-short_name repeal pairs…, reg_display_name(), test_reg_display_name_composes_year(), test_reg_display_name_falls_back_without_year()

### Community 103 - "app.py"
Cohesion: 0.27
Nodes (9): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only). Gradio SDK…, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict ISO YYYY-…, run_query_spaces(), warm_up_gpu() (+1 more)

### Community 104 - "test_build_reg_edges.py"
Cohesion: 0.67
Nodes (3): derive_regulatory_basis(), Regulatory-basis status of one circular from its resolved regulations.…, test_derive_regulatory_basis_truth_table()

### Community 105 - "floors_ok"
Cohesion: 0.67
Nodes (3): name_tokens(), Comparison tokens: lowercased, punctuation-split, stopwords dropped, naively…, test_name_tokens_singularises_and_drops_stopwords()

### Community 108 - ".test_mean_reproduces_the_archived_aggregate"
Cohesion: 0.25
Nodes (8): evaluate(), per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.…, run_retrieval_benchmark(), _doc(), _eval_item(), _unique(), Ten chunks of one circular must not crowd the cutoff: the k applies to unique…

## Knowledge Gaps
- **218 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+213 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **206 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `test_gate.py` to `benchmark.py`, `api.py`, `Settings`, `context_headers.py`, `test_golden_v7_resolver.py`, `test_spaces.py`, `lineage.py`, `segment.py`, `HybridRetriever`, `HashEmbedder`, `test_hyde.py`, `hierarchical_chunk`, `.load`, `retrieve.py`, `build_regulatory_index`, `Qwen3MLXReranker`, `test_golden_v7_pool.py`, `validate_golden_v7`, `test_every_alias_target_is_in_force_or_has_a_succession_entry`, `test_benchmark.py`, `answer_with_abstention`, `test_injection.py`, `main`, `derive_thresholds.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `api.py` to `benchmark.py`, `HashEmbedder`, `.test_mean_reproduces_the_archived_aggregate`, `Lineage`, `.load`, `test_api.py`, `test_gate.py`, `read_trec_run`, `test_eval_harness_v7.py`, `test_eval_asof.py`, `segment.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `sebi_rag/eval_asof.py` connect `test_eval_asof.py` to `clopper_pearson_ci`, `api.py`, `Lineage`, `lineage.py`, `segment.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `CitationMeta`) actually correct?**
  _`RAGPipeline` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `HashEmbedder` (e.g. with `_CannedGenerator` and `_SlowGenerator`) actually correct?**
  _`HashEmbedder` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `ExtractiveStubGenerator` (e.g. with `get_pipeline()` and `main()`) actually correct?**
  _`ExtractiveStubGenerator` has 13 INFERRED edges - model-reasoned connections that need verification._