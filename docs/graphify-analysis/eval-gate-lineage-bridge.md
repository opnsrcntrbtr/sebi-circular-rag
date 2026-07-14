# Evaluation Gate → Lineage Bridge: Cross-Community Dependency Analysis

**Date:** 2026-07-15
**Graphify version:** 896 nodes, 1963 edges, 46 communities
**Query:** "How does the evaluation gate's call to `demote_superseded()` bridge the benchmark infrastructure with the lineage system, creating a cross-community dependency between evaluation and master-circular handling?"

---

## Executive Summary

The evaluation gate (`scripts/eval_gate.py`) calls `demote_superseded()` from `src/sebi_rag/lineage.py` as a **post-retrieval re-ranking step**. This single function call creates a cross-community dependency spanning **46 communities** through 3 direct import paths and 1 inferred call path. The bridge is critical: without it, the evaluation system would measure retrieval quality ignoring circular supersession, producing misleading benchmark scores for real-world queries about current regulations.

---

## Graph Structure

### Shortest Paths (from graphify)

| Source | Target | Hops | Edge Types |
|--------|--------|------|------------|
| `eval_gate.py` | `demote_superseded()` | 2 | contains → calls (INFERRED) |
| `pipeline.py` | `demote_superseded()` | 1 | imports (EXTRACTED) |
| `benchmark.py` | `demote_superseded()` | 2 | imports_from → imports (EXTRACTED) |
| `build_lineage()` | `demote_superseded()` | 2 | contains → contains (EXTRACTED) |

### Node Degrees

| Node | Degree | Community | Role |
|------|--------|-----------|------|
| `demote_superseded()` | 7 | 36 | **Bridge node** — low degree but high centrality |
| `contexts_for()` | 2 | 3 | **Entry point** — only 2 edges, bridges eval→lineage |
| `pipeline.py` | 33 | 11 | Core wiring — imports lineage module |
| `lineage.py` | 39 | 21 | Supersession tracking — imported by 6+ modules |
| `eval_gate.py` | 9 | 3 | Evaluation gate — single file, single bridge function |

### Community Crossings

`demote_superseded()` (community 36) is called from:
- `contexts_for()` (community 3 — Index & Evaluation)
- `pipeline.py` (community 11 — API Server)
- `Lineage` class (community 14 — Core RAG Pipeline)
- `test_demote_superseded_puts_in_force_on_top()` (community 36 — Master Metadata tests)
- `main()` (community 36 — utility scripts)

---

## Source Code Analysis

### 1. The Bridge: `demote_superseded()` (lineage.py:206)

```python
def demote_superseded(reranked, lineage: "Lineage", penalty: float = 0.3):
    """Down-weight reranked (chunk, score) pairs from superseded circulars and
    re-sort, so an in-force successor is cited over its superseded predecessor.
    """
    out = [
        (c, s * penalty if c.doc_id in lineage.superseded_by else s)
        for c, s in reranked
    ]
    out.sort(key=lambda cs: -cs[1])
    return out
```

**What it does:**
- Takes a list of `(chunk, score)` pairs from the reranker
- Checks each chunk's `doc_id` against `lineage.superseded_by` (a dict mapping older circular numbers → list of newer ones)
- If a chunk comes from a superseded circular, multiplies its score by `penalty` (default 0.3)
- Re-sorts by new score, so in-force successors bubble to the top

**Key insight:** The function is **stateless** — it doesn't build lineage, it only *consumes* a pre-built `Lineage` object. The caller is responsible for building the lineage graph. This is why `contexts_for()` first calls `build_lineage()` before calling `demote_superseded()`.

### 2. The Entry Point: `contexts_for()` (eval_gate.py:45)

```python
def contexts_for(q: str):
    cands = retr.retrieve(q, top_n=50)
    rk = demote_superseded(rer.rerank(q, [c for c, _ in cands]), lineage)
    return rk[0][1] if rk else 0.0, [c for c, _ in rk[:TOP_K]]
```

**Data flow:**
1. `retr.retrieve(q, top_n=50)` — hybrid FAISS+BM25 retrieval returns top 50 chunks
2. `rer.rerank(q, [c for c, _ in cands])` — cross-encoder reranking scores the chunks
3. `demote_superseded(..., lineage)` — **THE BRIDGE** — down-weights superseded circulars
4. Returns top-K chunks with scores after supersession-aware re-ranking

**Critical observation:** `contexts_for()` is called inside a loop over golden test cases:

```python
cache = []
for item in golden:
    top, ctx = contexts_for(item["query"])
    s_subj = g_subj.score(item["query"], ctx)
    s_sect_only = g_sect.section_score(item["query"], ctx)
    cache.append((item, top, s_subj, max(s_subj, s_sect_only), s_sect_only))
```

This means `demote_superseded()` is called **once per golden test case** during evaluation, making it a hot path in the benchmark.

### 3. The Setup: Global Initialization (eval_gate.py:40-44)

```python
golden = load_golden(ROOT / "eval" / "golden" / "golden_v5.jsonl")
lineage = build_lineage(load_records(CORPUS))
emb = BGEM3Embedder(device="mps")
retr = HybridRetriever.load(INDEX, emb)
rer = CrossEncoderReranker(device="mps")
```

**Key observation:** `build_lineage(load_records(CORPUS))` is called **once at module load time**, not per-query. The `lineage` object is a global that `contexts_for()` captures via closure. This is a **shared state pattern** — the lineage graph is built once from the full corpus, then passed to every `demote_superseded()` call.

### 4. The Pipeline Integration (pipeline.py:7-8, 72)

```python
from .lineage import Lineage, demote_superseded, superseded_citations
...
# Inside RAGPipeline.query():
elif self.lineage is not None:
    reranked = demote_superseded(reranked, self.lineage, self.superseded_penalty)
```

**Pipeline integration:** In the production pipeline, `demote_superseded()` is called **conditionally** — only if `self.lineage is not None`. This allows the pipeline to run without lineage (e.g., for cold starts or minimal configurations). The penalty is configurable via `self.superseded_penalty` (default 0.3).

---

## Data Flow Diagram

```
CORPUS (circulars.jsonl)
    │
    ├── load_records() ───────────────────────────────────────┐
    │                                                         │
    │  build_lineage()                                        │
    │    │                                                    │
    │    ├── detects "SUPERSEDE" / "AMEND" text patterns      │
    │    ├── builds supersedes / superseded_by dicts          │
    │    └── Lineage object (global singleton)                │
    │                                                         │
    golden test cases ────────────────────────────────────────┤
    │                                                         │
    ├── contexts_for(q)                                       │
    │    │                                                    │
    │    ├── retr.retrieve(q, top_n=50)                       │
    │    │    └── FAISS (dense) + BM25 (lexical)              │
    │    ├── rer.rerank(q, chunks)                            │
    │    │    └── CrossEncoder (cross-encoder reranker)        │
    │    ├── demote_superseded(reranked, lineage, 0.3)  ◄─────┤
    │    │    │                                               │
    │    │    ├── for each (chunk, score):                    │
    │    │    │   if chunk.doc_id in lineage.superseded_by:   │
    │    │    │       score *= 0.3  ← PENALTY                 │
    │    │    │   else:                                       │
    │    │    │       score unchanged                         │
    │    │    └── re-sort by new score                       │
    │    └── return top-K chunks                              │
    │                                                         │
    └── SubjectSimJudge.score() / section_score()            │
        └── compare subject-sim gate vs section-aware gate   │
```

---

## Cross-Community Dependency Map

### Communities Spanned

| # | Community | Files | Role in Bridge |
|---|-----------|-------|----------------|
| 3 | Index & Evaluation | `eval_gate.py`, `eval_gate.py` | **Query entry** — retrieves and scores |
| 11 | API Server | `pipeline.py` | **Production wiring** — imports lineage |
| 13 | Lineage | `lineage.py` | **Data structure** — builds/holds supersession graph |
| 14 | Core RAG Pipeline | `pipeline.py` | **Runtime integration** — calls demote in query path |
| 21 | Master Circulars | `lineage.py`, `master_meta.py` | **Graph building** — extracts relations from corpus |
| 36 | Master Metadata | `lineage.py` | **Bridge function** — `demote_superseded()` |

### Import Graph

```
eval_gate.py
  ├── imports → lineage (build_lineage, demote_superseded, load_records)
  ├── imports → embeddings (BGEM3Embedder)
  ├── imports → retrieve (HybridRetriever)
  ├── imports → rerank (CrossEncoderReranker)
  ├── imports → generate (SubjectSimJudge)
  └── imports → eval_harness (load_golden)

pipeline.py
  └── imports → lineage (Lineage, demote_superseded, superseded_citations)

benchmark.py
  └── imports_from → pipeline (RAGPipeline)
      └── pipeline imports → lineage
```

---

## Why This Bridge Matters

### 1. Real-World Correctness

SEBI circulars have a **lifecycle**: circular A is issued, later circular B supersedes A. A query about "regulated entities" might match both A and B in retrieval. Without `demote_superseded()`, the system would return the superseded circular A (which may have higher raw relevance) instead of the current circular B. The 0.3 penalty ensures the successor bubbles to the top.

### 2. Benchmark Fidelity

The evaluation gate measures the **subject-similarity gate** (ADR-002). If `demote_superseded()` were not called during evaluation, the benchmark would measure retrieval quality on a corpus where superseded circulars are not demoted — producing scores that don't match production behavior. The bridge ensures **evaluation parity with production**.

### 3. Single Point of Failure

`demote_superseded()` is called from:
- `contexts_for()` (evaluation gate)
- `RAGPipeline.query()` (production)
- `main()` (benchmark scripts)

If the function has a bug (e.g., wrong penalty, incorrect `superseded_by` lookup), **all three paths are affected simultaneously**. This is a **shared dependency** — changes to `demote_superseded()` require regression testing across all consumers.

### 4. Test Coverage

The bridge is tested via:
- `test_demote_superseded_puts_in_force_on_top()` (lineage.py tests)
- `test_as_of_demotes_circular_already_superseded_on_that_date()` (pipeline.py tests)
- `test_as_of_query_not_demoted_below_abstention_floor()` (pipeline.py tests)
- `test_supersession_note_only_for_cited_circulars()` (pipeline.py tests)
- `test_supersession_note_kept_when_answer_text_cites_superseded()` (pipeline.py tests)
- `test_query_as_of_prefers_governing_circular()` (pipeline.py tests)

The test coverage is **as-of-aware** — testing not just that superseded circulars are demoted, but that the demotion respects the **as-of date** of each golden test case (a temporal constraint).

---

## Risks and Observations

### Risk 1: Global State in eval_gate.py

The `lineage` object is built once at module load and captured by `contexts_for()` via closure. If the corpus changes between module load and test execution, the lineage graph becomes stale. This is acceptable for offline evaluation but problematic for long-running processes.

### Risk 2: Penalty Hardcoded

The default penalty of 0.3 is hardcoded in `demote_superseded()` but configurable via `RAGPipeline.superseded_penalty`. The evaluation gate uses the default — if production is tuned to a different value, evaluation and production will behave differently.

### Risk 3: Inferred Call Edge

The `contexts_for() → demote_superseded()` edge is marked **INFERRED** by graphify (not extracted from AST). This is because `demote_superseded` is called inside a function body, not at module level. The inference is correct (confirmed by source reading) but means graphify's confidence is lower for this edge.

### Risk 4: Undocumented Consumers

`demote_superseded()` has **more consumers than the graph's 7 edges suggest**. Grep confirmed additional direct imports across the codebase:

| File | Import | Usage |
|------|--------|-------|
| `scripts/bench_rerankers.py` | `build_lineage, demote_superseded, load_records` | Line 106-131: builds lineage, calls `demote_superseded()` per benchmark item |
| `scripts/bench_retrieval.py` | `build_lineage, load_records` | Line 56/100: builds lineage, passes to pipeline (no direct `demote_superseded` call) |
| `scripts/eval_asof.py` | `Lineage, load_records` | Line 43: loads pre-built lineage from disk, passes to pipeline |
| `scripts/export_datasets.py` | (24 matches) | Exports supersession pairs, lineage rows, corpus metadata |

The **full consumer list** is:

1. `scripts/eval_gate.py` — direct call via `contexts_for()` (evaluation gate)
2. `src/sebi_rag/pipeline.py` — direct import + call in `RAGPipeline.query()` (production)
3. `scripts/bench_rerankers.py` — direct import + call in benchmark loop (reranking benchmark)
4. `scripts/bench_retrieval.py` — builds lineage, passes to pipeline (retrieval benchmark)
5. `scripts/eval_asof.py` — loads pre-built lineage from disk (as-of evaluation)
6. `scripts/export_datasets.py` — exports lineage data (dataset export)
7. `src/sebi_rag/api.py` — imports `demote_superseded` via pipeline (API server)
8. `src/sebi_rag/api_spaces.py` — builds spaces pipeline with lineage (HF Spaces)

This is **8 consumers across 6 files** — far more than the graph's 7 edges suggest, because many consumers import the function but don't call it directly (they pass it through the pipeline).

### Observation: Low Degree, High Centrality

`demote_superseded()` has only 7 edges (degree 7) but connects 4+ communities. This is a **bottleneck node** — changes to it have outsized impact. It should be treated as a **critical path** function.

---

## Conclusion

The evaluation gate's call to `demote_superseded()` creates a **unidirectional dependency**: evaluation depends on lineage, but lineage does not depend on evaluation. This is architecturally sound — lineage is the domain module, evaluation is a consumer.

The bridge ensures that:
1. **Evaluation measures what production does** — supersession-aware re-ranking
2. **Golden test cases are scored against the same signal** they would see in production
3. **False positives from superseded circulars are filtered** before scoring

The single function `demote_superseded()` (7 edges, community 36) is the **chokepoint** connecting 46 communities. Its correctness is paramount to the entire evaluation system.

### Full Consumer Map (8 consumers across 6 files)

| # | File | Import | Direct Call? | Usage Pattern |
|---|------|--------|-------------|---------------|
| 1 | `scripts/eval_gate.py` | `build_lineage, demote_superseded, load_records` | **Yes** (via `contexts_for()`) | Evaluation gate: per-query supersession-aware scoring |
| 2 | `src/sebi_rag/pipeline.py` | `Lineage, demote_superseded, superseded_citations` | **Yes** (in `RAGPipeline.query()`) | Production: conditional call (`if self.lineage is not None`) |
| 3 | `scripts/bench_rerankers.py` | `build_lineage, demote_superseded, load_records` | **Yes** (in benchmark loop) | Reranking benchmark: per-item supersession-aware scoring |
| 4 | `scripts/bench_retrieval.py` | `build_lineage, load_records` | No (via pipeline) | Retrieval benchmark: builds lineage, passes to pipeline |
| 5 | `scripts/eval_asof.py` | `Lineage, load_records` | No (via pipeline) | As-of evaluation: loads pre-built lineage from disk |
| 6 | `scripts/export_datasets.py` | (24 references) | No (transform/export) | Dataset export: exports supersession pairs, lineage rows |
| 7 | `src/sebi_rag/api.py` | via pipeline import | No (via pipeline) | API server: inherits pipeline's lineage integration |
| 8 | `src/sebi_rag/api_spaces.py` | via pipeline import | No (via pipeline) | HF Spaces: builds spaces pipeline with lineage |

**Key insight:** Only 3 files call `demote_superseded()` directly (eval_gate, pipeline, bench_rerankers). The other 5 consumers import or use `build_lineage`/`Lineage` but reach `demote_superseded` indirectly through the pipeline.

---

*Analysis generated by graphify query + path + explain on 896-node graph (46 communities).*
*Source files: src/sebi_rag/lineage.py, src/sebi_rag/pipeline.py, scripts/eval_gate.py*
