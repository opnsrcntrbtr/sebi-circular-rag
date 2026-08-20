# Fast Evaluation Tier — Preregistered Design + Validation

**Written:** 2026-08-19, **before** the tier is built or used to judge any arm.
**Status:** analysis plan frozen. Deviations get recorded as deviations, not edited away.
**Purpose:** make R0 (generator upgrade) and R1 (warrant scorer) iterable without weakening the gate.

---

## 0. A correction to the obvious design — read this first

The intuitive fast tier is "run the gate on the frozen 206-row perfect-retrieval subset instead
of all 260 rows." **That design is wrong twice over, and both faults are structural.**

### Fault 1 — the saving is not there

206/260 is a **21% reduction**. Against a measured `eval_json_full` of ~38 min at
Qwen2.5-1.5B, that is 38 → 30 min. At a 7B generator (~4-5x compute per token) it is
~3h → ~2.4h. **That does not make anything iterable.** Row count is the wrong lever; the cost is
dominated by generation, not by row count.

### Fault 2 — half the gated metrics are degenerate on that subset

The subset is *defined* as rows where every relevant document was retrieved. On it:

| Metric | Value on the subset | Why |
|---|---|---|
| `recall_at_k` | **1.000 by construction** | that is the subset's definition |
| `context_recall` | near-ceiling | same reason, one stage later |
| `ndcg_at_10` | uninformative | retrieval-stage metric, retrieval held perfect |
| `abstention_accuracy` | **undefined** | the 41 abstain rows are answerable-excluded |

Four of the six gated metrics cannot be read from it. A "fast gate" reporting `recall_at_k = 1.0`
would be reporting its own selection criterion.

**So the subset is a valid cohort for citation-stage endpoints and nothing else.** This spec
builds a different instrument.

---

## 1. Why

### 1.1 The cost trajectory

| Run | Measured | Source |
|---|---|---|
| `eval_json_full`, 260 rows, MLX 1.5B | **~38 min** | status.md 2026-08-15 |
| full reindex, 78k chunks | ~50 min | status.md 2026-08-12 |
| canary | 840 s | status.md 2026-08-13 |

R0's scope is a **full gate re-derivation** (`derive_thresholds.py` + `eval_json.py`, coupled via
`generate.eval_generator_for`). R1 iterates on top of R0. At ~3h per arm the loop does not run,
and the failure mode is silent: arms stop being re-run after small changes, and the gate drifts
from what production does — the exact class of defect the 2026-08-12 stub-vs-MLX re-derive fixed.

> **Addendum 2026-08-20 — the cost premise above is measured and was overstated.**
> §1.1 reasons from "~3 h per arm" at a 7B generator. Measured
> (`reports/generator-cost-Qwen2.5-7B-Instruct-4bit.json`): a 260-row gate is
> **69.9 min**, not ~3 h — 7B is **2.05x** 1.5B, not 4-5x. At 70 min the
> iteration-cost argument for T-Cohort is materially weaker, though §1.2's
> argument for **T-Screen** is untouched (it rests on the two no-ops, not on
> runtime). The original text is left as written; this is a record, not a rewrite.
> **Re-read §4 before running this spec** — the decision to build the ladder at
> all should be revisited against 70 min.
>
> **Addendum 2, same day — 69.9 min is itself superseded: the true cost is ~44 min.**
> That figure was inflated by a 3-row latency tail which proved **irreproducible**
> (`reports/timeout-tail-disconfound.json`): two further runs of the same 20 rows —
> one reversed, one in the identical original order — give **0** rows over
> `timeout_s` and 43.3 / 45.1 min. The tail followed neither the rows nor the run
> position. At ~44 min per arm the iteration-cost argument for **T-Cohort is weaker
> still**; §1.2's argument for **T-Screen** remains untouched, and T-Screen has
> since been run and returned a decisive result (see `docs/status.md` 2026-08-20).

### 1.2 Both known no-ops were detectable at n≈50

The two documented generator failures did not need 260 rows:

| Probe | Result | Rows needed to see it |
|---|---|---|
| Option A selective citations | **0 / 48** parseable brackets | 48 |
| CE rescue arm R1 | **74.2%** degenerate rewrites (23/31) | 31 |

Both were **total** no-ops — the mechanism never fired. A 50-row screen would have rejected each
in minutes. The memory note from that cycle says exactly this: *probe before preregistering any
generator-transforms-text intervention.* This spec makes the probe a standing tier rather than an
ad-hoc script.

---

## 2. Method — a three-tier ladder

Each tier answers a different question. **A tier may only be used for the question it answers.**

| Tier | n | Answers | May report | May NOT report |
|---|---|---|---|---|
| **T-Screen** | ~50, stratified | *Does the mechanism fire at all?* | mechanism-firing rate, degeneracy rate, latency | any gated metric |
| **T-Cohort** | 206 (frozen perfect-retrieval subset) | *Does it change citation behaviour?* | `zero_cite`, `citation_recall`, `citation_precision` | `recall_at_k`, `context_recall`, `ndcg_at_10`, `abstention_accuracy` (§0 Fault 2) |
| **T-Gate** | 260 (full golden_v7) | *Does it ship?* | all six gated metrics | — |

**Only T-Gate arms a floor.** T-Screen and T-Cohort are screening instruments; neither may derive,
re-derive, or compare against a floor as a shipping decision.

### 2.1 T-Screen composition (frozen)

50 rows drawn once, stratified proportionally to golden_v7's eight strata, seed fixed, ids written
to `eval/probes/screen_v1.jsonl`. Drawn from golden_v7 rather than held out, because T-Screen never
produces an adoption verdict — it only kills arms that do nothing, so reuse cannot inflate a
result.

**T-Screen's endpoint is mechanism-firing, not quality.** Examples: "fraction of answers containing
≥1 parseable bracket citation" (R0), "fraction of citation sets changed by the warrant scorer"
(R1). A firing rate of 0 rejects the arm outright; a non-zero rate licenses T-Cohort and nothing
more.

### 2.2 Capture-replay, where it applies

For arms **downstream of generation** — B′ margin, `min_keep`, citation scorer backend — retrieval,
reranking and generation are identical across arms. Those stages are captured **once** and the
citation variants replayed against the capture. This is not new: the B′ margin sweep already used
it (*"the capture-once sweep (one pipeline pass, instant margin evaluation) already validated the
full curve"*).

For arms that **change generation** (R0), capture-replay does not apply and T-Screen is the
saving.

---

## 3. Validation — the experiment this spec preregisters

The ladder is only sound if **T-Cohort deltas agree in sign with T-Gate deltas**. That is an
empirical claim and it is tested here before the ladder is used to judge anything.

### 3.1 Concordance set

Four arm-pairs whose T-Gate results are already recorded, re-measured on T-Cohort:

| # | Arm pair | Recorded T-Gate outcome |
|---|---|---|
| 1 | B′ OFF vs B′ ON | citation_recall 0.9248 → 0.8981; precision 0.1240 → 0.1948 |
| 2 | B′ ON vs B′ ON + `min_keep=3` | recall +0.0243 (p=0.061); precision −0.0388 (p=0.0005) |
| 3 | citation scorer `reranker` vs `nli` | zero-cite 19 → 54; Δ +0.1699, p=0.0001 |
| 4 | `superseded_penalty` 0.3 vs 0.5 | zero-cite 19 → 18; precision 0.1859 → 0.1757 |

These span both directions and both magnitudes, including one near-null (#4) — the hardest case
for a screening instrument and the one most likely to expose disagreement.

### 3.2 Endpoints

- **PRIMARY — sign concordance** on `citation_recall` and `citation_precision`: in how many of the
  4 pairs does T-Cohort agree with T-Gate on the direction of change.
- **SECONDARY — magnitude ratio**: T-Cohort Δ ÷ T-Gate Δ per pair, reported per metric.
- **GUARDRAIL — no inversions**: zero cases where T-Cohort shows improvement on a metric that
  T-Gate shows regressing.

## 4. Decision rule — fixed in advance

1. **Discard the ladder if any inversion occurs** (§3.2 guardrail). An instrument that can say
   "better" when the gate says "worse" is worse than no instrument, because it will be trusted.
2. **Adopt T-Cohort as a screening tier only if sign concordance is 4/4** on both metrics. 3/4 is
   not sufficient: with 4 pairs, one disagreement is 25% of the evidence.
3. **T-Screen requires no concordance validation** — it reports mechanism-firing, not a gated
   metric, and can only reject. Its false-negative risk (killing an arm that would have worked)
   is accepted and stated: an arm firing on 0 of 50 stratified rows is not worth 3h.
4. If 1-2 fail → the ladder is not adopted, and R0/R1 pay full T-Gate cost per arm. Record the
   null; do not weaken the concordance bar to rescue the design.

## 5. Confirmation and ongoing drift

Concordance is not a one-time property — it can decay as the corpus and generator change.

- Every arm that reaches **adoption** must still pass T-Gate (§2, "only T-Gate arms a floor").
  That is the standing drift check: each adoption produces a fresh T-Cohort/T-Gate pair.
- If any adoption run shows a sign disagreement, **the ladder is suspended** and re-validated
  under §3 before further use.
- The concordance table is appended to, never rewritten, so decay is visible.

## 6. Not permitted

- Arming, deriving, or re-deriving any gate floor from T-Screen or T-Cohort.
- Reporting `recall_at_k`, `context_recall`, `ndcg_at_10` or `abstention_accuracy` from T-Cohort
  (§0 Fault 2). These are structurally degenerate on that subset.
- Using T-Screen's firing rate as evidence an arm *works* — it can only show an arm does nothing.
- Lowering the 4/4 concordance bar after seeing the result.
- Expanding T-Screen beyond 50 rows to reach a cleaner concordance number.
- Substituting T-Cohort for T-Gate in the §7 confirmation of any other preregistration
  (`2026-08-19-supersession-confidence-tier-prereg.md`, `2026-08-19-crossref-eval-validity-prereg.md`).
- Re-drawing `screen_v1.jsonl` after seeing which rows an arm fails.

## 7. Implementation notes

| File | Change |
|---|---|
| `eval/probes/screen_v1.jsonl` | 50 stratified row ids, seed recorded |
| `scripts/analysis/eval_tier.py` | tier runner; refuses to emit a metric a tier may not report |
| `reports/fast-gate-concordance-2026-08-19.json` | §3 concordance results |

The tier guard must be **enforced in code, not by convention** — `eval_tier.py` raises on a request
for a disallowed metric rather than returning it with a caveat. This mirrors
`generate.eval_generator_for`, where three coupling tests prevent `derive_thresholds.py` and
`eval_json.py` from disagreeing about the generator; the same class of defect (two instruments
silently measuring different things) is what this guard prevents.

Hard constraints:

- **No change to `eval_json.py`'s full-gate path**, and no change to `derive_thresholds.py`. The
  gate is not modified by this spec — a new instrument is added beside it.
- **No new field on `CircularMeta`** (`segment.py:131` → 78,630 chunks).
- **No edit to `*_spaces.py` or root `app.py`.**
- Floors read from `eval/golden/gate_v7.json`, never transcribed from `docs/status.md`.

## 8. OUTCOME (recorded after execution)

_Not yet run._
