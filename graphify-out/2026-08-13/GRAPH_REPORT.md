# Graph Report - SEBI circular RAG  (2026-08-13)

## Corpus Check
- 190 files · ~178,360 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2352 nodes · 4758 edges · 164 communities (134 shown, 30 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 1086 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `43000c9f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Dataset Export and Packaging
- Telemetry and Performance Monitoring
- Human Annotation Workflow
- End-to-End Integration Testing
- Regulation Lineage and Identity
- LLM Generation Providers
- Groundedness Judging Protocol
- Hugging Face Data Loading
- Regulation Citation Extraction
- Regulation Metadata Annotation
- Dataset Card Validation
- Golden Set Versioning
- Answer Validation and Groundedness
- Circular Metadata and Validity
- Contextual Header Generation
- Circular Relation Detection
- LLM Adjudication Prompts
- SPLADE Sparse Indexing
- Dataset Export Testing
- Temporal Evaluation Runner
- Golden Set Schema Validation
- Annotation Promotion Logic
- API Service and Integration
- Golden Set Data Backfilling
- Gemini Model Adjudication
- Corpus Supersession Annotation
- Master Circular Verification
- Statistical Uncertainty Analysis
- Regulation Web Scraping
- Annotator Agreement Metrics
- PDF Ingestion and Normalization
- Retrieval Error Classification
- Local Model Adjudication
- TREC Runfile Conversion
- Circular Web Scraping
- Missing PDF Recovery
- PDF Metadata Parsing
- RAG Pipeline Construction
- Web Scraper Testing
- Context Precision Metrics
- Label Provenance and Tiers
- Statistical and Hardware Helpers
- Reranker Performance Evaluation
- Export Integration Testing
- Local Model Inference
- Citation and Generation Benchmarking
- HyDE Query Expansion
- Regulation Scraper Testing
- Document Segmentation and Chunking
- Metric Reporting and Testing
- Metric Execution Registry
- Query Expansion and RRF
- Hugging Face Spaces Deployment
- Golden Set Evaluation Gates
- Hardware Device Selection
- Reference Number Normalization
- Golden Set Seeding
- MLX Native Reranking
- Exact Confidence Intervals
- Master Circular Metadata
- Dataset Hub Upload
- User Interface Components
- Regulation Edge Auditing
- UI Logic Testing
- Benchmark Schema Validation
- Corpus Text Repair
- Evaluation Harness Testing
- Comparative Run Analysis
- Token Encoding Utilities
- Operations Server Management
- Regulation Edge Precision Audit
- Draft Adjudication Workflow
- Incremental Index Building
- Circular Alias Validation
- Bootstrap Confidence Intervals
- Retrieval Failure Analysis
- Governing Span Resolution
- .test_mean_reproduces_the_archived_aggregate
- Agreement Metric Testing
- Adjudication Error Handling
- Supersession Precision Metrics
- Regulation Edge Integration Testing
- SEBI RAG Project
- Run Rescoring and Backfilling
- Auto-research Driver Scripts
- Prompt Injection Security
- Regulatory Basis Indexing
- Auto-research Evaluation Support
- sweep_rrf_k.py
- Document ID Remapping
- New Circular Discovery
- Retrieval Metric Implementation
- .family
- Provision-Level Agreement
- SEBI Circular Identifiers
- Configuration and Settings Management
- Execution Shell Scripts
- Canary Deployment Scripts
- PDF Recovery Testing
- Path
- Data Refresh Scripts
- write_dataset_cards
- measure_supersession_precision
- Annotation Provenance Auditing
- Temporal Accuracy Metrics
- Temporal UI Testing
- detect_relations_ex
- test_gate.py
- Regulation Edge Construction
- Retrieval Artifact Testing
- Auto-research Environment Script
- run_all_metrics
- Retrieval Recall Metrics
- RAG Demo Application
- Human Evaluation Packets
- Lexical Reranking and Pooling
- Hugging Face Deployment
- Discovery Execution Script
- Index Artifact Upload
- Measurement Execution Script
- Operations Execution Script
- Notification Script
- Phoenix Monitoring Script
- Test Environment Configuration
- Mutual Fund Master Circulars
- Quote to Chunk Resolution
- SEBI Master Circulars
- Slash Command Optimization
- Circular ID Tracking
- Label Escalation Management
- RAG Benchmark Export
- Unresolved Regulation Tracking
- HF Spaces Dependencies
- Depository Master Appendix
- SEBI Regulations Directory
- test_pipeline.py
- test_eval_generator.py
- .build
- measure.py
- test_incremental_index.py
- expand.py
- test_build_index_out_dir.py
- measure_mrr
- .encode
- test_canary_generator.py
- TestPerQueryRecall
- measure_temporal_accuracy
- detect_relations_ex
- _unique
- stats.py
- _resolve_governing_spans
- write_run_doc
- SparseIndex
- test_trec_parity.py
- test_eval_asof.py
- _doc_checksum
- ndarray
- Path
- main
- TestPerQueryRecall
- discover_new.py
- load_golden_asof
- Chunk

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 54 edges
2. `RAGPipeline` - 50 edges
3. `hierarchical_chunk()` - 44 edges
4. `ExtractiveStubGenerator` - 42 edges
5. `HashEmbedder` - 40 edges
6. `CircularMeta` - 40 edges
7. `LexicalReranker` - 29 edges
8. `build_lineage()` - 28 edges
9. `Settings` - 26 edges
10. `MeasureResult` - 26 edges

## Surprising Connections (you probably didn't know these)
- `test_run_metadata_has_reproducibility_fields()` --calls--> `run_metadata()`  [INFERRED]
  tests/test_benchmark.py → src/sebi_rag/benchmark.py
- `test_chunk_meta_carries_new_fields()` --calls--> `load_circulars()`  [INFERRED]
  tests/test_metadata.py → src/sebi_rag/corpus.py
- `test_numbers_normalize_distinctly()` --calls--> `normalize_circular_number()`  [INFERRED]
  tests/test_repair_corpus_text.py → src/sebi_rag/ingest_pdf.py
- `test_to_record_carries_injection_flags()` --calls--> `to_record()`  [INFERRED]
  tests/test_injection.py → src/sebi_rag/ingest_pdf.py
- `test_corpus_records_feed_build_lineage()` --calls--> `build_lineage()`  [INFERRED]
  tests/test_spaces.py → src/sebi_rag/lineage.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **SEBI Regulatory Framework** — tests_fixtures_master_appendix_pre2015_sebi, tests_fixtures_master_appendix_pre2015_circulars, tests_fixtures_master_appendix_pre2015_communications [INFERRED 0.90]

## Communities (164 total, 30 thin omitted)

### Community 0 - "Dataset Export and Packaging"
Cohesion: 0.06
Nodes (66): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+58 more)

### Community 1 - "Telemetry and Performance Monitoring"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 2 - "Human Annotation Workflow"
Cohesion: 0.07
Nodes (52): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV ingest, Writes the blind human packet for `human_ids` (a subset of `ids`, the     full e (+44 more)

### Community 3 - "End-to-End Integration Testing"
Cohesion: 0.11
Nodes (22): hierarchical_chunk(), _paragraphs(), Segmentation: hierarchical chunking + metadata + stable citation IDs.  Minimal,, Split into units each <= max_chars.      PDF-extracted text often lacks blank-li, Document -> section -> paragraph chunks with stable IDs.      A "section" is det, test_numeric_miner_requires_numeric_pattern(), test_paraphrase_skips_preamble_and_short_chunks(), _ollama_up() (+14 more)

### Community 4 - "Regulation Lineage and Identity"
Cohesion: 0.08
Nodes (36): _record(), _jaccard(), load_regulations(), name_tokens(), Path, Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6).  Regulations, Resolve a cited regulation name+year to a canonical reg_id.      Returns (reg_id, Load data/corpus/regulations.jsonl into a list of regulation records.      Thin (+28 more)

### Community 5 - "LLM Generation Providers"
Cohesion: 0.11
Nodes (22): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).      Nev (+14 more)

### Community 6 - "Groundedness Judging Protocol"
Cohesion: 0.23
Nodes (16): main(), discover(), extract_pdf_urls(), fetch(), _listing_url(), looks_like_pdf(), main(), _page() (+8 more)

### Community 7 - "Hugging Face Data Loading"
Cohesion: 0.15
Nodes (20): Build the dense+sparse index once and persist it (run after corpus changes)., _compute_kwargs(), Resolve device/fp16/batch for the torch embedder + reranker., build_spaces_pipeline(), _cpu_env(), Pipeline builder for the Hugging Face Spaces demo (CPU-only, Linux).  Parallel t, _keep(), load_circulars_from_hf() (+12 more)

### Community 8 - "Regulation Citation Extraction"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).  Deliber, All regulation citations in a circular, one per occurrence (not deduped).      S, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years.      "Regulations (+24 more)

### Community 9 - "Regulation Metadata Annotation"
Cohesion: 0.14
Nodes (30): annotate_regulation_fields(), build_regulation_edges(), build_regulatory_index(), One `cites` edge per (circular, regulation) pair.      The merged edge carries t, Set regulations / primary_regulation / regulatory_basis_status in place.      Re, Per-circular regulatory-basis lookup for the query/citation layer.      Read-onl, _circ(), _icirc() (+22 more)

### Community 10 - "Dataset Card Validation"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 11 - "Golden Set Versioning"
Cohesion: 0.16
Nodes (24): main(), Emit TREC qrels for an eval set, keyed by its golden_sha256.      .venv/bin/pyth, beir_corpus_rows(), beir_query_rows(), build_golden_v6(), dir_fingerprint(), enrich_golden_item(), export_beir() (+16 more)

### Community 12 - "Answer Validation and Groundedness"
Cohesion: 0.18
Nodes (19): _assert_fixed_tail(), convert_run_dir(), main(), Path, Back-convert archived runfiles into standards-compliant TREC artifacts.  The arc, Trailing field of the first line; also the whitespace precondition check., read_trec_run assumes qid and tag carry no whitespace. Verify per line., Write run.chunk.trec, run.doc.trec and docids.tsv for one archived run. (+11 more)

### Community 13 - "Circular Metadata and Validity"
Cohesion: 0.12
Nodes (9): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., test_chunk_meta_carries_new_fields(), TestClassifyCircularType (+1 more)

### Community 14 - "Contextual Header Generation"
Cohesion: 0.10
Nodes (24): apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope(), load_headers(), Path, Contextual chunk headers (iv9): one lay+statutory sentence per chunk.  Index-sid, Spec scope: depth>=3 numbered sub-clauses plus annex-family headings. (+16 more)

### Community 15 - "Circular Relation Detection"
Cohesion: 0.07
Nodes (38): annotate_corpus(), build_lineage(), detect_relations(), detect_relations_ex(), Lineage, load_records(), Path, Map any cited circular that is superseded -> the circular(s) superseding it. (+30 more)

### Community 16 - "LLM Adjudication Prompts"
Cohesion: 0.12
Nodes (26): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape).     Non-abst, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing, a, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as     "confirms abs, A non-abstain row whose pool happens to have zero candidates can't     offer any, Decision #3: a valid letter alongside an unrecognized one invalidates     the WH, letters=[] is how adjudicate signals an abstain/zero-candidate row;     parse_re (+18 more)

### Community 17 - "SPLADE Sparse Indexing"
Cohesion: 0.18
Nodes (9): RuntimeError, csr_matrix, Path, SPLADE learned-sparse retrieval leg (iv11).  Non-destructive, opt-in third RRF l, SpladeIndex, _fake_encode(), Return an encode fn mapping known texts to known dense weight rows., test_save_load_roundtrip_and_guard() (+1 more)

### Community 18 - "Dataset Export Testing"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 19 - "Temporal Evaluation Runner"
Cohesion: 0.15
Nodes (13): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7)., Yield (circular, Citation) for every citation occurrence in the corpus., Stub records for cited regulations absent from the Updated List.      Returns NE, synthesise_repealed_stubs(), derive_regulatory_basis(), Regulatory-basis status of one circular from its resolved regulations.      `unk, test_stub_is_created_for_a_cited_regulation_with_a_known_successor() (+5 more)

### Community 20 - "Golden Set Schema Validation"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden.      `chunks` is optio, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 21 - "Annotation Promotion Logic"
Cohesion: 0.12
Nodes (27): decide(), Spec sec7 promotion rules for one row.      `votes_by_annotator` is this row's v, Abstain rows have no explicit claude vote at all (Task 8 never judged     them), Both externals independently think something DOES govern (disputing     the auth, The LLM leg is whichever single non-claude/non-human annotator voted -     "qwen, Amendment 2026-07-26 (user-approved): the promotion unit is the     PROVISION, n, External marked claude's chunk governing plus extras: claude's label     is conf, The abstain protocol can never emit non-empty governing (no letters     are offe (+19 more)

### Community 22 - "API Service and Integration"
Cohesion: 0.13
Nodes (8): FastAPI service tests (offline pipelines): endpoints, auth, rate limit, metadata, /ready should trigger pipeline build and return ready=true., test_auth_required_when_key_set(), test_citation_meta_reports_superseded(), test_query_exceeds_time_budget_returns_504(), test_rate_limit(), test_ready_triggers_pipeline(), _tiny_pipeline()

### Community 23 - "Golden Set Data Backfilling"
Cohesion: 0.09
Nodes (38): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate (2026-07-25 (+30 more)

### Community 24 - "Gemini Model Adjudication"
Cohesion: 0.10
Nodes (26): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec 2026-0 (+18 more)

### Community 25 - "Corpus Supersession Annotation"
Cohesion: 0.12
Nodes (32): citation_scorer_for(), The single enable/disable AND backend decision for B'.      Returns None when di, Context ids the answer rests on. Scores each context's answer-relevance     via, select_citations(), _chunk(), _FakeReranker, Tests for B' selective citations: select_citations() and its integration., When citation_scorer_enabled=True, Settings loads a non-None scorer. (+24 more)

### Community 26 - "Master Circular Verification"
Cohesion: 0.33
Nodes (8): diff_manifest(), Assign exactly one status to every listed row + extra_in_corpus rows., _rec(), _row(), test_coverage_pct_excludes_unfetchable(), test_diff_statuses(), test_summarize_and_markdown(), test_write_reports()

### Community 27 - "Statistical Uncertainty Analysis"
Cohesion: 0.10
Nodes (23): entailment_index(), NLIAttributionScorer, Chunk, NLI attribution scoring for B' citation selection.  B' asks "does this context s, Index of the entailment class in a model's label map.      Read from the checkpo, Scores each context by P(entailment) of the answer given that context.      Impl, Wrap an already-constructed cross-encoder (also the test seam)., _softmax() (+15 more)

### Community 28 - "Regulation Web Scraping"
Cohesion: 0.16
Nodes (14): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.      A, validate_golden(), Answerable-but-unjudged rows are excluded from metrics, never scored 0.  golden_, A real, fully-populated golden row, so the fixture cannot drift out of     sync, _template() (+6 more)

### Community 29 - "Annotator Agreement Metrics"
Cohesion: 0.14
Nodes (22): _claude_accuracy_ci(), cohen_kappa(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation slic, Categorical Cohen's kappa over paired labels (row-aligned). Each raw     element (+14 more)

### Community 30 - "PDF Ingestion and Normalization"
Cohesion: 0.14
Nodes (22): Re-derive circular number + dates from each record's stored text and rewrite the, _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number(), _ocr_text(), Path (+14 more)

### Community 31 - "Retrieval Error Classification"
Cohesion: 0.17
Nodes (18): classify_answer(), classify_query(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any, Chunk IDs embed section headings containing spaces, so parse TREC     fields pos (+10 more)

### Community 32 - "Local Model Adjudication"
Cohesion: 0.19
Nodes (12): _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external ann, Five pilot rows from five strata measure more than five from one -     the gemin, Vote records must say annotator "qwen" (never reuse "gemini" - the     agreement, Back-compat guard: the gemini leg (on hold, not removed) must keep     producing, Qwen-family models may emit <think>...</think> as inline text rather     than as, _row(), test_adjudicate_default_annotator_stays_gemini() (+4 more)

### Community 33 - "TREC Runfile Conversion"
Cohesion: 0.15
Nodes (22): chunk_docid(), circular_docid(), MalformedChunkId, Write TREC qrels (`qid 0 docid rel`) at circular level.      Binary relevance: g, Raised when an id cannot yield a whitespace-free TREC doc id., Percent-encode whitespace so a circular id is a single TREC field.      Reversib, Map a chunk id to a whitespace-free TREC doc id.      `<circular>#<heading with, write_trec_qrels() (+14 more)

### Community 34 - "Circular Web Scraping"
Cohesion: 0.22
Nodes (10): log(), Margin sweep for B' selective citations on the golden_v7 adjudicated set.  One m, run(), main(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).  Write, One scoring path shared by `eval_json.py` (which measures) and `derive_threshold, Score one golden row through the production-shaped pipeline.      Returns per-ro, Per-row records -> metric -> score vector, skipping rows where the     metric wa (+2 more)

### Community 35 - "Missing PDF Recovery"
Cohesion: 0.33
Nodes (14): validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations(), test_duplicate_text_across_records_flagged(), test_empty_text_is_not_a_duplicate_cluster(), test_flags_bad_issue_date() (+6 more)

### Community 36 - "PDF Metadata Parsing"
Cohesion: 0.10
Nodes (23): Pattern, _iso_date(), _labeled_date(), parse_meta(), _primary_number(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF. (+15 more)

### Community 37 - "RAG Pipeline Construction"
Cohesion: 0.15
Nodes (24): BaseModel, FastAPI, Build a lightweight pipeline for --smoke mode.      Uses a stub retriever (no FA, smoke_pipeline(), build_default_pipeline(), _citation_meta(), CitationMeta, create_app() (+16 more)

### Community 38 - "Web Scraper Testing"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 39 - "Context Precision Metrics"
Cohesion: 0.19
Nodes (7): MeasureReport, MeasureResult, Run all (or specified) metrics sequentially., run_all_metrics(), Empty metrics list is falsy → defaults to ALL_METRICS., TestDataClasses, TestRegistry

### Community 40 - "Label Provenance and Tiers"
Cohesion: 0.12
Nodes (20): classify_tier(), human_reviewed_ids(), main(), Path, Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.  go, Map provenance to the controlled vocabulary.      `human_reviewed` (row appears, Row ids present in the human labelling packet., Controlled-vocabulary label_tier over golden_v7 (spec A §8.3). (+12 more)

### Community 41 - "Statistical and Hardware Helpers"
Cohesion: 0.16
Nodes (9): _bootstrap_ci(), _git_commit(), _mps_memory(), Path, Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict., When torch+MPS available, returns memory stats dict. (+1 more)

### Community 42 - "Reranker Performance Evaluation"
Cohesion: 0.15
Nodes (11): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), v2 protocol: closed-set identification instead of yes/no judgment.     Naming wh, True iff the reply names a valid excerpt number. 'none' or anything     unparsea, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the     gat (+3 more)

### Community 43 - "Export Integration Testing"
Cohesion: 0.31
Nodes (10): assemble_pool(), TREC-style pool: gold-doc literal matches lead, then round-robin over     [reran, One gold doc with `n` chunks that ALL contain the word "broker", so a     must_c, Regression (2026-07-25): a must_contain literal matching many gold-doc     chunk, _retriever(), _saturating_retriever(), test_bm25_leg_uses_raw_query_not_expansion(), test_deep_relevant_chunk_is_reachable_despite_a_common_literal() (+2 more)

### Community 44 - "Local Model Inference"
Cohesion: 0.21
Nodes (14): _current_model(), _extract_text(), main(), pilot(), _pilot_ids(), _post_local(), Path, External annotation slice: local-model leg via oMLX - the PRIMARY leg since 2026 (+6 more)

### Community 45 - "Citation and Generation Benchmarking"
Cohesion: 0.17
Nodes (11): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage.  Offline only —, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_none_and_empty_hyde_are_identical_to_baseline() (+3 more)

### Community 46 - "HyDE Query Expansion"
Cohesion: 0.13
Nodes (8): expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic, _chunk(), Query-side lexical expansion (intervention #2, glossary variant).  Lay->statutor, test_expand_sparse_off_routes_raw_query_to_sparse_leg(), test_retrieve_dense_leg_keeps_raw_query(), test_retrieve_routes_expanded_query_to_sparse_leg()

### Community 48 - "Document Segmentation and Chunking"
Cohesion: 0.26
Nodes (11): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+3 more)

### Community 49 - "Metric Reporting and Testing"
Cohesion: 0.36
Nodes (7): auroc(), best_threshold(), evaluate(), main(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t

### Community 50 - "Metric Execution Registry"
Cohesion: 0.31
Nodes (8): parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY)., (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'.      Takes the LAST bracket group, short_name_of(), _text()

### Community 51 - "Query Expansion and RRF"
Cohesion: 0.17
Nodes (11): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).  Resumable, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10).  Pulls the i, load_circulars(), Path, Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., _pipeline() (+3 more)

### Community 52 - "Hugging Face Spaces Deployment"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_spaces), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 53 - "Golden Set Evaluation Gates"
Cohesion: 0.06
Nodes (35): derive_floors(), metric -> per-query score vector, into gate-floor names -> floor value.      Met, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the derived, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed     v7 gate,, True iff every floor's metric is present in `report_gate` and meets it.      Mis, select_golden() (+27 more)

### Community 54 - "Hardware Device Selection"
Cohesion: 0.20
Nodes (11): pick_device(), Device + precision selection for Apple-Silicon inference.  Centralizes the mps/c, Resolve the compute device.      A truthy explicit `pref` ("mps"/"cpu"/"cuda") w, fp16 only on GPU-class devices; never on cpu. bf16 is never returned     here by, should_use_fp16(), Device + fp16 policy selection (no real torch/mps required)., test_pick_device_auto_cpu_when_no_mps(), test_pick_device_auto_mps_when_available() (+3 more)

### Community 55 - "Reference Number Normalization"
Cohesion: 0.50
Nodes (4): Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104",     "HO/ (, References split across tokens: merge up to 4 tokens after the first     HO/CIR/, _rejoin_split(), _s_anchor_merge()

### Community 56 - "Golden Set Seeding"
Cohesion: 0.38
Nodes (4): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).  C, test_carry_preserves_ids_and_adds_v7_defaults()

### Community 57 - "MLX Native Reranking"
Cohesion: 0.15
Nodes (12): main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).  Standalo, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.  splad, (batch, seq, vocab) logits + (batch, seq) mask -> (batch, vocab) weights. (+4 more)

### Community 58 - "Exact Confidence Intervals"
Cohesion: 0.22
Nodes (5): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion.      Use this for stri, test_render_report_includes_ac1_and_provision(), The reason for the switch. On 9/10 the percentile bootstrap returns         [0.7, TestClopperPearson

### Community 59 - "Master Circular Metadata"
Cohesion: 0.25
Nodes (6): _doc(), cited_docs(), metrics(), Capture-once margin sweep for B' selective citations.  One pipeline pass over th, evaluate(), Calibrate top_k and the abstention threshold against the citation-precision sign

### Community 60 - "Dataset Hub Upload"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 61 - "User Interface Components"
Cohesion: 0.33
Nodes (8): build_ui(), _empty_outputs(), _parse_as_of(), Ten-slot output tuple for early returns (matches build_ui outputs order)., Normalise the optional as-of field: empty -> None, else strict ISO     YYYY-MM-D, SSRF guard: reject URLs pointing to private/internal/reserved addresses.      Bl, submit_query(), _validate_api_url()

### Community 62 - "Regulation Edge Auditing"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 63 - "UI Logic Testing"
Cohesion: 0.18
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 64 - "Benchmark Schema Validation"
Cohesion: 0.43
Nodes (5): _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields()

### Community 65 - "Corpus Text Repair"
Cohesion: 0.22
Nodes (4): main(), Repair the 6 records whose body text was overwritten with one shared circular's, The repair map must name a real orphan PDF that parses to the circular_number it, test_numbers_normalize_distinctly()

### Community 66 - "Evaluation Harness Testing"
Cohesion: 0.11
Nodes (14): _load_items(), main(), Path, Pool-width sweep (intervention #3): answer-level rescue rate vs reranker latency, main(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of, BGEM3Embedder, ndarray (+6 more)

### Community 67 - "Comparative Run Analysis"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries.      Returns mean_b - m, Randomization p-values use the (count+1)/(n+1) estimator, so a         p-value o, One query flipping out of 56 is exactly the iv9-style verdict: the         rando, TestPairedDelta

### Community 69 - "Operations Server Management"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 70 - "Regulation Edge Precision Audit"
Cohesion: 0.29
Nodes (10): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7).  Emits a, Up to `n` edges, spread as evenly as possible across evidence tiers.      Tiers, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+2 more)

### Community 71 - "Draft Adjudication Workflow"
Cohesion: 0.23
Nodes (12): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX.  Reads draft rows from golden_v7.json, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+4 more)

### Community 72 - "Incremental Index Building"
Cohesion: 0.13
Nodes (19): Protocol, Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the per, Emit one JSON line of retrieval/citation/abstention metrics using the persisted, Embedder, Embedder protocol + a deterministic test embedder + the real bge-m3 embedder.  T, faithfulness() (+11 more)

### Community 74 - "Bootstrap Confidence Intervals"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must         be, TestBootstrapCI

### Community 75 - "Retrieval Failure Analysis"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 76 - "Governing Span Resolution"
Cohesion: 0.21
Nodes (14): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions`     (keyed, _min_agreement_fixture(), Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7): Cohen's, _same_provision_fixture(), test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only() (+6 more)

### Community 77 - ".test_mean_reproduces_the_archived_aggregate"
Cohesion: 0.33
Nodes (3): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}., read_trec_run(), The archived runfiles embed section headings in the doc id.

### Community 78 - "Agreement Metric Testing"
Cohesion: 0.19
Nodes (15): _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain.      Cas, The non-SEBI domain filter must match words, not substrings.  Shipped 2026-07-30, The exact query that exposed the bug., Guard against false positives on cross-domain SEBI questions., Any single-token keyword <= 5 chars is a substring hazard. Embedding it     insi, test_arbitrage_is_not_a_non_sebi_domain(), test_arbitration_is_not_a_non_sebi_domain() (+7 more)

### Community 79 - "Adjudication Error Handling"
Cohesion: 0.22
Nodes (10): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt)     -> str, Scans the per-row cache for `ids` and returns the ones flagged     parse_error:, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct     from a we, Defensive: an id that was never adjudicated (no cache file at all)     is not re, test_adjudicate_marks_parse_error_for_garbled_abstain_protocol_reply() (+2 more)

### Community 80 - "Supersession Precision Metrics"
Cohesion: 0.28
Nodes (10): _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., _StubJudge, test_identify_prompt_numbers_excerpts(), test_judge_no_forces_abstention(), test_judge_yes_answers_normally(), test_no_judge_preserves_legacy_behaviour(), test_score_gate_short_circuits_judge() (+2 more)

### Community 81 - "Regulation Edge Integration Testing"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 82 - "SEBI RAG Project"
Cohesion: 0.26
Nodes (12): _build_chunks(), _build_pipeline(), Minimal end-to-end test of the SEBI RAG pipeline.  Runs fully offline (HashEmbed, Offline pipeline whose single circular rests on a repealed regulation., _repealed_basis_pipeline(), test_abstention_on_out_of_domain_query(), test_hybrid_retrieval_finds_relevant_circular(), test_note_absent_when_index_is_none() (+4 more)

### Community 83 - "Run Rescoring and Backfilling"
Cohesion: 0.07
Nodes (42): load_runs(), main(), Path, Assign epochs to the archived runs and write the epoch registry.  Every run's re, _fmt(), guard_pair(), main(), Path (+34 more)

### Community 85 - "Prompt Injection Security"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 86 - "Regulatory Basis Indexing"
Cohesion: 0.30
Nodes (9): HybridRetriever, _chunks(), _fake_encode(), Returns a fixed dense ranking regardless of query., _StubDense, _StubSparse, test_flag_off_is_unchanged_and_ignores_splade(), test_splade_leg_changes_fused_order_when_on() (+1 more)

### Community 88 - "sweep_rrf_k.py"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 89 - "Document ID Remapping"
Cohesion: 0.38
Nodes (6): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, Every record's text must match the PDF its provenance names.      Slow (re-extra, validate_deep()

### Community 90 - "New Circular Discovery"
Cohesion: 0.29
Nodes (8): _alias_keys(), Candidate alias lookup keys, most literal first.      Both the raw normalised fo, PMS/NCS/ILDS end in a literal S. Unconditional plural-stripping mapped     them, reg_id resolved purely through the alias table, ignoring the corpus., A table key that no _alias_keys() output can produce is dead config., _resolved(), test_acronyms_ending_in_s_reach_their_own_entry(), test_every_alias_entry_is_reachable_from_some_spelling()

### Community 91 - "Retrieval Metric Implementation"
Cohesion: 0.18
Nodes (7): Chunk, _grounded_prompt(), ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, SubjectSimJudge

### Community 92 - ".family"
Cohesion: 0.29
Nodes (7): gwet_ac1(), Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a     prevalen, The kappa base-rate paradox: one label dominates, raw agreement is high,     yet, test_gwet_ac1_both_constant_and_identical_is_one(), test_gwet_ac1_empty_input_is_one(), test_gwet_ac1_exceeds_kappa_on_skewed_high_agreement(), test_gwet_ac1_identical_lists_is_one()

### Community 93 - "Provision-Level Agreement"
Cohesion: 0.20
Nodes (10): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using     the, Does this external vote confirm claude's label, at PROVISION level?      Amendme, Different chunk copies of the same quoted provision agree at provision     level, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction(), test_provision_agree_disjoint_without_pool_is_false() (+2 more)

### Community 94 - "SEBI Circular Identifiers"
Cohesion: 0.25
Nodes (8): CIR/MRD/DP/19/2010, List of Circulars, List of Communications, MRD/DoP/Dep/Cir-29/2004, MRD/DoP/MAS – OW/16723/2010, Securities and Exchange Board of India, SEBI/MRD/SE/DEP/Cir-4/2005, SMDRP/NSDL/3055/1998

### Community 95 - "Configuration and Settings Management"
Cohesion: 0.19
Nodes (18): Build the full pipeline with real models., real_pipeline(), _as_bool(), _get(), Settings.load() plus the [spaces] table as settings.spaces.*          Load order, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default, _clear() (+10 more)

### Community 96 - "Execution Shell Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 97 - "Canary Deployment Scripts"
Cohesion: 0.25
Nodes (7): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, SEBI_RAG_EVAL_GENERATOR, canary.sh script, TOKENIZERS_PARALLELISM

### Community 98 - "PDF Recovery Testing"
Cohesion: 0.19
Nodes (11): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:, _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13).  Pure functions only: l, (listing_date, detail_url, title) rows from one listing page, deduped. (+3 more)

### Community 99 - "Path"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan, _master(), test_annotate_idempotent() (+7 more)

### Community 100 - "Data Refresh Scripts"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 101 - "write_dataset_cards"
Cohesion: 0.17
Nodes (18): AsofCaseResult, build_report(), As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, Assemble the persisted as-of run artifact.      Pipeline accuracy is the headlin, Aggregate case results with an exact confidence interval.      Pure function of, run_pipeline_cases(), summarize(), Shape of the persisted as-of run artifact. (+10 more)

### Community 102 - "measure_supersession_precision"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine.      Samples c, Verify a supersession edge by cross-referencing corpus records.      Returns "tr, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 103 - "Annotation Provenance Auditing"
Cohesion: 0.21
Nodes (15): audit(), collect_artifacts(), _ids_from_csv(), _ids_from_dir(), _ids_from_jsonl(), main(), Path, Report what the annotation artifacts can account for, before classifying.  golde (+7 more)

### Community 104 - "Temporal Accuracy Metrics"
Cohesion: 0.28
Nodes (5): main(), metrics_to_markdown(), Format results as a markdown table., Unit tests for sebi_rag.measure — automated metric collection., TestCLI

### Community 107 - "test_gate.py"
Cohesion: 0.38
Nodes (4): measure_parsing_latency(), Measure PDF ingestion throughput (chars/sec, ms/PDF).      Samples 20 PDFs strat, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 108 - "Regulation Edge Construction"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline).  No networ, write_jsonl()

### Community 109 - "Retrieval Artifact Testing"
Cohesion: 0.22
Nodes (5): bench_retrieval must emit valid TREC alongside the legacy runfile., run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so     every, iv9/iv10 build a headered index beside data/index. Without an index     override, test_bench_retrieval_can_bench_an_alternate_index(), test_bench_retrieval_can_measure_the_reranked_order()

### Community 110 - "Auto-research Environment Script"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 111 - "run_all_metrics"
Cohesion: 0.24
Nodes (11): Rankings, Path, Standards-compliant TREC run and qrels emission.  The archived runfiles are not, Reverse map `docid -> full chunk id`, so nothing is lost., Valid 6-field TREC run at chunk granularity., write_docids(), _write_lines(), write_run_chunk() (+3 more)

### Community 113 - "RAG Demo Application"
Cohesion: 0.31
Nodes (7): build_ui(), get_pipeline(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Gradio SDK, Cache one pipeline per mode; both share retriever/reranker/lineage., Normalise the optional as-of date field: empty -> None, else strict     ISO YYYY, run_query_spaces()

### Community 114 - "Human Evaluation Packets"
Cohesion: 0.67
Nodes (3): Golden v7 Human Packet, SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026, SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122

### Community 115 - "Lexical Reranking and Pooling"
Cohesion: 0.13
Nodes (31): Reranker, HashEmbedder, Deterministic hashed bag-of-words embedding. No model, no network.      Stable a, ExtractiveStubGenerator, Deterministic: returns the top context text. No model required., Chunk, Lineage, LexicalReranker (+23 more)

### Community 125 - "Quote to Chunk Resolution"
Cohesion: 0.20
Nodes (16): BenchmarkIssue, chunks_by_doc(), _norm_ws(), qrels_rows(), Span {doc, quote} -> matching chunk ids (all overlap matches count).      Legacy, resolve_chunk_spans(), _span_resolution_issues(), Chunk (+8 more)

### Community 130 - "RAG Benchmark Export"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation.  Outputs:, write_card()

### Community 136 - "test_pipeline.py"
Cohesion: 0.15
Nodes (10): Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, contexts_for(), ADR-002 follow-up: compare the production subject-sim gate against the SECTION-A, _currency(), demote_superseded(), mc_topic(), P2 — cross-document supersession resolution.  Classifies each circular's referen, Normalised topic of a 'Master Circular for/on <TOPIC>' title, else None.      Us (+2 more)

### Community 137 - "test_eval_generator.py"
Cohesion: 0.17
Nodes (9): The eval stack's generator choice must be one shared decision.  `derive_threshol, Uses an injected loader so the test stays offline., Silently falling back to the stub would derive floors under semantics     the ca, Must assert the factory is CALLED, not merely imported.      Verified 2026-08-12, A factory both call is not enough - they must pass the same setting,     or the, test_both_eval_scripts_read_the_same_setting(), test_eval_scripts_use_the_shared_factory(), test_mlx_kind_builds_the_production_generator() (+1 more)

### Community 138 - ".build"
Cohesion: 0.31
Nodes (8): main(), mrr(), ndcg_at_k(), Sweep RRF k_const values on the golden set. No index rebuild needed., recall_at_k(), Reciprocal Rank Fusion. Rank-only — sidesteps score-scale mismatch., rrf_fuse(), test_rrf_fusion_orders_by_reciprocal_rank()

### Community 139 - "measure.py"
Cohesion: 0.38
Nodes (4): mrr(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), Automated metric collection for the SEBI Circular RAG pipeline.  Six on-demand m

### Community 140 - "test_incremental_index.py"
Cohesion: 0.46
Nodes (6): _corpus_v1(), CountingEmbedder, _doc(), Offline tests for F3 incremental indexing (ADR-001): only new/changed docs are e, test_incremental_encodes_only_delta(), test_incremental_falls_back_to_full_without_cache()

### Community 141 - "expand.py"
Cohesion: 0.35
Nodes (10): Answer, answer_with_abstention(), _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful(), test_no_context_reason_when_top_k_zero() (+2 more)

### Community 142 - "test_build_index_out_dir.py"
Cohesion: 0.29
Nodes (5): build_index must be able to target a scratch index directory.  The iv9/iv10 head, A --out flag that is parsed but ignored is worse than none: it reads     as safe, lineage.json lands next to the index it describes; writing it into     data/inde, test_build_index_saves_to_the_resolved_out_dir_not_the_constant(), test_lineage_follows_the_out_dir()

### Community 143 - "measure_mrr"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level.      For each query, RR = 1/rank of firs, TestMRR

### Community 144 - ".encode"
Cohesion: 0.23
Nodes (16): _aggregate(), EvalReport, _mean(), Golden-set evaluation harness (P1).  Runs the pipeline over a labelled golden se, report_dict(), run_eval(), SEBI Circular RAG — local-first, Apple Silicon.  Pipeline: ingest -> segment ->, _pipeline() (+8 more)

### Community 145 - "test_canary_generator.py"
Cohesion: 0.27
Nodes (8): _canary_jscode(), _ops_timeout(), The eval canary must fit its timeout and alert on real regressions.  Measured 20, n8n gives up first if its budget is smaller, so the ops timeout is     never rea, A threshold above the healthy value fires every run. citation_precision     was, test_alert_thresholds_sit_below_measured_baselines(), test_n8n_timeout_not_tighter_than_the_ops_budget(), test_ops_timeout_fits_the_measured_runtime()

### Community 146 - "TestPerQueryRecall"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 147 - "measure_temporal_accuracy"
Cohesion: 0.43
Nodes (3): measure_temporal_accuracy(), Measure fraction of as_of queries returning correct pre-supersession     circula, TestTemporalAccuracy

### Community 148 - "detect_relations_ex"
Cohesion: 0.50
Nodes (3): _chunks(), Index persistence round-trip (offline)., test_index_save_load_roundtrip()

### Community 149 - "_unique"
Cohesion: 0.31
Nodes (7): run_retrieval_benchmark(), _doc(), _eval_item(), _unique(), measure_context_precision(), Fraction of top-k chunks from relevant circulars.      Unlike recall@k (which is, TestContextPrecision

### Community 150 - "stats.py"
Cohesion: 0.25
Nodes (5): BootstrapCI, PairedResult, Uncertainty quantification for benchmark runs.  The golden set is n=56 answerabl, True when the randomization test rejects at 1 - confidence AND the         paire, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 151 - "_resolve_governing_spans"
Cohesion: 0.36
Nodes (8): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote}     spans, look, _resolve_governing_spans(), _pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool(), test_resolve_governing_spans_short_body_uses_whole_body(), test_resolve_governing_spans_uses_first_60_body_chars()

### Community 152 - "write_run_doc"
Cohesion: 0.25
Nodes (8): Valid 6-field TREC run collapsed to circular level.      Keeps each circular onc, write_run_doc(), artifacts(), The encoding must agree across runs and qrels.      If a run says `SEBI/IMD/MC%2, test_qrels_docids_match_run_doc_docids_exactly(), test_run_doc_dedupes_to_best_rank(), test_run_doc_encodes_space_bearing_circulars(), test_run_doc_lines_have_exactly_six_fields()

### Community 153 - "SparseIndex"
Cohesion: 0.25
Nodes (3): BM25 lexical index (bm25s)., SparseIndex, test_expanded_sparse_query_hits_statutory_chunk()

### Community 154 - "test_trec_parity.py"
Cohesion: 0.57
Nodes (6): _internal(), Prove the internal retrieval metrics are the standard ones.  Skips unless the op, _standard(), test_mrr_matches_ir_measures(), test_ndcg_at_10_matches_ir_measures(), test_recall_at_10_matches_ir_measures()

### Community 155 - "test_eval_asof.py"
Cohesion: 0.40
Nodes (4): run_selector_cases(), _lin_chain(), P4b: as-of golden evaluation runner tests (offline)., test_run_selector_cases_pass_and_fail()

### Community 156 - "_doc_checksum"
Cohesion: 0.18
Nodes (11): Embedder, ndarray, Path, RAGPipeline, main(), smoke_pipeline(), DenseIndex, _doc_checksum() (+3 more)

### Community 159 - "main"
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the docume, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 162 - "load_golden_asof"
Cohesion: 0.67
Nodes (3): load_golden_asof(), Path, test_load_golden_asof_has_both_modes()

## Knowledge Gaps
- **46 isolated node(s):** `canary.sh script`, `HF_HUB_DISABLE_XET`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS`, `PYTORCH_ENABLE_MPS_FALLBACK` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `Quote to Chunk Resolution` to `RAG Benchmark Export`, `End-to-End Integration Testing`, `LLM Generation Providers`, `Hugging Face Data Loading`, `test_pipeline.py`, `Golden Set Versioning`, `expand.py`, `Contextual Header Generation`, `Golden Set Schema Validation`, `Citation and Generation Benchmarking`, `Query Expansion and RRF`, `Benchmark Schema Validation`, `Evaluation Harness Testing`, `Incremental Index Building`, `Supersession Precision Metrics`, `Prompt Injection Security`, `Regulatory Basis Indexing`, `sweep_rrf_k.py`, `Lexical Reranking and Pooling`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `RAG Pipeline Construction` to `Hugging Face Data Loading`, `Golden Set Versioning`, `measure.py`, `expand.py`, `measure_mrr`, `.encode`, `TestPerQueryRecall`, `measure_temporal_accuracy`, `_unique`, `API Service and Integration`, `TestPerQueryRecall`, `Circular Web Scraping`, `Context Precision Metrics`, `Incremental Index Building`, `Run Rescoring and Backfilling`, `Configuration and Settings Management`, `write_dataset_cards`, `measure_supersession_precision`, `test_gate.py`, `Lexical Reranking and Pooling`, `Quote to Chunk Resolution`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `CircularMeta` connect `Lexical Reranking and Pooling` to `TestPerQueryRecall`, `End-to-End Integration Testing`, `Context Precision Metrics`, `Hugging Face Data Loading`, `detect_relations_ex`, `test_gate.py`, `measure.py`, `Export Integration Testing`, `test_incremental_index.py`, `.encode`, `SEBI RAG Project`, `Query Expansion and RRF`, `detect_relations_ex`, `Run Rescoring and Backfilling`, `API Service and Integration`, `Quote to Chunk Resolution`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `Chunk` (e.g. with `BenchmarkIssue` and `HeaderGenerator`) actually correct?**
  _`Chunk` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `RAGPipeline` (e.g. with `run()` and `CitationMeta`) actually correct?**
  _`RAGPipeline` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `hierarchical_chunk()` (e.g. with `_distinct_pipeline()` and `_slow_pipeline()`) actually correct?**
  _`hierarchical_chunk()` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `ExtractiveStubGenerator` (e.g. with `get_pipeline()` and `run()`) actually correct?**
  _`ExtractiveStubGenerator` has 36 INFERRED edges - model-reasoned connections that need verification._