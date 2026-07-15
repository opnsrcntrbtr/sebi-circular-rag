# Graph Report - SEBI circular RAG  (2026-07-15)

## Corpus Check
- 84 files · ~44,148 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 913 nodes · 1864 edges · 45 communities (35 shown, 10 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 355 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `83a6ebe8`
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
- API Server
- Benchmark Scripts
- Master Circular Verification
- Lineage Tracking
- As-of Evaluation
- HF Spaces
- Scraper Tests
- Master Metadata
- Export Integration
- Generation & Judging
- Gate Tests
- test_gate.py
- Corpus Validation
- Reranking
- ZeroGPU Tests
- Dataset Push
- Answer Generation
- Ops Server
- test_incremental_index.py
- .encode
- annotate_corpus
- .load
- Build Scripts
- Canary Monitoring
- Index Refresh
- As-of UI Tests
- Lineage
- Space Deployment
- Discovery Scripts
- Index Upload
- Lineage
- UI Components
- Ops Scripts
- Notification Scripts
- Test Guards

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 73 edges
2. `hierarchical_chunk()` - 26 edges
3. `HashEmbedder` - 25 edges
4. `Lineage` - 23 edges
5. `build_lineage()` - 23 edges
6. `ExtractiveStubGenerator` - 21 edges
7. `CircularMeta` - 20 edges
8. `answer_with_abstention()` - 19 edges
9. `RAGPipeline` - 18 edges
10. `SpacesSettings` - 17 edges

## Surprising Connections (you probably didn't know these)
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py
- `test_chunks_config_refuses_header_and_maps_fields()` --indirect_call--> `Chunk`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/segment.py
- `run_query_spaces()` --calls--> `_citation_meta()`  [INFERRED]
  app.py → src/sebi_rag/api.py
- `_HallucinatingGenerator` --uses--> `RAGPipeline`  [INFERRED]
  tests/test_faithfulness.py → src/sebi_rag/pipeline.py

## Import Cycles
- None detected.

## Communities (45 total, 10 thin omitted)

### Community 0 - "Core RAG Pipeline"
Cohesion: 0.07
Nodes (54): Chunk, Embedder, Reranker, smoke_pipeline(), load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., HashEmbedder (+46 more)

### Community 1 - "Benchmark Infrastructure"
Cohesion: 0.05
Nodes (65): Answer, Any, main(), main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, evaluate(), Calibrate top_k and the abstention threshold against the citation-precision sign, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per (+57 more)

### Community 2 - "Data Processing"
Cohesion: 0.05
Nodes (57): Pattern, Re-derive circular number + dates from each record's stored text and rewrite the, _existing_numbers(), extract_text(), _header(), ingest(), injection_scan(), _iso_date() (+49 more)

### Community 3 - "Index & Evaluation"
Cohesion: 0.09
Nodes (34): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces(), Path (+26 more)

### Community 4 - "Dataset Export"
Cohesion: 0.08
Nodes (50): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+42 more)

### Community 5 - "Utility Scripts"
Cohesion: 0.08
Nodes (28): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+20 more)

### Community 6 - "Spaces CPU Pipeline"
Cohesion: 0.10
Nodes (23): Generator, ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, Fallback generator: small instruct model via transformers on CPU. (+15 more)

### Community 7 - "Dataset Card Tests"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 8 - "Metadata Engine"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 9 - "Export Tests"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 10 - "API Server"
Cohesion: 0.16
Nodes (10): Protocol, _grounded_prompt(), Judge, MLXGenerator, OllamaGenerator, F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, Apple-Silicon-native generation via MLX-LM (D6 preferred runtime).      Loads a, Grounded generation via local Ollama (D6 canonical runtime option).      Determi (+2 more)

### Community 11 - "Benchmark Scripts"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 12 - "Master Circular Verification"
Cohesion: 0.15
Nodes (22): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:, diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13).  Pure functions only: l (+14 more)

### Community 13 - "Lineage Tracking"
Cohesion: 0.19
Nodes (15): build_lineage(), _currency(), Map any cited circular that is superseded -> the circular(s) superseding it., superseded_citations(), _lin_chain(), P2 lineage / supersession resolution tests., test_build_lineage_edges_tiered(), test_build_lineage_inferred_master_topic_edge() (+7 more)

### Community 14 - "As-of Evaluation"
Cohesion: 0.12
Nodes (12): Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, faithfulness(), Check that every circular id the answer cites (in square brackets) was     actua, CrossEncoderReranker, Stage-2 reranking (mandatory, D4). Cross-encoder in production; a deterministic, Production reranker: bge-reranker-v2-m3 via sentence-transformers     CrossEncod, Segmentation: hierarchical chunking + metadata + stable citation IDs.  Minimal,, Faithfulness: catch answers that cite circulars not in the retrieved context. (+4 more)

### Community 15 - "HF Spaces"
Cohesion: 0.14
Nodes (14): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, detect_relations(), detect_relations_ex(), mc_topic(), P2 — cross-document supersession resolution.  Classifies each circular's referen, Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None.      Us, Like detect_relations, but returns dict records with evidence spans., Return (relation, referenced_circular) for each distinct reference. (+6 more)

### Community 16 - "Scraper Tests"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 17 - "Master Metadata"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan, _master(), test_annotate_idempotent() (+7 more)

### Community 18 - "Export Integration"
Cohesion: 0.15
Nodes (16): file_sha256(), Path, Task 5: Integration tests — idempotency and live export verification., All configs in manifest must share the same version tag (v2026.07)., Smoke test: live export on actual corpus produces valid datasets., Compute SHA256 of a file., Verify that dataset cards are generated with export., Running export_all() twice must produce identical output files. (+8 more)

### Community 19 - "Generation & Judging"
Cohesion: 0.44
Nodes (9): answer_with_abstention(), _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful(), test_no_context_reason_when_top_k_zero(), test_score_floor_reason() (+1 more)

### Community 20 - "Gate Tests"
Cohesion: 0.15
Nodes (13): Answer, _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), Generation with a hard abstention gate (D5).  If the top reranked score is below, True iff the reply names a valid excerpt number. 'none' or anything     unparsea (+5 more)

### Community 21 - "test_gate.py"
Cohesion: 0.28
Nodes (10): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge() (+2 more)

### Community 22 - "Corpus Validation"
Cohesion: 0.29
Nodes (13): main(), _plausible(), Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations() (+5 more)

### Community 23 - "Reranking"
Cohesion: 0.06
Nodes (31): Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Build the dense+sparse index once and persist it (run after corpus changes)., ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, Emit one JSON line of retrieval/citation/abstention metrics over golden_v5 (env, Embedder, ndarray, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, _tokens() (+23 more)

### Community 24 - "ZeroGPU Tests"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 25 - "Dataset Push"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 26 - "Answer Generation"
Cohesion: 0.10
Nodes (24): BaseModel, FastAPI, Lineage, Settings, build_default_pipeline(), _citation_meta(), CitationMeta, create_app() (+16 more)

### Community 27 - "Ops Server"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 28 - "test_incremental_index.py"
Cohesion: 0.21
Nodes (11): auroc(), best_threshold(), evaluate(), main(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t, contexts_for() (+3 more)

### Community 29 - ".encode"
Cohesion: 0.31
Nodes (4): ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge

### Community 30 - "annotate_corpus"
Cohesion: 0.22
Nodes (7): annotate_corpus(), load_records(), Path, Update each corpus record's supersession_status + superseded_by + supersedes, test_annotate_corpus_adds_master_fields_and_consolidates_edges(), test_annotate_corpus_writes_new_metadata_fields(), test_real_corpus_oiae_supersedes_listed_circulars()

### Community 32 - "Build Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 33 - "Canary Monitoring"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, canary.sh script, TOKENIZERS_PARALLELISM

### Community 34 - "Index Refresh"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 36 - "Lineage"
Cohesion: 0.24
Nodes (7): Lineage, Connected component over supersedes/superseded_by (both tiers)., The circular in this family that governs on date as_of (ISO), or         None wh, test_governing_on_cycle_safe(), test_governing_on_parallel_branches_max_date_wins(), test_lineage_load_old_file_defaults_empty_edges(), test_lineage_save_load_roundtrips_edges()

## Knowledge Gaps
- **22 isolated node(s):** `run.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `API Server` to `Core RAG Pipeline`, `Benchmark Infrastructure`, `Data Processing`, `Index & Evaluation`, `Spaces CPU Pipeline`, `Benchmark Scripts`, `As-of Evaluation`, `Generation & Judging`, `Gate Tests`, `test_gate.py`, `Reranking`, `test_incremental_index.py`, `.encode`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Why does `normalize_circular_number()` connect `Data Processing` to `Benchmark Infrastructure`, `Dataset Export`, `Corpus Validation`, `Master Metadata`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `Benchmark Infrastructure` to `Core RAG Pipeline`, `Index & Evaluation`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `Answer`) actually correct?**
  _`Chunk` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `hierarchical_chunk()` (e.g. with `smoke_pipeline()` and `test_run_pipeline_cases_pass_and_avoid()`) actually correct?**
  _`hierarchical_chunk()` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `test_advisory_draft_on_gate_failure_only_when_requested()`) actually correct?**
  _`HashEmbedder` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `Lineage` (e.g. with `AsofCaseResult` and `_lin_chain()`) actually correct?**
  _`Lineage` has 11 INFERRED edges - model-reasoned connections that need verification._