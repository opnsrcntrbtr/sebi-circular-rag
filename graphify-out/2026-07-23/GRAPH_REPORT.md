# Graph Report - SEBI circular RAG  (2026-07-23)

## Corpus Check
- 124 files · ~66,668 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1403 nodes · 2847 edges · 92 communities (75 shown, 17 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 622 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bfa72186`
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
- test_gate.py
- test_acquire_missing.py
- _alias_keys
- stats.py
- app.py
- main
- verify_master.py
- load_regulations
- reg_display_name
- name_tokens
- annotate_corpus
- test_faithfulness.py
- test_incremental_index.py
- .encode
- eval.py
- .build

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 82 edges
2. `RAGPipeline` - 32 edges
3. `HashEmbedder` - 30 edges
4. `hierarchical_chunk()` - 29 edges
5. `ExtractiveStubGenerator` - 26 edges
6. `build_lineage()` - 26 edges
7. `Lineage` - 24 edges
8. `SubjectSimJudge` - 22 edges
9. `extract_citations()` - 22 edges
10. `main()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_bge_fp16_encode_is_normalized()` --calls--> `BGEM3Embedder`  [INFERRED]
  tests/test_api.py → src/sebi_rag/embeddings.py
- `test_parse_meta_dept_order_document_end_to_end()` --calls--> `parse_meta()`  [INFERRED]
  tests/test_ingest_refs.py → src/sebi_rag/ingest_pdf.py
- `test_parse_meta_excludes_prefix_variant_self_reference()` --calls--> `parse_meta()`  [INFERRED]
  tests/test_ingest_refs.py → src/sebi_rag/ingest_pdf.py
- `test_to_record_carries_injection_flags()` --calls--> `to_record()`  [INFERRED]
  tests/test_injection.py → src/sebi_rag/ingest_pdf.py

## Import Cycles
- None detected.

## Communities (92 total, 17 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.19
Nodes (18): BaseModel, build_default_pipeline(), _citation_meta(), CitationMeta, QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline.  Run (real stack; loads the, BGEM3Embedder (+10 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.06
Nodes (49): Any, main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation.  Outputs: (+41 more)

### Community 2 - "Data Processing"
Cohesion: 0.08
Nodes (49): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline).  No networ, write_jsonl(), annotate_regulation_fields(), build_regulation_edges(), build_regulatory_index() (+41 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.14
Nodes (19): build_lineage(), Map any cited circular that is superseded -> the circular(s) superseding it., superseded_citations(), _lin_chain(), P2 lineage / supersession resolution tests., test_build_lineage_edges_tiered(), test_build_lineage_inferred_master_topic_edge(), test_governing_on_before_family_exists() (+11 more)

### Community 4 - "Dataset Export"
Cohesion: 0.08
Nodes (50): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+42 more)

### Community 5 - "Utility Scripts"
Cohesion: 0.16
Nodes (16): diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13).  Pure functions only: l, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows., render_markdown() (+8 more)

### Community 6 - "Spaces CPU Pipeline"
Cohesion: 0.24
Nodes (4): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion.      Use this for stri, The reason for the switch. On 9/10 the percentile bootstrap returns         [0.7, TestClopperPearson

### Community 7 - "Dataset Card Tests"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 8 - "Metadata Engine"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 9 - "Export Tests"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 11 - "Benchmark Scripts"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 13 - "Lineage"
Cohesion: 0.15
Nodes (11): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), True iff the reply names a valid excerpt number. 'none' or anything     unparsea, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the     gat, Deterministic groundedness judge on MLX (greedy decode, temp 0).      Pass share (+3 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.13
Nodes (24): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any (+16 more)

### Community 15 - "Embedder"
Cohesion: 0.18
Nodes (8): csr_matrix, Path, SPLADE learned-sparse retrieval leg (iv11).  Non-destructive, opt-in third RRF l, SpladeIndex, _fake_encode(), Return an encode fn mapping known texts to known dense weight rows., test_save_load_roundtrip_and_guard(), test_search_ranks_by_sparse_dot_product()

### Community 16 - "Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "Master Metadata"
Cohesion: 0.08
Nodes (28): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).  Resumable, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10).  Pulls the i, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+20 more)

### Community 18 - "Export Integration"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 19 - "lineage.py"
Cohesion: 0.38
Nodes (10): Answer, answer_with_abstention(), _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful(), test_no_context_reason_when_top_k_zero() (+2 more)

### Community 20 - "test_gate.py"
Cohesion: 0.29
Nodes (10): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7).  Emits a, Up to `n` edges, spread as evenly as possible across evidence tiers.      Tiers, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+2 more)

### Community 21 - "Chunk"
Cohesion: 0.06
Nodes (43): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces(), ExternalSpaceGenerator (+35 more)

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
Cohesion: 0.09
Nodes (28): FastAPI, create_app(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, run_pipeline_cases(), ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., LexicalReranker (+20 more)

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 29 - "test_gate.py"
Cohesion: 0.13
Nodes (11): Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, Generation with a hard abstention gate (D5).  If the top reranked score is below, Stage-2 reranking (mandatory, D4). Cross-encoder in production; a deterministic (+3 more)

### Community 30 - "build_lineage"
Cohesion: 0.25
Nodes (15): _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars.  Drop a circular PDF into data/raw/ and (+7 more)

### Community 31 - "detect_relations_ex"
Cohesion: 0.30
Nodes (9): HybridRetriever, _chunks(), _fake_encode(), Returns a fixed dense ranking regardless of query., _StubDense, _StubSparse, test_flag_off_is_unchanged_and_ignores_splade(), test_splade_leg_changes_fused_order_when_on() (+1 more)

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
Nodes (12): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).  Standalo, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.  splad, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+4 more)

### Community 40 - "test_incremental_index.py"
Cohesion: 0.18
Nodes (13): Resolve a cited regulation name+year to a canonical reg_id.      Returns (reg_id, resolve_regulation(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6)., Singular/plural and dropped-stopword variants normalise to identical     token s, A citation carrying a spurious extra token still resolves, but only via     the, test_acronym_aliases_resolve_as_explicit_text(), test_alias_year_matters(), test_exact_name_resolves_as_explicit_text() (+5 more)

### Community 41 - "test_integration_e2e.py"
Cohesion: 0.14
Nodes (17): Pattern, _header(), _iso_date(), _labeled_date(), parse_meta(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars., _subject(), _make_pdf() (+9 more)

### Community 42 - "UI Components"
Cohesion: 0.43
Nodes (6): build_ui(), _empty_outputs(), _parse_as_of(), Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO     YYYY-MM-D, submit_query()

### Community 46 - "bench_rerankers.py"
Cohesion: 0.18
Nodes (10): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage.  Offline only —, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_output_truncated_to_max_chars() (+2 more)

### Community 47 - "bench_retrieval.py"
Cohesion: 0.11
Nodes (27): Chunk, Embedder, Lineage, Reranker, _build_chunks(), _build_pipeline(), _FixedReranker, Minimal end-to-end test of the SEBI RAG pipeline.  Runs fully offline (HashEmbed (+19 more)

### Community 48 - ".encode"
Cohesion: 0.23
Nodes (8): Embedder, DenseIndex, _doc_checksum(), ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding, Deterministic per-document checksum over its (enriched) chunk texts —     captur, FAISS IndexFlatIP over L2-normalized vectors (cosine).

### Community 49 - "test_gate.py"
Cohesion: 0.18
Nodes (8): Protocol, Generator, _grounded_prompt(), Judge, F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, Reranker, Chunk, test_chunks_config_refuses_header_and_maps_fields()

### Community 50 - "bench_retrieval.py"
Cohesion: 0.29
Nodes (13): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations() (+5 more)

### Community 51 - "_compute_kwargs"
Cohesion: 0.10
Nodes (28): load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., CircularMeta, hierarchical_chunk(), _paragraphs(), Segmentation: hierarchical chunking + metadata + stable citation IDs.  Minimal,, Split into units each <= max_chars.      PDF-extracted text often lacks blank-li (+20 more)

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
Nodes (24): AsofCaseResult, build_report(), load_golden_asof(), Path, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, Assemble the persisted as-of run artifact.      Pipeline accuracy is the headlin, Aggregate case results with an exact confidence interval.      Pure function of, run_selector_cases() (+16 more)

### Community 57 - "test_pipeline.py"
Cohesion: 0.17
Nodes (15): Answer, Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, main(), Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, smoke_pipeline(), run_retrieval_benchmark(), _doc(), EvalReport (+7 more)

### Community 58 - "corpus.py"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries.      Returns mean_b - m, Randomization p-values use the (count+1)/(n+1) estimator, so a         p-value o, One query flipping out of 56 is exactly the iv9-style verdict: the         rando, TestPairedDelta

### Community 59 - "corpus_spaces.py"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan, _master(), test_annotate_idempotent() (+7 more)

### Community 60 - "eval.py"
Cohesion: 0.20
Nodes (11): pick_device(), Device + precision selection for Apple-Silicon inference.  Centralizes the mps/c, Resolve the compute device.      A truthy explicit `pref` ("mps"/"cpu"/"cuda") w, fp16 only on GPU-class devices; never on cpu. bf16 is never returned     here by, should_use_fp16(), Device + fp16 policy selection (no real torch/mps required)., test_pick_device_auto_cpu_when_no_mps(), test_pick_device_auto_mps_when_available() (+3 more)

### Community 61 - "test_integration_e2e.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 63 - "test_persistence.py"
Cohesion: 0.20
Nodes (10): _jaccard(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6).  Regulations, Deterministic, stable identity slug. This is the edge target and join key., reg_id(), RegulationMeta, _slug(), test_reg_id_is_a_deterministic_slug(), test_reg_id_is_stable_across_punctuation_and_case_variants() (+2 more)

### Community 64 - "faithfulness"
Cohesion: 0.18
Nodes (18): _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker., build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf() (+10 more)

### Community 69 - "acquire_missing_pdfs.py"
Cohesion: 0.26
Nodes (11): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+3 more)

### Community 70 - "audit_reg_edges.py"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must         be, TestBootstrapCI

### Community 71 - "paired_delta"
Cohesion: 0.22
Nodes (4): BM25 lexical index (bm25s)., Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), SparseIndex

### Community 72 - "scrape_regulations.py"
Cohesion: 0.27
Nodes (10): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY)., (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'.      Takes the LAST bracket group, _record() (+2 more)

### Community 73 - "bootstrap_ci"
Cohesion: 0.21
Nodes (11): auroc(), best_threshold(), evaluate(), main(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t, contexts_for() (+3 more)

### Community 74 - "detect_relations_ex"
Cohesion: 0.13
Nodes (15): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, _currency(), detect_relations(), detect_relations_ex(), mc_topic(), P2 — cross-document supersession resolution.  Classifies each circular's referen, Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None.      Us, Like detect_relations, but returns dict records with evidence spans. (+7 more)

### Community 75 - "test_build_reg_edges.py"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 76 - "test_gate.py"
Cohesion: 0.28
Nodes (10): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge() (+2 more)

### Community 78 - "_alias_keys"
Cohesion: 0.29
Nodes (8): _alias_keys(), Candidate alias lookup keys, most literal first.      Both the raw normalised fo, PMS/NCS/ILDS end in a literal S. Unconditional plural-stripping mapped     them, reg_id resolved purely through the alias table, ignoring the corpus., A table key that no _alias_keys() output can produce is dead config., _resolved(), test_acronyms_ending_in_s_reach_their_own_entry(), test_every_alias_entry_is_reachable_from_some_spelling()

### Community 79 - "stats.py"
Cohesion: 0.25
Nodes (5): BootstrapCI, PairedResult, Uncertainty quantification for benchmark runs.  The golden set is n=56 answerabl, True when the randomization test rejects at 1 - confidence AND the         paire, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 80 - "app.py"
Cohesion: 0.31
Nodes (4): ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge

### Community 81 - "main"
Cohesion: 0.67
Nodes (3): derive_regulatory_basis(), Regulatory-basis status of one circular from its resolved regulations.      `unk, test_derive_regulatory_basis_truth_table()

### Community 82 - "verify_master.py"
Cohesion: 0.67
Nodes (3): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:

### Community 83 - "load_regulations"
Cohesion: 0.40
Nodes (5): Path, load_regulations(), Load data/corpus/regulations.jsonl into a list of regulation records.      Thin, test_load_regulations_round_trips(), test_load_regulations_skips_blank_lines()

### Community 84 - "reg_display_name"
Cohesion: 0.50
Nodes (4): Human-readable regulation name. Year disambiguates same-short_name repeal     pa, reg_display_name(), test_reg_display_name_composes_year(), test_reg_display_name_falls_back_without_year()

### Community 85 - "name_tokens"
Cohesion: 0.67
Nodes (3): name_tokens(), Comparison tokens: lowercased, punctuation-split, stopwords dropped,     naively, test_name_tokens_singularises_and_drops_stopwords()

### Community 86 - "annotate_corpus"
Cohesion: 0.22
Nodes (7): annotate_corpus(), load_records(), Path, Update each corpus record's supersession_status + superseded_by + supersedes, test_annotate_corpus_adds_master_fields_and_consolidates_edges(), test_annotate_corpus_writes_new_metadata_fields(), test_real_corpus_oiae_supersedes_listed_circulars()

### Community 87 - "test_faithfulness.py"
Cohesion: 0.29
Nodes (6): faithfulness(), Check that every circular id the answer cites (in square brackets) was     actua, _HallucinatingGenerator, Faithfulness: catch answers that cite circulars not in the retrieved context., test_faithfulness_scoring(), test_pipeline_flags_hallucinated_citation()

### Community 88 - "test_incremental_index.py"
Cohesion: 0.46
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are e, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 91 - ".build"
Cohesion: 0.50
Nodes (4): _chunk(), test_retrieve_dense_leg_keeps_raw_query(), test_retrieve_routes_expanded_query_to_sparse_leg(), test_none_and_empty_hyde_are_identical_to_baseline()

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `test_gate.py` to `Core RAG Pipeline`, `Benchmark Infrastructure`, `Lineage`, `Master Metadata`, `lineage.py`, `Chunk`, `Answer Generation`, `test_gate.py`, `detect_relations_ex`, `bench_rerankers.py`, `.encode`, `_compute_kwargs`, `build_index.py`, `test_integration_e2e.py`, `faithfulness`, `paired_delta`, `bootstrap_ci`, `test_gate.py`, `app.py`, `.build`?**
  _High betweenness centrality (0.167) - this node is a cross-community bridge._
- **Why does `main()` connect `Benchmark Infrastructure` to `Data Processing`, `annotate_corpus`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `write_jsonl()` connect `Data Processing` to `Benchmark Infrastructure`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 39 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_CannedGenerator`) actually correct?**
  _`HashEmbedder` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `hierarchical_chunk()` (e.g. with `smoke_pipeline()` and `_distinct_pipeline()`) actually correct?**
  _`hierarchical_chunk()` has 20 INFERRED edges - model-reasoned connections that need verification._