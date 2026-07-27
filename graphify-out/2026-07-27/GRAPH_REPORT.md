# Graph Report - SEBI circular RAG  (2026-07-27)

## Corpus Check
- 154 files · ~154,351 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1804 nodes · 3820 edges · 107 communities (92 shown, 15 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 879 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ac9c797e`
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
- test_build_reg_edges.py
- load_regulations
- test_acquire_missing.py
- _alias_keys
- test_ingest_pdf.py
- test_faithfulness.py
- paired_delta
- verify_master.py
- load_regulations
- audit_reg_edges.py
- test_integration_e2e.py
- test_eval_harness_v7.py
- bootstrap_ci
- load_golden_asof
- .encode
- load_golden
- test_repair_corpus_text.py
- test_injection.py
- TestReadTrecRun
- SpladeIndex
- main
- test_benchmark.py
- .test_mean_reproduces_the_archived_aggregate
- test_golden_v7_local.py
- test_splade_leg.py
- Chunk
- __init__.py
- app.py
- settings.py
- .encode
- TestPerQueryRecall

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 80 edges
2. `HashEmbedder` - 39 edges
3. `hierarchical_chunk()` - 37 edges
4. `ExtractiveStubGenerator` - 36 edges
5. `RAGPipeline` - 36 edges
6. `Lineage` - 33 edges
7. `build_lineage()` - 30 edges
8. `CircularMeta` - 30 edges
9. `extract_citations()` - 25 edges
10. `HybridRetriever` - 25 edges

## Surprising Connections (you probably didn't know these)
- `test_run_metadata_has_reproducibility_fields()` --calls--> `run_metadata()`  [INFERRED]
  tests/test_benchmark.py → src/sebi_rag/benchmark.py
- `test_legacy_string_entries_pass_through()` --calls--> `resolve_chunk_spans()`  [INFERRED]
  tests/test_golden_v7_resolver.py → src/sebi_rag/benchmark.py
- `test_numbers_normalize_distinctly()` --calls--> `normalize_circular_number()`  [INFERRED]
  tests/test_repair_corpus_text.py → src/sebi_rag/ingest_pdf.py
- `test_to_record_carries_injection_flags()` --calls--> `to_record()`  [INFERRED]
  tests/test_injection.py → src/sebi_rag/ingest_pdf.py
- `test_real_corpus_loads_with_provenance_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_eval_harness.py → src/sebi_rag/corpus.py

## Import Cycles
- None detected.

## Communities (107 total, 15 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.07
Nodes (54): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV ingest, Writes the blind human packet for `human_ids` (a subset of `ids`, the     full e (+46 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.16
Nodes (29): Any, Chunk, main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6() (+21 more)

### Community 2 - "Data Processing"
Cohesion: 0.07
Nodes (56): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline).  No networ, write_jsonl(), annotate_regulation_fields(), build_regulation_edges(), build_regulatory_index() (+48 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.12
Nodes (25): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape).     Non-abst, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing, a, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as     "confirms abs, A non-abstain row whose pool happens to have zero candidates can't     offer any, letters=[] is how adjudicate signals an abstain/zero-candidate row;     parse_re, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct     from a we (+17 more)

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

### Community 10 - ".grounded"
Cohesion: 0.42
Nodes (8): _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through(), test_qrels_span_rows_get_grade_2(), test_resolves_normalized_whitespace_quote(), test_unresolvable_quote_returns_empty(), test_validator_flags_unresolvable_quote_when_chunks_given()

### Community 11 - "Benchmark Scripts"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 13 - "Lineage"
Cohesion: 0.13
Nodes (34): BaseModel, main(), main(), build_default_pipeline(), CitationMeta, QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline.  Run (real stack; loads the (+26 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.13
Nodes (24): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any (+16 more)

### Community 15 - "Embedder"
Cohesion: 0.16
Nodes (20): get_pipeline(), Cache one pipeline per mode; both share retriever/reranker/lineage., _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker., build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t, _keep() (+12 more)

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
Nodes (6): auroc(), best_threshold(), evaluate(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t

### Community 20 - "test_gate.py"
Cohesion: 0.09
Nodes (34): derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).  Write, metric -> per-query score vector, into gate-floor names -> floor value.      Met, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the derived, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed     v7 gate,, True iff every floor's metric is present in `report_gate` and meets it.      Mis (+26 more)

### Community 21 - "Chunk"
Cohesion: 0.11
Nodes (22): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).      Nev (+14 more)

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
Cohesion: 0.15
Nodes (13): main(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of, _body(), main(), _norm(), pick(), Label the 7 rows re-pooled after the assemble_pool fix (2026-07-25 remediation T, (candidate, quote) pairs for this row: the answer_contains carrier     first, th (+5 more)

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 29 - "test_gate.py"
Cohesion: 0.11
Nodes (20): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, Emit one JSON line of retrieval/citation/abstention metrics using the persisted, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, faithfulness(), Generation with a hard abstention gate (D5).  If the top reranked score is below, Check that every circular id the answer cites (in square brackets) was     actua (+12 more)

### Community 30 - "build_lineage"
Cohesion: 0.22
Nodes (15): _as_bool(), _get(), Path, Settings.load() plus the [spaces] table as settings.spaces.*          Load order, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default, _clear(), Settings: defaults, config.toml, and env-override precedence. (+7 more)

### Community 31 - "detect_relations_ex"
Cohesion: 0.20
Nodes (7): Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., Stage-1 hybrid retrieval: dense (FAISS) + sparse (BM25) fused by RRF.  Mandatory, _chunks(), Index persistence round-trip (offline)., test_index_save_load_roundtrip()

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
Cohesion: 0.07
Nodes (28): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).  Standalo, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.  splad, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+20 more)

### Community 40 - "test_incremental_index.py"
Cohesion: 0.16
Nodes (15): _jaccard(), Resolve a cited regulation name+year to a canonical reg_id.      Returns (reg_id, resolve_regulation(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6)., Singular/plural and dropped-stopword variants normalise to identical     token s, A citation carrying a spurious extra token still resolves, but only via     the, test_acronym_aliases_resolve_as_explicit_text(), test_alias_year_matters() (+7 more)

### Community 41 - "test_integration_e2e.py"
Cohesion: 0.14
Nodes (22): Re-derive circular number + dates from each record's stored text and rewrite the, _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number(), _ocr_text(), Path (+14 more)

### Community 42 - "UI Components"
Cohesion: 0.24
Nodes (10): Human-readable regulation name. Year disambiguates same-short_name repeal     pa, reg_display_name(), build_ui(), _empty_outputs(), _parse_as_of(), Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO     YYYY-MM-D, submit_query() (+2 more)

### Community 46 - "bench_rerankers.py"
Cohesion: 0.17
Nodes (11): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage.  Offline only —, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_none_and_empty_hyde_are_identical_to_baseline() (+3 more)

### Community 47 - "bench_retrieval.py"
Cohesion: 0.23
Nodes (14): hierarchical_chunk(), Document -> section -> paragraph chunks with stable IDs.      A "section" is det, _body(), Chunker (segment.hierarchical_chunk) behaviour.  Regression guard for the "5. Nu, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_absorption_respects_300_char_cap(), test_bare_parent_heading_folds_into_first_subsection(), test_bare_parent_heading_not_emitted_as_standalone_chunk() (+6 more)

### Community 48 - ".encode"
Cohesion: 0.15
Nodes (13): Embedder, DenseIndex, _doc_checksum(), ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding, Deterministic per-document checksum over its (enriched) chunk texts —     captur, FAISS IndexFlatIP over L2-normalized vectors (cosine). (+5 more)

### Community 49 - "answer_with_abstention"
Cohesion: 0.12
Nodes (14): FastAPI, _citation_meta(), create_app(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, /ready should trigger pipeline build and return ready=true., test_auth_required_when_key_set(), test_citation_meta_defaults_when_circular_absent_from_index(), test_citation_meta_defaults_when_index_none() (+6 more)

### Community 50 - "bench_retrieval.py"
Cohesion: 0.33
Nodes (14): validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations(), test_duplicate_text_across_records_flagged(), test_empty_text_is_not_a_duplicate_cluster(), test_flags_bad_issue_date() (+6 more)

### Community 51 - "_compute_kwargs"
Cohesion: 0.06
Nodes (64): apply(), _body(), _claude_accuracy_ci(), cohen_kappa(), _confirms_claude(), decide(), _label(), _literals_by_row() (+56 more)

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
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the docume, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 56 - "SparseIndex"
Cohesion: 0.21
Nodes (13): answer_with_abstention(), ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge, _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested() (+5 more)

### Community 57 - "SparseIndex"
Cohesion: 0.25
Nodes (5): BootstrapCI, PairedResult, Uncertainty quantification for benchmark runs.  The golden set is n=56 answerabl, True when the randomization test rejects at 1 - confidence AND the         paire, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 58 - "discover_new.py"
Cohesion: 0.16
Nodes (22): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate (2026-07-25 (+14 more)

### Community 59 - "corpus_spaces.py"
Cohesion: 0.19
Nodes (12): main(), One scoring path shared by `eval_json.py` (which measures) and `derive_threshold, Score one golden row through the production-shaped pipeline.      Returns per-ro, Per-row records -> metric -> score vector, skipping rows where the     metric wa, score_row(), vectors(), per_query_recall(), RAGPipeline (+4 more)

### Community 60 - "eval.py"
Cohesion: 0.20
Nodes (11): pick_device(), Device + precision selection for Apple-Silicon inference.  Centralizes the mps/c, Resolve the compute device.      A truthy explicit `pref` ("mps"/"cpu"/"cuda") w, fp16 only on GPU-class devices; never on cpu. bf16 is never returned     here by, should_use_fp16(), Device + fp16 policy selection (no real torch/mps required)., test_pick_device_auto_cpu_when_no_mps(), test_pick_device_auto_mps_when_available() (+3 more)

### Community 61 - "test_integration_e2e.py"
Cohesion: 0.18
Nodes (16): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), _build_chunks(), _build_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline.  Runs fully offline (HashEmbed, Offline pipeline whose single circular rests on a repealed regulation. (+8 more)

### Community 62 - "test_pipeline.py"
Cohesion: 0.29
Nodes (8): _alias_keys(), Candidate alias lookup keys, most literal first.      Both the raw normalised fo, PMS/NCS/ILDS end in a literal S. Unconditional plural-stripping mapped     them, reg_id resolved purely through the alias table, ignoring the corpus., A table key that no _alias_keys() output can produce is dead config., _resolved(), test_acronyms_ending_in_s_reach_their_own_entry(), test_every_alias_entry_is_reachable_from_some_spelling()

### Community 63 - "test_persistence.py"
Cohesion: 0.18
Nodes (11): derive_regulatory_basis(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6).  Regulations, Regulatory-basis status of one circular from its resolved regulations.      `unk, Deterministic, stable identity slug. This is the edge target and join key., reg_id(), RegulationMeta, _slug(), test_derive_regulatory_basis_truth_table() (+3 more)

### Community 64 - "faithfulness"
Cohesion: 0.10
Nodes (26): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec 2026-0 (+18 more)

### Community 65 - "LexicalReranker"
Cohesion: 0.31
Nodes (10): assemble_pool(), TREC-style pool: gold-doc literal matches lead, then round-robin over     [reran, One gold doc with `n` chunks that ALL contain the word "broker", so a     must_c, Regression (2026-07-25): a must_contain literal matching many gold-doc     chunk, _retriever(), _saturating_retriever(), test_bm25_leg_uses_raw_query_not_expansion(), test_deep_relevant_chunk_is_reachable_despite_a_common_literal() (+2 more)

### Community 66 - "eval_harness.py"
Cohesion: 0.53
Nodes (5): _fmt(), main(), Path, Re-score archived benchmark runs with bootstrap CIs and paired significance.  Re, score_run()

### Community 67 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden.      `chunks` is optio, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 68 - "SpladeIndex"
Cohesion: 0.28
Nodes (10): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge() (+2 more)

### Community 69 - "acquire_missing_pdfs.py"
Cohesion: 0.26
Nodes (11): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+3 more)

### Community 70 - "Chunk"
Cohesion: 0.14
Nodes (29): smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., LexicalReranker, Deterministic query-coverage reranker (test/fallback).      Score = fraction of, CircularMeta (+21 more)

### Community 71 - "HybridRetriever"
Cohesion: 0.46
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are e, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 72 - "scrape_regulations.py"
Cohesion: 0.27
Nodes (10): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY)., (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'.      Takes the LAST bracket group, _record() (+2 more)

### Community 73 - "resolve_chunk_spans"
Cohesion: 0.12
Nodes (14): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Answer, _currency(), demote_superseded(), mc_topic(), P2 — cross-document supersession resolution.  Classifies each circular's referen (+6 more)

### Community 74 - "test_ingest_refs.py"
Cohesion: 0.50
Nodes (4): Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104",     "HO/ (, References split across tokens: merge up to 4 tokens after the first     HO/CIR/, _rejoin_split(), _s_anchor_merge()

### Community 75 - "test_build_reg_edges.py"
Cohesion: 0.47
Nodes (8): remap(), Doc-id remapping after the 2026-07-25 corpus renumbering (Task 4)., _row(), test_input_rows_are_not_mutated(), test_matching_is_normalization_insensitive(), test_remaps_must_not_cite(), test_remaps_relevant_circulars_and_span_docs(), test_unmapped_rows_untouched()

### Community 76 - "load_regulations"
Cohesion: 0.06
Nodes (40): annotate_corpus(), detect_relations(), detect_relations_ex(), Update each corpus record's supersession_status + superseded_by + supersedes, Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window(), annotate_master_fields() (+32 more)

### Community 78 - "_alias_keys"
Cohesion: 0.38
Nodes (6): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, Every record's text must match the PDF its provenance names.      Slow (re-extra, validate_deep()

### Community 79 - "test_ingest_pdf.py"
Cohesion: 0.10
Nodes (23): Pattern, _iso_date(), _labeled_date(), parse_meta(), _primary_number(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF. (+15 more)

### Community 80 - "test_faithfulness.py"
Cohesion: 0.15
Nodes (11): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), True iff the reply names a valid excerpt number. 'none' or anything     unparsea, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the     gat, Deterministic groundedness judge on MLX (greedy decode, temp 0).      Pass share (+3 more)

### Community 81 - "paired_delta"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries.      Returns mean_b - m, Randomization p-values use the (count+1)/(n+1) estimator, so a         p-value o, One query flipping out of 56 is exactly the iv9-style verdict: the         rando, TestPairedDelta

### Community 82 - "verify_master.py"
Cohesion: 0.33
Nodes (3): Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 84 - "audit_reg_edges.py"
Cohesion: 0.29
Nodes (10): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7).  Emits a, Up to `n` edges, spread as evenly as possible across evidence tiers.      Tiers, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+2 more)

### Community 85 - "test_integration_e2e.py"
Cohesion: 0.40
Nodes (5): load_regulations(), Path, Load data/corpus/regulations.jsonl into a list of regulation records.      Thin, test_load_regulations_round_trips(), test_load_regulations_skips_blank_lines()

### Community 86 - "test_eval_harness_v7.py"
Cohesion: 0.25
Nodes (17): _aggregate(), _eval_item(), EvalReport, _mean(), RAGPipeline, Golden-set evaluation harness (P1).  Runs the pipeline over a labelled golden se, report_dict(), run_eval() (+9 more)

### Community 87 - "bootstrap_ci"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must         be, TestBootstrapCI

### Community 88 - "load_golden_asof"
Cohesion: 0.12
Nodes (25): AsofCaseResult, build_report(), load_golden_asof(), Path, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, Assemble the persisted as-of run artifact.      Pipeline accuracy is the headlin, Aggregate case results with an exact confidence interval.      Pure function of, run_pipeline_cases() (+17 more)

### Community 89 - ".encode"
Cohesion: 0.18
Nodes (15): _current_model(), main(), pilot(), _pilot_ids(), _post_local(), Path, External annotation slice: local-model leg via oMLX - the PRIMARY leg since 2026, First `n` non-abstain external ids, distinct strata first: five rows     from fi (+7 more)

### Community 90 - "load_golden"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).  C, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 91 - "test_repair_corpus_text.py"
Cohesion: 0.22
Nodes (4): main(), Repair the 6 records whose body text was overwritten with one shared circular's, The repair map must name a real orphan PDF that parses to the circular_number it, test_numbers_normalize_distinctly()

### Community 92 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 93 - "TestReadTrecRun"
Cohesion: 0.16
Nodes (10): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}., read_trec_run(), write_trec_run(), _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields() (+2 more)

### Community 94 - "SpladeIndex"
Cohesion: 0.67
Nodes (3): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:

### Community 95 - "main"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation.  Outputs:, write_card()

### Community 97 - ".test_mean_reproduces_the_archived_aggregate"
Cohesion: 0.22
Nodes (11): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt)     -> str, Scans the per-row cache for `ids` and returns the ones flagged     parse_error:, Same per-row deterministic shuffle as make_packet.py's write_packet:     random., _shuffled_candidates(), Defensive: an id that was never adjudicated (no cache file at all)     is not re (+3 more)

### Community 98 - "test_golden_v7_local.py"
Cohesion: 0.22
Nodes (14): _extract_text(), Anthropic Messages response -> reply text: concatenates `text`     content block, _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external ann, Five pilot rows from five strata measure more than five from one -     the gemin, Vote records must say annotator "qwen" (never reuse "gemini" - the     agreement, Back-compat guard: the gemini leg (on hold, not removed) must keep     producing, _row() (+6 more)

### Community 99 - "test_splade_leg.py"
Cohesion: 0.67
Nodes (3): name_tokens(), Comparison tokens: lowercased, punctuation-split, stopwords dropped,     naively, test_name_tokens_singularises_and_drops_stopwords()

### Community 101 - "Chunk"
Cohesion: 0.20
Nodes (7): Protocol, Generator, _grounded_prompt(), Judge, F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, Reranker, Chunk

### Community 103 - "app.py"
Cohesion: 0.28
Nodes (6): build_ui(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces(), Central configuration: config.toml defaults, overridden by SEBI_RAG_* env vars.

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `Lineage`, `Embedder`, `Master Metadata`, `Chunk`, `test_gate.py`, `detect_relations_ex`, `annotate_corpus`, `bench_rerankers.py`, `bench_retrieval.py`, `.encode`, `build_index.py`, `SparseIndex`, `SpladeIndex`, `Chunk`, `resolve_chunk_spans`, `test_faithfulness.py`, `verify_master.py`, `test_injection.py`, `TestReadTrecRun`, `main`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `load_golden()` connect `Answer Generation` to `faithfulness`, `Core RAG Pipeline`, `eval_harness.py`, `Benchmark Infrastructure`, `load_golden`, `Lineage`, `_compute_kwargs`, `test_eval_harness_v7.py`, `.encode`, `discover_new.py`, `corpus_spaces.py`, `main`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `main()` connect `Lineage` to `Benchmark Infrastructure`, `annotate_corpus`, `Chunk`, `bench_rerankers.py`, `Embedder`, `.encode`, `TestReadTrecRun`, `Answer Generation`, `corpus_spaces.py`, `test_gate.py`, `build_lineage`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Are the 39 inferred relationships involving `Chunk` (e.g. with `HeaderGenerator` and `Answer`) actually correct?**
  _`Chunk` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_CannedGenerator`) actually correct?**
  _`HashEmbedder` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `hierarchical_chunk()` (e.g. with `smoke_pipeline()` and `_distinct_pipeline()`) actually correct?**
  _`hierarchical_chunk()` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `ExtractiveStubGenerator` (e.g. with `get_pipeline()` and `main()`) actually correct?**
  _`ExtractiveStubGenerator` has 31 INFERRED edges - model-reasoned connections that need verification._