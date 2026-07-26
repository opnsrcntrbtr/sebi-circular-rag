# Graph Report - golden-v7  (2026-07-26)

## Corpus Check
- 148 files · ~149,437 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1706 nodes · 3675 edges · 95 communities (80 shown, 15 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 860 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1f2fbc35`
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
- audit_reg_edges.py
- test_eval_harness_v7.py
- bootstrap_ci
- .encode
- load_golden
- test_repair_corpus_text.py
- test_injection.py
- TestReadTrecRun
- main
- test_benchmark.py
- .test_mean_reproduces_the_archived_aggregate

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 89 edges
2. `RAGPipeline` - 43 edges
3. `hierarchical_chunk()` - 43 edges
4. `HashEmbedder` - 42 edges
5. `ExtractiveStubGenerator` - 37 edges
6. `CircularMeta` - 36 edges
7. `Lineage` - 33 edges
8. `build_lineage()` - 30 edges
9. `LexicalReranker` - 28 edges
10. `extract_citations()` - 25 edges

## Surprising Connections (you probably didn't know these)
- `test_run_metadata_has_reproducibility_fields()` --calls--> `run_metadata()`  [INFERRED]
  tests/test_benchmark.py → src/sebi_rag/benchmark.py
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_parse_meta_dept_order_document_end_to_end()` --calls--> `parse_meta()`  [INFERRED]
  tests/test_ingest_refs.py → src/sebi_rag/ingest_pdf.py
- `test_parse_meta_excludes_prefix_variant_self_reference()` --calls--> `parse_meta()`  [INFERRED]
  tests/test_ingest_refs.py → src/sebi_rag/ingest_pdf.py
- `test_to_record_carries_injection_flags()` --calls--> `to_record()`  [INFERRED]
  tests/test_injection.py → src/sebi_rag/ingest_pdf.py

## Import Cycles
- None detected.

## Communities (95 total, 15 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.07
Nodes (50): Random, _apportion(), ingest_packet(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV ingest, Writes the blind human packet for `human_ids` (a subset of `ids`, the     full e, Reads a human-filled labels_template.csv back into vote records     (`annotator: (+42 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.17
Nodes (25): Any, main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), dir_fingerprint() (+17 more)

### Community 2 - "Data Processing"
Cohesion: 0.16
Nodes (28): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair.      The merged edge carries t, Set regulations / primary_regulation / regulatory_basis_status in place.      Re, Stub records for cited regulations absent from the Updated List.      Returns NE, synthesise_repealed_stubs(), _circ(), Regulation edges + corpus annotation (spec 2026-07-23 §3.3, §3.4, §3.7). (+20 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.05
Nodes (64): Path, adjudicate(), build_prompt(), _current_model(), _daily_quota_exhausted(), main(), _parse_error_ids(), _parse_letter_choice() (+56 more)

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
Cohesion: 0.28
Nodes (12): chunks_by_doc(), _norm_ws(), Span {doc, quote} -> matching chunk ids (all overlap matches count).      Legacy, resolve_chunk_spans(), _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through() (+4 more)

### Community 11 - "Benchmark Scripts"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 13 - "Lineage"
Cohesion: 0.22
Nodes (15): _as_bool(), _get(), Path, Settings.load() plus the [spaces] table as settings.spaces.*          Load order, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default, _clear(), Settings: defaults, config.toml, and env-override precedence. (+7 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.09
Nodes (30): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any (+22 more)

### Community 15 - "Embedder"
Cohesion: 0.23
Nodes (13): build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row() (+5 more)

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
Cohesion: 0.07
Nodes (47): Protocol, Answer, answer_with_abstention(), ExtractiveStubGenerator, faithfulness(), Generator, _grounded_prompt(), Judge (+39 more)

### Community 20 - "test_gate.py"
Cohesion: 0.20
Nodes (5): BM25 lexical index (bm25s)., Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), SparseIndex, test_rrf_fusion_orders_by_reciprocal_rank()

### Community 21 - "Chunk"
Cohesion: 0.11
Nodes (22): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).      Nev (+14 more)

### Community 22 - "Corpus Validation"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 23 - "Reranking"
Cohesion: 0.09
Nodes (34): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).  Deliber, All regulation citations in a circular, one per occurrence (not deduped).      S, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years.      "Regulations (+26 more)

### Community 24 - "ZeroGPU Tests"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 25 - "Dataset Push"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 26 - "Answer Generation"
Cohesion: 0.08
Nodes (40): BaseModel, FastAPI, main(), build_default_pipeline(), _citation_meta(), CitationMeta, _compute_kwargs(), create_app() (+32 more)

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 29 - "test_gate.py"
Cohesion: 0.07
Nodes (35): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A (+27 more)

### Community 30 - "build_lineage"
Cohesion: 0.24
Nodes (12): build_report(), Assemble the persisted as-of run artifact.      Pipeline accuracy is the headlin, Aggregate case results with an exact confidence interval.      Pure function of, summarize(), Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid     measureme, The headline number must be the 10 pipeline cases alone — the whole     point of, _results() (+4 more)

### Community 31 - "detect_relations_ex"
Cohesion: 0.31
Nodes (7): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces()

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
Cohesion: 0.09
Nodes (29): _alias_keys(), load_regulations(), name_tokens(), Path, Candidate alias lookup keys, most literal first.      Both the raw normalised fo, Resolve a cited regulation name+year to a canonical reg_id.      Returns (reg_id, Load data/corpus/regulations.jsonl into a list of regulation records.      Thin, Comparison tokens: lowercased, punctuation-split, stopwords dropped,     naively (+21 more)

### Community 41 - "test_integration_e2e.py"
Cohesion: 0.15
Nodes (19): Re-derive circular number + dates from each record's stored text and rewrite the, _existing_numbers(), extract_text(), ingest(), main(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars.  Drop a circular PDF into data/raw/ and (+11 more)

### Community 42 - "UI Components"
Cohesion: 0.24
Nodes (10): Human-readable regulation name. Year disambiguates same-short_name repeal     pa, reg_display_name(), build_ui(), _empty_outputs(), _parse_as_of(), Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO     YYYY-MM-D, submit_query() (+2 more)

### Community 46 - "bench_rerankers.py"
Cohesion: 0.17
Nodes (11): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage.  Offline only —, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_none_and_empty_hyde_are_identical_to_baseline() (+3 more)

### Community 47 - "bench_retrieval.py"
Cohesion: 0.10
Nodes (27): load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., hierarchical_chunk(), _paragraphs(), Segmentation: hierarchical chunking + metadata + stable citation IDs.  Minimal,, Split into units each <= max_chars.      PDF-extracted text often lacks blank-li, Document -> section -> paragraph chunks with stable IDs.      A "section" is det (+19 more)

### Community 48 - ".encode"
Cohesion: 0.21
Nodes (8): Embedder, DenseIndex, _doc_checksum(), ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding, Deterministic per-document checksum over its (enriched) chunk texts —     captur, FAISS IndexFlatIP over L2-normalized vectors (cosine).

### Community 49 - "answer_with_abstention"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 50 - "bench_retrieval.py"
Cohesion: 0.20
Nodes (20): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, Every record's text must match the PDF its provenance names.      Slow (re-extra, validate(), validate_deep(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o (+12 more)

### Community 51 - "_compute_kwargs"
Cohesion: 0.09
Nodes (45): apply(), _body(), _claude_accuracy_ci(), cohen_kappa(), decide(), _label(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation slic (+37 more)

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
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer.      Read-onl, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 57 - "SparseIndex"
Cohesion: 0.25
Nodes (5): BootstrapCI, PairedResult, Uncertainty quantification for benchmark runs.  The golden set is n=56 answerabl, True when the randomization test rejects at 1 - confidence AND the         paire, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 58 - "discover_new.py"
Cohesion: 0.11
Nodes (32): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate (2026-07-25 (+24 more)

### Community 59 - "corpus_spaces.py"
Cohesion: 0.06
Nodes (44): annotate_corpus(), detect_relations(), detect_relations_ex(), Path, Update each corpus record's supersession_status + superseded_by + supersedes, Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window() (+36 more)

### Community 60 - "eval.py"
Cohesion: 0.20
Nodes (11): pick_device(), Device + precision selection for Apple-Silicon inference.  Centralizes the mps/c, Resolve the compute device.      A truthy explicit `pref` ("mps"/"cpu"/"cuda") w, fp16 only on GPU-class devices; never on cpu. bf16 is never returned     here by, should_use_fp16(), Device + fp16 policy selection (no real torch/mps required)., test_pick_device_auto_cpu_when_no_mps(), test_pick_device_auto_mps_when_available() (+3 more)

### Community 61 - "test_integration_e2e.py"
Cohesion: 0.07
Nodes (52): smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, build_lineage(), _currency(), mc_topic(), Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None.      Us, LexicalReranker (+44 more)

### Community 62 - "test_pipeline.py"
Cohesion: 0.47
Nodes (5): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), test_retrieval_metrics()

### Community 63 - "test_persistence.py"
Cohesion: 0.15
Nodes (14): Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7)., derive_regulatory_basis(), _jaccard(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6).  Regulations, Regulatory-basis status of one circular from its resolved regulations.      `unk, Deterministic, stable identity slug. This is the edge target and join key., reg_id(), RegulationMeta (+6 more)

### Community 64 - "faithfulness"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline).  No networ, write_jsonl()

### Community 65 - "LexicalReranker"
Cohesion: 0.23
Nodes (12): assemble_pool(), main(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of, TREC-style pool: gold-doc literal matches lead, then round-robin over     [reran, One gold doc with `n` chunks that ALL contain the word "broker", so a     must_c, Regression (2026-07-25): a must_contain literal matching many gold-doc     chunk, _retriever(), _saturating_retriever() (+4 more)

### Community 66 - "eval_harness.py"
Cohesion: 0.53
Nodes (5): _fmt(), main(), Path, Re-score archived benchmark runs with bootstrap CIs and paired significance.  Re, score_run()

### Community 67 - "validate_golden_v7"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden.      `chunks` is optio, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 69 - "acquire_missing_pdfs.py"
Cohesion: 0.26
Nodes (11): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+3 more)

### Community 70 - "Chunk"
Cohesion: 0.67
Nodes (3): _chunk(), test_retrieve_dense_leg_keeps_raw_query(), test_retrieve_routes_expanded_query_to_sparse_leg()

### Community 71 - "HybridRetriever"
Cohesion: 0.46
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are e, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 72 - "scrape_regulations.py"
Cohesion: 0.27
Nodes (10): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY)., (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'.      Takes the LAST bracket group, _record() (+2 more)

### Community 73 - "resolve_chunk_spans"
Cohesion: 0.15
Nodes (14): main(), per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.      A, run_retrieval_benchmark(), _aggregate(), _doc(), _eval_item(), EvalReport (+6 more)

### Community 74 - "test_ingest_refs.py"
Cohesion: 0.17
Nodes (10): _primary_number(), Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104",     "HO/ (, References split across tokens: merge up to 4 tokens after the first     HO/CIR/, _rejoin_split(), _s_anchor_merge(), Regression matrix for SEBI reference-number extraction.  One case per known form, test_fulltext_fallback_returns_earliest_body_reference(), test_parse_meta_dept_order_document_end_to_end() (+2 more)

### Community 75 - "test_build_reg_edges.py"
Cohesion: 0.43
Nodes (6): _body(), main(), _norm(), pick(), Label the 7 rows re-pooled after the assemble_pool fix (2026-07-25 remediation T, (candidate, quote) pairs for this row: the answer_contains carrier     first, th

### Community 79 - "test_ingest_pdf.py"
Cohesion: 0.15
Nodes (17): Pattern, _iso_date(), _labeled_date(), parse_meta(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF., A PDF kerning artifact can render the number's own '/' as a typographic     en-d (+9 more)

### Community 81 - "paired_delta"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries.      Returns mean_b - m, Randomization p-values use the (count+1)/(n+1) estimator, so a         p-value o, One query flipping out of 56 is exactly the iv9-style verdict: the         rando, TestPairedDelta

### Community 82 - "verify_master.py"
Cohesion: 0.67
Nodes (3): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:

### Community 84 - "audit_reg_edges.py"
Cohesion: 0.29
Nodes (10): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7).  Emits a, Up to `n` edges, spread as evenly as possible across evidence tiers.      Tiers, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+2 more)

### Community 86 - "test_eval_harness_v7.py"
Cohesion: 0.49
Nodes (10): run_eval(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-le, _row(), test_as_of_is_passed_to_pipeline(), test_chunk_metrics_computed_for_span_rows(), test_gate_is_none_when_nothing_adjudicated(), test_gate_subreport_covers_only_adjudicated() (+2 more)

### Community 87 - "bootstrap_ci"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must         be, TestBootstrapCI

### Community 90 - "load_golden"
Cohesion: 0.28
Nodes (6): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).  C, load_golden(), Path, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 91 - "test_repair_corpus_text.py"
Cohesion: 0.18
Nodes (7): main(), Repair the 6 records whose body text was overwritten with one shared circular's, normalize_circular_number(), Canonical COMPARISON key for a circular number: strip whitespace and     trailin, test_dedup_uses_normalized_numbers(), The repair map must name a real orphan PDF that parses to the circular_number it, test_numbers_normalize_distinctly()

### Community 92 - "test_injection.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 93 - "TestReadTrecRun"
Cohesion: 0.33
Nodes (5): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}., read_trec_run(), write_trec_run(), The archived runfiles embed section headings in the doc id., TestReadTrecRun

### Community 95 - "main"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation.  Outputs:, write_card()

### Community 96 - "test_benchmark.py"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `lineage.py` to `Benchmark Infrastructure`, `.grounded`, `Embedder`, `Master Metadata`, `test_gate.py`, `Chunk`, `Answer Generation`, `test_gate.py`, `annotate_corpus`, `bench_rerankers.py`, `bench_retrieval.py`, `.encode`, `build_index.py`, `test_integration_e2e.py`, `validate_golden_v7`, `Chunk`, `test_injection.py`, `main`, `test_benchmark.py`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `Answer Generation` to `Benchmark Infrastructure`, `resolve_chunk_spans`, `Embedder`, `.encode`, `test_integration_e2e.py`, `lineage.py`, `TestReadTrecRun`, `test_eval_harness_v7.py`, `test_gate.py`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Why does `extract_citations()` connect `Reranking` to `Data Processing`, `test_persistence.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `hierarchical_chunk()` (e.g. with `smoke_pipeline()` and `_distinct_pipeline()`) actually correct?**
  _`hierarchical_chunk()` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_CannedGenerator`) actually correct?**
  _`HashEmbedder` has 38 INFERRED edges - model-reasoned connections that need verification._