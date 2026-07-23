# Graph Report - SEBI circular RAG  (2026-07-23)

## Corpus Check
- 124 files · ~65,761 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1375 nodes · 2880 edges · 69 communities (56 shown, 13 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 654 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c7af0411`
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

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 85 edges
2. `RAGPipeline` - 40 edges
3. `HashEmbedder` - 38 edges
4. `hierarchical_chunk()` - 36 edges
5. `ExtractiveStubGenerator` - 33 edges
6. `Lineage` - 31 edges
7. `build_lineage()` - 29 edges
8. `CircularMeta` - 28 edges
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

## Communities (69 total, 13 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.11
Nodes (25): BaseModel, build_default_pipeline(), _citation_meta(), CitationMeta, QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline.  Run (real stack; loads the, load_circulars() (+17 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.05
Nodes (61): Any, _doc(), auroc(), best_threshold(), evaluate(), P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t, main() (+53 more)

### Community 2 - "Data Processing"
Cohesion: 0.05
Nodes (69): annotate_regulation_fields(), build_regulation_edges(), _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7)., One `cites` edge per (circular, regulation) pair.      The merged edge carries t, Set regulations / primary_regulation / regulatory_basis_status in place.      Re, Yield (circular, Citation) for every citation occurrence in the corpus., Stub records for cited regulations absent from the Updated List.      Returns NE (+61 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.14
Nodes (10): FastAPI, create_app(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, /ready should trigger pipeline build and return ready=true., test_auth_required_when_key_set(), test_citation_meta_reports_superseded(), test_query_exceeds_time_budget_returns_504(), test_rate_limit() (+2 more)

### Community 4 - "Dataset Export"
Cohesion: 0.08
Nodes (50): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+42 more)

### Community 5 - "Utility Scripts"
Cohesion: 0.06
Nodes (49): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+41 more)

### Community 6 - "Spaces CPU Pipeline"
Cohesion: 0.07
Nodes (19): bootstrap_ci(), BootstrapCI, clopper_pearson_ci(), paired_delta(), PairedResult, ProportionCI, Uncertainty quantification for benchmark runs.  The golden set is n=56 answerabl, Clopper-Pearson exact interval for a binomial proportion.      Use this for stri (+11 more)

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
Nodes (11): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage.  Offline only —, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_none_and_empty_hyde_are_identical_to_baseline() (+3 more)

### Community 11 - "Benchmark Scripts"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 12 - "Qwen3MLXReranker"
Cohesion: 0.08
Nodes (11): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY)., (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'.      Takes the LAST bracket group, _record() (+3 more)

### Community 13 - "Lineage"
Cohesion: 0.13
Nodes (15): faithfulness(), _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), Generation with a hard abstention gate (D5).  If the top reranked score is below, True iff the reply names a valid excerpt number. 'none' or anything     unparsea (+7 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.14
Nodes (22): classify_answer(), classify_query(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any, Chunk IDs embed section headings containing spaces, so parse TREC     fields pos (+14 more)

### Community 15 - "Embedder"
Cohesion: 0.18
Nodes (7): Protocol, Generator, _grounded_prompt(), Judge, F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, Reranker, Chunk

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
Cohesion: 0.12
Nodes (14): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Answer, _currency(), demote_superseded(), mc_topic(), P2 — cross-document supersession resolution.  Classifies each circular's referen (+6 more)

### Community 20 - "test_gate.py"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan, _master(), test_annotate_idempotent() (+7 more)

### Community 21 - "Chunk"
Cohesion: 0.21
Nodes (13): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).      Nev (+5 more)

### Community 22 - "Corpus Validation"
Cohesion: 0.07
Nodes (32): Path, ProportionCI, _emit(), main(), Precision audit for circular -> regulation edges (spec 2026-07-23 §7).  Emits a, Up to `n` edges, spread as evenly as possible across evidence tiers.      Tiers, Clopper-Pearson interval over hand-labelled edge correctness., score() (+24 more)

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
Nodes (31): smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., RAGPipeline, LexicalReranker, Deterministic query-coverage reranker (test/fallback).      Score = fraction of (+23 more)

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "trace_failure.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 29 - "test_gate.py"
Cohesion: 0.18
Nodes (8): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., Build the dense+sparse index once and persist it (run after corpus changes)., Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, Stage-1 hybrid retrieval: dense (FAISS) + sparse (BM25) fused by RRF.  Mandatory, Central configuration: config.toml defaults, overridden by SEBI_RAG_* env vars.

### Community 30 - "build_lineage"
Cohesion: 0.25
Nodes (15): _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number(), _ocr_text(), Path, Local PDF ingestion for SEBI circulars.  Drop a circular PDF into data/raw/ and (+7 more)

### Community 31 - "detect_relations_ex"
Cohesion: 0.17
Nodes (9): Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, End-to-end wiring: segment -> hybrid retrieve -> rerank -> generate/abstain., Stage-2 reranking (mandatory, D4). Cross-encoder in production; a deterministic, _paragraphs(), Segmentation: hierarchical chunking + metadata + stable citation IDs.  Minimal,, Split into units each <= max_chars.      PDF-extracted text often lacks blank-li, Faithfulness: catch answers that cite circulars not in the retrieved context., Step 12 — end-to-end RAG integration test with the REAL stack.  bge-m3 (MPS) + b (+1 more)

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
Nodes (35): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).  Standalo, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual, HybridRetriever, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.  splad (+27 more)

### Community 40 - "test_incremental_index.py"
Cohesion: 0.19
Nodes (9): Calibrate top_k and the abstention threshold against the citation-precision sign, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., EvalReport, Golden-set evaluation harness (P1).  Runs the pipeline over a labelled golden se, report_dict(), run_eval(), SEBI Circular RAG — local-first, Apple Silicon.  Pipeline: ingest -> segment ->, P1 evaluation-harness test (offline).  Loads the real seed corpus (data/corpus/c (+1 more)

### Community 41 - "test_integration_e2e.py"
Cohesion: 0.14
Nodes (17): Pattern, _header(), _iso_date(), _labeled_date(), parse_meta(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars., _subject(), _make_pdf() (+9 more)

### Community 42 - "UI Components"
Cohesion: 0.43
Nodes (6): build_ui(), _empty_outputs(), _parse_as_of(), Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO     YYYY-MM-D, submit_query()

### Community 46 - "bench_rerankers.py"
Cohesion: 0.14
Nodes (13): Embedder, DenseIndex, _doc_checksum(), ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding, Deterministic per-document checksum over its (enriched) chunk texts —     captur, FAISS IndexFlatIP over L2-normalized vectors (cosine). (+5 more)

### Community 47 - "bench_retrieval.py"
Cohesion: 0.26
Nodes (11): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), _build_chunks(), _build_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline.  Runs fully offline (HashEmbed, test_abstention_on_out_of_domain_query() (+3 more)

### Community 48 - ".encode"
Cohesion: 0.22
Nodes (15): _as_bool(), _get(), Path, Settings.load() plus the [spaces] table as settings.spaces.*          Load order, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default, _clear(), Settings: defaults, config.toml, and env-override precedence. (+7 more)

### Community 49 - "test_gate.py"
Cohesion: 0.13
Nodes (23): answer_with_abstention(), ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge, _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested() (+15 more)

### Community 50 - "bench_retrieval.py"
Cohesion: 0.29
Nodes (13): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations() (+5 more)

### Community 51 - "_compute_kwargs"
Cohesion: 0.23
Nodes (14): hierarchical_chunk(), Document -> section -> paragraph chunks with stable IDs.      A "section" is det, _body(), Chunker (segment.hierarchical_chunk) behaviour.  Regression guard for the "5. Nu, Chunk text is 'breadcrumb-header\\nbody'; return the body., test_absorption_respects_300_char_cap(), test_bare_parent_heading_folds_into_first_subsection(), test_bare_parent_heading_not_emitted_as_standalone_chunk() (+6 more)

### Community 52 - "paired_delta"
Cohesion: 0.18
Nodes (16): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic, _chunk(), Query-side lexical expansion (intervention #2, glossary variant).  Lay->statutor, test_all_five_sparse_failure_queries_expand(), test_expanded_sparse_query_hits_statutory_chunk(), test_lay_term_gains_statutory_synonym() (+8 more)

### Community 53 - "bootstrap_ci"
Cohesion: 0.16
Nodes (9): HF Spaces path: corpus_spaces loader mapping + HybridGenerator fallback.  Fully, ExternalSpaceGenerator must call huggingface-projects/llama-2-7b-chat's     veri, settings(), test_chunks_config_refuses_header_and_maps_fields(), test_corpus_records_feed_build_lineage(), test_external_space_generator_abstains_without_contexts(), test_external_space_generator_calls_llama2_generate_signature(), test_hybrid_falls_back_on_external_failure() (+1 more)

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
Cohesion: 0.31
Nodes (7): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces()

### Community 59 - "corpus_spaces.py"
Cohesion: 0.08
Nodes (33): main(), annotate_corpus(), build_lineage(), detect_relations(), detect_relations_ex(), load_records(), Path, Update each corpus record's supersession_status + superseded_by + supersedes (+25 more)

### Community 60 - "eval.py"
Cohesion: 0.15
Nodes (15): _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker., pick_device(), Device + precision selection for Apple-Silicon inference.  Centralizes the mps/c, Resolve the compute device.      A truthy explicit `pref` ("mps"/"cpu"/"cuda") w, fp16 only on GPU-class devices; never on cpu. bf16 is never returned     here by, should_use_fp16(), test_compute_kwargs_cpu_disables_fp16() (+7 more)

### Community 61 - "test_integration_e2e.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 63 - "test_persistence.py"
Cohesion: 0.33
Nodes (3): Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 64 - "faithfulness"
Cohesion: 0.24
Nodes (14): build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t, _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row() (+6 more)

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Embedder` to `Core RAG Pipeline`, `Benchmark Infrastructure`, `.grounded`, `Lineage`, `Master Metadata`, `lineage.py`, `Chunk`, `Answer Generation`, `test_gate.py`, `detect_relations_ex`, `annotate_corpus`, `test_incremental_index.py`, `bench_rerankers.py`, `test_gate.py`, `_compute_kwargs`, `paired_delta`, `bootstrap_ci`, `build_index.py`, `test_integration_e2e.py`, `test_persistence.py`, `faithfulness`?**
  _High betweenness centrality (0.154) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `Answer Generation` to `Core RAG Pipeline`, `Benchmark Infrastructure`, `faithfulness`, `Index & Evaluation`, `annotate_corpus`, `test_incremental_index.py`, `bench_rerankers.py`, `Embedder`, `lineage.py`, `SparseIndex`, `detect_relations_ex`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `Lineage` connect `Core RAG Pipeline` to `faithfulness`, `lineage.py`, `SparseIndex`, `Answer Generation`, `corpus_spaces.py`, `detect_relations_ex`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_CannedGenerator`) actually correct?**
  _`HashEmbedder` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `hierarchical_chunk()` (e.g. with `smoke_pipeline()` and `_distinct_pipeline()`) actually correct?**
  _`hierarchical_chunk()` has 27 INFERRED edges - model-reasoned connections that need verification._