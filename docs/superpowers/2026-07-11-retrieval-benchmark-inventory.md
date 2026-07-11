# Retrieval-Benchmark Inventory — 2026-07-11

## Purpose

Read-only inventory of the pieces a new retrieval-only benchmark would touch:
chunker output schema, retrieval/rerank interfaces, the lineage graph, the
Golden v6 query schema, and the existing evaluation runner. No code was
changed to produce this document. Companion to
`docs/superpowers/2026-07-09-benchmark-evaluation-handoff.md`, which covers
the benchmark-export slice already shipped.

## 1. Section-aware chunker (`src/sebi_rag/segment.py`)

- `CircularMeta` (frozen dataclass, `segment.py:14`) — per-circular metadata:
  `circular_number`, `issue_date`, `effective_date`, `subject`,
  `issuing_department`, `supersession_status` (`in_force | superseded |
  amended`), `amendment_history: tuple[str, ...]`,
  `version_lineage: tuple[str, ...]`.
- `Chunk` (frozen dataclass, `segment.py:26`) — output unit:
  - `id: str` — stable citation id, format `"{circular_number}#{section}#{para_idx}"`.
  - `doc_id: str` — the circular number.
  - `section: str` — hierarchy path `"{circular_number}/{section_name}/p{para_idx}"`.
  - `text: str` — enriched chunk body: a header line
    `"{circular_number} | {subject[:120]} | {section_name}"` prepended to the
    paragraph text (ADR-001 "F1" contextual enrichment, for dense/sparse
    disambiguation of topically-overlapping circulars).
  - `meta: dict[str, Any]` — `asdict(CircularMeta)`.
- `_paragraphs(text, max_chars)` (`segment.py:34`) — splits on blank lines,
  then single newlines, then sentence boundaries (`(?<=[.;:])\s+`), then hard
  character windows as a last resort; never splits mid-line if avoidable.
- `hierarchical_chunk(text, meta, max_chars=1200, overlap_chars=150) -> list[Chunk]`
  (`segment.py:71`) — the entry point. Section boundaries are detected by a
  leading numbered-heading regex `^\s*(\d+(\.\d+)*)[.)]\s+\S` (e.g. "2.
  Applicability"); paragraphs are packed into a buffer up to `max_chars` with
  `overlap_chars` of trailing context carried into the next chunk. Section
  name defaults to `"preamble"` before the first heading.

## 2. BM25 / dense / hybrid / rerank interfaces (`src/sebi_rag/retrieve.py`, `rerank.py`)

**Dense** — `DenseIndex` (`retrieve.py:30`): FAISS `IndexFlatIP` over
L2-normalized vectors (cosine via inner product). `build(texts) -> np.ndarray`,
`build_from_vecs(vecs)`, `search(query, k) -> list[tuple[int, float]]`
(row-index, score pairs into the chunk list).

**Sparse** — `SparseIndex` (`retrieve.py:52`): wraps `bm25s.BM25`.
`build(texts)`, `search(query, k) -> list[tuple[int, float]]`.

**Fusion** — `rrf_fuse(rankings, k_const=60, top_n=50) -> list[tuple[int, float]]`
(`retrieve.py:71`): Reciprocal Rank Fusion, rank-only (sidesteps dense/sparse
score-scale mismatch).

**Hybrid retriever** — `HybridRetriever` (`retrieve.py:86`, dataclass):
fields `chunks: list[Chunk]`, `dense: DenseIndex`, `sparse: SparseIndex`,
`vecs: np.ndarray | None`.
  - `HybridRetriever.build(chunks, embedder) -> HybridRetriever` — full build.
  - `HybridRetriever.build_incremental(chunks, embedder, path) -> tuple[HybridRetriever, dict]`
    — per-doc checksum manifest (`_doc_checksum`), reuses cached embedding
    rows for unchanged docs, re-encodes only changed/new docs, rebuilds
    FAISS+BM25 from the assembled matrix. Falls back to full build if no
    cache exists.
  - `retrieve(query, k_dense=50, k_sparse=50, top_n=50) -> list[tuple[Chunk, float]]`
    — dense search + sparse search fused by RRF, chunk objects resolved.
  - `save(path)` / `load(path, embedder)` — persists `dense.faiss`, `bm25/`,
    `chunks.jsonl`, `meta.json`, plus `embeddings.npy` + `manifest.json` when
    `vecs` is present.
  - `index_exists(path) -> bool` — checks for `dense.faiss` + `meta.json`.

**Reranker protocol** — `Reranker` (`rerank.py:15`, `runtime_checkable`
`Protocol`): `rerank(query, candidates: list[Chunk]) -> list[tuple[Chunk, float]]`.
Three implementations conform to it:
  - `LexicalReranker` (`rerank.py:22`) — deterministic query-term-coverage
    scorer; used for offline tests/fallback, not production.
  - `Qwen3MLXReranker` (`rerank.py:73`) — causal-LM yes/no judge reranker via
    MLX (Apple Silicon); benchmark candidate only, pinned to
    `mlx-community/Qwen3-Reranker-{0.6B,4B}-mxfp8`.
  - `CrossEncoderReranker` (`rerank.py:115`) — production reranker,
    `BAAI/bge-reranker-v2-m3` via `sentence_transformers.CrossEncoder` on
    `mps`.

## 3. Lineage / supersession graph (`src/sebi_rag/lineage.py`)

- `Lineage` (`lineage.py:52`, dataclass) — four adjacency dicts keyed by
  circular number:
  - `supersedes: dict[str, list[str]]` — newer → \[older\]
  - `superseded_by: dict[str, list[str]]` — older → \[newer\] (inverse of above)
  - `amends: dict[str, list[str]]` — amender → \[amended\]
  - `amended_by: dict[str, list[str]]` — amended → \[amender\] (inverse)
  - `status(circular_number) -> "superseded" | "amended" | "in_force"`.
  - `save(path)` / `load(path)` — flat JSON of the four dicts.
- **Relation types**: `supersedes`, `amends`, `references` (the third is
  detected but not stored as a graph edge — see below). Detected by
  `detect_relations(circular_number, text) -> list[tuple[relation, ref]]`
  (`lineage.py:29`), which finds all `REF_RE` (from `ingest_pdf.py`) matches
  and classifies each by proximity to trigger phrases:
  - `SUPERSEDE_RE` — "in supersession of", "supersed*", "rescind*",
    "repeal*", "stands withdrawn", etc. Any reference occurring *after* the
    first supersession trigger in the text is `supersedes`.
  - `AMEND_RE` — "in (partial) modification of", "amend*". A reference within
    120 chars of an amend trigger is `amends`.
  - Otherwise `references` (not persisted into `Lineage` edges — only
    `supersedes`/`amends` become graph edges).
- **Edge provenance** — two build paths in `build_lineage(records) -> Lineage`
  (`lineage.py:102`):
  1. Explicit textual triggers per-document via `detect_relations` (grounded
     in circular text — "authoritative-text rule": only asserts what the text
     states, ambiguous refs stay `references` and are dropped).
  2. Master-circular re-issue inference: `mc_topic(subject)` (`lineage.py:80`)
     normalizes "Master Circular for/on \<TOPIC\>" titles; circulars sharing a
     topic are grouped, sorted by `_currency` (max of issue/effective date),
     and the newest is asserted to supersede all older ones in the group.
- **Consumers**: `demote_superseded(reranked, lineage, penalty=0.3)`
  (`lineage.py:140`) — down-weights reranked chunks from superseded
  circulars post-rerank. `superseded_citations(citations, lineage)`
  (`lineage.py:152`) — maps cited-but-superseded circulars to their
  successors for answer-time warnings. `annotate_corpus(corpus_path)`
  (`lineage.py:175`) — idempotently writes `supersession_status`,
  `superseded_by`, `supersedes` back onto each corpus record.

## 4. Golden v6 schema and evaluation runner

**Schema** (built by `enrich_golden_item` / `build_golden_v6`,
`src/sebi_rag/benchmark.py:111`, validated by `validate_golden`
(`benchmark.py:160`)). Per-row fields:

| field | type | notes |
|---|---|---|
| `id` | str | unique |
| `query` | str | |
| `relevant_circulars` | list[str] | required unless `abstain` |
| `relevant_chunks` | list[str] | optional chunk-level override (grade 2 in qrels) |
| `answer_contains` | str | legacy; superseded by `must_contain` |
| `must_contain` | list[str] | |
| `must_not_contain` | list[str] | |
| `abstain` | bool | if true, `relevant_circulars` must be empty |
| `task_type` | str | one of `TASK_TYPES` (`benchmark.py:24`): `title_direct`, `body_paraphrase`, `numeric_table`, `lineage_supersession`, `exact_circular`, `hard_negative`, `far_negative` |
| `difficulty` | str | one of `DIFFICULTIES`: `easy`, `medium`, `hard` |
| `expected_citation_level` | str | one of `CITATION_LEVELS`: `none`, `circular`, `chunk` |
| `rationale` | str | free text |
| `label_source` | str | e.g. `golden_v5` |
| `review_status` | str | one of `REVIEW_STATUSES`: `seeded`, `draft`, `reviewed`, `adjudicated` |

Live at `eval/golden/golden_v6.jsonl` — currently 56 rows, all
`review_status=seeded` (carried over from `golden_v5`; see
`2026-07-09-benchmark-evaluation-handoff.md` for the expansion plan to ~200
reviewed items).

**Evaluation runners** — two, at different layers:

1. `src/sebi_rag/eval_harness.py` — end-to-end (retrieval + generation)
   golden-set runner.
   - `load_golden(path) -> list[dict]` (`eval_harness.py:49`).
   - `run_eval(pipeline: RAGPipeline, golden, k=10) -> EvalReport`
     (`eval_harness.py:58`) — calls `pipeline.query(item["query"])` per item
     and computes `EvalReport` (`eval_harness.py:34`): `recall_at_k`, `mrr`,
     `ndcg_at_k` (via `src/sebi_rag/eval.py`'s `recall_at_k`/`mrr`/`ndcg_at_k`),
     `citation_precision`, `citation_recall`, `abstention_accuracy`,
     `groundedness_proxy` (substring hit on `answer_contains`),
     `faithfulness` (bracketed-citation grounding from `Answer.faithfulness`),
     `avg_latency_s`, `k`.
   - `report_dict(report) -> dict`.
   - Doc/chunk convention: chunk id `"<circular_number>#<section>#<para>"`;
     `_doc(chunk_id)` splits on first `#` to get the circular number, so
     metrics are computed at circular level even though retrieval is
     chunk-level.

2. `src/sebi_rag/benchmark.py` — retrieval-only benchmark + export layer
   (added in the 2026-07-09 slice; intentionally decoupled from
   `eval_harness.py`/production pipeline behavior).
   - `run_retrieval_benchmark(pipeline, golden, top_n=50, run_name=...) -> dict`
     (`benchmark.py:293`) — calls `pipeline.retriever.retrieve(...)` directly
     (skips rerank/generation), reports `recall_at_10` and
     `avg_retrieval_latency_s`, plus raw `rankings` (`{query_id: [(chunk_id,
     score), ...]}`).
   - `export_beir(chunks, golden, out_dir)` (`benchmark.py:279`) — writes
     BEIR-style `corpus.jsonl`/`queries.jsonl`/`qrels/test.tsv` via
     `beir_corpus_rows`, `beir_query_rows`, `qrels_rows` (`benchmark.py:205,
     227, 231`).
   - `write_trec_run(path, run_name, rankings)` (`benchmark.py:267`) — TREC
     runfile format.
   - `run_metadata(...)` (`benchmark.py:78`) — reproducibility stamp: git
     commit, python/platform, model IDs, params, relevant env vars, corpus /
     index / golden checksums (`sha256_file`, `dir_fingerprint`).
   - CLI: `scripts/bench_retrieval.py` — `--smoke` (offline, `HashEmbedder` +
     `LexicalReranker`, synthetic single-item golden set via
     `smoke_pipeline()`) or real mode (loads persisted `data/index` +
     `BGEM3Embedder(device="mps")` + `CrossEncoderReranker(device="mps")` +
     `data/corpus/circulars.jsonl` lineage). Writes `run.trec` +
     `results.json` (metrics + metadata, rankings excluded — they live in the
     TREC file) under `eval/runs/baseline_retrieval/` by default. Wired to
     `make bench-retrieval`.
   - Only `recall_at_10` and latency are computed inline; nDCG@10/MAP/
     Precision@k from qrels + TREC runs are on the "Recommended Next Tasks"
     list in the 2026-07-09 handoff, not yet implemented.

## 5. Where a new retrieval-only benchmark fits with minimal disruption

The retrieval-only path already exists and is deliberately decoupled from
generation/production pipeline behavior — extending it is additive, not a
new subsystem:

- **New metrics** (nDCG@10, MAP, Precision@k, per-`task_type` /
  `difficulty` breakdowns) belong in `src/sebi_rag/eval.py` (currently just
  `recall_at_k`, `mrr`, `ndcg_at_k` — `eval.py:11,18,25`) and get consumed by
  `run_retrieval_benchmark` in `benchmark.py:293`, which already returns a
  plain dict — additional keys are backward compatible with
  `scripts/bench_retrieval.py`'s `results.json` writer.
- **New retriever/reranker variants to benchmark** (e.g. `Qwen3MLXReranker`,
  alternate `k_dense`/`k_sparse`/`top_n` or RRF `k_const`) plug in at
  `scripts/bench_retrieval.py`'s pipeline-construction block
  (`bench_retrieval.py:91-113`) without touching `benchmark.py` — the script
  already takes `--top-n` and constructs `RAGPipeline` explicitly, so a new
  `--reranker` flag or a second script following the same pattern
  (`scripts/bench_rerankers.py` already exists as precedent) is the natural
  extension point.
  - `run_retrieval_benchmark` calls `pipeline.retriever.retrieve(...)`
    directly and never touches `pipeline.reranker`, so **reranker
    comparisons need a small new function** (e.g.
    `run_reranked_retrieval_benchmark`) that also calls
    `pipeline.reranker.rerank(...)` on the retrieved pool — today rerank
    quality is only exercised indirectly through `eval_harness.run_eval`'s
    end-to-end citations, not isolated.
- **Golden-set slices for the new benchmark** (e.g. per-`task_type` recall)
  can filter `eval/golden/golden_v6.jsonl` rows in-memory by `task_type`
  before calling `run_retrieval_benchmark` — no schema change needed since
  `task_type`/`difficulty`/`expected_citation_level` are already present on
  every row.
- **Qrels/TREC export is reusable as-is**: `qrels_rows` already produces
  grade-1 (circular-expanded) vs grade-2 (`relevant_chunks`-curated) labels,
  so any external TREC-eval tool (`trec_eval`, `ir_measures`) can run against
  `write_trec_run`'s output without further plumbing.
- **Reproducibility metadata** (`run_metadata`) is generic and takes
  arbitrary `models`/`params` dicts, so a new benchmark variant just needs to
  pass its own model/param labels — no changes required there.
- **Avoid**: adding a new benchmark runner directly inside
  `eval_harness.py` — that module is intentionally coupled to full
  pipeline `.query()` (generation + abstention), per its docstring ("P1").
  The existing split (retrieval-only in `benchmark.py`, end-to-end in
  `eval_harness.py`) should be preserved per the 2026-07-09 handoff's design
  decision to "keep benchmark concerns separate from production RAG
  behavior."

## Files read for this inventory (not modified)

`src/sebi_rag/segment.py`, `src/sebi_rag/retrieve.py`, `src/sebi_rag/rerank.py`,
`src/sebi_rag/lineage.py`, `src/sebi_rag/benchmark.py`,
`src/sebi_rag/eval_harness.py`, `src/sebi_rag/pipeline.py`,
`scripts/bench_retrieval.py`, `docs/superpowers/2026-07-09-benchmark-evaluation-handoff.md`.
