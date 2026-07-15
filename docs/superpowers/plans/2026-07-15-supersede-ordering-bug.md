# Supersede Ordering Bug Fix

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix `detect_relations_ex()` in `lineage.py` so that a circular is classified as "supersedes" when ANY of its references appear after ANY supersede trigger word — not just after the first trigger.

**Architecture:** The bug is a single-function logic error in `lineage.py:detect_relations_ex()`. Change `first_sup` (min position) to `sup_positions` (all positions), then check `any(p > s for p in pos_list for s in sup_positions)` instead of `any(p > first_sup for p in pos_list)`.

**Tech Stack:** Python 3.12+, pytest, regex (stdlib `re`).

## Global Constraints

- No new dependencies — stdlib `re` only.
- `detect_relations()` (tuple wrapper on line 63-66) must remain unchanged — it delegates to `detect_relations_ex()` via dict unpacking.
- All 20 existing tests in `tests/test_lineage.py` must continue to pass.
- DRY: one test covers the bug; no regression test scaffolding needed.

---

## Root Cause

`lineage.py:40` captures only the **first** supersede trigger position:

```python
first_sup = min((m.start() for m in SUPERSEDE_RE.finditer(text)), default=None)
```

Then `lineage.py:47` checks if any reference appears after **that first** trigger:

```python
if first_sup is not None and any(p > first_sup for p in pos_list):
```

**Bug scenario:** A circular text contains a supersede trigger word (e.g., "supersedes") but ALL referenced circular numbers appear **before** the trigger text. Example:

```
"SEBI/HO/OLD/2020/1 dated Jan 1, 2020. This circular supersedes SEBI/HO/OLD/2020/1."
```

Here the reference `SEBI/HO/OLD/2020/1` appears at position ~4 (before "supersedes" at ~40). `first_sup` = ~40, reference pos = ~4. `any(p > first_sup)` = False → falls through to "references" instead of "supersedes".

## Fix

Replace `first_sup` with `sup_positions` (all trigger positions). Check if any reference position is after any supersede trigger position.

---

### Task 1: Write failing test for supersede-ordering bug

**Files:**
- Modify: `tests/test_lineage.py`

**Interfaces:**
- Consumes: `detect_relations_ex(circular_number: str, text: str) -> list[dict]`
- Produces: test case that fails with current code, passes with fix

- [ ] **Step 1: Write the failing test**

Append to `tests/test_lineage.py` (after line 296):

```python
def test_detect_relations_ex_supersedes_when_ref_before_trigger():
    """A circular that names itself (or another) BEFORE the supersede trigger
    word must still be classified as 'supersedes', not 'references'.

    Root cause: detect_relations_ex() tracks only the FIRST supersede trigger
    position (line 40: first_sup = min(...)) and checks whether any reference
    position exceeds that single point.  When a reference appears before the
    trigger text, the check fails and the relation is misclassified as
    'references'.

    Example text: the referenced circular number appears at char ~4, but
    'supersedes' appears at char ~40.  The old code sees 4 < 40 and falls
    through to 'references'.
    """
    from sebi_rag.lineage import detect_relations_ex

    # The referenced circular number appears BEFORE the trigger word "supersedes"
    text = (
        "Reference SEBI/HO/IMD/DF2/CIR/P/2021/024 dated March 15, 2021. "
        "This circular supersedes the above cited circulars with immediate effect."
    )
    rels = detect_relations_ex(
        "SEBI/HO/IMD/DF2/CIR/P/2024/031", text
    )

    # Must classify as supersedes, NOT references
    sup = [r for r in rels if r["relation"] == "supersedes"]
    assert len(sup) >= 1, (
        f"Expected 'supersedes' relation when reference appears before "
        f"trigger word, got: {rels}"
    )
    assert sup[0]["target"] == "SEBI/HO/IMD/DF2/CIR/P/2021/024"
    assert sup[0]["extractor"] == "regex:SUPERSEDE_RE"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && python -m pytest tests/test_lineage.py::test_detect_relations_ex_supersedes_when_ref_before_trigger -v`

Expected: FAIL with assertion error — `Expected 'supersedes' relation when reference appears before trigger word, got: [{'relation': 'references', ...}]`

- [ ] **Step 3: Commit test**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
git add tests/test_lineage.py
git commit -m "test: add supersede-ordering regression (ref before trigger word)"
```

### Task 2: Fix detect_relations_ex() to track all supersede positions

**Files:**
- Modify: `src/sebi_rag/lineage.py:35-60`

**Interfaces:**
- Consumes: `SUPERSEDE_RE` (line 23-27), `REF_RE` (imported from `ingest_pdf`)
- Produces: `detect_relations_ex()` that correctly classifies "supersedes" when ANY reference appears after ANY supersede trigger

- [ ] **Step 1: Replace first_sup with sup_positions**

Replace lines 40-48 in `src/sebi_rag/lineage.py` with:

```python
    sup_positions = [m.start() for m in SUPERSEDE_RE.finditer(text)]
    amd_pos = [m.start() for m in AMEND_RE.finditer(text)]

    out: list[dict] = []
    for ref, pos_list in positions.items():
        if ref == circular_number:
            continue
        if sup_positions and any(p > s for p in pos_list for s in sup_positions):
            pos = next(p for p in pos_list if any(p > s for s in sup_positions))
            out.append({"relation": "supersedes", "target": ref,
                        "evidence": _window(text, pos),
                        "extractor": "regex:SUPERSEDE_RE"})
```

Key changes:
1. Line 40: `first_sup = min(..., default=None)` → `sup_positions = [m.start() for m in SUPERSEDE_RE.finditer(text)]` — captures ALL trigger positions
2. Line 47: `first_sup is not None and any(p > first_sup for p in pos_list)` → `sup_positions and any(p > s for p in pos_list for s in sup_positions)` — checks if ANY reference is after ANY trigger
3. Line 48: `next(p for p in pos_list if p > first_sup)` → `next(p for p in pos_list if any(p > s for s in sup_positions))` — picks the first reference after any trigger

- [ ] **Step 2: Run all lineage tests to verify no regression**

Run: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && python -m pytest tests/test_lineage.py -v`

Expected: All 21 tests pass (20 existing + 1 new)

- [ ] **Step 3: Run full test suite**

Run: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && python -m pytest tests/ -x -q`

Expected: All tests pass (no regression in other modules)

- [ ] **Step 4: Commit fix**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
git add src/sebi_rag/lineage.py tests/test_lineage.py
git commit -m "fix: classify supersedes when any ref appears after any trigger

Old code tracked only the first supersede trigger position (first_sup =
min(...)) and checked whether any reference exceeded that single point.
When a referenced circular number appeared before the trigger word
(e.g., 'Reference SEBI/.../2021/024. This circular supersedes ...'),
the reference was misclassified as 'references' instead of 'supersedes'.

Fix: track all supersede trigger positions and check whether any
reference position exceeds any trigger position."
```

---

## Self-Review Checklist

1. **Spec coverage:** Bug description → Task 1 test covers the exact scenario. Fix → Task 2 replaces the buggy logic. ✓
2. **Placeholder scan:** No "TBD", "TODO", "add validation", "similar to" patterns found. Every step has complete code. ✓
3. **Type consistency:** `detect_relations_ex()` signature unchanged (`str, str) -> list[dict]`. `detect_relations()` delegate unchanged. ✓
4. **Edge cases:** Empty text (no triggers) → `sup_positions = []` → falsy → falls to "references" (correct). Text with only references, no triggers → `sup_positions = []` → "references" (correct). Multiple triggers, refs between them → `any(p > s for s in sup_positions)` catches refs after any trigger (correct). ✓
5. **Existing tests:** `test_plain_citation_is_not_supersession` (line 91-97) tests a citation WITHOUT trigger words → stays "references". `test_detect_relations_ex_evidence_and_extractor` (line 187-195) tests a reference AFTER the trigger → stays "supersedes". Both remain valid. ✓

---

**Plan complete and saved to `docs/superpowers/plans/2026-07-15-supersede-ordering-bug.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
