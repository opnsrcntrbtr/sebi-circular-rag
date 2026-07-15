# Pre-retrieval Pipeline Failure Taxonomy & Intervention Ranking — Design

**Date:** 2026-07-16
**Status:** Approved (brainstorming complete)
**Type:** Research only — no production code changes

## Goal

Rank enhancement interventions for the initial stages of the SEBI circular RAG
pipeline — scrape → PDF ingestion (`ingest_pdf.py`) → chunking (`segment.py`)
→ indexing (`embeddings.py`, FAISS/BM25) → hybrid retrieval (`retrieve.py`) —
by expected impact, grounded in qualitative failure analysis rather than a
survey of techniques. Generation and answer synthesis are out of scope;
reranking is observed only to attribute failures, not to be improved here.

## Approach (approved)

Failure-taxonomy-first: harvest real retrieval failures, trace each backwards
through the pipeline to a single root-cause bucket, rank buckets by
frequency × fixability, then do a targeted literature/tooling scan only for
the top buckets.

## Deliverable

A report at `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md` containing:

1. **Failure taxonomy** — buckets with per-bucket evidence (failure IDs, query
   text, trace summary).
2. **Ranked intervention list** — each entry states: target bucket(s) and
   failure IDs it addresses, expected metric gain (qualitative tier is
   acceptable: high/medium/low with reasoning), new dependencies (must run
   locally on Apple Silicon; new deps such as Docling/Marker/SPLADE are
   allowed), effort estimate, and how a follow-up implementation would
   measure success.
3. **Appendix** — raw failure traces.

Scratch analysis scripts live in `scripts/analysis/` and are throwaway unless
a later plan promotes them.

## Failure harvesting (two sources)

**Golden misses.** Run the retrieval benchmark (`scripts/bench_retrieval.py`,
non-smoke, real index + BGE-M3) against `eval/golden/golden_v6.jsonl`.
Extract:

- *Candidate-set misses*: queries where the gold chunk is absent from the
  hybrid retriever's top-k, with k set to the reranker-input cutoff — these
  implicate ingestion/chunking/indexing/retrieval.
- *Ranked-low hits* (captured separately): gold chunk retrieved but ranked
  low by fusion/reranker — these implicate fusion or reranking, not the
  earlier stages, and are reported as a distinct category.

**Probe queries.** ~25 handcrafted queries targeting suspected blind spots:

- table and annexure content
- numeric facts (nominee-count class of failure)
- supersession / as-of phrasing
- definitional lookups likely to hit heading-only degenerate chunks
- paraphrase / vocabulary-mismatch queries

Probe queries are written with expected source circulars/sections identified
manually so misses are verifiable.

## Root-cause tracing

Each failure is walked backwards through the pipeline with a fixed checklist:

1. Is the answer text present in the ingested text (`ingest_pdf.py` output)?
2. Does it land in a coherent chunk (`segment.py`)?
3. Does dense-only retrieval find it? Does sparse-only (BM25)? (isolates
   FAISS vs BM25 vs fusion)
4. If retrieved, where does the reranker place it?

Each failure is assigned exactly one **primary** bucket:

| Bucket | Meaning |
|---|---|
| extraction loss | answer text absent/garbled after PDF ingestion |
| chunking defect | text present but split incoherently / heading-only chunk |
| embedding-semantic miss | dense retrieval fails despite a good chunk |
| sparse-vocabulary miss | BM25 fails despite a good chunk |
| fusion-ranking loss | found by one retriever but lost in hybrid fusion or downranked |
| metadata-filter loss | excluded by validity/as-of/metadata scoping |

Secondary contributing causes may be noted but do not affect bucket counts.

## Intervention ranking

Buckets ranked by frequency × fixability. Literature/tooling scan is scoped
to the top buckets only (examples: Docling/Marker if extraction dominates;
chunk-repair of bodyless headings if chunking dominates; SPLADE or query
expansion if vocabulary mismatch dominates). No implementation in this
effort.

## Success criteria

- ≥90% of harvested failures assigned a primary bucket with evidence.
- Top 3 interventions each traceable to specific failure IDs.
- Report committed and reviewed.

## Constraints

- Local-first: everything must run on Apple Silicon (MPS); new local
  dependencies are acceptable, cloud APIs are not.
- Quick research: prefer existing tooling (bench-retrieval, golden v6, TREC
  runfiles) over new instrumentation.
