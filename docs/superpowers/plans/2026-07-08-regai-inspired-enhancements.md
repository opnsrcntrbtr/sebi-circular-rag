# regai-Inspired Enhancements (Validated)

> **For agentic workers:** Use `superpowers:executing-plans` or `superpowers:subagent-driven-development`. Execute one task at a time. `tests/test_ingest_refs.py` is the regression net — must stay green.

**Goal:** Adopt three regai ideas — table-aware chunking, successor-expansion retrieval, per-chunk cross-reference metadata — without changing the local-first stack.

**Architecture:** All three slot into existing pipeline stages. See Part A below.

**Tech Stack:** Python 3.12–3.13, pdfplumber (already imported in `ingest_pdf.py`), FAISS + bm25s, pytest. No new dependencies.

---

## Part A — Pending Tasks (1–6)

### Task 1: Table extraction at PDF ingestion

**Files:** `src/sebi_rag/ingest_pdf.py` (add after `extract_text()` at **line 71**), `tests/test_ingest_tables.py` (create)

**Interface:** `extract_tables(pdf_path) -> list[{"page": int, "headers": list[str], "rows": list[list[str]]}]`. Task 2 stores under corpus key `"tables"`; Task 3 chunks it.

**Steps:**
1. Write failing test for `_normalize_table(raw) -> dict | None` (strips cells, drops empty rows, first row = headers, rejects <2 data rows or <2 cols).
2. Run `uv run pytest tests/test_ingest_tables.py -v` → expect `ImportError`.
3. Implement `_normalize_table()` + `extract_tables()` in `ingest_pdf.py` (after line 71).
4. Run test → expect 2 PASSED.
5. `make test` → all pass. Commit.

```python
# tests/test_ingest_tables.py (minimal spec)
from sebi_rag.ingest_pdf import _normalize_table

def test_normalize_table_strips_cells_and_splits_headers():
    raw = [["Category ", None, "Min Equity %"], ["Large Cap", "Top 100", " 80 "],
           [None, None, None], ["Mid Cap", "101-250", "65"]]
    t = _normalize_table(raw)
    assert t["headers"] == ["Category", "", "Min Equity %"]
    assert t["rows"] == [["Large Cap", "Top 100", "80"], ["Mid Cap", "101-250", "65"]]

def test_normalize_table_rejects_degenerate():
    assert _normalize_table([["only header", "row"]]) is None
    assert _normalize_table([["a"], ["b"], ["c"]]) is None
```

### Task 2: Store tables on corpus records + backfill

**Files:** `src/sebi_rag/ingest_pdf.py:ingest()` (~line 314), `scripts/backfill_tables.py` (create), extend `tests/test_ingest_tables.py`

**Interface:** Corpus JSONL records gain optional `"tables"` key. `load_circulars` reads via `r.get("tables", [])`.

**Steps:**
1. Read `ingest()` at `src/sebi_rag/ingest_pdf.py:314`; locate where the record dict is assembled.
2. Add `record["tables"] = extract_tables(pdf_path)` after text extraction + `parse_meta`.
3. Write `scripts/backfill_tables.py`: re-extracts tables from `data/raw/*.pdf`, matches by `circular_number`, updates corpus in-place. Idempotent.
4. Run `uv run python scripts/backfill_tables.py` → expect summary line. Spot-check: `uv run python -c "import json; rs=[json.loads(l) for l in open('data/corpus/circulars.jsonl')]; ts=[r for r in rs if r.get('tables')]; print(len(ts))"` → nonzero.
5. `make test` → all pass. Commit.

### Task 3: Table-aware chunking in segmentation

**Files:** `src/sebi_rag/segment.py` (add `format_table_rows()` + `table_chunks()` after `hierarchical_chunk()` at **line 78**), `src/sebi_rag/corpus.py` (line 30, append table chunks in `load_circulars`), `tests/test_segment_tables.py` (create)

**Interface:** `table_chunks(tables, meta: CircularMeta, max_chars=1200) -> list[Chunk]`. IDs: `{circular_number}#table{t_idx}#p{part}`. Meta carries `{"chunk_type": "table"}`.

**Note:** `CircularMeta` now has 11 fields (plan didn't list these newer ones): `circular_type`, `validity_status`, `superseded_by_id`, `amendment_history`. Task 3's `asdict(meta)` will include them — that's fine, they're additive per-circular metadata on the corpus record.

**Steps:**
1. Write failing test for `format_table_rows(headers, rows) -> list[str]` (pairs each cell with header) + `table_chunks()` (stable IDs, enriched text, splits at row boundaries, empty tables → no chunks).
2. Run → expect `ImportError`.
3. Implement `format_table_rows()` + `table_chunks()` in `segment.py` (after line 78).
4. Run test → expect 4 PASSED.
5. Wire into `corpus.py:load_circulars` (line 30): import `table_chunks`, append `chunks.extend(table_chunks(r.get("tables", []), meta))` after `hierarchical_chunk` call.
6. Add corpus-level test: `load_circulars` emits chunks with `chunk_type == "table"` and header-paired text.
7. `make test` → all pass (records without `tables` unaffected). Commit.

### Task 4: Successor-expansion retrieval

**Files:** `src/sebi_rag/lineage.py` (add `expand_successors()` after `demote_superseded()` at **line 206**), `src/sebi_rag/pipeline.py:44` (`RAGPipeline.query`), `tests/test_lineage_expand.py` (create)

**Interface:** `expand_successors(candidates, all_chunks, lineage, query, per_doc=3) -> list[tuple[Chunk, float]]`. Injects up to `per_doc` query-overlapping chunks from each in-force successor. Scored `0.0` (reranker rescores). New `RAGPipeline.successor_expansion: int = 3` (0 = off).

**Note:** `Lineage` now has 6 fields (plan only listed 4): `supersedes`, `amends`, `edges` in addition to `superseded_by`, `amended_by`. `expand_successors` should use `superseded_by` and `amended_by` (as planned). `RAGPipeline.query()` also accepts `as_of` and `advisory` params (plan omitted these).

**Steps:**
1. Write failing test: expands with successor chunks ranked by query overlap; no expansion for in-force candidates; no duplicates when successor already retrieved; amended circulars also expand.
2. Run → expect `ImportError`.
3. Implement `_lex_overlap(query, text) -> int` + `expand_successors()` in `lineage.py` (after line 206).
4. Run test → expect 4 PASSED.
5. Wire into `pipeline.py`: import `expand_successors`; add `successor_expansion: int = 3` to `RAGPipeline` (after `superseded_penalty` at line 22); call `expand_successors()` between `retrieve()` and `rerank()` when `lineage is not None and successor_expansion > 0`.
6. Add pipeline-level test: `RAGPipeline.build()` with `lineage=LIN`, query returns successor chunks in `retrieved_ids`.
7. `make test` → all pass. Commit.

### Task 5: Per-chunk cross-reference metadata + exact-reference promotion

**Files:** `src/sebi_rag/segment.py:99-125` (`flush` inside `hierarchical_chunk`), `src/sebi_rag/pipeline.py` (`query()` before rerank), `tests/test_segment_refs.py` (create)

**Interface:** Chunk `meta["cross_references"]: list[str]` (only when non-empty). `RAGPipeline.query()` promotes candidates matching a circular number typed in the query to front of rerank pool.

**Note:** `pipeline.py` already imports `Lineage, demote_superseded, superseded_citations` at line 8. Task 5 adds `REF_RE` import (safe: `ingest_pdf` imports no `sebi_rag` modules, same pattern as `lineage.py:19`).

**Steps:**
1. Write failing test: chunks carry inline cross-refs (from `REF_RE` in `ingest_pdf.py:28`); own number excluded; chunks without refs omit the key.
2. Run → expect first test fails (empty list).
3. In `segment.py`: import `REF_RE` from `ingest_pdf`; in `flush()` (line 99), replace `meta=asdict(meta)` with meta dict carrying `refs = [r for r in dict.fromkeys(x.group(0) for x in REF_RE.finditer(body)) if r != meta.circular_number]`; set `m["cross_references"] = refs` when non-empty.
4. Run test → expect 3 PASSED.
5. Add failing test for `_promote_reference_matches(question, candidates)`: moves chunks FROM or REFERRING TO the asked-about circular to front (stable order); query without reference is untouched.
6. Implement `_promote_reference_matches()` in `pipeline.py` (imports `REF_RE`); call before `rerank()` in `query()`.
7. Run test → expect 5 PASSED. `make test` → all pass. Commit.

### Task 6: Rebuild index and verify end-to-end

**Files:** None. Operational verification.

**Steps:**
1. `make reindex` → chunk count increases (table chunks additive). Note new total.
2. Smoke-test three features:
   - Table retrieval: threshold question → expect `#table` in retrieved IDs or correct threshold in answer.
   - Successor expansion: query about superseded circular → expect in-force successor cited, successor chunks in `retrieved_ids`.
   - Exact-reference lookup: circular number in query → expect chunks from or referencing that circular.
3. `uv run python scripts/calibrate.py` → metrics ≥ pre-change baseline. Record new `abstain_threshold` if shifted.
4. `git add -A docs/; git commit -m "docs: record post-enhancement calibration results"`

---

## Part B — Completed (Tasks 7–11)

All tasks 7–11 are **DONE** (commits `0599f8d`, `ceee476`, `a78fd7d`, `9a3198e`). Codebase confirms:

| Artifact | Path | Line | Status |
|----------|------|------|--------|
| `_primary_number()` (4-strategy chain) | `src/sebi_rag/ingest_pdf.py` | 196 | ✅ |
| `normalize_circular_number()` | `src/sebi_rag/ingest_pdf.py` | 31 | ✅ |
| `REF_RE` (3 grammar families) | `src/sebi_rag/ingest_pdf.py` | 28 | ✅ |
| `parse_meta()` | `src/sebi_rag/ingest_pdf.py` | 214 | ✅ |
| `Lineage` class (6 fields) | `src/sebi_rag/lineage.py` | 70 | ✅ |
| `detect_relations_ex()` | `src/sebi_rag/lineage.py` | 35 | ✅ (newer, not in plan) |
| `demote_superseded()` | `src/sebi_rag/lineage.py` | 206 | ✅ |
| `superseded_citations()` | `src/sebi_rag/lineage.py` | 218 | ✅ |
| `detect_relations()` / `detect_relations_ex()` | `src/sebi_rag/lineage.py` | 63, 35 | ✅ |
| `RAGPipeline` class | `src/sebi_rag/pipeline.py` | 16 | ✅ |
| `RAGPipeline.query()` | `src/sebi_rag/pipeline.py` | 44 | ✅ |
| `Chunk` / `CircularMeta` | `src/sebi_rag/segment.py` | 33, 18 | ✅ |
| Regression test suite | `tests/test_ingest_refs.py` | — | ✅ |
| Corpus validation script | `scripts/validate_corpus.py` | — | ✅ |
| Validation test | `tests/test_validate_corpus.py` | — | ✅ |
| Missing PDFs script | `scripts/acquire_missing_pdfs.py` | — | ✅ (0/14 recovered — stems likely withdrawn) |

**Key data structures (current state):**

```
CircularMeta (11 fields): circular_number, issue_date, effective_date, subject,
  issuing_department, supersession_status, amendment_history, version_lineage,
  circular_type, validity_status, superseded_by_id

Lineage (6 fields): supersedes, amends, superseded_by, amended_by, edges

RAGPipeline fields: retriever, reranker, generator, abstain_threshold=0.40,
  lineage, superseded_penalty=0.3, judge, regulatory_index, query()
```

**Key decisions from Part B:**
- `circular_number` is the corpus primary key — drives dedup (`_existing_numbers`), chunk identity (`segment.py:92`), lineage graph (`lineage.py:70`), and supersession demotion (`pipeline.py:48-66`).
- 8 format families observed (see original plan B.2 table). The 4-strategy chain in `_primary_number` handles all.
- Stage 6 (full-text fallback) is known-risky: returns earliest cited circular when header yields nothing. Mitigated by `validate_corpus.py` (catches collisions/self-references).
- 14 stems from 2026-07-08 audit remain absent (603 records, not 617). `attachdocs` path appears retired site-wide; script will recover PDFs if/when SEBI's listings change.

---

## Global Constraints (unchanged)

- Local-first: no network calls, no new services, no cloud dependencies.
- Python 3.12–3.13; run tests with `uv run pytest` (offline: `make test`).
- Chunk IDs must stay stable and deterministic (they are citation keys).
- `Chunk` must remain round-trippable through `retrieve.py` persistence (`Chunk(**json.loads(line))`).
- Corpus JSONL changes must be backward compatible: readers tolerate records without new `tables` field.
- All existing tests must keep passing after every task.
- Commit after every green test cycle.
