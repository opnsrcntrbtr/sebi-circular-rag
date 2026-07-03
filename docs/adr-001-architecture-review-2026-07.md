# ADR-001: June-2026 Architecture Review — Findings F1–F5 and D1/D2 Amendments

**Status:** Accepted
**Date:** 2026-07-02
**Deciders:** Ian (owner)
**Context baseline:** 124 circulars / 22,273 chunks; recall@10 = 1.0, citation precision ~0.73–0.77 @ top_k=3, faithfulness = 1.0, abstention = 1.0, ~2.1 s warm /query. All 12 handbook validation steps PASS.

## Context

External review of the production system against June-2026 local-first RAG best
practices, scoped to four dimensions: retrieval-quality ceiling, scalability to
the full SEBI corpus (~2.8k circulars), security/robustness, and modern OSS
alternatives. All components were on the table; D1–D7 remain in force except as
amended below. Five findings accepted, priority **F1 → F5 → F3 → F4 → F2**.

## Findings (accepted decisions)

### F1 — Contextual chunk enrichment (retrieval quality, HIGH impact)

**Problem.** Citation precision plateaus ~0.75 because chunks carry no document
identity at embed time; topically-overlapping master circulars compete in dense
space. **Decision.** Prepend `<circular_no> | <subject> | <section heading>` to
each chunk's text before embedding (summary-augmented / contextual chunking;
arXiv:2510.06999, arXiv:2603.19251). **Change.** One-line prefix in
segmentation → reindex → recalibrate against golden_v4 (after F5). **Success
criterion.** ≥10% top-3 citation-precision gain, recall@10 held at 1.0.

### F2 — MLX-native reranker benchmark candidate (quality + Apple Silicon)

**Problem.** Top-1 precision is reranker-bound; the PyTorch-MPS dual-model path
requires the B3 env-guard workarounds. **Decision.** Benchmark
Qwen3-Reranker-0.6B/4B on MLX (embed/rerank forward paths merged in MLX
ecosystem ~Mar 2026) against bge-reranker-v2-m3. Adoption only on benchmark
evidence per D4/D6. A win additionally retires the MPS segfault guards for
rerank. **Baseline unchanged until then.**

### F3 — Incremental indexing before corpus growth (scalability, CRITICAL)

**Problem.** `build_index.py` re-encodes the entire corpus (335 s @ 20k chunks
→ est. 2.5–3 h+ at ~450–500k chunks); no incremental path. Memory is not the
constraint (500k × 1024-dim fp32 ≈ 2 GB); rebuild cost and index versioning
are. **Decision.** Checksum-keyed incremental encode: embed only new/changed
documents, `IndexHNSW.add` for dense, rebuild BM25 (cheap), version the index
per D6/§11. **Benchmark candidate:** LanceDB (embedded, disk-backed, versioned,
serverless — fits local-first) vs FAISS at ≥100k chunks. FAISS retained per D1
unless evidence justifies. WAF-blocked pagination fallback: browser automation
or scheduled newest-page ingestion.

### F4 — Indirect prompt-injection hardening (security)

**Problem.** Scraped PDF text enters the generator context verbatim (OWASP
LLM01:2025). Faithfulness check catches fabricated citations, not injected
instructions. **Decision.** (1) HTTPS-only fetch + verify recorded checksums at
ingest; (2) wrap retrieved chunks in explicit data delimiters with a
system-prompt rule that context is data, never instructions; (3)
ingestion-time scan for instruction-like patterns in extracted text; (4)
timing-safe API-key compare (`secrets.compare_digest`); (5) bind service to
localhost unless fronted by TLS.

### F5 — Golden-set circularity fix (evaluation robustness)

**Problem.** golden_v4 is generated from corpus subjects, so queries share
vocabulary with the chunks they label — recall/abstention = 1.0 everywhere is
partly an artifact. Calibration may not survive real-user phrasing.
**Decision.** Add a held-out slice of human-written paraphrase queries (no
subject-line vocabulary) plus hard negatives (SEBI topics absent from the
corpus but near in embedding space) to stress the 0.4 abstention threshold.
**Gate:** land before any further calibration (including F1's) so downstream
benchmarks are trustworthy.

## Amendments to Design Decisions

- **D1 (amended 2026-07-02).** Hybrid retrieval remains mandatory; FAISS remains
  the dense engine. **LanceDB is recorded as the sanctioned benchmark candidate**
  for the dense store at ≥100k-chunk scale (embedded/disk-backed/versioned).
  Replacement only on benchmark evidence of ≥10% measurable benefit
  (build/reload time, memory, or retrieval quality) with no recall regression.
- **D2 (amended 2026-07-02).** bge-m3 remains the baseline embedder.
  **Qwen3-Embedding (0.6B local variant) and Qwen3-Reranker-0.6B/4B via MLX are
  recorded as the sanctioned benchmark candidates** for embedder and reranker
  respectively. Same evidence bar; canonical-runtime rules (D6) apply to any
  benchmark run.

## Consequences

- Easier: precision gains without model swaps (F1); trustworthy metrics (F5);
  corpus growth without multi-hour rebuilds (F3); reduced injection surface (F4).
- Harder: one full reindex required by F1; golden-set curation is manual work;
  incremental indexing adds index-state bookkeeping (checksum registry).
- Revisit: after F1+F5 recalibration, re-decide whether F2's reranker benchmark
  is still needed for top-1 precision; re-run calibration after every corpus
  growth step (§7 rule).

## Action Items

1. [x] F5 — golden_v5: held-out paraphrase slice + hard negatives; recalibrated 2026-07-02.
       Baseline: recall@10 0.96, cit-prec 0.60 / cit-rec 0.87 @ top_k=3 thr=0.4, abst 0.82.
2. [x] F1 — metadata prefix in segmentation; reindexed + recalibrated 2026-07-02.
       Result: cit-prec 0.60 → 0.74 (+23%), recall@10 0.96 → 1.00, cit-rec 0.87 → 0.89. Criterion met.
       Follow-on finding: abstention clusters are threshold-inseparable (5 false abstains at
       score 0.01–0.36 vs 8 hard-negative false answers at 0.40–0.99) — raises F2's priority
       and adds a groundedness-gate option to the abstention design (see status.md).
3. [x] F3 — incremental indexing implemented 2026-07-02: embeddings.npy cache +
       per-doc checksum manifest; delta-only encode; FAISS-Flat/BM25 rebuilt from cached
       matrix (cheaper and deletion-safe vs HNSW add — HNSW deferred until Flat search
       latency matters at scale). Seed run pending; then corpus growth unblocked.
4. [x] F4 — done 2026-07-02. (1) _grounded_prompt hardened: <<<SOURCE id>>> delimiters +
       explicit data-not-instructions rule (shared by MLX and Ollama generators — duplicate
       prompt removed); delimiter-spoofing is itself a scanned pattern. (2) ingest_pdf
       .injection_scan: 8 instruction-pattern classes, recorded as injection_flags on each
       record + ingest warning (review-not-reject: legal text may quote such phrases).
       Retroactive scan of all 207 corpus records: 1 benign FP ("system prompt to change
       default password", broker master circular) — 0.5% FP rate. (3) API key check now
       secrets.compare_digest (timing-safe). (4) Binds verified 127.0.0.1 everywhere
       (Makefile serve, run.sh, ops_server); scraper URL patterns HTTPS-anchored to
       sebi.gov.in; checksum dedupe + provenance already recorded at ingest (§11).
5. [x] F2 — Qwen3-Reranker MLX benchmark run 2026-07-02: **rejected**. 0.6B-mxfp8 AUROC
       0.799 vs baseline 0.812; judge scores saturate ~0.99 on near-domain hard negatives;
       cit-prec@3 0.72 vs 0.80; 4.82 vs 2.24 s/q. Baseline bge-reranker-v2-m3 retained.
       Consequence: abstention redesign proceeds as a post-generation groundedness gate
       (new action item 7).
7. [x] Groundedness abstention gate — resolved 2026-07-02 with a PARTIAL outcome.
       LLM judges failed 3x (yes/no @1.5B lenient / @3B strict; closed-set identification
       @1.5B: 7 false abstains, 6/10 hn) — the protocol is scale-unstable and bluffable.
       **Adopted: deterministic SubjectSimJudge** — max cosine(query, subject line of
       top-k docs) via bge-m3, threshold 0.42, plus score floor 0.05 (was 0.4).
       golden_v5: abstention 0.77 → 0.875, gate false abstentions 0, all 45 answerable
       answered (recovers 5 score-gate false abstentions), 5/10 near-domain hard
       negatives caught, ~30ms. **Target 0.93 NOT met**: paraphrase queries (built to
       avoid subject vocabulary) and near-domain negatives overlap in subject-sim space
       (0.43–0.62 vs 0.35–0.56); no signal in the current stack separates them fully.
       Residual risk documented in status.md; revisit only with a new signal class
       (e.g. corpus-coverage/topic-inventory check), not more threshold tuning.
6. [ ] Update `docs/status.md` as each item lands.

## References

- arXiv:2510.06999 — Reliable Retrieval in RAG for Large Legal Datasets
- arXiv:2603.19251 — Metadata-Enriched RAG Pipelines for Legal LLMs
- OWASP GenAI Top 10 — LLM01:2025 Prompt Injection
- MLX embed/rerank support: github.com/ollama/ollama/issues/16076
- LanceDB vs FAISS: zilliz.com/comparison/faiss-vs-lancedb
