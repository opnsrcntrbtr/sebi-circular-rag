# Pre-retrieval Failure Taxonomy & Intervention Ranking — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a ranked-intervention report for the pre-generation pipeline (ingestion → chunking → indexing → hybrid retrieval), grounded in a root-caused failure taxonomy harvested from golden-set misses and handcrafted probe queries.

**Architecture:** Research only — no production code changes. Reuse `scripts/bench_retrieval.py` (real index + BGE-M3 on MPS) to produce TREC runfiles for golden v6 and a new probe set; throwaway analysis scripts in `scripts/analysis/` classify misses and trace each failure backwards through the pipeline (corpus text → chunk → dense-only/sparse-only/fused retrieval → reranker) to assign one primary bucket; report ranks interventions by bucket frequency × fixability.

**Tech Stack:** Python 3.12/3.13 via `uv run`, existing sebi_rag modules (`HybridRetriever`, `BGEM3Embedder`, `CrossEncoderReranker`, `benchmark.py` helpers), pytest for the one pure-logic module.

**Spec:** `docs/superpowers/specs/2026-07-16-preretrieval-failure-taxonomy-design.md`

## Global Constraints

- Local-first: everything runs on Apple Silicon (MPS); cloud APIs are NOT allowed. New local deps are allowed only as *recommendations in the report* — nothing new is installed in this effort.
- No production code changes: only `scripts/analysis/`, `eval/probes/`, `eval/runs/`, and `docs/` may gain files. `src/sebi_rag/` is read-only.
- Scratch scripts in `scripts/analysis/` are throwaway unless a later plan promotes them; keep them dependency-free beyond what `pyproject.toml` already provides.
- Model-loaded commands (non-smoke bench, tracing) take minutes on MPS; run them in the foreground and wait — do not parallelize model loads.
- Offline tests run with `PYTHONPATH=src uv run pytest ...` (the `sebi_rag` package is not installed; scripts add `src/` to `sys.path` themselves).
- Deliverable report: `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md`.
- Success criteria (from spec): ≥90% of harvested failures get a primary bucket with evidence; top 3 interventions each cite specific failure IDs; report committed.

---

### Task 1: Baseline golden run

Produce the retrieval-only runfile for golden v6 against the real persisted index. This is the raw material for miss extraction.

**Files:**
- Create: `eval/runs/ft-golden/run.trec`, `eval/runs/ft-golden/results.json` (generated artifacts)

**Interfaces:**
- Consumes: `scripts/bench_retrieval.py` (existing; `--golden`, `--out`, `--top-n` flags).
- Produces: `eval/runs/ft-golden/run.trec` — TREC format `qid Q0 chunk_id rank score baseline-retrieval`, top-50 chunks per query. Chunk IDs look like `SEBI/HO/.../2023/123#preamble#0`; the doc is the part before the first `#`. Later tasks read this file.

- [ ] **Step 1: Verify the real index and corpus exist**

Run: `ls data/index/dense.faiss data/index/chunks.jsonl data/corpus/circulars.jsonl`
Expected: all three paths listed. If missing, STOP and report — `make reindex` is out of scope for a research branch without user sign-off.

- [ ] **Step 2: Run the retrieval benchmark (non-smoke, top-50)**

Top-50 matches `RAGPipeline.query(pool=50)` — the reranker-input cutoff, per spec.

Run:
```bash
uv run python scripts/bench_retrieval.py \
  --golden eval/golden/golden_v6.jsonl \
  --out eval/runs/ft-golden --top-n 50
```
Expected: JSON summary printed with `"n"` = number of golden rows, a `recall_at_10` value, and `eval/runs/ft-golden/run.trec` + `results.json` created. Takes a few minutes (loads bge-m3 on MPS). Record `recall_at_10` — it goes in the report as the baseline.

- [ ] **Step 3: Sanity-check the runfile**

Run: `head -3 eval/runs/ft-golden/run.trec && wc -l eval/runs/ft-golden/run.trec`
Expected: lines like `<qid> Q0 <doc>#<section>#<n> 1 0.03278688 baseline-retrieval`; line count ≈ 50 × number of non-empty queries.

- [ ] **Step 4: Commit the run artifacts**

```bash
git add eval/runs/ft-golden
git commit -m "research: baseline golden-v6 retrieval run for failure taxonomy"
```

---

### Task 2: Miss-extraction module + script

Pure-logic classifier (unit-tested, offline) plus a CLI that joins a TREC runfile with a golden/probe JSONL and emits `failures.jsonl`.

**Files:**
- Create: `scripts/analysis/extract_misses.py`
- Test: `tests/test_extract_misses.py`

**Interfaces:**
- Consumes: TREC runfile (Task 1 format), golden JSONL rows with `id`, `query`, `relevant_circulars`, `abstain`, `must_contain`, `task_type` fields; `sebi_rag.ingest_pdf.normalize_circular_number(n: str) -> str` for doc matching.
- Produces: `classify_query(ranked_chunk_ids: list[str], relevant_circulars: list[str]) -> tuple[str, int]` returning `("hit" | "ranked_low" | "candidate_miss", first_relevant_doc_rank)` where rank is 1-based over *deduplicated docs* and `-1` when absent. CLI writes `failures.jsonl`: one row per non-hit, `{"id", "query", "class", "first_relevant_rank", "relevant_circulars", "must_contain", "task_type", "source"}`. Tasks 3–5 consume `failures.jsonl`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_extract_misses.py`:

```python
"""Offline tests for the failure-taxonomy miss classifier (throwaway research)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "analysis"))

from extract_misses import classify_query  # noqa: E402


CHUNKS = [
    "SEBI/HO/A/1#preamble#0",
    "SEBI/HO/A/1#body#1",
    "SEBI/HO/B/2#preamble#0",
    "SEBI/HO/C/3#preamble#0",
]


def test_hit_when_relevant_doc_in_top10_docs():
    cls, rank = classify_query(CHUNKS, ["SEBI/HO/B/2"])
    assert cls == "hit"
    assert rank == 2  # docs dedupe to [A/1, B/2, C/3]; B/2 is doc-rank 2


def test_candidate_miss_when_relevant_doc_absent():
    cls, rank = classify_query(CHUNKS, ["SEBI/HO/ZZZ/9"])
    assert cls == "candidate_miss"
    assert rank == -1


def test_ranked_low_when_first_relevant_doc_after_rank10():
    ranked = [f"SEBI/HO/D{i}/{i}#p#0" for i in range(12)] + ["SEBI/HO/B/2#p#0"]
    cls, rank = classify_query(ranked, ["SEBI/HO/B/2"])
    assert cls == "ranked_low"
    assert rank == 13


def test_doc_matching_is_normalized():
    # normalize_circular_number: strips whitespace/punct, drops leading SEBI/, casefolds
    cls, _ = classify_query(CHUNKS, ["HO/B/2 "])
    assert cls == "hit"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `PYTHONPATH=src uv run pytest tests/test_extract_misses.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'extract_misses'`

- [ ] **Step 3: Write the module**

Create `scripts/analysis/extract_misses.py`:

```python
"""Classify golden/probe queries against a TREC runfile (throwaway research).

Classes: hit (relevant doc within top-10 deduped docs), ranked_low (relevant
doc in candidates but first appears after doc-rank 10), candidate_miss
(relevant doc absent from the top-50 candidate set entirely).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.ingest_pdf import normalize_circular_number  # noqa: E402


def _doc(chunk_id: str) -> str:
    return chunk_id.split("#", 1)[0]


def classify_query(
    ranked_chunk_ids: list[str], relevant_circulars: list[str]
) -> tuple[str, int]:
    relevant = {normalize_circular_number(c) for c in relevant_circulars}
    docs: list[str] = []
    seen: set[str] = set()
    for cid in ranked_chunk_ids:
        d = normalize_circular_number(_doc(cid))
        if d not in seen:
            seen.add(d)
            docs.append(d)
    for rank, d in enumerate(docs, start=1):
        if d in relevant:
            return ("hit" if rank <= 10 else "ranked_low"), rank
    return "candidate_miss", -1


def load_run(path: Path) -> dict[str, list[str]]:
    run: dict[str, list[tuple[int, str]]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        qid, _q0, cid, rank, _score, _name = line.split()
        run.setdefault(qid, []).append((int(rank), cid))
    return {q: [c for _, c in sorted(v)] for q, v in run.items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--golden", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--source", required=True, help="label: golden_v6 | probes_v1")
    args = ap.parse_args()

    run = load_run(Path(args.run))
    rows = [
        json.loads(line)
        for line in Path(args.golden).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    failures, hits, skipped = [], 0, 0
    for row in rows:
        if row.get("abstain"):
            skipped += 1
            continue
        cls, rank = classify_query(run.get(row["id"], []), row["relevant_circulars"])
        if cls == "hit":
            hits += 1
            continue
        failures.append({
            "id": row["id"],
            "query": row["query"],
            "class": cls,
            "first_relevant_rank": rank,
            "relevant_circulars": row["relevant_circulars"],
            "must_contain": row.get("must_contain", []),
            "task_type": row.get("task_type", ""),
            "source": args.source,
        })
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in failures:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({
        "answerable": len(rows) - skipped, "hits": hits,
        "candidate_miss": sum(1 for r in failures if r["class"] == "candidate_miss"),
        "ranked_low": sum(1 for r in failures if r["class"] == "ranked_low"),
        "out": str(out),
    }, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONPATH=src uv run pytest tests/test_extract_misses.py -v`
Expected: 4 passed

- [ ] **Step 5: Extract golden failures**

Run:
```bash
uv run python scripts/analysis/extract_misses.py \
  --run eval/runs/ft-golden/run.trec \
  --golden eval/golden/golden_v6.jsonl \
  --out eval/runs/ft-golden/failures.jsonl \
  --source golden_v6
```
Expected: JSON summary with `answerable`, `hits`, `candidate_miss`, `ranked_low` counts; `failures.jsonl` written. Note the counts — they anchor the report.

- [ ] **Step 6: Commit**

```bash
git add scripts/analysis/extract_misses.py tests/test_extract_misses.py eval/runs/ft-golden/failures.jsonl
git commit -m "research: miss classifier + golden-v6 failure extraction"
```

---

### Task 3: Probe query set + probe run

~25 handcrafted queries targeting suspected blind spots, in golden-v6 schema so `bench_retrieval.py --golden` and `validate_golden` work unchanged.

**Files:**
- Create: `eval/probes/probes_v1.jsonl`
- Create: `eval/runs/ft-probes/run.trec`, `eval/runs/ft-probes/failures.jsonl` (generated)

**Interfaces:**
- Consumes: golden-v6 row schema (all fields required by `sebi_rag.benchmark.validate_golden`: `id, query, relevant_circulars, relevant_chunks, must_contain, must_not_contain, abstain, task_type, difficulty, expected_citation_level, rationale, label_source, review_status`). `task_type` must be one of `benchmark.TASK_TYPES`; use `label_source: "probes_v1"`, `review_status: "draft"`.
- Produces: `eval/probes/probes_v1.jsonl` and `eval/runs/ft-probes/failures.jsonl` in the same formats as Tasks 1–2. Task 4 consumes both failure files.

- [ ] **Step 1: Mine the corpus for probe targets**

For each of the 5 blind-spot categories, find real circulars whose text contains a verifiable answer. Work from the corpus, not memory:

```bash
# candidate circulars with tables/annexures
uv run python - <<'EOF'
import json
for line in open("data/corpus/circulars.jsonl", encoding="utf-8"):
    r = json.loads(line)
    t = r.get("text", "")
    if "Annexure" in t or "| " in t:
        print(r["circular_number"], "|", r["subject"][:80])
EOF
```
Repeat with predicates for numeric facts (`re.search(r"\b(shall not exceed|maximum of|at least) \d", t)`), supersession phrasing (`"supersession" in t or "rescinded" in t`), and short/definitional sections. For each chosen target, record: circular_number, the exact answer sentence (becomes `must_contain`), and the section it lives in.
Expected: a scratch list of ≥25 (circular, answer-text, category) triples covering all 5 categories: table/annexure, numeric fact, supersession/as-of phrasing, definitional lookup, paraphrase/vocabulary-mismatch.

- [ ] **Step 2: Write `eval/probes/probes_v1.jsonl`**

25 rows (5 per category). Category → `task_type` mapping: table/annexure → `numeric_table`; numeric fact → `numeric_table`; supersession phrasing → `lineage_supersession`; definitional lookup → `title_direct`; paraphrase → `body_paraphrase`. Phrase paraphrase probes WITHOUT reusing the circular's own vocabulary (that's the point). Row template — every field below is required:

```json
{"id": "probe-tbl-01", "query": "<natural question a compliance officer would ask>", "relevant_circulars": ["<exact circular_number from corpus>"], "relevant_chunks": [], "must_contain": ["<exact answer substring from the circular text>"], "must_not_contain": [], "abstain": false, "task_type": "numeric_table", "difficulty": "hard", "expected_citation_level": "circular", "rationale": "Probe: table/annexure content — <why this target>", "label_source": "probes_v1", "review_status": "draft"}
```

ID convention: `probe-<cat>-NN` with cat ∈ {tbl, num, sup, def, par}.

- [ ] **Step 3: Validate the probe file**

Run:
```bash
uv run python - <<'EOF'
import sys; sys.path.insert(0, "src")
from sebi_rag.benchmark import validate_golden
from sebi_rag.eval_harness import load_golden
rows = load_golden("eval/probes/probes_v1.jsonl")
issues = validate_golden(rows)
for i in issues: print(i)
print(f"{len(rows)} rows, {len(issues)} issues")
EOF
```
Expected: `25 rows, 0 issues` (count may be 25±3 if targets were scarce; ≥20 required).

- [ ] **Step 4: Verify every must_contain actually appears in its target circular**

```bash
uv run python - <<'EOF'
import json, sys; sys.path.insert(0, "src")
from sebi_rag.ingest_pdf import normalize_circular_number as norm
corpus = {norm(json.loads(l)["circular_number"]): json.loads(l)["text"]
          for l in open("data/corpus/circulars.jsonl", encoding="utf-8")}
bad = 0
for l in open("eval/probes/probes_v1.jsonl", encoding="utf-8"):
    row = json.loads(l)
    for c in row["relevant_circulars"]:
        t = corpus.get(norm(c), "")
        for m in row["must_contain"]:
            if m not in t:
                bad += 1
                print(f"{row['id']}: must_contain not found in {c!r}: {m[:60]!r}")
print(f"{bad} unverifiable probes")
EOF
```
Expected: `0 unverifiable probes`. Fix any offenders before proceeding (misses must be attributable to the pipeline, not to a bad label).

- [ ] **Step 5: Run the probe benchmark and extract failures**

```bash
uv run python scripts/bench_retrieval.py \
  --golden eval/probes/probes_v1.jsonl \
  --out eval/runs/ft-probes --top-n 50
uv run python scripts/analysis/extract_misses.py \
  --run eval/runs/ft-probes/run.trec \
  --golden eval/probes/probes_v1.jsonl \
  --out eval/runs/ft-probes/failures.jsonl \
  --source probes_v1
```
Expected: benchmark summary, then classifier summary. Probes were designed to stress weaknesses, so a low hit-rate is fine and informative.

- [ ] **Step 6: Commit**

```bash
git add eval/probes/probes_v1.jsonl eval/runs/ft-probes
git commit -m "research: probe query set v1 + probe retrieval run"
```

---

### Task 4: Failure trace harness

For every failure, walk the spec's 4-step checklist and emit a machine-readable trace with a *proposed* bucket. Final bucket assignment is human (Task 5); this harness gathers the evidence.

**Files:**
- Create: `scripts/analysis/trace_failure.py`
- Create: `eval/runs/ft-traces/traces.jsonl` (generated)

**Interfaces:**
- Consumes: `failures.jsonl` rows (Task 2 format); `HybridRetriever.load(path, embedder)`, `retr.dense.search(q, k) / retr.sparse.search(q, k) -> list[tuple[int, float]]` (indices into `retr.chunks`), `retr.retrieve(q, top_n=50) -> list[tuple[Chunk, float]]`; `CrossEncoderReranker(device="mps").rerank(q, chunks) -> list[tuple[Chunk, float]]`; corpus rows `{"circular_number", "text", ...}`; chunk fields `id, doc_id, section, text`.
- Produces: `traces.jsonl` — one row per failure: `{"id", "class", "source", "text_in_corpus": bool, "gold_chunks": [{"id", "len", "heading_only": bool}], "dense_rank": int, "sparse_rank": int, "fused_rank": int, "rerank_rank": int, "proposed_bucket": str}`. Ranks are 1-based first position of any gold-doc chunk, `-1` if absent in top-50. Task 5 consumes this.

- [ ] **Step 1: Write the harness**

Create `scripts/analysis/trace_failure.py`:

```python
"""Trace each retrieval failure backwards through the pipeline (throwaway).

Checklist per spec: (1) answer text present in ingested corpus text?
(2) does it land in a coherent chunk? (3) dense-only vs sparse-only vs fused
rank of the gold doc, (4) reranker placement. Emits a proposed primary
bucket; final assignment is human (see the taxonomy report).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.ingest_pdf import normalize_circular_number as norm  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402


def _ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def heading_only(text: str) -> bool:
    """Degenerate chunk heuristic: short and no sentence-final punctuation
    (the nominee-count bug class)."""
    body = text.split("|")[-1].strip()  # chunks are prefixed "doc | subject | ..."
    return len(body) < 80 and not re.search(r"[.;:]\s*$", body)


def first_gold_rank(chunk_ids: list[str], gold_docs: set[str]) -> int:
    for i, cid in enumerate(chunk_ids, start=1):
        if norm(cid.split("#", 1)[0]) in gold_docs:
            return i
    return -1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--failures", action="append", required=True,
                    help="failures.jsonl (repeatable)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=50)
    args = ap.parse_args()

    corpus = {}
    for line in (ROOT / "data" / "corpus" / "circulars.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        corpus[norm(r["circular_number"])] = r.get("text", "")

    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(ROOT / "data" / "index", emb)
    reranker = CrossEncoderReranker(device="mps")

    failures = []
    for fp in args.failures:
        failures += [json.loads(l) for l in Path(fp).read_text(encoding="utf-8").splitlines() if l.strip()]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in failures:
            gold_docs = {norm(c) for c in row["relevant_circulars"]}
            needles = [_ws(m) for m in row.get("must_contain", []) if m.strip()]

            # (1) extraction: is the answer text in the ingested corpus?
            hay = " ".join(_ws(corpus.get(d, "")) for d in gold_docs)
            text_in_corpus = all(n in hay for n in needles) if needles else bool(
                gold_docs & set(corpus)
            )

            # (2) chunking: which gold-doc chunks carry the answer, and are
            # they coherent?
            gold_chunks = []
            for c in retr.chunks:
                if norm(c.doc_id) in gold_docs and (
                    not needles or any(n in _ws(c.text) for n in needles)
                ):
                    gold_chunks.append({
                        "id": c.id, "len": len(c.text),
                        "heading_only": heading_only(c.text),
                    })

            # (3) retriever isolation
            q = row["query"]
            dense = [retr.chunks[i].id for i, _ in retr.dense.search(q, args.k)]
            sparse = [retr.chunks[i].id for i, _ in retr.sparse.search(q, args.k)]
            fused_pairs = retr.retrieve(q, top_n=args.k)
            fused = [c.id for c, _ in fused_pairs]
            dense_rank = first_gold_rank(dense, gold_docs)
            sparse_rank = first_gold_rank(sparse, gold_docs)
            fused_rank = first_gold_rank(fused, gold_docs)

            # (4) reranker placement (only meaningful if gold in candidates)
            rerank_rank = -1
            if fused_rank != -1:
                reranked = reranker.rerank(q, [c for c, _ in fused_pairs])
                rerank_rank = first_gold_rank([c.id for c, _ in reranked], gold_docs)

            # proposed bucket, in checklist order
            if not text_in_corpus:
                bucket = "extraction_loss"
            elif needles and not gold_chunks:
                bucket = "chunking_defect"  # text in corpus but in no chunk
            elif gold_chunks and all(g["heading_only"] for g in gold_chunks):
                bucket = "chunking_defect"
            elif dense_rank == -1 and sparse_rank == -1:
                bucket = "embedding_semantic_miss"  # neither retriever; refine by hand
            elif dense_rank == -1:
                bucket = "embedding_semantic_miss"
            elif sparse_rank == -1:
                bucket = "sparse_vocabulary_miss"
            elif fused_rank == -1 or (row["class"] == "ranked_low" and rerank_rank > 10):
                bucket = "fusion_ranking_loss"
            else:
                bucket = "fusion_ranking_loss"  # retrieved-but-low default
            # NOTE: metadata_filter_loss cannot be auto-detected here (no
            # metadata filtering happens inside HybridRetriever.retrieve);
            # assign it manually in Task 5 if as-of/validity scoping explains
            # a miss.

            f.write(json.dumps({
                "id": row["id"], "class": row["class"], "source": row["source"],
                "query": q, "text_in_corpus": text_in_corpus,
                "gold_chunks": gold_chunks[:10],
                "dense_rank": dense_rank, "sparse_rank": sparse_rank,
                "fused_rank": fused_rank, "rerank_rank": rerank_rank,
                "proposed_bucket": bucket,
            }, ensure_ascii=False) + "\n")
            print(f"{row['id']}: {bucket} (d={dense_rank} s={sparse_rank} "
                  f"f={fused_rank} r={rerank_rank})")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-test on a single failure**

Run (builds a one-row input from whichever failure file is non-empty):
```bash
head -1 eval/runs/ft-golden/failures.jsonl > /tmp/one_failure.jsonl
[ -s /tmp/one_failure.jsonl ] \
  || head -1 eval/runs/ft-probes/failures.jsonl > /tmp/one_failure.jsonl
uv run python scripts/analysis/trace_failure.py \
  --failures /tmp/one_failure.jsonl --out /tmp/one_trace.jsonl
cat /tmp/one_trace.jsonl
```
Expected: one JSON trace row with all fields populated, no traceback. If golden produced zero failures (possible if retrieval is strong), the probe file supplies the row.

- [ ] **Step 3: Trace all failures from both sources**

```bash
uv run python scripts/analysis/trace_failure.py \
  --failures eval/runs/ft-golden/failures.jsonl \
  --failures eval/runs/ft-probes/failures.jsonl \
  --out eval/runs/ft-traces/traces.jsonl
```
Expected: one line per failure printed with its proposed bucket; `traces.jsonl` written. Model-heavy — expect minutes, run once.

- [ ] **Step 4: Commit**

```bash
git add scripts/analysis/trace_failure.py eval/runs/ft-traces
git commit -m "research: failure trace harness + traces for golden and probe misses"
```

---

### Task 5: Human bucket assignment + taxonomy table

Review every trace, confirm or override the proposed bucket, and record evidence. This is judgment work — the harness only proposes.

**Files:**
- Create: `eval/runs/ft-traces/buckets.md`

**Interfaces:**
- Consumes: `traces.jsonl` (Task 4 format), corpus/chunk texts for spot-reading, spec's six buckets: `extraction_loss, chunking_defect, embedding_semantic_miss, sparse_vocabulary_miss, fusion_ranking_loss, metadata_filter_loss`.
- Produces: `buckets.md` — a table `| failure_id | source | class | final_bucket | evidence (1-2 sentences) |` plus a per-bucket count summary. Task 6/7 consume the counts and evidence.

- [ ] **Step 1: Review each trace and assign the final bucket**

For each row in `traces.jsonl`: read the trace, spot-read the gold chunks (`grep -F '<chunk_id>' data/index/chunks.jsonl`) and, where the proposal looks wrong, the corpus text. Rules:
- Trust `extraction_loss` / `chunking_defect` proposals only after eyeballing the actual text (the `_ws` substring check has false positives/negatives on OCR artifacts).
- `embedding_semantic_miss` with BOTH dense and sparse rank -1 deserves a second look — if the chunk itself is bad, it's `chunking_defect`; if the query needs as-of/validity context, it's `metadata_filter_loss`.
- Exactly one primary bucket per failure; note secondary causes in the evidence sentence.

Write each decision as a table row in `eval/runs/ft-traces/buckets.md` as you go.

- [ ] **Step 2: Add the summary section**

At the top of `buckets.md`, add: total failures, count + percentage per bucket, split by source (golden vs probe), and the count of unassigned failures. Verify unassigned ≤ 10% (spec success criterion). If >10%, return to Step 1 for the unassigned rows.

- [ ] **Step 3: Commit**

```bash
git add eval/runs/ft-traces/buckets.md
git commit -m "research: final bucket assignments with per-failure evidence"
```

---

### Task 6: Targeted literature/tooling scan

Scan ONLY for the top buckets by count (typically 2-3). No implementation, no installs — recommendations only.

**Files:**
- Create: `eval/runs/ft-traces/interventions-notes.md` (scratch notes feeding the report)

**Interfaces:**
- Consumes: bucket counts from `buckets.md`.
- Produces: per top bucket, 2-3 candidate interventions, each with: what it is, evidence it helps (paper/benchmark/changelog), Apple-Silicon-local feasibility (license, runtime, MPS/CPU support), integration surface (which sebi_rag module it would touch), effort tier (S/M/L).

- [ ] **Step 1: Identify top buckets**

From `buckets.md`, take buckets covering ≥70% of failures (usually top 2-3). List them in `interventions-notes.md`.

- [ ] **Step 2: Research candidates per bucket (web search)**

Starting points by bucket (pursue only the buckets that actually surfaced):
- `extraction_loss` → Docling, Marker, pymupdf4llm, unstructured — table/layout fidelity on Indian-government PDF styles; all run locally.
- `chunking_defect` → heading-fold repair in `segment.py` (nominee-bug class, already diagnosed in this repo), structure-aware chunking, parent-child chunk retrieval (retrieve small, return enclosing section).
- `embedding_semantic_miss` → query expansion/rewriting with the local LLM, HyDE, instruction-tuned local embedders (bge-m3 alternatives that fit MPS), matryoshka rerank pools.
- `sparse_vocabulary_miss` → SPLADE/uniCOIL-style learned sparse (local), BM25 field boosting (subject/section), synonym expansion from SEBI glossary.
- `fusion_ranking_loss` → RRF k_const sweep (existing `make calibrate`), weighted RRF, candidate-pool widening with reranker budget analysis.
- `metadata_filter_loss` → validity/as-of scoping at retrieval time vs post-rerank demotion (interacts with `pipeline.query` as-of logic — flag, don't redesign).

For each candidate record the fields listed in **Produces**. Cite sources (URL + date).

- [ ] **Step 3: Commit**

```bash
git add eval/runs/ft-traces/interventions-notes.md
git commit -m "research: targeted intervention scan for top failure buckets"
```

---

### Task 7: Final report + self-check

**Files:**
- Create: `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md`

**Interfaces:**
- Consumes: everything from Tasks 1–6.
- Produces: the spec's deliverable — taxonomy, ranked interventions, appendix.

- [ ] **Step 1: Write the report**

Structure (from spec):
1. **Method + baseline** — one paragraph; baseline `recall_at_10` from Task 1, probe hit-rate from Task 3, harvest counts from Task 2/3 summaries.
2. **Failure taxonomy** — the `buckets.md` summary table; per bucket: count, % , 2-3 exemplar failure IDs with query text and one-sentence trace summary. Report ranked-low hits as their own category (per spec they implicate fusion/rerank, not earlier stages).
3. **Ranked intervention list** — order by bucket frequency × fixability. Each entry: target bucket(s), failure IDs addressed, expected gain tier (high/medium/low + reasoning), new local deps if any, effort tier, and the measurement a follow-up would run (e.g. "re-run Task 1 + Task 3 benchmarks; success = candidate_miss count for bucket X drops ≥50%").
4. **Appendix** — pointer to `eval/runs/ft-traces/traces.jsonl` + inline copies of the exemplar traces.

- [ ] **Step 2: Self-check against spec success criteria**

Verify and note results in the report footer:
- ≥90% of harvested failures have a final bucket in `buckets.md` — count it.
- Top 3 interventions each cite specific failure IDs — check each entry.
- All commands/artifacts referenced by path actually exist — `ls` each.

- [ ] **Step 3: Run the full offline test suite (no regressions from the new test file)**

Run: `PYTHONPATH=src uv run pytest -q`
Expected: all tests pass (240 baseline + 4 new = 244, count may drift).

- [ ] **Step 4: Commit and hand off**

```bash
git add docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md
git commit -m "research: pre-retrieval failure taxonomy + ranked interventions report"
```

Then present the report's ranked intervention list to the user — the follow-up implementation gets its own brainstorm/spec/plan cycle per the approved scope (research only).
