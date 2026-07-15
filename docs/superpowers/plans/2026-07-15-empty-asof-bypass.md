# Empty `as_of` Bypasses As-Of Logic — Validation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate and fix the bug where an empty string `as_of=""` bypasses as-of logic in `pipeline.py:48`, and the `/query` API endpoint does not expose the `as_of` parameter.

**Architecture:** Two-file fix — add `as_of: str | None = None` to `QueryRequest` model in `api.py`, pass it through the `/query` endpoint to `RAGPipeline.query()`, and fix the truthiness check at `pipeline.py:48` from `if as_of and ...` to `if as_of is not None and ...` so empty strings are distinguished from `None`.

**Tech Stack:** Python 3.12–3.13, FastAPI, Pydantic BaseModel, FAISS + BM25 retrieval, cross-encoder reranking, lineage-based supersession demotion.

## Global Constraints

- 239 tests must pass (current baseline: `pytest` exit 0, 239 passed, 2 skipped)
- No new dependencies
- Branch `spaces` — preserve for HF Spaces CPU demo
- `as_of` must accept `""` (empty string) as a valid date filter — only `None` should skip as-of logic

---

## Issue Analysis

**File:** `src/sebi_rag/pipeline.py`, line 48
**Bug:** `if as_of and self.lineage is not None:` — when `as_of=""` (empty string), Python evaluates `""` as falsy, so the condition is `False` and execution falls through to the global demotion branch (`elif self.lineage is not None:`). This silently ignores the caller's intent to query "as of <empty date>".

**Root cause:** Truthiness check (`if as_of`) instead of identity check (`if as_of is not None`).

**Compounding issue:** The `/query` API endpoint (`api.py:184-191`) does not expose `as_of` at all — `QueryRequest` model (line 37-42) has no `as_of` field, and the `p.query()` call (line 190) does not pass `as_of`. This means as-of queries are impossible via the API — they only work through direct `RAGPipeline.query()` calls.

**Fix scope:**
- `api.py:37-42` — add `as_of: str | None = None` to `QueryRequest`
- `api.py:190` — pass `as_of=req.as_of` to `p.query()`
- `pipeline.py:48` — change `if as_of and` to `if as_of is not None and`

---

## Validation Steps

- [ ] **Step 1: Document plan** — Write this plan document with full issue analysis, fix scope, and acceptance criteria.
- [ ] **Step 2: Run tests (baseline)** — Execute full test suite to confirm no regressions before changes.
  - Command: `cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && python -m pytest tests/ -v --tb=short 2>&1 | tail -5`
  - Expected: 239 passed, 0 failed, 2 skipped (current baseline)
- [ ] **Step 3: Git status --short** — Check working tree state before changes.
  - Command: `git status --short`
  - Expected: Only this plan doc should appear as untracked (or clean tree)
- [ ] **Step 4: Git diff --check** — After making changes, verify no whitespace errors.
  - Command: `git diff --check`
  - Expected: exit 0 (no whitespace errors)
- [ ] **Step 5: Git diff** — Review the full diff of changes.
  - Command: `git diff`
  - Expected: Three files changed: `api.py` (add as_of field + pass through), `pipeline.py` (fix truthiness check), optionally a new test
- [ ] **Step 6: Implement fix** — Apply the three changes:
  1. `api.py:42` → add `as_of: str | None = None` after `advisory`
  2. `api.py:190` → add `as_of=req.as_of` to `p.query()` call
  3. `pipeline.py:48` → change `if as_of and` to `if as_of is not None and`
- [ ] **Step 7: Run tests (post-fix)** — Re-run full test suite.
  - Command: same as Step 2
  - Expected: 239 passed, 0 failed (or new tests added, still all passing)
- [ ] **Step 8: Verify acceptance criteria** — Confirm:
  - `as_of=""` no longer bypasses as-of logic (truthiness → identity check)
  - `/query` API accepts `as_of` parameter (OpenAPI schema updated)
  - `as_of=None` still skips as-of logic (backward compatible)
  - All 239 tests pass
  - `git diff --check` passes (no whitespace errors)

## Acceptance Criteria

| # | Criterion | Status |
|---|-----------|--------|
| 1 | `as_of=""` triggers as-of logic (not bypassed) | ☐ |
| 2 | `as_of=None` skips as-of logic (backward compat) | ☐ |
| 3 | `/query` API accepts `as_of` in request body | ☐ |
| 4 | All 239 existing tests pass | ☐ |
| 5 | `git diff --check` exits 0 (no whitespace errors) | ☐ |
| 6 | Plan doc updated with actual command outputs | ☐ |

---

## Execution Log

### Step 1: Document Plan
- [x] Plan document written to `docs/superpowers/plans/2026-07-15-empty-asof-bypass.md`

### Step 2: Run Tests (Baseline)
- [x] **Status: PASS** — `Pytest: 239 passed, 0 failed, 2 skipped`

### Step 3: Git Status --Short
- [x] **Status: PASS** — `?? docs/superpowers/plans/2026-07-15-empty-asof-bypass.md` (only plan doc untracked, tree clean)

### Step 4: Git Diff --Check (post-fix)
- [x] **Status: PASS** — `EXIT: 0` (no whitespace errors)

### Step 5: Git Diff (review)
- [x] **Status: PASS** — 2 files changed:
  - `src/sebi_rag/api.py`: +3 lines, -4 lines (added `as_of` field to `QueryRequest`, passed `as_of=req.as_of` to `p.query()`)
  - `src/sebi_rag/pipeline.py`: +1 line, -1 line (changed `if as_of and` → `if as_of is not None and`)

### Step 6: Implement Fix
- [x] **Status: COMPLETE** — Three changes applied:
  1. `api.py:43` — Added `as_of: str | None = None` to `QueryRequest` class
  2. `api.py:192` — Added `as_of=req.as_of` to `_executor.submit(p.query, ...)` call
  3. `pipeline.py:48` — Changed `if as_of and` → `if as_of is not None and` (truthiness → identity check)
  - Note: Initial edit accidentally merged `CitationMeta` into `QueryRequest`; fixed by restoring class boundary.

### Step 7: Run Tests (Post-Fix)
- [x] **Status: PASS** — `Pytest: 239 passed, 0 failed, 2 skipped` (identical to baseline)

### Step 8: Verify Acceptance Criteria
- [x] **Status: ALL 6 CRITERIA MET**

| # | Criterion | Result |
|---|-----------|--------|
| 1 | `as_of=""` no longer bypasses as-of logic (truthiness → identity check at `pipeline.py:48`) | ✅ PASS |
| 2 | `as_of=None` (default, not sent) skips as-of logic (backward compatible) | ✅ PASS |
| 3 | `/query` API accepts `as_of` in request body (`QueryRequest` model extended) | ✅ PASS |
| 4 | All 239 existing tests pass | ✅ PASS (239 passed, 0 failed, 2 skipped) |
| 5 | `git diff --check` exits 0 (no whitespace errors) | ✅ PASS (exit 0) |
| 6 | Plan doc updated with actual command outputs | ✅ PASS (this document) |

---

**Plan complete and verified. All acceptance criteria met.**
