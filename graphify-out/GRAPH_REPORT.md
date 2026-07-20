# Graph Report - SEBI circular RAG  (2026-07-20)

## Corpus Check
- 104 files · ~51,760 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1061 nodes · 2228 edges · 52 communities (40 shown, 12 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 458 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d194d375`
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
- test_gate.py
- build_lineage
- main
- Build Scripts
- Canary Monitoring
- Index Refresh
- As-of UI Tests
- .grounded
- Space Deployment
- Discovery Scripts
- Index Upload
- HybridGenerator
- test_integration_e2e.py
- UI Components
- Ops Scripts
- Notification Scripts
- Test Guards
- bench_rerankers.py
- bench_retrieval.py
- app.py
- .encode
- _s_header_token
- _s_dept_only

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 71 edges
2. `RAGPipeline` - 34 edges
3. `hierarchical_chunk()` - 33 edges
4. `HashEmbedder` - 32 edges
5. `Lineage` - 31 edges
6. `build_lineage()` - 27 edges
7. `ExtractiveStubGenerator` - 22 edges
8. `SubjectSimJudge` - 22 edges
9. `CircularMeta` - 22 edges
10. `answer_with_abstention()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `test_governing_on_cycle_safe()` --calls--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_governing_on_parallel_branches_max_date_wins()` --calls--> `Lineage`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_build_lineage_edges_tiered()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_build_lineage_inferred_master_topic_edge()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py
- `test_master_circular_reissue_supersession()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_lineage.py → src/sebi_rag/lineage.py

## Import Cycles
- None detected.

## Communities (52 total, 12 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.15
Nodes (21): _keep(), load_circulars_from_hf(), load_corpus_records_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path).  Loads the pu, One HF dataset config as plain dicts (network; cached by `datasets`)., Full-circular records (dicts) for build_lineage() — always the     "corpus" conf (+13 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.08
Nodes (47): Any, main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation.  Outputs: (+39 more)

### Community 2 - "Data Processing"
Cohesion: 0.05
Nodes (57): Pattern, Re-derive circular number + dates from each record's stored text and rewrite the, _existing_numbers(), extract_text(), _header(), ingest(), injection_scan(), _iso_date() (+49 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.17
Nodes (15): AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, run_pipeline_cases(), run_selector_cases(), summarize(), Lineage (+7 more)

### Community 4 - "Dataset Export"
Cohesion: 0.08
Nodes (50): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+42 more)

### Community 5 - "Utility Scripts"
Cohesion: 0.05
Nodes (50): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+42 more)

### Community 6 - "Spaces CPU Pipeline"
Cohesion: 0.16
Nodes (9): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, demote_superseded(), P2 — cross-document supersession resolution.  Classifies each circular's referen, Down-weight reranked (chunk, score) pairs from superseded circulars and     re-s, Map any cited circular that is superseded -> the circular(s) superseding it., superseded_citations() (+1 more)

### Community 7 - "Dataset Card Tests"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 8 - "Metadata Engine"
Cohesion: 0.12
Nodes (8): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., TestClassifyCircularType, TestDeriveValidity

### Community 9 - "Export Tests"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 10 - ".grounded"
Cohesion: 0.15
Nodes (11): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), True iff the reply names a valid excerpt number. 'none' or anything     unparsea, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the     gat, Deterministic groundedness judge on MLX (greedy decode, temp 0).      Pass share (+3 more)

### Community 11 - "Benchmark Scripts"
Cohesion: 0.12
Nodes (19): Protocol, Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Embedder, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T (+11 more)

### Community 12 - "Qwen3MLXReranker"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 13 - "test_integration_e2e.py"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.13
Nodes (24): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any (+16 more)

### Community 15 - "Embedder"
Cohesion: 0.06
Nodes (36): Chunk, Embedder, ndarray, Path, expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic, DenseIndex (+28 more)

### Community 16 - "Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "Master Metadata"
Cohesion: 0.09
Nodes (27): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).  Resumable, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10).  Pulls the i, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+19 more)

### Community 18 - "Export Integration"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 19 - "answer_with_abstention"
Cohesion: 0.29
Nodes (12): answer_with_abstention(), faithfulness(), Check that every circular id the answer cites (in square brackets) was     actua, _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful() (+4 more)

### Community 20 - "test_gate.py"
Cohesion: 0.07
Nodes (23): csr_matrix, Build the SPLADE learned-sparse doc matrix once and persist it (iv11).  Standalo, Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.  splad, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights., splade_pool(), SpladeEncoder, SPLADE learned-sparse retrieval leg (iv11).  Non-destructive, opt-in third RRF l (+15 more)

### Community 21 - "Chunk"
Cohesion: 0.14
Nodes (16): ExternalSpaceGenerator, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).      Nev, SpacesSettings, _Boom, _Canned, _hybrid(), HF Spaces path: corpus_spaces loader mapping + HybridGenerator fallback.  Fully (+8 more)

### Community 22 - "Corpus Validation"
Cohesion: 0.29
Nodes (13): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations() (+5 more)

### Community 23 - "Reranking"
Cohesion: 0.14
Nodes (6): _grounded_prompt(), Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, Chunk, test_chunks_config_refuses_header_and_maps_fields()

### Community 24 - "ZeroGPU Tests"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 25 - "Dataset Push"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 26 - "Answer Generation"
Cohesion: 0.05
Nodes (75): FastAPI, create_app(), load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, mrr() (+67 more)

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "SubjectSimJudge"
Cohesion: 0.16
Nodes (22): BaseModel, build_default_pipeline(), _citation_meta(), CitationMeta, QueryRequest, QueryResponse, FastAPI service over the SEBI Circular RAG pipeline.  Run (real stack; loads the, build_spaces_pipeline() (+14 more)

### Community 29 - "test_gate.py"
Cohesion: 0.28
Nodes (10): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge() (+2 more)

### Community 30 - "build_lineage"
Cohesion: 0.06
Nodes (45): annotate_corpus(), detect_relations(), detect_relations_ex(), Update each corpus record's supersession_status + superseded_by + supersedes, Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference., _window(), annotate_master_fields() (+37 more)

### Community 31 - "main"
Cohesion: 0.24
Nodes (9): auroc(), best_threshold(), evaluate(), main(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t, load_records() (+1 more)

### Community 32 - "Build Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 33 - "Canary Monitoring"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 34 - "Index Refresh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 36 - ".grounded"
Cohesion: 0.17
Nodes (11): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage.  Offline only —, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_none_and_empty_hyde_are_identical_to_baseline() (+3 more)

### Community 40 - "HybridGenerator"
Cohesion: 0.24
Nodes (5): HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Fallback generator: small instruct model via transformers on CPU.

### Community 41 - "test_integration_e2e.py"
Cohesion: 0.40
Nodes (3): _ollama_up(), pipeline(), Step 12 — end-to-end RAG integration test with the REAL stack.  bge-m3 (MPS) + b

### Community 47 - "bench_retrieval.py"
Cohesion: 0.60
Nodes (4): RAGPipeline, main(), Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, smoke_pipeline()

### Community 48 - "app.py"
Cohesion: 0.31
Nodes (7): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces()

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Reranking` to `Core RAG Pipeline`, `Benchmark Infrastructure`, `Data Processing`, `.grounded`, `Spaces CPU Pipeline`, `HybridGenerator`, `.grounded`, `Benchmark Scripts`, `Qwen3MLXReranker`, `Embedder`, `Master Metadata`, `answer_with_abstention`, `Chunk`, `Answer Generation`, `SubjectSimJudge`, `test_gate.py`?**
  _High betweenness centrality (0.133) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `SubjectSimJudge` to `Benchmark Infrastructure`, `Index & Evaluation`, `Spaces CPU Pipeline`, `Benchmark Scripts`, `Reranking`, `Answer Generation`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `normalize_circular_number()` connect `Data Processing` to `Benchmark Infrastructure`, `Dataset Export`, `As-of Evaluation`, `Corpus Validation`, `build_lineage`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `Answer`) actually correct?**
  _`Chunk` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `RAGPipeline` (e.g. with `CitationMeta` and `QueryRequest`) actually correct?**
  _`RAGPipeline` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `hierarchical_chunk()` (e.g. with `_slow_pipeline()` and `_tiny_pipeline()`) actually correct?**
  _`hierarchical_chunk()` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `HashEmbedder` (e.g. with `_offline_pipeline()` and `_slow_pipeline()`) actually correct?**
  _`HashEmbedder` has 28 INFERRED edges - model-reasoned connections that need verification._