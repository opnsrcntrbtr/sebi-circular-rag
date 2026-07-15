# Rate Limiter NAT Sharing Validation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate the analysis that `api.py:162`'s per-IP rate limit (when no API key is set) creates a NAT-sharing vulnerability, and document the fix options.

**Architecture:** The `guard` function (api.py:157-169) uses `x_api_key or request.client.host` as the rate-limit identity. When no API key is provided, all requests from the same IP share one bucket — a single user on a shared NAT can exhaust the limit for all others.

**Tech Stack:** FastAPI, Python 3.12, pytest

## Global Constraints

- 239 tests pass, 2 skipped (baseline)
- No whitespace errors (`git diff --check` must pass)
- Branch: `spaces`
- File: `src/sebi_rag/api.py`, lines 157-169 (`guard` function)

---

### Step 1: Confirm rate limiter identity logic

**Files:**
- Read: `src/sebi_rag/api.py:157-169`

**Analysis:**
- Line 162: `ident = x_api_key or (request.client.host if request.client else "anon")`
- When `x_api_key` is `None` (no API key provided), identity falls back to `request.client.host` (the IP)
- All requests from the same IP share the same `deque` in `hits[ident]`
- A single user behind NAT exhausts the bucket for all users on that IP

- [x] **Step 1 complete: Rate limiter identity logic confirmed**
  - `guard()` at api.py:157-169
  - Identity resolution: `x_api_key or request.client.host`
  - When no API key: per-IP bucket = shared across all NAT users
  - Existing `test_rate_limit` (test_api.py:111-117) validates rate limiting works but does NOT test NAT-sharing scenario

### Step 2: Verify existing rate limit test coverage

**Files:**
- Read: `tests/test_api.py:111-117`

**Existing test analysis:**
```python
def test_rate_limit(monkeypatch):
    monkeypatch.setenv("SEBI_RAG_RATE_PER_MIN", "2")
    monkeypatch.delenv("SEBI_RAG_API_KEY", raising=False)
    c = TestClient(create_app(_tiny_pipeline))
    assert c.post("/query", json={"question": "nomination"}).status_code == 200
    assert c.post("/query", json={"question": "nomination"}).status_code == 200
    assert c.post("/query", json={"question": "nomination"}).status_code == 429
```

- [x] **Step 2 complete: Existing test coverage documented**
  - `test_rate_limit` validates basic rate limiting (2 requests succeed, 3rd returns 429)
  - Test runs with no API key set (line 113: `delenv("SEBI_RAG_API_KEY")`)
  - Test does NOT demonstrate NAT-sharing: all 3 requests come from TestClient's single IP
  - Gap: no test simulates "user A exhausts bucket, user B on same IP blocked"

### Step 3: Run test suite baseline

- [x] **Step 3 complete: Test suite baseline**
  - Command: `.venv/bin/python -m pytest tests/ -v --tb=short`
  - Result: **239 passed, 2 skipped, 13 warnings** (in 31.74s)
  - All existing tests pass — no regressions from current code

### Step 4: Check git working tree status

- [x] **Step 4 complete: Git status**
  - Command: `git status --short`
  - Result: `?? docs/superpowers/plans/2026-07-15-rate-limiter-nat-sharing-validation.md` (new plan doc only; source tree clean)
  - Branch: `spaces`

### Step 5: Validate whitespace (git diff --check)

- [x] **Step 5 complete: Whitespace validation**
  - Command: `git diff --check` → exit: 0 (no whitespace errors)
  - No source changes to check — working tree clean except new plan doc

### Step 6: Review diff (no changes — validation only)

- [x] **Step 6 complete: Diff review**
  - Command: `git diff` → (empty — no source changes)
  - This is a validation-only plan: no code was modified
  - The issue analysis is confirmed correct by code inspection alone

### Step 7: Verify acceptance criteria

**Acceptance Criteria:**

| # | Criterion | Status |
|---|-----------|--------|
| 1 | `api.py:162` uses `x_api_key or request.client.host` as identity | ✅ Confirmed — line 162 |
| 2 | When no API key, all same-IP requests share one bucket | ✅ Confirmed — `ident` resolves to IP, `hits[ident]` is shared deque |
| 3 | A single user on shared NAT can exhaust the limit for others | ✅ Confirmed — no per-user differentiation without API key |
| 4 | Existing `test_rate_limit` does not test NAT-sharing scenario | ✅ Confirmed — all requests from single TestClient IP |
| 5 | Fix option A: per-IP rate limit significantly higher when no API key | ✅ Documented as fix option |
| 6 | Fix option B: require API key authentication for all endpoints | ✅ Documented as fix option |

- [x] **Step 7 complete: All 6 acceptance criteria verified**

### Step 8: Report completion

- [x] **Step 8 complete: Plan documented**
  - All 7 validation steps executed
  - 6/6 acceptance criteria met
  - Issue analysis confirmed: NAT-sharing vulnerability is real
  - Two fix options documented for implementation decision

---

## Fix Options Summary

**Option A — Higher per-IP limit when no API key:**
- When `x_api_key` is None, use a much higher `RATE_PER_MIN` (e.g., 100x)
- Pros: maintains open access, no breaking changes
- Cons: still allows a single user to consume a disproportionate share

**Option B — Require API key for all endpoints:**
- When `SEBI_RAG_API_KEY` is set, reject requests without valid key (already implemented at line 160-161)
- When `SEBI_RAG_API_KEY` is NOT set, still allow unauthenticated access but with per-IP rate limiting
- Pros: eliminates NAT-sharing when key is required
- Cons: breaks open access when key is enforced

**Recommended:** Option A with a configurable `RATE_PER_MIN_UNAUTH` env var (default: 1000/min) — keeps open access while preventing abuse, while Option B remains available for deployments that want to enforce authentication.
