# Spec B — Auto-Research Loop

**Date:** 2026-08-06
**Status:** Design approved, not implemented
**Depends on:** `2026-08-06-evidence-base-remediation-design.md` (Spec A). No cycle may run before Spec A §7 establishes frame E4/golden_v7.

## 1. Problem

The project has every organ of a research loop — benchmark runner, bootstrap re-scoring, derived gate floors, parameter sweeps, frozen run archive — and no decidable objective. Every intervention verdict on record is "not distinguishable":

| Intervention | delta | p | queries changed |
|---|---|---|---|
| iv1+iv2 clause folding + glossary (ADOPTED) | +2.2 | 1.000 | 1 |
| iv8 HyDE | +0.0 | 1.000 | 0 |
| iv9 contextual headers | -2.2 | 1.000 | 1 |
| iv10 targeted headers | +0.0 | 1.000 | 0 |
| iv11 SPLADE | +0.0 | 1.000 | 2 |

Automating this loop without fixing the cause produces a faster route to p=1.000. The loop's distinguishing feature is therefore **refusal**: the ability to determine before spending compute that an experiment cannot yield evidence, and to record what would have been required instead.

## 2. The possibility floor

For a two-sided exact McNemar test at α=0.05 with `n_d` discordant pairs, the most extreme achievable outcome — every discordant pair favouring one arm — gives `p = 2 · 0.5^n_d`.

```
n_d = 5  →  p = 0.0625   never significant
n_d = 6  →  p = 0.03125  significant only if all 6 agree in direction
```

**No paired retrieval experiment with fewer than 6 discordant queries can produce a significant result, regardless of outcome.** This is arithmetic, not an assumption — no effect-size or variance estimate is involved.

Every intervention in the archive changed 0, 1, or 2 queries. All five were structurally incapable of significance before they were run. The loop's core precheck is to compute this number *first*.

## 3. Objective

Constrained, not blended:

```
maximize   citation_precision            current 0.224,  floor 0.1896
subject to citation_recall     ≥ 0.7233  current 0.783
           recall_at_k         ≥ 0.906   current 0.943   guardrail
           abstention_accuracy ≥ 0.9335  current 0.962   guardrail
```

`recall_at_k` is saturated with a ±11pt CI at n=45 and is demoted from target to guardrail. `citation_precision` is the only gated metric with meaningful headroom.

A weighted blend is rejected: the B′ margin sweep (`reports/b-prime-margin-sweep.md`) established that precision and recall trade directly (margin 0.35: precision +88%, recall 0.888→0.783). A blend lets the loop buy precision by sacrificing recall and score it as progress.

## 4. Cycle state machine

```
SELECT ───── 4 generators feed one queue, ranked by reach x plausible effect / cost tier
   │
REACH ───── deterministic count of golden queries the intervention changes   [seconds, no models]
   │
PREREG ──── MDE at frame n vs declared expected effect; freeze metric+direction+threshold
   │        git-commit the prereg record BEFORE measuring
   ├──────── reach < 6, or MDE > expected effect  →  REFUSED_UNDERPOWERED(n_required)  → next
   │
PROVISION ─ T0/T1: shared data/index/ opened read-only
   │        T2:    git worktree + isolated index dir
   │
MEASURE ─── eval on the frame's eval set → run.chunk.trec, run.doc.trec, results.json
   │
ADJUDICATE  exact McNemar (binary) / paired bootstrap (continuous) vs the frozen prereg
   │        ADOPT_CANDIDATE | REJECT | INCONCLUSIVE(n_required)
   │
PROPOSE ─── branch + .auto/proposals/<exp_id>.md   — the loop never merges
   │
LEDGER ──── append experiment record; upsert claims
```

## 5. Reach estimation

`reach(hypothesis) -> int` counts golden queries the intervention changes *at all*, before any effect is measured. Implementations by intervention class:

| Class | Method | Cost |
|---|---|---|
| Query-side transform (glossary, HyDE) | Count queries whose transformed text differs from the original | Pure string ops, no models |
| Post-retrieval knob (citation margin, `superseded_penalty`, `score_floor`) | Replay a captured artifact — the capture-once pattern from `scripts/analysis/sweep_citation_margin_capture.py` | One capture, then free |
| Retrieval-time knob (RRF `k`, `k_dense`, `k_sparse`, `top_n`) | Retrieve at both settings on the cached index, count queries with a differing top-k circular set | Retrieval only, no rerank/generate |
| Corpus-side transform (headers, chunking) | Count golden-relevant chunks whose text changes | Corpus scan |
| Third-leg retriever (SPLADE) | Count queries whose fused top-k differs | Retrieval only |

Reach is an **upper bound** on discordant pairs: a query the intervention does not touch cannot become discordant. So `reach < 6 ⇒ significance impossible ⇒ REFUSED`, with no eval run.

The converse does not hold. `reach ≥ 6` does not establish power — it only means the experiment is not provably futile, so it proceeds to the MDE check. Reach and observed discordance are different quantities: the archive's "queries changed" figures (1, 0, 1, 0, 2) are *observed discordance*, measured after the fact, and reach for those same interventions may have been higher. What the archive establishes is that all five were incapable of significance; which of them `reach.py` would have refused in advance is an empirical question this spec measures rather than assumes (§15).

## 6. Power module

`src/sebi_rag/autoresearch/power.py`. `scipy` 1.18.0 and `numpy` 2.5.1 are both present (`pyproject.toml:14-15`), so `scipy.stats` is available for the exact tests and normal quantiles. No new dependency is required.

| Function | Method |
|---|---|
| `mcnemar_exact(b, c)` | Two-sided exact binomial at p=0.5 via `scipy.stats.binomtest(b, b + c, 0.5)`; never the chi-square approximation, which is invalid at the small discordance counts this loop operates in |
| `min_discordant_for_significance(alpha=0.05)` | Smallest `n_d` with `2·0.5^n_d ≤ alpha` → 6 at α=0.05 |
| `paired_bootstrap_ci(deltas, resamples=10000, seed=0)` | Percentile CI; matches `rescore_runs.py` conventions |
| `mde_continuous(sd_diff, n, alpha=0.05, power=0.80)` | `(z_{1-α/2} + z_{power}) · sd_diff / √n`, constant 2.80 |
| `n_required(sd_diff, delta, ...)` | `(2.80 · sd_diff / delta)²` |

`sd_diff` is estimated from prior paired runs **in the same frame**. When none exist, the conservative bound `sd_diff ≤ √2 · sd_metric` is used and the resulting MDE is labelled `upper_bound: true` in the prereg record, so a refusal based on it is legible as conservative rather than measured.

## 7. Preregistration

Written and **git-committed before the treatment arm runs**. The commit timestamp is the tamper-evidence; nothing else is required to make the claim credible.

```json
{"record":"prereg","exp_id":"E4-x017","ts":"2026-08-06T11:00:00Z","frame":{"epoch":"E4","eval_set":"3e44dfb9..."},
 "hypothesis":"raise citation margin 0.35 -> 0.45","generator":"knob_sweep","cost_tier":"T0",
 "target_metric":"citation_precision","direction":"increase","expected_effect":0.04,
 "constraints":{"citation_recall":0.7233,"recall_at_k":0.906,"abstention_accuracy":0.9335},
 "reach":31,"mde":0.028,"mde_upper_bound":false,"decision":"RUN"}
```

A verdict record may never alter a prereg field. Enforced by test, not convention.

## 8. Verdict

```json
{"record":"verdict","exp_id":"E4-x017","prereg_commit":"a1b2c3d","ts":"2026-08-06T11:07:00Z",
 "run":"eval/runs/E4-x017-golden","observed":{"citation_precision":0.251,"citation_recall":0.744,
 "recall_at_k":0.941,"abstention_accuracy":0.960},
 "delta":0.027,"ci95":[0.004,0.051],"n_discordant":19,"p":0.021,
 "constraints_held":true,"verdict":"ADOPT_CANDIDATE"}
```

| Verdict | Condition |
|---|---|
| `ADOPT_CANDIDATE` | CI excludes 0 in the prereg direction **and** every constraint holds |
| `REJECT` | CI excludes 0 against the prereg direction, or any constraint breached |
| `INCONCLUSIVE` | CI includes 0; records `n_required` for the observed effect size |
| `REFUSED_UNDERPOWERED` | Terminated at PREREG; no eval run performed |

`ADOPT_CANDIDATE` writes a branch and `.auto/proposals/<exp_id>.md`. **The loop never merges.** Adoption is a human act, consistent with `make golden-v7-gate` refusing rather than relaxing.

## 9. Hypothesis generators

Four generators feed one queue; ranking is `reach × plausible_per_query_effect ÷ cost_tier_weight`.

Proposals with `reach < 6` are **not silently dropped** — they proceed to PREREG and terminate as `REFUSED_UNDERPOWERED` with a recorded `n_required`. The refusal record is the scientific product (§12); discarding it at selection would empty the null-results table the loop exists to build. Ranking only determines order of attempt.

| Generator | Source |
|---|---|
| `failure_driven` | `failures.jsonl`, `scripts/analysis/extract_misses.py`, `trace_failure.py`, per-stratum breakdowns across the 8 v7 strata — targets the largest concentrated error mass |
| `backlog` | Ranked hypothesis file maintained by hand; deferred work (MLX embedding/reranker backend, measure-pipeline CI) |
| `knob_sweep` | Systematic sweep of `config.toml` parameters: RRF `k`, `score_floor`, `superseded_penalty`, `citation_margin`, `k_dense`, `k_sparse`, `top_n` |
| `literature` | Techniques from recent RAG/legal-IR work not yet tried. Ranked last by default: HyDE, SPLADE and contextual headers all reached 0–2 queries here. |

Generators propose; they do not decide. Every proposal passes through the same REACH → PREREG gate.

## 10. Cost tiers and isolation

| Tier | Change class | Provisioning | Cost |
|---|---|---|---|
| T0 | `config.toml` only | Shared `data/index/`, read-only | Seconds |
| T1 | Retrieval-time code | Shared `data/index/`, read-only | Minutes |
| T2 | Chunking, embeddings, sidecars | `git worktree` + isolated index dir (the `data/index_ar` pattern from `autoresearch.sh`) | ~82s incremental / ~8 min full reindex |

T0 and T1 assert `index_fingerprint` is unchanged after the run. A tier misclassification is caught rather than silently corrupting the 1.0 GB index.

Eval cost is modest because golden scoring runs through `ExtractiveStubGenerator`, not MLX — embed 219 queries, FAISS, cross-encoder rerank, B′ citation scoring.

## 11. Ledgers

| Ledger | Path | Content |
|---|---|---|
| Experiments | `.auto/experiments.jsonl` | prereg + verdict records linked by `exp_id`, append-only |
| Claims | `.auto/claims.jsonl` | supersession-aware insights |
| Proposals | `.auto/proposals/<exp_id>.md` | human-readable adoption request |
| Runs | `eval/runs/<epoch>-<exp_id>-<set>/` | frozen TREC + qrels + results |

`.auto/` is the existing convention (`log.jsonl`, `measure.sh`, `research_report.md`).

### 11.1 Claims ledger

The project's own supersession model applied to its research record — the same amend/repeal structure `lineage.py` implements for circulars.

```json
{"claim_id":"c-041","statement":"B' margin 0.35 improves citation_precision without breaching the citation_recall floor",
 "frame":{"epoch":"E4","eval_set":"3e44dfb9..."},"status":"supported",
 "evidence":{"exp_ids":["E4-x017"],"effect":0.027,"ci95":[0.004,0.051],"p":0.021},
 "supersedes":["c-022"],"superseded_by":null,"ts":"2026-08-06T11:07:00Z"}
```

`status ∈ {supported, refuted, superseded, underpowered}`.

**Staleness is derived, never stored.** A claim whose frame is not the current frame, with no revalidating experiment in the current frame, is computed stale on read. This is what prevents the failure mode already visible in the repo: `dist/datasets/manifest.json` still pins `golden_v6` and reads as authoritative.

`make claims` prints live / stale / superseded. A stale claim may not be cited in a release.

## 12. Publication surface

Continuous HF Hub revisions via the existing `push_datasets.py`, one revision per closed epoch, **tagged `epoch-E4`** so revisions remain stable references despite not being archival DOIs.

Each revision carries corpus snapshot, eval set, qrels, every run in the epoch, the experiment ledger, and live claims. The dataset card is the datasheet: provenance stratification (Spec A §8), κ/AC1, licensing (government works for circular text, CC-BY-4.0 for annotations), and the null-results table with `n_required` per refused or inconclusive intervention.

The null-results table is the artifact most worth publishing. "Five techniques show no detectable effect on Indian regulatory retrieval at n=219, and here is the sample size each would have needed" is defensible precisely because the protocol refuses underpowered runs — there is no path by which it could have been p-hacked.

## 13. Components

```
src/sebi_rag/autoresearch/
  epoch.py       # from Spec A
  trecio.py      # from Spec A
  power.py       # mcnemar_exact, min_discordant_for_significance,
                 # paired_bootstrap_ci, mde_continuous, n_required
  reach.py       # reach estimators per intervention class
  hypothesis.py  # 4 generators + ranking
  prereg.py      # prereg record write + git commit + immutability guard
  verdict.py     # decision rule
  claims.py      # claims ledger, supersession chains, derived staleness
scripts/autoresearch/run_cycle.py
```

Makefile: `autoresearch` (one cycle), `epoch-open`, `epoch-status`, `claims`.

Unattended invocation reuses the existing scheduling surface (`automation/n8n/`, `scripts/notify.sh`).

## 14. Error handling

| Condition | Behaviour |
|---|---|
| Cycle crash | Ledger records `status: aborted` with traceback path; worktree removed; shared index was read-only so it cannot have been written |
| Corpus refresh mid-cycle | Frame fingerprint mismatch detected at result-write time → cycle invalidated, never recorded as a result |
| T0/T1 mutated the index | Post-run `index_fingerprint` assertion fails the cycle and flags tier misclassification |
| Constraint metric missing | Verdict is `REJECT`; a missing guardrail is never treated as a passing one |
| Prereg commit fails | Cycle aborts before measuring — an unrecorded prereg forfeits the credibility the design exists to provide |
| HF push failure | Local epoch bundle stays authoritative; retry is idempotent |

## 15. Testing

TDD. Offline, no network, no model weights, inside `make test`:

| Test | Asserts |
|---|---|
| `test_mcnemar_exact_matches_known_values` | Against hand-computed binomial values |
| `test_min_discordant_is_six_at_alpha_05` | The possibility floor |
| `test_reach_below_floor_refuses` | `reach=5` yields `REFUSED_UNDERPOWERED`, no eval invoked |
| `test_reach_equals_actual_changed_queries` | Reach estimate matches a fixture's measured discordance |
| `test_mde_decreases_with_n` | Monotonicity |
| `test_n_required_inverts_mde` | Round-trip |
| `test_prereg_fields_immutable` | Verdict cannot alter a prereg field |
| `test_verdict_rejects_on_constraint_breach` | Precision gain with recall below floor ⇒ `REJECT` |
| `test_claim_supersession_chain` | `supersedes` / `superseded_by` resolve correctly |
| `test_claim_stale_when_frame_advances` | Derived staleness, not stored |
| `test_cycle_refuses_frame_without_baseline` | Spec A §7 dependency enforced |

The historical archive is a fixture. Two distinct assertions, kept separate:

- `test_archived_interventions_were_incapable_of_significance` — observed discordance for iv2, iv8, iv9, iv10, iv11 is 1, 0, 1, 0, 2, each below the floor of 6. This is a fact about the record and is asserted exactly.
- `test_reach_is_upper_bound_on_observed_discordance` — for each archived intervention, `reach.py` ≥ its observed discordance. Reach values are **measured and recorded**, not asserted against expected constants; how many of the five reach would have refused in advance is a finding of Phase 1, reported in the null-results table.

## 16. Build order

| Phase | Delivers |
|---|---|
| 1 | `power.py`, `reach.py`, `prereg.py`, `verdict.py`, experiment ledger; loop runs T0 knob sweeps only |
| 2 | Four hypothesis generators; T1/T2 tiered isolation with worktrees |
| 3 | Claims ledger; HF epoch revisions; dataset card with null-results table |

## 17. Acceptance

1. `min_discordant_for_significance(0.05) == 6`, proven by test.
2. The five archived interventions are shown incapable of significance (observed discordance 1, 0, 1, 0, 2 < 6), and `reach.py` returns a value ≥ observed discordance for each, with the measured reach values recorded.
3. A T0 knob sweep completes end to end: prereg committed before measurement, verdict recorded, `index_fingerprint` unchanged.
4. An `ADOPT_CANDIDATE` produces a branch and a proposal file and merges nothing.
5. A cycle in a frame with no baseline refuses.
6. `make claims` distinguishes live, stale, and superseded claims.
7. `make test` still passes at ≥667.
