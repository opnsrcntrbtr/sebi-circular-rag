# Status — SEBI Circular RAG

> Records completed work and blockers. Consult before requesting information.
> Last updated: 2026-07-30.

## Current Snapshot

| Metric | Value |
|---|---|
| **Corpus** | 705 SEBI circular records, 77,841 chunks (75 MB JSONL) |
| **Index** | 1.0 GB at `data/index/` — dense.faiss, bm25, chunks.jsonl, lineage.json, embeddings.npy, manifest.json, meta.json, splade.npz (eval-only) |
| **Reporting set** | `eval/golden/golden_v7.jsonl` (n=260); **adjudicated_n = 106** |
| **Gate** | `gate_v7.json` armed: recall_at_k 0.9155, citation_recall 0.3245, abstention_accuracy 0.8346 |
| **Frozen sets** | `golden_v5` (n=56), `golden_v6` (n=56) |
| **v7 strata** | title_direct 40, body_paraphrase 60, numeric_table 30, lineage_supersession 40, multi_hop 20, repealed_basis 20, hard_negative 40, far_negative 10 |
| **Abstain/as_of rows** | 53 abstain, 15 dated `as_of` |
| **Draft rows** | 121 draft, 33 seeded |
| **Test suite** | 603 tests pass (546 test functions, 3 deselected integration) |
| **Source tree** | 37 Python modules in `src/sebi_rag/` (api, pipeline, retrieve, rerank, embeddings, segment, lineage, generate, eval, eval_harness, benchmark, splade, hyde, context_headers, reg_citations, reg_lineage, regulations, master_meta, settings, stats, ui, expand, verify_master, eval_asof, device, corpus, metadata); 40+ scripts in `scripts/` |
| **Golden-v7 pipeline** | 14 scripts in `scripts/golden_v7/` (agreement, backfill_escalations, build_pool, derive_thresholds, gate_select, gemini_adjudicate, local_adjudicate, make_packet, mine_strata, relabel_repooled, remap_doc_ids, score, seed_v7) |
| **V7 annotations** | `eval/golden/v7_annotations/` — votes.jsonl (207 claude records), pools.jsonl (4.2 MB), arbitration_queue.jsonl (65 KB), external_sample.json, gemini/ (21 dirs), qwen/ (150 files), candidates/, packet_human/ |
| **Documentation** | 3 ADRs (adr-001 architecture review, adr-002 certainty architecture, adr-003 ANE declined), project_context.md, scraping_plan.md, n8n_automation_plan.md, USAGE.md |
| **Automation** | n8n workflows in `automation/n8n/` |

### Production metrics (real stack, 705 circulars)
- recall@10 ≈ 0.98; citation_precision ~0.73–0.77 @ top_k=3; citation_recall ~0.91–0.96
- abstention 0.875 (subject-sim gate); faithfulness 1.0
- Generation: MLXGenerator (Qwen2.5-0.5B-4bit) ~2.1s warm; Ollama fallback (env SEBI_RAG_GENERATOR=mlx|ollama, SEBI_RAG_MLX_MODEL)
- Index reload: 0.34s; incremental reindex: ~82s for delta (8x faster than full ~8 min)

### Operating point
`top_k=3`, score floor 0.05, two-tier subject+section gate (subject ≥ 0.42 OR section ≥ 0.60); env SEBI_RAG_GATE, SEBI_RAG_SUBJ_THRESHOLD, SEBI_RAG_SECT_THRESHOLD.

## Source Architecture

| File (`src/sebi_rag/`) | Purpose |
|---|---|
| `api.py` | FastAPI entry point, app factory, key-in-body auth |
| `pipeline.py` | `RAGPipeline` orchestration; `regulatory_basis_status` per-citation |
| `retrieve.py` | `HybridRetriever` — FAISS + BM25 RRF fusion (SPLADE eval-only) |
| `rerank.py` / `embeddings.py` | Cross-encoder / BGE-M3 embedding |
| `segment.py` | Hierarchical chunking (`CircularMeta`, `Chunk`) |
| `lineage.py` | Supersession tracking + corpus annotation |
| `regulations.py` | Regulation identity, alias table, name resolution |
| `reg_citations.py` | Regulation citations from circular text |
| `reg_lineage.py` | Circular→regulation edges + `regulatory_basis_status` |
| `generate.py` | Local generation + abstention gate (MLXJudge/SubjectSimJudge) |
| `eval.py` / `eval_harness.py` / `benchmark.py` | Metrics, golden-set runner, BEIR/TREC export |
| `splade.py`, `hyde.py`, `context_headers.py` | Retrieval experiments (opt-in, off by default) |

> ⚠️ `*_spaces.py` (`api_spaces`, `corpus_spaces`, `generate_spaces`) + root `app.py` = CPU-only HF Spaces demo. **Do not edit when fixing local Apple-Silicon pipeline.** Config in `config.toml [spaces]`; runbook in `README-spaces.md`.
>
> ⚠️ **Never add fields to `CircularMeta`** — `hierarchical_chunk()` does `meta=asdict(meta)` (`segment.py:131`), so new fields land in every chunk payload (77.8k chunks). Additive per-circular metadata goes on corpus JSONL record only — see `master_meta.annotate_master_fields` and `reg_lineage.annotate_regulation_fields`.

## Completed Phases & Validation

### Prerequisite Validations (Steps 1–12) — All PASS

| Step | Item | Result |
|---|---|---|
| 1 | Hardware & macOS: Apple M4 Pro, 14 cores (10P+4E), 48 GiB, arm64, ~1 TB SSD; macOS 25F80 | PASS |
| 2 | Xcode CLT: pkg 26.6.0.0; Apple clang 21.0.0, git 2.50.1, GNU Make 3.81 | PASS |
| 3 | Homebrew: 6.0.5, ARM prefix /opt/homebrew, on PATH | PASS |
| 4 | Python + uv: Python 3.14.6 (arm64), uv 0.11.25; project venv pins 3.12.x | PASS |
| 5 | Git: 2.54.0 (Homebrew); identity configured, init.defaultBranch=main | PASS |
| 6 | MLX: .venv (Python 3.12.13); mlx 0.31.2 + mlx-lm 0.31.3; Metal GPU verified (516 tok/s, 0.34 GB) | PASS |
| 7 | Ollama: 0.30.6 (≥0.19, MLX backend); server on :11434; inference OK | PASS |
| 8 | PyTorch MPS: torch 2.12.1 MPS available+built; sentence-transformers 5.6.0; FlagEmbedding 1.4.0 | PASS |
| 9 | FAISS: faiss-cpu 1.14.3; IndexFlatIP + IndexHNSWFlat build+search OK | PASS |
| 10 | Embeddings + Reranker: bge-m3 on MPS (dense 1024 + sparse + ColBERT); bge-reranker-v2-m3 CrossEncoder (scores [0.9914,0,0]); FlagReranker unusable on transformers 5.x | PASS |
| 11 | Repo scaffold: src/sebi_rag (segment, embeddings, retrieve, rerank, generate, eval, pipeline), tests/, pyproject.toml; bm25s 0.3.9, pytest 9.1.1 | PASS |
| 12 | End-to-end RAG: bge-m3 (MPS) + bm25s + RRF → bge-reranker-v2-m3 CrossEncoder (MPS) → Ollama llama3.1:8b (seed 42, temp 0) + abstention; 7 passed in ~15s | PASS |

### Phase Deliverables

| Phase | Item | Status |
|---|---|---|
| P1 | Golden eval set + harness (7 versions: v1→v7); corpus 705 records, 77,841 chunks; harness: `eval_harness.py` (recall@10, MRR, nDCG, citation prec/recall, abstention acc, faithfulness, injection_flagged); corpus: `corpus.py`; eval: `eval.py`; calibration: `calibrate.py` | Complete |
| P2 | Cross-document supersession resolution; `lineage.py` (12,849 B, class `Lineage`, 17 functions: status, explicit_superseded_by, build_lineage, add_supersede, demote_superseded, superseded_citations); 705 records annotated, 5 lineage edges (90 false-positives removed via corpus text repair) | Complete |
| P3 | FastAPI service; `api.py` (10,475 B): GET /health, POST /query (answer + citations + abstained + superseded + retrieved); auth: SEBI_RAG_API_KEY → X-API-Key (401); rate limit: SEBI_RAG_RATE_PER_MIN (429); latency_ms per response; citations_meta with status + superseded_by | Complete |
| — | Scraping plan + scraper; `scraping_plan.md` (8,278 B), `scripts/scrape_sebi.py` (11,487 B); robots.txt verified; polite stdlib scraper (UA, rate-limit, backoff, checksum dedupe) → ingest_pdf → corpus; Legal>Master (ssid=6, 135 recs); Circulars (ssid=7, ~2.8k) | Complete |
| — | PDF ingestion; `ingest_pdf.py` (13,918 B): pdfplumber extraction (header circular number, date, subject, dept, version lineage); provenance, dedupe, --replace | Complete |
| — | Index persistence; `HybridRetriever.save/load/index_exists` (FAISS + bm25s + chunks + meta); `scripts/build_index.py` (2,367 B) → `data/index/` (1.0 GB); load <1s | Complete |
| — | Answer-layer supersession warning; `pipeline.py` (6,207 B) imports demote_superseded/superseded_citations; superseded_penalty=0.3; `Answer.superseded` set | Complete |
| — | Generation latency reduction; MLXGenerator (MLX-LM, Apple-Silicon native); `generate.py` (15,898 B) class MLXGenerator (line 265); Qwen2.5-1.5B-4bit ~0.2s; end-to-end /query: ~18.8s → ~2.1s warm (~9x); env SEBI_RAG_GENERATOR=mlx|ollama, SEBI_RAG_MLX_MODEL; SEBI_RAG_TIMEOUT_S default 30s | Complete |
| — | Faithfulness verification; `generate.py` faithfulness(text, allowed_ids) (line 21): flags bracketed citations absent from retrieved context; returns (score, unsupported_citations); pipeline appends caution when unsupported_citations | Complete |
| — | Supersession-aware retrieval; demote_superseded penalises superseded chunks in rerank (superseded_penalty=0.3); verified at 705 records | Complete |
| — | Golden set sharpening: v3 (20 discriminating queries), v4 (30 grounded queries, multi-label), v5 (56 held-out: 31 v4 + 15 paraphrase with title-vocab non-overlap + 10 hard negatives), v6 (56), v7 (260) | Complete |
| — | Contextual chunk enrichment (F1); `segment.py` (6,843 B) prepends circular_no + subject(≤120) + section to every chunk at flush; cit-prec 0.60→0.74 (+23%), recall@10 0.98→1.00, cit-rec 0.87→0.89 | Complete |
| — | Reranker benchmark (F2); `rerank.py` (4,941 B) Qwen3MLXReranker + `bench_rerankers.py` (6,532 B); bge-reranker-v2-m3 AUROC 0.812 vs Qwen3-Reranker-0.6B AUROC 0.799 (saturation, worse precision, 2x latency) — **baseline retained** | Complete |
| — | Groundedness gate (ADR-001 item 7); SubjectSimJudge adopted: `generate.py` class SubjectSimJudge (line 176, deterministic, reuses bge-m3, ~30ms); two-tier gate: subject_sim ≥ 0.42 OR section_sim ≥ 0.60; env SEBI_RAG_GATE, SEBI_RAG_SUBJ_THRESHOLD, SEBI_RAG_SECT_THRESHOLD; abstention 0.875, ZERO gate false abstentions | Complete |
| — | Incremental indexing (F3); `retrieve.py` build_incremental (line 105): reuses cached rows for unchanged docs, encodes only new/changed; `build_index.py` incremental by default, --full forces re-encode; seed: 507s full → 5s incremental (docs_reused=705, chunks_encoded=0) | Complete |
| — | Prompt-injection hardening (F4); delimited data-not-instructions grounded prompt; `ingest_pdf.py` injection_scan (8 pattern classes incl. delimiter spoofing) → injection_flags; timing-safe API-key compare | Complete |
| — | ADR-002 certainty architecture; top_k Field(ge=1,le=10) → 422; confidence{rerank_top,margin,subject_sim}; banded certainty (high|medium|low); abstention_reason; opt-in advisory: true → draft_answer | Complete |
| — | n8n automation drift review; `eval_json.py` (4,818 B) → golden_v5 + production-mirrored abstention; canary thresholds re-based | Complete |
| — | Regulatory cross-reference infrastructure; `scripts/build_reg_edges.py` | Complete |

### ADR-001 Findings Status

| Finding | Item | Result |
|---|---|---|
| F1 | Contextual chunk enrichment | Complete — cit-prec +23%, recall@10 → 1.00 |
| F2 | Reranker benchmark (Qwen3-Reranker-0.6B) | Rejected — saturation, worse precision, 2x latency; baseline retained |
| F3 | Incremental indexing | Complete — seed 507s → incremental 5s (100x reduction) |
| F4 | Prompt-injection hardening | Complete — 8 pattern classes, timing-safe auth |
| F5 | Golden v5 held-out eval | Complete — 56 items, honest baseline confirmed |
| Gate | Groundedness gate (item 7) | Adopted — SubjectSimJudge two-tier (partial: target 0.93 abst_acc not met; residual near-domain risk) |

## Golden v7 Pipeline Status (2026-07-30)

### Census
- **Total**: 260 rows | **Adjudicated**: 106 | **Draft**: 121 | **Seeded**: 33
- Strata on target: title_direct 40, body_paraphrase 60, numeric_table 30, lineage_supersession 40, multi_hop 20, repealed_basis 20, hard_negative 40, far_negative 10
- 53 abstain rows, 15 dated `as_of` rows

### Agreement (claude vs qwen, 150 external rows)
- **Promoted**: 103 (exact-set agreement → adjudicated)
- **Flipped**: 0
- **Arbitration queue**: 47 (28 external draft + 19 seeded non-external)

### Agreement κ by stratum (exact-set; deliberately stricter than provision-level promotion)

| Stratum | n | κ | Raw agreement |
|---|---|---|---|
| far_negative | 4 | 1.000 | 100% |
| hard_negative | 15 | 1.000 | 100% |
| title_direct | 25 | 0.077 | 8% |
| multi_hop | 13 | 0.071 | 7.7% |
| numeric_table | 19 | 0.000 | 0% |
| lineage_supersession | 24 | 0.201 | 20.8% |
| repealed_basis | 13 | 0.291 | 30.8% |
| body_paraphrase | 37 | 0.265 | 27% |

Low κ on title_direct/multi_hop/numeric_table reflects spec §7 promotion amendment (2026-07-26): κ stays exact-set while promotion accepts containment or quote-match.

### Gate floors (106 adjudicated rows)
- `adjudicated_n`: **106** (≥ 100 threshold met)
- `recall_at_k`: **0.9155** (was 0.9126)
- `citation_recall`: **0.3245** (was 0.3126)
- `abstention_accuracy`: **0.8346** (was 0.83)

### Key decisions
- **Local adjudication**: Qwen3.6-35B-A3B-MLX-4bit via oMLX (127.0.0.1:8001) is PRIMARY annotator, not Gemini
- **Provision-level promotion**: spec §7 amended to accept containment/quote-match; κ stays exact-set
- **Parse-error recovery**: 4 rows recovered (truncated at max_tokens=4096); re-ran with GOLDEN_LOCAL_MAX_TOKENS=16384; 3 promoted, 1 draft (v7-rb-007: genuine disagreement → needs human arbitration)
- **Claude-label accuracy vs externals**: 48/166 matched (28.9%), 95% CI 22.2–36.4%

## Known Blockers

**No active blockers.** All validation steps pass, all phases complete, 603 tests pass.

### Historical (resolved)
- **B3** — Step 12: dual-model-on-MPS segfault (FlagEmbedding pool vs Metal). Fixed via env guards in tests/conftest.py.
- **B2** — Step 10: bge-m3 weights download stalled (Xet-backed bin under HF throttle). Fixed via `HF_HUB_DISABLE_XET=1`.
- **B1** — Step 6: mlx-lm pinning. Fixed by Python 3.12.13 venv.

## Corpus Integrity (2026-07-25 repair)

**Defects found**: 6 text-corrupted + 12 stale-numbered records (of 705).
- 5 records: body text overwritten with shared circular's text (batch write from stale variables); PDFs still on disk as orphans; repaired via `scripts/repair_corpus_text.py`
- 12 records: stale circular_number (truncated or from cited circular); fixed via `scripts/renumber.py`
- Parser fix: `_rejoin_split` converted en-dash to `/`; spacing disambiguation changes exactly 2 records
- **Impact**: removed 90 false-positive supersession pairs (2850→2760); entire delta attributable to 12 records
- **Guardrail**: `make validate-corpus` / `scripts/validate_corpus.py`: no duplicate body text, circular_number derivable from own text, --deep PDF re-extraction match

**Pooling fix**: `assemble_pool` cap saturation (cap=20 consumed by common-word must_contain literals). Bounded via gold_literal_cap=6, reranked instead of document-ordered.

**Residual**: 22 orphan PDFs in `data/raw/`; SPLADE sidecar (splade.npz) pinned to old 77,859 chunk count — needs rebuild before SPLADE runs.

## Token Optimization (2026-07-28)

Three-phase optimization reduced pre-injected context from **99,189 bytes (~24,800 tokens)** to **~10,500 bytes (~2,600 tokens)** — **92.7% reduction**, zero regression (603 tests pass).

| Phase | Changes | Savings |
|---|---|---|
| 1: On-demand context | AGENTS.md inline refs; replaced pre-injected status.md (46KB) + project_context.md (34KB); folded README.md quick ref | ~22,930 tokens/turn |
| 2: Structural | CLAUDE.md → 350B pointer; .pi/SYSTEM.md (1,377 B); compaction/thinking budgets optimized | ~1,200 tokens/turn |
| 3: Output & workflow | Output constraints (schemas, diffs); session workflow; model routing guidelines; PI_CACHE_RETENTION=long | — |
| 3.1: Prompt cache | Removed redundant ## System Prompt from AGENTS.md; prefix files: .pi/SYSTEM.md (1,736 B) + AGENTS.md (7,779 B) + CLAUDE.md (350 B) = ~9.2KB | ~2,070 tokens/turn (cache hit) |
| 3.2: Package tools | Removed pi-smart-fetch (3.7MB) + pi-smart-web-search (40KB); npm install: 87MB→4KB | ~55K–134K tokens/turn |

**Files changed**: AGENTS.md, CLAUDE.md, .pi/SYSTEM.md, .pi/settings.json, .pi/env, .pi/npm/package.json, docs/optimization_summary.md, docs/optimization_roadmap.md.

## Last Updated

2026-07-30
