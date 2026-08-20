# Project Context — SEBI Circular RAG

> Authoritative architecture record. Consult before requesting any information.
> Governed by `SEBI_RAG_Claude_Desktop_Engineering_Handbook.md`. Last updated: 2026-08-16 (corpus growth to 728 circulars / 78,585 chunks; gate floors re-derived).

## 1. Purpose

Production-grade, local-first RAG over Indian SEBI Circulars. Deterministic engineering, reproducibility, minimal tokens, Apple Silicon performance, legal-domain factual accuracy. Official SEBI publications authoritative; insufficient evidence → **"I don't know based on the available evidence."**

## 2. Hardware

macOS: Apple M4 Pro, 14-core CPU (10P+4E), 48 GB unified memory, 1 TB SSD

## 3. Operating System

Latest stable macOS; local-first AI stack; no external GPU; allowlisted network only for corpus fetch + dependency install.


## 4. Target Architecture

### Pipeline stages
```yaml
stages:
  - name: ingestion
    script: ingest_pdf.py
    desc: Fetch SEBI circulars; record provenance (source URL, fetch date, checksum)
    details:
      - PDF text extraction (OCR fallback for scanned PDFs)
      - Metadata parsing: circular number, dates, subject, department, version_lineage
      - F4 injection scanning (OWASP LLM01): flags instruction-like content for review
  - name: segmentation_mandatory
    desc: Hierarchical chunking — document → section → paragraph, ≈1200 chars, ≈150-char overlap
    details:
      - PDF-aware fallback: blank-line → single-newline → sentence → hard-window (no mid-clause splits)
      - Stable retrieval ID per chunk for precise citation
      - Wrapped-clause folding: absorbs hard-wrapped continuation lines after headings
      - Intervention #1: prepends governing clause for numbered sub-clauses
      - F1 contextual enrichment: prepends circular_no + subject to every chunk
    CircularMeta fields: [circular_number, issue_date, effective_date, subject, issuing_department, supersession_status (in_force|superseded|amended), amendment_history, version_lineage, circular_type, validity_status (current|superseded|partially_superseded|unknown), superseded_by_id]
  - name: metadata_extraction_mandatory
    desc: Per document/chunk — circular number, issue date, effective date, subject, issuing department, supersession status, amendment history, version lineage
    details:
      - Cross-document supersession: `lineage.py` (P2) — references classified supersedes/amends/cites from circular text; master-circular re-issues detected by normalised title (newest supersedes older)
      - Produces lineage graph + in_force|superseded|amended status; superseded chunks demoted in rerank, flagged at retrieval
      - Regulation-level annotation: `reg_lineage.py` builds Circular→regulation edges; `regulations.py` resolves regulation identity + alias table
      - `CitationMeta.regulations` + `regulatory_basis_status` (current|repealed_basis|mixed|unknown) surfaced per-citation in API
      - In-text advisory note appended when cited circular rests on repealed regulation
  - name: indexing
    desc: Dense FAISS (IndexFlatIP, in-memory) over bge-m3 baseline embeddings; Sparse BM25 lexical index (bm25s)
    details:
      - Versioned via `manifest.json` with per-document checksums (supports incremental indexing — F3: encode only new/changed documents, reuse cached embedding rows)
  - name: stage1_retrieval_mandatory_hybrid
    desc: Dense (FAISS) + sparse (BM25) sequential, fused by RRF → candidate pool ~50–100
    details:
      - Optional SPLADE learned-sparse third leg (eval-only, off by default)
      - Optional HyDE hypothetical-passage third dense leg (intervention #5, off by default)
      - Query expansion (statutory-synonym expansion) applied to sparse leg only — BM25 misses lay vocabulary; dense keeps raw query
  - name: stage2_reranking_mandatory
    desc: Production: cross-encoder reranker (bge-reranker-v2-m3 via sentence-transformers CrossEncoder on MPS)
    details:
      - Benchmark candidate: Qwen3-Reranker via MLX (causal-LM, P("yes") vs P("no"))
      - Test fallback: deterministic LexicalReranker (query-coverage score)
      - Output → top-k context
  - name: generation
    desc: Local LLM. Default MLX-LM Qwen2.5-1.5B-Instruct-4bit (Apple-Silicon native). Ollama optional via SEBI_RAG_GENERATOR (deterministic: temperature 0, fixed seed)
    details:
      - Abstention gate — TWO SEPARATE SIGNALS ON TWO SCALES, routinely confused: score floor `abstain_threshold = 0.05` on the cross-encoder `rerank_top` (`config.toml [service]`), and the groundedness gate `subject_sim >= 0.42` / `section_sim >= 0.60` (SubjectSimJudge). Below either → abstain ("I don't know based on the available evidence."); never generate unsupported legal conclusions. ⚠️ 0.4 is the `RAGPipeline` dataclass default (`pipeline.py:41`), NOT production — `Settings.load()` supplies 0.05. Comparing one gate against the other's threshold produced a misclassified diagnostic on 2026-08-18; see `.claude/rules/refusal-criteria.md`.
      - ADR-002 certainty architecture: SubjectSimJudge (two-tier groundedness — max cosine(query, subject line) threshold 0.42, section-heading tier at 0.60); MLXJudge (deterministic groundedness judge on MLX, modes: identify/provisions)
      - Confidence bands: high (subject_sim ≥ 0.65 + faithfulness 1.0), medium (passed all gates), low (abstained)
      - Advisory mode: `advisory=True` returns clearly-labelled low-confidence draft answer on gate failure (never authoritative)
      - `as_of` date-scoped queries: score against law as of a date (circular demoted only if superseding circular issued by that date)
  - name: evaluation_mandatory
    desc: See §7
```

### Pipeline flow
`Query → [Dense ANN (FAISS IndexFlatIP, bge-m3) | Sparse lexical (bm25s)] → RRF → pool(50-100) → cross-encoder (bge-reranker-v2-m3) → top-k → select_citations() [opt-in, margin-based answer-relevance filter] → LLM → answer + citations`

Gate: `Abstain if below threshold (~0.4) | Advisory mode: low-confidence draft on gate failure (advisory=True)`

Date-scoped: `as_of: demote only if superseded by as_of date`

Optional legs: `SPLADE / HyDE (eval-only, off by default)`

## 5. Dependency Versions

```yaml
deps:
  xcode_clt: "* (pin @ validation)"
  homebrew: "* (pin @ validation)"
  python: "3.12.13 (.venv; system default 3.14.6 unused — no mlx-lm wheel)"
  uv: "0.12.4 (Homebrew)"
  git: "2.55.0 (Homebrew; Apple Git 2.50.1 also present)"
  mlx: "0.31.3 / MLX-LM 0.31.3 (validated in .venv)"
  ollama: "0.19+ (MLX backend on Apple Silicon) (* pin @ validation)"
  pytorch_mps: "2.13.0 (required: baseline runtime for bge-m3 embeddings + cross-encoder reranker via sentence-transformers / FlagEmbedding)"
  sentence_transformers: "5.6.0"
  flag_embedding: "1.4.0"
  faiss: "faiss-cpu 1.14.3 (Apple Silicon arm64)"
  hf_xet: "1.5.1 (Xet transfer; large weights). Note: bge-m3 weights are Xet-backed; if downloads stall, set HF_HUB_DISABLE_XET=1 and ignore onnx/pytorch_model.bin duplicates as needed."
  embedding_model: "bge-m3 (baseline, runs on PyTorch MPS; dense 1024 + sparse + ColBERT validated)"
  reranker: "bge-reranker-v2-m3 via sentence-transformers CrossEncoder on MPS (validated). NOTE: FlagEmbedding 1.4.0 FlagReranker is incompatible with transformers 5.12.1 (prepare_for_model removed) — use CrossEncoder, not FlagReranker."
  lexical_index: "bm25s 0.3.9 (* select @ retrieval stage)"
```

## 6. Validation Sequence

Canonical source: `docs/project_context.md` §6. Mirrored in `CLAUDE.md` and `AGENTS.md`. One step at a time; never validate later stage until current passes. Any FAIL is blocker — stop, record root cause + exact commands + verification command in `docs/status.md`, resolve before proceeding.

1. Hardware & macOS → 2. Xcode CLT → 3. Homebrew → 4. Python + uv → 5. Git → 6. MLX → 7. Ollama → 8. PyTorch MPS (only if required) → 9. FAISS → 10. Embeddings → 11. Repository tests → 12. End-to-end RAG

## 7. Performance Goals & Evaluation

### 7.1 Mandatory Evaluation Metrics

| Category | Metric | Where Measured |
|---|---|---|
| **Retrieval** | Recall@k, MRR, nDCG@k | `src/sebi_rag/eval.py` (recall_at_k, mrr, ndcg_at_k); `eval_harness.py` (chunk-level recall@k, chunk MRR) |
| **Citation** | Citation precision, citation recall | `eval_harness.py`, `golden_v7/score.py` |
| **Groundedness** | Faithfulness (every bracketed citation id in answer appears in retrieved context), groundedness proxy (answer_contains hit rate on answered items) | `eval_harness.py` |
| **Behaviour** | Abstention accuracy, must_not_cite violation rate | `eval_harness.py`, `golden_v7/score.py` |
| **System** | Latency (ms per query), index build time, Apple Silicon memory usage | `eval_harness.py` (avg_latency_s), `benchmark.py` (run metadata) |
| **Safety** | Injection flag count (8 pattern classes at ingest) | `eval_json.py` (live corpus scan) |
| **Certainty** | Confidence bands (high | medium | low), abstention_reason enum (no_context | score_floor | subject_gate) | `generate.py` (SubjectSimJudge), `pipeline.py` |

### 7.2 Performance Rule

Optimise only validated stages; recommend changes expected to yield ≥10% measurable benefit. Quantization baseline: 4-bit group-size 64, with embedding/projection layers at 6–8 bit.

### 7.3 Calibrated Retrieval Parameters

Real stack calibration over 728 circulars / 78,585 chunks (golden_v7). ⚠️ The live index is **730 circulars / 78,630 chunks** (`eval/runs/full-eval-2026-08-19.json`); these parameters have not been re-calibrated against it.

```yaml
params:
  top_k: 10 (default, configurable via SEBI_RAG_TOP_K)
  abstain_threshold: 0.05 (cross-encoder; configurable via SEBI_RAG_ABSTAIN_THRESHOLD)
  subject_sim_threshold: 0.42 (two-tier: subject_sim >= 0.42 OR section_sim >= 0.60)
  section_threshold: 0.60 (configurable via SEBI_RAG_SECT_THRESHOLD)
index_path: data/index/ (reload 0.34s). Re-run after corpus growth.
thresholds_are_model_dependent: |
  abstain_threshold is a raw cross-encoder score, so it is meaningful ONLY for
  bge-reranker-v2-m3. subject_sim / section_sim are cosines in bge-m3 embedding space.
  Swapping either model changes the SCALE these numbers live on, not just the optimum —
  0.05 does not transfer to a different reranker. Re-calibrate via scripts/calibrate.py
  before carrying any of these across a model change.
```

### 7.4 Golden-Set Architecture

```yaml
reporting_set: eval/golden/golden_v7.jsonl (n=260, adjudicated_n=260)
strata: [title_direct 40, body_paraphrase 60, numeric_table 30, lineage_supersession 40, multi_hop 20, repealed_basis 20, hard_negative 40, far_negative 10]
abstain_rows: 41 | as_of_dated_rows: 15
frozen_fallback: golden_v5.jsonl (n=56) — used when v7 gate not armed
golden_v6: golden_v6.jsonl (n=56) — intermediate set
gate: eval/golden/gate_v7.json (armed at adjudicated_n=260) — AUTHORITATIVE; read the JSON, not this prose
  floors (armed under B' selective citations, margin 0.35, derived 2026-08-13 MLX generator): recall_at_k=0.906, context_recall=0.874, ndcg_at_10=0.6512, citation_recall=0.8169, abstention_accuracy=0.9412, citation_precision=0.1577
  floors_are_model_dependent: |
    These floors are NOT properties of the corpus or the golden set. They were derived under a
    specific stack: bge-m3 embedder + bge-reranker-v2-m3 cross-encoder + B' margin 0.35 +
    MLX generator Qwen2.5-1.5B-Instruct-4bit. Three of the six (citation_recall,
    citation_precision, abstention_accuracy) are generation-dependent and WILL move if the
    generator changes; the 2026-08-12 stub->MLX re-derivation moved citation_recall 0.7233 ->
    0.8169 and citation_precision 0.1896 -> 0.1577 on an unchanged corpus.
    RULE: changing the generator, embedder, reranker, or B' margin INVALIDATES these floors.
    Re-derive via scripts/golden_v7/derive_thresholds.py before comparing anything against them.
    A candidate model measured against floors derived under a different model is not a
    pass/fail result — it is a category error.
  ci_gates: v7 only when adjudicated_n >= 100
adjudication_pipeline: scripts/golden_v7/ (seed, mine_strata, build_pool, gate_select, local_adjudicate [Qwen3.6-35B-MLX], gemini_adjudicate [on hold], agreement, relabel_repooled, backfill_escalations, derive_thresholds, score)
```

### 7.5 Evaluation Infrastructure

| Script | Purpose |
|---|---|
| `scripts/eval_json.py` | Production-mirrored eval via RAGPipeline. ⚠️ **Runs the real MLX generator, not a stub** — `config.toml [service] eval_generator = "mlx"`, routed through `generate.eval_generator_for` so floors and measurements can never come from different generators. Floors were re-derived under MLX on 2026-08-12 precisely because stub-derived floors describe a system that does not run (the stub overstated B′ citation failures ~2×: 34 rows vs 19). (The module docstring, the origin of this error, was corrected 2026-08-20.) Golden-set resolution (v7 gate → v5 fallback); prints JSON for n8n |
| `src/sebi_rag/eval_harness.py` (module) | `run_eval()` → EvalReport (recall, MRR, nDCG, citation prec/rec, abstention acc, groundedness proxy, faithfulness, latency, chunk-level metrics) |
| `scripts/golden_v7/score.py` | Per-row scoring shared by eval_json.py and derive_thresholds.py; `vectors()` aggregates to metric vectors |
| `scripts/bench_retrieval.py` | Retrieval-only benchmark + TREC runfile export |
| `scripts/bench_rerankers.py` | Reranker benchmark (AUROC, cluster separation) |
| `scripts/bench_generators.py` | Generator benchmark (faithfulness, groundedness, latency) |
| `scripts/eval_gate.py` | Groundedness / subject-sim judge evaluation |
| `scripts/eval_asof.py` | As-of-date golden evaluation |
| `scripts/rescore_runs.py` | Re-score archived runs with bootstrap CIs + paired significance |
| `scripts/export_benchmark.py` | BEIR/TREC/RAG benchmark export |
| `scripts/export_datasets.py` | Dataset export (chunks, corpus, lineage, eval) |
| `scripts/calibrate.py` | Retrieval calibration sweep (RRF, top-k, threshold) |

### 7.6 Current Baseline Numbers (golden_v7, full set, n=260)

⚠️ **These are BASELINE observations under one specific generator, not properties of the system.**
Source of truth is the newest dated run in `eval/runs/`, not this block — it has drifted before.

```yaml
generator: mlx-community/Qwen2.5-1.5B-Instruct-4bit   # the arm these numbers describe
recall_at_k: 0.943 observed (floor 0.906)
context_recall: 0.916 observed (floor 0.874)
ndcg_at_10: 0.697 observed (floor 0.6512)
citation_recall: 0.881 observed (floor 0.8169)
abstention_accuracy: 0.981 observed (floor 0.9412)
citation_precision: 0.194 observed (floor 0.1577)
```

⚠️ **Three of these disagree with the newest recorded run** (`eval/runs/full-eval-2026-08-19.json`,
which post-dates the 2026-08-17 index rebuild): context_recall **0.906** (not 0.916),
citation_recall **0.872** (not 0.881), citation_precision **0.191** (not 0.194). recall_at_k,
ndcg_at_10 and abstention_accuracy agree. The three that differ are exactly the
generation-and-rerank-dependent ones. Do not cite this block as current until a fresh control run
resolves it — quote the dated run file instead.

### 7.7 Index Performance

```yaml
full_seed_build: ~507s (22,273 chunks at 209 circulars)
incremental_reindex: ~5s (no-op, all docs reused)
index_reload: 0.34s
disk_embeddings_npy: 307 MB (78,585 chunks); scales to ~2 GB at 500k chunks
```


## 8. Design Decisions

```yaml
design_decisions:
  D1:
    title: "Hybrid retrieval is mandatory"
    desc: FAISS (dense) + BM25 (sparse) + RRF form Stage-1. FAISS retained as dense engine, not replaced.
    amended: "2026-07-02 (ADR-001): LanceDB sanctioned benchmark candidate for dense store at >=100k-chunk scale; replacement only on >=10% evidence."
  D2:
    title: "bge-m3 is the baseline embedding model only"
    desc: Subject to benchmarking against Qwen-family embedder and one lightweight Apple Silicon model. Do not change baseline without benchmark evidence.
    amended: "2026-07-02 (ADR-001): Qwen3-Embedding-0.6B (embedder) and Qwen3-Reranker-0.6B/4B via MLX (reranker) are sanctioned benchmark candidates; D6 canonical-runtime rules apply."
    baseline_vs_candidate: |
      "Baseline" names the model currently instantiating a MANDATORY stage (D1 hybrid retrieval,
      D4 reranking) — it does not make that model architectural. The stage is fixed; the model
      is replaceable on >=10% evidence (D1 amendment). Any doc sentence that reads as though
      bge-m3 or bge-reranker-v2-m3 were themselves architecture is describing the current
      instantiation, not a constraint.
    candidates_added_2026-08-20:
      jina-reranker-v3:
        status: "candidate — NOT benchmarked here, no spec written"
        why: |
          Listwise "last but not late interaction" reranker (~0.6B): documents and query share one
          context window and are scored in a single pass. That makes it an INSTANTIATION of the
          roadmap's R4 (listwise/set-wise reranking), not a separate line item.
        caution: |
          Its attention is causal, so scores are ORDER-DEPENDENT — unlike Set-Encoder, which is
          permutation-invariant by construction. Any benchmark must fix and report input order,
          or it measures the ordering as much as the model.
        numbers: |
          arXiv 2509.25085 reports BEIR nDCG@10 ~61.94 vs bge-reranker-v2-m3 ~56.5 (~+5.4).
          PAPER-REPORTED, NOT MEASURED HERE — verify against the paper before quoting in a spec.
          An earlier internal handoff circulated "76.69 vs 67.69 (+9)" for this pair; that is
          WRONG and must not be propagated. On multilingual benchmarks the direction REVERSES
          (bge-reranker-v2-m3 ~69.32, Jina lower) — SEBI is English, so the candidate survives,
          but at roughly 60% of the margin that handoff claimed.
      voyage-3/4-large:
        status: "REJECTED as a candidate on architectural grounds — not on quality"
        why: |
          API-only proprietary service. This conflicts head-on with the project's first
          principle (local-first) and with D6 (one canonical LOCAL benchmark runtime), and it
          would send SEBI queries to a third party. Strong MTEB law/finance results do not
          override that. Reconsider only if the local-first constraint is deliberately relaxed
          by explicit decision, which has not happened.
  D3: "Sparse path = BM25 (bm25s 0.3.9 — NOT SPLADE, and not bge-m3's sparse head). bge-m3 supplies dense only for baseline; its sparse/ColBERT vectors deferred to avoid fusion double-counting. SPLADE exists only as an opt-in eval-only third leg (D13) and was rejected on confirmation; its index artifacts no longer exist on disk."
  D4: "Reranking is a mandatory production stage, not an implementation detail."
  D5: "Citation-grounded evaluation + abstention policy are architectural components, not optional add-ons."
  D7:
    title: "Embeddings + reranking run on PyTorch MPS"
    desc: sentence-transformers / FlagEmbedding baseline. Keeps bge-m3 dense+sparse+ColBERT heads on sanctioned runtime (D2), avoids hand-porting to MLX. MLX-native embedders remain D2 benchmark candidates only. PyTorch MPS stability to be re-confirmed at Step 10 under real reranker load. Generation stays on MLX-LM/Ollama (D6).
  D6: "One canonical benchmark runtime (MLX-LM or Ollama), with pinned model version, quantization, runtime params, and seeds. Alternative runtimes allowed for experimentation but must be tagged and never mixed into official benchmarks without documentation."
  D8:
    title: "Certainty architecture (ADR-002)"
    desc: Every response carries confidence block ({rerank_top, margin, subject_sim, section_sim}) and banded certainty (high | medium | low), never a probability.
    bands:
      high: "passed both gates AND subject_sim >= 0.65 AND faithfulness 1.0 (100% citation recall on golden_v5)"
      medium: "passed gates otherwise"
      low: "any gate failed (always on abstention)"
    abstention_reason_enum: [no_context, score_floor, subject_gate] — distinguishes client error, far-domain, near-domain ungrounded
    advisory_mode: "advisory=True: on score_floor/subject_gate with non-empty context, response additionally carries draft_answer prefixed LOW CONFIDENCE — not regulatory guidance… (never default, never produced for no_context)"
    as_of: "date-scoped queries: score against law as of a date (circular demoted only if superseding circular issued by that date)"
    groundedness_gate: "two-tier subject/section gate adopted (2026-07-02 ADR-002): grounded = subject_sim >= 0.42 OR section_sim >= 0.60"
    judge: "SubjectSimJudge (max cosine(query, subject line), threshold 0.42) OR section-heading tier (threshold 0.60). MLXJudge (deterministic groundedness judge on MLX, modes: identify/provisions) available but not default (scale-unstable). Faithfulness check: every cited circular id in square brackets must appear in retrieved context; unsupported citations flagged."
  D9: "Apple Neural Engine (ANE) declined (ADR-003). Pipeline stays on MLX (generation) and MPS/MLX (embeddings/reranker). ANE is energy-efficiency engine (~93+ tok/s vs ~9 tok/s on 8B model); throughput-oriented server RAG on plugged-in Apple Silicon does not benefit. Revisit only if battery life, thermal envelope, or always-on background inference becomes explicit goal."
  D10:
    title: "F1-F5 findings (ADR-001)"
    F1: "contextual chunk enrichment: prepend <circular_no> | <subject> | <section> to each chunk before embedding (criterion met: +23% citation precision, recall@10 held at 1.0)"
    F2: "Qwen3-Reranker MLX benchmark rejected (AUROC 0.799 vs baseline 0.812; baseline retained)"
    F3: "incremental indexing: checksum-keyed encode (embeddings.npy cache + per-doc manifest); delta-only encode, FAISS-Flat/BM25 rebuilt from cached matrix (deletion-safe vs HNSW)"
    F4: "prompt-injection hardening: 8 injection-pattern classes scanned at ingest (OWASP LLM01); <<<SOURCE>>> delimiters in prompts; timing-safe API key compare (secrets.compare_digest); localhost binding"
    F5: "golden-set circularity fix: held-out paraphrase queries + hard negatives (golden_v5/v6/v7 with human adjudication)"
    status: "All F1-F5 accepted and implemented"
  D11: "Wrapped-clause folding (Intervention #1). SEBI PDFs hard-wrap clause text; a non-heading paragraph right after a heading is usually its continuation. Absorb into recorded head unless head already terminated or capped. Additionally, numbered sub-clauses (4.1.1.2. …) are meaningless without their governing clause (4.1.1 On and from the date… the CRA shall:). Prepend nearest recorded ancestor heading to every chunk so both retrievers see context."
  D12: "Query expansion via statutory-synonym glossary (Intervention #2). SEBI circulars use statutory vocabulary (freeze, dematerialised, rescinded) where users ask in lay terms (block, electronic, replaced). Appending statutory synonyms to BM25 query closes vocabulary gap without touching index; dense leg keeps raw query. Deterministic and additive: original query always preserved as prefix. Entries grounded in eval/runs/ft-traces/buckets.md failure analysis."
  D13: "Optional third RRF legs (Interventions #5, iv9, iv11). HyDE (Part B): hypothetical statutory passage as additive third dense leg (opt-in, off by default, silent failure). SPLADE: learned-sparse third RRF leg (opt-in, eval-only, off by default). Contextual headers: one lay+statutory sentence per deep sub-clause/annex chunk (opt-in, off by default, silent failure). All three non-destructive — mandatory dense + BM25 + RRF path unchanged; enabling any third leg requires explicit configuration."
  D14: "Regulation-level annotation. Regulations are consolidated living documents (no circular_number, no issue_date, one current row each), keyed by deterministic reg_id slug. Three-stage resolution: exact token match, then hand-maintained REGULATION_ALIASES table (acronyms like PIT → prohibition-of-insider-trading), then Jaccard fuzzy match (threshold 0.8). regulatory_basis_status (current|repealed_basis|mixed|unknown) derived from resolved regulation statuses; CitationMeta.regulations surfaced per-citation in API. In-text advisory note appended when cited circular rests on repealed regulation."
  D16: "B' Selective Citations (post-hoc cross-encoder answer-relevance filter). `generate.py` `select_citations(answer_text, contexts, scorer, margin)` scores each context via `scorer.rerank(answer_text, contexts)` (sigmoid 0–1) and keeps those within `margin` of the top; always ≥1. Wired into `answer_with_abstention()` (opt-in via Settings.citation_scorer_enabled). `RAGPipeline` holds `citation_scorer` (reuses reranker instance) + `citation_margin`. `citation_precision` added to `_GATED_METRICS` in derive_thresholds.py alongside recall/citation_recall/abstention — protects both sides of the precision↔recall trade-off. Supersedes the inert Option A (prompt-bracket parsing, 100% no-op at Qwen-1.5B). **Status 2026-08-14: ARMED. All 3 builders (`build_default_pipeline`, `eval_json`, `derive_thresholds`) route through `generate.citation_scorer_for(enabled, reranker)` so eval==production (parity-gap fix e1f7859). Calibrated margin=0.35 (MLX-parallel sweep knee, 219 adjudicated answerable): citation_precision 0.192→0.202 mean (+5.4%), citation_recall 0.881→0.872. Gate re-derived under MLX generator (margin=0.35, 2026-08-13). ⚠️ This line previously quoted floors 0.8124 / 0.1571; the armed values in `eval/golden/gate_v7.json` (derived_at 2026-08-13T15:47:25) are **citation_recall 0.8169, citation_precision 0.1577**. Read the JSON, never this prose — stale floors propagating out of docs have already produced one wrong review finding. Verified end-to-end `floors_ok: true` (observed 0.881/0.192). Enabled via `config.toml citation_scorer_enabled=true` — gate now REQUIRES B' on to pass.**"
```


## 9. Engineering Constraints

- Deterministic, reproducible, token-minimal responses
- Apple Silicon first: prefer MLX / MLX-LM / Metal where appropriate
- Treat SEBI publications as primary legal authority; never fabricate citations or legal interpretations
- Validate one step at a time; any FAIL is blocker — stop until resolved and `docs/status.md` updated
- Review only supplied files; never infer contents of unseen files

## 10. Directory Structure (target)

```
SEBI circular RAG/
├── docs/ — project_context.md (this file), status.md, scraping_plan.md, n8n_automation_plan.md, adr-001/002/003-*.md, graphify-analysis/, assets/, superpowers/{plans/, reports/, specs/}
├── data/ — raw/ (PDFs + .sha256, 728 records), corpus/ (circulars.jsonl, context_headers_targeted.jsonl, regulations.jsonl), manifests/ (master_circulars.jsonl, master_exceptions.jsonl, regulation_edges.jsonl), index/ (dense.faiss, bm25/, chunks.jsonl, lineage.json, embeddings.npy, manifest.json, meta.json; splade.npz absent)
├── src/sebi_rag/ — flat module (no subpackages): __init__.py, api.py, api_spaces.py, pipeline.py, retrieve.py, splade.py, splade_encoder.py, context_headers.py, hyde.py, rerank.py, embeddings.py, segment.py, lineage.py, master_meta.py, metadata.py, generate.py, generate_spaces.py, corpus.py, corpus_spaces.py, eval.py, eval_asof.py, eval_harness.py, benchmark.py, settings.py, device.py, stats.py, expand.py, reg_citations.py, reg_lineage.py, regulations.py, verify_master.py, ui.py, ingest_pdf.py, attribution.py, measure.py |
├── scripts/ — build_index.py, calibrate.py, scrape_sebi.py, scrape_regulations.py, build_golden.py, build_golden_v6.py, build_reg_edges.py, build_splade_index.py, eval_json.py, eval_gate.py, eval_asof.py, bench_generators.py, bench_rerankers.py, bench_retrieval.py, export_benchmark.py, export_datasets.py, golden_v7/ (agreement.py, build_pool.py, derive_thresholds.py, gate_select.py, local_adjudicate.py, gemini_adjudicate.py, …), validate_corpus.py, repair_corpus_text.py, renu... |
├── tests/ — conftest.py (fixtures, env guards, mock models), fixtures/, test_*.py
├── eval/ — golden/ (golden_v1-v7.jsonl, gate_v7.json, v7_annotations/), probes/, runs/
├── reports/ — intervention reports (golden_v7 agreement, master coverage, reg_edge_audit, …)
├── graphify-out/ — graph.json, GRAPH_REPORT.md, cache, cost.json
├── logs/ — automation logs (canary, discover, refresh)
├── automation/n8n/ — n8n workflow JSON exports
├── dist/ — datasets/, backups/ (hf-sebi-circulars-pre-push)
├── deploy/ — com.sebi-rag.plist, com.sebi-rag-ops.plist
├── app.py — root-level HF Space entry point (CPU-only)
├── run.sh, run_ops.sh — service launchers
├── Makefile — operations (test, reindex, serve, scrape, calibrate, …)
├── config.toml — service config (env-overridable)
├── pyproject.toml, uv.lock — project metadata + dependencies
├── requirements-spaces.txt — HF Space dependencies (separate from local)
├── README.md, README-spaces.md — project readme + HF Space runbook
├── AGENTS.md, CLAUDE.md — agent guidance
```

## 11. Reproducibility Requirements

```yaml
reproducibility:
  - "Pin all dependency versions at their validation step"
  - "Pin model version, quantization, runtime parameters, and random seeds for canonical benchmark runtime"
  - "Version every index; record per-document provenance (source URL, fetch date, checksum); deterministic rebuild path"
  - "Benchmark results must always identify the runtime used"
  env_guards:
    - TOKENIZERS_PARALLELISM=false
    - OMP_NUM_THREADS=1
    - PYTORCH_ENABLE_MPS_FALLBACK=1
    desc: "Required to run bge-m3 (FlagEmbedding) and cross-encoder together on MPS without segfault. Pinned in tests/conftest.py"
```

## 12. Known Architectural Prerequisites (tracked in status.md)

```yaml
prerequisites:
  P1: "Labelled SEBI evaluation set — COMPLETED (golden_v7, n=260, adjudicated_n=260, gate armed). Calibrated: top_k=10, abstain_threshold=0.05"
  P2: "Metadata lineage extraction — COMPLETED (lineage.py, 5 edges, answer-layer warnings wired)"
```

## 13. Token Optimization (tracked in status.md)

Three-phase optimization reduced pre-injected context from **99,189 bytes (~24,800 tokens)** to **~10,500 bytes (~2,600 tokens)** — a **92.7% reduction** with zero regression (603 tests pass).

```yaml
config:
  APPEND_SYSTEM_md: ".omp/APPEND_SYSTEM.md — Concise OMP append (1,758 B) concatenated to session system prompt"
  settings_json: ".omp/settings.json — Optimized compaction (keepRecentTokens=16,384, reserveTokens=12,288) and thinking levels (default low with budgets: low=2,048, medium=8,192, high=24,576)"
  env: ".omp/env — PI_CACHE_RETENTION=long + OMP_CACHE_RETENTION=long for extended prompt cache (Anthropic: 1h, OpenAI: 24h)"
  agents_md: "AGENTS.md — On-demand context instructions, output constraints, session workflow, model routing"
  claude_md: "CLAUDE.md — 350-byte pointer (duplicate eliminated)"
savings:
  per_turn: "~22,200 tokens/turn saved (no on-demand reads)"
  per_1000_turns: "~22.2M tokens saved (~$2,220 at $0.10/MTok cached)"
  full_details: "See docs/optimization_summary.md"
  roadmap: "See docs/optimization_roadmap.md for Phase 3 validation checklist"
```

