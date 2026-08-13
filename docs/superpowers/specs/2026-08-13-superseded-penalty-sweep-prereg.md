# `superseded_penalty` sweep — Preregistered Analysis

**Written:** 2026-08-13, **before** the sweep was implemented or run.
**Status:** analysis plan frozen. Deviations get recorded as deviations, not edited away.

---

## 1. Why

Diagnosed 2026-08-13: `demote_superseded` is the **largest single cause** of zero-cite rows —
6 of 19, ahead of B′ (4). In each case the relevant document was *inside* the `top_k` context
window after reranking and `superseded_penalty=0.3` pushed it out (two from rank 0).

The mechanism is a pure post-hoc reweighting (`lineage.py:210-215`): score × penalty if the
circular is superseded, then re-sort. Larger penalty = less demotion; `1.0` = none.

## 2. The trade this is measuring — both harms, not one

Demotion exists so an in-force successor is cited over its superseded predecessor. Weakening it
buys citation correctness and risks surfacing repealed law. **A sweep that measures only the first
would argue for penalty=1.0 and quietly make the product worse for a legal user.** Both are
endpoints here.

## 3. Method — one rerank pass, penalties applied post-hoc

Demotion is post-hoc reweighting of an already-reranked list, so the reranked
`(chunk, score)` list is computed **once per query** and every penalty applied to that same list
in memory. Arms are therefore exactly comparable by construction — no run-to-run variation can
enter, because there is only one run.

`contexts` is reconstructed exactly as `generate.py:486-492` does: dedup by `doc_id` keeping the
highest score, sort descending, take `top_k`. Any divergence from that logic invalidates the
sweep; it is asserted against the live baseline (penalty=0.3 must reproduce the observed 6
demotion-caused misses).

**Scope:** answerable golden_v7 rows. `as_of` rows are **excluded** — they take a different branch
(`pipeline.py:51` if/elif) and never call `demote_superseded`.

## 4. Endpoints

- **PRIMARY — `context_miss`**: rows where no relevant circular appears in `contexts`.
  This is exactly the zero-cite mechanism under B′-off and the upstream cause under B′-on.
- **GUARDRAIL — `stale_context`**: rows where `contexts` contains a circular that is superseded
  **and not in `relevant_circulars`**. Superseded-but-relevant does not count: for
  `lineage_supersession` and `repealed_basis` rows, the superseded circular is the answer.

Both are counts over the same row set, so they move on a common scale.

## 5. Arms

`penalty ∈ {0.15, 0.3 (current), 0.5, 0.7, 0.85, 1.0}` — spanning harsher than today through no
demotion at all.

## 6. Decision rule — fixed in advance

Report the full frontier. Then:

1. Discard any arm whose `stale_context` exceeds the penalty=0.3 baseline by **more than 2
   rows** (~1% of the row set). Surfacing repealed law is the more serious harm for a legal tool.
2. Among the survivors, pick the arm with the lowest `context_miss`.
3. Adopt only if it improves `context_miss` by **≥3 rows** over baseline. A 1–2 row gain is noise
   at this sample size and does not justify touching a legal-correctness mechanism.
4. If no arm qualifies → **keep 0.3** and record that the current value is at the knee.

## 7. Confirmation required before adoption

The sweep measures the **context window**, not end citations. Any arm selected by §6 must be
confirmed with a full production run (MLX generator, B′ on) reporting zero-cite and
citation_precision against the armed gate floors, before `config.toml` changes.

A sweep result alone is **not** grounds to change `superseded_penalty`.

## 8. Not permitted after seeing the result

- Switching the primary to `stale_context` because the frontier looks better that way.
- Relaxing the 2-row guardrail to admit a lower-miss arm.
- Reporting a penalty not in the §5 grid (no post-hoc interpolation to a flattering value).
- Dropping `lineage_supersession`/`repealed_basis` rows as "unrepresentative" — they are the
  strata the mechanism exists for.

---

## 10. OUTCOME (recorded 2026-08-13, after execution)

204 answerable non-`as_of` rows, one rerank pass, penalties applied post-hoc.

**Fidelity assertion (§3) PASSED**: all 6 diagnosed demotion-caused rows are `context_miss` at
penalty 0.3, and all 6 are rescued at 1.0. The model reproduces the diagnosis exactly.

| penalty | context_miss | stale_context (@10) | Δ miss | Δ stale |
|---|---|---|---|---|
| 0.15 | 17 | 192 | +2 | −6 |
| **0.30 (current)** | **15** | **198** | — | — |
| 0.50 | 13 | 200 | −2 | +2 |
| 0.70 | 12 | 200 | −3 | +2 |
| 0.85 | 12 | 200 | −3 | +2 |
| 1.00 | 9 | 203 | −6 | +5 |

### What the §6 rule selects — and why it must not be acted on

Applied literally: 1.0 is discarded (+5 > 2); 0.7 and 0.85 tie at miss=12; the improvement is
exactly 3 rows, meeting the ≥3 bar. **The rule selects 0.7.**

**That selection is not trustworthy, because the guardrail I preregistered cannot see the harm it
exists to prevent.** `stale_context@10` is near-ceiling — 192–203 of 204 rows — because the corpus
holds 1350 superseded circulars, so nearly every top-10 window contains one. It moves 11 rows
across the entire penalty range and is effectively constant.

Rank-sensitive views, computed as a limitation assessment (not a rule change):

| penalty | miss | stale@10 | stale@3 | **stale@1** |
|---|---|---|---|---|
| 0.15 | 17 | 192 | 70 | 1 |
| **0.30** | **15** | **198** | **83** | **1** |
| 0.50 | 13 | 200 | 101 | 1 |
| 0.70 | 12 | 200 | 122 | **4** |
| 0.85 | 12 | 200 | 140 | **11** |
| 1.00 | 9 | 203 | 188 | **68** |

Moving 0.3 → 0.7 buys 3 citation rows and **quadruples the rate at which the top-ranked context is
repealed law** (1 → 4), with stale@3 rising 83 → 122 (+47%). At 1.0 the top context is repealed law
in 68 of 204 rows (33%).

### Decision

**DO NOT ADOPT. `superseded_penalty` stays 0.3.**

Per §8 I may not swap the primary or relax the guardrail to make the rule choose differently, and
I have not. The rule's output is recorded above as it stands. What is recorded alongside it is that
one of its inputs was mis-specified, which makes the output uninformative — the correct response is
to re-run under a valid guardrail, not to act on a number produced by a broken one.

Per §7 no confirmatory production run was performed: spending it to confirm a change the evidence
argues against would be waste.

**Incidental finding:** 0.3 sits near the knee of the stale@3 curve (0.15 → 70, 0.3 → 83, 0.5 →
101). The current value looks well chosen, which was not the expected result.

### Follow-up — needs its own preregistration

Re-run this grid with **`stale@1` and `stale@3` as the guardrail** (rank-sensitive, not saturated),
and a decision rule that prices one top-rank repealed-law exposure against one citation miss
explicitly. That ratio is a product judgement about legal risk and should be set by the owner
before the numbers are seen, not inferred from them afterwards.

## 9. Standing limitation

`context_miss` assumes a relevant document inside `top_k` will be cited. Under B′-off that is
exact; under B′-on the filter can still drop it (4 rows, measured). So the sweep bounds the
achievable improvement rather than predicting it.
