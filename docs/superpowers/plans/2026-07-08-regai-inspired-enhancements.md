# regai-Inspired Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adopt the three ideas from the regai prototype (github.com/balabommablock-cpu/regai) that this codebase lacks — table-aware chunking, successor-expansion retrieval, and per-chunk cross-reference metadata — without changing the local-first stack. **Addendum (Part B, Tasks 7–11):** harden `ingest_pdf.py` reference-number parsing based on a deep analysis of the recent inconsistency fixes (regression suite, strategy refactor, canonical normalization, corpus validation, missing-PDF acquisition).

**Architecture:** All three features slot into the existing pipeline stages. Tables are extracted at PDF ingestion (`ingest_pdf.py`, pdfplumber already in use), stored on the corpus record, and chunked with header-paired rows at load time (`segment.py` / `corpus.py`). Successor expansion is a pure function in `lineage.py` called by `RAGPipeline.query()` between retrieval and reranking. Cross-references are extracted per chunk during segmentation using the existing `REF_RE` and used to guarantee exact-reference candidates survive into the rerank pool.

**Tech Stack:** Python 3.12–3.13, pdfplumber, FAISS + bm25s (unchanged), pytest. No new dependencies.

## Background (comparison findings)

regai is a work-in-progress prototype (chunker + keyword evaluator only; its demo imports modules that don't exist). Its stack (pgvector/Supabase, `text-embedding-3-large`, Claude API) was **rejected** — it contradicts this project's local-first Apple Silicon design. Three of its design ideas are worth adopting:

1. **Table-aware chunking** — regai formats each table row paired with its column headers (`Category: Equity | Min Equity %: 80`) so numeric thresholds keep their meaning. Our `hierarchical_chunk` flattens tables into plain text.
2. **Amendment-aware retrieval expansion** — regai pulls chunks from the amending circular when a retrieved chunk is from an amended one. We demote superseded chunks (`demote_superseded`) but never fetch the in-force successor's content.
3. **Per-chunk cross-references** — regai stores inline circular references on each chunk. We extract references only at document level for lineage.

## Global Constraints

- Local-first: no network calls, no new services, no cloud dependencies.
- Python 3.12–3.13; run tests with `uv run pytest` (offline suite: `make test`).
- Chunk IDs must stay stable and deterministic (they are citation keys).
- `Chunk` must remain round-trippable through `retrieve.py` persistence (`Chunk(**json.loads(line))`).
- Corpus JSONL (`data/corpus/circulars.jsonl`) changes must be backward compatible: readers must tolerate records without the new `tables` field.
- All existing tests must keep passing after every task.
- Commit after every green test cycle.

---

### Task 1: Table extraction at PDF ingestion

**Files:**
- Modify: `src/sebi_rag/ingest_pdf.py` (add `extract_tables()` after `extract_text()`, ~line 69)
- Test: `tests/test_ingest_tables.py` (create)

**Interfaces:**
- Consumes: `pdfplumber` (already imported in `ingest_pdf.py`).
- Produces: `extract_tables(pdf_path: str | Path) -> list[dict]` where each dict is `{"page": int, "headers": list[str], "rows": list[list[str]]}`. Task 2 stores this under the corpus record key `"tables"`; Task 3 chunks it.

- [ ] **Step 1: Write the failing test**

pdfplumber can't easily fabricate a table-bearing PDF in a unit test, so split the logic: a pure normalizer `_normalize_table(raw: list[list[str | None]]) -> dict | None` that `extract_tables` applies to each `page.extract_tables()` result. Test the normalizer.

```python
# tests/test_ingest_tables.py
from sebi_rag.ingest_pdf import _normalize_table


def test_normalize_table_strips_cells_and_splits_headers():
    raw = [
        ["Category ", None, "Min Equity %"],
        ["Large Cap", "Top 100", " 80 "],
        [None, None, None],          # fully empty row dropped
        ["Mid Cap", "101-250", "65"],
    ]
    t = _normalize_table(raw)
    assert t["headers"] == ["Category", "", "Min Equity %"]
    assert t["rows"] == [["Large Cap", "Top 100", "80"], ["Mid Cap", "101-250", "65"]]


def test_normalize_table_rejects_degenerate_tables():
    # fewer than 2 rows or 2 columns is not a table worth indexing
    assert _normalize_table([["only header", "row"]]) is None
    assert _normalize_table([["a"], ["b"], ["c"]]) is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_ingest_tables.py -v`
Expected: FAIL with `ImportError: cannot import name '_normalize_table'`

- [ ] **Step 3: Write minimal implementation**

Add to `src/sebi_rag/ingest_pdf.py` directly below `extract_text()`:

```python
def _normalize_table(raw: list[list[str | None]]) -> dict | None:
    """Clean a pdfplumber table: strip cells, drop empty rows, first row = headers.
    Returns None for degenerate tables (<2 data-bearing rows or <2 columns)."""
    rows = [[(c or "").strip() for c in row] for row in raw]
    rows = [r for r in rows if any(r)]
    if len(rows) < 2 or len(rows[0]) < 2:
        return None
    return {"headers": rows[0], "rows": rows[1:]}


def extract_tables(pdf_path: str | Path) -> list[dict]:
    """Extract tables from a circular PDF, one dict per table with page number.

    SEBI circulars carry critical numeric thresholds in tables; extracting
    them structurally (instead of relying on extract_text's flattened lines)
    lets segmentation keep each row paired with its column headers.
    """
    out: list[dict] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for pno, page in enumerate(pdf.pages, 1):
            for raw in page.extract_tables():
                t = _normalize_table(raw)
                if t:
                    out.append({"page": pno, **t})
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_ingest_tables.py -v`
Expected: 2 PASSED

- [ ] **Step 5: Run full suite, then commit**

Run: `make test`
Expected: all pass.

```bash
git add tests/test_ingest_tables.py src/sebi_rag/ingest_pdf.py
git commit -m "feat: extract structured tables from circular PDFs at ingestion"
```

---

### Task 2: Store tables on corpus records + backfill script

**Files:**
- Modify: `src/sebi_rag/ingest_pdf.py` — the `ingest()` function (line ~263) writes corpus records; add `"tables"` to each record.
- Create: `scripts/backfill_tables.py`
- Test: `tests/test_ingest_tables.py` (extend)

**Interfaces:**
- Consumes: `extract_tables(pdf_path)` from Task 1; `extract_text(pdf_path)`, `parse_meta(text) -> dict` (existing).
- Produces: corpus JSONL records gain optional key `"tables": list[{"page": int, "headers": list[str], "rows": list[list[str]]}]`. Task 3's `load_circulars` reads it via `r.get("tables", [])`.

- [ ] **Step 1: Read `ingest()` and locate where the record dict is assembled**

Open `src/sebi_rag/ingest_pdf.py:263` and find where the record written to `circulars.jsonl` is built from `parse_meta(text)`. The exact variable names may differ from this plan — adapt the next step to the real code, keeping the behavior exactly as specified.

- [ ] **Step 2: Add `tables` to the record**

In `ingest()`, after text extraction and `parse_meta`, add:

```python
record["tables"] = extract_tables(pdf_path)
```

(where `record` is the dict that gets `json.dumps`-ed into the corpus, and `pdf_path` the source PDF being ingested).

- [ ] **Step 3: Write the backfill script for existing corpus records**

Existing corpus records (600+) were ingested without tables. The backfill re-extracts tables from `data/raw/*.pdf`, matches each PDF to its corpus record by parsed `circular_number`, and updates records in place.

```python
# scripts/backfill_tables.py
"""Backfill 'tables' onto existing corpus records from data/raw PDFs.

Match key: circular_number parsed from the PDF (same parse_meta path used at
ingestion). Records whose PDF is missing keep tables=[] and are counted.
Idempotent: re-running produces the same corpus file.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sebi_rag.ingest_pdf import extract_tables, extract_text, parse_meta  # noqa: E402

CORPUS = Path("data/corpus/circulars.jsonl")
RAW = Path("data/raw")


def main() -> int:
    records = [json.loads(l) for l in CORPUS.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_number = {r["circular_number"]: r for r in records}
    matched = updated = 0
    for pdf in sorted(RAW.glob("*.pdf")):
        try:
            text = extract_text(pdf)
            number = parse_meta(text).get("circular_number")
        except Exception as e:  # unparseable PDFs are already tracked elsewhere
            print(f"skip {pdf.name}: {e}")
            continue
        rec = by_number.get(number)
        if rec is None:
            continue
        matched += 1
        tables = extract_tables(pdf)
        if rec.get("tables") != tables:
            rec["tables"] = tables
            updated += 1
    CORPUS.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )
    missing = len(records) - matched
    print(f"records={len(records)} matched={matched} updated={updated} no_pdf={missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the backfill and verify**

Run: `uv run python scripts/backfill_tables.py`
Expected: a summary line like `records=603 matched=<n> updated=<n> no_pdf=<n>`. Spot-check one record known to contain a table:

Run: `uv run python -c "import json; rs=[json.loads(l) for l in open('data/corpus/circulars.jsonl')]; ts=[r for r in rs if r.get('tables')]; print(len(ts), 'records with tables'); print(ts[0]['circular_number'], ts[0]['tables'][0]['headers'] if ts else '')"`
Expected: a nonzero count and plausible headers.

- [ ] **Step 5: Run full suite, then commit**

Run: `make test`
Expected: all pass.

```bash
git add src/sebi_rag/ingest_pdf.py scripts/backfill_tables.py
git commit -m "feat: persist extracted tables on corpus records with backfill script"
```

(Do **not** commit `data/corpus/circulars.jsonl` unless the repo already versions it — follow existing practice; check `git status` first.)

---

### Task 3: Table-aware chunking in segmentation

**Files:**
- Modify: `src/sebi_rag/segment.py` (add `format_table_rows()` and `table_chunks()` after `hierarchical_chunk`)
- Modify: `src/sebi_rag/corpus.py:27` (append table chunks in `load_circulars`)
- Test: `tests/test_segment_tables.py` (create)

**Interfaces:**
- Consumes: `Chunk`, `CircularMeta` (existing, `segment.py:13-31`); corpus record key `"tables"` from Task 2.
- Produces: `table_chunks(tables: list[dict], meta: CircularMeta, max_chars: int = 1200) -> list[Chunk]`. Chunk IDs: `{circular_number}#table{t_idx}#p{part}` (stable, citation-safe). Chunk meta carries `{"chunk_type": "table"}` in addition to `asdict(meta)`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_segment_tables.py
from sebi_rag.segment import CircularMeta, format_table_rows, table_chunks

META = CircularMeta(circular_number="SEBI/HO/IMD/DF3/CIR/P/2017/114", subject="Categorization of Mutual Fund Schemes")

TABLE = {
    "page": 2,
    "headers": ["Category", "Sub-Category", "Min Equity %"],
    "rows": [["Equity", "Large Cap", "80"], ["Equity", "Mid Cap", "65"]],
}


def test_format_table_rows_pairs_each_cell_with_header():
    lines = format_table_rows(TABLE["headers"], TABLE["rows"])
    assert lines[0] == "Category: Equity | Sub-Category: Large Cap | Min Equity %: 80"
    assert lines[1] == "Category: Equity | Sub-Category: Mid Cap | Min Equity %: 65"


def test_table_chunks_have_stable_ids_and_enriched_text():
    chunks = table_chunks([TABLE], META)
    assert len(chunks) == 1
    c = chunks[0]
    assert c.id == "SEBI/HO/IMD/DF3/CIR/P/2017/114#table0#p0"
    assert c.doc_id == META.circular_number
    # contextual enrichment mirrors hierarchical_chunk (F1, ADR-001)
    assert c.text.startswith("SEBI/HO/IMD/DF3/CIR/P/2017/114 | Categorization")
    assert "Min Equity %: 80" in c.text
    assert c.meta["chunk_type"] == "table"


def test_table_chunks_split_long_tables_at_row_boundaries():
    big = {"page": 1, "headers": ["H1", "H2"], "rows": [[f"row{i}", "x" * 100] for i in range(40)]}
    chunks = table_chunks([big], META, max_chars=600)
    assert len(chunks) > 1
    # every part repeats no partial rows: each line stays intact
    for c in chunks:
        body = c.text.split("\n", 1)[1]
        assert all(line.startswith("H1: row") for line in body.splitlines())


def test_empty_tables_yield_no_chunks():
    assert table_chunks([], META) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_segment_tables.py -v`
Expected: FAIL with `ImportError: cannot import name 'format_table_rows'`

- [ ] **Step 3: Write minimal implementation**

Add to `src/sebi_rag/segment.py` after `hierarchical_chunk`:

```python
def format_table_rows(headers: list[str], rows: list[list[str]]) -> list[str]:
    """One line per row, each cell paired with its column header.

    Naive chunking splits table rows from their headers, destroying the
    meaning of numeric thresholds; header-paired rows keep it (regai-inspired).
    """
    out: list[str] = []
    for row in rows:
        pairs = [f"{h}: {v}" for h, v in zip(headers, row) if h or v]
        if pairs:
            out.append(" | ".join(pairs))
    return out


def table_chunks(
    tables: list[dict],
    meta: CircularMeta,
    max_chars: int = 1200,
) -> list[Chunk]:
    """Chunk extracted tables; splits only at row boundaries.

    IDs are `{circular}#table{t_idx}#p{part}` — stable across re-ingestion as
    long as the PDF's table order is unchanged.
    """
    chunks: list[Chunk] = []
    header = " | ".join(
        p for p in (meta.circular_number, meta.subject.strip()[:120]) if p
    )
    for t_idx, t in enumerate(tables):
        lines = format_table_rows(t.get("headers", []), t.get("rows", []))
        part = 0
        buf: list[str] = []
        size = 0

        def flush() -> None:
            nonlocal part, buf, size
            if not buf:
                return
            body = "\n".join(buf)
            m = asdict(meta)
            m["chunk_type"] = "table"
            chunks.append(Chunk(
                id=f"{meta.circular_number}#table{t_idx}#p{part}",
                doc_id=meta.circular_number,
                section=f"{meta.circular_number}/table{t_idx}/p{part}",
                text=f"{header}\n{body}",
                meta=m,
            ))
            part += 1
            buf, size = [], 0

        for line in lines:
            if size + len(line) + 1 > max_chars and buf:
                flush()
            buf.append(line)
            size += len(line) + 1
        flush()
    return chunks
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_segment_tables.py -v`
Expected: 4 PASSED

- [ ] **Step 5: Wire into corpus loading**

In `src/sebi_rag/corpus.py`, change the import and the loop tail:

```python
from .segment import Chunk, CircularMeta, hierarchical_chunk, table_chunks
```

and replace line 27 (`chunks.extend(hierarchical_chunk(r["text"], meta))`) with:

```python
        chunks.extend(hierarchical_chunk(r["text"], meta))
        chunks.extend(table_chunks(r.get("tables", []), meta))
```

- [ ] **Step 6: Add a corpus-level test**

Append to `tests/test_segment_tables.py`:

```python
def test_load_circulars_emits_table_chunks(tmp_path):
    import json
    from sebi_rag.corpus import load_circulars

    rec = {
        "circular_number": "SEBI/HO/TEST/2024/001",
        "subject": "Test",
        "text": "1. Applicability\nThis applies to all schemes.",
        "tables": [TABLE],
    }
    p = tmp_path / "c.jsonl"
    p.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    chunks = load_circulars(p)
    kinds = {c.meta.get("chunk_type") for c in chunks}
    assert "table" in kinds
    assert any("Min Equity %: 80" in c.text for c in chunks)
```

Run: `uv run pytest tests/test_segment_tables.py -v`
Expected: 5 PASSED

- [ ] **Step 7: Run full suite, then commit**

Run: `make test`
Expected: all pass (existing corpus records without `tables` are unaffected).

```bash
git add tests/test_segment_tables.py src/sebi_rag/segment.py src/sebi_rag/corpus.py
git commit -m "feat: table-aware chunking with header-paired rows"
```

---

### Task 4: Successor-expansion retrieval

**Files:**
- Modify: `src/sebi_rag/lineage.py` (add `expand_successors()` after `demote_superseded`, ~line 150)
- Modify: `src/sebi_rag/pipeline.py:42-49` (`RAGPipeline.query`)
- Test: `tests/test_lineage_expand.py` (create)

**Interfaces:**
- Consumes: `Lineage.superseded_by` / `Lineage.amended_by` (dict[str, list[str]]), `Chunk` (has `.id`, `.doc_id`, `.text`), `HybridRetriever.chunks` (full chunk list, `pipeline.py` accesses `self.retriever.chunks`).
- Produces: `expand_successors(candidates: list[tuple[Chunk, float]], all_chunks: list[Chunk], lineage: Lineage, query: str, per_doc: int = 3) -> list[tuple[Chunk, float]]` — the input candidates plus up to `per_doc` chunks from each in-force successor of any superseded/amended candidate. Injected chunks get score `0.0` (the reranker rescores everything downstream, so the score is a placeholder). New `RAGPipeline` field `successor_expansion: int = 3` (0 disables).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_lineage_expand.py
from sebi_rag.lineage import Lineage, expand_successors
from sebi_rag.segment import Chunk


def _chunk(cid: str, doc: str, text: str) -> Chunk:
    return Chunk(id=cid, doc_id=doc, section=f"{doc}/s/p0", text=text)


OLD = _chunk("OLD/2020/1#s#0", "OLD/2020/1", "margin requirements old rules")
NEW1 = _chunk("NEW/2023/9#s#0", "NEW/2023/9", "margin requirements revised threshold")
NEW2 = _chunk("NEW/2023/9#s#1", "NEW/2023/9", "unrelated annexure boilerplate")
OTHER = _chunk("X/2021/5#s#0", "X/2021/5", "something else entirely")
ALL = [OLD, NEW1, NEW2, OTHER]

LIN = Lineage(superseded_by={"OLD/2020/1": ["NEW/2023/9"]},
              supersedes={"NEW/2023/9": ["OLD/2020/1"]})


def test_expands_with_successor_chunks_ranked_by_query_overlap():
    out = expand_successors([(OLD, 1.0)], ALL, LIN, query="margin requirements", per_doc=1)
    ids = [c.id for c, _ in out]
    assert ids[0] == OLD.id                    # original candidates preserved, in order
    assert NEW1.id in ids                      # best-matching successor chunk added
    assert NEW2.id not in ids                  # per_doc=1 caps injection


def test_no_expansion_for_in_force_candidates():
    out = expand_successors([(OTHER, 1.0)], ALL, LIN, query="anything")
    assert [c.id for c, _ in out] == [OTHER.id]


def test_no_duplicate_when_successor_already_retrieved():
    out = expand_successors([(OLD, 1.0), (NEW1, 0.9)], ALL, LIN, query="margin", per_doc=2)
    ids = [c.id for c, _ in out]
    assert ids.count(NEW1.id) == 1


def test_amended_circulars_also_expand():
    lin = Lineage(amended_by={"OLD/2020/1": ["NEW/2023/9"]})
    out = expand_successors([(OLD, 1.0)], ALL, lin, query="margin requirements", per_doc=1)
    assert NEW1.id in [c.id for c, _ in out]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_lineage_expand.py -v`
Expected: FAIL with `ImportError: cannot import name 'expand_successors'`

- [ ] **Step 3: Write minimal implementation**

Add to `src/sebi_rag/lineage.py` after `demote_superseded`:

```python
def _lex_overlap(query: str, text: str) -> int:
    """Cheap query/chunk term-overlap score for picking successor chunks.
    The cross-encoder rescores everything downstream; this only decides
    WHICH successor chunks enter the rerank pool."""
    terms = {w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 2}
    tl = text.lower()
    return sum(1 for t in terms if t in tl)


def expand_successors(
    candidates: list,
    all_chunks: list,
    lineage: "Lineage",
    query: str,
    per_doc: int = 3,
) -> list:
    """Successor-expansion (regai-inspired): when a retrieved chunk belongs to
    a superseded/amended circular, inject the top `per_doc` query-overlapping
    chunks from each in-force successor so the reranker can prefer current
    law over demoted history. Complements demote_superseded: demotion pushes
    stale content down; expansion guarantees the replacement content is even
    present in the pool."""
    successors: list[str] = []
    for c, _ in candidates:
        for s in (lineage.superseded_by.get(c.doc_id, [])
                  + lineage.amended_by.get(c.doc_id, [])):
            if s not in successors:
                successors.append(s)
    if not successors:
        return list(candidates)

    have = {c.id for c, _ in candidates}
    by_doc: dict[str, list] = {}
    for c in all_chunks:
        if c.doc_id in successors and c.id not in have:
            by_doc.setdefault(c.doc_id, []).append(c)

    out = list(candidates)
    for s in successors:
        pool = sorted(by_doc.get(s, []), key=lambda c: -_lex_overlap(query, c.text))
        for c in pool[:per_doc]:
            out.append((c, 0.0))
            have.add(c.id)
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_lineage_expand.py -v`
Expected: 4 PASSED

- [ ] **Step 5: Wire into the pipeline**

In `src/sebi_rag/pipeline.py`:

1. Extend the import on line 8:

```python
from .lineage import Lineage, demote_superseded, expand_successors, superseded_citations
```

2. Add a field to `RAGPipeline` (after `superseded_penalty`, line 21):

```python
    successor_expansion: int = 3  # chunks injected per in-force successor (0 = off)
```

3. In `query()`, replace lines 46-47:

```python
        candidates = self.retriever.retrieve(question, top_n=pool)
        reranked = self.reranker.rerank(question, [c for c, _ in candidates])
```

with:

```python
        candidates = self.retriever.retrieve(question, top_n=pool)
        if self.lineage is not None and self.successor_expansion > 0:
            candidates = expand_successors(
                candidates, self.retriever.chunks, self.lineage,
                query=question, per_doc=self.successor_expansion,
            )
        reranked = self.reranker.rerank(question, [c for c, _ in candidates])
```

(`retrieved_ids` at line 73 picks up injected chunks automatically since it reads `candidates`.)

- [ ] **Step 6: Add a pipeline-level test**

Append to `tests/test_lineage_expand.py` (mirror the fixture style of `tests/test_pipeline.py` — it builds pipelines with `HashEmbedder`; read that file first and reuse its helpers if importable):

```python
def test_pipeline_query_includes_successor_in_retrieved_ids():
    from sebi_rag.embeddings import HashEmbedder
    from sebi_rag.generate import ExtractiveStubGenerator
    from sebi_rag.pipeline import RAGPipeline
    from sebi_rag.rerank import LexicalReranker

    pipe = RAGPipeline.build(
        chunks=ALL,
        embedder=HashEmbedder(),
        reranker=LexicalReranker(),
        generator=ExtractiveStubGenerator(),
        abstain_threshold=0.0,
        lineage=LIN,
    )
    _ans, retrieved = pipe.query("margin requirements old rules", pool=1, top_k=2)
    assert any(rid.startswith("NEW/2023/9") for rid in retrieved)
```

If `HashEmbedder`/`LexicalReranker`/`ExtractiveStubGenerator` constructors take arguments (check `tests/test_pipeline.py` for the working invocation), copy the invocation used there.

Run: `uv run pytest tests/test_lineage_expand.py -v`
Expected: 5 PASSED

- [ ] **Step 7: Run full suite, then commit**

Run: `make test`
Expected: all pass.

```bash
git add tests/test_lineage_expand.py src/sebi_rag/lineage.py src/sebi_rag/pipeline.py
git commit -m "feat: successor-expansion retrieval for superseded/amended circulars"
```

---

### Task 5: Per-chunk cross-reference metadata + exact-reference promotion

**Files:**
- Modify: `src/sebi_rag/segment.py:87-107` (`flush` inside `hierarchical_chunk`)
- Modify: `src/sebi_rag/pipeline.py` (`query()`, before rerank)
- Test: `tests/test_segment_refs.py` (create)

**Interfaces:**
- Consumes: `REF_RE` from `src/sebi_rag/ingest_pdf.py:28` (safe import: `ingest_pdf` imports no sebi_rag modules, so no cycle — same pattern as `lineage.py:19`).
- Produces: chunk `meta["cross_references"]: list[str]` (only present when non-empty; keeps JSONL lean). `RAGPipeline.query()` promotes candidates matching a circular number typed in the query to the front of the rerank pool.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_segment_refs.py
from sebi_rag.segment import CircularMeta, hierarchical_chunk

META = CircularMeta(circular_number="SEBI/HO/MRD/2024/100", subject="Margin rules")


def test_chunks_carry_inline_cross_references():
    text = (
        "1. Background\n"
        "In supersession of SEBI/HO/IMD/DF3/CIR/P/2017/114, the following applies.\n\n"
        "2. Requirements\n"
        "No references here."
    )
    chunks = hierarchical_chunk(text, META)
    ref_chunks = [c for c in chunks if c.meta.get("cross_references")]
    assert ref_chunks, "chunk containing the reference should carry it in meta"
    assert "SEBI/HO/IMD/DF3/CIR/P/2017/114" in ref_chunks[0].meta["cross_references"]


def test_own_number_is_not_a_cross_reference():
    text = "1. Scope\nThis circular SEBI/HO/MRD/2024/100 applies to brokers."
    chunks = hierarchical_chunk(text, META)
    for c in chunks:
        assert "SEBI/HO/MRD/2024/100" not in c.meta.get("cross_references", [])


def test_chunks_without_refs_omit_the_key():
    chunks = hierarchical_chunk("1. Scope\nPlain text only.", META)
    assert all("cross_references" not in c.meta for c in chunks)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_segment_refs.py -v`
Expected: first test FAILS (`assert ref_chunks` → empty list).

- [ ] **Step 3: Write minimal implementation**

In `src/sebi_rag/segment.py`, add the import after line 10:

```python
from .ingest_pdf import REF_RE
```

In `flush()` (line 87), replace `meta=asdict(meta)` (line 104) with a meta dict that carries the refs. The full updated `flush`:

```python
    def flush(sec: str, body: str) -> None:
        nonlocal para_idx
        body = body.strip()
        if not body:
            return
        cid = f"{meta.circular_number}#{sec}#{para_idx}"
        # F1 (ADR-001): contextual enrichment — prepend document identity so
        # dense/sparse indexing can disambiguate topically-overlapping circulars.
        header = " | ".join(
            p for p in (meta.circular_number, meta.subject.strip()[:120], sec) if p
        )
        m = asdict(meta)
        # per-chunk inline references (regai-inspired): lets retrieval promote
        # chunks that discuss a circular the user asked about by number.
        refs = [r for r in dict.fromkeys(x.group(0) for x in REF_RE.finditer(body))
                if r != meta.circular_number]
        if refs:
            m["cross_references"] = refs
        chunks.append(
            Chunk(
                id=cid,
                doc_id=meta.circular_number,
                section=f"{meta.circular_number}/{sec}/p{para_idx}",
                text=f"{header}\n{body}",
                meta=m,
            )
        )
        para_idx += 1
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_segment_refs.py -v`
Expected: 3 PASSED

- [ ] **Step 5: Add exact-reference promotion in the pipeline (failing test first)**

Append to `tests/test_segment_refs.py`:

```python
def test_query_with_circular_number_promotes_matching_chunks():
    from sebi_rag.pipeline import _promote_reference_matches
    from sebi_rag.segment import Chunk

    target = Chunk(id="A#s#0", doc_id="A", section="A/s/p0", text="t",
                   meta={"cross_references": ["SEBI/HO/IMD/DF3/CIR/P/2017/114"]})
    noise = Chunk(id="B#s#0", doc_id="B", section="B/s/p0", text="t", meta={})
    exact = Chunk(id="SEBI/HO/IMD/DF3/CIR/P/2017/114#s#0",
                  doc_id="SEBI/HO/IMD/DF3/CIR/P/2017/114",
                  section="x/s/p0", text="t", meta={})
    cands = [(noise, 0.9), (target, 0.5), (exact, 0.4)]
    out = _promote_reference_matches(
        "What does SEBI/HO/IMD/DF3/CIR/P/2017/114 say about categorization?", cands
    )
    # chunks FROM or REFERRING TO the asked-about circular come first (stable order)
    assert [c.id for c, _ in out][:2] == [target.id, exact.id]


def test_query_without_reference_is_untouched():
    from sebi_rag.pipeline import _promote_reference_matches
    from sebi_rag.segment import Chunk
    a = Chunk(id="A#s#0", doc_id="A", section="A/s/p0", text="t")
    out = _promote_reference_matches("plain question", [(a, 1.0)])
    assert [c.id for c, _ in out] == ["A#s#0"]
```

Run: `uv run pytest tests/test_segment_refs.py -v`
Expected: 2 new FAIL (`ImportError: cannot import name '_promote_reference_matches'`)

- [ ] **Step 6: Implement promotion**

In `src/sebi_rag/pipeline.py`, add after the imports:

```python
from .ingest_pdf import REF_RE


def _promote_reference_matches(question: str, candidates: list) -> list:
    """If the user names a circular number, move candidates from that circular
    or whose text cross-references it to the front of the rerank pool (stable).
    Guarantees exact-reference lookups survive pool truncation before rerank."""
    q_refs = {m.group(0) for m in REF_RE.finditer(question)}
    if not q_refs:
        return candidates
    def hits(c) -> bool:
        return c.doc_id in q_refs or bool(q_refs & set(c.meta.get("cross_references", [])))
    return sorted(candidates, key=lambda cs: not hits(cs[0]))
```

Then in `query()`, immediately before the `reranked = self.reranker.rerank(...)` line, add:

```python
        candidates = _promote_reference_matches(question, candidates)
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `uv run pytest tests/test_segment_refs.py -v`
Expected: 5 PASSED

- [ ] **Step 8: Run full suite, then commit**

Run: `make test`
Expected: all pass. (Chunk `meta` roundtrips through `retrieve.py` persistence unchanged — it's a plain dict. Adding `cross_references` does not change chunk `.text`, so the F3 incremental-embedding checksum still reuses cached vectors; only `chunks.jsonl` is rewritten on the next `make reindex`.)

```bash
git add tests/test_segment_refs.py src/sebi_rag/segment.py src/sebi_rag/pipeline.py
git commit -m "feat: per-chunk cross-references with exact-reference promotion"
```

---

### Task 6: Rebuild index and verify end-to-end

**Files:**
- No source changes. Operational verification.

**Interfaces:**
- Consumes: everything above; `make reindex`, `make test`, `scripts/calibrate.py` (existing).

- [ ] **Step 1: Rebuild the index**

Run: `make reindex`
Expected: completes; chunk count increases versus the pre-change baseline (table chunks are additive). Note the new chunk total.

- [ ] **Step 2: Smoke-test the three features against the live index**

Run each and eyeball the output:

```bash
# table retrieval: a threshold question that lives in a table
uv run python -c "
from sebi_rag.api import build_default_pipeline
p = pipe = build_default_pipeline()
ans, ids = pipe.query('What is the minimum equity percentage for large cap mutual fund schemes?')
print(ans.text[:400]); print(ids[:5])
"
```

Expected: at least one retrieved id containing `#table`, or a correct threshold in the answer. (If `build_default_pipeline()` takes arguments, check `src/sebi_rag/api.py:68` for the working invocation.)

```bash
# successor expansion: ask about a topic covered by a known superseded circular
# pick one from: uv run python -c "import json; print([r['circular_number'] for r in map(json.loads, open('data/corpus/circulars.jsonl')) if r.get('supersession_status')=='superseded'][:5])"
```

Expected: the answer cites the in-force successor (or carries the existing supersession note), and `retrieved_ids` includes successor chunks.

```bash
# exact-reference lookup: put a known circular number in the question verbatim
```

Expected: cited chunks are from or reference that circular.

- [ ] **Step 3: Re-run retrieval calibration**

Run: `uv run python scripts/calibrate.py` (use the invocation documented in that script's header if different).
Expected: retrieval metrics ≥ pre-change baseline. If the abstention threshold shifts materially, record the new value in `RAGPipeline.abstain_threshold`'s comment — do not silently change the default.

- [ ] **Step 4: Commit any calibration doc updates**

```bash
git add -A docs/
git commit -m "docs: record post-enhancement calibration results"
```

---

# Part B — ingest_pdf.py Reference-Number Parsing: Deep Analysis & Hardening

*Added 2026-07-08 after analysis of commit `1df1892` ("Improves reference extraction for SEBI circulars with new 2026 departmental-order format") and the same-day corpus repair session. Tasks 7–10 are independent of Tasks 1–6 and may be executed first; Task 11 (network acquisition) should run last, and its reindex folds into Task 6's verification.*

## B.1 Why this module is load-bearing

`circular_number` is the corpus's primary key. It drives:

- **Deduplication** at ingest (`_existing_numbers()` / `_rewrite_replacing()`, `ingest_pdf.py:238-260`)
- **Chunk identity** — every chunk ID and `doc_id` embeds it (`segment.py:92`), so it is the citation key shown to users
- **The lineage graph** — `supersedes` / `superseded_by` / `amends` maps are keyed by it (`lineage.py:52-56`), and `detect_relations()` mines body text with the same `REF_RE`
- **Supersession demotion and warnings** at query time (`pipeline.py:48-66`)

A wrong or non-canonical number therefore silently corrupts dedup, citations, and supersession answers — which is exactly what happened (see B.3).

## B.2 The format inconsistency problem

SEBI has never used one reference format. Formats observed in the 600+ document corpus, and which parsing stage handles each:

| # | Format family | Example | Handled by |
|---|---------------|---------|-----------|
| 1 | New standard (2016+) | `SEBI/HO/IMD/DF3/CIR/P/2017/114` | `_NEW` regex; header-token stage |
| 2 | Old standard (pre-2016) | `CIR/CFD/CMD/4/2015` | `_OLD` regex; header-token stage |
| 3 | Space-split by PDF layout | `SEBI/HO/DDHS-PoD-2/ P/CIR/ 2025/104` | slash-rejoin (`ingest_pdf.py:107`) |
| 4 | Parenthetical split | `HO/ (79)2026-MIRSD` | rejoin extended to `(` (commit 1df1892) |
| 5 | Department-only prefix | `AFD/P/CIR/2022/125` | ≥4-slash + `CIR` fallback (`:116-119`) |
| 6 | 2026 departmental order (no `/CIR/`) | `HO/(79)2026-MIRSD` | `_NEW_FMT2` regex + dept-order fallbacks (`:144-156`) |
| 7 | Free-form 2026 header | `HO/47/17/12(11)2025-MRD-POD3/I/11107/2026` | first slash-heavy header token (`HEADER_TOKEN_RE`) |
| 8 | No parseable header at all | (Hindi-corrupted / gazette-style headers) | full-text `REF_RE` search (`:159`) — **risky, see R3** |

## B.3 Fix history (what recent commits changed and why)

**Commit `1df1892` (2026-07-08, +54/-3 lines)** turned `_primary_number()` from a 2-step lookup into a **6-stage fallback chain**:

1. Slash-rejoin (now including `(`) → first header token matching `HEADER_TOKEN_RE` with ≥3 slashes and a digit
2. Department-only tokens: ≥4 slashes containing `CIR`
3. Anchor-merge: join up to 4 tokens after the first `HO`/`CIR`/year anchor, search `REF_RE`, then a year-first pattern
4. Dept-order regex `HO/\(\d+\)\d{4}-DEPT` over the header
5. Prefixed variant `SEBI/HO/DEPT/(N)YYYY-...`
6. **Last resort:** earliest `REF_RE` match anywhere in the full document text

It also extended `REF_RE` with `_NEW_FMT2` so 2026 departmental orders participate in lineage mining.

**Outcome of the same-day repair session:** 400+ malformed reference numbers corrected in the corpus; of the original 19 "unparseable" PDFs, 9 available files now all parse (the remaining 14 were never downloaded — see Task 11); 6 corrupted records were re-parsed. One confirmed mis-assignment was caused by stage 6: PDF stem `1669373687117` received `CIR/2/266/2000` (a *cited* circular in its body) instead of its own `DOF2/P/CIR/2022/161`.

## B.4 Residual risks (each maps to a task below)

- **R1 — Near-zero regression coverage.** `tests/test_ingest_pdf.py` has 2 tests covering only formats 1–2. Stages 2–6 of the fallback chain — the code most likely to be touched next time SEBI invents a format — have no tests. Any future "fix" can silently regress a previously recovered format. → **Task 7**
- **R2 — Duplicated regex truth.** `dept_order_re` inside `_primary_number` (`:147-148`) restates `_NEW_FMT2` (`:27`) minus the optional `SEBI/` prefix; the prefixed variant at `:154` is a third spelling. They will drift. The 6-stage chain is also a single 59-line function that is hard to reason about per-stage. → **Task 8**
- **R3 — Full-text fallback mis-assignment.** Stage 6 returns the *earliest cited circular* when the header yields nothing — the proven `CIR/2/266/2000` failure mode. It cannot be removed (it is what recovers format 8), but its output is unvalidated. → **Task 10** (validation catches collisions/self-references) and the Task 7 test that pins this behavior as *known-risky*.
- **R4 — No canonical identity.** `SEBI/HO/X/...` and `HO/X/...` spellings of the same number are distinct keys today, so a re-scraped circular can bypass dedup and exist twice, and a body reference to the prefixed variant of the document's own number leaks into `version_lineage` as a self-reference. → **Task 9**
- **R5 — `issuing_department` gaps.** `DEPT_RE` (`:40`) only understands `SEBI/HO/<dept>/`; formats 5–7 leave the field empty. Low retrieval impact (department isn't in chunk enrichment headers); recorded here as accepted debt — fix only if a feature needs the field.
- **R6 — 14 circulars missing from the corpus.** Stems identified in the 2026-07-08 audit were never downloaded to `data/raw/`. → **Task 11**

---

### Task 7: Reference-format regression test suite (R1)

**Files:**
- Test: `tests/test_ingest_refs.py` (create)
- Modify: none (tests pin current behavior before the Task 8 refactor)

**Interfaces:**
- Consumes: `_primary_number(header: str, full: str) -> str`, `parse_meta(text: str) -> dict`, `REF_RE` from `src/sebi_rag/ingest_pdf.py`.
- Produces: the safety net Task 8 refactors against. No production code.

- [ ] **Step 1: Write the format-matrix tests (they should pass immediately)**

```python
# tests/test_ingest_refs.py
"""Regression matrix for SEBI reference-number extraction.

One case per known format family (see plan section B.2). If SEBI invents a
new format, add a row here FIRST, watch it fail, then extend the parser.
"""
import pytest

from sebi_rag.ingest_pdf import REF_RE, _primary_number, parse_meta

# (format family, header text, expected primary number)
HEADER_CASES = [
    ("new-standard", "SEBI/HO/IMD/DF3/CIR/P/2017/114 May 04, 2017",
     "SEBI/HO/IMD/DF3/CIR/P/2017/114"),
    ("old-standard", "CIR/CFD/CMD/4/2015 September 9, 2015",
     "CIR/CFD/CMD/4/2015"),
    ("space-split", "SEBI/HO/DDHS/DDHS-PoD-2/ P/CIR/ 2025/104",
     "SEBI/HO/DDHS/DDHS-PoD-2/P/CIR/2025/104"),
    ("paren-split", "HO/ (79)2026-MIRSD",
     "HO/(79)2026-MIRSD"),
    ("dept-only", "AFD/P/CIR/2022/125 dated October 28, 2022",
     "AFD/P/CIR/2022/125"),
    ("dept-order-2026", "HO/(79)2026-MIRSD",
     "HO/(79)2026-MIRSD"),
    ("free-form-2026", "SEBI/HO/47/17/12(11)2025-MRD-POD3/I/11107/2026",
     "SEBI/HO/47/17/12(11)2025-MRD-POD3/I/11107/2026"),
]


@pytest.mark.parametrize("family,header,expected",
                         HEADER_CASES, ids=[c[0] for c in HEADER_CASES])
def test_primary_number_format_matrix(family, header, expected):
    assert _primary_number(header, full=header) == expected


def test_fulltext_fallback_returns_earliest_body_reference():
    # Pins stage-6 behavior (plan risk R3): with no parseable header token the
    # earliest well-formed reference in the body wins, even though it may be a
    # CITED circular rather than the document's own number. Mitigated by the
    # corpus validation script (Task 10), not by the parser.
    n = _primary_number("Gazette Notification", 
                        "…in terms of CIR/MRD/DP/2/2000 read with…")
    assert n == "CIR/MRD/DP/2/2000"


def test_ref_re_matches_all_three_reference_grammars():
    text = ("cites SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123 and CIR/CFD/CMD/4/2015 "
            "and the order HO/(12)2026-MRD.")
    found = {m.group(0) for m in REF_RE.finditer(text)}
    assert found == {"SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123",
                     "CIR/CFD/CMD/4/2015", "HO/(12)2026-MRD"}


def test_parse_meta_dept_order_document_end_to_end():
    text = ("HO/(79)2026-MIRSD\n"
            "February 10, 2026\n"
            "To,\nAll Market Infrastructure Institutions\n"
            "Sub: Departmental reorganisation\n\n"
            "1. In terms of SEBI/HO/MIRSD/CIR/P/2023/50, the following applies.")
    meta = parse_meta(text)
    assert meta["circular_number"] == "HO/(79)2026-MIRSD"
    assert meta["issue_date"] == "2026-02-10"
    assert "SEBI/HO/MIRSD/CIR/P/2023/50" in meta["version_lineage"]
```

- [ ] **Step 2: Run and inspect**

Run: `uv run pytest tests/test_ingest_refs.py -v`
Expected: **all PASS** — these pin current behavior. If any case fails, the plan's B.2 table is wrong for that format: fix the *test's* fixture to whatever `git show 1df1892` demonstrates the parser was built to handle, and note the discrepancy in the commit message. Do not change parser code in this task.

- [ ] **Step 3: Commit**

```bash
git add tests/test_ingest_refs.py
git commit -m "test: regression matrix for SEBI reference-number formats"
```

---

### Task 8: Refactor `_primary_number` into named strategies (R2)

**Files:**
- Modify: `src/sebi_rag/ingest_pdf.py:102-160` (`_primary_number`)
- Test: `tests/test_ingest_refs.py` (no changes — it is the guard)

**Interfaces:**
- Consumes: `HEADER_TOKEN_RE`, `REF_RE`, `_NEW_FMT2` (existing module constants).
- Produces: identical signature `_primary_number(header: str, full: str) -> str`; behavior identical (Task 7 suite proves it). New module-level constants `DEPT_ORDER_RE`, `PREFIXED_DEPT_ORDER_RE`, `YEAR_FIRST_RE` replacing inline regex literals.

- [ ] **Step 1: Replace the function body with an ordered strategy chain**

Replace `_primary_number` (lines 102-160) with:

```python
# Single source of truth for the 2026 departmental-order grammar: reuse
# _NEW_FMT2 (optional SEBI/ prefix) instead of restating it inline.
DEPT_ORDER_RE = re.compile(_NEW_FMT2)
PREFIXED_DEPT_ORDER_RE = re.compile(
    r"SEBI/HO/[A-Za-z0-9_()\-]+/\(\d+\)\d{4}-[A-Za-z0-9_()\-]+")
YEAR_FIRST_RE = re.compile(r"\d{4}/[A-Za-z0-9_()\-/]+?/\d+")


def _rejoin_split(header: str) -> str:
    """Rejoin numbers split by a space after a slash, e.g. "CIR/ 2025/104" or
    "HO/ (79)2026-MRD" (PDF layout inserts a space mid-number)."""
    return re.sub(r"/\s+(?=[A-Za-z0-9(])", "/", header)


def _s_header_token(header: str) -> str:
    """Format 1/2/3/7: first slash-heavy HO/CIR-prefixed header token."""
    for tok in header.split():
        t = tok.strip(".,;:")
        if HEADER_TOKEN_RE.match(t) and t.count("/") >= 3 and re.search(r"\d", t):
            return t
    return ""


def _s_dept_only(header: str) -> str:
    """Format 5: department-only prefixes without HO/CIR anchor,
    e.g. AFD/P/CIR/2022/125."""
    for tok in header.split():
        t = tok.strip(".,;:")
        if t.count("/") >= 4 and "CIR" in t:
            return t
    return ""


def _s_anchor_merge(header: str) -> str:
    """Formats split across tokens: merge up to 4 tokens after the first
    HO/CIR/year anchor, then look for a well-formed or year-first reference."""
    parts = header.split()
    for i, tok in enumerate(parts):
        t = tok.strip(".,;:")
        if HEADER_TOKEN_RE.match(t) or re.match(r"^\d{4}/", t):
            merged = _rejoin_split(" ".join(parts[i:i + 4]))
            m = REF_RE.search(merged) or YEAR_FIRST_RE.search(merged)
            return m.group(0) if m else ""
    return ""


def _s_dept_order(header: str) -> str:
    """Format 6: 2026 departmental orders, bare or SEBI/HO-prefixed —
    no /CIR/ and possibly the only token on the line."""
    m = DEPT_ORDER_RE.search(header) or PREFIXED_DEPT_ORDER_RE.search(header)
    return m.group(0) if m else ""


_PRIMARY_STRATEGIES = (_s_header_token, _s_dept_only, _s_anchor_merge, _s_dept_order)


def _primary_number(header: str, full: str) -> str:
    header = _rejoin_split(header)
    for strategy in _PRIMARY_STRATEGIES:
        n = strategy(header)
        if n:
            return n
    # Last resort (risk R3, see docs/superpowers/plans/2026-07-08-*.md B.4):
    # earliest well-formed reference anywhere in the text — may be a CITED
    # circular. Output is checked by scripts/validate_corpus.py.
    m = REF_RE.search(full)
    return m.group(0) if m else ""
```

Note one deliberate behavior change: `DEPT_ORDER_RE` (via `_NEW_FMT2`) accepts an optional `SEBI/` prefix that the old inline `dept_order_re` did not — a strict superset, and `PREFIXED_DEPT_ORDER_RE` still covers the `SEBI/HO/DEPT/(N)YYYY` shape.

- [ ] **Step 2: Run the regression suite**

Run: `uv run pytest tests/test_ingest_refs.py tests/test_ingest_pdf.py -v`
Expected: all PASS. If any format-matrix case fails, the refactor changed stage ordering or a regex — fix the refactor, not the test.

- [ ] **Step 3: Verify against the real corpus (no output change)**

Run: `uv run python -c "
import json
from sebi_rag.ingest_pdf import parse_meta
recs = [json.loads(l) for l in open('data/corpus/circulars.jsonl') if l.strip()]
mismatch = sum(1 for r in recs if parse_meta(r['text'])['circular_number'] != r['circular_number'])
print(f'{len(recs)} records, {mismatch} parse mismatches')
"`
Expected: `mismatch` equal to the count *before* the refactor (measure by running the same command on `git stash`-ed state first; some stored numbers were hand-repaired and never matched re-parsing — the refactor must not increase the number).

- [ ] **Step 4: Run full suite, then commit**

Run: `make test`
Expected: all pass.

```bash
git add src/sebi_rag/ingest_pdf.py
git commit -m "refactor: split _primary_number into ordered named strategies"
```

---

### Task 9: Canonical circular-number normalization (R4)

**Files:**
- Modify: `src/sebi_rag/ingest_pdf.py` (add `normalize_circular_number()`; use in `_existing_numbers`, `ingest`, `_rewrite_replacing`, `parse_meta`)
- Test: `tests/test_ingest_refs.py` (extend)

**Interfaces:**
- Consumes: nothing new.
- Produces: `normalize_circular_number(n: str) -> str` — a *comparison key only*; stored `circular_number` values keep their original spelling (chunk IDs and lineage keys stay stable per Global Constraints). Task 10's validator uses it for uniqueness checks.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_ingest_refs.py`:

```python
def test_normalize_treats_prefix_and_spacing_variants_as_same():
    from sebi_rag.ingest_pdf import normalize_circular_number as norm
    assert norm("SEBI/HO/MIRSD/CIR/P/2024/10") == norm("HO/MIRSD/CIR/P/2024/10")
    assert norm("CIR/ CFD/CMD/4/2015") == norm("CIR/CFD/CMD/4/2015")
    assert norm("cir/cfd/cmd/4/2015.") == norm("CIR/CFD/CMD/4/2015")
    # different numbers must stay different
    assert norm("CIR/CFD/CMD/4/2015") != norm("CIR/CFD/CMD/5/2015")


def test_dedup_uses_normalized_numbers(tmp_path):
    import json
    from sebi_rag.ingest_pdf import _existing_numbers, normalize_circular_number
    p = tmp_path / "c.jsonl"
    p.write_text(json.dumps({"circular_number": "SEBI/HO/X/CIR/2024/9"}) + "\n",
                 encoding="utf-8")
    assert normalize_circular_number("HO/X/CIR/2024/9") in _existing_numbers(p)


def test_parse_meta_excludes_prefix_variant_self_reference():
    from sebi_rag.ingest_pdf import parse_meta
    text = ("HO/MIRSD/CIR/P/2024/10\nMarch 01, 2024\nTo,\nAll intermediaries\n"
            "Sub: Something\n\n"
            "1. This circular SEBI/HO/MIRSD/CIR/P/2024/10 shall come into force…")
    meta = parse_meta(text)
    assert meta["version_lineage"] == []  # own number, prefixed variant, excluded
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_ingest_refs.py -v -k "normalize or dedup or self_reference"`
Expected: FAIL (`ImportError: cannot import name 'normalize_circular_number'`, and the self-reference test finds the variant leaked into `version_lineage`).

- [ ] **Step 3: Implement**

Add to `src/sebi_rag/ingest_pdf.py` after `REF_RE`:

```python
def normalize_circular_number(n: str) -> str:
    """Canonical COMPARISON key for a circular number: strip whitespace and
    trailing punctuation, drop the optional leading 'SEBI/', casefold.
    Never store this form — stored numbers keep the document's own spelling
    (chunk IDs and lineage keys must stay stable)."""
    n = re.sub(r"\s+", "", n).strip(".,;:")
    if n.upper().startswith("SEBI/"):
        n = n[len("SEBI/"):]
    return n.casefold()
```

Then apply it in four places:

1. `_existing_numbers` — normalize what goes into the set:

```python
def _existing_numbers(corpus_path: Path) -> set[str]:
    if not corpus_path.exists():
        return set()
    nums = set()
    for line in corpus_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            nums.add(normalize_circular_number(
                json.loads(line).get("circular_number", "")))
    return nums
```

2. `ingest` — normalize the membership probe (line 278):

```python
    if normalize_circular_number(rec["circular_number"]) in _existing_numbers(corpus_path):
```

3. `_rewrite_replacing` — normalized comparison (line 256):

```python
        if (normalize_circular_number(json.loads(line).get("circular_number", ""))
                == normalize_circular_number(rec["circular_number"])):
            continue
```

4. `parse_meta` — exclude normalized-equal self-references from lineage (lines 172-176):

```python
    lineage = []
    primary_key = normalize_circular_number(primary) if primary else ""
    for m in REF_RE.finditer(text):
        n = m.group(0)
        if normalize_circular_number(n) != primary_key and n not in lineage:
            lineage.append(n)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_ingest_refs.py -v`
Expected: all PASS (including the Task 7 matrix — normalization must not alter extraction).

- [ ] **Step 5: Run full suite, then commit**

Run: `make test`
Expected: all pass.

```bash
git add tests/test_ingest_refs.py src/sebi_rag/ingest_pdf.py
git commit -m "feat: canonical circular-number normalization for dedup and lineage"
```

---

### Task 10: Corpus validation script (R3, R4 guard)

**Files:**
- Create: `scripts/validate_corpus.py`
- Test: `tests/test_validate_corpus.py` (create)

**Interfaces:**
- Consumes: `normalize_circular_number` from Task 9; corpus JSONL schema.
- Produces: `validate(records: list[dict]) -> list[str]` (list of human-readable violations, empty = clean) and a CLI that exits 1 on violations. Run after every ingest, backfill (Task 2), or repair session.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_validate_corpus.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_corpus import validate  # noqa: E402


def _rec(**kw) -> dict:
    base = {"circular_number": "SEBI/HO/X/CIR/P/2024/1", "issue_date": "2024-01-05",
            "version_lineage": [], "text": "body"}
    return {**base, **kw}


def test_clean_corpus_has_no_violations():
    assert validate([_rec()]) == []


def test_flags_empty_and_malformed_numbers():
    v = validate([_rec(circular_number=""),
                  _rec(circular_number="BROKEN NUMBER 12")])
    assert len(v) == 2


def test_flags_normalized_duplicates():
    v = validate([_rec(), _rec(circular_number="HO/X/CIR/P/2024/1")])
    assert any("duplicate" in x for x in v)


def test_flags_self_reference_in_lineage():
    v = validate([_rec(version_lineage=["SEBI/HO/X/CIR/P/2024/1"])])
    assert any("self-reference" in x for x in v)


def test_flags_bad_issue_date():
    v = validate([_rec(issue_date="05-01-2024")])
    assert any("issue_date" in x for x in v)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_validate_corpus.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'validate_corpus'`

- [ ] **Step 3: Write the script**

```python
# scripts/validate_corpus.py
"""Validate corpus invariants after any ingest/backfill/repair.

Checks (per plan B.4): every record has a plausible circular_number
(non-empty, no whitespace, contains '/' and a digit); numbers are unique
under normalization (catches SEBI/-prefix duplicates, R4); version_lineage
contains no self-references (catches stage-6 mis-assignment fallout, R3);
issue_date is ISO or empty.

Usage: uv run python scripts/validate_corpus.py [data/corpus/circulars.jsonl]
Exit 0 = clean, 1 = violations (printed one per line).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sebi_rag.ingest_pdf import normalize_circular_number  # noqa: E402

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _plausible(n: str) -> bool:
    return bool(n) and " " not in n and "/" in n and any(ch.isdigit() for ch in n)


def validate(records: list[dict]) -> list[str]:
    violations: list[str] = []
    seen: dict[str, str] = {}
    for i, r in enumerate(records):
        n = r.get("circular_number", "")
        where = f"record {i} ({n or '<empty>'})"
        if not _plausible(n):
            violations.append(f"{where}: implausible circular_number")
            continue
        key = normalize_circular_number(n)
        if key in seen:
            violations.append(f"{where}: duplicate of {seen[key]} under normalization")
        else:
            seen[key] = n
        for ref in r.get("version_lineage", []):
            if normalize_circular_number(ref) == key:
                violations.append(f"{where}: self-reference in version_lineage")
        d = r.get("issue_date", "")
        if d and not ISO_DATE_RE.match(d):
            violations.append(f"{where}: non-ISO issue_date {d!r}")
    return violations


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/corpus/circulars.jsonl")
    records = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()
               if l.strip()]
    violations = validate(records)
    for v in violations:
        print(v)
    print(f"{len(records)} records, {len(violations)} violations")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_validate_corpus.py -v`
Expected: 5 PASSED

- [ ] **Step 5: Run against the real corpus**

Run: `uv run python scripts/validate_corpus.py`
Expected: `603 records, 0 violations` (or a small violation list — today's repair session claimed zero broken numbers; any violations found are *pre-existing data bugs*: fix the data with the Task 2 backfill/repair tooling, re-run, and record what was found in the commit message).

- [ ] **Step 6: Commit**

```bash
git add tests/test_validate_corpus.py scripts/validate_corpus.py
git commit -m "feat: corpus validation script for reference-number invariants"
```

---

### Task 11: Acquire the 14 missing circular PDFs (R6)

**Files:**
- Create: `scripts/acquire_missing_pdfs.py`

**Interfaces:**
- Consumes: `fetch(url, rate)` from `scripts/scrape_sebi.py` (polite, rate-limited; robots.txt permits `/sebi_data/attachdocs`); `sebi_rag.ingest_pdf.ingest()`; `scripts/validate_corpus.py` from Task 10.
- Produces: the 14 PDFs in `data/raw/`, ingested corpus records, and a clean validation run. **Network task** — the Global Constraints "no network" rule applies to the RAG pipeline, not to the sanctioned scraper path (`make scrape` precedent).

- [ ] **Step 1: Write the acquisition script**

```python
# scripts/acquire_missing_pdfs.py
"""Download the 14 circular PDFs identified as missing in the 2026-07-08
audit (never downloaded; blocked corpus completion of the '19 unparseable'
issue), then ingest each into the corpus.

Polite: reuses scrape_sebi.fetch (rate-limited). Idempotent: skips stems
already present in data/raw/ and relies on ingest()'s dedup.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from scrape_sebi import fetch            # noqa: E402
from sebi_rag.ingest_pdf import ingest   # noqa: E402

MISSING_STEMS = [
    "1705319176210", "1706306045806", "1708533481758", "1709691276891",
    "1709783974409", "1710751501256", "1711441070499", "1711642358729",
    "1711994539797", "1713433746620", "1714509677753", "1714919308556",
    "1724114634944", "1737774327832",
]
RAW = ROOT / "data/raw"
CORPUS = ROOT / "data/corpus/circulars.jsonl"
RATE = 3.0  # seconds between requests


def main() -> int:
    ok = failed = skipped = 0
    for stem in MISSING_STEMS:
        dest = RAW / f"{stem}.pdf"
        url = f"https://www.sebi.gov.in/sebi_data/attachdocs/{stem}.pdf"
        if not dest.exists():
            try:
                dest.write_bytes(fetch(url, RATE))
            except Exception as e:
                print(f"FAIL download {stem}: {e}")
                failed += 1
                continue
        try:
            rec = ingest(dest, CORPUS, source_url=url)
            status = rec.get("_skipped") or ("replaced" if rec.get("_replaced") else "ingested")
            print(f"{status}: {stem} -> {rec['circular_number']}")
            skipped += status == "duplicate"
            ok += status != "duplicate"
        except Exception as e:
            print(f"FAIL ingest {stem}: {e}")
            failed += 1
    print(f"ok={ok} duplicate={skipped} failed={failed} of {len(MISSING_STEMS)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Before running, check `fetch`'s exact signature in `scripts/scrape_sebi.py:75` (it may take extra keyword arguments or return a response object rather than bytes) and adapt the call — keep the rate limit.

- [ ] **Step 2: Run it**

Run: `uv run python scripts/acquire_missing_pdfs.py`
Expected: up to 14 downloads + ingests. Some stems may 404 (SEBI occasionally relocates attachments) and some may hit the `ValueError: No SEBI circular number found` guard — report both counts; do not retry-loop 404s. Any `No SEBI circular number found` failure is a *new format family*: add it to the Task 7 matrix as a failing test before extending the parser.

- [ ] **Step 3: Validate and reindex**

Run: `uv run python scripts/validate_corpus.py`
Expected: 0 violations, record count grown by the number ingested.

Run: `make reindex`
Expected: completes; index picks up the new circulars (this also serves Task 6 Step 1 if Part B runs before Part A).

- [ ] **Step 4: Commit**

```bash
git add scripts/acquire_missing_pdfs.py
git commit -m "feat: acquire and ingest the 14 missing circular PDFs"
```

(Corpus/data files: follow the same versioning practice as Task 2's note.)

---

## Explicitly out of scope (decided during planning)

- **regai's cloud stack** (pgvector/Supabase, OpenAI `text-embedding-3-large`, Claude API): rejected — conflicts with local-first Apple Silicon design.
- **Multi-regulator corpus** (RBI master directions, AMFI guidelines): deferred by user decision; would need new scrapers, reference regexes (`RBI/\d{4}-\d{2}/...`), and lineage rules.
- **Synthetic "amendment_link" chunks** (regai's approach): redundant here — the lineage graph plus supersession notes in `pipeline.query()` already cover it with real provenance instead of synthetic text.
- **`issuing_department` extraction for non-standard formats** (risk R5 in Part B): `DEPT_RE` only understands `SEBI/HO/<dept>/`; dept-only and 2026 formats leave the field empty. Accepted debt — the field feeds no retrieval or citation feature today; revisit only when something consumes it.
