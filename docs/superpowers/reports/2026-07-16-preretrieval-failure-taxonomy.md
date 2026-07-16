# Pre-retrieval Failure Taxonomy & Ranked Interventions

**Date:** 2026-07-16
**Spec:** `docs/superpowers/specs/2026-07-16-preretrieval-failure-taxonomy-design.md`
**Plan:** `docs/superpowers/plans/2026-07-16-preretrieval-failure-taxonomy.md`
**Scope:** research only — findings and recommendations; no production code changed.

## 1. Method & baseline

Failures were harvested from two sources against the real persisted index
(FAISS + BM25, BGE-M3 on MPS, top-50 candidates = the reranker-input pool):
(a) golden v6 (56 items, 45 answerable) and (b) 25 handcrafted probe queries
(`eval/probes/probes_v1.jsonl`) targeting suspected blind spots, each with a
corpus-verified `must_contain` answer string. Misses were classified at two
levels: **doc-level** (relevant circular in top-10 deduped docs) and
**answer-level** (a retrieved chunk actually carries the answer text — the
spec's "gold chunk in top-k" criterion). Every failure was traced backwards
through the pipeline (corpus text → chunk → dense-only / sparse-only / fused
rank → reranker placement) by `scripts/analysis/trace_failure.py` and manually
assigned one primary bucket (`eval/runs/ft-traces/buckets.md`).

Baselines: golden doc-level recall@10 = **0.956**; probe doc-level recall@10 =
**0.96**. Doc-level retrieval is near-saturated — but at the answer-chunk
level, 3/45 golden and 7/25 probe queries fail. **The pipeline's real
bottleneck up to retrieval is answer-chunk recall, not document recall.**

## 2. Failure taxonomy (10 failures: 3 golden, 7 probes)

| bucket | count | % | exemplars |
|---|---|---|---|
| sparse_vocabulary_miss | 5 | 50% | para-freeze, probe-par-02, probe-sup-01 |
| embedding_semantic_miss | 3 | 30% | para-aifmaster, para-parrva, probe-sup-04 |
| chunking_defect | 1 | 10% | probe-par-03 |
| fusion_ranking_loss | 1 | 10% | probe-num-05 |
| extraction_loss | 0 | 0% | — |
| metadata_filter_loss | 0 | 0% | — |

Exemplar traces (full set in `eval/runs/ft-traces/traces.jsonl`, decisions in
`buckets.md`):

- **para-freeze** (golden, candidate miss): query "block all outgoing
  transactions from their folio" vs corpus "freeze" — BM25 never finds it,
  dense only at rank 43, RRF cuts it from the top-50 entirely.
- **para-aifmaster** (golden, ranked low): "Category II private pooled
  investment vehicle" for "Alternative Investment Fund" defeats dense (24),
  sparse (33), and reranker (16) alike — pure paraphrase gap.
- **probe-par-03** (probe, answer-level candidate miss): CRA-master
  sub-clauses 4.1.1.1–4.1.1.5 are chunked as bare list items severed from the
  governing clause carrying the "winding down / surrender" context, so no
  retriever can reach them — same context-orphaning family as the
  nominee-count bug.
- **probe-sup-04** (probe, answer-level candidate miss): the rescission clause
  naming appendix Sl.No. 68-74 is never retrieved by either retriever even
  though its document ranks top-10 via sibling chunks.

Ranked-low hits are reported separately per spec: in 4 of 10 failures
(probe-num-05, probe-sup-01, probe-par-01, probe-par-02) the cross-encoder
**reranker rescues** the answer chunk into the top-10, muting end-to-end
impact. The reranker is the strongest component in the pipeline; the highest
leverage is getting answer chunks into its pool at all.

Cross-cutting: no extraction losses (ingested text contained the answer in
all 10 cases) and no metadata-filter losses were observed. Layout-aware PDF
parsing (Docling/Marker) is **not** justified by current evidence.

## 3. Ranked interventions

Ranked by (failures addressed × expected gain) ÷ effort. Details and sources
in `eval/runs/ft-traces/interventions-notes.md`.

### #1 — Contextual chunk enrichment: clause-context folding + template headers
- **Buckets:** chunking_defect + embedding_semantic_miss + sparse_vocabulary_miss (side effect). **Failure IDs:** probe-par-03, para-parrva, probe-sup-04, plus the known nominee-count class.
- **What:** in `segment.py`, (a) fold governing-clause text into bare list-item chunks (4.1.1.x class), and (b) extend the existing `doc | subject | …` prefix into a fuller template context header (section path + parent-clause lead). Deterministic — no models, no new deps. The LLM-generated variant (Anthropic contextual retrieval, ~35% failure reduction reported) is a follow-on if the template variant under-delivers.
- **Effort:** S–M. **Expected gain:** high — the only intervention touching three buckets.
- **Measurement:** `make reindex`, re-run both benchmarks + `extract_misses.py`; success = probe answer-level failures drop ≥50% (7→≤3), golden answer-level failures do not regress.

### #2 — Query-side lexical expansion for BM25 (SEBI glossary, then LLM rewrite)
- **Buckets:** sparse_vocabulary_miss. **Failure IDs:** para-freeze, probe-tbl-05, probe-sup-01, probe-par-01, probe-par-02.
- **What:** statutory-synonym expansion of the query before `SparseIndex.search` (freeze↔block, dematerialized↔electronic, rescinded↔replaced/void, …); deterministic glossary first, local-LLM query2doc as a second stage. Query-side only — no reindex.
- **Effort:** S (glossary) / M (LLM). **Expected gain:** high for the largest bucket; directly addresses 5/10 failures.
- **Measurement:** re-run probe benchmark; success = sparse rank of the 5 failure IDs improves from -1 to top-50 and answer-level class improves for ≥3 of them.

### #3 — Reranker pool widening (50 → 100–150 sweep)
- **Buckets:** fusion_ranking_loss + every rescued ranked-low. **Failure IDs:** probe-num-05, para-aifmaster (fused 47), para-freeze (cut at fusion).
- **What:** parameter sweep of `pipeline.query(pool=…)` and RRF `top_n` with reranker latency budget via `make calibrate`. The reranker rescued 4/7 candidate-set survivors — widening its input is the cheapest recall lever available.
- **Effort:** S. **Expected gain:** medium; immediate.
- **Measurement:** calibration sweep report — answer-level ranked_low count at pool 100 vs 50, with p95 query latency delta ≤2×.

### #4 — Learned sparse retrieval (SPLADE-class) as third RRF leg
- **Buckets:** sparse_vocabulary_miss (structural fix). **Failure IDs:** same 5 as #2.
- **What:** replace/augment BM25 with a learned sparse encoder. Higher ceiling than #2 but new model dependency (110M encoder, ~3.5h index pass locally, license check needed on SPLADE-v3 checkpoints).
- **Effort:** M–L. **Expected gain:** high, but only pursue if #2's glossary variant plateaus.
- **Measurement:** BEIR-style export (`make benchmark-export`) A/B: BM25 vs SPLADE vs BM25+SPLADE fusion.

### #5 — HyDE-style query embedding (local LLM)
- **Buckets:** embedding_semantic_miss residue. **Failure IDs:** para-aifmaster, para-parrva.
- **What:** embed a locally generated hypothetical statutory answer instead of the raw query for dense search. Latency +43–60% and hallucination risk on small models — last in line.
- **Effort:** M. **Expected gain:** medium, uncertain.
- **Measurement:** golden para-* items + probes; recall delta must survive an as-of/abstention regression run.

## 4. Appendix

- Raw traces: `eval/runs/ft-traces/traces.jsonl` (10 rows, per-stage ranks).
- Bucket decisions + evidence: `eval/runs/ft-traces/buckets.md`.
- Intervention scan with sources: `eval/runs/ft-traces/interventions-notes.md`.
- Probe set: `eval/probes/probes_v1.jsonl` (25 rows, all `must_contain` corpus-verified).
- Runs: `eval/runs/ft-golden/`, `eval/runs/ft-probes/` (TREC runfiles + reproducibility metadata).
- Analysis scripts (throwaway unless promoted): `scripts/analysis/extract_misses.py` (tested: `tests/test_extract_misses.py`), `scripts/analysis/trace_failure.py`.

## Self-check vs spec success criteria

- [x] ≥90% of harvested failures assigned a primary bucket with evidence — 10/10 (100%).
- [x] Top 3 interventions traceable to specific failure IDs — each entry lists them.
- [x] Report committed; artifacts verified to exist at the paths above.
