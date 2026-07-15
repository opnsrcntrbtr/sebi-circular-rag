# API Blocking fut.result() Inside Sync Handler — Validation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate the issue analysis that `fut.result()` inside the sync `/query` handler blocks the FastAPI threadpool, exhausts the max_workers=2 executor, and blocks on first-query model loading.

**Architecture:** The `/query` endpoint (api.py:184-210) is a synchronous FastAPI handler. It submits work to a `ThreadPoolExecutor(max_workers=2)` (api.py:145) and blocks on `fut.result(timeout=budget)` (api.py:193). This means the FastAPI threadpool thread is blocked waiting for the future, and the custom executor can be exhausted, causing all subsequent requests to queue up. If model loading is slow (first query), the thread is blocked for the entire duration.

**Tech Stack:** Python, FastAPI, ThreadPoolExecutor, pytest, git

## Global Constraints

- `max_workers=2` is a hard concurrency limit — documented and validated
- All verification must use fresh command output — no extrapolation
- Plan document is the single source of truth for acceptance criteria
- Every step must show actual command output with exit codes

---

### Task 1: Baseline Test Suite

**Files:**
- Read: `src/sebi_rag/api.py:145-210`
- Read: `tests/test_api.py`

**Interfaces:**
- Consumes: existing test infrastructure (TestClient, create_app)
- Produces: test pass/fail baseline count

- [x] **Step 1: Run the full test suite to establish a baseline**

Run:
```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && python -m pytest tests/ -v --tb=short 2>&1 | tail -20
```

Expected: All existing tests pass (239 passed, 2 deselected — matching prior session baseline). Record the exact pass/fail count and any failures.

- [x] **Step 2: Record the test baseline in the plan document**

Append to this plan doc under a "Test Baseline" section:
```
Test Baseline: <count> passed, <count> failed, <count> deselected
Exit code: <N>
```

---

### Task 2: Git Status Validation

**Files:**
- `src/sebi_rag/api.py` (current state)

**Interfaces:**
- Consumes: current working tree state
- Produces: clean status confirmation (no unexpected changes)

- [x] **Step 3: Check git status is clean (no unexpected changes)**

Run:
```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && git status --short
```

Expected: Empty output (working tree clean) or only expected untracked files. No modified files other than what we intentionally change.

- [x] **Step 4: Record git status result**

Append to this plan doc:
```
Git Status: <output or "clean">
```

---

### Task 3: Diff Validation

**Files:**
- `src/sebi_rag/api.py`

**Interfaces:**
- Consumes: any changes made during validation
- Produces: whitespace-clean diff confirmation

- [x] **Step 5: Check diff has no whitespace errors**

Run:
```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && git diff --check 2>&1; echo "EXIT:$?"
```

Expected: Exit code 0, no whitespace error lines output. If any trailing whitespace or tabs before spaces exist, they will be reported.

- [x] **Step 6: Show the full diff for review**

Run:
```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG" && git diff
```

Expected: Shows all changes made during this validation session. Record the diff output (insertions/deletions count).

---

### Task 4: Acceptance Criteria Verification

**Files:**
- `src/sebi_rag/api.py:145,184-210`

**Interfaces:**
- Consumes: results from Tasks 1-3
- Produces: pass/fail on each acceptance criterion

- [x] **Step 7: Verify acceptance criteria**

Check each criterion against the evidence gathered:

| # | Criterion | Evidence Source | Pass/Fail |
|---|-----------|----------------|-----------|
| AC1 | `max_workers=2` is set at api.py:145 | Read api.py line 145 | [ ] |
| AC2 | `_executor.submit()` called at api.py:190 | Read api.py line 190 | [ ] |
| AC3 | `fut.result(timeout=budget)` blocks the calling thread | Read api.py line 193 | [ ] |
| AC4 | Handler is synchronous (no `async` keyword on `query()`) | Read api.py line 185 | [ ] |
| AC5 | All existing tests pass (no regression) | Task 1 output | [ ] |
| AC6 | Git working tree is clean before validation | Task 2 output | [ ] |
| AC7 | No whitespace errors in current diff | Task 3 output | [ ] |
| AC8 | Issue analysis accurately describes the blocking pattern | Manual verification | [ ] |

For each criterion:
- State the evidence (quote the relevant code or command output)
- Mark [x] for pass or [ ] for fail
- If any criterion fails, document what needs to change

- [x] **Step 8: Report completion in this plan document**

Append a "Validation Results" section with:
```
## Validation Results

Test Baseline: <count> passed, <count> failed
Git Status: <clean or listing>
Whitespace Check: exit <N>, <errors or "clean">
Diff: <N> insertions(+), <M> deletion(s)(-)

### Acceptance Criteria
- [x] AC1: <evidence>
- [x] AC2: <evidence>
...

### Conclusion
<One-paragraph summary: issue analysis confirmed or refuted, with reasoning>
```

---

## Acceptance Criteria Summary

The issue analysis is **validated** when:
1. All 8 acceptance criteria pass (marked [x])
2. Test suite shows no regression (all existing tests pass)
3. Git status is clean (no unexpected modifications)
4. Diff has zero whitespace errors
5. The blocking pattern is confirmed by reading api.py:145, 190, 193

The issue analysis is **refuted** when:
- Any acceptance criterion fails with evidence, OR
- Tests show a regression introduced by the current code state

---

## Execution Results

> **Completed: 2026-07-15**

### Test Baseline (Task 1, Step 1)
- **239 passed, 0 failed, 2 skipped** — all tests pass, no regressions
- Command: `python -m pytest tests/ -v --tb=short 2>&1 | tail -25`
- Output: `Pytest: 239 passed, 0 failed, 2 skipped`

### Git Status (Task 2, Step 3)
- **Clean** — working tree clean (only new untracked plan file)
- Command: `git status --short`
- Output: `?? docs/superpowers/plans/2026-07-15-api-blocking-fut-result-validation.md` (only the plan file itself)

### Whitespace Check (Task 3, Step 5)
- **Exit 0, no whitespace errors** — `git diff --check` passed cleanly
- Command: `git diff --check 2>&1; echo "EXIT:$?"`
- Output: `EXIT:0`

### Diff (Task 3, Step 6)
- **No changes** — validation-only session, no code modifications
- Command: `git diff`
- Output: (empty — no tracked file changes)

### Acceptance Criteria (Task 4, Step 7)

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| AC1 | `max_workers=2` at api.py:145 | `_executor = ThreadPoolExecutor(max_workers=2)` | ✅ |
| AC2 | `_executor.submit()` at api.py:190 | `fut = _executor.submit(p.query, req.question, top_k=top_k, advisory=req.advisory)` | ✅ |
| AC3 | `fut.result(timeout=budget)` blocks | `ans, retrieved = fut.result(timeout=budget)` on line 193 | ✅ |
| AC4 | Handler is synchronous | `def query(req: QueryRequest, _: None = Depends(guard))` — no `async` keyword | ✅ |
| AC5 | All existing tests pass | 239 passed, 0 failed, 2 skipped | ✅ |
| AC6 | Git working tree clean | `git status --short` — only new plan file | ✅ |
| AC7 | No whitespace errors | `git diff --check` exit 0 | ✅ |
| AC8 | Issue analysis accurately describes blocking pattern | Confirmed: sync handler blocks FastAPI thread on `fut.result()`, executor max_workers=2 is a hard concurrency limit, first-query model load blocks entire thread | ✅ |

### Conclusion (Task 4, Step 8)

**Issue analysis CONFIRMED.** The `/query` handler at `api.py:185-210` is synchronous and blocks the FastAPI threadpool thread on `fut.result(timeout=budget)` (line 193). The `ThreadPoolExecutor(max_workers=2)` at line 145 imposes a hard concurrency limit of 2. When both worker slots are occupied (e.g., by a slow first-query model load), all subsequent requests queue at the FastAPI level, causing cascading latency. The fix options are: (a) make the handler `async` and use `asyncio.to_thread()`, (b) increase `max_workers` with proper queue management, or (c) at minimum, document that `max_workers=2` is a hard concurrency limit.

Co-Authored-By: Claude <noreply@anthropic.com>
