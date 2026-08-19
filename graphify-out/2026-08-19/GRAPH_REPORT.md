# Graph Report - SEBI circular RAG  (2026-08-19)

## Corpus Check
- 199 files · ~186,345 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2501 nodes · 5257 edges · 146 communities (119 shown, 27 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 1262 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b1d5c5c4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- export_datasets.py
- answer_with_abstention
- telemetry_engine.py
- test_golden_v7_packet.py
- Frame
- RAGPipeline
- HybridRetriever
- SpladeIndex
- test_golden_v7_gate.py
- generate.py
- backfill_escalations.py
- test_selective_citations.py
- test_api.py
- build_lineage
- test_regulations.py
- extract_citations
- test_dataset_cards.py
- test_ui.py
- derive_validity
- ValueError
- test_reg_lineage.py
- test_golden_v7_gemini.py
- test_attribution.py
- _is_non_sebi_domain
- test_export_datasets.py
- load_circulars
- _row
- extract_misses.py
- benchmark.py
- test_label_tier.py
- scrape_sebi.py
- discover_new.py
- gemini_adjudicate.py
- app.py
- regulations.py
- test_trecio.py
- agreement.py
- ingest_pdf.py
- SpacesSettings
- Settings
- test_golden_v7_local.py
- per_query_recall
- publish_hf.py
- parse_meta
- test_ingest_pdf.py
- write_run_chunk
- sebi_rag/eval_asof.py
- test_pipeline.py
- hierarchical_chunk
- test_scrape_sebi.py
- audit_label_provenance.py
- local_adjudicate.py
- eval_harness.py
- consolidation_edges
- test_export_integration.py
- sweep_citation_margin.py
- measure_supersession_precision
- validate_golden_v7
- bootstrap_ci
- test_scrape_regulations.py
- reg_display_name
- main
- sweep_rrf_k.py
- test_expand.py
- test_hyde.py
- stats.py
- test_app_zerogpu.py
- eval_generator_for
- test_ingest_refs.py
- MeasureResult
- Qwen3MLXReranker
- clopper_pearson_ci
- ui.py
- adjudicate_draft.py
- write_run_doc
- test_golden_v7_pool.py
- test_push_datasets.py
- test_certainty.py
- gwet_ac1
- test_audit_reg_edges.py
- test_spaces.py
- test_trec_parity.py
- test_repair_corpus_text.py
- resolve_chunk_spans
- Handler
- audit_reg_edges.py
- remap_doc_ids.py
- build_spaces_pipeline
- build_report
- trace_failure.py
- _provision_agree
- adjudicate
- read_trec_run
- main
- test_build_reg_edges.py
- test_canary_generator.py
- _rejoin_split
- _doc
- test_injection.py
- _FixedReranker
- faithfulness
- test_bench_retrieval_artifacts.py
- canary.sh
- _resolve_governing_spans
- relabel_repooled.py
- pipeline
- .encode
- _s_mc_no
- .encode
- test_incremental_index.py
- _HallucinatingGenerator
- run.sh
- test_annotation_adds_no_circular_meta_field
- .grounded
- seed_v7.py
- refresh.sh
- api.py
- test_every_alias_target_is_in_force_or_has_a_succession_entry
- sebi-rag
- run_all_metrics
- test_app_asof.py
- Overall Evaluation Summary
- autoresearch.sh
- TestPerQueryRecall
- MLXGenerator
- Overall Evaluation Summary
- Golden v7 Human Packet
- deploy_space.py
- upload_spaces_index.py
- Chunk
- measure.sh
- scripts/autoresearch/__init__.py
- dev.sh
- notify.sh
- start_phoenix.sh
- conftest.py
- conftest.py
- SEBI Master Circular CIR/DNPD/1/2012
- Optimize Slash Command
- Seen Circular IDs
- SEBI Master Circular CIR/DNPD/1/2012
- Seen Circular IDs
- Hugging Face Spaces Requirements
- Master Appendix (Depository)
- SEBI Regulations Listing

## God Nodes (most connected - your core abstractions)
1. `Chunk` - 99 edges
2. `RAGPipeline` - 58 edges
3. `ExtractiveStubGenerator` - 56 edges
4. `HashEmbedder` - 47 edges
5. `hierarchical_chunk()` - 45 edges
6. `CircularMeta` - 41 edges
7. `answer_with_abstention()` - 34 edges
8. `Lineage` - 33 edges
9. `build_lineage()` - 32 edges
10. `SubjectSimJudge` - 31 edges

## Surprising Connections (you probably didn't know these)
- `test_run_metadata_has_reproducibility_fields()` --calls--> `run_metadata()`  [INFERRED]
  tests/test_benchmark.py → src/sebi_rag/benchmark.py
- `test_validate_golden_reports_unjudged_as_warning_not_error()` --calls--> `validate_golden()`  [INFERRED]
  tests/test_unjudged_exclusion.py → src/sebi_rag/benchmark.py
- `test_validate_golden_still_errors_on_real_corruption()` --calls--> `validate_golden()`  [INFERRED]
  tests/test_unjudged_exclusion.py → src/sebi_rag/benchmark.py
- `test_legacy_string_entries_pass_through()` --calls--> `resolve_chunk_spans()`  [INFERRED]
  tests/test_golden_v7_resolver.py → src/sebi_rag/benchmark.py
- `test_numbers_normalize_distinctly()` --calls--> `normalize_circular_number()`  [INFERRED]
  tests/test_repair_corpus_text.py → src/sebi_rag/ingest_pdf.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Evaluation Run 2026-08-15** — eval_runs_eval_asof_2026_08_15_pipeline, eval_runs_eval_asof_2026_08_15_selector, eval_runs_eval_asof_2026_08_15_overall [EXTRACTED 1.00]
- **SEBI Regulatory Framework** — tests_fixtures_master_appendix_pre2015_sebi, tests_fixtures_master_appendix_pre2015_circulars, tests_fixtures_master_appendix_pre2015_communications [INFERRED 0.90]

## Communities (146 total, 27 thin omitted)

### Community 0 - "export_datasets.py"
Cohesion: 0.06
Nodes (66): build_aikosh_pack(), build_chunk_rows(), build_citation_pairs(), build_corpus_rows(), build_eval_rows(), build_hf_card(), build_kaggle_metadata(), build_lineage_rows() (+58 more)

### Community 1 - "answer_with_abstention"
Cohesion: 0.05
Nodes (65): Rankings, _assert_fixed_tail(), convert_run_dir(), main(), Path, Back-convert archived runfiles into standards-compliant TREC artifacts.  The arc, Trailing field of the first line; also the whitespace precondition check., read_trec_run assumes qid and tag carry no whitespace. Verify per line. (+57 more)

### Community 2 - "telemetry_engine.py"
Cohesion: 0.07
Nodes (32): Protocol, Capture-once margin sweep for B' selective citations.  One pipeline pass over th, Margin sweep for B' selective citations on the golden_v7 adjudicated set.  One m, Benchmark MLX generators on the golden set: faithfulness, groundedness, abstenti, Retrieval-only benchmark with TREC runfile and reproducibility metadata.  Use --, Build eval/golden/golden_v4.jsonl for the larger corpus. Each query is mapped to, Build the dense+sparse index once and persist it (run after corpus changes)., Calibrate top_k and the abstention threshold against the citation-precision sign (+24 more)

### Community 3 - "test_golden_v7_packet.py"
Cohesion: 0.06
Nodes (55): ArgumentParser, analyze_state(), build_parser(), capture_live_performance(), check_degradation(), check_safety_limit(), correction_pass(), fetch_omlx_metrics() (+47 more)

### Community 4 - "Frame"
Cohesion: 0.07
Nodes (52): Random, _apportion(), ingest_packet(), _ingest_to_votes(), main(), Path, External annotation slice: stratified sampling + blind human packet + CSV ingest, Writes the blind human packet for `human_ids` (a subset of `ids`, the     full e (+44 more)

### Community 5 - "RAGPipeline"
Cohesion: 0.08
Nodes (37): load_runs(), main(), Path, Assign epochs to the archived runs and write the epoch registry.  Every run's re, guard_pair(), Refuse any paired comparison that spans two frames.      The archive covers four, assert_comparable(), assign_epochs() (+29 more)

### Community 6 - "HybridRetriever"
Cohesion: 0.07
Nodes (29): RuntimeError, main(), Build the SPLADE learned-sparse doc matrix once and persist it (iv11).  Standalo, main(), Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the residual, csr_matrix, ndarray, Real Splade_PP encoder: max-pooled MLM logits -> sparse CSR term weights.  splad (+21 more)

### Community 7 - "SpladeIndex"
Cohesion: 0.05
Nodes (57): derive_floors(), Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).  Write, metric -> per-query score vector, into gate-floor names -> floor value.      Met, floors_ok(), Path, Which golden set gates CI, and whether its adjudicated subset clears the derived, Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed     v7 gate,, True iff every floor's metric is present in `report_gate` and meets it.      Mis (+49 more)

### Community 8 - "test_golden_v7_gate.py"
Cohesion: 0.06
Nodes (44): AsofCaseResult, load_golden_asof(), Path, As-of-date golden evaluation runner (P4b).  Two case modes drawn from eval/golde, run_selector_cases(), annotate_corpus(), detect_relations(), detect_relations_ex() (+36 more)

### Community 9 - "generate.py"
Cohesion: 0.16
Nodes (22): _body(), _doc_keys(), find_source_chunk(), _load_candidates(), main(), _norm(), quote_for(), Backfill escalated golden_v7 rows from their Task-5 source candidate (2026-07-25 (+14 more)

### Community 10 - "backfill_escalations.py"
Cohesion: 0.15
Nodes (11): _judge_prompt(), _judge_prompt_identify(), MLXJudge, parse_excerpt_choice(), parse_yes_no(), v2 protocol: closed-set identification instead of yes/no judgment.     Naming wh, True iff the reply names a valid excerpt number. 'none' or anything     unparsea, First yes/no in the reply; unparseable fails OPEN (grounded=True) so the     gat (+3 more)

### Community 11 - "test_selective_citations.py"
Cohesion: 0.08
Nodes (33): _alias_keys(), load_regulations(), name_tokens(), Path, Candidate alias lookup keys, most literal first.      Both the raw normalised fo, Resolve a cited regulation name+year to a canonical reg_id.      Returns (reg_id, Load data/corpus/regulations.jsonl into a list of regulation records.      Thin, Human-readable regulation name. Year disambiguates same-short_name repeal     pa (+25 more)

### Community 12 - "test_api.py"
Cohesion: 0.10
Nodes (43): log(), run(), Build a lightweight pipeline for --smoke mode.      Uses a stub retriever (no FA, Build the full pipeline with real models., real_pipeline(), smoke_pipeline(), main(), smoke_pipeline() (+35 more)

### Community 13 - "build_lineage"
Cohesion: 0.07
Nodes (31): entailment_index(), NLI attribution scoring for B' citation selection.  B' asks "does this context s, Index of the entailment class in a model's label map.      Read from the checkpo, Wrap an already-constructed cross-encoder (also the test seam)., _softmax(), pick_device(), Device + precision selection for Apple-Silicon inference.  Centralizes the mps/c, Resolve the compute device.      A truthy explicit `pref` ("mps"/"cpu"/"cuda") w (+23 more)

### Community 14 - "test_regulations.py"
Cohesion: 0.13
Nodes (22): ExternalSpaceGenerator, HFGenerator, HybridGenerator, CPU / remote generation for the Hugging Face Spaces demo.  All classes implement, External Space first; on ANY failure fall back to the local CPU model.      exte, Primary generator: calls a public LLM Space via gradio_client.      Wired to hug, Fallback generator: small instruct model via transformers on CPU., [spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).      Nev (+14 more)

### Community 15 - "extract_citations"
Cohesion: 0.05
Nodes (60): main(), Generate contextual headers for deep sub-clause + annex chunks (iv9).  Resumable, main(), Select + reuse iv9 headers for 3 failure-adjacent documents (iv10).  Pulls the i, apply_context_headers(), filter_targeted_rows(), HeaderGenerator, in_scope() (+52 more)

### Community 16 - "test_dataset_cards.py"
Cohesion: 0.10
Nodes (38): citation_scorer_for(), The single enable/disable AND backend decision for B'.      Returns None when di, Context ids the answer rests on. Scores each context's answer-relevance     via, select_citations(), _chunk(), _FakeReranker, Tests for B' selective citations: select_citations() and its integration., When citation_scorer_enabled=True, Settings loads a non-None scorer. (+30 more)

### Community 17 - "test_ui.py"
Cohesion: 0.06
Nodes (52): Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks., _keep(), load_circulars_from_hf(), load_hf_rows(), _meta_from_row(), HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path).  Loads the pu, One HF dataset config as plain dicts (network; cached by `datasets`)., HF-dataset counterpart of corpus.load_circulars() — returns Chunks     ready for (+44 more)

### Community 18 - "derive_validity"
Cohesion: 0.14
Nodes (30): annotate_regulation_fields(), build_regulation_edges(), One `cites` edge per (circular, regulation) pair.      The merged edge carries t, Set regulations / primary_regulation / regulatory_basis_status in place.      Re, Stub records for cited regulations absent from the Updated List.      Returns NE, synthesise_repealed_stubs(), _circ(), Regulation edges + corpus annotation (spec 2026-07-23 §3.3, §3.4, §3.7). (+22 more)

### Community 19 - "ValueError"
Cohesion: 0.10
Nodes (32): Citation, _clause_in(), extract_citations(), _is_table_artefact(), Extract regulation citations from circular text (spec 2026-07-23 §3.3).  Deliber, All regulation citations in a circular, one per occurrence (not deduped).      S, (start, end, sentence) spans over `text`, in order., First clause reference in a sentence, ignoring 4-digit years.      "Regulations (+24 more)

### Community 20 - "test_reg_lineage.py"
Cohesion: 0.06
Nodes (29): Task 4 & 5: Dataset card generation and platform packaging tests., Zenodo pack must have metadata.json + tarball instructions., Zenodo must include DOI and versioning fields., AIKosh pack must include CSV manifests + metadata + licensing., AIKosh manifest must list all dataset configs with row counts., write_dataset_cards() must create HF/Kaggle/Zenodo/AIKosh bundles., README.md for HF must have YAML front matter with dataset metadata., YAML front matter in HF card must parse without errors. (+21 more)

### Community 21 - "test_golden_v7_gemini.py"
Cohesion: 0.06
Nodes (4): Unit tests for the local Gradio UI's pure logic (no server, no gradio launch)., _Resp, test_submit_query_retrieval_only_prepends_banner(), test_submit_query_surfaces_confidence_and_retrieved()

### Community 22 - "test_attribution.py"
Cohesion: 0.12
Nodes (8): classify_circular_type(), derive_validity(), Metadata layer: circular_type taxonomy + validity_status derivation.  Locked dec, Validity of one circular from the tiered edge list (any scope: the     function, edge(), Metadata layer: circular_type taxonomy + validity_status derivation., TestClassifyCircularType, TestDeriveValidity

### Community 23 - "_is_non_sebi_domain"
Cohesion: 0.12
Nodes (26): build_prompt(), Blind-protocol prompt text (plain text, not HTML - no html.escape).     Non-abst, _pool(), Offline tests for gemini_adjudicate.py: blind-protocol prompts, reply parsing, a, Reviewer Important #1: _parse_yes_no reads a blank EXPECTED as     "confirms abs, A non-abstain row whose pool happens to have zero candidates can't     offer any, Decision #3: a valid letter alongside an unrecognized one invalidates     the WH, letters=[] is how adjudicate signals an abstain/zero-candidate row;     parse_re (+18 more)

### Community 24 - "test_export_datasets.py"
Cohesion: 0.10
Nodes (29): _is_non_sebi_domain(), Return True if the query clearly targets a non-SEBI regulator's domain.      Cas, The non-SEBI domain filter must match words, not substrings.  Shipped 2026-07-30, Any single-token keyword <= 5 chars is a substring hazard. Embedding it     insi, Query mentioning both SEBI and RBI should NOT abstain — SEBI intent wins., Empty query should not trigger the non-SEBI filter., FEMA keyword in a SEBI context should NOT abstain — SEBI intent wins., The exact query that exposed the bug. (+21 more)

### Community 25 - "load_circulars"
Cohesion: 0.11
Nodes (24): _chunk(), _citation_corpus_record(), _dept_record(), Offline tests for the dataset export pipeline (corpus config, Task 1)., _record(), test_build_citation_pairs_context_window_is_whitespace_collapsed(), test_build_citation_pairs_excludes_self_reference(), test_build_citation_pairs_normalizes_and_classifies_family() (+16 more)

### Community 26 - "_row"
Cohesion: 0.33
Nodes (14): validate(), 2011-era master circulars use "SEBI/IMD/MC No.2/836/2011" — the     document's o, _rec(), test_allows_legacy_mc_no_format(), test_clean_corpus_has_no_violations(), test_duplicate_text_across_records_flagged(), test_empty_text_is_not_a_duplicate_cluster(), test_flags_bad_issue_date() (+6 more)

### Community 27 - "extract_misses.py"
Cohesion: 0.17
Nodes (23): answer_with_abstention(), _chunk(), Offline tests for the groundedness abstention gate (ADR-001 item 7)., rerank_top exactly at 0.85 overrides judge abstention (HYBRID_THRESHOLD=0.85)., rerank_top just below 0.85 does NOT override judge abstention., When no judge is present, hybrid gate logic must be inert (no crash)., Unrelated query vs context: subject_sim < 0.42 → grounded() returns False., SubjectSimJudge has a section_score method (second-tier gate). (+15 more)

### Community 28 - "benchmark.py"
Cohesion: 0.20
Nodes (3): _grounded_prompt(), F4 (ADR-001): retrieved text is explicitly delimited as quoted DATA and     the, Chunk

### Community 29 - "test_label_tier.py"
Cohesion: 0.13
Nodes (25): decide(), Spec sec7 promotion rules for one row.      `votes_by_annotator` is this row's v, Abstain rows have no explicit claude vote at all (Task 8 never judged     them), Both externals independently think something DOES govern (disputing     the auth, The LLM leg is whichever single non-claude/non-human annotator voted -     "qwen, External marked claude's chunk governing plus extras: claude's label     is conf, The abstain protocol can never emit non-empty governing (no letters     are offe, Two externals both replying NONE on an answerable row must queue,     not flip: (+17 more)

### Community 30 - "scrape_sebi.py"
Cohesion: 0.13
Nodes (21): Embedder, DenseIndex, _doc_checksum(), HybridRetriever, ndarray, Path, F3 (ADR-001): encode only new/changed documents; reuse cached         embedding, Deterministic per-document checksum over its (enriched) chunk texts —     captur (+13 more)

### Community 31 - "discover_new.py"
Cohesion: 0.14
Nodes (13): per_query_recall(), Per-query recall@k at circular level, matching `run_retrieval_benchmark`.      A, Ten chunks of one circular must not crowd the cutoff: the k applies         to u, Answerable-but-unjudged rows are excluded from metrics, never scored 0.  golden_, A real, fully-populated golden row, so the fixture cannot drift out of     sync, v7-ls-038/039/040 are answerable but unjudged; they carry     expected_citation_, _template(), test_abstain_rows_still_excluded() (+5 more)

### Community 32 - "gemini_adjudicate.py"
Cohesion: 0.12
Nodes (20): classify_tier(), human_reviewed_ids(), main(), Path, Add a controlled-vocabulary `label_tier` alongside free-text `label_source`.  go, Map provenance to the controlled vocabulary.      `human_reviewed` (row appears, Row ids present in the human labelling packet., Controlled-vocabulary label_tier over golden_v7 (spec A §8.3). (+12 more)

### Community 33 - "app.py"
Cohesion: 0.10
Nodes (26): _current_model(), _daily_quota_exhausted(), main(), _parse_letter_choice(), _parse_reply(), _parse_yes_no(), _post_gemini(), External annotation slice: second-family LLM leg via the Gemini API (spec 2026-0 (+18 more)

### Community 34 - "regulations.py"
Cohesion: 0.23
Nodes (15): discover(), extract_pdf_urls(), fetch(), _listing_url(), looks_like_pdf(), main(), _page(), _parse_date() (+7 more)

### Community 35 - "test_trecio.py"
Cohesion: 0.16
Nodes (17): _append_message(), _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_citations_md(), _on_submit(), _parse_as_of(), Hugging Face Spaces entrypoint — SEBI Circular RAG demo (CPU-only).  Redesigned (+9 more)

### Community 36 - "agreement.py"
Cohesion: 0.07
Nodes (45): get_pipeline(), Cache one pipeline per mode; both share retriever/reranker/lineage., BaseModel, FastAPI, main(), build_default_pipeline(), _citation_meta(), CitationMeta (+37 more)

### Community 37 - "ingest_pdf.py"
Cohesion: 0.17
Nodes (25): main(), Create the enriched golden_v6 benchmark seed from frozen golden_v5.  This does n, beir_corpus_rows(), beir_query_rows(), BenchmarkIssue, build_golden_v6(), chunks_by_doc(), dir_fingerprint() (+17 more)

### Community 38 - "SpacesSettings"
Cohesion: 0.16
Nodes (16): diff_manifest(), _iso(), parse_listing(), Path, Master-circular coverage verification (spec 2026-07-13).  Pure functions only: l, (listing_date, detail_url, title) rows from one listing page, deduped., Assign exactly one status to every listed row + extra_in_corpus rows., render_markdown() (+8 more)

### Community 39 - "Settings"
Cohesion: 0.11
Nodes (26): classify_answer(), classify_query(), _doc(), load_run(), main(), Path, Classify golden/probe queries against a TREC runfile (throwaway research).  Clas, Answer-level classification: a candidate chunk qualifies if it contains     any (+18 more)

### Community 40 - "test_golden_v7_local.py"
Cohesion: 0.15
Nodes (21): _claude_accuracy_ci(), gwet_ac1(), _label(), _literals_by_row(), _llm_annotator(), main(), Agreement, promotion, and arbitration for the golden-v7 external annotation slic, Gwet's AC1 over the same paired labels as `cohen_kappa`, but with a     prevalen (+13 more)

### Community 41 - "per_query_recall"
Cohesion: 0.19
Nodes (12): _pool(), Offline tests for local_adjudicate.py - the local-model (oMLX/Qwen) external ann, Five pilot rows from five strata measure more than five from one -     the gemin, Vote records must say annotator "qwen" (never reuse "gemini" - the     agreement, Back-compat guard: the gemini leg (on hold, not removed) must keep     producing, Qwen-family models may emit <think>...</think> as inline text rather     than as, _row(), test_adjudicate_default_annotator_stays_gemini() (+4 more)

### Community 42 - "publish_hf.py"
Cohesion: 0.21
Nodes (17): _as_bool(), _get(), Path, Settings.load() plus the [spaces] table as settings.spaces.*          Load order, Resolve a setting: env var > config dict > default., Coerce a config/env value to bool. Env vars arrive as strings; toml/default, _clear(), Settings: defaults, config.toml, and env-override precedence. (+9 more)

### Community 43 - "parse_meta"
Cohesion: 0.26
Nodes (11): assemble_pool(), Candidate pools for chunk-label judging (spec §6). TREC-style pooling: union of, TREC-style pool: gold-doc literal matches lead, then round-robin over     [reran, One gold doc with `n` chunks that ALL contain the word "broker", so a     must_c, Regression (2026-07-25): a must_contain literal matching many gold-doc     chunk, _retriever(), _saturating_retriever(), test_bm25_leg_uses_raw_query_not_expansion() (+3 more)

### Community 44 - "test_ingest_pdf.py"
Cohesion: 0.33
Nodes (10): main(), Rewrite golden_v7 doc references after the corpus renumbering (2026-07-25 remedi, remap(), Doc-id remapping after the 2026-07-25 corpus renumbering (Task 4)., _row(), test_input_rows_are_not_mutated(), test_matching_is_normalization_insensitive(), test_remaps_must_not_cite() (+2 more)

### Community 45 - "write_run_chunk"
Cohesion: 0.16
Nodes (20): main(), Emit TREC qrels for an eval set, keyed by its golden_sha256.      .venv/bin/pyth, export_golden_v7_arrow(), log(), main(), Path, Run export_datasets.py then add golden_v7 Arrow config., Upload dist/datasets/ to HF dataset repo. (+12 more)

### Community 46 - "sebi_rag/eval_asof.py"
Cohesion: 0.12
Nodes (24): Re-derive circular number + dates from each record's stored text and rewrite the, main(), Repair the 6 records whose body text was overwritten with one shared circular's, _existing_numbers(), extract_text(), ingest(), main(), normalize_circular_number() (+16 more)

### Community 47 - "test_pipeline.py"
Cohesion: 0.21
Nodes (13): _build_citations_markdown(), build_ui(), _certainty_badge(), _empty_outputs_md(), _parse_as_of(), Return empty markdown placeholder for streaming., Generator that streams the answer while updating chat history., Return a color-coded confidence badge string. (+5 more)

### Community 48 - "hierarchical_chunk"
Cohesion: 0.14
Nodes (6): Offline tests for the SEBI scraper parsing / pagination logic (no network)., _row(), test_discover_applies_date_filter(), test_discover_graceful_on_fetch_error(), test_discover_no_advance_guard_stops(), test_parse_rows_pairs_date_and_url()

### Community 49 - "test_scrape_sebi.py"
Cohesion: 0.19
Nodes (13): Standards-compliant TREC run and qrels emission.  The archived runfiles are not, Span {doc, quote} -> matching chunk ids (all overlap matches count).      Legacy, resolve_chunk_spans(), run_retrieval_benchmark(), _aggregate(), _doc(), _eval_item(), EvalReport (+5 more)

### Community 50 - "audit_label_provenance.py"
Cohesion: 0.21
Nodes (15): audit(), collect_artifacts(), _ids_from_csv(), _ids_from_dir(), _ids_from_jsonl(), main(), Path, Report what the annotation artifacts can account for, before classifying.  golde (+7 more)

### Community 51 - "local_adjudicate.py"
Cohesion: 0.42
Nodes (8): _chunks(), Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud., _row(), test_legacy_string_entries_pass_through(), test_qrels_span_rows_get_grade_2(), test_resolves_normalized_whitespace_quote(), test_unresolvable_quote_returns_empty(), test_validator_flags_unresolvable_quote_when_chunks_given()

### Community 52 - "eval_harness.py"
Cohesion: 0.20
Nodes (15): annotate_master_fields(), consolidation_edges(), master_series(), Master-circular identity metadata (spec 2026-07-13 §3).  Additive fields only (l, Set is_master/master_series/master_edition/previous_edition in place.      Retur, Edges for circulars listed in a master circular's rescission appendix.      Scan, _master(), test_annotate_idempotent() (+7 more)

### Community 53 - "consolidation_edges"
Cohesion: 0.29
Nodes (4): bootstrap_ci(), Percentile bootstrap interval for the mean of per-query scores., The point of this module: at n=56 and recall ~0.956 the interval must         be, TestBootstrapCI

### Community 54 - "test_export_integration.py"
Cohesion: 0.21
Nodes (14): _current_model(), _extract_text(), main(), pilot(), _pilot_ids(), _post_local(), Path, External annotation slice: local-model leg via oMLX - the PRIMARY leg since 2026 (+6 more)

### Community 55 - "sweep_citation_margin.py"
Cohesion: 0.17
Nodes (8): _bootstrap_ci(), _git_commit(), _mps_memory(), Return (mean, lower_95, upper_95) via bootstrap., Return MPS memory stats if torch+mps available, else empty dict., When torch import fails, _mps_memory returns empty dict., When torch+MPS available, returns memory stats dict., TestHelpers

### Community 56 - "measure_supersession_precision"
Cohesion: 0.28
Nodes (14): Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden.      `chunks` is optio, validate_golden_v7(), Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)., _row(), test_abstain_row_needs_no_labels(), test_as_of_only_on_lineage_rows_and_iso(), test_bad_v7_id_flagged(), test_carried_ids_exempt_from_v7_pattern() (+6 more)

### Community 57 - "validate_golden_v7"
Cohesion: 0.49
Nodes (10): run_eval(), _pipeline(), Offline harness tests for v7 metrics: as_of passthrough, must_not_cite, chunk-le, _row(), test_as_of_is_passed_to_pipeline(), test_chunk_metrics_computed_for_span_rows(), test_gate_is_none_when_nothing_adjudicated(), test_gate_subreport_covers_only_adjudicated() (+2 more)

### Community 58 - "bootstrap_ci"
Cohesion: 0.18
Nodes (10): ADOPTED gate (eval_gate round 3): deterministic groundedness signal —     max co, Max cosine(query, doc subject line) over contexts — the primary         gate sig, Max cosine(query, section heading) over contexts — the second tier., SubjectSimJudge, subject_sim == threshold (0.42) passes the gate (>= comparison)., section_score == section_threshold (0.60) passes via second tier., test_section_score_exactly_at_threshold_passes(), test_subject_sim_exactly_at_threshold_passes() (+2 more)

### Community 60 - "reg_display_name"
Cohesion: 0.09
Nodes (23): main(), mrr(), ndcg_at_k(), Sweep RRF k_const values on the golden set. No index rebuild needed., recall_at_k(), expand_query(), Query-side lexical expansion for BM25 (intervention #2, glossary variant).  SEBI, Append statutory synonyms for lay tokens present in `query`.      Deterministic (+15 more)

### Community 61 - "main"
Cohesion: 0.18
Nodes (10): HydeExpander, HyDE (Hypothetical Document Embeddings): query -> statutory passage.  Part B of, _chunk(), _rank(), HyDE expander (Part B): query -> hypothetical statutory passage.  Offline only —, test_generation_error_returns_empty(), test_hyde_leg_improves_paraphrase_gap_rank(), test_output_truncated_to_max_chars() (+2 more)

### Community 62 - "sweep_rrf_k.py"
Cohesion: 0.26
Nodes (5): paired_delta(), Compare run `b` against run `a` on their shared queries.      Returns mean_b - m, Randomization p-values use the (count+1)/(n+1) estimator, so a         p-value o, One query flipping out of 56 is exactly the iv9-style verdict: the         rando, TestPairedDelta

### Community 63 - "test_expand.py"
Cohesion: 0.14
Nodes (11): Regression coverage for the ZeroGPU-hardware workaround in app.py.  Background:, Inject a fake `spaces` module so app.py's `import spaces` succeeds     offline,, Static guard: if `import spaces` or the `@spaces.GPU` decorator is     ever remo, It must stay dead code: calling it would request a real ZeroGPU     allocation (, The functions actually on the request path (get_pipeline,     run_query_stream), `hardware:` in README-spaces.md is not a documented Spaces config key     (only, stub_spaces_module(), test_app_imports_spaces_and_declares_gpu_function() (+3 more)

### Community 64 - "test_hyde.py"
Cohesion: 0.32
Nodes (5): measure_parsing_latency(), Path, Measure PDF ingestion throughput (chars/sec, ms/PDF).      Samples 20 PDFs strat, Test with a dummy PDF file — should not crash., TestParsingLatency

### Community 65 - "stats.py"
Cohesion: 0.18
Nodes (9): The eval stack's generator choice must be one shared decision.  `derive_threshol, Uses an injected loader so the test stays offline., Silently falling back to the stub would derive floors under semantics     the ca, Must assert the factory is CALLED, not merely imported.      Verified 2026-08-12, A factory both call is not enough - they must pass the same setting,     or the, test_both_eval_scripts_read_the_same_setting(), test_eval_scripts_use_the_shared_factory(), test_mlx_kind_builds_the_production_generator() (+1 more)

### Community 66 - "test_app_zerogpu.py"
Cohesion: 0.18
Nodes (8): qwen3_rerank_prompt(), Qwen3MLXReranker, Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only     (D2, Offline tests for the Qwen3 MLX reranker (F2, ADR-001) — prompt format and reran, Bypass __init__ (no mlx); score by keyword overlap to test ordering., _StubQwen, test_prompt_format_matches_model_card(), test_rerank_orders_by_score_and_truncates()

### Community 67 - "eval_generator_for"
Cohesion: 0.24
Nodes (4): clopper_pearson_ci(), Clopper-Pearson exact interval for a binomial proportion.      Use this for stri, The reason for the switch. On 9/10 the percentile bootstrap returns         [0.7, TestClopperPearson

### Community 68 - "test_ingest_refs.py"
Cohesion: 0.22
Nodes (11): main(), Path, Push dist/datasets to the live HF Hub dataset repo (default: opnsrcntrbtrian/seb, (local_path, path_in_repo) pairs; SystemExit if anything is missing., upload_plan(), _fake_dist(), Path, Offline tests for the HF dataset push script (no network). (+3 more)

### Community 69 - "MeasureResult"
Cohesion: 0.27
Nodes (10): main(), parse_last_amended(), parse_listing(), Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY)., (year, url, title, short_name, last_amended) per listing row, in order., ISO date of the last amendment, or None when the title carries none., The bracketed short name, e.g. 'Mutual Funds'.      Takes the LAST bracket group, _record() (+2 more)

### Community 70 - "Qwen3MLXReranker"
Cohesion: 0.38
Nodes (4): mrr(), Minimal retrieval metrics (subset of docs/project_context.md section 7).  Recall, recall_at_k(), Automated metric collection for the SEBI Circular RAG pipeline.  Six on-demand m

### Community 71 - "clopper_pearson_ci"
Cohesion: 0.24
Nodes (7): measure_supersession_precision(), Measure fraction of detected supersession edges that are genuine.      Samples c, Verify a supersession edge by cross-referencing corpus records.      Returns "tr, _verify_supersession_edge(), Two circulars where A supersedes B, dates consistent, mutual reference., Circulars with no supersession text — should get zero precision edges., TestSupersessionPrecision

### Community 72 - "ui.py"
Cohesion: 0.23
Nodes (9): _edges(), Sampling + scoring for the regulation-edge precision audit., A tier with only 2 edges must not cap the sample at 6., test_sample_covers_every_evidence_tier(), test_sample_has_no_duplicates(), test_sample_is_deterministic_for_a_fixed_seed(), test_sample_size_is_respected(), test_sample_smaller_than_requested_returns_everything() (+1 more)

### Community 73 - "adjudicate_draft.py"
Cohesion: 0.10
Nodes (23): Pattern, _iso_date(), _labeled_date(), parse_meta(), _primary_number(), _subject(), _make_pdf(), Validate the local PDF ingestion path with a synthetic circular PDF. (+15 more)

### Community 74 - "write_run_doc"
Cohesion: 0.25
Nodes (5): BootstrapCI, PairedResult, Uncertainty quantification for benchmark runs.  The golden set is n=56 answerabl, True when the randomization test rejects at 1 - confidence AND the         paire, Uncertainty quantification for benchmark runs (bootstrap CIs + paired tests).

### Community 75 - "test_golden_v7_pool.py"
Cohesion: 0.19
Nodes (15): apply(), Applies each row's `(decision, new_governing_spans)` from `decisions`     (keyed, _min_agreement_fixture(), Offline tests for golden-v7 agreement/promotion (spec 2026-07-23 sec 7): Cohen's, _same_provision_fixture(), test_apply_does_not_mutate_input_rows(), test_apply_flip_promote_rebuilds_spans_and_label_source(), test_apply_promote_sets_adjudicated_only() (+7 more)

### Community 76 - "test_push_datasets.py"
Cohesion: 0.39
Nodes (8): _chunk(), Offline tests for the ADR-002 certainty architecture: abstention reasons, confid, test_advisory_draft_on_gate_failure_only_when_requested(), test_certainty_capped_medium_without_gate(), test_certainty_high_when_subject_sim_strong_and_faithful(), test_no_context_reason_when_top_k_zero(), test_score_floor_reason(), test_subject_gate_reason_and_subject_sim_recorded()

### Community 77 - "test_certainty.py"
Cohesion: 0.35
Nodes (4): BaseHTTPRequestHandler, Handler, run_script(), smoketest()

### Community 78 - "gwet_ac1"
Cohesion: 0.23
Nodes (12): adjudicate_draft(), _current_model(), _extract_text(), main(), _post_local(), Adjudicate draft rows using Qwen via oMLX.  Reads draft rows from golden_v7.json, Extract text from oMLX chat completion response., Run blind protocol over draft rows. (+4 more)

### Community 79 - "test_audit_reg_edges.py"
Cohesion: 0.38
Nodes (6): main(), _pool(), Probe: does query-side reformulation lift the CE score on the 4 CE_MISMATCH rows, Return (ce_top, best relevant score, chunk_id of argmax)., Top-8 pool plus every relevant chunk, de-duplicated on chunk_id., _score()

### Community 80 - "test_spaces.py"
Cohesion: 0.24
Nodes (12): build_report(), Assemble the persisted as-of run artifact.      Pipeline accuracy is the headlin, Aggregate case results with an exact confidence interval.      Pure function of, summarize(), Shape of the persisted as-of run artifact., Pooling a unit regression with an end-to-end metric is not a valid     measureme, The headline number must be the 10 pipeline cases alone — the whole     point of, _results() (+4 more)

### Community 81 - "test_trec_parity.py"
Cohesion: 0.38
Nodes (6): main(), _plausible(), Path, Validate corpus invariants after any ingest/backfill/repair.  Checks (per docs/s, Every record's text must match the PDF its provenance names.      Slow (re-extra, validate_deep()

### Community 82 - "test_repair_corpus_text.py"
Cohesion: 0.40
Nodes (4): main(), Dry-run audit of every circular_number renumber.py would change, with the docume, _header(), Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars.

### Community 83 - "resolve_chunk_spans"
Cohesion: 0.29
Nodes (9): first_answer_rank(), first_gold_rank(), heading_only(), main(), Trace each retrieval failure backwards through the pipeline (throwaway).  Checkl, # NOTE: metadata_filter_loss cannot be auto-detected here (no, Degenerate chunk heuristic: short and no sentence-final punctuation     (the nom, Rank of the first chunk that actually carries the answer text. (+1 more)

### Community 84 - "Handler"
Cohesion: 0.26
Nodes (10): _emit(), main(), Path, Precision audit for circular -> regulation edges (spec 2026-07-23 §7).  Emits a, Up to `n` edges, spread as evenly as possible across evidence tiers.      Tiers, Clopper-Pearson interval over hand-labelled edge correctness., score(), _score_file() (+2 more)

### Community 85 - "audit_reg_edges.py"
Cohesion: 0.18
Nodes (11): _confirms_claude(), _provision_agree(), Symmetric provision-level agreement between two governing labels, using     the, Does this external vote confirm claude's label, at PROVISION level?      Amendme, _norm_ws(), Different chunk copies of the same quoted provision agree at provision     level, test_provision_agree_both_empty_is_true(), test_provision_agree_containment_either_direction() (+3 more)

### Community 86 - "remap_doc_ids.py"
Cohesion: 0.22
Nodes (10): adjudicate(), _parse_error_ids(), Path, Runs the blind protocol over every id in `ids`, calling `post(prompt)     -> str, Scans the per-row cache for `ids` and returns the ones flagged     parse_error:, A garbled reply to an abstain-protocol (YES/NO) prompt is distinct     from a we, Defensive: an id that was never adjudicated (no cache file at all)     is not re, test_adjudicate_marks_parse_error_for_garbled_abstain_protocol_reply() (+2 more)

### Community 87 - "build_spaces_pipeline"
Cohesion: 0.67
Nodes (3): fetch_manifest(), main(), Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.  Usage:

### Community 88 - "build_report"
Cohesion: 0.31
Nodes (7): End-to-end driver test on a temporary corpus (no network)., _setup(), test_driver_appends_repealed_stub_to_the_regulations_file(), test_driver_is_idempotent(), test_driver_preserves_unrelated_circular_fields(), test_driver_writes_edges_and_annotates(), test_driver_writes_the_unresolved_report()

### Community 89 - "trace_failure.py"
Cohesion: 0.27
Nodes (8): _canary_jscode(), _ops_timeout(), The eval canary must fit its timeout and alert on real regressions.  Measured 20, n8n gives up first if its budget is smaller, so the ops timeout is     never rea, A threshold above the healthy value fires every run. citation_precision     was, test_alert_thresholds_sit_below_measured_baselines(), test_n8n_timeout_not_tighter_than_the_ops_budget(), test_ops_timeout_fits_the_measured_runtime()

### Community 90 - "_provision_agree"
Cohesion: 0.28
Nodes (5): main(), metrics_to_markdown(), Format results as a markdown table., Unit tests for sebi_rag.measure — automated metric collection., TestCLI

### Community 91 - "adjudicate"
Cohesion: 0.15
Nodes (14): auroc(), best_threshold(), evaluate(), main(), F2 (ADR-001): benchmark rerankers on golden_v5 with cluster-separation metrics., P(pos_score > neg_score); ties count half. pos = answerable top-scores,     neg, Threshold maximising abstention accuracy: answer if score >= thr.     Returns (t, contexts_for() (+6 more)

### Community 92 - "read_trec_run"
Cohesion: 0.67
Nodes (3): faithfulness(), Check that every circular id the answer cites (in square brackets) was     actua, test_faithfulness_scoring()

### Community 94 - "test_build_reg_edges.py"
Cohesion: 0.28
Nodes (8): injection_scan(), Return the list of matched instruction-like patterns (empty = clean)., _chunk(), Offline tests for F4 prompt-injection hardening (ADR-001)., test_grounded_prompt_delimits_sources_and_states_data_rule(), test_injection_scan_clean_on_real_legal_text(), test_injection_scan_flags_known_patterns(), test_to_record_carries_injection_flags()

### Community 95 - "test_canary_generator.py"
Cohesion: 0.24
Nodes (6): measure_context_precision(), MeasureReport, MeasureResult, Fraction of top-k chunks from relevant circulars.      Unlike recall@k (which is, TestContextPrecision, TestDataClasses

### Community 96 - "_rejoin_split"
Cohesion: 0.33
Nodes (9): build_regulatory_index(), Per-circular regulatory-basis lookup for the query/citation layer.      Read-onl, _icirc(), test_index_dangling_reg_id_falls_back(), test_index_happy_path_resolves_successor_object(), test_index_missing_basis_fields_default(), test_index_primary_is_unknown_but_a_repealed_reg_is_present(), test_index_repealed_with_missing_successor_record() (+1 more)

### Community 98 - "test_injection.py"
Cohesion: 0.22
Nodes (5): bench_retrieval must emit valid TREC alongside the legacy runfile., run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so     every, iv9/iv10 build a headered index beside data/index. Without an index     override, test_bench_retrieval_can_bench_an_alternate_index(), test_bench_retrieval_can_measure_the_reranked_order()

### Community 100 - "faithfulness"
Cohesion: 0.25
Nodes (7): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, SEBI_RAG_EVAL_GENERATOR, canary.sh script, TOKENIZERS_PARALLELISM

### Community 101 - "test_bench_retrieval_artifacts.py"
Cohesion: 0.27
Nodes (10): _body(), Winning chunk ids (from a flip_promote decision) -> {doc, quote}     spans, look, _resolve_governing_spans(), _pool(), Amendment 2026-07-26 (user-approved): the promotion unit is the     PROVISION, n, test_decide_same_provision_other_chunk_promotes_with_pool(), test_resolve_governing_spans_multiple_ids_dedupes_and_preserves_order(), test_resolve_governing_spans_raises_on_chunk_not_in_pool() (+2 more)

### Community 102 - "canary.sh"
Cohesion: 0.16
Nodes (10): Parse a runfile written by `write_trec_run` back into {qid: [(doc, score)]}., read_trec_run(), write_trec_run(), _chunks(), _golden(), test_beir_export_and_qrels_shape(), test_golden_v6_schema_guardrails(), test_run_metadata_has_reproducibility_fields() (+2 more)

### Community 103 - "_resolve_governing_spans"
Cohesion: 0.25
Nodes (8): CIR/MRD/DP/19/2010, List of Circulars, List of Communications, MRD/DoP/Dep/Cir-29/2004, MRD/DoP/MAS – OW/16723/2010, Securities and Exchange Board of India, SEBI/MRD/SE/DEP/Cir-4/2005, SMDRP/NSDL/3055/1998

### Community 104 - "relabel_repooled.py"
Cohesion: 0.43
Nodes (6): _body(), main(), _norm(), pick(), Label the 7 rows re-pooled after the assemble_pool fix (2026-07-25 remediation T, (candidate, quote) pairs for this row: the answer_contains carrier     first, th

### Community 105 - "pipeline"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, run.sh script, TOKENIZERS_PARALLELISM

### Community 106 - ".encode"
Cohesion: 0.26
Nodes (11): _add_months(), check_robots(), main(), month_window(), date, Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving their d, [first day of month-pad, last day of month+pad] around the stem's epoch., Map each stem to (current pdf_url, detail_url) via listing sweeps. (+3 more)

### Community 107 - "_s_mc_no"
Cohesion: 0.52
Nodes (6): dataset_quality(), load_index_chunks(), main(), Path, Export benchmark artifacts for retrieval/RAG/data-quality evaluation.  Outputs:, write_card()

### Community 109 - "test_incremental_index.py"
Cohesion: 0.18
Nodes (11): carry_v6_rows(), main(), Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).  C, _fmt(), main(), Path, Re-score archived benchmark runs with bootstrap CIs and paired significance.  Re, score_run() (+3 more)

### Community 110 - "_HallucinatingGenerator"
Cohesion: 0.29
Nodes (6): HF_HUB_DISABLE_XET, OMP_NUM_THREADS, PYTHONPATH, PYTORCH_ENABLE_MPS_FALLBACK, refresh.sh script, TOKENIZERS_PARALLELISM

### Community 111 - "run.sh"
Cohesion: 0.43
Nodes (3): measure_mrr(), Mean reciprocal rank at circular level.      For each query, RR = 1/rank of firs, TestMRR

### Community 112 - "test_annotation_adds_no_circular_meta_field"
Cohesion: 0.43
Nodes (3): measure_retrieval_recall(), Standard recall@k at circular level, excluding abstain items., TestRetrievalRecall

### Community 113 - ".grounded"
Cohesion: 0.43
Nodes (3): measure_temporal_accuracy(), Measure fraction of as_of queries returning correct pre-supersession     circula, TestTemporalAccuracy

### Community 114 - "seed_v7.py"
Cohesion: 0.13
Nodes (16): _cited(), Circular -> regulation edges and corpus annotation (spec 2026-07-23 §3.3-§3.7)., Yield (circular, Citation) for every citation occurrence in the corpus., derive_regulatory_basis(), _jaccard(), Regulation identity + name resolution (spec 2026-07-23 §3.2, §3.6).  Regulations, Regulatory-basis status of one circular from its resolved regulations.      `unk, Deterministic, stable identity slug. This is the edge target and join key. (+8 more)

### Community 117 - "api.py"
Cohesion: 0.29
Nodes (5): build_index must be able to target a scratch index directory.  The iv9/iv10 head, A --out flag that is parsed but ignored is worse than none: it reads     as safe, lineage.json lands next to the index it describes; writing it into     data/inde, test_build_index_saves_to_the_resolved_out_dir_not_the_constant(), test_lineage_follows_the_out_dir()

### Community 118 - "test_every_alias_target_is_in_force_or_has_a_succession_entry"
Cohesion: 0.60
Nodes (5): load_jsonl(), main(), Path, Build circular -> regulation edges and annotate the corpus (offline).  No networ, write_jsonl()

### Community 119 - "sebi-rag"
Cohesion: 0.25
Nodes (8): cohen_kappa(), Categorical Cohen's kappa over paired labels (row-aligned). Each raw     element, The kappa base-rate paradox: one label dominates, raw agreement is high,     yet, test_cohen_kappa_both_constant_and_identical_is_one(), test_cohen_kappa_empty_input_is_one(), test_cohen_kappa_identical_lists_is_one(), test_cohen_kappa_independent_looking_lists_is_low(), test_gwet_ac1_exceeds_kappa_on_skewed_high_agreement()

### Community 120 - "run_all_metrics"
Cohesion: 0.29
Nodes (4): Run all (or specified) metrics sequentially., run_all_metrics(), Empty metrics list is falsy → defaults to ALL_METRICS., TestRegistry

### Community 121 - "test_app_asof.py"
Cohesion: 0.40
Nodes (4): OMP_NUM_THREADS, PYTHONPATH, autoresearch.sh script, TOKENIZERS_PARALLELISM

### Community 125 - "Overall Evaluation Summary"
Cohesion: 0.67
Nodes (4): Failure: asof-p2, Overall Evaluation Summary, Pipeline Evaluation Results, Selector Evaluation Results

### Community 127 - "TestPerQueryRecall"
Cohesion: 0.50
Nodes (4): Rejoin numbers split by a space around a slash, e.g. "CIR/ 2025/104",     "HO/ (, References split across tokens: merge up to 4 tokens after the first     HO/CIR/, _rejoin_split(), _s_anchor_merge()

### Community 128 - "MLXGenerator"
Cohesion: 0.67
Nodes (3): Golden v7 Human Packet, SEBI Circular HO/19/34/14(5)2025-AFD-POD2/I/2703/2026, SEBI Circular SEBI/HO/MRD/TPD/CIR/P/2025/122

## Knowledge Gaps
- **48 isolated node(s):** `measure.sh script`, `autoresearch.sh script`, `PYTHONPATH`, `TOKENIZERS_PARALLELISM`, `OMP_NUM_THREADS` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chunk` connect `benchmark.py` to `telemetry_engine.py`, `HybridRetriever`, `SpladeIndex`, `backfill_escalations.py`, `test_api.py`, `build_lineage`, `test_regulations.py`, `extract_citations`, `test_dataset_cards.py`, `test_ui.py`, `extract_misses.py`, `scrape_sebi.py`, `agreement.py`, `ingest_pdf.py`, `test_scrape_sebi.py`, `measure_supersession_precision`, `bootstrap_ci`, `reg_display_name`, `main`, `test_app_zerogpu.py`, `test_push_datasets.py`, `adjudicate`, `test_build_reg_edges.py`, `canary.sh`, `_s_mc_no`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `RAGPipeline` connect `test_api.py` to `telemetry_engine.py`, `RAGPipeline`, `test_golden_v7_gate.py`, `test_ui.py`, `benchmark.py`, `scrape_sebi.py`, `agreement.py`, `ingest_pdf.py`, `test_scrape_sebi.py`, `validate_golden_v7`, `test_hyde.py`, `Qwen3MLXReranker`, `clopper_pearson_ci`, `adjudicate`, `test_canary_generator.py`, `run.sh`, `test_annotation_adds_no_circular_meta_field`, `.grounded`, `run_all_metrics`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `main()` connect `test_api.py` to `answer_with_abstention`, `telemetry_engine.py`, `agreement.py`, `ingest_pdf.py`, `canary.sh`, `HybridRetriever`, `publish_hf.py`, `test_incremental_index.py`, `test_scrape_sebi.py`, `main`, `scrape_sebi.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 48 inferred relationships involving `Chunk` (e.g. with `NLIAttributionScorer` and `BenchmarkIssue`) actually correct?**
  _`Chunk` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `RAGPipeline` (e.g. with `run()` and `main()`) actually correct?**
  _`RAGPipeline` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `ExtractiveStubGenerator` (e.g. with `get_pipeline()` and `run()`) actually correct?**
  _`ExtractiveStubGenerator` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `HashEmbedder` (e.g. with `smoke_pipeline()` and `_CannedGenerator`) actually correct?**
  _`HashEmbedder` has 43 INFERRED edges - model-reasoned connections that need verification._