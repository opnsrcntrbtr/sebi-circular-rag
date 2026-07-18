# Glossary Winding-Down Expansion (Part A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the probes answer-level gate (4 → ≤ 3) by adding three corpus-grounded lay→statutory glossary entries so the BM25 leg can reach the folded CRA chunk that probe-par-03 needs.

**Architecture:** Extend the existing `GLOSSARY` dict in `src/sebi_rag/expand.py` (intervention #2 mechanism: deterministic, additive, sparse-leg-only query expansion — the dense leg keeps the raw query, the index is untouched). Validation is benchmark-only against the current index: no reindex, so the measure cycle is minutes, not hours.

**Tech Stack:** Python 3.12 (uv-managed venv), pytest, existing benchmark scripts `scripts/bench_retrieval.py` and `scripts/analysis/extract_misses.py`.

**Spec:** `docs/superpowers/specs/2026-07-18-glossary-winding-expansion-design.md` (approved). Part B (HyDE) is explicitly out of scope for this plan.

## Global Constraints

- Deterministic query-side change only — no LLM, no new dependencies, **no reindex** (`data/index/` untouched).
- New glossary entries exactly as specified: `"winding": ("surrender", "wound-up", "cancellation")`, `"wind": ("surrender", "wound-up")`, `"pull": ("withdraw",)` — corpus-grounded, never probe-fitted.
- Never overwrite existing run dirs (`ft-*`, `iv-final-*`, `iv2-*`, `iv6-*`); new runs go to `eval/runs/iv7-probes/` and `eval/runs/iv7-golden/`.
- `make test` green after every task (262 currently passing; 265 after Task 1's three new tests).
- After modifying source code, run `graphify update .` before committing (project rule).
- All commands run from repo root: `/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG`. Use `uv run python …` or `.venv/bin/python …` — bare `python` lacks the project deps.

---

### Task 1: Glossary entries for winding-down vocabulary (TDD)

**Files:**
- Modify: `src/sebi_rag/expand.py:16-40` (append three entries to `GLOSSARY`)
- Test: `tests/test_expand.py` (append three tests after `test_all_five_sparse_failure_queries_expand`, before the HybridRetriever wiring section)

**Interfaces:**
- Consumes: `expand_query(query: str, glossary: dict[str, tuple[str, ...]] = GLOSSARY) -> str` — unchanged; keys are single lowercase tokens, values are tuples of statutory synonyms.
- Produces: no signature change; behavioral only — queries containing "winding", "wind", or "pull" now gain statutory synonyms on the sparse leg. Task 2 relies on nothing else.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_expand.py` immediately after `test_all_five_sparse_failure_queries_expand` (keep the HybridRetriever wiring section below it intact):

```python
def test_winding_down_gains_surrender_vocabulary():
    # probe-par-03: SEBI says "winding down" for KRAs/AIFs but
    # "surrender/cancellation of certificate of registration" for CRAs.
    q = ("When a rating agency is winding down its business, can companies "
         "pull their ongoing rating assignments?")
    out = expand_query(q)
    assert out.startswith(q)
    assert "surrender" in out
    assert "withdraw" in out


def test_wind_down_phrasing_expands():
    out = expand_query("what must a CRA do when it decides to wind down")
    assert "surrender" in out


def test_pull_maps_to_withdraw():
    out = expand_query("can clients pull their mandates")
    assert "withdraw" in out
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `uv run pytest tests/test_expand.py -v`
Expected: the three new tests FAIL (`assert "surrender" in out` — no glossary key matches, so `expand_query` returns the query unchanged). All 8 pre-existing tests PASS. If a new test passes here, stop and check for a colliding glossary key before implementing.

- [ ] **Step 3: Add the glossary entries**

In `src/sebi_rag/expand.py`, extend `GLOSSARY` by inserting before the closing brace (after the `"broking": ("broker", "brokers"),` entry):

```python
    # probe-par-03: "winding down / pull assignments" vs corpus
    # "surrender/cancellation of certificate of registration;
    # withdraw assignment". Corpus-wide counts: winding 304, surrender 603,
    # wound 108 — SEBI's own vocabulary split across intermediary types.
    "winding": ("surrender", "wound-up", "cancellation"),
    "wind": ("surrender", "wound-up"),
    "pull": ("withdraw",),
```

No other code changes — `expand_query` already handles multi-entry appends and dedup.

- [ ] **Step 4: Run the expand tests to verify green**

Run: `uv run pytest tests/test_expand.py -v`
Expected: all 11 tests PASS (8 pre-existing + 3 new).

- [ ] **Step 5: Full test suite**

Run: `make test`
Expected: 265 passed (262 previous + 3 new), 0 failures.

- [ ] **Step 6: Update the knowledge graph and commit**

```bash
graphify update .
git add src/sebi_rag/expand.py tests/test_expand.py graphify-out
git commit -m "feat: glossary entries bridging winding-down to surrender vocabulary (probe-par-03)"
```

---

### Task 2: iv7 re-measurement against gates, report update

**Files:**
- Output: new run dirs `eval/runs/iv7-probes/`, `eval/runs/iv7-golden/` (no index rebuild)
- Modify: `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md` (append §5.2 after §5.1)

**Interfaces:**
- Consumes: Task 1's committed glossary change; `scripts/bench_retrieval.py --golden <jsonl> --out <dir>`; `scripts/analysis/extract_misses.py --run <trec> --golden <jsonl> --out <jsonl> --source <label>`.
- Produces: the measured verdict against the spec's gates, recorded in report §5.2.

- [ ] **Step 1: Run both benchmarks and classify misses**

No reindex — the index is unchanged; only the sparse-leg query text changed.

```bash
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/probes/probes_v1.jsonl --out eval/runs/iv7-probes

HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/golden/golden_v6.jsonl --out eval/runs/iv7-golden

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv7-probes/run.trec --golden eval/probes/probes_v1.jsonl \
  --out eval/runs/iv7-probes/failures.jsonl --source probes_v1

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv7-golden/run.trec --golden eval/golden/golden_v6.jsonl \
  --out eval/runs/iv7-golden/failures.jsonl --source golden_v6
```

Expected gates (report actual numbers verbatim whether or not met):
- probes answer-level failures (`answer_candidate_miss + answer_ranked_low`) ≤ 3 (from 4) — probe-par-03 is the target;
- golden answer-level failures ≤ 3 and `recall_at_10` ≥ 0.956;
- no previously-passing probe or golden item newly fails (compare `failures.jsonl` IDs against `eval/runs/iv6-*/failures.jsonl` — any new ID = regression, stop and investigate before reporting).

- [ ] **Step 2: Full test suite**

Run: `make test`
Expected: 265 passed, 0 failures.

- [ ] **Step 3: Append §5.2 to the report**

Append to `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md`, directly after the §5.1 subsection (before `## Self-check vs spec success criteria`):

```markdown
### 5.2 Glossary winding-down expansion (iv7, 2026-07-18)

Part A of the semantic-gap resolution: three corpus-grounded glossary
entries (`winding`, `wind`, `pull`; commit <sha>) bridge SEBI's own
vocabulary split ("winding down" for KRAs/AIFs vs "surrender/cancellation"
for CRAs). Query-side only — index unchanged from iv6. Spec:
`docs/superpowers/specs/2026-07-18-glossary-winding-expansion-design.md`,
plan: `docs/superpowers/plans/2026-07-18-glossary-winding-expansion.md`.

| run | answerable | answer-level failures | doc recall@10 |
|---|---|---|---|
| probes prior (`iv6-probes`) | 25 | 4 | 1.0 |
| probes iv7 (`iv7-probes`) | 25 | <n> | <x> |
| golden prior (`iv6-golden`) | 45 | 2 | 0.956 |
| golden iv7 (`iv7-golden`) | 45 | <n> | <x> |

probe-par-03: candidate_miss → <new class, with first_answer_rank>.
Regression check vs iv6: <none / list of new failure IDs>.
Gate verdict: <met / not met, which gates>. <If probes gate still unmet:
Part B (HyDE) trigger fires per the spec — full design in its own cycle.>
```

Fill every `<…>` with measured values (iv7 rows from Step 1 output; the commit SHA from Task 1's commit). Keep only the applicable branch of the final sentence.

- [ ] **Step 4: Commit results**

```bash
git add docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md \
        eval/runs/iv7-probes eval/runs/iv7-golden
git commit -m "eval: glossary winding-down expansion results (iv7) + report update"
```

---

## Self-review notes

- Spec coverage: Part A entries → Task 1 Step 3 (verbatim from spec); Testing § → Task 1 Steps 1–2 (red-first "winding down"→"surrender", "pull"→"withdraw", unchanged-query case already covered by pre-existing `test_query_without_glossary_terms_is_unchanged`); Measurement & gates § → Task 2 (iv7 run dirs, all gates incl. no-new-failure check, report §5.2). Part B § deliberately has no task — the spec scopes it out; §5.2's final sentence records whether its trigger fired.
- Type consistency: `expand_query(str, dict) -> str` unchanged; glossary entry shapes match the existing `dict[str, tuple[str, ...]]`.
- The existing wiring tests (`test_retrieve_routes_expanded_query_to_sparse_leg`, `test_retrieve_dense_leg_keeps_raw_query`) already pin sparse-leg-only routing, so no new wiring tests are needed.
