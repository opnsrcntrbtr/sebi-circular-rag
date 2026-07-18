# Wrapped-Line Governing-Clause Folding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recover full (multi-physical-line) governing-clause text in `hierarchical_chunk` so folded prefixes on numbered sub-clause chunks are no longer truncated at SEBI PDF hard-wrap boundaries.

**Architecture:** Extend the existing `heads` dict in `src/sebi_rag/segment.py` with an "open for absorption" state: after recording a heading, subsequent non-heading paragraphs are space-appended to that head until a clause terminator, the 300-char cap, or a new heading closes it. Chunk packing, IDs, and the fold-at-flush logic are untouched — absorption only changes the *recorded head text* that flush prepends.

**Tech Stack:** Python 3.12 (uv-managed venv), pytest, existing FAISS/BM25 index build (`make reindex`), benchmark scripts `scripts/bench_retrieval.py` and `scripts/analysis/extract_misses.py`.

**Spec:** `docs/superpowers/specs/2026-07-17-wrapped-clause-folding-design.md` (approved).

## Global Constraints

- Deterministic fix only — no LLM calls, no new dependencies. The embedding-semantic residue (para-aifmaster, probe-sup-04) is out of scope.
- Clause terminators are exactly `:` `;` `.` `–` (en-dash U+2013) `-` (hyphen). A trailing comma or bare word keeps absorbing.
- Head cap is 300 chars (existing cap retained: append, then re-truncate to 300; a head at ≥ 300 chars absorbs nothing further).
- Absorption never affects chunk packing: every paragraph still flows into `buf` exactly as today. Chunk count and IDs must be unchanged.
- Never overwrite existing run dirs (`eval/runs/ft-*`, `iv-final-*`, `iv2-*`); new runs go to `eval/runs/iv6-probes/` and `eval/runs/iv6-golden/`.
- `make test` green after every task (259 currently passing; 262 after Task 1's three new tests).
- After modifying source code, run `graphify update .` before committing (project rule).
- All commands run from repo root: `/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG`. Use `uv run python …` or `.venv/bin/python …` — bare `python` lacks the project deps.

---

### Task 1: Absorption mechanism in `hierarchical_chunk` (TDD)

**Files:**
- Modify: `src/sebi_rag/segment.py:90` (add `open_num` state next to `heads`), `src/sebi_rag/segment.py:131-158` (heading loop: open/absorb/close)
- Test: `tests/test_segment.py` (append three tests after `test_nominee_regression_corpus_unchanged_behaviour`)

**Interfaces:**
- Consumes: `hierarchical_chunk(text: str, meta: CircularMeta, max_chars: int = 1200, overlap_chars: int = 150) -> list[Chunk]` — signature unchanged.
- Produces: same signature; behavioral change only — `heads[num]` may now hold a wrapped clause joined across physical lines (space-joined, ≤ 300 chars). Task 2 relies on nothing else.

- [ ] **Step 1: Write the failing regression test plus the two guard tests**

Append to `tests/test_segment.py` (module constants `_META`, `_FILLER`, and helper `_body` already exist at the top of the file — reuse them):

```python
# --- wrapped-line governing-clause absorption (probe-par-03 residual) --------
# SEBI PDFs hard-wrap clause text; in a blank-line-free block each physical
# line arrives as its own paragraph, so only line 1 was recorded as the head.
_WRAPPED_CRA_TEXT = (
    _FILLER + "\n"
    "4.1.1. On and from the date of the Order, or the date of submission of "
    "request for\n"
    "surrender of certificate of registration to SEBI, as applicable,\n"
    "the concerned CRA shall –\n"
    "4.1.1.1. disclose prominently on its website the fact of winding down;\n"
    "4.1.1.2. permit companies to withdraw ongoing rating assignments "
    "without levy of any charge;\n"
    "4.1.2. All other obligations of the CRA shall continue as specified."
)


def test_wrapped_governing_clause_folds_full_text_into_sibling():
    # Head line 1 ends at "request for"; the discriminative tokens
    # ("surrender", "certificate") live on wrap line 2. The sibling chunk
    # 4.1.1.2 must carry them via the folded prefix.
    chunks = hierarchical_chunk(_WRAPPED_CRA_TEXT, _META)
    for c in chunks:
        if "withdraw ongoing rating assignments" in c.text:
            assert "surrender of certificate" in c.text, (
                f"wrapped clause text missing from sibling chunk: {c.text!r}"
            )
            break
    else:
        raise AssertionError("4.1.1.2 provision text missing from all chunks")


def test_terminator_head_absorbs_nothing():
    # A head already ending in a clause terminator (":") must not absorb the
    # following body line into the governing clause.
    text = (
        _FILLER + "\n"
        "5. Number of nominees:\n"
        "This provision applies to all folios opened after the effective "
        "date.\n"
        "5.1. Investors can provide up to 3 nominees."
    )
    chunks = hierarchical_chunk(text, _META)
    for c in chunks:
        if "up to 3 nominees" in c.text:
            assert "applies to all folios" not in c.text, (
                f"terminated head wrongly absorbed body text: {c.text!r}"
            )
            break
    else:
        raise AssertionError("5.1 provision text missing from all chunks")


def test_absorption_respects_300_char_cap():
    # A long unterminated head plus a long continuation must never yield a
    # folded governing-clause line over 300 chars.
    head_line = "7.1.1. " + ("alpha bravo charlie delta echo " * 9).strip()
    continuation = ("wrapped continuation tokens " * 12).strip()
    text = (
        _FILLER + "\n"
        f"{head_line}\n"
        f"{continuation}\n"
        "7.1.1.1. first child provision;\n"
        "7.1.1.2. second child provision about margin obligations;"
    )
    chunks = hierarchical_chunk(text, _META)
    for c in chunks:
        if "second child provision" in c.text:
            gov_lines = [
                l for l in c.text.splitlines() if l.startswith("7.1.1. ")
            ]
            assert gov_lines, "governing clause not folded into child chunk"
            assert all(len(l) <= 300 for l in gov_lines), (
                f"folded clause exceeds 300-char cap: {gov_lines!r}"
            )
            break
    else:
        raise AssertionError("7.1.1.2 provision text missing from all chunks")
```

- [ ] **Step 2: Run the new tests to verify red/green baseline**

Run: `uv run pytest tests/test_segment.py -v`

Expected: `test_wrapped_governing_clause_folds_full_text_into_sibling` FAILS with `wrapped clause text missing from sibling chunk` (today only head line 1 — ending "…request for" — is recorded and prepended). The two guard tests PASS already (they guard the new code against over-absorption; today there is no absorption at all). All six pre-existing tests PASS. If the regression test passes here, stop — the premise is wrong; debug before writing any implementation.

- [ ] **Step 3: Implement absorption in `segment.py`**

Add a module-level constant near the top of `src/sebi_rag/segment.py` (after the imports):

```python
# Clause terminators: a recorded heading ending in one of these is complete
# and must not absorb the next physical line (wrapped-clause folding).
_TERMINATORS = (":", ";", ".", "–", "-")
```

In `hierarchical_chunk`, add the open-head state next to `heads` (line 90):

```python
    heads: dict[str, str] = {}  # dotted num -> full heading line (governing clause)
    open_num = ""  # head still absorbing hard-wrapped continuation lines
```

Then extend the paragraph loop. Current code (lines 132-153):

```python
    for para in _paragraphs(text, max_chars):
        first_line = para.splitlines()[0]
        m = heading.match(first_line)
        if m:
            hnum = m.group(1)
            ...
            heads[hnum] = first_line.strip()[:300]
```

becomes (only the two marked additions; everything else — the `if buf:` carry block, `section_name`/`section_head`/`section_num` assignments, and the buf-packing below — stays byte-identical):

```python
    for para in _paragraphs(text, max_chars):
        first_line = para.splitlines()[0]
        m = heading.match(first_line)
        if m:
            hnum = m.group(1)
            ...
            heads[hnum] = first_line.strip()[:300]
            open_num = hnum                      # ADDITION 1: open absorption
        elif open_num:                           # ADDITION 2: wrapped-line absorption
            # SEBI PDFs hard-wrap clause text; a non-heading paragraph right
            # after a heading is usually its continuation. Absorb it into the
            # recorded head unless the head is already terminated or capped.
            head = heads[open_num]
            if len(head) < 300 and not head.endswith(_TERMINATORS):
                heads[open_num] = f"{head} {' '.join(para.split())}"[:300]
            else:
                open_num = ""
        if len(buf) + len(para) + 1 > max_chars and buf:
            ...
```

Notes for the implementer:
- The `elif open_num:` branch sits between the `if m:` heading block and the buf-packing `if` — it never touches `buf`, `carry`, or the section variables, so packing and chunk IDs are unchanged.
- `" ".join(para.split())` space-joins a possibly multi-line paragraph and normalizes whitespace before appending.
- A head that reaches exactly 300 chars (including the initial `[:300]` truncation of a long first line) absorbs nothing further (`len(head) < 300` fails), and the *next* non-heading paragraph closes absorption.
- The fold-at-flush logic (`flush`'s ancestor walk with the `gov not in body` dedup guard, lines 106-113) is deliberately untouched — it now simply prepends the fuller clause.

- [ ] **Step 4: Run the segment tests to verify green**

Run: `uv run pytest tests/test_segment.py -v`
Expected: all 9 tests PASS (6 pre-existing + 3 new). The pre-existing `_CRA_TEXT` tests stay green because that head ends in `:` (terminator guard), and the nominee tests stay green for the same reason.

- [ ] **Step 5: Red-green verify the fix is necessary**

```bash
git stash -- src/sebi_rag/segment.py
uv run pytest tests/test_segment.py::test_wrapped_governing_clause_folds_full_text_into_sibling -v
git stash pop
uv run pytest tests/test_segment.py -v
```

Expected: FAIL with the stash applied (old code), then all 9 PASS after `git stash pop`.

- [ ] **Step 6: Full test suite**

Run: `make test`
Expected: 262 passed (259 previous + 3 new), 0 failures.

- [ ] **Step 7: Update the knowledge graph and commit**

```bash
graphify update .
git add src/sebi_rag/segment.py tests/test_segment.py graphify-out
git commit -m "fix: absorb wrapped heading lines into governing clause (terminator + 300-char cap)"
```

---

### Task 2: Reindex, re-measurement against gates, report update

**Files:**
- Output: rebuilt `data/index/`, new run dirs `eval/runs/iv6-probes/`, `eval/runs/iv6-golden/`
- Modify: `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md` (append a subsection under §5)

**Interfaces:**
- Consumes: Task 1's committed chunker change; `make reindex`; `scripts/bench_retrieval.py --golden <jsonl> --out <dir>`; `scripts/analysis/extract_misses.py --run <trec> --golden <jsonl> --out <jsonl> --source <label>`.
- Produces: the measured verdict against the spec's gates, recorded in the report.

- [ ] **Step 1: Rebuild the index**

Run: `make reindex` (background it — chunk *text* changed for every doc whose sub-clause heads now absorb wrapped lines, so embeddings re-encode; expect ~30 min on MPS).
Expected: completes without error; `data/index/meta.json` updated. **Gate:** the chunk count printed by the build must be ≈ 77,859 — folding adds text, not chunks. A large delta means a chunker regression: stop, debug, do not benchmark.

- [ ] **Step 2: Re-run both benchmarks and classify misses**

```bash
HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/probes/probes_v1.jsonl --out eval/runs/iv6-probes

HF_HUB_DISABLE_XET=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 \
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv/bin/python scripts/bench_retrieval.py \
  --golden eval/golden/golden_v6.jsonl --out eval/runs/iv6-golden

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv6-probes/run.trec --golden eval/probes/probes_v1.jsonl \
  --out eval/runs/iv6-probes/failures.jsonl --source probes_v1

.venv/bin/python scripts/analysis/extract_misses.py \
  --run eval/runs/iv6-golden/run.trec --golden eval/golden/golden_v6.jsonl \
  --out eval/runs/iv6-golden/failures.jsonl --source golden_v6
```

Expected gates (report actual numbers verbatim whether or not met):
- probes answer-level failures (`answer_candidate_miss + answer_ranked_low`) ≤ 3 (from 4) — probe-par-03 is the specific target;
- golden answer-level failures ≤ 3 and `recall_at_10` ≥ 0.956 (no regression).

- [ ] **Step 3: Full test suite against the rebuilt index**

Run: `make test`
Expected: 262 passed, 0 failures.

- [ ] **Step 4: Append results to the report**

Append under `## 5.` of `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md` (after its existing content):

```markdown
### 5.x Wrapped-line clause folding (iv6, 2026-07-18)

Follow-up to intervention #1: heads now absorb hard-wrapped continuation
lines (terminator + 300-char cap; commit <sha>). Spec:
`docs/superpowers/specs/2026-07-17-wrapped-clause-folding-design.md`.

| run | answerable | answer-level failures | recall@10 |
|---|---|---|---|
| probes prior (`iv-final-probes`) | 25 | 4 | <x> |
| probes iv6 (`iv6-probes`) | 25 | <n> | <x> |
| golden prior (`iv-final-golden`) | 45 | <n> | 0.956 |
| golden iv6 (`iv6-golden`) | 45 | <n> | <x> |

Chunk count: <n> (expected ≈ 77,859). probe-par-03: <old class -> new
class>. Gate verdict: <met / not met, which gates>.
```

Fill every `<…>` with measured values (prior-row values come from the committed `eval/runs/iv-final-*/results.json` and `failures.jsonl`; iv6 rows from Step 2 output; the commit SHA from Task 1's commit).

- [ ] **Step 5: Commit results**

```bash
git add docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md \
        eval/runs/iv6-probes eval/runs/iv6-golden
git commit -m "eval: wrapped-clause folding benchmark results (iv6) + report update"
```

---

## Self-review notes

- Spec coverage: Mechanism §steps 1-5 → Task 1 Step 3 (state + absorb + close-on-heading + buf untouched + flush untouched); Testing § → Task 1 Steps 1-2-5 (regression red-first, terminator guard, cap guard, red-green cycle); Measurement & gates § → Task 2 (iv6 run dirs, all four gates, report §5 subsection). Scope §: no LLM work planned anywhere.
- Type consistency: `hierarchical_chunk` signature unchanged; `_TERMINATORS` defined in Task 1 Step 3 and used only there; test names in Step 5 match Step 1 definitions.
- The two guard tests are green-before-fix by design (they constrain the new absorption path); only the wrapped regression test carries the red-first burden, and Step 2 says to stop if it unexpectedly passes.
