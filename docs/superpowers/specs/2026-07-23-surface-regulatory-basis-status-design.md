# Surface `regulatory_basis_status` Through Retrieval / Generation — Design

**Date:** 2026-07-23
**Status:** Approved for planning
**Builds on:** `docs/superpowers/specs/2026-07-23-sebi-regulations-cross-reference-design.md`
(the layer that computed the field this design exposes)

## 1. Problem

The SEBI Regulations cross-reference layer (spec `bf0c174`, closed `c7af041`,
2026-07-23) added three additive fields to every corpus record —
`regulations`, `primary_regulation`, `regulatory_basis_status` — via
`make reg-edges`. That layer's whole purpose, in its own words, was
"exposing a regulation-repeal staleness signal the circular-to-circular
supersession graph cannot see."

The signal was computed and gated, but **it is written to the corpus JSONL and
nowhere else**. `regulatory_basis_status` appears only in `reg_lineage.py` and
on the persisted record; it is not read by `pipeline.py`, `generate.py`,
`api.py`, or `ui.py`. A verification pass on 2026-07-23 confirmed no consumer.

So a query that retrieves one of the flagged circulars gets **no** indication
its regulatory basis is stale, even though the data to say so now exists on
disk. Concretely (from `reports/2026-07-23-regulation-cross-reference-results.md`):

| `validity_status` | `regulatory_basis_status` | Circulars |
|---|---|---|
| `current` | `repealed_basis` | 29 |
| `current` | `mixed` | 45 |

**74 circulars (10.5% of the corpus)** carry a regulatory-basis signal invisible
to `validity_status`, and today it reaches no user.

## 2. Goal

Surface `regulatory_basis_status` at citation time — in the HTTP API response,
in the Gradio UI, and, for the highest-signal case, as an in-text advisory note
in the answer itself — **without** altering retrieval, the persisted index, or
the locked circular-to-circular supersession rules.

### Non-goals (explicit scope fence)

- **No retrieval-ranking impact.** No `regulatory_basis_penalty` mirroring
  `superseded_penalty`. The 2026-07-12 locked rule stands: ranking-affecting
  status derives from circular→circular `explicit_text` edges only. This is a
  presentation signal, consistent with the just-passed no-op eval gate
  (chunk payload + FAISS/BM25 index unchanged).
- **No `CircularMeta` change.** The field is not on the chunk payload and never
  will be (`hierarchical_chunk` does `meta=asdict(meta)`; a new field would
  mutate all 77.8k chunks and the index).
- **No Spaces changes.** `api_spaces.py`, `corpus_spaces.py`,
  `generate_spaces.py`, and root `app.py` are the CPU-only HF demo path and are
  out of scope (CLAUDE.md: do not edit Spaces when fixing the local pipeline).
- **No `validity_status` / `supersession_status` change.**

## 3. Approach

Approach **B** of three considered (chosen 2026-07-23):

- **A — extend `Lineage`.** Rejected. `Lineage` carries the locked
  supersession rule; bolting an unrelated signal onto it blurs a boundary the
  codebase deliberately keeps separate and raises review risk on frozen code.
- **B — new independent lookup (chosen).** A dedicated `regulatory_index`
  built alongside `lineage`, threaded through `RAGPipeline` as an additive
  optional field. Preserves the parallel-signal design intent, touches nothing
  frozen, and is cheap (dict joins over data already on disk).
- **C — thread raw corpus dicts.** Rejected. `pipeline.py::query()` and
  `api.py::_citation_meta()` don't see raw records today; C converges to the
  same new pipeline field as B, built ad hoc instead of via a named, testable
  function. Strictly worse for equal cost.

## 4. Architecture

One new stdlib loader, one new pure join function, one additive `RAGPipeline`
field, additive changes to `api.py` and `ui.py`. Data flows:

```
circulars.jsonl (already annotated by make reg-edges)
regulations.jsonl (reg_id -> short_name, status, superseded_by_reg)
        |
        v  build time, once, in build_default_pipeline()
build_regulatory_index()  ->  dict[circular_number, entry]
        |
        v  stored on the pipeline object
RAGPipeline.regulatory_index
        |
        +--> pipeline.py::query()      (in-text note, repealed_basis only)
        +--> api.py::_citation_meta()  (per-citation metadata, all statuses)
                    |
                    v
              ui.py citations table ("Regulatory Basis" column)
```

### 4.1 `regulations.py` — `load_regulations`

```python
def load_regulations(path: str | Path) -> list[dict]:
    """Load data/corpus/regulations.jsonl into a list of regulation records."""
```

Thin JSONL loader, symmetric with `lineage.load_records` and
`corpus.load_circulars`. Stdlib only.

### 4.2 `reg_lineage.py` — `build_regulatory_index`

```python
def build_regulatory_index(
    circulars: list[dict], regulations: list[dict]
) -> dict[str, dict]:
    """Per-circular regulatory-basis lookup for the query/citation layer.

    Read-only join of already-annotated corpus fields with regulations.jsonl.
    Never touches validity_status/supersession_status.
    """
```

Returns `{circular_number: entry}` for **every** circular in `circulars`, where
`entry` is:

```python
{
  "regulatory_basis_status": str,      # current | repealed_basis | mixed | unknown
  "primary_regulation": str | None,    # reg_id, verbatim from the record (internal-only)
  "regulations": [                     # one per reg_id in c["regulations"]
    {
      "reg_id": str,
      "short_name": str,               # from regulations.jsonl; falls back to reg_id
      "year": int | None,              # from regulations.jsonl; None if unresolvable
      "status": str,                   # in_force | repealed | unknown
      "superseded_by": {               # successor, populated iff status == repealed
        "reg_id": str,
        "short_name": str,
        "year": int | None,
      } | None,
    },
    ...
  ],
}
```

**Why `short_name` alone is not enough (verified against real data
2026-07-23):** `short_name` is a bare noun (`"Stock Brokers"`, `"Mutual
Funds"`), and the year lives in a separate `year: int` field. Repeal-and-replace
pairs share the same `short_name` — e.g. repealed `stock-brokers-1992` and its
successor `stock-brokers-2026` are **both** `short_name: "Stock Brokers"`. A
note built from `short_name` alone reads "…the Stock Brokers, replaced by the
Stock Brokers" — useless. Every displayed regulation name MUST be composed as
`"{short_name} Regulations, {year}"` so the year disambiguates.

Construction:
- `regulatory_basis_status` and `primary_regulation` are copied verbatim from
  the annotated record (`c.get(...)`, defaulting to `"unknown"` / `None`). This
  function does not recompute them — it is a presentation join, not logic.
  `primary_regulation` is carried for completeness/debuggability; it is NOT
  used by the note (see §4.3 step 3) and is NOT surfaced in the API (§4.4).
- `regulations` is built by resolving each `reg_id` in `c.get("regulations", [])`
  against a `by_id = {r["reg_id"]: r}` map of `regulations`. `short_name` and
  `year` come from the resolved record.
- **Dangling `reg_id`** (present on the circular but absent from
  `regulations.jsonl`): include a `RegRef` with `short_name = reg_id`,
  `year = None`, `status = "unknown"`, `superseded_by = None`. Never raise.
- **`superseded_by`** is populated only when `status == "repealed"`: read the
  reg's `superseded_by_reg` (a `str | None` successor reg_id, verified not a
  list), resolve it through `by_id` to `{reg_id, short_name, year}`. If the
  successor reg_id is missing from `by_id`, leave `superseded_by = None`
  (note degrades to naming the repealed reg only).

Invariant relied on (from the cross-reference layer, `reg_lineage.py:88`): a reg
earns `status: "repealed"` only when it has a `REG_SUCCESSION` successor, so a
`repealed` reg always has a `superseded_by_reg` to resolve, and in the common
case (verified: `mutual-funds-1996` → in-force `mutual-funds-2026`) that
successor record is present in `regulations.jsonl`.

### 4.3 `pipeline.py` — in-text note

`RAGPipeline` gains one additive field:

```python
regulatory_index: dict[str, dict] | None = None
```

In `query()`, **after** the existing supersession-note block and before the
unsupported-citation warning, add a mirrored block. Guard: run only if
`self.regulatory_index is not None and not ans.abstained and ans.citations`.

Logic (mirrors the supersession note's structure and its text-referenced gate):
1. Normalise `ans.citations` by stripping `#` fragments
   (`cn = c.split("#", 1)[0]`), dedup.
2. For each `cn`: look up `entry = self.regulatory_index.get(cn)`. Keep it iff
   `entry` exists, `entry["regulatory_basis_status"] == "repealed_basis"`,
   **and** `cn in ans.text` (verbatim, identical to the supersession gate).
3. For each kept `cn`, select its `repealed`-status regs from
   `entry["regulations"]` (NOT `primary_regulation` — primary is chosen by
   evidence tier and may point at an `unknown`-status reg even when the basis
   is `repealed_basis`).
4. Compose one note per kept circular naming the repealed reg(s) and, where
   `superseded_by` is present, the successor. Every regulation name is composed
   as `"{short_name} Regulations, {year}"` (§4.2 — year is required to
   disambiguate same-`short_name` repeal pairs). When `year is None`, fall back
   to `short_name` alone.

   > Note: this answer cites circular(s) resting on a repealed regulation —
   > `{cn}` rests on the Stock Brokers Regulations, 1992, which has been
   > repealed and replaced by the Stock Brokers Regulations, 2026. Refer to
   > the current regulation.

   When `superseded_by is None`: "…rests on the {name}, which has been
   repealed. Verify the current regulatory basis." When a circular has multiple
   repealed regs, join them in one clause (mirroring the supersession note's
   `"; ".join(...)`).
5. Append the composed text to `ans.text` (same mechanism as the supersession
   note). Do **not** add a new `Answer` field.

### 4.4 `api.py` — response surface

- **`build_default_pipeline`**: after building `lineage`, load the regulatory
  index. `load_records(s.corpus_path)` must be called explicitly here — in the
  common case `lineage.json` exists so `load_records` is *not* otherwise called.
  Guarded by existence of `regulations.jsonl` (path derived from
  `s.corpus_path`'s directory, `regulations.jsonl` sibling):

  ```python
  regs_path = Path(s.corpus_path).with_name("regulations.jsonl")
  regulatory_index = None
  if regs_path.exists():
      from .reg_lineage import build_regulatory_index
      from .regulations import load_regulations
      regulatory_index = build_regulatory_index(
          load_records(s.corpus_path), load_regulations(regs_path))
  ```

  Pass `regulatory_index=regulatory_index` into the `RAGPipeline(...)`.

- **New models**:
  - `RegulationSuccessor(BaseModel)`: `reg_id: str`, `short_name: str`,
    `year: int | None = None`.
  - `RegulationRef(BaseModel)`: `reg_id: str`, `short_name: str`,
    `year: int | None = None`, `status: str`,
    `superseded_by: RegulationSuccessor | None = None`. These mirror the
    internal index `RegRef` shape (§4.2) 1:1, so `_citation_meta` maps
    dict → model field-for-field.

- **`CitationMeta`** gains: `regulatory_basis_status: str = "unknown"` and
  `regulations: list[RegulationRef] = []`. (`primary_regulation` is NOT
  surfaced — the user chose status + full regulations list only.)

- **`_citation_meta(citations, lineage, regulatory_index)`**: for each distinct
  cited circular, when `regulatory_index` is not None and has the circular,
  fill `regulatory_basis_status` and map its `regulations` entries into
  `RegulationRef`s. When `None` or absent, defaults stand (`"unknown"`, `[]`).
  The call site at the `QueryResponse(...)` construction passes
  `p.regulatory_index`.

### 4.5 `ui.py` — citations table

The per-citation loop over `citations_meta` gains a **"Regulatory Basis"**
column. Value: the `regulatory_basis_status`; when regs are present and any is
not `in_force`, append the non-`in_force` regulation names as
`"{short_name} {year}"` in parentheses for context (e.g.
`repealed_basis (Stock Brokers 1992)`). Same mechanism as the existing
"Status" / "Superseded By" columns — no new request field, no logic.

## 5. Error handling / graceful degradation

| Condition | Behaviour |
|---|---|
| `regulations.jsonl` missing (`make reg-edges` never run) | `regulatory_index = None`; every `CitationMeta` defaults to `unknown`/`[]`; no note ever fires; no crash. Mirrors `lineage: Lineage \| None`. |
| Circular has a `reg_id` absent from `regulations.jsonl` | `RegRef` with `short_name=reg_id`, `status="unknown"`, `superseded_by=None`. No raise. |
| `repealed` reg whose successor reg_id is missing | `superseded_by=None`; note degrades to "…has been repealed." |
| Cited circular absent from `regulatory_index` | Treated as `unknown`; no note. |
| Citation carries a `#chunk` fragment | Stripped via `split("#", 1)[0]` before lookup (matches `superseded_citations`). |

## 6. Testing

All new tests run under `-m "not integration"` (stdlib-only modules).

- **`test_regulations.py`** — `load_regulations` round-trips a temp JSONL.
- **`test_reg_lineage.py`** — `build_regulatory_index`:
  - happy path: `repealed_basis` circular yields regs with `superseded_by`
    resolved to `{reg_id, short_name, year}`;
  - uncited circular → `unknown` / `None` / `[]`;
  - dangling `reg_id` → `RegRef` with `short_name==reg_id`, `year is None`,
    `status=="unknown"`;
  - **`primary_regulation` is an `unknown`-status reg while basis is
    `repealed_basis`** (guards §4.3 step 3 — note must select repealed regs,
    not primary);
  - repealed reg with missing successor record → `superseded_by is None`.
- **`test_pipeline.py`** — with a fixture `regulatory_index`:
  - note fires for a `repealed_basis` circular whose number is in `ans.text`,
    and names the successor;
  - **year-disambiguation regression guard**: a repealed reg and its successor
    that share a `short_name` (e.g. Stock Brokers 1992 → 2026) produce a note
    naming both years distinctly — asserts the note is NOT "…Stock Brokers …
    replaced by the Stock Brokers" (the bug this fix prevents);
  - note does **not** fire when the circular number is absent from `ans.text`;
  - note does **not** fire for `current` / `mixed` / `unknown`;
  - `regulatory_index=None` → no note, no error.
- **`test_api.py`** — `CitationMeta` carries the new fields when the index is
  present; degrades to `unknown`/`[]` when the pipeline's index is `None`.

`make test` must stay green (baseline 443 passed, 3 deselected) with the new
tests added and **zero regressions**. No `bench-retrieval` / `eval-asof` re-run
needed: chunk payload and persisted index are untouched by construction (§2).

## 7. Files

| File | Change |
|---|---|
| `src/sebi_rag/regulations.py` | + `load_regulations` |
| `src/sebi_rag/reg_lineage.py` | + `build_regulatory_index` |
| `src/sebi_rag/pipeline.py` | + `regulatory_index` field; in-text note block |
| `src/sebi_rag/api.py` | load index in `build_default_pipeline`; `RegulationRef`; `CitationMeta` fields; `_citation_meta` signature |
| `src/sebi_rag/ui.py` | + "Regulatory Basis" column |
| `tests/test_regulations.py` | + `load_regulations` test |
| `tests/test_reg_lineage.py` | + `build_regulatory_index` tests |
| `tests/test_pipeline.py` | + note-firing tests |
| `tests/test_api.py` | + `CitationMeta` field / degrade tests |
| `CLAUDE.md` | note that the field is now surfaced (if warranted) |
