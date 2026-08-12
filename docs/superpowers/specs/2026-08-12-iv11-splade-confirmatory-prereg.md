# iv11 SPLADE — Preregistered Confirmatory Analysis

**Written:** 2026-08-12, **before** any confirmatory run was executed.
**Status:** analysis plan frozen. Any deviation below must be recorded as a deviation, not edited away.

---

## 1. Why this document exists

The exploratory result (frame E4 / golden_v7, n=216 scored):

| Metric | Baseline | iv11 SPLADE | Δ | p (uncorrected) |
|---|---|---|---|---|
| R@10 | 0.9560 | 0.9745 | +0.0185 | 0.169 |
| **nDCG@10** | 0.7044 | 0.7335 | **+0.0291** | **0.032** |
| MRR | 0.6339 | 0.6623 | +0.0284 | 0.101 |

That p=0.032 came out of **9 tests** (3 arms × 3 metrics) with no multiplicity control, and the
metric that produced it was chosen *after* seeing that recall@10 was ceiling-limited. Bonferroni
at α=0.05 requires p<0.0056 (family of 9) or p<0.0167 (family of 3). It clears neither. The
three metrics are strongly correlated, so their agreement is not independent evidence.

This is a textbook exploratory finding. It needs confirmation on data that did not generate it.

## 2. The trap: a "confirmatory re-run" would be theatre

Retrieval here is **deterministic** — same corpus, same index, same query set, same code produces
byte-identical run files. Re-running iv11 on golden_v7 would reproduce nDCG@10 = 0.7335 exactly
and p = 0.032 exactly. That is not confirmation; it is the same measurement printed twice.

**Confirmation requires held-out queries, not a repeated run.** Recording this explicitly because
"just run it again to be sure" is the intuitive and wrong move.

## 3. Held-out set

`eval/probes/probes_v1.jsonl` — **n=25, zero id overlap with golden_v7** (verified 2026-08-12).
It is the only labelled retrieval data not consumed by the exploratory analysis.

Rejected alternatives, with reasons:
- **golden_v6 / golden_v5 (n=56)** — not independent. golden_v7 inherited 30 rows from v5, and the
  non-`v7-` prefixed ids in the exploratory run (`aif_co`, `blockdeal`, `broker`, …) are v5/v6
  heritage. Overlapping queries cannot confirm.
- **golden_v7 abstain rows (41)** — no retrieval labels; nDCG undefined.
- **golden_v7 unjudged rows (3)** — `v7-ls-038/039/040` carry no `relevant_circulars`.

## 4. Power — stated in advance

n=25 is **underpowered** for the observed effect. The exploratory run moved 95 of 216 queries
(~44%) on nDCG@10; scaled down, expect ~11 discordant queries here. A paired randomization test on
~11 discordant observations cannot reliably detect Δ≈0.03.

**Therefore, declared before running:**
- A **significant** result on probes is meaningful confirmation.
- A **null** result on probes is **not** a refutation — it is the expected outcome of an
  underpowered test, and must not be reported as "iv11 failed to confirm."
- Neither outcome licenses a third metric or a fourth analysis.

## 5. Frozen analysis plan

- **Primary endpoint:** `nDCG@10`. **Single. Decisional. No substitutes.**
- **Secondary (descriptive only, never decisional):** R@10, MRR, mean retrieval latency.
- **Design:** paired, per-query, both arms on frame E4 (`corpus 5f626dd9`) over `probes_v1`.
  Control = `--splade` absent; treatment = `--splade`. Nothing else differs.
- **Test:** `sebi_rag.stats.paired_delta`, two-sided randomization, 10,000 resamples, seed 0 —
  the same function used for the exploratory analysis.
- **α = 0.05**, two-sided, uncorrected (a single preregistered primary endpoint needs no correction).
- **Comparability:** both runs must resolve to the same `Frame`; `assert_comparable` must pass.

## 6. Decision rule — fixed in advance

| Outcome on probes (nDCG@10) | Decision |
|---|---|
| p < 0.05 **and** CI excludes 0 **and** Δ > 0 | **Adopt iv11.** Proceed to production wiring (SPLADE is currently eval-only) and re-arm the gate with the new operating point. |
| p ≥ 0.05, Δ > 0 | **Hold.** Consistent direction, insufficient power. Do not adopt, do not discard. Revisit when a larger independent set exists. |
| Δ ≤ 0 | **Reject iv11.** The exploratory result does not replicate in direction. |

Latency is a veto, not an endpoint: if the SPLADE arm exceeds **3× baseline** retrieval latency,
adoption is refused regardless of the primary endpoint. (Exploratory measurement: 1.36×.)

## 7. What is NOT permitted after seeing the result

- Switching the primary endpoint.
- Adding strata, filters, or query subsets not named above.
- Dropping probe queries as "unrepresentative."
- Re-running with different `top_n` and reporting the better one.
- Treating an underpowered null as evidence of no effect (see §4).

---

## 9. OUTCOME (recorded 2026-08-12, after execution)

Runs: `eval/runs/E4-probes-baseline`, `eval/runs/E4-probes-iv11-splade`. Frame E4, n=25 judged.

| Endpoint | Baseline | iv11 SPLADE | Δ | 95% CI | p | discordant |
|---|---|---|---|---|---|---|
| **nDCG@10 (primary)** | 0.7237 | 0.7169 | **−0.0068** | [−0.0860, +0.0646] | 0.865 | 11 |
| R@10 (secondary) | 1.0000 | 0.9600 | −0.0400 | [−0.1200, 0.0000] | 1.000 | 1 |
| MRR (secondary) | 0.6348 | 0.6415 | +0.0066 | [−0.0918, +0.0963] | 0.917 | 11 |

Latency 0.0867 s vs 0.0845 s (1.03×) — the latency veto was not triggered.

**The §4 power prediction was accurate:** 11 discordant queries predicted, 11 observed.

### Decision, per the §6 rule fixed in advance

Δ on the primary endpoint is **−0.0068 ≤ 0** → **REJECT iv11.** Not adopted.

The exploratory +0.0291 did **not replicate in direction** on independent queries.

### Honest reading of what this does and does not establish

- It does **not** show SPLADE is harmful. Δ≈−0.007 with CI ±0.08 is consistent with no effect,
  and the interval still overlaps the exploratory +0.029. n=25 cannot separate those.
- It **does** remove the basis for adopting iv11. The one result that survived exploration failed
  the only test run on data that did not generate it — which is exactly what §1 flagged as the
  risk of a metric chosen after seeing the data.
- Secondary R@10 fell from a saturated 1.000 to 0.960: the SPLADE leg *lost* a relevant document
  on one probe query. Directionally consistent with the primary; not independently meaningful.
- Per §4, a null here was pre-declared as non-refuting. But §6 separates "p≥0.05 with Δ>0" (hold)
  from "Δ≤0" (reject) precisely so that a sign flip cannot be relabelled as an underpowered hold
  after the fact. The rule is honoured as written.

### Consequence for the programme

All three interventions measurable on frame E4 have now resolved: **iv2 exact no-op, iv8 rejected,
iv11 rejected on confirmation.** No retrieval intervention in the iv-series is currently
adoptable. The durable deliverable from this cycle is the **gate fix** (§ nDCG@10 now floored at
0.6512), not an accepted intervention.

---

## 8. Standing limitation

All of this measures **retrieval only**. None of these metrics observe answer quality,
citation correctness, or abstention behaviour. A retrieval gain that does not reach the
generated answer is not a product improvement, and this analysis cannot detect that distinction.
