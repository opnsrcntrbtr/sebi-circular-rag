# Wrapped-Line Governing-Clause Folding — Design

**Date:** 2026-07-17
**Status:** approved (scope and absorption rule chosen by user)
**Predecessor:** `docs/superpowers/reports/2026-07-16-preretrieval-failure-taxonomy.md` §5 (probe-par-03 residual root cause), plan `docs/superpowers/plans/2026-07-16-preretrieval-interventions.md` Task 4.

## Problem

Intervention #1 (governing-clause folding, commit 4039715) records only the
heading's **first physical line** as the governing clause (`heads[hnum]` in
`src/sebi_rag/segment.py`). SEBI PDFs hard-wrap clause text, so the recorded
head truncates mid-sentence. Observed in the CRA master circular
(SEBI/HO/DDHS/DDHS-POD2/P/CIR/2025/101):

```
4.1.1. On and from the date of the Order, or the date of submission of request for
surrender of certificate of registration ("the Request") to SEBI, as applicable,
the concerned CRA shall –
4.1.1.1. disclose prominently on its website, ...
```

Only line 1 is recorded; the folded prefix on child chunks (4.1.1.x) ends at
"…request for" and lacks the discriminative tokens ("surrender", "winding
down", "shall"). Result: probe-par-03 stays an answer-level candidate miss
(probes gate 4 > 3 target).

## Scope (user decision)

Deterministic folding fix **only**. The embedding-semantic residue
(para-aifmaster, probe-sup-04) is explicitly out of scope, deferred to a
future LLM-based iteration (HyDE / contextual headers per report #5).

## Mechanism (user-selected: terminator + cap)

In `hierarchical_chunk` (`src/sebi_rag/segment.py`):

1. Keep `heads: dict[str, str]` as today. Additionally track the most
   recently recorded heading number as **open for absorption**.
2. When a **non-heading** paragraph arrives while a head is open, append it
   (space-joined) to `heads[open_num]` iff:
   - the current head does **not** already end in a clause terminator —
     one of `:` `;` `.` `–` `-` (a trailing comma or bare word keeps
     absorbing), and
   - the head is under the **300-char cap** (existing cap retained; append
     then re-truncate to 300).
3. Any new numbered heading closes absorption (and opens its own).
4. Absorbed-or-not, the paragraph still flows into `buf` exactly as today —
   absorption only affects the recorded head text, never chunk packing.
5. The fold-at-flush logic (nearest-ancestor prepend with `gov not in body`
   dedup guard) is unchanged; it now simply prepends the full clause.

Invariants preserved: chunk count and IDs unchanged (prepend still happens at
flush, after packing decisions); no new dependencies; fully deterministic.

Known accepted risk: a heading that legitimately ends mid-thought without
punctuation absorbs one body line (bounded by the cap and terminator check on
the grown head).

## Testing (TDD, offline)

New tests in `tests/test_segment.py` using the real CRA text shape (blank-line-
free block to force per-line splitting):

- **Regression (red first):** sibling chunk 4.1.1.2 must contain
  "surrender of certificate" (currently fails — head truncates before it).
- **Terminator guard:** a head ending in `:` (e.g. "5. Number of nominees:")
  absorbs nothing; existing nominee tests stay green.
- **Cap guard:** absorption never grows a head beyond 300 chars.
- Red-green cycle verified on the regression test (revert fix → fail →
  restore → pass).

## Measurement & gates

`make reindex` (~30 min MPS), then re-run both benchmarks
(`scripts/bench_retrieval.py`) and `scripts/analysis/extract_misses.py` into
fresh run dirs (`eval/runs/iv6-*`; never overwrite `ft-*` baselines).

- Probes answer-level failures ≤ 3 (from 4) — probe-par-03 is the target.
- Golden answer-level failures ≤ 3 and doc recall@10 ≥ 0.956 (no regression).
- Chunk count ≈ 77,859 (folding adds text, not chunks; large delta = stop and debug).
- `make test` green (259 passing) after every step.

Report results (verbatim numbers, met or not) as a new subsection appended to
report §5.
