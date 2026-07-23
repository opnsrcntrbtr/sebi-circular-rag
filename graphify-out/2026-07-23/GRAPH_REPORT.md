# Graph Report - SEBI circular RAG  (2026-07-23)

## Corpus Check
- 124 files · ~65,928 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1384 nodes · 2901 edges · 80 communities (62 shown, 18 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 666 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c78cd600`
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
- test_gate.py
- bench_retrieval.py
- _compute_kwargs
- paired_delta
- bootstrap_ci
- build_index.py
- eval_harness.py
- SparseIndex
- test_pipeline.py
- corpus.py
- corpus_spaces.py
- eval.py
- test_integration_e2e.py
- Answer
- test_persistence.py
- faithfulness
- _rejoin_split
- faithfulness
- _s_header_token
- _s_mc_no
- acquire_missing_pdfs.py
- audit_reg_edges.py
- paired_delta
- scrape_regulations.py
- bootstrap_ci
- detect_relations_ex
- test_build_reg_edges.py
- test_acquire_missing.py
- _alias_keys
- main
- verify_master.py

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 85 edges
2. `RAGPipeline` - 40 edges
3. `HashEmbedder` - 38 edges
4. `hierarchical_chunk()` - 36 edges
5. `ExtractiveStubGenerator` - 33 edges
6. `Lineage` - 31 edges
7. `build_lineage()` - 29 edges
8. `CircularMeta` - 29 edges
9. `extract_citations()` - 25 edges
10. `HybridRetriever` - 23 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_parse_meta_dept_order_document_end_to_end()` --calls--> `parse_meta()`  [INFERRED]
  tests/test_ingest_refs.py → src/sebi_rag/ingest_pdf.py
- `test_parse_meta_excludes_prefix_variant_self_reference()` --calls--> `parse_meta()`  [INFERRED]
  tests/test_ingest_refs.py → src/sebi_rag/ingest_pdf.py
- `test_to_record_carries_injection_flags()` --calls--> `to_record()`  [INFERRED]
  tests/test_injection.py → src/sebi_rag/ingest_pdf.py
- `test_governing_on_cycle_safe()` --calls--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py

## Import Cycles
- None detected.

## Communities (80 total, 18 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.14
Nodes (22): BaseModel, build_default_pipeline(), _citation_meta(), CitationMeta, QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline.  Run (real stack; loads the, BGEM3Embedder (+14 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.06
Nodes (59): Any, main(), main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, dataset_quality(), load_index_chunks(), main(), Path (+51 more)

### Community 2 - "Data Processing"
Cohesion: 0.16
Nodes (28): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair.      The merged edge carries t, Set regulations / primary_regulation / regulatory_basis_status in place.      Re, Stub records for cited regulations absent from the Updated List.      Returns NE, synthesise_repealed_stubs(), _circ(), Regulation edges + corpus annotation (spec 2026-07-23 §3.3, §3.4, §3.7). (+20 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.12
Nodes (13): FastAPI, create_app(), _offline_pipeline(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, /ready should trigger pipeline build and return ready=true., _slow_pipeline(), _SlowGenerator, test_auth_required_when_key_set() (+5 more)

### Community 4 - "Dataset Export"
Cohesion: 0.08
Nodes (50): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+42 more)

### Community 5 - "Utility Scripts"
Cohesion: 0.16
Nodes (16): diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13).  Pure functions only: l, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows., render_markdown() (+8 more)

### Community 6 - "Spaces CPU Pipeline"
Cohesion: 0.06
Nodes (28): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7).  Emits a, Up to `n` edges, spread as evenly as possible across evidence tiers.      Tiers, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+20 more)

### Community 7 - "Dataset Card Tests"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 8 - "Metadata Engine"
Cohesion: 0.06
Nodes (28): annotate_corpus(), Update each corpus record's supersession_status + superseded_by + supersedes, annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan (+20 more)

### Community 9 - "Export Tests"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 10 - ".grounded"
Cohesion: 0.18
Nodes (10): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage.  Offline only —, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_output_truncated_to_max_chars() (+2 more)

### Community 11 - "Benchmark Scripts"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 13 - "Lineage"
Cohesion: 0.12
Nodes (19): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), True iff the reply names a valid excerpt number. 'none' or anything     unparsea, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the     gat, Deterministic groundedness judge on MLX (greedy decode, temp 0).      Pass share (+11 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.09
Nodes (30): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any (+22 more)

### Community 15 - "Embedder"
Cohesion: 0.18
Nodes (10): main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.  splad, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights., splade_pool(), SpladeEncoder (+2 more)

### Community 16 - "Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "Master Metadata"
Cohesion: 0.08
Nodes (31): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).  Resumable, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10).  Pulls the i, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+23 more)

### Community 18 - "Export Integration"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 19 - "lineage.py"
Cohesion: 0.18
Nodes (17): contexts_for(), Answer, answer_with_abstention(), faithfulness(), Check that every circular id the answer cites (in square brackets) was     actua, demote_superseded(), Down-weight reranked (chunk, score) pairs from superseded circulars and     re-s, _chunk() (+9 more)

### Community 20 - "test_gate.py"
Cohesion: 0.30
Nodes (9): HybridRetriever, _chunks(), _fake_encode(), Returns a fixed dense ranking regardless of query., _StubDense, _StubSparse, test_flag_off_is_unchanged_and_ignores_splade(), test_splade_leg_changes_fused_order_when_on() (+1 more)

### Community 21 - "Chunk"
Cohesion: 0.06
Nodes (45): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces(), ExternalSpaceGenerator (+37 more)

### Community 22 - "Corpus Validation"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

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
Cohesion: 0.12
Nodes (32): smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., LexicalReranker, Deterministic query-coverage reranker (test/fallback).      Score = fraction of, CircularMeta (+24 more)

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 29 - "test_gate.py"
Cohesion: 0.09
Nodes (23): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env (+15 more)

### Community 30 - "build_lineage"
Cohesion: 0.25
Nodes (15): _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars.  Drop a circular PDF into data/raw/ and (+7 more)

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
Cohesion: 0.15
Nodes (10): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).  Standalo, csr_matrix, Path, SPLADE learned-sparse retrieval leg (iv11).  Non-destructive, opt-in third RRF l, SpladeIndex, _fake_encode(), Return an encode fn mapping known texts to known dense weight rows. (+2 more)

### Community 40 - "test_incremental_index.py"
Cohesion: 0.09
Nodes (29): Path, _jaccard(), load_regulations(), name_tokens(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6).  Regulations, Resolve a cited regulation name+year to a canonical reg_id.      Returns (reg_id, Load data/corpus/regulations.jsonl into a list of regulation records.      Thin, Human-readable regulation name. Year disambiguates same-short_name repeal     pa (+21 more)

### Community 41 - "test_integration_e2e.py"
Cohesion: 0.14
Nodes (17): Pattern, _header(), _iso_date(), _labeled_date(), parse_meta(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars., _subject(), _make_pdf() (+9 more)

### Community 42 - "UI Components"
Cohesion: 0.43
Nodes (6): build_ui(), _empty_outputs(), _parse_as_of(), Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO     YYYY-MM-D, submit_query()

### Community 46 - "bench_rerankers.py"
Cohesion: 0.16
Nodes (10): Embedder, DenseIndex, _doc_checksum(), ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding, Deterministic per-document checksum over its (enriched) chunk texts —     captur, FAISS IndexFlatIP over L2-normalized vectors (cosine). (+2 more)

### Community 47 - "bench_retrieval.py"
Cohesion: 0.47
Nodes (5): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), test_retrieval_metrics()

### Community 48 - ".encode"
Cohesion: 0.24
Nodes (7): _chunk(), test_retrieve_dense_leg_keeps_raw_query(), test_retrieve_routes_expanded_query_to_sparse_leg(), test_none_and_empty_hyde_are_identical_to_baseline(), _chunks(), Index persistence round-trip (offline)., test_index_save_load_roundtrip()

### Community 49 - "test_gate.py"
Cohesion: 0.14
Nodes (13): Protocol, Generator, _grounded_prompt(), Judge, ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the (+5 more)

### Community 50 - "bench_retrieval.py"
Cohesion: 0.29
Nodes (13): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations() (+5 more)

### Community 51 - "_compute_kwargs"
Cohesion: 0.23
Nodes (14): hierarchical_chunk(), Document -> section -> paragraph chunks with stable IDs.      A "section" is det, _body(), Chunker (segment.hierarchical_chunk) behaviour.  Regression guard for the "5. Nu, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_absorption_respects_300_char_cap(), test_bare_parent_heading_folds_into_first_subsection(), test_bare_parent_heading_not_emitted_as_standalone_chunk() (+6 more)

### Community 52 - "paired_delta"
Cohesion: 0.22
Nodes (13): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic, Query-side lexical expansion (intervention #2, glossary variant).  Lay->statutor, test_all_five_sparse_failure_queries_expand(), test_expanded_sparse_query_hits_statutory_chunk(), test_lay_term_gains_statutory_synonym(), test_multiword_synonym_splits_into_tokens() (+5 more)

### Community 53 - "bootstrap_ci"
Cohesion: 0.23
Nodes (15): discover(), extract_pdf_urls(), fetch(), _listing_url(), looks_like_pdf(), main(), _page(), _parse_date() (+7 more)

### Community 54 - "build_index.py"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 55 - "eval_harness.py"
Cohesion: 0.17
Nodes (10): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104",     "HO/ (, References split across tokens: merge up to 4 tokens after the first     HO/CIR/, _rejoin_split(), _s_anchor_merge(), Regression matrix for SEBI reference-number extraction.  One case per known form, test_fulltext_fallback_returns_earliest_body_reference(), test_parse_meta_dept_order_document_end_to_end() (+2 more)

### Community 56 - "SparseIndex"
Cohesion: 0.12
Nodes (25): AsofCaseResult, build_report(), load_golden_asof(), Path, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, Assemble the persisted as-of run artifact.      Pipeline accuracy is the headlin, Aggregate case results with an exact confidence interval.      Pure function of, run_pipeline_cases() (+17 more)

### Community 57 - "test_pipeline.py"
Cohesion: 0.46
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are e, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 59 - "corpus_spaces.py"
Cohesion: 0.09
Nodes (31): main(), build_lineage(), _currency(), detect_relations(), detect_relations_ex(), load_records(), Path, Like detect_relations, but returns dict records with evidence spans. (+23 more)

### Community 60 - "eval.py"
Cohesion: 0.20
Nodes (11): pick_device(), Device + precision selection for Apple-Silicon inference.  Centralizes the mps/c, Resolve the compute device.      A truthy explicit `pref` ("mps"/"cpu"/"cuda") w, fp16 only on GPU-class devices; never on cpu. bf16 is never returned     here by, should_use_fp16(), Device + fp16 policy selection (no real torch/mps required)., test_pick_device_auto_cpu_when_no_mps(), test_pick_device_auto_mps_when_available() (+3 more)

### Community 61 - "test_integration_e2e.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 63 - "test_persistence.py"
Cohesion: 0.33
Nodes (6): Deterministic, stable identity slug. This is the edge target and join key., reg_id(), _slug(), test_reg_id_is_a_deterministic_slug(), test_reg_id_is_stable_across_punctuation_and_case_variants(), test_reg_ids_from_the_fixture_are_unique()

### Community 64 - "faithfulness"
Cohesion: 0.18
Nodes (18): _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker., build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf() (+10 more)

### Community 69 - "acquire_missing_pdfs.py"
Cohesion: 0.26
Nodes (11): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+3 more)

### Community 71 - "paired_delta"
Cohesion: 0.50
Nodes (3): Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 72 - "scrape_regulations.py"
Cohesion: 0.27
Nodes (10): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY)., (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'.      Takes the LAST bracket group, _record() (+2 more)

### Community 73 - "bootstrap_ci"
Cohesion: 0.33
Nodes (4): Index-invariance guard (spec §3.1): the new fields must never be ones     Circul, An alias pointing at a slug that is neither a scraped in-force     regulation no, test_annotation_adds_no_circular_meta_field(), test_every_alias_target_is_in_force_or_has_a_succession_entry()

### Community 75 - "test_build_reg_edges.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 78 - "_alias_keys"
Cohesion: 0.29
Nodes (8): _alias_keys(), Candidate alias lookup keys, most literal first.      Both the raw normalised fo, PMS/NCS/ILDS end in a literal S. Unconditional plural-stripping mapped     them, reg_id resolved purely through the alias table, ignoring the corpus., A table key that no _alias_keys() output can produce is dead config., _resolved(), test_acronyms_ending_in_s_reach_their_own_entry(), test_every_alias_entry_is_reachable_from_some_spelling()

### Community 81 - "main"
Cohesion: 0.21
Nodes (11): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline).  No networ, write_jsonl(), _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7)., Yield (circular, Citation) for every citation occurrence in the corpus. (+3 more)

### Community 82 - "verify_master.py"
Cohesion: 0.67
Nodes (3): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `test_gate.py` to `faithfulness`, `Benchmark Infrastructure`, `Core RAG Pipeline`, `paired_delta`, `.grounded`, `Lineage`, `bench_rerankers.py`, `.encode`, `Master Metadata`, `lineage.py`, `test_gate.py`, `Chunk`, `build_index.py`, `_compute_kwargs`, `test_integration_e2e.py`, `Answer Generation`, `test_gate.py`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `Core RAG Pipeline` to `faithfulness`, `Benchmark Infrastructure`, `Index & Evaluation`, `audit_reg_edges.py`, `bench_rerankers.py`, `test_gate.py`, `lineage.py`, `test_gate.py`, `SparseIndex`, `Answer Generation`, `test_gate.py`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `CircularMeta` connect `Answer Generation` to `faithfulness`, `Benchmark Infrastructure`, `Index & Evaluation`, `audit_reg_edges.py`, `bootstrap_ci`, `.encode`, `Master Metadata`, `_compute_kwargs`, `test_pipeline.py`, `test_gate.py`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_CannedGenerator`) actually correct?**
  _`HashEmbedder` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `hierarchical_chunk()` (e.g. with `smoke_pipeline()` and `_distinct_pipeline()`) actually correct?**
  _`hierarchical_chunk()` has 27 INFERRED edges - model-reasoned connections that need verification._