# Intervention Scan Notes — Top Failure Buckets

Scanned 2026-07-16. Scope: top buckets from `buckets.md` — sparse_vocabulary_miss
(50%) + embedding_semantic_miss (30%) cover 80% of failures; chunking_defect
(10%) included because it links to the already-diagnosed nominee-count bug.
Recommendations only; nothing installed. All candidates must run locally on
Apple Silicon (MPS/CPU); no cloud APIs.

## Bucket: sparse_vocabulary_miss (5/10 failures)

Failures: para-freeze, probe-tbl-05, probe-sup-01, probe-par-01, probe-par-02.
Pattern: regulatory synonymy — query uses lay vocabulary (block/electronic
form/replaced/template/papers), corpus uses statutory vocabulary
(freeze/dematerialized/rescinded/Models of Agreement/documents).

### S1. Learned sparse retrieval (SPLADE-v3 class) replacing/augmenting BM25
- What: encoder produces weighted sparse term expansions; inverted-index
  lookup like BM25 but with learned synonymy. SPLADE-v3 significantly beats
  BM25 and compares well to cross-encoder rerankers
  ([SPLADE-v3 paper](https://www.emergentmind.com/papers/2403.06789),
  [overview](https://suhasbhairav.com/blog/splade-vs-bm25-learned-sparse-retrieval-vs-traditional-keyword-scoring)).
- Local feasibility: 110M-param BERT-base encoder; ~160 ms/doc offline
  indexing (78k chunks ≈ 3.5h CPU, less on MPS), 17–150 ms/query. Acceptable
  for this corpus size. Naver checkpoints are research-licensed —
  license check required before productizing; `efficient-splade` variants are
  more permissive.
- Integration surface: `retrieve.py` (`SparseIndex` swap or third RRF leg);
  index build in `HybridRetriever.build`.
- Effort: M–L. Expected gain: high for this bucket (directly targets learned
  term expansion); measured by re-running the probe benchmark.

### S2. Query-side lexical expansion with the local LLM (query2doc-lite / synonym injection)
- What: before BM25, expand the query with statutory synonyms — either a
  static SEBI glossary map (freeze↔block, demat↔electronic,
  rescind↔replace/withdraw/void) or a small local LLM rewrite
  ([Query2doc](https://arxiv.org/pdf/2303.07678),
  [query-rewriting survey](https://thegeocommunity.com/blogs/generative-engine-optimization/query-rewriting-multiquery-rag/)).
- Local feasibility: glossary variant is zero-dep, deterministic, testable
  offline; LLM variant adds latency (+0.5–2s) on the existing local model.
- Integration surface: `retrieve.py` `SparseIndex.search` (query-side only —
  no reindex needed).
- Effort: S (glossary) / M (LLM). Expected gain: medium-high; glossary variant
  is the cheapest intervention in this report and directly addresses 5
  observed failures.

### S3. BM25 field boosting (subject/section weighting)
- What: weight subject + section-heading terms higher than body terms.
- Local feasibility: bm25s supports per-field indexing via text composition;
  trivial infra.
- Integration surface: chunk text enrichment already prefixes doc/subject —
  tune repetition/weighting in `segment.py` enrichment or a bm25s field index.
- Effort: S. Expected gain: low-medium here (failures were body-level
  synonymy, not heading mismatch); cheap to sweep during calibration.

## Bucket: embedding_semantic_miss (3/10 failures)

Failures: para-aifmaster, para-parrva, probe-sup-04.
Pattern: heavy paraphrase or entity-anchored questions that bge-m3 does not
map to the answer chunk, even when the doc is found via siblings.

### E1. HyDE / hypothetical-answer embedding at query time
- What: local LLM drafts a hypothetical statutory answer; embed that instead
  of (or fused with) the raw query
  ([HyDE overview](https://www.emergentmind.com/topics/hypothetical-document-embeddings-hyde),
  caveats on knowledge leakage: [rethinking LLM query expansion](https://arxiv.org/pdf/2504.14175)).
  Reported gains up to +4–6% recall on BEIR-style suites; on small local
  models expect latency +43–60% and hallucination risk on out-of-domain
  queries.
- Local feasibility: uses the existing local generator; no new models.
- Integration surface: `retrieve.py` `DenseIndex.search` (query-side).
- Effort: M. Expected gain: medium for paraphrase-class failures
  (para-aifmaster); measured on probes + golden para-* items.

### E2. Contextual chunk headers / contextual retrieval at index time
- What: prepend a generated 50–100-token context line ("this clause sits
  under section X about Y of circular Z") to each chunk before embedding —
  Anthropic reports ~35% retrieval-failure reduction
  ([Anthropic contextual retrieval](https://www.anthropic.com/news/contextual-retrieval),
  [contextual chunking](https://unstructured.io/blog/contextual-chunking-in-unstructured-platform-boost-your-rag-retrieval-accuracy)).
  Also directly helps the chunking_defect bucket (orphaned clauses regain
  their governing context).
- Local feasibility: one-time offline pass with the local LLM over 78k chunks
  (hours, not days, on M-series; incremental via F3 manifest); deterministic
  cheaper variant: template headers from existing section metadata (no LLM).
- Integration surface: `segment.py` enrichment (chunk text prefix already
  exists — extend it with parent-clause text), then `make reindex`.
- Effort: S (template variant) / M (LLM variant). Expected gain: high — the
  single intervention that touches BOTH embedding_semantic_miss and
  chunking_defect, plus BM25 term availability (sparse bucket) as a side
  effect.

### E3. Multi-vector / late-interaction reranking pool widening
- What: raise retriever pool beyond 50 for the reranker (the cross-encoder
  rescued 4/7 candidate-set survivors; para-aifmaster sat at fused 47 —
  pool width is the binding constraint for rescues). Sweep pool 50→100–150
  with reranker latency budget.
- Local feasibility: pure parameter change; reranker cost scales linearly
  (~2x latency at pool 100).
- Integration surface: `pipeline.query(pool=...)` + `make calibrate` sweep.
- Effort: S. Expected gain: medium; cheapest recall lever for ranked-low
  failures.

## Bucket: chunking_defect (1/10 observed + known nominee-bug class)

Failure: probe-par-03 (orphaned sub-clauses 4.1.1.1–.5); same family as the
nominee-count bug (bodyless headings) documented in repo memory.

### C1. Clause-context folding (parent-clause prefix on list items)
- What: when a chunk is a bare list item (`4.1.1.2. …;`), prepend the
  governing clause text (`4.1.1 On and from the date of the Order… the CRA
  shall:`) during segmentation — the deterministic cousin of E2.
- Local feasibility: pure `segment.py` logic; no models.
- Integration surface: `segment.py` `hierarchical_chunk` / `_paragraphs`;
  reindex after.
- Effort: S-M. Expected gain: high for this class (answer chunks become
  retrievable by both retrievers); verify with probe-par-03 + a new
  list-item probe set.

### C2. Parent-document (small-to-big) retrieval
- What: retrieve on small chunks, return the enclosing section to the
  reranker/generator
  ([PDR overview](https://dzone.com/articles/parent-document-retrieval-useful-technique-in-rag),
  [chunking strategies](https://langcopilot.com/posts/2025-10-11-document-chunking-for-rag-practical-guide)).
- Local feasibility: no models; needs parent-pointer bookkeeping in `Chunk`
  and retrieval-time expansion.
- Integration surface: `segment.py` (parent ids) + `retrieve.py`/`rerank.py`.
- Effort: M. Expected gain: medium-high but larger blast radius than C1.

## Non-findings (for completeness)

- extraction_loss: 0 observed — layout-aware PDF parsers (Docling/Marker)
  are NOT justified by this evidence; do not prioritize.
- metadata_filter_loss: 0 observed — validity/as-of scoping did not cause
  any harvested miss.
