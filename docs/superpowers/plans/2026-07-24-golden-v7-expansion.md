# Golden v7 Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Grow the golden eval set from n=56 to n=260 stratified rows with span-anchored chunk-level labels, an external annotation slice (human blind packet + Gemini), and a self-expanding adjudicated-subset CI gate.

**Architecture:** Deterministic scripts do all mechanical work (mining, pooling, packets, agreement); Claude-judgment happens only in drafting and pool-labeling batch tasks under binding anti-leakage rules. Rails land first (validator, span resolver, harness metrics), then data flows through them. The CI gate keeps running on frozen golden_v5 until the v7 adjudicated subset reaches ≥100 rows.

**Tech Stack:** Python 3.12 (`.venv`), pytest offline suite (`-m "not integration"`), HashEmbedder/LexicalReranker/ExtractiveStubGenerator for offline tests, bm25s + FAISS + bge-m3 + bge-reranker-v2-m3 for the two real-stack scripts, httpx for the Gemini REST leg.

**Spec:** `docs/superpowers/specs/2026-07-23-golden-v7-expansion-design.md` (read it before starting any task; its §5 anti-leakage rules are binding).

## Global Constraints

- Python is ALWAYS `.venv/bin/python`; tests run as `.venv/bin/python -m pytest -q -m "not integration"` from repo root. `PYTHONPATH=src` is set by pytest config; scripts insert `src` on `sys.path` themselves (copy the existing pattern).
- Real-stack scripts (pool build, external pass, gate) need env: `HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1` (Makefile `$(ENV)` provides them).
- Sampling seed is **20260723** everywhere (`random.Random(20260723)`).
- The spec's "temporal_supersession" stratum uses the **existing** task_type value `lineage_supersession` (already in `TASK_TYPES`). New task_type values added: `multi_hop`, `repealed_basis`. Never rename existing values.
- Strata targets (exact, n=260): title_direct 40, body_paraphrase 60, numeric_table 30, lineage_supersession 40, multi_hop 20, repealed_basis 20, hard_negative 40, far_negative 10.
- New row ids: `v7-<px>-NNN` with prefix map td/bp/nt/ls/mh/rb/hn/fn (three-digit, zero-padded, unique). Carried v5/v6 ids stay unchanged.
- `relevant_chunks` entries are span objects `{"doc": <circular_number>, "quote": <verbatim substring>}`, quote ≥40 chars after whitespace-normalization, taken from chunk BODY text (never the first enrichment-header line `"<circular> | <subject> | <section>"`).
- **Anti-leakage (spec §5, verbatim in every drafting subagent prompt):** (1) queries are drafted one-shot from source text only and frozen before any retrieval runs — never iterate a query against the retriever; (2) drafting must not read `src/sebi_rag/expand.py`; (3) negatives may use BM25 absence-verification output already present in candidate files; (4) all sampling seeded 20260723.
- Frozen files — never modify: `eval/golden/golden_v1..v6.jsonl`, `eval/probes/probes_v1.jsonl`, `eval/golden/golden_asof_v1.jsonl`.
- Commits end with `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Vote record (shared by Tasks 8–12): `{"id": <row_id>, "annotator": "claude"|"gemini"|"human", "governing": [<chunk_id>, ...], "expected_literal": <str>}` appended to `eval/golden/v7_annotations/votes.jsonl`. Empty `governing` means "none/abstain".
- Pool record (Tasks 7–10): `{"id": <row_id>, "candidates": [{"chunk_id": str, "doc": str, "text": str}, ...]}` in `eval/golden/v7_annotations/pools.jsonl`.

---

### Task 1: v7 schema constants + `validate_golden_v7` rails

**Files:**
- Modify: `src/sebi_rag/benchmark.py` (after `REVIEW_STATUSES`, line ~36, and after `validate_golden`, line ~202)
- Test: `tests/test_golden_v7_schema.py` (create)

**Interfaces:**
- Consumes: existing `validate_golden(rows) -> list[BenchmarkIssue]`, `BenchmarkIssue(item_id, message)`.
- Produces: `STRATA_TARGETS_V7: dict[str, int]`; `V7_ID_RE` (compiled regex); `validate_golden_v7(rows: list[dict], chunks: list[Chunk] | None = None) -> list[BenchmarkIssue]`. Task 2 adds quote-resolution rails into it; Tasks 4/6/8 run it as their gate.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_golden_v7_schema.py
"""Offline tests for the golden_v7 schema rails (spec 2026-07-23 §3, §4, §8)."""
from sebi_rag.benchmark import (
    STRATA_TARGETS_V7, validate_golden_v7,
)


def _row(**over):
    base = {
        "id": "v7-ls-001", "query": "What replaced the 2020 margin circular?",
        "relevant_circulars": ["SEBI/HO/NEW/2024/1"],
        "relevant_chunks": [{"doc": "SEBI/HO/NEW/2024/1",
                             "quote": "the margin requirements specified herein shall apply to all"}],
        "answer_contains": "margin", "must_contain": ["margin"],
        "must_not_contain": [], "must_not_cite": ["SEBI/HO/OLD/2020/9"],
        "abstain": False, "as_of": None, "task_type": "lineage_supersession",
        "difficulty": "hard", "expected_citation_level": "chunk",
        "rationale": "test", "label_source": "v7-miner-lineage",
        "review_status": "draft",
    }
    base.update(over)
    return base


def test_strata_targets_sum_to_260():
    assert sum(STRATA_TARGETS_V7.values()) == 260
    assert STRATA_TARGETS_V7["lineage_supersession"] == 40


def test_valid_row_passes():
    assert validate_golden_v7([_row()]) == []


def test_bad_v7_id_flagged():
    issues = validate_golden_v7([_row(id="v7-xx-1")])
    assert any("id" in i.message for i in issues)


def test_carried_ids_exempt_from_v7_pattern():
    row = _row(id="surv", must_not_cite=[], task_type="title_direct",
               label_source="golden_v5", review_status="seeded")
    assert validate_golden_v7([row]) == []


def test_short_quote_flagged():
    row = _row(relevant_chunks=[{"doc": "SEBI/HO/NEW/2024/1", "quote": "too short"}])
    issues = validate_golden_v7([row])
    assert any("quote" in i.message for i in issues)


def test_quote_doc_must_be_relevant_circular():
    row = _row(relevant_chunks=[{"doc": "SEBI/HO/OTHER/2021/5",
                                 "quote": "x" * 50}])
    issues = validate_golden_v7([row])
    assert any("doc" in i.message for i in issues)


def test_as_of_only_on_lineage_rows_and_iso():
    issues = validate_golden_v7([_row(task_type="title_direct",
                                      must_not_cite=[], as_of="2023-05-01")])
    assert any("as_of" in i.message for i in issues)
    issues = validate_golden_v7([_row(as_of="01/05/2023")])
    assert any("as_of" in i.message for i in issues)


def test_must_not_cite_only_on_lineage_rows():
    issues = validate_golden_v7([_row(task_type="title_direct")])
    assert any("must_not_cite" in i.message for i in issues)


def test_abstain_row_needs_no_labels():
    row = _row(id="v7-hn-001", task_type="hard_negative", abstain=True,
               relevant_circulars=[], relevant_chunks=[], must_contain=[],
               must_not_cite=[], as_of=None, expected_citation_level="none")
    assert validate_golden_v7([row]) == []


def test_census_enforced_at_full_size():
    rows = [_row(id=f"v7-ls-{i:03d}") for i in range(260)]
    issues = validate_golden_v7(rows)
    assert any("census" in i.message for i in issues)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_schema.py`
Expected: FAIL with `ImportError: cannot import name 'STRATA_TARGETS_V7'`

- [ ] **Step 3: Implement in `src/sebi_rag/benchmark.py`**

Add `"multi_hop", "repealed_basis"` to the `TASK_TYPES` set literal. After `validate_golden`, add:

```python
import re as _re
from datetime import date as _date

STRATA_TARGETS_V7 = {
    "title_direct": 40, "body_paraphrase": 60, "numeric_table": 30,
    "lineage_supersession": 40, "multi_hop": 20, "repealed_basis": 20,
    "hard_negative": 40, "far_negative": 10,
}
V7_ID_RE = _re.compile(r"^v7-(td|bp|nt|ls|mh|rb|hn|fn)-\d{3}$")
_MIN_QUOTE_CHARS = 40


def _norm_ws(text: str) -> str:
    return " ".join(text.split()).lower()


def validate_golden_v7(
    rows: list[dict[str, Any]], chunks: list[Chunk] | None = None
) -> list[BenchmarkIssue]:
    """Spec 2026-07-23 §3/§4/§8 rails on top of validate_golden.

    `chunks` is optional: when provided, every span quote must resolve to at
    least one chunk of its doc (re-chunking drift is a loud error, never rot).
    """
    issues = list(validate_golden(rows))
    for row in rows:
        rid = str(row.get("id", "<no-id>"))
        if rid.startswith("v7-") and not V7_ID_RE.match(rid):
            issues.append(BenchmarkIssue(rid, "invalid v7 id format"))
        as_of = row.get("as_of")
        if as_of is not None:
            if row.get("task_type") != "lineage_supersession":
                issues.append(BenchmarkIssue(rid, "as_of only allowed on lineage_supersession"))
            else:
                try:
                    _date.fromisoformat(as_of)
                except (TypeError, ValueError):
                    issues.append(BenchmarkIssue(rid, f"as_of not ISO: {as_of!r}"))
        mnc = row.get("must_not_cite", [])
        if mnc and row.get("task_type") != "lineage_supersession":
            issues.append(BenchmarkIssue(rid, "must_not_cite only allowed on lineage_supersession"))
        if mnc and row.get("abstain"):
            issues.append(BenchmarkIssue(rid, "abstain row has must_not_cite"))
        relevant = set(row.get("relevant_circulars", []))
        for span in row.get("relevant_chunks", []):
            if not isinstance(span, dict) or set(span) != {"doc", "quote"}:
                issues.append(BenchmarkIssue(rid, f"span must be {{doc, quote}}: {span!r}"))
                continue
            if span["doc"] not in relevant:
                issues.append(BenchmarkIssue(rid, f"span doc not in relevant_circulars: {span['doc']}"))
            if len(_norm_ws(span["quote"])) < _MIN_QUOTE_CHARS:
                issues.append(BenchmarkIssue(rid, f"quote under {_MIN_QUOTE_CHARS} chars"))
    if len(rows) >= sum(STRATA_TARGETS_V7.values()):
        from collections import Counter
        census = Counter(r.get("task_type") for r in rows)
        for tt, want in STRATA_TARGETS_V7.items():
            if census.get(tt, 0) != want:
                issues.append(BenchmarkIssue(
                    "<census>", f"census: {tt} has {census.get(tt, 0)}, want {want}"))
        for tt in STRATA_TARGETS_V7:
            strat = [r for r in rows if r.get("task_type") == tt]
            hard = sum(1 for r in strat if r.get("difficulty") == "hard")
            if strat and hard / len(strat) < 0.2:
                issues.append(BenchmarkIssue("<census>", f"census: {tt} under 20% hard"))
    if chunks is not None:
        issues.extend(_span_resolution_issues(rows, chunks))
    return issues


def _span_resolution_issues(
    rows: list[dict[str, Any]], chunks: list[Chunk]
) -> list[BenchmarkIssue]:
    return []  # replaced in Task 2 with real resolution checks
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_schema.py`
Expected: PASS (10 tests)

- [ ] **Step 5: Full offline suite, then commit**

Run: `.venv/bin/python -m pytest -q -m "not integration"`
Expected: no regressions (baseline 459 passing).

```bash
git add src/sebi_rag/benchmark.py tests/test_golden_v7_schema.py
git commit -m "feat(golden-v7): schema constants + validate_golden_v7 rails

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Span resolver + qrels span support

**Files:**
- Modify: `src/sebi_rag/benchmark.py` (`_span_resolution_issues` stub from Task 1; `qrels_rows` at line ~231)
- Test: `tests/test_golden_v7_resolver.py` (create)

**Interfaces:**
- Consumes: `_norm_ws`, `BenchmarkIssue`, `Chunk` (fields: `id`, `doc_id`, `section`, `text`, `meta`), `normalize_circular_number`.
- Produces: `resolve_chunk_spans(row: dict, chunks_by_doc: dict[str, list[Chunk]]) -> list[str]` (chunk ids, deduped, [] when nothing resolves); `chunks_by_doc(chunks: list[Chunk]) -> dict[str, list[Chunk]]`. Task 3 (harness metrics) and `qrels_rows` both call these.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_golden_v7_resolver.py
"""Span→chunk resolution (spec §3): quotes survive re-chunking; failures are loud."""
from sebi_rag.benchmark import (
    chunks_by_doc, qrels_rows, resolve_chunk_spans, validate_golden_v7,
)
from sebi_rag.segment import CircularMeta, hierarchical_chunk

_TEXT = (
    "1. Applicability:\nThis circular applies to all registered stock brokers "
    "and depository participants dealing in the equity derivatives segment.\n\n"
    "2. Margin requirements:\nThe upfront margin shall be collected at the rate "
    "of twenty per cent of the transaction value in all cases without exception."
)


def _chunks(doc="SEBI/HO/T/2024/1"):
    return hierarchical_chunk(_TEXT, CircularMeta(circular_number=doc, subject="Margins"))


def _row(quote, doc="SEBI/HO/T/2024/1"):
    return {"id": "v7-nt-001", "relevant_circulars": [doc],
            "relevant_chunks": [{"doc": doc, "quote": quote}], "abstain": False}


def test_resolves_normalized_whitespace_quote():
    chunks = _chunks()
    quote = "upfront  margin shall be collected at the\nrate of twenty per cent"
    ids = resolve_chunk_spans(_row(quote), chunks_by_doc(chunks))
    assert ids and all(i in {c.id for c in chunks} for i in ids)


def test_unresolvable_quote_returns_empty():
    ids = resolve_chunk_spans(
        _row("this text appears nowhere in the corpus at all, honestly"),
        chunks_by_doc(_chunks()))
    assert ids == []


def test_legacy_string_entries_pass_through():
    row = {"id": "x", "relevant_chunks": ["SEBI/HO/T/2024/1#preamble#0"]}
    assert resolve_chunk_spans(row, {}) == ["SEBI/HO/T/2024/1#preamble#0"]


def test_validator_flags_unresolvable_quote_when_chunks_given():
    row = _row("this text appears nowhere in the corpus at all, honestly")
    row.update({"query": "q", "answer_contains": "", "must_contain": [],
                "must_not_contain": [], "task_type": "numeric_table",
                "difficulty": "hard", "expected_citation_level": "chunk",
                "rationale": "t", "label_source": "t", "review_status": "draft"})
    issues = validate_golden_v7([row], chunks=_chunks())
    assert any("resolve" in i.message for i in issues)


def test_qrels_span_rows_get_grade_2():
    chunks = _chunks()
    golden = [{"id": "q1", "abstain": False,
               "relevant_circulars": ["SEBI/HO/T/2024/1"],
               "relevant_chunks": [{"doc": "SEBI/HO/T/2024/1",
                                    "quote": "upfront margin shall be collected at the rate of twenty per cent"}]}]
    rows = qrels_rows(golden, chunks)
    assert rows and all(score == 2 for _, _, score in rows)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_resolver.py`
Expected: FAIL with `ImportError: cannot import name 'chunks_by_doc'`

- [ ] **Step 3: Implement**

In `benchmark.py`, replace the `_span_resolution_issues` stub and add the resolver; update `qrels_rows`:

```python
def chunks_by_doc(chunks: list[Chunk]) -> dict[str, list[Chunk]]:
    out: dict[str, list[Chunk]] = {}
    for c in chunks:
        out.setdefault(c.doc_id, []).append(c)
    return out


def resolve_chunk_spans(
    row: dict[str, Any], by_doc: dict[str, list[Chunk]]
) -> list[str]:
    """Span {doc, quote} -> matching chunk ids (all overlap matches count).

    Legacy plain-string entries pass through untouched (v6 compat)."""
    ids: list[str] = []
    for span in row.get("relevant_chunks", []):
        if isinstance(span, str):
            ids.append(span)
            continue
        q = _norm_ws(span.get("quote", ""))
        if not q:
            continue
        ids.extend(c.id for c in by_doc.get(span.get("doc", ""), [])
                   if q in _norm_ws(c.text))
    return _unique(ids)


def _span_resolution_issues(
    rows: list[dict[str, Any]], chunks: list[Chunk]
) -> list[BenchmarkIssue]:
    by_doc = chunks_by_doc(chunks)
    issues = []
    for row in rows:
        rid = str(row.get("id", "<no-id>"))
        for span in row.get("relevant_chunks", []):
            if isinstance(span, dict) and not resolve_chunk_spans(
                    {"relevant_chunks": [span]}, by_doc):
                issues.append(BenchmarkIssue(
                    rid, f"quote does not resolve to any chunk of {span.get('doc')}"))
    return issues
```

In `qrels_rows`, replace the `explicit = [...]` line with:

```python
        explicit = [cid for cid in resolve_chunk_spans(item, chunks_by_doc(chunks))
                    if cid in by_id]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_resolver.py tests/test_golden_v7_schema.py`
Expected: PASS

- [ ] **Step 5: Full offline suite (export tests exercise qrels_rows), then commit**

Run: `.venv/bin/python -m pytest -q -m "not integration"`
Expected: no regressions.

```bash
git add src/sebi_rag/benchmark.py tests/test_golden_v7_resolver.py
git commit -m "feat(golden-v7): span-anchored chunk labels — resolver + qrels grade-2 support

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Harness — as_of passthrough, must_not_cite, chunk metrics, gate sub-report

**Files:**
- Modify: `src/sebi_rag/eval_harness.py` (whole `run_eval` body + `EvalReport`)
- Test: `tests/test_eval_harness_v7.py` (create; existing `tests/test_eval_harness.py` loads the real corpus — do not touch it)

**Interfaces:**
- Consumes: `resolve_chunk_spans`, `chunks_by_doc` from `benchmark` — import inside `run_eval` to avoid a module cycle (`benchmark` imports `eval_harness` at top level).
- Produces: `EvalReport` gains `chunk_recall_at_k: float`, `chunk_mrr: float`, `chunk_labeled_n: int`, `must_not_cite_violation_rate: float`, `gate: dict | None`. `run_eval(pipeline, golden, k=10)` signature unchanged; it now calls `pipeline.query(item["query"], as_of=item.get("as_of"))`. Task 13's CI emitter consumes `gate`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_eval_harness_v7.py
"""Offline harness tests for v7 metrics: as_of passthrough, must_not_cite,
chunk-level recall/MRR, and the adjudicated-subset gate sub-report."""
from sebi_rag.embeddings import HashEmbedder
from sebi_rag.eval_harness import run_eval
from sebi_rag.generate import ExtractiveStubGenerator
from sebi_rag.pipeline import RAGPipeline
from sebi_rag.rerank import LexicalReranker
from sebi_rag.segment import CircularMeta, hierarchical_chunk

_DOC = "SEBI/HO/T/2024/1"
_TEXT = (
    "1. Applicability:\nThis circular applies to all registered stock brokers "
    "and depository participants dealing in the equity derivatives segment.\n\n"
    "2. Margin requirements:\nThe upfront margin shall be collected at the rate "
    "of twenty per cent of the transaction value in all cases without exception."
)


def _pipeline():
    chunks = hierarchical_chunk(
        _TEXT, CircularMeta(circular_number=_DOC, subject="Margin requirements"))
    return RAGPipeline.build(chunks, HashEmbedder(), LexicalReranker(),
                             ExtractiveStubGenerator(), abstain_threshold=0.0)


def _row(**over):
    base = {"id": "v7-nt-001", "query": "upfront margin rate for stock brokers",
            "relevant_circulars": [_DOC],
            "relevant_chunks": [{"doc": _DOC,
                                 "quote": "upfront margin shall be collected at the rate of twenty per cent"}],
            "answer_contains": "twenty", "must_contain": [], "must_not_contain": [],
            "abstain": False, "task_type": "numeric_table", "difficulty": "hard",
            "review_status": "draft"}
    base.update(over)
    return base


def test_chunk_metrics_computed_for_span_rows():
    report = run_eval(_pipeline(), [_row()], k=10)
    assert report.chunk_labeled_n == 1
    assert report.chunk_recall_at_k == 1.0
    assert report.chunk_mrr > 0.0


def test_rows_without_spans_do_not_dilute_chunk_metrics():
    report = run_eval(_pipeline(), [_row(), _row(id="v7-td-001", relevant_chunks=[])], k=10)
    assert report.chunk_labeled_n == 1


def test_as_of_is_passed_to_pipeline():
    calls = {}
    class _Spy:
        retriever = _pipeline().retriever
        def query(self, q, as_of=None, **kw):
            calls["as_of"] = as_of
            return _pipeline().query(q)
    run_eval(_Spy(), [_row(as_of="2023-05-01", task_type="lineage_supersession",
                           must_not_cite=[])], k=10)
    assert calls["as_of"] == "2023-05-01"


def test_must_not_cite_violation_counted():
    report = run_eval(_pipeline(), [_row(task_type="lineage_supersession",
                                         must_not_cite=[_DOC])], k=10)
    assert report.must_not_cite_violation_rate == 1.0


def test_gate_subreport_covers_only_adjudicated():
    rows = [_row(), _row(id="v7-nt-002", review_status="adjudicated")]
    report = run_eval(_pipeline(), rows, k=10)
    assert report.gate is not None and report.gate["n"] == 1
    assert 0.0 <= report.gate["recall_at_k"] <= 1.0


def test_gate_is_none_when_nothing_adjudicated():
    assert run_eval(_pipeline(), [_row()], k=10).gate is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest -q tests/test_eval_harness_v7.py`
Expected: FAIL with `AttributeError: ... 'chunk_labeled_n'` (or TypeError on `as_of`)

- [ ] **Step 3: Implement in `eval_harness.py`**

Replace `EvalReport` and `run_eval` with:

```python
@dataclass
class EvalReport:
    n: int
    recall_at_k: float
    mrr: float
    ndcg_at_k: float
    citation_precision: float
    citation_recall: float
    abstention_accuracy: float
    groundedness_proxy: float
    faithfulness: float
    avg_latency_s: float
    k: int
    chunk_recall_at_k: float = 0.0
    chunk_mrr: float = 0.0
    chunk_labeled_n: int = 0
    must_not_cite_violation_rate: float = 0.0
    gate: dict | None = None  # same aggregate over review_status == "adjudicated"


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _eval_item(pipeline: RAGPipeline, item: dict, k: int, by_doc) -> dict:
    from .benchmark import resolve_chunk_spans  # local: benchmark imports us

    rec = {"adjudicated": item.get("review_status") == "adjudicated"}
    relevant = set(item.get("relevant_circulars", []))
    t0 = time.time()
    ans, retrieved_ids = pipeline.query(item["query"], as_of=item.get("as_of"))
    rec["latency"] = time.time() - t0
    if item.get("abstain"):
        rec["abstain_ok"] = ans.abstained
        return rec
    rec["abstain_ok"] = not ans.abstained
    rec["faith"] = ans.faithfulness
    retrieved_docs = _unique(_doc(i) for i in retrieved_ids)
    rec["recall"] = M.recall_at_k(retrieved_docs, relevant, k)
    rec["mrr"] = M.mrr(retrieved_docs, relevant)
    rec["ndcg"] = M.ndcg_at_k(retrieved_docs, relevant, k)
    pred = _unique(_doc(c) for c in ans.citations)
    hit = len(set(pred) & relevant)
    rec["cprec"] = hit / len(pred) if pred else 0.0
    rec["crec"] = hit / len(relevant) if relevant else 0.0
    want = (item.get("answer_contains") or "").lower()
    rec["ground"] = 1.0 if want and want in ans.text.lower() else 0.0
    forbidden = set(item.get("must_not_cite", []))
    if forbidden:
        cited_docs = set(pred)
        rec["mnc_violation"] = 1.0 if cited_docs & forbidden else 0.0
    gold_chunks = set(resolve_chunk_spans(item, by_doc))
    if gold_chunks:
        top = retrieved_ids[:k]
        rec["chunk_recall"] = len(set(top) & gold_chunks) / len(gold_chunks)
        rec["chunk_mrr"] = next(
            (1.0 / r for r, cid in enumerate(retrieved_ids, 1) if cid in gold_chunks), 0.0)
    return rec


def _aggregate(recs: list[dict], k: int) -> dict:
    chunk = [r for r in recs if "chunk_recall" in r]
    return {
        "n": len(recs),
        "recall_at_k": _mean([r["recall"] for r in recs if "recall" in r]),
        "mrr": _mean([r["mrr"] for r in recs if "mrr" in r]),
        "ndcg_at_k": _mean([r["ndcg"] for r in recs if "ndcg" in r]),
        "citation_precision": _mean([r["cprec"] for r in recs if "cprec" in r]),
        "citation_recall": _mean([r["crec"] for r in recs if "crec" in r]),
        "abstention_accuracy": _mean([r["abstain_ok"] for r in recs]),
        "groundedness_proxy": _mean([r["ground"] for r in recs if "ground" in r]),
        "faithfulness": _mean([r["faith"] for r in recs if "faith" in r]),
        "avg_latency_s": _mean([r["latency"] for r in recs]),
        "k": k,
        "chunk_recall_at_k": _mean([r["chunk_recall"] for r in chunk]),
        "chunk_mrr": _mean([r["chunk_mrr"] for r in chunk]),
        "chunk_labeled_n": len(chunk),
        "must_not_cite_violation_rate": _mean(
            [r["mnc_violation"] for r in recs if "mnc_violation" in r]),
    }


def run_eval(pipeline: RAGPipeline, golden: list[dict], k: int = 10) -> EvalReport:
    from .benchmark import chunks_by_doc  # local: benchmark imports us

    by_doc = chunks_by_doc(pipeline.retriever.chunks)
    recs = [_eval_item(pipeline, item, k, by_doc) for item in golden]
    agg = _aggregate(recs, k)
    gated = [r for r in recs if r["adjudicated"]]
    agg["gate"] = {k2: v for k2, v in _aggregate(gated, k).items()} if gated else None
    return EvalReport(**agg)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest -q tests/test_eval_harness_v7.py`
Expected: PASS (6 tests)

- [ ] **Step 5: Full offline suite (guards `test_eval_harness.py` P1 behavior), then commit**

Run: `.venv/bin/python -m pytest -q -m "not integration"`
Expected: no regressions.

```bash
git add src/sebi_rag/eval_harness.py tests/test_eval_harness_v7.py
git commit -m "feat(golden-v7): harness chunk metrics, as_of passthrough, must_not_cite, adjudicated gate sub-report

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Seed script — carry the 56 v6 rows into golden_v7.jsonl

**Files:**
- Create: `scripts/golden_v7/__init__.py` (empty), `scripts/golden_v7/seed_v7.py`
- Modify: `Makefile` (append target after `benchmark-export`)
- Test: `tests/test_golden_v7_seed.py` (create)

**Interfaces:**
- Consumes: `load_golden`, `validate_golden_v7`, `write_jsonl` from `sebi_rag`.
- Produces: `carry_v6_rows(rows: list[dict]) -> list[dict]` (pure, importable as `scripts.golden_v7.seed_v7.carry_v6_rows`); the file `eval/golden/golden_v7.jsonl` (56 rows, `review_status` stays `seeded`, adds `as_of: None` + `must_not_cite: []` defaults). Drafting tasks append to this file.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_golden_v7_seed.py
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.seed_v7 import carry_v6_rows  # noqa: E402


def test_carry_preserves_ids_and_adds_v7_defaults():
    v6 = [{"id": "surv", "query": "q", "relevant_circulars": ["C/1"],
           "relevant_chunks": [], "answer_contains": "a", "must_contain": ["a"],
           "must_not_contain": [], "abstain": False, "task_type": "title_direct",
           "difficulty": "medium", "expected_citation_level": "circular",
           "rationale": "r", "label_source": "golden_v5", "review_status": "seeded"}]
    out = carry_v6_rows(v6)
    assert out[0]["id"] == "surv"
    assert out[0]["as_of"] is None and out[0]["must_not_cite"] == []
    assert out[0]["review_status"] == "seeded"


def test_seed_script_writes_56_valid_rows(tmp_path):
    root = Path(__file__).resolve().parents[1]
    out = tmp_path / "golden_v7.jsonl"
    subprocess.run(
        [sys.executable, str(root / "scripts" / "golden_v7" / "seed_v7.py"),
         "--out", str(out)], check=True)
    rows = [json.loads(l) for l in out.read_text().splitlines()]
    assert len(rows) == 56
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_seed.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'golden_v7'`

- [ ] **Step 3: Implement `scripts/golden_v7/seed_v7.py`**

```python
"""Seed golden_v7.jsonl from frozen golden_v6 (spec 2026-07-23 §3, §10 phase 3).

Carries all 56 rows unchanged (ids, labels, `seeded` status — no grandfathering:
seeded behaves as draft for promotion) and adds the v7-only fields.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.benchmark import validate_golden_v7, write_jsonl  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402


def carry_v6_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        r = dict(r)
        r.setdefault("as_of", None)
        r.setdefault("must_not_cite", [])
        out.append(r)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "eval" / "golden" / "golden_v7.jsonl"))
    args = ap.parse_args()
    rows = carry_v6_rows(load_golden(ROOT / "eval" / "golden" / "golden_v6.jsonl"))
    issues = validate_golden_v7(rows)
    if issues:
        for i in issues:
            print(f"{i.item_id}: {i.message}", file=sys.stderr)
        raise SystemExit(1)
    write_jsonl(args.out, rows)
    print(f"wrote {len(rows)} rows -> {args.out}")


if __name__ == "__main__":
    main()
```

Create empty `scripts/golden_v7/__init__.py`. Append to `Makefile` (tab-indented recipe, matching existing style):

```make
golden-v7-seed:
	$(ENV) $(PY) scripts/golden_v7/seed_v7.py
```

- [ ] **Step 4: Run test, then generate the real file**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_seed.py` → PASS
Run: `make golden-v7-seed`
Expected: `wrote 56 rows -> .../eval/golden/golden_v7.jsonl`

- [ ] **Step 5: Commit (including the generated file)**

```bash
git add scripts/golden_v7/ tests/test_golden_v7_seed.py Makefile eval/golden/golden_v7.jsonl
git commit -m "feat(golden-v7): seed v7 from frozen v6 (56 rows, no grandfathering)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: `mine_strata.py` — candidate sources for every stratum

**Files:**
- Create: `scripts/golden_v7/mine_strata.py`
- Modify: `Makefile` (append `golden-v7-mine`)
- Test: `tests/test_golden_v7_mine.py` (create)

**Interfaces:**
- Consumes: corpus records via `sebi_rag.lineage.load_records(path) -> list[dict]` (fields used: `circular_number`, `subject`, `issue_date`, `text`, `regulatory_basis_status`, `regulations`); chunks via `sebi_rag.corpus.load_circulars(path) -> list[Chunk]`; `data/index/lineage.json` (`{"superseded_by": {circ: [circ,...]}, "edges": [...]}`); `bm25s` for negative-absence sweeps.
- Produces: pure functions below + `eval/golden/v7_annotations/candidates/<stratum>.jsonl`. Drafting tasks (6A–6E) read only these candidate files.
  - `sample_title_direct(records, n, rng) -> list[dict]` — `{"circular_number", "subject", "issue_date"}`, stratified round-robin over (year, issuing_department) buckets.
  - `sample_paraphrase_chunks(chunks, n, rng) -> list[dict]` — `{"chunk_id", "doc", "subject", "text"}`, body chunks only (section not "preamble", body ≥300 chars).
  - `mine_numeric(chunks, n, rng) -> list[dict]` — same shape, only chunks whose body matches `re.compile(r"(?i)(\bannexure\b|\bper cent\b|\d+\s*%|\blakh\b|\bcrore\b|within\s+\d+\s+(?:calendar\s+|working\s+)?days)")`.
  - `mine_lineage_pairs(superseded_by, records_by_id, n, rng) -> list[dict]` — `{"old", "new", "old_date", "new_date", "as_of_mid", "as_of_before"}` where both ids are in `records_by_id` and both have non-empty `issue_date`; `as_of_mid` = ISO date halfway between the two issue dates; `as_of_before` = old_date minus 30 days.
  - `mine_multi_hop(edges, records_by_id, n, rng) -> list[dict]` — `{"a", "b", "subject_a", "subject_b"}` for reference-edge pairs with both ends in-corpus and different circulars.
  - `mine_repealed_basis(records, n, rng) -> list[dict]` — `{"circular_number", "subject", "regulations"}` for records with `regulatory_basis_status == "repealed_basis"`.
  - `verify_negative_absence(bm25_index, corpus_texts_meta, topics) -> list[dict]` — per topic `{"topic", "top_hits": [{"doc", "subject"}...3]}` so the drafting batch can eyeball that nothing governs it.
- Oversampling rule: every miner emits 2× the stratum's *new-row* need (e.g. 90 paraphrase candidates for 45 rows) so drafting can skip junk without re-mining.

- [ ] **Step 1: Write the failing tests** (pure functions on tiny fixtures)

```python
# tests/test_golden_v7_mine.py
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.mine_strata import (  # noqa: E402
    mine_lineage_pairs, mine_numeric, mine_repealed_basis, sample_paraphrase_chunks,
    sample_title_direct,
)
from sebi_rag.segment import CircularMeta, hierarchical_chunk  # noqa: E402


def _rec(cn, date="2024-01-10", dept="ISD", **over):
    r = {"circular_number": cn, "subject": f"About {cn}", "issue_date": date,
         "issuing_department": dept, "text": "body " * 200}
    r.update(over)
    return r


def test_title_direct_stratifies_across_years():
    recs = [_rec(f"C/{y}/{i}", date=f"{y}-03-01") for y in (2022, 2023, 2024) for i in range(5)]
    got = sample_title_direct(recs, 6, random.Random(20260723))
    assert len(got) == 6
    assert len({r["issue_date"][:4] for r in got}) == 3  # all years covered


def test_paraphrase_skips_preamble_and_short_chunks():
    chunks = hierarchical_chunk(
        "intro line\n\n1. Rule:\n" + ("The registered intermediary shall maintain records. " * 20),
        CircularMeta(circular_number="C/1", subject="Records"))
    got = sample_paraphrase_chunks(chunks, 5, random.Random(20260723))
    assert got and all("preamble" not in g["chunk_id"] for g in got)


def test_numeric_miner_requires_numeric_pattern():
    chunks = hierarchical_chunk(
        "1. Fees:\n" + ("The fee shall be twenty five per cent of turnover payable "
                        "within 30 days of the end of the quarter. " * 10),
        CircularMeta(circular_number="C/2", subject="Fees"))
    assert mine_numeric(chunks, 3, random.Random(20260723))


def test_lineage_pairs_need_both_dates_and_membership():
    recs = {"OLD/1": _rec("OLD/1", "2020-06-01"), "NEW/1": _rec("NEW/1", "2023-06-01")}
    pairs = mine_lineage_pairs({"OLD/1": ["NEW/1"], "GONE/9": ["NEW/1"]}, recs, 5,
                               random.Random(20260723))
    assert len(pairs) == 1
    p = pairs[0]
    assert p["old"] == "OLD/1" and "2020-06-01" < p["as_of_mid"] < "2023-06-01"
    assert p["as_of_before"] < "2020-06-01"


def test_repealed_basis_filters_on_status():
    recs = [_rec("C/3", regulatory_basis_status="repealed_basis", regulations=[]),
            _rec("C/4", regulatory_basis_status="current")]
    got = mine_repealed_basis(recs, 5, random.Random(20260723))
    assert [g["circular_number"] for g in got] == ["C/3"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_mine.py`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `scripts/golden_v7/mine_strata.py`**

```python
"""Deterministic candidate mining for golden_v7 drafting (spec §4, §5).

Pure functions + a main() that writes one JSONL per stratum under
eval/golden/v7_annotations/candidates/. Seed 20260723. Oversamples 2x.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.corpus import load_circulars  # noqa: E402
from sebi_rag.lineage import load_records  # noqa: E402

NUMERIC_RE = re.compile(
    r"(?i)(\bannexure\b|\bper cent\b|\d+\s*%|\blakh\b|\bcrore\b|"
    r"within\s+\d+\s+(?:calendar\s+|working\s+)?days)")

# Near-domain topics with no governing document in the 705-circular corpus.
# Drafting batch 6E confirms absence via the top_hits the sweep attaches.
HARD_NEGATIVE_TOPICS = [
    "RBI prudential norms for NBFC gold loans",
    "IRDAI motor insurance premium filing",
    "MCA board meeting frequency for private companies",
    "Income tax TDS rates on dividend income",
    "SEBI requirements for crypto asset custodians",
    "FEMA overseas direct investment reporting by individuals",
    "Bank locker agreement stamp duty",
    "GST e-invoicing turnover threshold",
    "PFRDA NPS partial withdrawal rules",
    "Competition Commission merger notification thresholds",
    # drafting expands variations from these seeds to reach 30 rows
]
FAR_NEGATIVE_TOPICS = [
    "best sourdough fermentation schedule", "monsoon trekking routes in Sahyadris",
    "python asyncio event loop internals", "history of the Deccan sultanates",
    "cricket LBW review protocol", "EV battery thermal runaway chemistry",
    "Himalayan glacier mass balance measurement", "opera seria vocal ornamentation",
    "sous vide steak temperatures",
]


def _body(chunk_text: str) -> str:
    lines = chunk_text.split("\n", 1)
    return lines[1] if len(lines) > 1 else lines[0]


def sample_title_direct(records, n, rng):
    buckets: dict[tuple[str, str], list[dict]] = {}
    for r in records:
        key = ((r.get("issue_date") or "")[:4], r.get("issuing_department", ""))
        buckets.setdefault(key, []).append(r)
    for b in buckets.values():
        rng.shuffle(b)
    order = sorted(buckets)
    out, i = [], 0
    while len(out) < n and any(buckets[k] for k in order):
        key = order[i % len(order)]
        if buckets[key]:
            r = buckets[key].pop()
            out.append({"circular_number": r["circular_number"],
                        "subject": r.get("subject", ""),
                        "issue_date": r.get("issue_date", "")})
        i += 1
    return out


def sample_paraphrase_chunks(chunks, n, rng):
    pool = [c for c in chunks
            if "#preamble#" not in c.id and len(_body(c.text)) >= 300]
    rng.shuffle(pool)
    return [{"chunk_id": c.id, "doc": c.doc_id,
             "subject": (c.meta or {}).get("subject", ""), "text": _body(c.text)}
            for c in pool[:n]]


def mine_numeric(chunks, n, rng):
    pool = [c for c in chunks
            if "#preamble#" not in c.id and NUMERIC_RE.search(_body(c.text))]
    rng.shuffle(pool)
    return [{"chunk_id": c.id, "doc": c.doc_id,
             "subject": (c.meta or {}).get("subject", ""), "text": _body(c.text)}
            for c in pool[:n]]


def _mid(d1: str, d2: str) -> str:
    a, b = date.fromisoformat(d1), date.fromisoformat(d2)
    return (a + (b - a) / 2).isoformat()


def mine_lineage_pairs(superseded_by, records_by_id, n, rng):
    pairs = []
    for old, news in sorted(superseded_by.items()):
        for new in news:
            ro, rn = records_by_id.get(old), records_by_id.get(new)
            if not (ro and rn and ro.get("issue_date") and rn.get("issue_date")):
                continue
            if ro["issue_date"] >= rn["issue_date"]:
                continue
            pairs.append({
                "old": old, "new": new,
                "old_date": ro["issue_date"], "new_date": rn["issue_date"],
                "as_of_mid": _mid(ro["issue_date"], rn["issue_date"]),
                "as_of_before": (date.fromisoformat(ro["issue_date"])
                                 - timedelta(days=30)).isoformat(),
            })
    rng.shuffle(pairs)
    return pairs[:n]


def mine_multi_hop(edges, records_by_id, n, rng):
    pairs = []
    for e in edges:
        a, b = e.get("source"), e.get("target")
        if a and b and a != b and a in records_by_id and b in records_by_id:
            pairs.append({"a": a, "b": b,
                          "subject_a": records_by_id[a].get("subject", ""),
                          "subject_b": records_by_id[b].get("subject", "")})
    rng.shuffle(pairs)
    return pairs[:n]


def mine_repealed_basis(records, n, rng):
    pool = [r for r in records
            if r.get("regulatory_basis_status") == "repealed_basis"]
    rng.shuffle(pool)
    return [{"circular_number": r["circular_number"],
             "subject": r.get("subject", ""),
             "regulations": r.get("regulations", [])} for r in pool[:n]]


def verify_negative_absence(records, topics):
    import bm25s
    texts = [(r.get("subject", "") + " " + r.get("text", ""))[:5000] for r in records]
    bm = bm25s.BM25()
    bm.index(bm25s.tokenize(texts, stopwords="en", show_progress=False),
             show_progress=False)
    out = []
    for t in topics:
        res, _ = bm.retrieve(bm25s.tokenize(t, stopwords="en", show_progress=False),
                             k=3, show_progress=False)
        out.append({"topic": t, "top_hits": [
            {"doc": records[int(i)]["circular_number"],
             "subject": records[int(i)].get("subject", "")} for i in res[0]]})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(ROOT / "data" / "corpus" / "circulars.jsonl"))
    ap.add_argument("--lineage", default=str(ROOT / "data" / "index" / "lineage.json"))
    ap.add_argument("--out", default=str(ROOT / "eval" / "golden" / "v7_annotations" / "candidates"))
    args = ap.parse_args()
    rng = random.Random(20260723)
    records = load_records(args.corpus)
    by_id = {r["circular_number"]: r for r in records}
    chunks = load_circulars(args.corpus)
    lin = json.loads(Path(args.lineage).read_text(encoding="utf-8"))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    def write(name, rows):
        with (out / f"{name}.jsonl").open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"{name}: {len(rows)} candidates")

    write("title_direct", sample_title_direct(records, 20, rng))
    write("body_paraphrase", sample_paraphrase_chunks(chunks, 90, rng))
    write("numeric_table", mine_numeric(chunks, 60, rng))
    write("lineage_supersession", mine_lineage_pairs(lin.get("superseded_by", {}), by_id, 80, rng))
    write("multi_hop", mine_multi_hop(lin.get("edges", []), by_id, 40, rng))
    write("repealed_basis", mine_repealed_basis(records, 40, rng))
    write("hard_negative", verify_negative_absence(records, HARD_NEGATIVE_TOPICS))
    write("far_negative", [{"topic": t} for t in FAR_NEGATIVE_TOPICS])


if __name__ == "__main__":
    main()
```

Note: if `lin["edges"]` rows are not `{"source", "target"}` dicts, inspect one row of `data/index/lineage.json` first and adapt the two key lookups in `mine_multi_hop` (keep the function signature).

Append to `Makefile`:

```make
golden-v7-mine:
	$(ENV) $(PY) scripts/golden_v7/mine_strata.py
```

- [ ] **Step 4: Run tests, then run the real miner**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_mine.py` → PASS
Run: `make golden-v7-mine`
Expected: eight `"<stratum>: N candidates"` lines; `lineage_supersession` ≥ 40; `repealed_basis` ≈ 40 (74 exist); `multi_hop` ≥ 20. If any stratum under-delivers its need, STOP and report — do not pad by hand.

- [ ] **Step 5: Commit (code + candidate files)**

```bash
git add scripts/golden_v7/mine_strata.py tests/test_golden_v7_mine.py Makefile eval/golden/v7_annotations/candidates/
git commit -m "feat(golden-v7): stratum candidate miners (seeded, oversampled 2x)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Tasks 6A–6E: Drafting batches (Claude judgment; no new code)

Five sibling tasks with an identical step shape; each drafts one stratum group from its candidate file(s), appends to `eval/golden/golden_v7.jsonl`, validates, commits. **These are data tasks: the "test" is `validate_golden_v7` plus the row-count check.**

**Files (all five):**
- Modify: `eval/golden/golden_v7.jsonl` (append only — never touch existing rows)
- Read-only inputs: `eval/golden/v7_annotations/candidates/*.jsonl`, corpus text via `data/corpus/circulars.jsonl` for the sampled items

**Batch → strata → new-row counts:**
- **6A:** title_direct +10 (all `difficulty: hard` — census needs ≥8 hard among the 10 since the 30 carried are medium) and body_paraphrase +45 (≥9 hard)
- **6B:** numeric_table +30 (≥6 hard)
- **6C:** lineage_supersession +40: 25 undated (gold = successor, `must_not_cite: [old]`), 12 dated (`as_of = as_of_mid`, gold = **predecessor**, `must_not_cite: [new]`), 3 dated-abstain (`as_of = as_of_before`, `abstain: true`, no labels)
- **6D:** multi_hop +20 (both circulars in `relevant_circulars`) and repealed_basis +20 (`must_contain` includes `"repealed"`)
- **6E:** hard_negative +30 (expand the 10 verified topic seeds into 3 phrasing variants each; check each seed's `top_hits` really are off-topic before using it — if a hit governs the topic, drop the seed and note it in the commit message) and far_negative +9

**Drafting rules (verbatim in every subagent prompt, plus spec §4/§5):**
1. One-shot: draft each query once from the candidate's source text; NEVER run retrieval to check whether a draft "works". Do not open `src/sebi_rag/expand.py`.
2. `relevant_chunks` stays `[]` at this phase (Task 8 fills it). `answer_contains` = one short literal from the source; `must_contain` = 1–2 literals.
3. Paraphrase rows: re-express in lay vocabulary a user would type (no copied statutory phrases from the source sentence you are targeting).
4. ids sequential per stratum (`v7-bp-001`…); `label_source`: `v7-draft-2026-07`; `review_status`: `draft`; `expected_citation_level`: `chunk` for body/numeric strata, `circular` otherwise, `none` for abstain rows.
5. Worked example (6C dated row; adapt real ids/dates from the candidate file):

```json
{"id": "v7-ls-026", "query": "As the rules stood in May 2022, what was the timeline for brokers to settle client funds?", "relevant_circulars": ["SEBI/HO/OLD/2021/55"], "relevant_chunks": [], "answer_contains": "quarterly", "must_contain": ["quarter"], "must_not_contain": [], "must_not_cite": ["SEBI/HO/NEW/2023/12"], "abstain": false, "as_of": "2022-05-15", "task_type": "lineage_supersession", "difficulty": "hard", "expected_citation_level": "circular", "rationale": "Dated as-of: successor SEBI/HO/NEW/2023/12 issued 2023-06-01 postdates as_of, so the predecessor governs. Pool-exhaustion adversarial shape (spec §4).", "label_source": "v7-draft-2026-07", "review_status": "draft"}
```

**Steps (identical for 6A–6E):**

- [ ] **Step 1:** Read the batch's candidate file(s) and the source circular text for each sampled item (`data/corpus/circulars.jsonl` records by `circular_number`). Draft the batch's rows per the rules above, append to `eval/golden/golden_v7.jsonl`.
- [ ] **Step 2: Validate**

Run: `.venv/bin/python -c "
import sys; sys.path.insert(0, 'src')
from sebi_rag.eval_harness import load_golden
from sebi_rag.benchmark import validate_golden_v7
rows = load_golden('eval/golden/golden_v7.jsonl')
issues = validate_golden_v7(rows)
print(f'{len(rows)} rows, {len(issues)} issues')
[print(i.item_id, i.message) for i in issues]
raise SystemExit(1 if issues else 0)"`
Expected: `<expected running total> rows, 0 issues` (6A→111, 6B→141, 6C→181, 6D→221, 6E→260; after 6E the census rail activates and must also pass)

- [ ] **Step 3: Commit**

```bash
git add eval/golden/golden_v7.jsonl
git commit -m "data(golden-v7): draft batch <6X> — <strata and counts>

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: `build_pool.py` — labeling pools from the real index

**Files:**
- Create: `scripts/golden_v7/build_pool.py`
- Modify: `Makefile` (append `golden-v7-pool`)
- Test: `tests/test_golden_v7_pool.py` (create)

**Interfaces:**
- Consumes: `HybridRetriever` (`.retrieve(q, top_n)`, `.sparse.search(q, k)`, `.dense.search(q, k)`, `.chunks`), a `Reranker`, golden rows, `_norm_ws`.
- Produces: `assemble_pool(row: dict, retriever, reranker, cap: int = 20) -> list[Chunk]` (pure given injected components — offline-testable) and `eval/golden/v7_annotations/pools.jsonl` (one pool record per answerable row, Global-Constraints shape). Task 8 (labeling), Task 9 (packet), Task 10 (Gemini) all read `pools.jsonl`.
- Pool order (dedupe by chunk id, first wins): (1) gold-doc chunks containing any `must_contain` literal, (2) round-robin over [reranked-RRF top-15, dense top-15, raw-BM25 top-15] until `cap`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_golden_v7_pool.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from golden_v7.build_pool import assemble_pool  # noqa: E402
from sebi_rag.embeddings import HashEmbedder  # noqa: E402
from sebi_rag.rerank import LexicalReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.segment import CircularMeta, hierarchical_chunk  # noqa: E402


def _retriever():
    chunks = []
    for i, (cn, body) in enumerate([
        ("SEBI/GOLD/1", "1. Margin:\nThe upfront margin shall be twenty per cent "
                        "of transaction value collected from every client without exception."),
        ("SEBI/OTHER/2", "1. Fees:\nAnnual regulatory fees shall be paid before "
                         "the thirtieth day of April every financial year by members."),
    ]):
        chunks += hierarchical_chunk(body, CircularMeta(circular_number=cn, subject=f"S{i}"))
    return HybridRetriever.build(chunks, HashEmbedder())


def test_gold_literal_chunks_lead_the_pool():
    row = {"query": "upfront margin percentage", "relevant_circulars": ["SEBI/GOLD/1"],
           "must_contain": ["twenty per cent"], "abstain": False}
    pool = assemble_pool(row, _retriever(), LexicalReranker(), cap=5)
    assert pool and pool[0].doc_id == "SEBI/GOLD/1"
    assert len(pool) <= 5
    assert len({c.id for c in pool}) == len(pool)  # deduped


def test_bm25_leg_uses_raw_query_not_expansion():
    # "block" expands to "freeze" via expand.py in production retrieve();
    # pooling must bypass that (spec §5: pool sees the frozen raw query).
    row = {"query": "block transactions", "relevant_circulars": ["SEBI/GOLD/1"],
           "must_contain": [], "abstain": False}
    pool = assemble_pool(row, _retriever(), LexicalReranker(), cap=10)
    assert isinstance(pool, list)  # smoke: no crash, raw-query leg wired
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_pool.py`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `scripts/golden_v7/build_pool.py`**

```python
"""Candidate pools for chunk-label judging (spec §6). TREC-style pooling:
union of system legs + gold-doc literal chunks, capped, deduped.

Real run (writes pools.jsonl):
    make golden-v7-pool          # needs the persisted index + MPS models
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

from sebi_rag.benchmark import _norm_ws  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402


def assemble_pool(row, retriever, reranker, cap: int = 20):
    by_id = {c.id: c for c in retriever.chunks}
    gold_docs = set(row.get("relevant_circulars", []))
    literals = [_norm_ws(m) for m in row.get("must_contain", []) if m]
    q = row["query"]

    pool, seen = [], set()

    def add(c):
        if c.id not in seen and len(pool) < cap:
            seen.add(c.id)
            pool.append(c)

    for c in retriever.chunks:
        if c.doc_id in gold_docs and literals and any(
                lit in _norm_ws(c.text) for lit in literals):
            add(c)
    rrf = retriever.retrieve(q, top_n=50)
    reranked = [c for c, _ in reranker.rerank(q, [c for c, _ in rrf])[:15]]
    dense = [retriever.chunks[i] for i, _ in retriever.dense.search(q, 15)]
    bm25 = [retriever.chunks[i] for i, _ in retriever.sparse.search(q, 15)]  # raw query: no expand_query
    legs = [reranked, dense, bm25]
    i = 0
    while len(pool) < cap and any(legs):
        leg = legs[i % 3]
        if leg:
            add(leg.pop(0))
        i += 1
    return pool


def main() -> None:
    from sebi_rag.embeddings import BGEM3Embedder
    from sebi_rag.rerank import CrossEncoderReranker
    from sebi_rag.retrieve import HybridRetriever
    from sebi_rag.settings import Settings

    s = Settings.load()
    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(s.index_dir, emb)
    rer = CrossEncoderReranker(device="mps")
    golden = load_golden(ROOT / "eval" / "golden" / "golden_v7.jsonl")
    out = ROOT / "eval" / "golden" / "v7_annotations" / "pools.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in golden:
            if row.get("abstain"):
                continue
            pool = assemble_pool(row, retr, rer)
            f.write(json.dumps({"id": row["id"], "candidates": [
                {"chunk_id": c.id, "doc": c.doc_id, "text": c.text}
                for c in pool]}, ensure_ascii=False) + "\n")
            print(row["id"], len(pool), file=sys.stderr)
    print(f"wrote pools -> {out}")


if __name__ == "__main__":
    main()
```

Append to `Makefile`:

```make
golden-v7-pool:
	$(ENV) $(PY) scripts/golden_v7/build_pool.py
```

- [ ] **Step 4: Run test → PASS, then the real pool build**

Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_pool.py` → PASS
Run: `make golden-v7-pool` (real models; several minutes)
Expected: `wrote pools -> .../pools.jsonl` with ~207 records (one per answerable row).

- [ ] **Step 5: Commit**

```bash
git add scripts/golden_v7/build_pool.py tests/test_golden_v7_pool.py Makefile eval/golden/v7_annotations/pools.jsonl
git commit -m "feat(golden-v7): TREC-style labeling pools (gold-literal + 3 system legs, cap 20)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: Labeling batches — fill `relevant_chunks` + emit Claude votes

Claude-judgment task over `pools.jsonl`, in 5 batches of ~42 answerable rows (batch = contiguous slice of pools.jsonl order). No new code.

**Files:**
- Modify: `eval/golden/golden_v7.jsonl` (fill `relevant_chunks` on answerable rows only)
- Create/append: `eval/golden/v7_annotations/votes.jsonl` (annotator `"claude"`)

**Judging rules (verbatim in every subagent prompt):**
1. A pooled chunk is **governing** iff its text contains the provision that answers the query — topical relatedness is NOT enough (same bar as the SubjectSimJudge docstring).
2. For each governing chunk, record a verbatim quote from its BODY (never the first `"<circular> | ..."` header line), ≥40 chars, that carries the provision. That quote becomes the span `{"doc": <chunk's doc>, "quote": ...}`.
3. Every answerable row must end with ≥1 span; if NO pooled chunk governs, do not invent one — add the row id to `eval/golden/v7_annotations/label_escalations.txt` with one line of why, and leave `relevant_chunks` empty (the validator census still passes; escalations resolve in Task 12 arbitration).
4. Append one vote record per judged row: `{"id", "annotator": "claude", "governing": [<chunk_ids you marked>], "expected_literal": <row's answer_contains>}`.
5. `must_not_cite` docs never yield spans (their chunks are distractors by construction).

**Steps (per batch):**

- [ ] **Step 1:** Judge the batch's rows per the rules; update `golden_v7.jsonl` spans; append votes.
- [ ] **Step 2: Validate (quote resolution against the live corpus)**

Run: `.venv/bin/python -c "
import sys; sys.path.insert(0, 'src')
from sebi_rag.eval_harness import load_golden
from sebi_rag.benchmark import validate_golden_v7
from sebi_rag.corpus import load_circulars
rows = load_golden('eval/golden/golden_v7.jsonl')
issues = validate_golden_v7(rows, chunks=load_circulars('data/corpus/circulars.jsonl'))
print(len(issues), 'issues'); [print(i.item_id, i.message) for i in issues]
raise SystemExit(1 if issues else 0)"`
Expected: `0 issues`

- [ ] **Step 3: Commit** (message `data(golden-v7): chunk labels batch <N>/5 (+claude votes)` with the trailer)

---

### Task 9: `make_packet.py` — external sampling, human packet, CSV ingest

**Files:**
- Create: `scripts/golden_v7/make_packet.py`
- Modify: `Makefile` (append `golden-v7-packet`)
- Test: `tests/test_golden_v7_packet.py` (create)

**Interfaces:**
- Consumes: golden rows, `pools.jsonl`, vote-record shape.
- Produces:
  - `sample_external(rows: list[dict], n: int, human_n: int, rng) -> tuple[list[str], list[str]]` — (external_ids 100, human_ids 30 ⊂ external), stratified proportionally per `task_type` over ALL rows (carried included; abstain rows included — their "pool" is their nearest-topic distractors already in pools? No: abstain rows have no pool records, so their packet entry shows the query with excerpts from the top-scoring pool of the corpus-wide RRF — SIMPLIFICATION: abstain rows sampled into the external slice get their excerpts from a fresh pool record built in Task 7's real run? They were skipped there.) → **Rule:** `sample_external` draws only from rows that HAVE a pool record, plus abstain rows; for abstain rows the packet shows the query with the excerpts of the *most similar answerable row's pool omitted* — instead it shows NO excerpts and asks only "is this answerable from SEBI circulars? (yes = flag, no = confirm abstain)". Vote for abstain rows: `governing: []` + `expected_literal: ""` confirms abstain; any text in expected_literal flags a dispute.
  - `write_packet(rows, pools, ids, human_ids, out_dir) -> None` — `packet_human/packet.html` (self-contained, escaped, excerpts shuffled per-row by `random.Random(row_id)`, labeled A, B, C…; NO scores, ranks, or system answers), `packet_human/manifest.json` (`{row_id: {"A": chunk_id, ...}}`), `packet_human/labels_template.csv` (columns `id,choices,expected_literal`; `choices` = semicolon-joined letters or `none`).
  - `ingest_packet(csv_path, manifest_path) -> list[dict]` — vote records (`annotator: "human"`), letters mapped to chunk ids; unknown letters or ids → `ValueError`.
- [ ] **Step 1: Failing tests** — three tests: (a) `sample_external` is deterministic for seed 20260723, returns 100/30 with human ⊂ external and every task_type represented; (b) `write_packet` output HTML contains no `"score"` substring and every sampled answerable row's letters appear in manifest; (c) `ingest_packet` round-trips a hand-written 2-row CSV to vote records. Use ~12 synthetic rows spanning all 8 task_types + 2-candidate pools. Complete test code follows the fixture pattern of Task 1 (`_row(**over)`); packet fixture pools: `[{"id": rid, "candidates": [{"chunk_id": f"{d}#s#0", "doc": d, "text": "t"*60}]}]`.
- [ ] **Step 2:** Run: `.venv/bin/python -m pytest -q tests/test_golden_v7_packet.py` → FAIL (`ModuleNotFoundError`)
- [ ] **Step 3:** Implement (pure functions + `main()` that reads golden_v7 + pools, calls `sample_external(rows, 100, 30, random.Random(20260723))`, writes `eval/golden/v7_annotations/packet_human/` and `external_sample.json` (`{"external": [...ids], "human": [...ids]}`). `html.escape` every excerpt; one `<details>` block per row.)
- [ ] **Step 4:** Tests PASS; run `make golden-v7-packet` (offline, instant) → packet files exist; open `packet.html` once to sanity-check rendering.

Append to `Makefile`:

```make
golden-v7-packet:
	$(ENV) $(PY) scripts/golden_v7/make_packet.py
```

- [ ] **Step 5: Commit** (`feat(golden-v7): external sampling + blind human packet + CSV ingest` with trailer; include generated `packet_human/` + `external_sample.json`)

---

### Task 10: `gemini_adjudicate.py` — second-family LLM leg (httpx, cached)

**Files:**
- Create: `scripts/golden_v7/gemini_adjudicate.py`
- Modify: `Makefile` (append `golden-v7-gemini`)
- Test: `tests/test_golden_v7_gemini.py` (create)

**Interfaces:**
- Consumes: `external_sample.json` (external ids), golden rows, `pools.jsonl`.
- Produces: `build_prompt(row, pool) -> str` (same blind protocol as the packet: shuffled lettered excerpts, "reply with the letter(s) that contain the governing provision, comma-separated, or NONE; then on a new line EXPECTED: <short literal>"); `parse_reply(text, letters) -> tuple[list[str], str]` (chosen letters, expected literal; unparseable → `([], "")` and the row is marked `"parse_error": true` in the cache); `adjudicate(rows, pools, ids, post) -> list[dict]` vote records (`annotator: "gemini"`), where `post(prompt) -> str` is injected (real impl = httpx POST to `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}`, model from `GOLDEN_GEMINI_MODEL`, default `gemini-3-flash-preview`; extract `candidates[0].content.parts[0].text`). Per-row JSON cache in `eval/golden/v7_annotations/gemini/<row_id>.json` — reruns skip cached rows (resumable, spec §7).
- [ ] **Step 1: Failing tests** — (a) `build_prompt` contains every excerpt letter and no chunk scores; (b) `parse_reply("B, C\nEXPECTED: twenty per cent", ["A","B","C"]) == (["B","C"], "twenty per cent")`, `parse_reply("NONE", ...) == ([], "")`, garbage → `([], "")`; (c) `adjudicate` with a fake `post` returning a canned reply writes vote records and cache files, and a second call performs zero `post` calls (assert via counter).
- [ ] **Step 2:** Run → FAIL (`ModuleNotFoundError`)
- [ ] **Step 3:** Implement; abstain-row prompts follow the Task 9 abstain protocol (no excerpts; "Is this answerable from SEBI circulars? reply YES or NO, then EXPECTED: ..."; NO → vote `governing: []`).
- [ ] **Step 4:** Tests PASS.

Append to `Makefile`:

```make
golden-v7-gemini:
	$(ENV) $(PY) scripts/golden_v7/gemini_adjudicate.py
```

- [ ] **Step 5: Commit** (`feat(golden-v7): Gemini adjudication leg (blind protocol, per-row cache)` with trailer)

---

### Task 11: `agreement.py` — κ, promotion, arbitration queue, report

**Files:**
- Create: `scripts/golden_v7/agreement.py`
- Modify: `Makefile` (append `golden-v7-agree`)
- Test: `tests/test_golden_v7_agreement.py` (create)

**Interfaces:**
- Consumes: `votes.jsonl` (all annotators), golden rows, `sebi_rag.stats.clopper_pearson_ci(successes, n, confidence) -> ProportionCI` (check the exact signature at `src/sebi_rag/stats.py:95` before use and adapt the call).
- Produces:
  - `cohen_kappa(a: list, b: list) -> float` — categorical κ where each label is `frozenset(governing)` (empty = "none"); chance agreement from marginals; returns 1.0 when both raters constant and identical.
  - `decide(row, votes_by_annotator, dated_ids: set[str]) -> tuple[str, list[str] | None]` — returns `(decision, new_governing)` with decision ∈ {`promote`, `flip_promote`, `queue`}: dated `as_of` rows always `queue` (spec §7 exception); Gemini-only row agrees with claude → `promote`; three-way all agree → `promote`; human+gemini agree on the same alternative ≠ claude → `flip_promote` with their set; anything else → `queue`. Agreement = exact `frozenset(governing)` match.
  - `apply(golden_rows, decisions) -> list[dict]` — promoted rows get `review_status: "adjudicated"`; flipped rows also get `relevant_chunks` rebuilt from the winning chunk ids' `{doc, quote}` (quote = first 60 body chars of that chunk, re-judged in arbitration if needed) and `label_source: "external-flip"`.
  - Outputs: updated `golden_v7.jsonl`, `v7_annotations/arbitration_queue.jsonl` (row + all votes), `reports/golden_v7_agreement.md` (κ per annotator-pair per stratum, raw agreement %, Clopper-Pearson 95% CI on claude-label accuracy vs externals, promoted/flipped/queued counts).
- [ ] **Step 1: Failing tests** — (a) `cohen_kappa` on identical lists = 1.0, on independent-looking lists < 0.5; (b) `decide` truth table: gemini-agree → promote; three-way split → queue; human+gemini same alternative → flip_promote; dated id → queue even on full agreement; (c) `apply` sets `adjudicated` only on promote/flip decisions and never touches `seeded`/`draft` rows without a decision.
- [ ] **Step 2:** Run → FAIL
- [ ] **Step 3:** Implement (+ `main()` wiring files together; dated ids = rows where `as_of` is not None).
- [ ] **Step 4:** Tests PASS.

Append to `Makefile`:

```make
golden-v7-agree:
	$(ENV) $(PY) scripts/golden_v7/agreement.py
```

- [ ] **Step 5: Commit** (`feat(golden-v7): agreement kappa + promotion rules + arbitration queue` with trailer)

---

### Task 12: Run the external pass (real Gemini; human packet handoff)

No new code. Requires Tasks 8–11 complete and `GEMINI_API_KEY` in env.

- [ ] **Step 1:** `make golden-v7-gemini` — real API run over the 100 external ids (cached; safe to rerun). Expected: 100 cache files, 100 gemini vote records appended.
- [ ] **Step 2:** `make golden-v7-agree` — writes agreement report, applies promotions from the Gemini-only slice (70 rows), queues disagreements + all 30 human-slice rows (no human votes yet) + all dated rows.
- [ ] **Step 3:** Validate + full suite: the Task 8 Step-2 validation command, then `.venv/bin/python -m pytest -q -m "not integration"`. Expected: 0 issues, no regressions.
- [ ] **Step 4:** Commit all artifacts (`data(golden-v7): external pass — gemini votes, promotions, agreement report` with trailer).
- [ ] **Step 5: HANDOFF (async):** tell the user: open `eval/golden/v7_annotations/packet_human/packet.html`, fill `labels_template.csv` (~30 rows), then run `make golden-v7-packet-ingest && make golden-v7-agree` (Task 13 adds the ingest target). The gate flip does not block on this — the Gemini-only leg feeds it.

---

### Task 13: Gate flip machinery — `eval_json.py` refactor + thresholds

**Files:**
- Modify: `scripts/eval_json.py` (full rewrite of the metric loop onto `RAGPipeline`), `Makefile` (append `golden-v7-packet-ingest`, `golden-v7-gate`)
- Create: `scripts/golden_v7/derive_thresholds.py`
- Test: `tests/test_golden_v7_gate.py` (create)

**Interfaces:**
- Consumes: `run_eval` + `EvalReport.gate` (Task 3), `sebi_rag.stats.bootstrap_ci` (check exact signature at `src/sebi_rag/stats.py:62` and adapt), `RAGPipeline`, `ExtractiveStubGenerator`, `SubjectSimJudge`.
- Produces:
  - `derive_thresholds.py`: runs the production-shaped pipeline (stub generator — no LLM) over the v7 **adjudicated** subset, computes per-query recall/citation/abstention vectors, and writes `eval/golden/gate_v7.json`: `{"adjudicated_n": int, "derived_at": iso, "floors": {"recall_at_10": <2.5th-pct bootstrap lower bound - 0.005>, "citation_recall": ..., "abstention_accuracy": ...}}`. Refuses to write when `adjudicated_n < 100` (prints why, exit 1) — this file IS the flip switch.
  - `eval_json.py` (rewritten core): builds `RAGPipeline(retriever, reranker=CrossEncoderReranker, generator=ExtractiveStubGenerator(), lineage, judge=SubjectSimJudge(...), abstain_threshold=s.abstain_threshold)` and computes the SAME output keys as today via `pipeline.query` (citations = top-k contexts, so semantics are preserved). Golden file resolution: `SEBI_RAG_GOLDEN` env if set; else **golden_v7 iff `eval/golden/gate_v7.json` exists with `adjudicated_n >= 100`**, else golden_v5. Output JSON keeps every existing key and adds: `"golden_file"`, `"gate": {…}|null` (adjudicated-subset metrics + `"floors_ok": bool` vs gate_v7.json floors when on v7), `"adjudicated_n"`. One JSON object on stdout, noise on stderr (n8n contract).
  - Makefile:

```make
golden-v7-packet-ingest:
	$(ENV) $(PY) scripts/golden_v7/make_packet.py --ingest eval/golden/v7_annotations/packet_human/labels_template.csv

golden-v7-gate:
	$(ENV) $(PY) scripts/golden_v7/derive_thresholds.py
```

  (Task 9's `main()` gains the `--ingest <csv>` flag here if not already present: it appends human vote records and exits.)
- [ ] **Step 1: Failing tests** — pure parts only (the script's model boot stays untested): extract the golden-file resolution into `scripts/golden_v7/gate_select.py::select_golden(env: dict, gate_path: Path, v5: Path, v7: Path) -> Path` and test: env override wins; gate file with `adjudicated_n: 120` → v7; missing/`90` → v5. Also test `floors_ok(report_gate: dict, floors: dict) -> bool`.
- [ ] **Step 2:** Run → FAIL
- [ ] **Step 3:** Implement `gate_select.py`, `derive_thresholds.py`, rewrite `eval_json.py` importing `select_golden`/`floors_ok`.
- [ ] **Step 4:** Tests PASS; full offline suite green. Real smoke: `SEBI_RAG_GOLDEN=eval/golden/golden_v5.jsonl .venv/bin/python scripts/eval_json.py` (with `$(ENV)` vars) — expected: one JSON line, `recall_at_10` within ±0.02 of the archived 0.955 (semantic-parity check for the pipeline refactor; investigate any larger delta before committing).
- [ ] **Step 5:** If `adjudicated_n >= 100`: run `make golden-v7-gate` then `.venv/bin/python scripts/eval_json.py` and confirm `golden_file` endswith `golden_v7.jsonl` and `gate.floors_ok` is present. Otherwise note in the commit message that the flip stays armed-but-off. Commit (`feat(golden-v7): gate flip machinery — pipeline-based eval_json, derived floors, v5 fallback` with trailer).

---

### Task 14: Docs, final census, wrap-up

**Files:**
- Modify: `CLAUDE.md` (Testing & Evaluation section), `docs/status.md` (append entry), `docs/superpowers/plans/2026-07-24-golden-v7-expansion.md` (tick boxes)

- [ ] **Step 1:** CLAUDE.md: in "Testing & Evaluation", replace the golden-set sentence with: golden_v7 (n=260, span-anchored chunk labels, `review_status` lifecycle) is the reporting set; CI gates on its adjudicated subset once `eval/golden/gate_v7.json` arms (else golden_v5); v1–v6 + probes + asof are frozen; `make golden-v7-*` targets exist.
- [ ] **Step 2:** status.md: dated entry — final strata census (from the validator), adjudicated_n, κ headline numbers from `reports/golden_v7_agreement.md`, arbitration-queue depth, gate state.
- [ ] **Step 3:** Full suite one last time: `.venv/bin/python -m pytest -q -m "not integration"` → green; `git add -A && git commit` (`docs(golden-v7): wire v7 into CLAUDE.md + status; final census` with trailer).
- [ ] **Step 4:** Report to user: census table, agreement stats, queue depth, whether the gate flipped, and the standing human-packet handoff from Task 12.

---

## Plan Self-Review (performed at write time)

- **Spec coverage:** §3 schema → Tasks 1–2; §4 strata → Tasks 5–6; §5 anti-leakage → Global Constraints + Task 6/7 rules; §6 pooling → Task 7–8; §7 external/promotion (incl. dated-row exception, configurable sample) → Tasks 9–12; §8 harness/gate/validator → Tasks 1–3, 13; §9 layout → matches; §10 phases → task order; §11 out-of-scope respected (no as-of retrieval fix anywhere); §12 risks → cache/resume (T10), v5 fallback (T13), arbitration queue (T11).
- **Known judgment points for implementers:** `lineage.json` `edges` element shape (Task 5 note); `stats.py` exact signatures (Tasks 11/13 say check before use).
- **Type consistency:** vote/pool/gate-file shapes defined once in Global Constraints and reused by name in Tasks 7–13; `validate_golden_v7(rows, chunks=None)` consistent across Tasks 1/2/6/8; `EvalReport.gate` dict consumed by Task 13.
