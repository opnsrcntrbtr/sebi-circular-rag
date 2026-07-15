# /ready Endpoint Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix `/ready` endpoint so it returns `{"ready": true}` after the pipeline is built, instead of always returning `{"ready": false}` until the first `/query` call.

**Architecture:** The `pipe()` helper (api.py:152-155) lazily builds the RAG pipeline on first invocation. The `/ready` endpoint (api.py:171-173) checks `"p" in state` without calling `pipe()`, so it always returns `{"ready": false}` until some other route triggers `pipe()`. The fix: make `/ready` call `pipe()` so it triggers eager pipeline initialization, matching the existing `/health` endpoint's pattern.

**Tech Stack:** Python 3.12, FastAPI, pytest

## Global Constraints

- All 239 existing tests must continue to pass (0 regressions)
- `git diff --check` must exit 0 (no whitespace errors)
- Branch `spaces` must remain clean (only plan doc + fix changes)
- Follow established patterns: `/health` already calls `pipe()` eagerly (api.py:177)

---

### Task 1: Implement /ready fix + test

**Files:**
- Modify: `src/sebi_rag/api.py:171-173`
- Test: `tests/test_api.py` (append ready test)

**Interfaces:**
- Consumes: `pipe()` helper (api.py:152-155), returns `dict` with `"ready": bool`
- Produces: `/ready` endpoint that triggers pipeline build and returns `{"ready": true}` after first call

- [x] **Step 1: Write failing test for /ready**

Test appended to `tests/test_api.py:137-142` (corrected fixture from `client: TestClient` to local `TestClient(create_app(_offline_pipeline))` matching existing pattern):

```python
def test_ready_triggers_pipeline() -> None:
    """/ready should trigger pipeline build and return ready=true."""
    c = TestClient(create_app(_offline_pipeline))
    resp = c.get("/ready")
    assert resp.status_code == 200
    assert resp.json() == {"ready": True}
```

This test FAILS because the current `/ready` returns `{"ready": false}`.

- [x] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_api.py::test_ready_triggers_pipeline -v`
Result: FAILED — `AssertionError: assert {'ready': False} == {'ready': True}`

- [x] **Step 3: Write minimal implementation**

Added single line to api.py:172:

```python
    @app.get("/ready")
    def ready() -> dict:
        pipe()  # trigger eager pipeline build so readiness probe works immediately
        return {"ready": "p" in state}
```

This is the minimal change: call `pipe()` before the check, so the first call builds the pipeline and `"p" in state` is True.

- [x] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_api.py::test_ready_triggers_pipeline -v`
Result: PASSED (11.91s)

- [x] **Step 5: Run full test suite**

Run: `.venv/bin/python -m pytest tests/ -x --tb=short -q`
Result: 240 passed, 2 skipped in 43.34s (new test included, 0 regressions)

- [x] **Step 6: Git whitespace + diff check**

```
$ git diff --check
(exit 0 — no whitespace errors)

$ git status --short
 M src/sebi_rag/api.py
 M tests/test_api.py
?? docs/superpowers/plans/2026-07-15-ready-endpoint-fix.md

$ git diff src/sebi_rag/api.py tests/test_api.py
 src/sebi_rag/api.py | 1 +
 tests/test_api.py   | 8 ++++++++
 2 files changed, 9 insertions(+)
```

- [x] **Step 7: Verify acceptance criteria**

Checklist:
- [x] `/ready` returns `{"ready": true}` on first call (triggers pipeline build)
- [x] All 240 tests pass (239 existing + 1 new, 2 skipped)
- [x] `git diff --check` exits 0 (no trailing whitespace / missing newlines)
- [x] Working tree clean except for api.py, test_api.py, and plan doc
- [x] No new dependencies added
- [x] Pattern matches existing `/health` endpoint (both call `pipe()`)

- [x] **Step 8: Commit**

```
$ git add src/sebi_rag/api.py tests/test_api.py
$ git commit -m "fix: /ready endpoint triggers pipeline build (eager init)
...
83a6ebe
```
