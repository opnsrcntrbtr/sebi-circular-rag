# Graph Report - SEBI circular RAG  (2026-07-17)

## Corpus Check
- 90 files · ~47,213 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 957 nodes · 2086 edges · 49 communities (38 shown, 11 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 440 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c8268068`
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
- Lineage
- Benchmark Scripts
- Master Circular Verification
- test_integration_e2e.py
- As-of Evaluation
- Embedder
- Scraper Tests
- Master Metadata
- Export Integration
- answer_with_abstention
- test_gate.py
- Chunk
- Corpus Validation
- Reranking
- ZeroGPU Tests
- Dataset Push
- Answer Generation
- Ops Server
- SubjectSimJudge
- .encode
- build_lineage
- .load
- Build Scripts
- Canary Monitoring
- Index Refresh
- As-of UI Tests
- eval.py
- Space Deployment
- Discovery Scripts
- Index Upload
- trace_failure.py
- embeddings.py
- UI Components
- Ops Scripts
- Notification Scripts
- Test Guards
- .family
- app.py
- Path

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 77 edges
2. `RAGPipeline` - 36 edges
3. `HashEmbedder` - 31 edges
4. `Lineage` - 31 edges
5. `hierarchical_chunk()` - 31 edges
6. `build_lineage()` - 28 edges
7. `ExtractiveStubGenerator` - 24 edges
8. `CircularMeta` - 23 edges
9. `SubjectSimJudge` - 22 edges
10. `answer_with_abstention()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_governing_on_cycle_safe()` --calls--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_governing_on_parallel_branches_max_date_wins()` --calls--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `get_pipeline()` --calls--> `build_spaces_pipeline()`  [INFERRED]
  app.py → src/sebi_rag/api_spaces.py
- `get_pipeline()` --calls--> `ExtractiveStubGenerator`  [INFERRED]
  app.py → src/sebi_rag/generate.py

## Import Cycles
- None detected.

## Communities (49 total, 11 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.15
Nodes (11): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), True iff the reply names a valid excerpt number. 'none' or anything     unparsea, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the     gat, Deterministic groundedness judge on MLX (greedy decode, temp 0).      Pass share (+3 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.08
Nodes (48): Any, main(), main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, dataset_quality(), load_index_chunks(), main(), Path (+40 more)

### Community 2 - "Data Processing"
Cohesion: 0.05
Nodes (57): Pattern, Re-derive circular number + dates from each record's stored text and rewrite the, _existing_numbers(), extract_text(), _header(), ingest(), injection_scan(), _iso_date() (+49 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan, _master(), test_annotate_idempotent() (+7 more)

### Community 4 - "Dataset Export"
Cohesion: 0.08
Nodes (50): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+42 more)

### Community 5 - "Utility Scripts"
Cohesion: 0.08
Nodes (28): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+20 more)

### Community 6 - "Spaces CPU Pipeline"
Cohesion: 0.08
Nodes (31): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, Fallback generator: small instruct model via transformers on CPU., _get() (+23 more)

### Community 7 - "Dataset Card Tests"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 8 - "Metadata Engine"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 9 - "Export Tests"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 10 - "Lineage"
Cohesion: 0.23
Nodes (14): AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, run_pipeline_cases(), run_selector_cases(), summarize(), Lineage (+6 more)

### Community 11 - "Benchmark Scripts"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 12 - "Master Circular Verification"
Cohesion: 0.15
Nodes (22): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:, diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13).  Pure functions only: l (+14 more)

### Community 13 - "test_integration_e2e.py"
Cohesion: 0.14
Nodes (19): load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., hierarchical_chunk(), _paragraphs(), Segmentation: hierarchical chunking + metadata + stable citation IDs.  Minimal,, Split into units each <= max_chars.      PDF-extracted text often lacks blank-li, Document -> section -> paragraph chunks with stable IDs.      A "section" is det (+11 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.09
Nodes (30): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any (+22 more)

### Community 15 - "Embedder"
Cohesion: 0.15
Nodes (13): Embedder, DenseIndex, _doc_checksum(), ndarray, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding, Deterministic per-document checksum over its (enriched) chunk texts —     captur, FAISS IndexFlatIP over L2-normalized vectors (cosine)., _chunk() (+5 more)

### Community 16 - "Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "Master Metadata"
Cohesion: 0.18
Nodes (10): FastAPI, create_app(), FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, /ready should trigger pipeline build and return ready=true., test_auth_required_when_key_set(), test_citation_meta_reports_superseded(), test_query_exceeds_time_budget_returns_504(), test_rate_limit() (+2 more)

### Community 18 - "Export Integration"
Cohesion: 0.15
Nodes (16): Path, file_sha256(), Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 19 - "answer_with_abstention"
Cohesion: 0.29
Nodes (12): answer_with_abstention(), faithfulness(), Check that every circular id the answer cites (in square brackets) was     actua, _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful() (+4 more)

### Community 20 - "test_gate.py"
Cohesion: 0.28
Nodes (10): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge() (+2 more)

### Community 21 - "Chunk"
Cohesion: 0.20
Nodes (4): _grounded_prompt(), F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, Chunk, test_chunks_config_refuses_header_and_maps_fields()

### Community 22 - "Corpus Validation"
Cohesion: 0.29
Nodes (13): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations() (+5 more)

### Community 23 - "Reranking"
Cohesion: 0.12
Nodes (15): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic, BM25 lexical index (bm25s)., Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), SparseIndex, Query-side lexical expansion (intervention #2, glossary variant).  Lay->statutor (+7 more)

### Community 24 - "ZeroGPU Tests"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 25 - "Dataset Push"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 26 - "Answer Generation"
Cohesion: 0.14
Nodes (32): smoke_pipeline(), HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., LexicalReranker, Deterministic query-coverage reranker (test/fallback).      Score = fraction of, CircularMeta (+24 more)

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "SubjectSimJudge"
Cohesion: 0.31
Nodes (4): ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge

### Community 29 - ".encode"
Cohesion: 0.39
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are e, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 30 - "build_lineage"
Cohesion: 0.07
Nodes (36): annotate_corpus(), build_lineage(), _currency(), detect_relations(), detect_relations_ex(), mc_topic(), Path, Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None.      Us (+28 more)

### Community 31 - ".load"
Cohesion: 0.08
Nodes (44): BaseModel, first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom (+36 more)

### Community 32 - "Build Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 33 - "Canary Monitoring"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 34 - "Index Refresh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 36 - "eval.py"
Cohesion: 0.47
Nodes (5): mrr(), ndcg_at_k(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), test_retrieval_metrics()

### Community 41 - "embeddings.py"
Cohesion: 0.09
Nodes (27): Protocol, Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, contexts_for() (+19 more)

### Community 47 - "app.py"
Cohesion: 0.31
Nodes (7): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces()

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Chunk` to `Core RAG Pipeline`, `Benchmark Infrastructure`, `Data Processing`, `Spaces CPU Pipeline`, `embeddings.py`, `Lineage`, `Benchmark Scripts`, `test_integration_e2e.py`, `Embedder`, `answer_with_abstention`, `test_gate.py`, `Reranking`, `Answer Generation`, `SubjectSimJudge`, `.load`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `Lineage` to `Benchmark Infrastructure`, `embeddings.py`, `Embedder`, `Master Metadata`, `Chunk`, `Answer Generation`, `.load`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `normalize_circular_number()` connect `Data Processing` to `Benchmark Infrastructure`, `Index & Evaluation`, `Dataset Export`, `As-of Evaluation`, `Corpus Validation`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `Answer`) actually correct?**
  _`Chunk` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_offline_pipeline()`) actually correct?**
  _`HashEmbedder` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Lineage` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`Lineage` has 15 INFERRED edges - model-reasoned connections that need verification._