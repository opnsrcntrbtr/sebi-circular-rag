# Surface `regulatory_basis_status` Through Retrieval / Generation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the already-computed `regulatory_basis_status` corpus field reach users — as per-citation metadata in the API/UI and as an in-text advisory note for the `repealed_basis` case — without touching retrieval, the index, or the locked supersession rules.

**Architecture:** One stdlib loader (`load_regulations`) and one display helper (`reg_display_name`) in `regulations.py`; one pure join (`build_regulatory_index`) in `reg_lineage.py` producing a `dict[circular_number, entry]`; one additive optional field `regulatory_index` on `RAGPipeline` consumed in two places — an in-text note in `pipeline.py::query()` and per-citation metadata in `api.py::_citation_meta()`, surfaced in the Gradio table in `ui.py`. `regulations.jsonl` missing ⇒ index `None` ⇒ everything degrades to today's behaviour.

**Tech Stack:** Python 3.12, stdlib only for `regulations.py` / `reg_lineage.py` (no torch/faiss). Pydantic v2 models in `api.py`. pytest. Gradio + pandas in `ui.py`.

**Spec:** `docs/superpowers/specs/2026-07-23-surface-regulatory-basis-status-design.md`

## Global Constraints

- Python 3.12 only (`pyproject.toml` pins `>=3.12,<3.13`). Use `.venv/bin/python`.
- Run all commands from the repo root: `/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG`.
- Tests need `PYTHONPATH=src`. Prefix pytest with it, e.g. `PYTHONPATH=src .venv/bin/python -m pytest ...`.
- **Never add fields to `CircularMeta`** (`src/sebi_rag/segment.py:18-30`). This feature adds nothing to the chunk payload or the persisted index — it reads corpus-record fields that already exist.
- **Never edit the Spaces modules** — `api_spaces.py`, `corpus_spaces.py`, `generate_spaces.py`, root `app.py`.
- **Do not modify `validity_status`, `supersession_status`, retrieval ranking, or `superseded_penalty`.** No `regulatory_basis_penalty`. This is a presentation signal only.
- `regulatory_basis_status` vocabulary is exactly `current | repealed_basis | mixed | unknown`. Regulation `status` vocabulary is exactly `in_force | repealed | unknown`.
- The in-text note fires only for `repealed_basis` **and** only when the circular number appears verbatim in `ans.text` (identical gate to the existing supersession note at `pipeline.py:77-92`).
- Every displayed regulation name is composed as `"{short_name} Regulations, {year}"` — never `short_name` alone (repeal pairs share `short_name`; only the year disambiguates).
- The three new source modules (`regulations.py`, `reg_lineage.py` additions) import stdlib only, so every new test runs under `-m "not integration"`.
- Commit after every task. Do not squash tasks together.

## Data shapes (verified against real files 2026-07-23)

A `regulations.jsonl` record (fields this feature reads):
```json
{"reg_id": "stock-brokers-1992", "title": "SEBI (Stock Brokers) Regulations, 1992",
 "short_name": "Stock Brokers", "year": 1992, "status": "repealed",
 "superseded_by_reg": "stock-brokers-2026", "supersedes_reg": []}
```
- `short_name` is a bare noun; `year` is an `int`; `superseded_by_reg` is `str | None` (NOT a list).
- An in-force reg has `superseded_by_reg: null`; a `repealed` reg always has a non-null `superseded_by_reg` (invariant from `reg_lineage.py:88`).

A `circulars.jsonl` record carries (added by `make reg-edges`): `regulations: list[str]` (reg_ids), `primary_regulation: str | None`, `regulatory_basis_status: str`, plus `circular_number`.

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `src/sebi_rag/regulations.py` | + `load_regulations`, `reg_display_name` | 1 |
| `tests/test_regulations.py` | tests for the above | 1 |
| `src/sebi_rag/reg_lineage.py` | + `build_regulatory_index` | 2 |
| `tests/test_reg_lineage.py` | tests for the above | 2 |
| `src/sebi_rag/pipeline.py` | + `regulatory_index` field; in-text note block | 3 |
| `tests/test_pipeline.py` | note-firing + year-disambiguation tests | 3 |
| `src/sebi_rag/api.py` | `RegulationSuccessor`/`RegulationRef` models; `CitationMeta` fields; `_citation_meta` signature; load index in `build_default_pipeline` | 4 |
| `tests/test_api.py` | CitationMeta field + degrade tests | 4 |
| `src/sebi_rag/ui.py` | + "Regulatory Basis" column | 5 |
| `CLAUDE.md` | document that the field is now surfaced | 5 |

---

### Task 1: `load_regulations` + `reg_display_name`

**Files:**
- Modify: `src/sebi_rag/regulations.py` (append two functions)
- Test: `tests/test_regulations.py` (append)

**Interfaces:**
- Consumes: nothing (stdlib only)
- Produces:
  - `load_regulations(path: str | Path) -> list[dict]`
  - `reg_display_name(short_name: str, year: int | None) -> str` → `"{short_name} Regulations, {year}"`, or `short_name` alone when `year` is falsy.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_regulations.py`:

```python
import json

from sebi_rag.regulations import load_regulations, reg_display_name


def test_load_regulations_round_trips(tmp_path):
    p = tmp_path / "regulations.jsonl"
    recs = [
        {"reg_id": "mutual-funds-1996", "short_name": "Mutual Funds", "year": 1996},
        {"reg_id": "mutual-funds-2026", "short_name": "Mutual Funds", "year": 2026},
    ]
    p.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    out = load_regulations(p)
    assert out == recs


def test_load_regulations_skips_blank_lines(tmp_path):
    p = tmp_path / "regulations.jsonl"
    p.write_text('{"reg_id": "x"}\n\n   \n', encoding="utf-8")
    assert load_regulations(p) == [{"reg_id": "x"}]


def test_reg_display_name_composes_year():
    assert reg_display_name("Stock Brokers", 1992) == "Stock Brokers Regulations, 1992"


def test_reg_display_name_falls_back_without_year():
    assert reg_display_name("Stock Brokers", None) == "Stock Brokers"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_regulations.py -k "load_regulations or reg_display_name" -v`
Expected: FAIL with `ImportError: cannot import name 'load_regulations'`.

- [ ] **Step 3: Write minimal implementation**

Check the top of `src/sebi_rag/regulations.py` for existing imports; ensure `import json` and `from pathlib import Path` are present (add if missing). Append at end of file:

```python
def load_regulations(path: str | Path) -> list[dict]:
    """Load data/corpus/regulations.jsonl into a list of regulation records.

    Thin JSONL loader, symmetric with lineage.load_records / corpus.load_circulars.
    """
    out: list[dict] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def reg_display_name(short_name: str, year: int | None) -> str:
    """Human-readable regulation name. Year disambiguates same-short_name repeal
    pairs (e.g. 'Stock Brokers' 1992 vs 2026), so it is included whenever known.
    """
    return f"{short_name} Regulations, {year}" if year else short_name
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_regulations.py -v`
Expected: PASS (existing tests in the file stay green too).

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/regulations.py tests/test_regulations.py
git commit -m "feat(regulations): load_regulations + reg_display_name helper"
```

---

### Task 2: `build_regulatory_index`

**Files:**
- Modify: `src/sebi_rag/reg_lineage.py` (append one function)
- Test: `tests/test_reg_lineage.py` (append)

**Interfaces:**
- Consumes: annotated corpus records (`regulations`, `primary_regulation`, `regulatory_basis_status`, `circular_number`) + `regulations` list (`reg_id`, `short_name`, `year`, `status`, `superseded_by_reg`).
- Produces:
  - `build_regulatory_index(circulars: list[dict], regulations: list[dict]) -> dict[str, dict]`
  - Entry shape per circular_number:
    ```python
    {"regulatory_basis_status": str, "primary_regulation": str | None,
     "regulations": [
        {"reg_id": str, "short_name": str, "year": int | None, "status": str,
         "superseded_by": {"reg_id": str, "short_name": str, "year": int | None} | None},
        ...]}
    ```

- [ ] **Step 1: Write the failing test**

Append to `tests/test_reg_lineage.py`:

```python
from sebi_rag.reg_lineage import build_regulatory_index

_INDEX_REGS = [
    {"reg_id": "stock-brokers-1992", "short_name": "Stock Brokers", "year": 1992,
     "status": "repealed", "superseded_by_reg": "stock-brokers-2026"},
    {"reg_id": "stock-brokers-2026", "short_name": "Stock Brokers", "year": 2026,
     "status": "in_force", "superseded_by_reg": None},
    {"reg_id": "aif-2012", "short_name": "Alternative Investment Funds", "year": 2012,
     "status": "in_force", "superseded_by_reg": None},
    {"reg_id": "orphan-2009", "short_name": "Orphan", "year": 2009,
     "status": "unknown", "superseded_by_reg": None},
    {"reg_id": "no-successor-record-1999", "short_name": "No Successor Record",
     "year": 1999, "status": "repealed", "superseded_by_reg": "missing-2030"},
]


def _icirc(num, regs, primary, basis):
    return {"circular_number": num, "regulations": regs,
            "primary_regulation": primary, "regulatory_basis_status": basis}


def test_index_happy_path_resolves_successor_object():
    circs = [_icirc("C/1", ["stock-brokers-1992"], "stock-brokers-1992",
                    "repealed_basis")]
    idx = build_regulatory_index(circs, _INDEX_REGS)
    entry = idx["C/1"]
    assert entry["regulatory_basis_status"] == "repealed_basis"
    (reg,) = entry["regulations"]
    assert reg["reg_id"] == "stock-brokers-1992"
    assert reg["short_name"] == "Stock Brokers" and reg["year"] == 1992
    assert reg["status"] == "repealed"
    assert reg["superseded_by"] == {"reg_id": "stock-brokers-2026",
                                    "short_name": "Stock Brokers", "year": 2026}


def test_index_uncited_circular_is_unknown_empty():
    circs = [_icirc("C/2", [], None, "unknown")]
    entry = build_regulatory_index(circs, _INDEX_REGS)["C/2"]
    assert entry["regulatory_basis_status"] == "unknown"
    assert entry["primary_regulation"] is None
    assert entry["regulations"] == []


def test_index_missing_basis_fields_default():
    entry = build_regulatory_index([{"circular_number": "C/3"}], _INDEX_REGS)["C/3"]
    assert entry["regulatory_basis_status"] == "unknown"
    assert entry["primary_regulation"] is None
    assert entry["regulations"] == []


def test_index_dangling_reg_id_falls_back():
    circs = [_icirc("C/4", ["ghost-2000"], "ghost-2000", "unknown")]
    (reg,) = build_regulatory_index(circs, _INDEX_REGS)["C/4"]["regulations"]
    assert reg == {"reg_id": "ghost-2000", "short_name": "ghost-2000",
                   "year": None, "status": "unknown", "superseded_by": None}


def test_index_primary_is_unknown_but_a_repealed_reg_is_present():
    # basis repealed_basis; primary points at the unknown reg, not the repealed one.
    circs = [_icirc("C/5", ["orphan-2009", "stock-brokers-1992"], "orphan-2009",
                    "repealed_basis")]
    regs = build_regulatory_index(circs, _INDEX_REGS)["C/5"]["regulations"]
    by_id = {r["reg_id"]: r for r in regs}
    assert by_id["orphan-2009"]["status"] == "unknown"
    assert by_id["stock-brokers-1992"]["status"] == "repealed"
    assert by_id["stock-brokers-1992"]["superseded_by"]["reg_id"] == "stock-brokers-2026"


def test_index_repealed_with_missing_successor_record():
    circs = [_icirc("C/6", ["no-successor-record-1999"], "no-successor-record-1999",
                    "repealed_basis")]
    (reg,) = build_regulatory_index(circs, _INDEX_REGS)["C/6"]["regulations"]
    assert reg["status"] == "repealed"
    assert reg["superseded_by"] is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_reg_lineage.py -k index -v`
Expected: FAIL with `ImportError: cannot import name 'build_regulatory_index'`.

- [ ] **Step 3: Write minimal implementation**

Append to `src/sebi_rag/reg_lineage.py`:

```python
def build_regulatory_index(circulars: list[dict],
                           regulations: list[dict]) -> dict[str, dict]:
    """Per-circular regulatory-basis lookup for the query/citation layer.

    Read-only join of already-annotated corpus fields with regulations.jsonl.
    Every circular gets an entry. Never recomputes regulatory_basis_status and
    never touches validity_status/supersession_status.
    """
    by_id = {r["reg_id"]: r for r in regulations}

    def _ref(reg_id: str) -> dict:
        rec = by_id.get(reg_id)
        if rec is None:  # dangling reg_id: present on circular, absent from listing
            return {"reg_id": reg_id, "short_name": reg_id, "year": None,
                    "status": "unknown", "superseded_by": None}
        status = rec.get("status", "unknown")
        superseded_by = None
        if status == "repealed":
            succ = by_id.get(rec.get("superseded_by_reg"))
            if succ is not None:
                superseded_by = {"reg_id": succ["reg_id"],
                                 "short_name": succ.get("short_name", succ["reg_id"]),
                                 "year": succ.get("year")}
        return {"reg_id": reg_id, "short_name": rec.get("short_name", reg_id),
                "year": rec.get("year"), "status": status,
                "superseded_by": superseded_by}

    index: dict[str, dict] = {}
    for c in circulars or []:
        reg_ids = c.get("regulations") or []
        index[c["circular_number"]] = {
            "regulatory_basis_status": c.get("regulatory_basis_status") or "unknown",
            "primary_regulation": c.get("primary_regulation"),
            "regulations": [_ref(rid) for rid in reg_ids],
        }
    return index
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_reg_lineage.py -v`
Expected: PASS (all existing reg_lineage tests stay green).

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/reg_lineage.py tests/test_reg_lineage.py
git commit -m "feat(reg_lineage): build_regulatory_index join for the query layer"
```

---

### Task 3: In-text advisory note in `pipeline.py`

**Files:**
- Modify: `src/sebi_rag/pipeline.py` (add field + note block)
- Test: `tests/test_pipeline.py` (append)

**Interfaces:**
- Consumes: `build_regulatory_index` output (Task 2), `reg_display_name` (Task 1).
- Produces: `RAGPipeline.regulatory_index: dict[str, dict] | None = None`; `query()` appends a note to `ans.text` for text-referenced `repealed_basis` citations.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_pipeline.py`:

```python
def _repealed_basis_pipeline():
    """Offline pipeline whose single circular rests on a repealed regulation."""
    C = "SEBI/HO/W/P/CIR/2020/07"
    text = (f"CIRCULAR {C}. Registration norms for stock brokers under the "
            "erstwhile regulations.")
    chunks = hierarchical_chunk(text, CircularMeta(circular_number=C))
    lineage = build_lineage([{"circular_number": C, "text": text}])
    pipe = RAGPipeline.build(
        chunks=chunks, embedder=HashEmbedder(256), reranker=LexicalReranker(),
        generator=ExtractiveStubGenerator(), abstain_threshold=0.05, lineage=lineage,
    )
    pipe.regulatory_index = {
        C: {"regulatory_basis_status": "repealed_basis", "primary_regulation":
            "stock-brokers-1992", "regulations": [
            {"reg_id": "stock-brokers-1992", "short_name": "Stock Brokers",
             "year": 1992, "status": "repealed", "superseded_by": {
                 "reg_id": "stock-brokers-2026", "short_name": "Stock Brokers",
                 "year": 2026}}]}}
    return pipe, C


def test_note_fires_and_disambiguates_year():
    pipe, C = _repealed_basis_pipeline()
    ans, _ = pipe.query("What are the registration norms for stock brokers?")
    assert not ans.abstained and C in ans.text
    # names BOTH years distinctly — guards the short_name-collision bug
    assert "Stock Brokers Regulations, 1992" in ans.text
    assert "Stock Brokers Regulations, 2026" in ans.text
    assert "repealed" in ans.text.lower()


def test_note_absent_when_status_not_repealed_basis():
    pipe, C = _repealed_basis_pipeline()
    pipe.regulatory_index[C]["regulatory_basis_status"] = "mixed"
    ans, _ = pipe.query("What are the registration norms for stock brokers?")
    assert "Stock Brokers Regulations, 1992" not in ans.text


def test_note_absent_when_index_is_none():
    pipe, _ = _repealed_basis_pipeline()
    pipe.regulatory_index = None
    ans, _ = pipe.query("What are the registration norms for stock brokers?")
    assert "repealed regulation" not in ans.text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_pipeline.py -k "note_fires or note_absent" -v`
Expected: FAIL — `AttributeError: 'RAGPipeline' object has no attribute 'regulatory_index'` (or the note assertions fail).

- [ ] **Step 3: Write minimal implementation**

In `src/sebi_rag/pipeline.py`, add imports at the top (with the existing imports):

```python
from .regulations import reg_display_name
```

Add the field to the `RAGPipeline` dataclass, right after the `judge` field (`pipeline.py:22`):

```python
    regulatory_index: dict[str, dict] | None = None  # repealed-basis staleness signal
```

In `query()`, insert this block **after** the superseded-citation block (the one ending at `pipeline.py:92`) and **before** the `if not ans.abstained and ans.unsupported_citations:` block (`pipeline.py:93`):

```python
        if (self.regulatory_index is not None and not ans.abstained
                and ans.citations):
            seen, notes = set(), []
            for cit in ans.citations:
                cn = cit.split("#", 1)[0]
                if cn in seen:
                    continue
                seen.add(cn)
                entry = self.regulatory_index.get(cn)
                if (entry is None
                        or entry["regulatory_basis_status"] != "repealed_basis"
                        or cn not in ans.text):
                    continue
                for reg in entry["regulations"]:
                    if reg["status"] != "repealed":
                        continue
                    name = reg_display_name(reg["short_name"], reg["year"])
                    succ = reg["superseded_by"]
                    if succ:
                        sname = reg_display_name(succ["short_name"], succ["year"])
                        notes.append(f"{cn} rests on the {name}, which has been "
                                     f"repealed and replaced by the {sname}")
                    else:
                        notes.append(f"{cn} rests on the {name}, which has been "
                                     "repealed")
            if notes:
                ans.text += (
                    "\n\nNote: this answer cites circular(s) resting on a repealed "
                    "regulation — " + "; ".join(notes)
                    + ". Refer to the current regulation(s) for the governing "
                    "requirements."
                )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_pipeline.py -v`
Expected: PASS (existing pipeline tests, including `test_answer_flags_superseded_citation`, stay green).

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/pipeline.py tests/test_pipeline.py
git commit -m "feat(pipeline): repealed-basis in-text advisory note (year-disambiguated)"
```

---

### Task 4: API surface — models, `_citation_meta`, `build_default_pipeline`

**Files:**
- Modify: `src/sebi_rag/api.py`
- Test: `tests/test_api.py` (append)

**Interfaces:**
- Consumes: `build_regulatory_index` (Task 2), `load_regulations` (Task 1), `RAGPipeline.regulatory_index` (Task 3).
- Produces: `RegulationSuccessor`, `RegulationRef` Pydantic models; `CitationMeta` with `regulatory_basis_status: str` + `regulations: list[RegulationRef]`; `_citation_meta(citations, lineage, regulatory_index)`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_api.py`:

```python
from sebi_rag.api import _citation_meta

_API_INDEX = {
    "SEBI/HO/Z/P/CIR/2021/1": {
        "regulatory_basis_status": "repealed_basis",
        "primary_regulation": "stock-brokers-1992",
        "regulations": [{
            "reg_id": "stock-brokers-1992", "short_name": "Stock Brokers",
            "year": 1992, "status": "repealed",
            "superseded_by": {"reg_id": "stock-brokers-2026",
                              "short_name": "Stock Brokers", "year": 2026}}]},
}


def test_citation_meta_fills_regulatory_fields():
    out = _citation_meta(["SEBI/HO/Z/P/CIR/2021/1#0"], None, _API_INDEX)
    assert len(out) == 1
    m = out[0]
    assert m.regulatory_basis_status == "repealed_basis"
    assert len(m.regulations) == 1
    assert m.regulations[0].year == 1992
    assert m.regulations[0].superseded_by.year == 2026


def test_citation_meta_defaults_when_index_none():
    out = _citation_meta(["SEBI/HO/Z/P/CIR/2021/1"], None, None)
    assert out[0].regulatory_basis_status == "unknown"
    assert out[0].regulations == []


def test_citation_meta_defaults_when_circular_absent_from_index():
    out = _citation_meta(["SEBI/HO/NOT/IN/INDEX/9"], None, _API_INDEX)
    assert out[0].regulatory_basis_status == "unknown"
    assert out[0].regulations == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_api.py -k citation_meta -v`
Expected: FAIL — `_citation_meta()` takes 2 args / `RegulationRef` attributes missing.

- [ ] **Step 3: Write minimal implementation**

In `src/sebi_rag/api.py`, add the two models just before `class CitationMeta` (`api.py:47`):

```python
class RegulationSuccessor(BaseModel):
    reg_id: str
    short_name: str
    year: int | None = None


class RegulationRef(BaseModel):
    reg_id: str
    short_name: str
    year: int | None = None
    status: str
    superseded_by: RegulationSuccessor | None = None
```

Add two fields to `class CitationMeta` (`api.py:47-50`), after `superseded_by`:

```python
    regulatory_basis_status: str = "unknown"  # current|repealed_basis|mixed|unknown
    regulations: list[RegulationRef] = []
```

Replace `_citation_meta` (`api.py:131-146`) with:

```python
def _citation_meta(citations: list[str], lineage: Lineage | None,
                   regulatory_index: dict[str, dict] | None = None) -> list[CitationMeta]:
    seen, out = set(), []
    for c in citations:
        cn = c.split("#", 1)[0]
        if cn in seen:
            continue
        seen.add(cn)
        if lineage is None:
            meta = CitationMeta(circular=cn, status="unknown")
        else:
            meta = CitationMeta(
                circular=cn,
                status=lineage.status(cn),
                superseded_by=lineage.superseded_by.get(cn, []),
            )
        entry = regulatory_index.get(cn) if regulatory_index else None
        if entry is not None:
            meta.regulatory_basis_status = entry["regulatory_basis_status"]
            meta.regulations = [RegulationRef(**r) for r in entry["regulations"]]
        out.append(meta)
    return out
```

Update the call site in `query()` (`api.py:226`):

```python
            citations_meta=_citation_meta(ans.citations, p.lineage, p.regulatory_index),
```

In `build_default_pipeline` (`api.py:117-127`), after the `lineage = (...)` assignment and before the `return RAGPipeline(...)`, add:

```python
    regs_path = Path(s.corpus_path).with_name("regulations.jsonl")
    regulatory_index = None
    if regs_path.exists():
        from .reg_lineage import build_regulatory_index
        from .regulations import load_regulations
        regulatory_index = build_regulatory_index(
            load_records(s.corpus_path), load_regulations(regs_path))
```

Then add `regulatory_index=regulatory_index,` to the `RAGPipeline(...)` constructor call (`api.py:120-128`). Note `load_records` is already imported at `api.py:86`.

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_api.py -v`
Expected: PASS (all existing API tests stay green; the offline `_offline_pipeline` has `regulatory_index=None`, so `citations_meta` degrades cleanly).

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/api.py tests/test_api.py
git commit -m "feat(api): surface regulatory_basis_status + regulations in CitationMeta"
```

---

### Task 5: Gradio "Regulatory Basis" column + docs

**Files:**
- Modify: `src/sebi_rag/ui.py`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: `citations_meta[i].regulatory_basis_status` and `.regulations` from the API response (Task 4); `reg_display_name` (Task 1).
- Produces: a "Regulatory Basis" column in the citations dataframe.

- [ ] **Step 1: Update the empty-df columns and the row builder**

In `src/sebi_rag/ui.py`, change `_EMPTY_DF_COLS` (`ui.py:8`):

```python
_EMPTY_DF_COLS = ["Circular", "Status", "Superseded By", "Regulatory Basis"]
```

Add the import near the top of `ui.py` (with the other `sebi_rag` imports if any, else beside the stdlib imports):

```python
from sebi_rag.regulations import reg_display_name
```

Replace the citation-row loop (`ui.py:59-66`) with:

```python
    df_rows = []
    for item in data.get("citations_meta", []):
        superseded_by = ", ".join(item.get("superseded_by", []))
        basis = item.get("regulatory_basis_status", "unknown")
        stale = [reg_display_name(r.get("short_name", r.get("reg_id", "?")),
                                  r.get("year"))
                 for r in item.get("regulations", [])
                 if r.get("status") != "in_force"]
        basis_cell = f"{basis} ({', '.join(stale)})" if stale else basis
        df_rows.append({
            "Circular": item.get("circular"),
            "Status": item.get("status"),
            "Superseded By": superseded_by if superseded_by else "-",
            "Regulatory Basis": basis_cell,
        })
```

- [ ] **Step 2: Manual smoke check (no automated UI test in repo)**

Run: `PYTHONPATH=src .venv/bin/python -c "import sebi_rag.ui as u; print(u._EMPTY_DF_COLS)"`
Expected: `['Circular', 'Status', 'Superseded By', 'Regulatory Basis']` and no import error (confirms `reg_display_name` import resolves).

- [ ] **Step 3: Update CLAUDE.md**

In `CLAUDE.md`, in the architecture table row for `reg_lineage.py`, append to its Purpose cell: `+ build_regulatory_index (query-layer lookup)`. Under the `regulations.py` row (or `reg_citations.py` if clearer), note `load_regulations`/`reg_display_name`. Add one sentence after the pipeline description noting: "`regulatory_basis_status` is surfaced per-citation in the API (`CitationMeta.regulations`) and UI, with an in-text advisory note for `repealed_basis` circulars." Keep edits minimal and factual.

- [ ] **Step 4: Run the full suite**

Run: `PYTHONPATH=src .venv/bin/python -m pytest -q -m "not integration"`
Expected: PASS — baseline 443 passed, 3 deselected, plus the new tests from Tasks 1–4 (≈ 456 passed), **zero regressions**.

- [ ] **Step 5: Commit**

```bash
git add src/sebi_rag/ui.py CLAUDE.md
git commit -m "feat(ui): Regulatory Basis column; docs for the surfaced signal"
```

---

## Self-Review

**Spec coverage:**
- §4.1 `load_regulations` → Task 1. ✅
- §4.2 `build_regulatory_index` (entry shape, year, nested successor, dangling reg_id, missing successor) → Task 2. ✅
- §4.3 pipeline field + note (repealed-reg selection not primary, text-referenced gate, year-disambiguation, multi-reg join, None-index degrade) → Task 3. ✅
- §4.4 `RegulationSuccessor`/`RegulationRef`, `CitationMeta` fields, `_citation_meta` signature + call site, `build_default_pipeline` load → Task 4. ✅
- §4.5 UI column → Task 5. ✅
- §5 error handling: `regulations.jsonl` missing (Task 4 guard + Task 3 None test), dangling reg_id (Task 2), missing successor (Task 2), circular absent (Task 4), `#` fragment (Task 3/4 strip). ✅
- §6 testing: all enumerated tests mapped to Tasks 1–3 (`test_regulations`, `test_reg_lineage`, `test_pipeline`) and Task 4 (`test_api`). ✅
- §2 non-goals: no ranking/index/CircularMeta/Spaces/validity change — none of the five tasks touch those files. ✅

**Placeholder scan:** No TBD/TODO; every code step shows full code; CLAUDE.md step (Task 5 Step 3) describes exact cells to edit. ✅

**Type consistency:** `reg_display_name(short_name, year)` used identically in Tasks 3 and 5. Entry/`RegRef` dict shape from Task 2 matches the `RegulationRef(**r)` mapping in Task 4 (`reg_id, short_name, year, status, superseded_by`) and the `superseded_by` nested `{reg_id, short_name, year}` matches `RegulationSuccessor`. `regulatory_index` field name identical across Tasks 3/4. ✅
