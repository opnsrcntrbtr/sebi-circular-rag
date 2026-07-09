# Status — SEBI Circular RAG

> Records completed work and blockers. Consult before requesting information.
> Last updated: 2026-07-09.

## Current Snapshot

- Shipped baseline: local-first SEBI circular RAG with hybrid FAISS + BM25
  retrieval, cross-encoder reranking, grounded generation, abstention, and
  supersession-aware citations behind an authenticated FastAPI service.
- Current evaluation baseline: `eval/golden/golden_v6.jsonl`, with the current
  dense-corpus profile showing recall and abstention at 1.0 and citation
  precision in the ~0.73-0.77 range.
- Active roadmap: corpus expansion, OCR hardening, evaluation maintenance, and
  legal-safety tightening for near-domain queries. See [docs/next_steps.md](next_steps.md).

## Completed

- Phase 1 — Architecture validation pass 1 (PASS, conditional). Five findings raised.
- Phase 1 refinement — seven user refinements agreed (hybrid mandatory, bge-m3 as
  baseline, mandatory reranker, citation-grounded eval + abstention, canonical
  benchmark runtime, segmentation/metadata section, second validation).
- Architecture validation pass 2 (PASS). Confidence: High on soundness, Medium on
  metadata-lineage feasibility. No architectural blocker.
- Phase 2 — `docs/project_context.md` generated (v1 architecture).
- Phase 3 — `docs/status.md` generated (this file).
- Phase 4 — `docs/validation_roadmap.md` generated (handbook sequence, no expansion).
- Validation Step 1 — Hardware & macOS: **PASS**. Apple M4 Pro, 14 cores (10P+4E),
  48 GiB, arm64, ~1 TB SSD. macOS pinned at 26.5.1 (build 25F80).
- Validation Step 2 — Xcode CLT: **PASS**. Active dir Xcode.app; CLT pkg 26.6.0.0;
  Apple clang 21.0.0, git 2.50.1 (Apple Git-155), GNU Make 3.81.
- Validation Step 3 — Homebrew: **PASS**. Homebrew 6.0.5, ARM prefix
  /opt/homebrew, on PATH, no Rosetta. doctor non-fatal advisory only.
- Validation Step 4 — Python + uv: **PASS**. Python 3.14.6 (arm64), uv 0.11.25
  (arm64). Project venv to pin 3.12.x via `uv python` at repo init (Step 11) for
  MLX/FAISS wheel compatibility.
- Validation Step 5 — Git: **PASS**. Active git 2.54.0 (Homebrew; Apple 2.50.1 at
  /usr/bin). Identity configured, init.defaultBranch=main. init/add/commit verified.
- Validation Step 6 — MLX: **PASS**. .venv (Python 3.12.13); mlx 0.31.2 +
  mlx-lm 0.31.3; Metal GPU verified; load+generate OK (516 tok/s, 0.34 GB).
- Validation Step 7 — Ollama: **PASS**. Ollama 0.30.6 (≥0.19, MLX backend),
  server on :11434; inference on llama3.1:8b via API (seed=42) returned 'Fine.'.
- Validation Step 8 — PyTorch MPS (**required**, per D7): **PASS**. torch 2.12.1
  MPS available+built, mps matmul OK; sentence-transformers 5.6.0; FlagEmbedding
  1.4.0. bge-m3 load deferred to Step 10. Re-confirm MPS stability under reranker
  load at Step 10.
- Validation Step 9 — FAISS: **PASS**. faiss-cpu 1.14.3; IndexFlatIP (self-match
  top1 True) and IndexHNSWFlat build+search OK on Python 3.12.13.
- Validation Step 10 — Embeddings + Reranker: **PASS**. bge-m3 on MPS (dense 1024 +
  sparse + ColBERT); bge-reranker-v2-m3 on MPS via sentence-transformers CrossEncoder
  (scores [0.9914,0,0], correct ranking). FlagReranker unusable on transformers 5.x.
- Prerequisite — Repo scaffolded: src/sebi_rag (segment, embeddings, retrieve,
  rerank, generate, eval, pipeline), tests/, pyproject.toml. Models injected via
  Embedder/Reranker protocols for offline testing. bm25s 0.3.9, pytest 9.1.1 added.
- Validation Step 11 — Repository tests: **PASS**. 5 passed in 0.13s (offline:
  HashEmbedder+bm25s+FAISS+RRF+LexicalReranker; covers segmentation, RRF, hybrid
  retrieval, abstention, metrics).
- Validation Step 12 — End-to-end RAG: **PASS**. Real stack: bge-m3 (MPS) + bm25s +
  RRF → bge-reranker-v2-m3 CrossEncoder (MPS) → Ollama llama3.1:8b (seed 42, temp 0)
  + abstention. 2 integration tests pass (grounded+cited answer; out-of-domain
  abstains). Full suite: 7 passed in ~15s. **All 12 handbook steps validated.**

- P1 — Golden eval set + harness: **seeded**. Real corpus data/corpus/circulars.jsonl
  (1 verified circular SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123, verbatim excerpt from
  official SEBI page); eval/golden/golden_v1.jsonl (5 items); src/sebi_rag/{corpus,
  eval_harness}.py. Baseline (offline stack): Recall@10/MRR/nDCG=1.0, citation
  recall=1.0, citation precision=0.375, abstention acc=1.0, latency 0.4ms. 8 offline
  tests pass.

- PDF ingestion path: **ready & used**. src/sebi_rag/ingest_pdf.py (pdfplumber)
  extracts header circular number (2026 + legacy formats), date (month-name +
  numeric), subject, dept, version lineage; provenance, dedupe, --replace.
- Real corpus ingested: 4 circulars (CFD/2023/123 full; ITD AI advisory 2026; MRD
  price-data 2026; OIAE nomination 2026) → 233 chunks after PDF-aware chunking fix.
- Golden set golden_v2.jsonl (6 items across all 4 circulars) + calibration
  (scripts/calibrate.py): **top_k=3, abstain_threshold≈0.4** now pipeline defaults.

- P2 — Cross-document supersession resolution: **done**. src/sebi_rag/lineage.py
  classifies references as supersedes/amends/cites from circular text, builds a
  lineage graph, derives in_force|superseded|amended status, and flags superseded
  citations for retrieval. Real corpus annotated: OIAE/2026/12676 supersedes 12
  prior circulars. 4 lineage tests pass (13 offline total).

- Answer-layer supersession warning: **wired**. RAGPipeline takes a lineage graph;
  query() appends a "no longer in force — superseded by <X>" note and sets
  Answer.superseded when an answer cites a superseded circular. 14 offline tests pass.

- FastAPI service: **done**. src/sebi_rag/api.py exposes GET /health and
  POST /query (answer + citations + abstained + superseded + retrieved). Pipeline
  built once (lazy); create_app(factory) for offline tests. Smoke-tested with the
  real stack: /health -> {chunks:233, circulars:4}; /query (nomination) returned a
  grounded, correctly-cited OIAE/2026 answer. 3 api tests pass (17 offline total).

- Scraping plan + scraper: **ready** (docs/scraping_plan.md, scripts/scrape_sebi.py).
  robots.txt verified (allows /legal/circulars + /sebi_data/attachdocs; only js/css
  disallowed). Polite stdlib scraper (UA, rate-limit, backoff, checksum dedupe) ->
  ingest_pdf -> corpus. Confirmed Legal>Master Circulars endpoint (ssid=6, 135 recs).
  3 offline parsing tests pass (20 total). NOTE: scraper runs on USER's machine
  (Claude's web tools are restricted from bulk fetch); pagination param to verify.

- Corpus grown via scraper: **29 circulars, 20,349 chunks** (25 master circulars
  ingested). ingest_pdf fixed: rejoin space-split numbers; capture "Last updated on"
  as effective_date. Lineage rebuilt: 1,222 supersedes edges; **in-corpus
  supersession now live** — SEBI/HO/CFD/PoD-1/P/CIR/2024/0154 (Nov-2024 ICDR master
  circular) marked superseded by its 2026 successor. 20 offline tests pass.

- Index persistence: **implemented + tested**. HybridRetriever.save/load/index_exists
  (FAISS + bm25s + chunks + meta); scripts/build_index.py builds once -> data/index/;
  api.py loads the index in <1s instead of re-encoding. Round-trip test passes
  (21 offline tests). One-time full index build (~25 min bge-m3 encode) running in
  background -> data/index/.

- Index built + persisted (data/index/, 20,349 chunks, 335s). **Reload verified at
  0.34s.** calibrate.py + api.py now load the index (no re-encode).
- Supersession warning **verified on real data**: ICDR query cited superseded
  2024/0154; answer appended "no longer in force — superseded by 2026 ICDR master
  circular". end-to-end working.
- Realistic-corpus calibration (20k chunks, golden_v2): recall@10=1.0, abstention=1.0
  across the sweep; citation precision/recall now trade off (top_k=3: prec 0.53 /
  recall 0.80; top_k=5: prec 0.45 / recall 1.0). Toy-corpus perfection was an
  artifact. Root cause: topically-overlapping master circulars incl. superseded
  prior versions competing with in-force successors.

- Supersession-aware retrieval: **implemented + verified**. lineage.demote_superseded
  penalises superseded chunks in rerank (RAGPipeline.superseded_penalty=0.3, applied
  in query; mirrored in calibrate.py). Unit-tested. Live ICDR demo: top-3 went from
  [2026-ICDR, 2026-CFD, 2024/0154-superseded] -> [2026-ICDR, 2026-CFD]; the superseded
  circular is dropped and the in-force version cited. 22 offline tests pass.
- Note: golden_v2 aggregate calibration unchanged (those 5 queries have no superseded
  competitors; their precision dip is in-force topical overlap, not supersession).

- Golden set sharpened: **eval/golden/golden_v3.jsonl** (20 discriminating per-topic
  queries; current in-force circulars labelled).
- Lineage refinement: **master-circular re-issue detection** (lineage.mc_topic groups
  by normalised title; newest supersedes older). 5 verified re-issue groups; now 5
  in-corpus circulars correctly superseded (2024 LODR/ICDR, 2025 IA/RA/RTA -> 2026
  successors). No false merges. Recalibration (real stack + demotion):
  **citation precision 0.97 / recall 1.0 at top_k=3** (1.0/1.0 at top_k=1),
  recall@10=1.0, abstention=1.0. 23 offline tests pass.

- API hardening: **done + smoke-tested**. API-key auth (SEBI_RAG_API_KEY -> X-API-Key,
  401 verified), in-memory per-key/IP rate limit (SEBI_RAG_RATE_PER_MIN, 429 tested),
  latency_ms in every /query response, and citations_meta exposing each cited
  circular's status + superseded_by. Live ICDR query: cited only the in-force 2026
  ICDR (superseded 2024 demoted out), status in_force. 26 offline tests pass.

- Generation latency reduced: **MLXGenerator** (MLX-LM, Apple-Silicon native, D6) is
  now the default generator (env SEBI_RAG_GENERATOR=mlx|ollama, SEBI_RAG_MLX_MODEL).
  Cached Qwen2.5-0.5B-4bit generates in ~0.2s. End-to-end /query: **~18.8s -> ~2.1s
  warm** (~9x). Response-time budget added (SEBI_RAG_TIMEOUT_S, default 30s -> 504;
  verified). 27 offline tests pass. Smoke-tested with persisted index.

- Faithfulness verification (legal-safety): **done**. generate.faithfulness flags
  bracketed circular citations in an answer that are absent from the retrieved
  context; pipeline appends a caution caveat; /query exposes faithfulness +
  unsupported_citations; new eval-harness metric. Real smoke: faithfulness=1.0,
  ~2.4s. 29 offline tests pass.

- Corpus grown to **50 circulars** (page-0 scrape; 21 new ingested). ingest_pdf
  number-join fix (slash-space-alnum) recovers 2 truncated numbers; remaining odd
  numbers (HO/(1)..., HO/(92)...) are pdfplumber dropping digits in those PDFs (need
  OCR, not parser). 1 scanned PDF failed (use --ocr). scripts/renumber.py re-derives
  numbers from stored text. Recalibration (50 circulars): recall@10 1.0, abstention
  1.0, citation precision 0.87@top_k=3 / 0.92@top_k=2 (down from 0.97 — more topical
  overlap from regular circulars; recall stays 1.0).
- **Pagination SOLVED** (via Claude-in-Chrome inspection of searchFormNewsList JS):
  it's a POST to `/sebiweb/ajax/home/getnewslistinfo.jsp` with `doDirect=<0-based
  page>` (+ sid/ssid/smid/ssidhidden/next=n/nextValue/intmid=-1 and empty search/
  date/text fields); response is `listHTML #@# breadcrumb`, same row format so
  parse_rows works. Verified live: doDirect=0 -> ids ~102385, doDirect=5 -> ~93101.
  scrape_sebi._page() now uses it (page-0 GET seeds the JSESSIONID cookie). No Struts
  token needed. **Verified: --max 100 paged correctly; corpus 50 -> 124 circulars
  (22,273 chunks), 18 superseded-in-corpus.**
- **Metrics at 124 circulars:** recall@10=1.0, citation_recall=1.0 (top_k>=2),
  abstention=1.0, faithfulness=1.0 (bench). Citation precision fell to 0.77@top_k=3 /
  0.82@top_k=2. This is a **golden-set measurement artifact, not a retrieval defect**:
  golden_v3 (20 single-label items, built for the 29-circular corpus) is now
  under-specified. **Resolved via golden_v4** (scripts/build_golden.py: 30 queries
  grounded in real subjects, exact numbers resolved from corpus, multi-label where
  genuine e.g. SWAGAT). Fair recalibration at 124 circulars: recall@10=1.0,
  citation_recall=1.0@top_k=3 (0.93@top_k=2), abstention=1.0, **citation precision
  ~0.73-0.77**. Conclusion: the earlier 0.97 was a SMALL-corpus effect, not a labeling
  artifact — at 124 dense circulars precision naturally settles ~0.75 (governing
  circular always in top-3 + ~2 genuinely-related circulars co-cited). Honest,
  defensible legal profile (recall/faithfulness/abstention all 1.0). top_k=3 kept.
  Further top-1 precision would need metadata boosting or a stronger reranker.
  Data quality: ~10 records have pdfplumber digit-drop numbers (cosmetic); 1 scanned
  PDF failed (use --ocr); 1 empty issue_date.

- Architecture review (June-2026 best practices): **done** →
  docs/adr-001-architecture-review-2026-07.md. Five findings accepted, priority
  F1(chunk enrichment) → F5(golden-set circularity) → F3(incremental indexing) →
  F4(prompt-injection hardening) → F2(Qwen3-Reranker MLX benchmark). D1/D2
  amended with benchmark candidates (LanceDB; Qwen3-Embedding/Reranker via MLX).

- F5 (ADR-001) — golden_v5 held-out eval: **done + calibrated**. eval/golden/
  golden_v5.jsonl (56 items = 31 v4 + 15 body-grounded paraphrases with verified
  title-vocab non-overlap + 10 absence-verified hard negatives). calibrate.py
  golden path configurable (SEBI_RAG_GOLDEN/argv; default v5). 35 offline tests
  pass. **Honest baseline (real stack, 124 circulars):** recall@10=0.96,
  cit-prec 0.60 / cit-rec 0.87 @ top_k=3 thr=0.4, abstention acc 0.82 (peak at
  thr=0.4). Confirms v4 perfection was circularity artifact: paraphrase queries
  break recall (~2 misses); several hard negatives defeat the 0.4 threshold.
  **top_k=3 / thr=0.4 retained** (best cit-rec/abst trade-off in sweep;
  RECOMMEND None is expected — recommender criteria were tuned to v4 perfection).
  golden_v5 is the pre-F1 baseline; F1 (chunk enrichment) targets exactly these
  gaps.

- F1 (ADR-001) — contextual chunk enrichment: **done + verified**. segment.py
  prepends `circular_no | subject(≤120) | section` to every chunk at flush;
  reindexed (503s, 22,273 chunks); calibrate.py gained per-item diagnostics at
  top_k=3/thr=0.4. **golden_v5 @ top_k=3 thr=0.4: cit-prec 0.60 → 0.74 (+23%,
  exceeds ≥10% criterion), recall@10 0.96 → 1.00, cit-rec 0.87 → 0.89.** Both
  paraphrase recall misses fixed. Abstention 0.82 → 0.77.
- **NEW FINDING (from F1 diagnostics) — abstention gate is score-separable-only
  in theory, not in practice.** The 12 remaining FAILs decompose into two
  disjoint clusters: (a) 5 paraphrase FALSE ABSTENTIONS — correct doc retrieved
  at r@10=1 but cross-encoder top score 0.01–0.36 (< 0.4); (b) 8 hard-negative
  FALSE ANSWERS — no relevant doc exists but near-domain chunks score 0.40–0.99
  (esop 0.93, steward 0.99, fvci 0.90, ipef 0.85). Clusters overlap around
  0.34–0.47, so **no single rerank-score threshold can fix both**. Legal-safety
  relevance: system will confidently answer near-domain questions outside the
  corpus, citing non-governing circulars. Remedy is architectural, not
  calibration: stronger reranker (F2) and/or a groundedness-based abstention
  gate (answer-support check post-generation). top_k=3 / thr=0.4 retained
  meanwhile.

- F2 (ADR-001) — reranker benchmark: **done, candidate REJECTED on evidence**.
  Harness: rerank.Qwen3MLXReranker (yes/no-logit judge, model-card prompt) +
  scripts/bench_rerankers.py (shared pools, AUROC cluster separation, per-item
  scores) + make bench-rerank; results eval/bench_rerankers.json. golden_v5:
  bge-reranker-v2-m3 AUROC 0.812, abst 0.82, cit-prec@3 0.80, 2.24s/q.
  Qwen3-Reranker-0.6B (mxfp8, MLX) AUROC **0.799**, abst 0.82, cit-prec@3 0.72,
  4.82s/q — scores saturate 0.97–1.0 on ALL near-domain items (hard negatives
  ≈0.99 ≈ answerable ≈0.999): no separation, worse precision, 2x latency. 4B not
  run: saturation is judge-prompt-fundamental, and ~24s/q breaks the 2s budget.
  **Decision: baseline reranker retained (D2/D4 unchanged). Per the
  pre-registered rule (AUROC < 0.9), abstention moves to a post-generation
  groundedness gate** — a reranker swap cannot separate the clusters. Note:
  bge's accuracy-optimal threshold is 0.011, i.e. it stops abstaining rather
  than separating — confirms threshold-on-rerank-score is architecturally dead
  for near-domain negatives.

- Groundedness gate (ADR-001 item 7) — implemented; **first eval FAIL at 1.5B**.
  Infrastructure done + offline-tested (42 tests): Judge protocol, MLXJudge
  (deterministic, fail-open parse, shares generator model), pipeline/api wiring
  (SEBI_RAG_GATE, default **off** pending validation), scripts/eval_gate.py.
  Qwen2.5-1.5B-4bit judge on golden_v5: abst_acc 0.71–0.73 (below the 0.77
  no-judge baseline), judge false abstentions 7–8 (target 0; incl. master-
  circular items broker/cra/sif where context IS governing), hn_caught 5–6/10
  (passes RTA-master mention-chunks as "specific provisions"). Judge latency
  fine (0.42s/q); judge QUALITY at 1.5B is the failure.
  **Round 2 — 3B yes/no judge also FAIL, opposite direction:** abst_acc 0.32,
  36 judge false abstentions (rejects even direct master-circular matches),
  10/10 hn caught but useless. 1.5B lenient + 3B strict ⇒ the yes/no
  "specific provisions" protocol is scale-unstable — protocol defect, not
  capacity. **Round 3 built:** (A) judge-v2 closed-set excerpt identification
  (MLXJudge mode="identify", fails closed, parse_excerpt_choice) and
  (B) deterministic query↔subject-line cosine via bge-m3 (no extra model);
  eval_gate.py rewritten to score A, B, AND, OR in one pass with AUROC for B.
  **Round 3 results:** judge-v2 identification also FAIL (7 false abstains,
  6/10 hn) — LLM-judge line closed after 3 protocol/scale failures. Subject-sim:
  AUROC 0.887, and at thr 0.42 with score floor 0.05: **abstention 0.875, ZERO
  gate false abstentions, all 45 answerable answered, 5/10 hn caught** (all
  far-domain caught). **ADOPTED**: generate.SubjectSimJudge (deterministic,
  reuses bge-m3, ~30ms, subject-embedding cache); api.py gates by default
  (SEBI_RAG_GATE=off / SEBI_RAG_SUBJ_THRESHOLD to tune); abstain_threshold
  default 0.4 → 0.05 (config.toml, settings.py, calibrate sweep + 0.05).
  **Target 0.93 not met — recorded as partial.** Residual legal-safety risk:
  near-domain out-of-corpus queries whose topic resembles a corpus subject line
  (buyback/ESOP/muni/EGR/FVCI class) still get answered with non-governing
  citations. Escaped-hn subjsim range 0.49–0.56 overlaps answerable paraphrases
  0.43–0.62 — inseparable with current signals. 35+ offline tests pass.

- F3 (ADR-001) — incremental indexing: **implemented + offline-tested** (awaiting
  seed run). HybridRetriever.save now persists embeddings.npy + manifest.json
  (per-doc sha256 over enriched chunk texts — catches corpus AND
  segmentation/enrichment changes). build_incremental reuses cached rows for
  unchanged docs, encodes only new/changed docs, drops deleted/changed rows
  implicitly, rebuilds FAISS-Flat + BM25 from the matrix (encode is ~99% of a
  full build; Flat/BM25 rebuild is cheap). build_index.py incremental by
  default; --full forces re-encode. Tests: delta-encode counting (unchanged doc
  NOT re-encoded, rows bit-identical), delete drops rows, fallback-to-full
  without cache. 37 offline tests pass. NOTE: first `make reindex` after this
  change re-encodes once (~8 min) to seed the cache; growth steps after that
  encode only the delta (~25 new circulars ≈ 2–5 min vs hours at 2.8k scale).
  Disk: embeddings.npy ≈ 91 MB now, ≈ 2 GB at 500k chunks.
  **Seed + acceptance verified 2026-07-02:** full seed 507s (22,273 chunks),
  immediate re-run **5s, mode=incremental, docs_reused=124, chunks_encoded=0**
  (~100x rebuild-cost reduction for no-op/delta). F3 CLOSED. Reindex-on-growth
  is no longer a scaling blocker; corpus growth toward ~2.8k circulars is
  unblocked. Remaining ADR-001 item: F4 (prompt-injection hardening).

- Corpus-growth attempt 2026-07-02: `make scrape MAX=100` discovered 100 pages,
  **ingested=0 skipped=100** — the default section (master-circulars, ~135
  total) is already fully covered by the 124-circular corpus; no new issues
  since the last scrape. Reindex correctly no-opped (4s incremental,
  docs_reused=124) — F3's no-op path verified on the real corpus; the
  real-DELTA path still awaits genuinely new documents. Calibration identical
  (unchanged corpus). **Production operating point confirmed in sweep:**
  top_k=3, score floor 0.05 (printed as "0.1" — cosmetic %.1f rounding in
  calibrate.py): recall@10=1.0, cit-prec 0.77, cit-rec 0.96; near-domain
  abstention handled by the subject-sim gate (0.875, eval_gate). Real growth
  requires `--section circulars` (ssid=7, ~2.8k regular circulars).
- Growth attempt #2 (`--section circulars --from 2026-01-01 --max 200`):
  discovered only 53 pages, **ingested=0 skipped=53** — all 2026 regular
  circulars already in corpus. 53 << expected ~130 for H1-2026 suggests
  date-filtered pagination may stall after ~2 pages (guarded stop in _page).
  One transient IncompleteRead recovered by backoff. Corpus/index/calibration
  unchanged. Next: widen window to 2025 (--from 2025-01-01 --to 2025-12-31);
  if discovery again caps ~50, ssid=7 pagination needs browser-network-tab
  re-verification (same method that solved master-circular pagination).

- Corpus grown to **207 circulars / 24,609 chunks** (2025 tranche: 83 ingested,
  47 skipped, 1 failed — scanned PDF `1747655007246.pdf` (MII internal-audit
  norms, May-2025), retry with --ocr). **F3 real-delta VERIFIED:** reindex 82s,
  `mode=incremental, docs_reused=124, chunks_encoded=2336` (~6x faster than
  full; only new docs encoded). F3 fully closed.
- Supersession cascade verified at scale: superseded_in_corpus 18 → **74** —
  the ingested 2025 circulars matched pre-existing supersedes edges from the
  2026 master circulars (edges unchanged at 1,226; targets now present).
- Post-growth calibration (golden_v5, 207 circulars): recall@10 **0.98**
  (para-freeze now misses top-10 — new 2025 competitors crowd it out),
  cit-prec@3 0.73@floor-0.05 / 0.69@0.4 (was 0.77/0.74), cit-rec@3 0.91.
  hn scores unchanged. Two new diagnostics FAILs beyond para-freeze:
  para-aifmaster (AIF master displaced from top-3) and para-window (top hit now
  SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/97 — the July-2025 re-lodgement-window
  circular; partially a LABEL-AMBIGUITY: 2025/97 is topically legitimate but
  the Feb-2026 window circular governs "until when"; lineage has no edge
  between them). Params retained (top_k=3, floor 0.05, gate 0.42); drift is
  within expected topical-crowding range, golden label review flagged for the
  next growth step.

- F4 (ADR-001) — prompt-injection hardening: **done + offline-tested** (41
  sandbox tests; full suite expected 51). Delimited data-not-instructions
  grounded prompt (shared MLX/Ollama — duplicate removed); ingest_pdf
  injection_scan (8 pattern classes incl. delimiter spoofing) recorded as
  injection_flags per record with ingest warning; retroactive corpus scan:
  1 benign FP / 207 (broker master's password-policy text); timing-safe API-key
  compare (secrets.compare_digest); 127.0.0.1 binds and HTTPS-anchored scraper
  URLs verified. **ALL ADR-001 action items now closed** (F5, F1, F3, F4 done;
  F2 rejected on evidence; gate adopted as partial). Prompt change alters
  generation input — groundedness/faithfulness spot-check recommended at next
  bench run; retrieval/index unaffected (no reindex needed).

- n8n automation drift review (post-ADR-001): **updated**. eval_json.py →
  golden_v5 + production-mirrored abstention (score floor + SubjectSimJudge) +
  live injection_flagged count; canary/refresh Code-node thresholds re-based
  (recall<0.97, cit_rec<0.85, abst<0.82, cit_prec<0.60, injection_flagged>1);
  discover_new.py checks master-circulars too; plan doc §6 rewritten.
  Old thresholds would have FALSE-ALERTED on the honest v5 baselines
  (recall 0.98, abst 0.875). USER ACTION: re-import 1_corpus_refresh.json +
  3_eval_canary.json into n8n (import replaces; re-activate schedules) and
  restart the ops server if running. Canary runtime rises ~2x (56 v5 items vs
  31 + gate encode) — still well under the 300s ops-server timeout.

- ADR-002 — certainty architecture: **implemented + offline-tested** (47
  sandbox tests; full suite expected 60). Root cause of the reported silent
  abstention: request sent `top_k=0` → empty context → gate correctly abstained
  (retrieval itself was perfect). Changes: top_k Field(ge=1,le=10) → 422;
  every /query response now carries confidence{rerank_top,margin,subject_sim},
  banded certainty (high|medium|low; high = gates passed ∧ subject_sim ≥ 0.65 ∧
  faithfulness 1.0 — 100%-citation-recall region on golden_v5), and
  abstention_reason (no_context|score_floor|subject_gate); opt-in per-request
  `advisory: true` adds a mandatory-prefixed LOW-CONFIDENCE draft_answer on
  gate failure while answer/abstained stay authoritative (D5 preserved).
  SubjectSimJudge gained .score(). Schema change is additive (n8n unaffected).
  See docs/adr-002-certainty-and-advisory.md.

- Live false abstention analysed ("What is a regulated entity?", top_k=1):
  ADR-002 telemetry worked — abstention_reason=subject_gate, rerank_top 0.997,
  subject_sim 0.361 < 0.42. Root cause: **definitional query answered inside a
  broadly-scoped master circular** — gate signal is doc-subject-level, evidence
  is section-level ("3. Regulated Entity (RE)" in the brokers master). Same
  residual-weakness class as ADR-001's paraphrase/hn overlap, new manifestation.
  **Section-aware gate variant implemented** (SubjectSimJudge include_sections:
  max over subject + section heading; env SEBI_RAG_GATE_SECTIONS, default off);
  eval_gate.py rewritten to compare subject-only vs subject+section on
  golden_v5 in one pass (AUROC, false-abst, hn_caught, changed-items marks,
  plus the live probe). Decision rule: flip default on only if hn_caught does
  not regress and the probe passes. 48 offline tests pass.
- Section-gate eval (207 circulars) + **two-tier gate ADOPTED**. Plain
  max(subj,section) at 0.42 REJECTED (hn 4/10 → 3/10; hn-settle crossed at
  0.493) despite better AUROC (0.933 vs 0.897). Data showed clean separation
  for section-driven scores: legit section matches ≥ 0.62 (mfmaster/block/
  window/probe 0.624–0.644) vs max section-driven hn 0.493 → **two-tier gate:
  subject_sim ≥ 0.42 OR section_sim ≥ 0.60** (margin 0.107). Provably no
  golden_v5 regression (only adds correct answers); fixes the definitional
  top_k=1 false abstention (probe section-only 0.644). SubjectSimJudge now
  two-tier (section_threshold, env SEBI_RAG_SECT_THRESHOLD, default 0.60,
  "off" disables); confidence block gains section_sim; answer_with_abstention
  delegates to judge.grounded() (no more inline threshold duplication);
  eval_json mirrors production; eval_gate reports subj-only/max/section-only +
  two-tier. Note: live probe passes at default top_k=3 even under subject-only
  (subj 0.457) — the reported failure was top_k=1-specific. 48 offline tests.

## Pending

Structured plans for the next tracks: **docs/next_steps.md** —
(a) quality bump — **DONE**. Model sweep (scripts/bench_generators.py, golden_v3):
    faithfulness 1.00 at all sizes (0.5B/1.5B/3B); groundedness 0.84/0.89/0.95;
    abstention 1.0, cit-prec 0.97 (model-independent); latency 2.32/2.64/3.30s.
    **Default set to Qwen2.5-1.5B-4bit** (balanced); 3B via SEBI_RAG_MLX_MODEL for
    max groundedness.
(b) packaging/deployment — **DONE**. config.toml + settings.py (env overrides file,
    precedence tested); Lineage.save/load -> data/index/lineage.json (built by
    build_index.py, loaded by api.py — no rebuild); /ready + config-reporting /health;
    Makefile (test/reindex/index/annotate/calibrate/serve/scrape), run.sh, launchd
    plist (deploy/). Smoke-tested: /health reports config, /ready toggles, /query uses
    persisted lineage (ICDR -> in-force citations). 33 offline tests pass.
(c) grow corpus via scraper — **IMPLEMENTED**. --section circulars(ssid=7,~2.8k)|
    master-circulars; --from/--to date filter; --ocr fallback. Offline-tested.
    **Live finding:** page-0 GET works; pagination POST returns HTTP 530 BLOCKED
    (SEBI WAF). Fixes applied: graceful degradation (no crash, keep page-0 results)
    + browser-like POST (cookie session from GET + Content-Type/Referer/Origin/
    X-Requested-With) as best-effort unblock. RETRY needed to confirm; if 530
    persists, programmatic pagination is WAF-blocked -> use browser automation or
    accept newest-page ingestion. reindex/calibrate confirmed working (cit-prec 0.97
    @ top_k=3). 35 offline tests pass.
- Remaining ~2s warm /query is bge-m3 query-encode + cross-encoder rerank.
- Prerequisite **P1** — build labelled SEBI evaluation set (query → answer +
  citation). Gates all eval metrics and threshold calibration.
- Prerequisite **P2** — metadata lineage extraction approach (supersession /
  amendment / version lineage via cross-document linking).

## Current Validation Step

All 12 validation steps PASS. Real corpus = 4 SEBI circulars (233 chunks). P1
(golden set + harness + calibration: top_k=3, threshold≈0.4) and P2 (cross-document
supersession resolution; OIAE/2026 supersedes 12 circulars) both done. 13 offline
tests pass. FastAPI service done and smoke-tested with the real stack (17 offline
tests). System is end-to-end complete. Next: grow the corpus / API hardening.

## Known Blockers

- **B3 (resolved)** — Step 12: dual-model-on-MPS segfault (FlagEmbedding pool vs
  Metal). Fixed via env guards in tests/conftest.py (TOKENIZERS_PARALLELISM=false,
  OMP_NUM_THREADS=1, PYTORCH_ENABLE_MPS_FALLBACK=1).
- **B2 (resolved)** — Step 10: bge-m3 weights download stalled (Xet-backed bin under
  HF throttle). Fixed by `hf auth login` + `hf-xet` install + `HF_HUB_DISABLE_XET=1`,
  ignoring onnx/`.bin` duplicates.
- **B1 (resolved)** — Step 6 mlx-lm: fixed by pinning Python 3.12.13 venv.
- P1 / P2 — implementation prerequisites (not blockers).

## Last Updated

2026-06-29
