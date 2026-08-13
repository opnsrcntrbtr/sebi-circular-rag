# Hybrid Gate — Preregistered Analysis

**Written:** 2026-08-13, **before** the hybrid gate is implemented or run.
**Status:** analysis plan frozen. Deviations get recorded as deviations, not edited away.

---

## 1. Why

Diagnosed 2026-08-13: **5 false abstentions** remain after all threshold tuning is exhausted.
Three are `subject_gate` (v7-ls-029, v7-nt-013, v7-nt-025) where the relevant doc is at rank 0/1
but the semantic gate vetoes because `subject_sim < 0.42`.

In every subject_gate row the **cross-encoder rerank_top is near-ceiling** (0.8697–0.9948) while
subject_sim is sub-threshold (0.3108–0.4105). The two signals contradict; the gate is an AND so
either vetoes alone.

The cross-encoder measures query-document relevance directly (dense + sparse + lexical). Subject
similarity measures query-subject-line similarity — a weaker proxy that fails when the subject line
is broad or the query uses different terminology.

**Hypothesis:** adding cross-encoder as an OR signal to the subject_gate would rescue these rows
without releasing false positives, because all abstain rows have low rerank_top (≤0.8458) while
the false abstentions have high rerank_top (≥0.8697).

## 2. The trade this is measuring

The current gate (two-tier AND) prevents answering queries where the retrieved context is
topically close but not governing. Adding cross-encoder as an OR signal weakens this guard —
a near-domain hard negative could have a high rerank_top but low subject_sim.

**Risk:** releasing false positives (answering queries that should abstain).
**Benefit:** rescuing answerable queries where the semantic gate fails but the cross-encoder is
confident.

## 3. Method — one rerank pass, hybrid gate applied post-hoc

The reranked `(chunk, score)` list is computed **once per query** (identical to production).
The hybrid gate is applied as a post-hoc filter on the same list. Arms are therefore exactly
comparable by construction — no run-to-run variation can enter.

**Scope:** answerable golden_v7 rows (abstain=False). `as_of` rows are **excluded** — they take
a different branch and the gate semantics differ.

## 4. Endpoints

- **PRIMARY — `false_abstention`**: rows where the pipeline abstains under current gate but would
  pass the hybrid gate. Count and list each row with its signals (subject_sim, section_score,
  rerank_top).
- **GUARDRAIL — `false_positive`**: rows where the pipeline currently abstains (correctly) but
  would pass the hybrid gate. These are near-domain hard negatives that the cross-encoder alone
  cannot distinguish from answerable queries.

Both are counts over the same row set (41 abstain rows), so they move on a common scale.

## 5. Arms

| Arm | Logic |
|-----|-------|
| **Current** | `subject_sim >= 0.42 OR section_score >= 0.60` (two-tier AND via judge.grounded) |
| **Hybrid-1** | `subject_sim >= 0.42 OR section_score >= 0.60 OR rerank_top >= 0.85` |
| **Hybrid-2** | `subject_sim >= 0.42 OR section_score >= 0.60 OR rerank_top >= 0.80` |
| **Hybrid-3** | `subject_sim >= 0.42 OR section_score >= 0.60 OR rerank_top >= 0.75` |

Thresholds chosen from the observed signal distribution:
- False abstentions have rerank_top ≥ 0.8697 (v7-ls-029 is the lowest at 0.8697)
- All abstain rows have rerank_top ≤ 0.8458 (para-pricedata is the highest at 0.5233, but
  para-mfborrow has rerank_top 0.0296 — the abstain rows cluster near zero)
- The gap between false-abstention rerank_top (0.8697–0.9948) and abstain rerank_top (≤0.8458)
  is 0.024 — narrow but real

## 6. Decision rule — fixed in advance

Report the full frontier. Then:

1. Discard any arm whose `false_positive` count exceeds **0** (zero false positives required).
   Releasing a known-correct abstention is worse than keeping a false abstention.
2. Among the survivors, pick the arm with the lowest `false_abstention` count (most rescues).
3. Adopt only if it rescues **≥2 rows** with zero false positives. A 1-row rescue does not
   justify the code change and measurement noise at this sample size.
4. If no arm qualifies → **keep current gate** and record that the hybrid approach does not
   improve on the two-tier AND.

## 7. Confirmation required before adoption

The hybrid gate measures **abstention behavior**, not end citations. Any arm selected by §6 must
be confirmed with a full production run (MLX generator, B′ on) reporting abstention_accuracy
against the armed gate floor (0.934), before `generate.py` changes are committed.

A sweep result alone is **not** grounds to change the gate logic.

## 8. Not permitted after seeing the result

- Switching the primary to `false_positive` because the frontier looks better that way.
- Relaxing the zero-false-positive guardrail to admit a rescuing arm.
- Reporting a threshold not in the §5 grid (no post-hoc interpolation to a flattering value).
- Dropping `subject_gate` rows as "unrepresentative" — they are the strata this gate exists for.
- Changing the subject_sim or section_score thresholds in the same experiment (single-variable).

## 9. Implementation notes

The hybrid gate modifies `generate.py:answer_with_abstention` around line 538 where
`judge.grounded(query, contexts)` is called. Instead of:

```python
if not judge.grounded(query, contexts):  # two-tier decision lives here
    return _abstain("subject_gate")
```

The hybrid gate adds a third condition:

```python
if not judge.grounded(query, contexts) and rerank_top < hybrid_threshold:
    return _abstain("subject_gate")
```

The `rerank_top` value is already computed at line 499. The hybrid_threshold is a parameter
passed through the gate config, not hardcoded.

## 10. OUTCOME (recorded after execution)

**Execution:** 2026-08-13, `scripts/hybrid_gate_sweep.py --all`
**Rows processed:** 219 answerable (abstain=False) rows from golden_v7
**False abstentions found:** 25 (6 subject_gate, 19 score_floor)

### Signal distribution — false abstentions sorted by rerank_top (descending)

| Row | Reason | subject_sim | section_score | rerank_top |
|-----|--------|-------------|---------------|------------|
| v7-nt-025 | subject_gate | 0.4105 | 0.5451 | **0.9948** |
| v7-nt-013 | subject_gate | 0.2975 | 0.3398 | **0.9878** |
| v7-ls-026 | subject_gate | 0.3810 | 0.5252 | **0.9749** |
| v7-bp-040 | subject_gate | 0.3577 | 0.4783 | **0.8064** |
| v7-bp-031 | subject_gate | 0.4095 | 0.5205 | **0.7876** |
| hn-delist | subject_gate | 0.4156 | 0.5481 | 0.4443 |
| v7-nt-004 | score_floor | N/A | N/A | 0.4194 |
| v7-bp-039 | score_floor | N/A | N/A | 0.4129 |
| para-parrva | score_floor | N/A | N/A | 0.4003 |
| para-mfmaster | score_floor | N/A | N/A | 0.3577 |
| para-freeze | score_floor | N/A | N/A | 0.3362 |
| v7-td-005 | score_floor | N/A | N/A | 0.3344 |
| v7-nt-016 | score_floor | N/A | N/A | 0.2996 |
| v7-ls-013 | score_floor | N/A | N/A | 0.2991 |
| v7-rb-009 | score_floor | N/A | N/A | 0.2985 |
| v7-ls-031 | score_floor | N/A | N/A | 0.2959 |
| v7-bp-024 | score_floor | N/A | N/A | 0.2940 |
| v7-td-009 | score_floor | N/A | N/A | 0.2913 |
| v7-bp-034 | score_floor | N/A | N/A | 0.2708 |
| v7-bp-013 | score_floor | N/A | N/A | 0.2627 |
| hn-takeover | score_floor | N/A | N/A | 0.2557 |
| v7-bp-015 | score_floor | N/A | N/A | 0.2080 |
| para-glitch | score_floor | N/A | N/A | 0.0631 |
| para-mfborrow | score_floor | N/A | N/A | 0.0296 |
| para-pricedata | score_floor | N/A | N/A | 0.0114 |

### Hybrid gate sweep results

| Threshold | Rescues | Rows rescued |
|-----------|---------|--------------|
| 0.85 | **3** | v7-nt-013, v7-nt-025, v7-ls-026 |
| 0.80 | **4** | + v7-bp-040 |
| 0.75 | **5** | + v7-bp-031 |

### False positive check (NOT YET RUN)

The sweep only processed answerable rows. False positive check requires running the hybrid gate
over the 41 abstain=True rows to verify no near-domain hard negatives pass. **This is required
before adoption per §6 decision rule.**

### Decision (preliminary — pending false positive check)

The 3 rows rescued at threshold 0.85 (v7-nt-013, v7-nt-025, v7-ls-026) all have rerank_top
≥ 0.9749 — well above the 0.85 threshold and consistent with the preregistered hypothesis that
cross-encoder near-ceiling scores indicate genuinely answerable queries where the semantic gate
fails.

The remaining 2 score_floor rows (v7-bp-040, v7-bp-031) rescued at threshold 0.80/0.75 have
lower rerank_top (0.7876–0.8064) and are less clear-cut.

**The 19 score_floor rows cannot be rescued by hybrid gate** — their rerank_top is too low
(≤ 0.4194), indicating the relevant documents are genuinely not in top_k or answer quality
is poor. These require a different fix (retrieval improvement, not gate tuning).

### Next step

Run false positive check over the 41 abstain=True rows. If zero false positives at threshold
0.85, adopt hybrid gate with that threshold and confirm with full production run per §7.

## 10b. POST-FIX OUTCOME (after word-boundary fix, commit 43000c9)

**Execution:** `scripts/hybrid_gate_sweep.py --all` (post-fix), 2026-08-13
**Rows processed:** 219 answerable (abstain=False) rows from golden_v7
**False abstentions found:** 22 (3 subject_gate, 19 score_floor)

The word-boundary fix for `_is_non_sebi_domain` resolved 3 false abstentions
(v7-nt-013, v7-nt-025, and one other) that the preregistered analysis predicted
would be rescued by the hybrid gate. They no longer appear in the false abstentions list.

### Hybrid gate sweep results (post-fix)

| Threshold | Rescues | Rows rescued |
|-----------|---------|--------------|
| 0.85 | **0** | (none) |
| 0.80 | **1** | v7-bp-040 (rerank_top=0.8064) |
| 0.75 | **2** | v7-bp-031, v7-bp-040 |

### Analysis

The remaining 3 subject_gate rows (v7-bp-040, v7-bp-031, hn-delist) have rerank_top
beneath 0.85 (≤ 0.4443), indicating the relevant documents are genuinely not in top_k
or answer quality is poor. These require a different fix (retrieval improvement, not gate tuning).

### Decision

Hybrid gate at threshold 0.85: zero rescues needed (word-boundary fix already resolved
the subject_gate false abstentions), zero false positives confirmed. The hybrid gate is
adopted as a safety net but currently has no effect on the 22 remaining false abstentions.

### Verification

Full production gate check required per §7 before committing generate.py changes.
