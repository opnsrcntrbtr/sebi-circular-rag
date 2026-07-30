# Graph Report - SEBI circular RAG  (2026-07-30)

## Corpus Check
- 155 files · ~157,292 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2045 nodes · 3949 edges · 304 communities (90 shown, 214 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 919 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e06a26da`
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
- verify_master.py
- test_annotation_adds_no_circular_meta_field
- _norm_ws
- test_parse_reply_unknown_letter_fails_the_whole_reply_closed
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
- Community 126
- Community 127
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
- `test_citation_meta_defaults_when_circular_absent_from_index()` --calls--> `_citation_meta()`  [INFERRED]
  tests/test_api.py → src/sebi_rag/api.py
- `test_citation_meta_defaults_when_index_none()` --calls--> `_citation_meta()`  [INFERRED]
  tests/test_api.py → src/sebi_rag/api.py
- `test_citation_meta_fills_regulatory_fields()` --calls--> `_citation_meta()`  [INFERRED]
  tests/test_api.py → src/sebi_rag/api.py
- `test_run_metadata_has_reproducibility_fields()` --calls--> `run_metadata()`  [INFERRED]
  tests/test_benchmark.py → src/sebi_rag/benchmark.py
- `test_real_corpus_loads_with_provenance_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_eval_harness.py → src/sebi_rag/corpus.py

## Import Cycles
- None detected.

## Communities (304 total, 214 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.07
Nodes (52): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV ingest, Writes the blind human packet for `human_ids` (a subset of `ids`, the     full e (+44 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.24
Nodes (19): beir_corpus_rows(), beir_query_rows(), build_golden_v6(), dir_fingerprint(), enrich_golden_item(), export_beir(), git_commit(), Any (+11 more)

### Community 2 - "Data Processing"
Cohesion: 0.12
Nodes (37): annotate_regulation_fields(), build_regulation_edges(), build_regulatory_index(), One `cites` edge per (circular, regulation) pair.      The merged edge carries t, Set regulations / primary_regulation / regulatory_basis_status in place.      Re, Per-circular regulatory-basis lookup for the query/citation layer.      Read-onl, Stub records for cited regulations absent from the Updated List.      Returns NE, synthesise_repealed_stubs() (+29 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.12
Nodes (25): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape).     Non-abst, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing, a, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as     "confirms abs, A non-abstain row whose pool happens to have zero candidates can't     offer any, letters=[] is how adjudicate signals an abstain/zero-candidate row;     parse_re, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct     from a we (+17 more)

### Community 4 - "Dataset Export"
Cohesion: 0.08
Nodes (50): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+42 more)

### Community 5 - "Utility Scripts"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 6 - "Spaces CPU Pipeline"
Cohesion: 0.05
Nodes (33): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7).  Emits a, Up to `n` edges, spread as evenly as possible across evidence tiers.      Tiers, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+25 more)

### Community 7 - "Dataset Card Tests"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 8 - "Metadata Engine"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 9 - "Export Tests"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 10 - ".grounded"
Cohesion: 0.17
Nodes (26): BaseModel, FastAPI, build_default_pipeline(), _citation_meta(), CitationMeta, _compute_kwargs(), create_app(), QueryRequest (+18 more)

### Community 11 - "Benchmark Scripts"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 13 - "Lineage"
Cohesion: 0.22
Nodes (14): _extract_text(), Anthropic Messages response -> reply text: concatenates `text`     content block, _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external ann, Five pilot rows from five strata measure more than five from one -     the gemin, Vote records must say annotator "qwen" (never reuse "gemini" - the     agreement, Back-compat guard: the gemini leg (on hold, not removed) must keep     producing, _row() (+6 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.09
Nodes (30): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any (+22 more)

### Community 15 - "Embedder"
Cohesion: 0.10
Nodes (28): main(), main(), main(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of, main(), build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t (+20 more)

### Community 16 - "Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "Master Metadata"
Cohesion: 0.08
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).  Resumable, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10).  Pulls the i, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 18 - "Export Integration"
Cohesion: 0.29
Nodes (13): chunks_by_doc(), qrels_rows(), Span {doc, quote} -> matching chunk ids (all overlap matches count).      Legacy, resolve_chunk_spans(), _span_resolution_issues(), _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row() (+5 more)

### Community 19 - "lineage.py"
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the docume, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 20 - "test_gate.py"
Cohesion: 0.08
Nodes (37): derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).  Write, metric -> per-query score vector, into gate-floor names -> floor value.      Met, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the derived, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed     v7 gate,, True iff every floor's metric is present in `report_gate` and meets it.      Mis (+29 more)

### Community 21 - "Chunk"
Cohesion: 0.11
Nodes (22): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).      Nev (+14 more)

### Community 22 - "Corpus Validation"
Cohesion: 0.21
Nodes (10): ProportionCI, _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected() (+2 more)

### Community 23 - "Reranking"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).  Deliber, All regulation citations in a circular, one per occurrence (not deduped).      S, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years.      "Regulations (+24 more)

### Community 24 - "ZeroGPU Tests"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 25 - "Dataset Push"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 26 - "Answer Generation"
Cohesion: 0.31
Nodes (10): build_report(), Assemble the persisted as-of run artifact.      Pipeline accuracy is the headlin, Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid     measureme, The headline number must be the 10 pipeline cases alone — the whole     point of, _results(), test_pipeline_metrics_are_not_polluted_by_selector_cases(), test_pooled_overall_carries_no_interval() (+2 more)

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 29 - "test_gate.py"
Cohesion: 0.10
Nodes (18): Reranker, Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Calibrate top_k and the abstention threshold against the citation-precision sign, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Emit one JSON line of retrieval/citation/abstention metrics using the persisted, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks. (+10 more)

### Community 30 - "build_lineage"
Cohesion: 0.10
Nodes (39): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+31 more)

### Community 31 - "detect_relations_ex"
Cohesion: 0.23
Nodes (16): main(), discover(), extract_pdf_urls(), fetch(), _listing_url(), looks_like_pdf(), main(), _page() (+8 more)

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
Nodes (8): csr_matrix, Path, SPLADE learned-sparse retrieval leg (iv11).  Non-destructive, opt-in third RRF l, SpladeIndex, _fake_encode(), Return an encode fn mapping known texts to known dense weight rows., test_save_load_roundtrip_and_guard(), test_search_ranks_by_sparse_dot_product()

### Community 40 - "test_incremental_index.py"
Cohesion: 0.26
Nodes (13): _get(), Path, Settings.load() plus the [spaces] table as settings.spaces.*          Load order, Resolve a setting: env var > config dict > default., _clear(), Settings: defaults, config.toml, and env-override precedence., test_compute_defaults(), test_compute_env_overrides() (+5 more)

### Community 41 - "test_integration_e2e.py"
Cohesion: 0.13
Nodes (14): Pattern, Re-derive circular number + dates from each record's stored text and rewrite the, _iso_date(), _labeled_date(), main(), Local PDF ingestion for SEBI circulars.  Drop a circular PDF into data/raw/ and, Standard formats (old CIR, new SEBI/HO, free-form 2026): first     slash-heavy H, Department-only prefixes without HO/CIR anchor,     e.g. AFD/P/CIR/2022/125. (+6 more)

### Community 42 - "UI Components"
Cohesion: 0.24
Nodes (10): Human-readable regulation name. Year disambiguates same-short_name repeal     pa, reg_display_name(), build_ui(), _empty_outputs(), _parse_as_of(), Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO     YYYY-MM-D, submit_query() (+2 more)

### Community 46 - "bench_rerankers.py"
Cohesion: 0.17
Nodes (11): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage.  Offline only —, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_none_and_empty_hyde_are_identical_to_baseline() (+3 more)

### Community 47 - "bench_retrieval.py"
Cohesion: 0.15
Nodes (20): load_circulars(), Path, hierarchical_chunk(), _paragraphs(), Split into units each <= max_chars.      PDF-extracted text often lacks blank-li, Document -> section -> paragraph chunks with stable IDs.      A "section" is det, _pipeline(), test_eval_harness_metric_suite() (+12 more)

### Community 48 - ".encode"
Cohesion: 0.16
Nodes (10): Embedder, DenseIndex, _doc_checksum(), ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding, Deterministic per-document checksum over its (enriched) chunk texts —     captur, FAISS IndexFlatIP over L2-normalized vectors (cosine). (+2 more)

### Community 49 - "answer_with_abstention"
Cohesion: 0.10
Nodes (14): _offline_pipeline(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, /ready should trigger pipeline build and return ready=true., _slow_pipeline(), _SlowGenerator, test_auth_required_when_key_set(), test_citation_meta_defaults_when_circular_absent_from_index(), test_citation_meta_defaults_when_index_none() (+6 more)

### Community 50 - "bench_retrieval.py"
Cohesion: 0.20
Nodes (20): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, Every record's text must match the PDF its provenance names.      Slow (re-extra, validate(), validate_deep(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o (+12 more)

### Community 51 - "_compute_kwargs"
Cohesion: 0.07
Nodes (62): apply(), _body(), _claude_accuracy_ci(), cohen_kappa(), decide(), _label(), _literals_by_row(), _llm_annotator() (+54 more)

### Community 52 - "paired_delta"
Cohesion: 0.22
Nodes (13): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic, Query-side lexical expansion (intervention #2, glossary variant).  Lay->statutor, test_all_five_sparse_failure_queries_expand(), test_expanded_sparse_query_hits_statutory_chunk(), test_lay_term_gains_statutory_synonym(), test_multiword_synonym_splits_into_tokens() (+5 more)

### Community 53 - "bootstrap_ci"
Cohesion: 0.16
Nodes (16): diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13).  Pure functions only: l, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows., render_markdown() (+8 more)

### Community 54 - "build_index.py"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 55 - "eval_harness.py"
Cohesion: 0.16
Nodes (16): AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, Aggregate case results with an exact confidence interval.      Pure function of, run_pipeline_cases(), run_selector_cases(), summarize() (+8 more)

### Community 57 - "SparseIndex"
Cohesion: 0.08
Nodes (47): smoke_pipeline(), assemble_pool(), TREC-style pool: gold-doc literal matches lead, then round-robin over     [reran, run_retrieval_benchmark(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, LexicalReranker, Deterministic query-coverage reranker (test/fallback).      Score = fraction of (+39 more)

### Community 58 - "discover_new.py"
Cohesion: 0.09
Nodes (38): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate (2026-07-25 (+30 more)

### Community 60 - "eval.py"
Cohesion: 0.20
Nodes (11): pick_device(), Device + precision selection for Apple-Silicon inference.  Centralizes the mps/c, Resolve the compute device.      A truthy explicit `pref` ("mps"/"cpu"/"cuda") w, fp16 only on GPU-class devices; never on cpu. bf16 is never returned     here by, should_use_fp16(), Device + fp16 policy selection (no real torch/mps required)., test_pick_device_auto_cpu_when_no_mps(), test_pick_device_auto_mps_when_available() (+3 more)

### Community 61 - "test_integration_e2e.py"
Cohesion: 0.47
Nodes (5): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), test_retrieval_metrics()

### Community 62 - "test_pipeline.py"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan, _master(), test_annotate_idempotent() (+7 more)

### Community 63 - "test_persistence.py"
Cohesion: 0.30
Nodes (12): main(), _existing_numbers(), extract_text(), ingest(), normalize_circular_number(), _ocr_text(), Path, Canonical COMPARISON key for a circular number: strip whitespace and     trailin (+4 more)

### Community 64 - "faithfulness"
Cohesion: 0.10
Nodes (26): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec 2026-0 (+18 more)

### Community 65 - "LexicalReranker"
Cohesion: 0.09
Nodes (29): _alias_keys(), load_regulations(), name_tokens(), Path, Candidate alias lookup keys, most literal first.      Both the raw normalised fo, Resolve a cited regulation name+year to a canonical reg_id.      Returns (reg_id, Load data/corpus/regulations.jsonl into a list of regulation records.      Thin, Comparison tokens: lowercased, punctuation-split, stopwords dropped,     naively (+21 more)

### Community 67 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden.      `chunks` is optio, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 68 - "SpladeIndex"
Cohesion: 0.13
Nodes (15): faithfulness(), _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), Generation with a hard abstention gate (D5).  If the top reranked score is below, True iff the reply names a valid excerpt number. 'none' or anything     unparsea (+7 more)

### Community 69 - "acquire_missing_pdfs.py"
Cohesion: 0.26
Nodes (11): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+3 more)

### Community 72 - "scrape_regulations.py"
Cohesion: 0.27
Nodes (9): parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY)., (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'.      Takes the LAST bracket group, _record(), short_name_of() (+1 more)

### Community 73 - "resolve_chunk_spans"
Cohesion: 0.13
Nodes (16): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7)., Yield (circular, Citation) for every citation occurrence in the corpus., derive_regulatory_basis(), _jaccard(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6).  Regulations, Regulatory-basis status of one circular from its resolved regulations.      `unk, Deterministic, stable identity slug. This is the edge target and join key. (+8 more)

### Community 76 - "load_regulations"
Cohesion: 0.07
Nodes (39): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, annotate_corpus(), build_lineage(), _currency(), detect_relations(), detect_relations_ex(), mc_topic(), Path (+31 more)

### Community 78 - "_alias_keys"
Cohesion: 0.36
Nodes (6): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields(), test_trec_run_and_research_judges_are_sidecar_only()

### Community 79 - "test_ingest_pdf.py"
Cohesion: 0.15
Nodes (16): parse_meta(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic     en-d, The mirror of the kerning case above. When the en-dash has spaces on     BOTH si, 2011-era master circulars use "SEBI/<DEPT>/MC No.<n>/<serial>/<year>",     match, Old-format PDFs (e.g. CIR/MRD/DP/ 11 /2012) split the number with a     space BE (+8 more)

### Community 82 - "answer_with_abstention"
Cohesion: 0.35
Nodes (10): Answer, answer_with_abstention(), _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful(), test_no_context_reason_when_top_k_zero() (+2 more)

### Community 83 - "test_gate.py"
Cohesion: 0.38
Nodes (8): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge()

### Community 86 - "test_eval_harness_v7.py"
Cohesion: 0.23
Nodes (16): _aggregate(), EvalReport, _mean(), Golden-set evaluation harness (P1).  Runs the pipeline over a labelled golden se, report_dict(), run_eval(), SEBI Circular RAG — local-first, Apple Silicon.  Pipeline: ingest -> segment ->, _pipeline() (+8 more)

### Community 88 - "CircularMeta"
Cohesion: 0.32
Nodes (6): _chunk(), test_retrieve_dense_leg_keeps_raw_query(), test_retrieve_routes_expanded_query_to_sparse_leg(), _chunks(), Index persistence round-trip (offline)., test_index_save_load_roundtrip()

### Community 89 - ".encode"
Cohesion: 0.18
Nodes (15): _current_model(), main(), pilot(), _pilot_ids(), _post_local(), Path, External annotation slice: local-model leg via oMLX - the PRIMARY leg since 2026, First `n` non-abstain external ids, distinct strata first: five rows     from fi (+7 more)

### Community 90 - "load_golden"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).  C, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 91 - "test_repair_corpus_text.py"
Cohesion: 0.25
Nodes (3): Repair the 6 records whose body text was overwritten with one shared circular's, The repair map must name a real orphan PDF that parses to the circular_number it, test_numbers_normalize_distinctly()

### Community 92 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 93 - "TestReadTrecRun"
Cohesion: 0.36
Nodes (4): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}., read_trec_run(), The archived runfiles embed section headings in the doc id., TestReadTrecRun

### Community 94 - "test_splade_leg.py"
Cohesion: 0.30
Nodes (9): HybridRetriever, _chunks(), _fake_encode(), Returns a fixed dense ranking regardless of query., _StubDense, _StubSparse, test_flag_off_is_unchanged_and_ignores_splade(), test_splade_leg_changes_fused_order_when_on() (+1 more)

### Community 95 - "main"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation.  Outputs:, write_card()

### Community 96 - "splade_encoder.py"
Cohesion: 0.15
Nodes (12): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).  Standalo, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.  splad, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+4 more)

### Community 97 - ".test_mean_reproduces_the_archived_aggregate"
Cohesion: 0.22
Nodes (11): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt)     -> str, Scans the per-row cache for `ids` and returns the ones flagged     parse_error:, Same per-row deterministic shuffle as make_packet.py's write_packet:     random., _shuffled_candidates(), Defensive: an id that was never adjudicated (no cache file at all)     is not re (+3 more)

### Community 98 - "test_incremental_index.py"
Cohesion: 0.46
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are e, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 99 - "corpus.py"
Cohesion: 0.20
Nodes (8): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104",     "HO/ (, References split across tokens: merge up to 4 tokens after the first     HO/CIR/, _rejoin_split(), _s_anchor_merge(), Regression matrix for SEBI reference-number extraction.  One case per known form, test_fulltext_fallback_returns_earliest_body_reference(), test_primary_number_format_matrix()

### Community 101 - "Chunk"
Cohesion: 0.09
Nodes (18): Protocol, contexts_for(), Generator, _grounded_prompt(), Judge, ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier. (+10 more)

### Community 103 - "app.py"
Cohesion: 0.16
Nodes (11): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces(), Build the dense+sparse index once and persist it (run after corpus changes). (+3 more)

### Community 104 - "_alias_keys"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 106 - ".retrieve"
Cohesion: 0.50
Nodes (3): Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 107 - "filter_targeted_rows"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline).  No networ, write_jsonl()

### Community 108 - ".test_mean_reproduces_the_archived_aggregate"
Cohesion: 0.22
Nodes (8): Score one golden row through the production-shaped pipeline.      Returns per-ro, score_row(), per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.      A, _doc(), _eval_item(), _unique(), Ten chunks of one circular must not crowd the cutoff: the k applies         to u

### Community 109 - "main"
Cohesion: 0.40
Nodes (4): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, BenchmarkIssue, validate_golden()

### Community 111 - "verify_master.py"
Cohesion: 0.67
Nodes (3): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:

### Community 112 - "test_annotation_adds_no_circular_meta_field"
Cohesion: 0.33
Nodes (4): Index-invariance guard (spec §3.1): the new fields must never be ones     Circul, An alias pointing at a slug that is neither a scraped in-force     regulation no, test_annotation_adds_no_circular_meta_field(), test_every_alias_target_is_in_force_or_has_a_succession_entry()

### Community 113 - "_norm_ws"
Cohesion: 0.67
Nodes (3): _confirms_claude(), Does this external vote confirm claude's label, at PROVISION level?      Amendme, _norm_ws()

## Knowledge Gaps
- **225 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+220 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **214 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `Benchmark Infrastructure`, `.grounded`, `Embedder`, `Master Metadata`, `Export Integration`, `Chunk`, `test_gate.py`, `bench_rerankers.py`, `bench_retrieval.py`, `.encode`, `build_index.py`, `SparseIndex`, `validate_golden_v7`, `SpladeIndex`, `_alias_keys`, `answer_with_abstention`, `test_gate.py`, `CircularMeta`, `test_injection.py`, `test_splade_leg.py`, `main`, `.retrieve`, `main`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `.grounded` to `Benchmark Infrastructure`, `Chunk`, `.test_mean_reproduces_the_archived_aggregate`, `main`, `Embedder`, `.encode`, `answer_with_abstention`, `answer_with_abstention`, `test_eval_harness_v7.py`, `eval_harness.py`, `SparseIndex`, `TestReadTrecRun`, `test_splade_leg.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `main()` connect `Embedder` to `splade_encoder.py`, `Benchmark Infrastructure`, `annotate_corpus`, `test_incremental_index.py`, `.grounded`, `load_regulations`, `main`, `bench_rerankers.py`, `.encode`, `SparseIndex`, `test_gate.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `RAGPipeline` (e.g. with `main()` and `CitationMeta`) actually correct?**
  _`RAGPipeline` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `hierarchical_chunk()` (e.g. with `smoke_pipeline()` and `_distinct_pipeline()`) actually correct?**
  _`hierarchical_chunk()` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_CannedGenerator`) actually correct?**
  _`HashEmbedder` has 38 INFERRED edges - model-reasoned connections that need verification._