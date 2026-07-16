# Pre-retrieval Interventions (Top-3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and measure the top-3 ranked interventions from `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md` — query-side lexical expansion for BM25, reranker pool widening, and governing-clause chunk enrichment — to cut answer-level retrieval failures (probes 7→≤3, golden not regressing above 3).

**Architecture:** Intervention #2 (glossary expansion) is a new pure module `expand.py` wired into the sparse leg of `HybridRetriever.retrieve` — query-side only, no reindex. Intervention #3 (pool widening) is a research sweep script over `retrieve(top_n=…)` + reranker with a conditional default bump in `pipeline.query`. Intervention #1 (clause-context folding) extends `segment.hierarchical_chunk` to prepend the nearest recorded ancestor heading line to each chunk body, then requires `make reindex` and full re-measurement.

**Tech Stack:** Python 3.12, bm25s, FAISS, bge-m3 (MPS), bge-reranker-v2-m3, pytest. No new dependencies.

## Global Constraints

- No new package dependencies; everything deterministic and local (Apple Silicon MPS/CPU, no cloud APIs) — per `eval/runs/ft-traces/interventions-notes.md` scope.
- `make test` (offline suite, currently 248 passed) must stay green after every task.
- Tests must run offline: use `HashEmbedder` / `SparseIndex` / stub chunks, never MPS models.
- Real-index measurement commands need env: `HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 PYTHONPATH=src` and `.venv/bin/python`.
- Chunk IDs must remain stable for unchanged content (F3 incremental index manifest depends on chunk text; ID scheme `doc#sec#idx` must not change shape).
- Baselines to compare against (committed): golden `eval/runs/ft-golden/` (45 answerable, 43 hits, answer-level failures = 3), probes `eval/runs/ft-probes/` (25 answerable, answer-level failures = 7). Never overwrite these directories.
- Success gates (from the report): probe answer-level failures drop 7→≤3; golden answer-level failures stay ≤3; pool-widening accepted only if p95 retrieval+rerank latency at the wider pool ≤ 2× the pool-50 p95.

---

### Task 1: Glossary expansion module (`expand.py`)

**Files:**
- Create: `src/sebi_rag/expand.py`
- Test: `tests/test_expand.py`

**Interfaces:**
- Consumes: nothing (pure stdlib).
- Produces: `expand_query(query: str, glossary: dict[str, tuple[str, ...]] = GLOSSARY) -> str` and module constant `GLOSSARY: dict[str, tuple[str, ...]]`. Task 2 imports both from `sebi_rag.expand`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_expand.py`:

```python
"""Query-side lexical expansion (intervention #2, glossary variant).

Lay->statutory synonym injection for the BM25 leg only. Grounded in the
sparse_vocabulary_miss bucket of eval/runs/ft-traces/buckets.md.
"""
from __future__ import annotations

from sebi_rag.expand import GLOSSARY, expand_query


def test_lay_term_gains_statutory_synonym():
    out = expand_query("Can an investor block all outgoing transactions?")
    # original query preserved as prefix; statutory synonym appended
    assert out.startswith("Can an investor block all outgoing transactions?")
    assert "freeze" in out


def test_query_without_glossary_terms_is_unchanged():
    q = "What is the settlement cycle for equity trades?"
    assert expand_query(q) == q


def test_synonym_already_present_is_not_duplicated():
    out = expand_query("freeze or block the folio")
    assert out.lower().split().count("freeze") == 1


def test_multiword_synonym_splits_into_tokens():
    glossary = {"template": ("model agreement",)}
    out = expand_query("is there a template", glossary=glossary)
    assert out == "is there a template model agreement"


def test_all_five_sparse_failure_queries_expand():
    # the 5 sparse_vocabulary_miss failures from buckets.md must each gain
    # at least one statutory term
    queries = [
        "Can an investor voluntarily block all outgoing transactions from their folio?",   # para-freeze
        "Is there a template contract between a registrar to an issue and the company?",    # probe-tbl-05
        "Which circular replaced the earlier ICDR-related circulars and made them void?",   # probe-sup-01
        "How recent do the papers accompanying a broking licence application need to be?",  # probe-par-01
        "What fraction of the shares held by public investors must be kept in electronic form?",  # probe-par-02
    ]
    for q in queries:
        assert expand_query(q) != q, f"no expansion for: {q}"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_expand.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sebi_rag.expand'`

- [ ] **Step 3: Write the module**

Create `src/sebi_rag/expand.py`:

```python
"""Query-side lexical expansion for BM25 (intervention #2, glossary variant).

SEBI circulars use statutory vocabulary (freeze, dematerialised, rescinded)
where users ask in lay terms (block, electronic, replaced). Appending
statutory synonyms to the sparse-leg query closes the vocabulary gap without
touching the index; the dense leg keeps the raw query. Entries are grounded
in the sparse_vocabulary_miss failures of eval/runs/ft-traces/buckets.md.
"""
from __future__ import annotations

import re

# lay token -> statutory synonyms appended to the BM25 query.
# Keys are single lowercase tokens; values may be multi-word phrases.
GLOSSARY: dict[str, tuple[str, ...]] = {
    # para-freeze: "block all outgoing transactions" vs corpus "freeze"
    "block": ("freeze",),
    "blocked": ("frozen", "freeze"),
    "blocking": ("freezing", "freeze"),
    "unblock": ("unfreeze",),
    "re-enable": ("unfreeze",),
    # probe-par-02: "electronic form" vs corpus "dematerialised"
    "electronic": ("dematerialised", "dematerialized", "demat"),
    "paper": ("physical",),
    "fraction": ("percentage", "per cent"),
    # probe-sup-01: "replaced ... made them void" vs corpus "rescinded"
    "replaced": ("rescinded", "superseded"),
    "replaces": ("rescinds", "supersedes"),
    "void": ("rescinded",),
    "withdrawn": ("rescinded",),
    # probe-tbl-05: "template contract" vs corpus "Model ... Agreement"
    "template": ("model",),
    "contract": ("agreement",),
    # probe-par-01: "papers ... broking licence" vs corpus
    # "documents ... certificate of registration"
    "papers": ("documents",),
    "licence": ("registration", "certificate"),
    "license": ("registration", "certificate"),
    "broking": ("broker", "brokers"),
}

_TOKEN = re.compile(r"[a-z][a-z0-9-]*")


def expand_query(
    query: str, glossary: dict[str, tuple[str, ...]] = GLOSSARY
) -> str:
    """Append statutory synonyms for lay tokens present in `query`.

    Deterministic and additive: the original query is always preserved as a
    prefix, so expansion can only add BM25 candidate terms, never remove any.
    """
    tokens = _TOKEN.findall(query.lower())
    present = set(tokens)
    extra: list[str] = []
    for t in tokens:
        for syn in glossary.get(t, ()):
            for w in syn.lower().split():
                if w not in present:
                    present.add(w)
                    extra.append(w)
    return f"{query} {' '.join(extra)}" if extra else query
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_expand.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/expand.py tests/test_expand.py
git commit -m "feat: statutory-synonym query expansion module (intervention #2, glossary variant)"
```

---

### Task 2: Wire expansion into the sparse leg + measure

**Files:**
- Modify: `src/sebi_rag/retrieve.py:164-170` (`HybridRetriever.retrieve`)
- Test: `tests/test_expand.py` (append wiring tests)

**Interfaces:**
- Consumes: `expand_query` from Task 1; `SparseIndex.search(query: str, k: int)`.
- Produces: `HybridRetriever.retrieve` now expands the sparse-leg query internally; signature unchanged (`retrieve(self, query, k_dense=50, k_sparse=50, top_n=50)`), so no caller changes anywhere.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_expand.py`:

```python
from sebi_rag.embeddings import HashEmbedder
from sebi_rag.retrieve import HybridRetriever, SparseIndex
from sebi_rag.segment import Chunk


def _chunk(i: int, text: str) -> Chunk:
    return Chunk(id=f"DOC/{i}#s#0", doc_id=f"DOC/{i}",
                 section=f"DOC/{i}/s/p0", text=text)


def test_expanded_sparse_query_hits_statutory_chunk():
    s = SparseIndex()
    s.build([
        "The depository shall freeze the folio upon written request.",
        "Settlement of trades occurs on a T plus one cycle.",
        "Margin requirements for derivatives are specified in Annexure A.",
    ])
    top = s.search(expand_query("investor wants to block debit entries"), 1)
    assert top[0][0] == 0 and top[0][1] > 0


def test_retrieve_routes_expanded_query_to_sparse_leg(monkeypatch):
    chunks = [
        _chunk(1, "The depository shall freeze the folio upon written request."),
        _chunk(2, "Settlement of trades occurs on a T plus one cycle."),
    ]
    r = HybridRetriever.build(chunks, HashEmbedder(dim=64))
    seen: dict[str, str] = {}
    orig = r.sparse.search

    def spy(q: str, k: int):
        seen["q"] = q
        return orig(q, k)

    monkeypatch.setattr(r.sparse, "search", spy)
    r.retrieve("investor wants to block debit entries")
    assert "freeze" in seen["q"]


def test_retrieve_dense_leg_keeps_raw_query(monkeypatch):
    chunks = [
        _chunk(1, "The depository shall freeze the folio upon written request."),
        _chunk(2, "Settlement of trades occurs on a T plus one cycle."),
    ]
    r = HybridRetriever.build(chunks, HashEmbedder(dim=64))
    seen: dict[str, str] = {}
    orig = r.dense.search

    def spy(q: str, k: int):
        seen["q"] = q
        return orig(q, k)

    monkeypatch.setattr(r.dense, "search", spy)
    q = "investor wants to block debit entries"
    r.retrieve(q)
    assert seen["q"] == q
```

- [ ] **Step 2: Run tests to verify the wiring tests fail**

Run: `.venv/bin/python -m pytest tests/test_expand.py -v`
Expected: `test_expanded_sparse_query_hits_statutory_chunk` PASSES (it only uses `expand_query` + `SparseIndex` directly); `test_retrieve_routes_expanded_query_to_sparse_leg` FAILS with `AssertionError` ("freeze" not in the raw query); `test_retrieve_dense_leg_keeps_raw_query` PASSES.

- [ ] **Step 3: Wire it in**

In `src/sebi_rag/retrieve.py`, add to the imports block (after `from .embeddings import Embedder`):

```python
from .expand import expand_query
```

Change `HybridRetriever.retrieve`:

```python
    def retrieve(
        self, query: str, k_dense: int = 50, k_sparse: int = 50, top_n: int = 50
    ) -> list[tuple[Chunk, float]]:
        dense = self.dense.search(query, k_dense)
        # intervention #2: statutory-synonym expansion, sparse leg only —
        # BM25 misses lay vocabulary; dense keeps the raw query.
        sparse = self.sparse.search(expand_query(query), k_sparse)
        fused = rrf_fuse([dense, sparse], top_n=top_n)
        return [(self.chunks[i], score) for i, score in fused]
```

- [ ] **Step 4: Run the full offline suite**

Run: `make test`
Expected: all tests pass (248 + 8 new = 256), 0 failures. If any pipeline/e2e test broke because expansion changed a smoke-query ranking, inspect that test's query, and only if the new ranking is semantically correct update the expectation — otherwise fix the glossary entry that caused it.

- [ ] **Step 5: Measure on the real index (probes + golden)**

Run (each takes a few minutes; loads bge-m3 on MPS):

```bash
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/probes/probes_v1.jsonl --out eval/runs/iv2-probes

HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/golden/golden_v6.jsonl --out eval/runs/iv2-golden

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv2-probes/run.trec --golden eval/probes/probes_v1.jsonl \
  --out eval/runs/iv2-probes/failures.jsonl --source probes_v1

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv2-golden/run.trec --golden eval/golden/golden_v6.jsonl \
  --out eval/runs/iv2-golden/failures.jsonl --source golden_v6
```

Expected (report's success criterion for #2): among the 5 sparse-failure IDs (para-freeze, probe-tbl-05, probe-sup-01, probe-par-01, probe-par-02) at least 3 improve their answer-level class vs the committed baselines `eval/runs/ft-probes/failures.jsonl` / `eval/runs/ft-golden/failures.jsonl`; golden failure count does not exceed baseline (3) and `recall_at_10` in `iv2-golden/results.json` ≥ 0.956. Record actual numbers in the commit message. If the criterion is NOT met, keep the code (it cannot remove candidates) but flag the shortfall in the final report update (Task 5) instead of claiming success.

- [ ] **Step 6: Commit**

```bash
git add src/sebi_rag/retrieve.py tests/test_expand.py eval/runs/iv2-probes eval/runs/iv2-golden
git commit -m "feat: expand sparse-leg queries with statutory synonyms (intervention #2)

probes: <n> answer-level failures (baseline 7); golden: <n> (baseline 3)"
```

---

### Task 3: Reranker pool-widening sweep

**Files:**
- Create: `scripts/analysis/sweep_pool.py`
- Modify (conditional): `src/sebi_rag/pipeline.py:43` (`pool` default)
- Output: `eval/runs/pool-sweep/sweep.json`

**Interfaces:**
- Consumes: `classify_answer(ranked_chunk_ids, chunk_texts, must_contain) -> tuple[str, int]` and `classify_query(ranked_chunk_ids, relevant_circulars) -> tuple[str, int]` from `scripts/analysis/extract_misses.py`; `HybridRetriever.load`, `CrossEncoderReranker.rerank`.
- Produces: `eval/runs/pool-sweep/sweep.json` with per-pool answer-level counts and latency stats; possibly a new `pool` default in `RAGPipeline.query`.

- [ ] **Step 1: Write the sweep script**

Create `scripts/analysis/sweep_pool.py`:

```python
"""Pool-width sweep (intervention #3): answer-level rescue rate vs reranker
latency at retriever pool 50/100/150 (throwaway research script).

The TREC runfiles record fused (pre-rerank) order, so this script reranks
inline and classifies at the answer level on the RERANKED ordering — the
question is whether widening the pool lets the cross-encoder rescue answer
chunks into the top-10.

Run:  HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
      PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/analysis/sweep_pool.py
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
for k, v in {
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(k, v)

from extract_misses import classify_answer, classify_query  # noqa: E402
from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402


def _load_items(path: Path) -> list[dict]:
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    return [r for r in rows if not r.get("abstain")]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pools", default="50,100,150")
    ap.add_argument("--out", default=str(ROOT / "eval" / "runs" / "pool-sweep"))
    args = ap.parse_args()
    pools = [int(p) for p in args.pools.split(",")]

    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(ROOT / "data" / "index", emb)
    rer = CrossEncoderReranker(device="mps")
    items = _load_items(ROOT / "eval" / "golden" / "golden_v6.jsonl")
    items += _load_items(ROOT / "eval" / "probes" / "probes_v1.jsonl")
    print(f"items={len(items)} pools={pools}", flush=True)

    report: dict[str, dict] = {}
    for pool in pools:
        lats: list[float] = []
        counts = {"hit": 0, "ranked_low": 0, "candidate_miss": 0}
        failures: list[dict] = []
        for item in items:
            t0 = time.time()
            cands = retr.retrieve(item["query"], top_n=pool)
            reranked = rer.rerank(item["query"], [c for c, _ in cands])
            lats.append(time.time() - t0)
            ids = [c.id for c, _ in reranked]
            texts = {c.id: c.text for c, _ in reranked}
            must = item.get("must_contain", [])
            if must:
                cls, rank = classify_answer(ids, texts, must)
            else:
                cls, rank = classify_query(ids, item["relevant_circulars"])
            counts[cls] += 1
            if cls != "hit":
                failures.append({"id": item["id"], "class": cls, "rank": rank})
        p95 = (statistics.quantiles(lats, n=20)[18] if len(lats) >= 20
               else max(lats))
        report[str(pool)] = {
            "answer_level": counts,
            "failures": failures,
            "latency_mean_s": round(statistics.mean(lats), 3),
            "latency_p95_s": round(p95, 3),
        }
        print(f"pool={pool} {counts} mean={report[str(pool)]['latency_mean_s']}s "
              f"p95={report[str(pool)]['latency_p95_s']}s", flush=True)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "sweep.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out / "sweep.json")}, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the sweep**

Run (loads two MPS models; expect 10–30 min for 70 items × 3 pools):

```bash
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/analysis/sweep_pool.py
```

Expected: per-pool console lines and `eval/runs/pool-sweep/sweep.json` written. Read the JSON.

- [ ] **Step 3: Apply the decision rule**

Acceptance rule (from the report): pick the smallest pool P > 50 where `answer_level.hit` strictly increases vs pool 50 AND `latency_p95_s(P) <= 2 * latency_p95_s(50)`.

- If such P exists: change `src/sebi_rag/pipeline.py` line 43 default from `pool: int = 50` to `pool: int = P`, and add one line to the docstring-free dataclass area? No — just change the default and note the sweep in a comment:

```python
    def query(
        self, question: str, pool: int = 100,  # sweep 2026-07-16: eval/runs/pool-sweep
        top_k: int = 3,
        advisory: bool = False, as_of: str | None = None,
    ) -> tuple[Answer, list[str]]:
```

(with `100` replaced by the winning P), then run `make test` — expected all pass, since offline tests build tiny corpora where `top_n` is clamped by corpus size.

- If no P qualifies: make no code change and record the sweep numbers for the report update in Task 5.

- [ ] **Step 4: Commit**

```bash
git add scripts/analysis/sweep_pool.py eval/runs/pool-sweep
# plus src/sebi_rag/pipeline.py if the default changed
git commit -m "perf: reranker pool sweep 50/100/150 (intervention #3)

answer-level hits per pool: 50=<n> 100=<n> 150=<n>; p95 latency <a>/<b>/<c>s; default pool -> <P or unchanged>"
```

---

### Task 4: Governing-clause folding in the chunker (intervention #1)

**Files:**
- Modify: `src/sebi_rag/segment.py:74-146` (`hierarchical_chunk`)
- Test: `tests/test_segment.py` (append)

**Interfaces:**
- Consumes: existing `hierarchical_chunk(text, meta, max_chars=1200, overlap_chars=150) -> list[Chunk]`.
- Produces: same signature; chunk bodies for numbered sub-clauses now begin with the nearest recorded ancestor heading line. Chunk IDs/count unchanged for documents without numbered hierarchies.

**Background for the implementer:** the existing `carry` mechanism (segment.py:89,98-100,131-133) already folds a *bodyless* parent heading into its **first** child chunk. The probe-par-03 defect is the *sibling* chunks (4.1.1.2 … 4.1.1.5): they never see the governing clause "4.1.1 On and from the date of the Order of winding down… the CRA shall:". Fix: record every heading line by its dotted number and prepend the nearest ancestor heading to each flushed body (skipping when already present, which also covers the carry-overlap case).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_segment.py`:

```python
# --- governing-clause folding (probe-par-03 / CRA sub-clause class) ---------
# Same per-line splitting trigger as _TEXT: one blank-line-free block.
_CRA_TEXT = (
    _FILLER + "\n"
    "4.1.1. On and from the date of the Order of winding down or surrender "
    "of certificate of registration, the CRA shall:\n"
    "4.1.1.1. not onboard any new clients or accept fresh rating mandates;\n"
    "4.1.1.2. permit companies to withdraw ongoing rating assignments "
    "without levy of any charge;\n"
    "4.1.2. All other obligations of the CRA shall continue as specified."
)


def test_sibling_list_item_carries_governing_clause():
    # 4.1.1.2 is the SECOND child: the carry mechanism only rescues the first,
    # so this chunk historically lost the "winding down" context entirely.
    chunks = hierarchical_chunk(_CRA_TEXT, _META)
    for c in chunks:
        if "withdraw ongoing rating assignments" in c.text:
            assert "winding down" in c.text, (
                f"governing clause missing from sibling chunk: {c.text!r}"
            )
            break
    else:
        raise AssertionError("4.1.1.2 provision text missing from all chunks")


def test_governing_clause_not_duplicated():
    chunks = hierarchical_chunk(_CRA_TEXT, _META)
    for c in chunks:
        assert c.text.count("On and from the date of the Order") <= 1, (
            f"governing clause duplicated: {c.text!r}"
        )


def test_nominee_regression_corpus_unchanged_behaviour():
    # the original nominee-bug guarantees still hold with folding active
    chunks = hierarchical_chunk(_TEXT, _META)
    for c in chunks:
        assert _body(c) != "5. Number of nominees:"
    assert any(
        "Number of nominees" in c.text and "up to 3 nominees" in c.text
        for c in chunks
    )
```

- [ ] **Step 2: Run tests to verify the new one fails**

Run: `.venv/bin/python -m pytest tests/test_segment.py -v`
Expected: `test_sibling_list_item_carries_governing_clause` FAILS ("governing clause missing"); `test_governing_clause_not_duplicated` and `test_nominee_regression_corpus_unchanged_behaviour` PASS (they assert current invariants).

- [ ] **Step 3: Implement folding**

In `src/sebi_rag/segment.py`, inside `hierarchical_chunk`:

(a) add a heading registry next to the other state (after `carry = ""`, line 89):

```python
    heads: dict[str, str] = {}  # dotted num -> full heading line (governing clause)
```

(b) in the heading branch (after `section_num = hnum`, line 139), record the line:

```python
            heads[hnum] = first_line.strip()[:300]
```

(c) in `flush`, after the carry-prepend block (lines 98-100), fold in the nearest recorded ancestor heading. `flush` reads `section_num` from the enclosing scope — at every call site it still holds the number of the section the buffered body belongs to (headings update it only after flushing):

```python
        # Intervention #1 (2026-07-16 failure taxonomy): numbered sub-clauses
        # ("4.1.1.2. ...") are meaningless without their governing clause
        # ("4.1.1 On and from the date... the CRA shall:"). Prepend the nearest
        # recorded ancestor heading so both retrievers see the context.
        num = section_num
        while "." in num:
            num = num.rsplit(".", 1)[0]
            gov = heads.get(num, "")
            if gov:
                if gov not in body:
                    body = f"{gov}\n{body}"
                break
```

`flush` must declare no new nonlocals for this (it only reads `section_num` and `heads`). The `gov not in body` guard prevents duplication when `carry` already prefixed the same heading.

- [ ] **Step 4: Run the segment tests, then the full suite**

Run: `.venv/bin/python -m pytest tests/test_segment.py -v`
Expected: all 6 pass.
Run: `make test`
Expected: 0 failures. Chunker-dependent tests (pipeline/e2e smoke corpora) use flat or single-level texts where no ancestor heading exists, so behaviour is unchanged; if one fails, read the failing text — only accept expectation updates where a numbered sub-clause genuinely gained its governing line.

- [ ] **Step 5: Red-green sanity on the regression guard**

Temporarily comment out the folding block from Step 3(c), run `.venv/bin/python -m pytest tests/test_segment.py::test_sibling_list_item_carries_governing_clause -v` — expected FAIL; restore the block, rerun — expected PASS. This proves the test actually pins the fix.

- [ ] **Step 6: Commit**

```bash
git add src/sebi_rag/segment.py tests/test_segment.py
git commit -m "fix: fold governing clause into numbered sub-clause chunks (intervention #1)"
```

---

### Task 5: Reindex, full re-measurement, report update

**Files:**
- Output: rebuilt `data/index/`, `eval/runs/iv-final-probes/`, `eval/runs/iv-final-golden/`
- Modify: `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md` (append results section)

**Interfaces:**
- Consumes: everything from Tasks 1–4; `make reindex`; `scripts/bench_retrieval.py`; `scripts/analysis/extract_misses.py`.
- Produces: the final measured verdict against the report's success gates.

- [ ] **Step 1: Rebuild the index**

Run: `make reindex` (background it; chunk texts changed for every doc with numbered sub-clauses, so most embeddings re-encode — expect 30–90 min on MPS).
Expected: completes without error; `data/index/meta.json` updated. Note the new chunk count printed by the build and confirm it is close to the previous count (folding adds no chunks; a large delta means a chunker regression — stop and debug before benchmarking).

- [ ] **Step 2: Re-run both benchmarks and classify**

```bash
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/probes/probes_v1.jsonl --out eval/runs/iv-final-probes

HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/golden/golden_v6.jsonl --out eval/runs/iv-final-golden

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv-final-probes/run.trec --golden eval/probes/probes_v1.jsonl \
  --out eval/runs/iv-final-probes/failures.jsonl --source probes_v1

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv-final-golden/run.trec --golden eval/golden/golden_v6.jsonl \
  --out eval/runs/iv-final-golden/failures.jsonl --source golden_v6
```

Expected gates: probes answer-level failures (`answer_candidate_miss + answer_ranked_low`) ≤ 3 (baseline 7); golden answer-level failures ≤ 3 (baseline 3) and `recall_at_10` ≥ 0.956. Report the actual numbers verbatim whether or not the gates pass.

- [ ] **Step 3: Full test suite**

Run: `make test`
Expected: 0 failures.

- [ ] **Step 4: Append results to the report**

Add to `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md`:

```markdown
## 5. Intervention results (2026-07-16, this branch)

| run | answerable | answer-level failures | recall@10 |
|---|---|---|---|
| probes baseline (`ft-probes`) | 25 | 7 | 0.96 |
| probes final (`iv-final-probes`) | 25 | <n> | <x> |
| golden baseline (`ft-golden`) | 45 | 3 | 0.956 |
| golden final (`iv-final-golden`) | 45 | <n> | <x> |

Interventions landed: #2 glossary expansion (commit <sha>), #3 pool sweep
(commit <sha>, default pool = <P or unchanged>), #1 governing-clause folding
(commit <sha>). Per-failure before/after: <one line per original failure ID
with old class -> new class>. Gate verdict: <met / not met, which>.
```

Fill every `<…>` with measured values from Step 2 and the actual commit SHAs.

- [ ] **Step 5: Update the knowledge graph and commit**

```bash
graphify update .
git add docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md \
        eval/runs/iv-final-probes eval/runs/iv-final-golden graphify-out
git commit -m "eval: post-intervention benchmark results + report update"
```

---

## Self-review notes

- Spec coverage: report interventions #1/#2/#3 → Tasks 4/1+2/3; #4 (SPLADE) and #5 (HyDE) are conditional follow-ons per the report and intentionally out of scope.
- Measurement always compares against the committed `ft-*` baselines; new runs go to fresh directories.
- Type consistency: `expand_query(str, dict) -> str` used identically in Tasks 1–2; `classify_answer`/`classify_query` signatures copied from `scripts/analysis/extract_misses.py:25-59`.
