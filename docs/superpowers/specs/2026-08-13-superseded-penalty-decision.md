# `superseded_penalty` — decision record and confirmation plan

**Written:** 2026-08-13, **before** the confirmatory run.

---

## 1. Status of the evidence — read this first

The sweep (`2026-08-13-superseded-penalty-sweep-prereg.md`) was preregistered, but its guardrail was
mis-specified and the full grid has since been examined. **Any re-scoring of those same 204 rows is
post-hoc analysis, not preregistration**, and is labelled as such below.

What *is* preregisterable: the production pipeline (MLX generator, B′ on) has **never been measured
at penalty 0.5**. That run is new data, so its criteria are fixed here in advance.

## 2. The owner's decision (post-hoc selection, transparently labelled)

Harm definition set by the project owner, 2026-08-13: **exposure = the single top-ranked context is
a superseded circular the question did not ask about** (`stale@1`).

Under that definition the grid selects **penalty 0.5**, and does so for every price from 0.5 to 20
citation-misses per exposure — a 40× range. The selection is insensitive to the exact number, which
is the main reason to trust it despite being chosen post-hoc.

| penalty | context_miss | stale@1 | stale@3 |
|---|---|---|---|
| 0.30 (current) | 15 | 1 | 83 |
| **0.50 (selected)** | **13** | **1** | **101** |
| 0.70 | 12 | 4 | 122 |

**Accepted cost, stated plainly:** repealed law anywhere in the top 3 rises 83 → 101 rows (+22%).
The owner's harm definition prices that at zero. If that judgement changes, this decision reverses.

## 3. Confirmation criteria — fixed before the run

Run the production pipeline (MLX, B′ on) at `superseded_penalty=0.5` over golden_v7 and compare to
the archived 0.3 baseline (`mlx_reranker.json`, same generator and scorer).

**Validity check (failure ⇒ VOID, not repaired):** the 206-row perfect-retrieval subset must be
unchanged. That subset is defined by `recall`, which is computed over the **pre-rerank** fusion list
(`pipeline.py:141`) and cannot be affected by a demotion penalty. If it moves, the run is
misconfigured.

| Endpoint | Rule |
|---|---|
| **PRIMARY — zero-cite count** | must be **< 19** (the 0.3 baseline) |
| **GUARDRAIL — citation_precision** | must stay **≥ 0.1571**, the armed `gate_v7.json` floor |
| **GUARDRAIL — citation_recall** | must stay **≥ 0.8124**, the armed floor |
| Descriptive | recall_at_k, ndcg_at_10, abstention_accuracy — must not move (all are pre-generation) |

**Decision:**
- All criteria met → adopt: set `config.toml superseded_penalty = 0.5`, then **re-derive the gate
  floors**, because the operating point has moved and floors derived at 0.3 no longer describe the
  system.
- Any guardrail breached → **reject, keep 0.3**, regardless of the zero-cite improvement.
- zero-cite ≥ 19 → **reject**: the context-level gain did not survive into end citations, which is
  the standing limitation §9 of the sweep warned about.

---

## 5. OUTCOME (recorded 2026-08-13, after the confirmatory run)

**Validity checks PASSED**: 206-row subset unchanged, per-row `recall` identical across arms
(as required — `recall` is pre-rerank and cannot see the penalty).

| | 0.3 (baseline) | 0.5 (candidate) |
|---|---|---|
| **zero-cite (primary)** | 19 | **18** |
| citation_recall (subset) | 0.8981 | 0.8981 |
| citation_precision (subset) | 0.1948 | 0.1841 |

Gate metrics over 260 adjudicated rows, against the floors armed **before** this change:

| metric | 0.3 | 0.5 | floor | |
|---|---|---|---|---|
| recall_at_k | 0.9429 | 0.9429 | 0.9060 | OK |
| ndcg_at_10 | 0.6975 | 0.6975 | 0.6512 | OK |
| citation_recall | 0.8630 | 0.8630 | 0.8124 | OK |
| citation_precision | 0.1859 | **0.1757** | 0.1571 | OK |
| abstention_accuracy | 0.9615 | 0.9615 | 0.9335 | OK |

Paired zero-cite: Δ = −0.0049, CI [−0.0243, +0.0097], **p = 1.000**.

### The rule says adopt. I recommend against it.

By the letter of §3 every criterion is met: zero-cite 18 < 19, no guardrail breached. **The rule
selects adoption.** That is recorded as it stands.

But the criterion was under-specified in the same way the sweep's guardrail was: **I set a
direction (`< 19`) and no minimum effect size.** What it actually bought:

- **One row of 206**, p = 1.000. The context-level sweep predicted 2 rows; only 1 survived into end
  citations — exactly the standing limitation the sweep's §9 warned about.
- **citation_precision 0.1859 → 0.1757.** Headroom above the armed floor was 0.0288; this consumes
  **0.0102 of it, about 35%**. The guardrail passes because it asks "above the floor?", not "how
  much margin is left?".

Trading a third of the precision safety margin for one row at p = 1.000, on a legal tool, is a bad
trade. A criterion requiring a minimum effect would have rejected it, and should have been written
that way.

### Decision: NOT ADOPTED — `superseded_penalty` stays 0.3

`config.toml` unchanged; gate floors not re-derived. This is a deviation from the rule as written,
recorded here as a deviation rather than by quietly rewriting the criterion. The owner can overrule.

**If revisited, fix the criterion first:** require a minimum improvement (e.g. ≥4 rows, ~2pp) *and*
a maximum permitted consumption of floor headroom (e.g. ≤10%), set before the run.

## 4. Not permitted after seeing the result

- Adopting on a zero-cite improvement while a guardrail is breached.
- Re-deriving the floors first and then checking the metrics against the new, looser floors — the
  comparison must be against the floors armed **before** this change.
- Trying 0.6 or 0.55 because 0.5 disappointed.
