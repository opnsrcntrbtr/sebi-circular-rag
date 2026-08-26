# Retrieval Optimization — 5-Turn Sweep Report

**Date:** 2026-08-26
**Prereg:** `docs/superpowers/specs/2026-08-26-retrieval-param-sweep-prereg.md` (decision rule and
early-exit criteria fixed before any arm ran)
**Scope:** report + recommendation only — **no `config.toml` change shipped from this loop.**
**Outcome:** all 5 turns run to completion (owner override of the preregistered early-exit rule
after Turn 2 — see "Early exit and override" below); **no parameter change recommended.**

## Summary

| Turn | Variable | Golden set | Result | Verdict |
|---|---|---|---|---|
| 1 | RRF `k_const` | golden_v6 (n=45 scorable) | doc_recall@10 flat 0.9111 @ k∈{40,50,60,70,80}; ndcg@10 Δ ≤0.0075, none significant (p≥0.4975) | **NULL** |
| 2 | Pool depth (k_dense=k_sparse=top_n) | golden_v6 (n=45) | doc_recall@10 flat 0.9111 @ n∈{30,40,60,80}; ndcg@10 Δ ≤0.0105, none significant (p≥0.2508) | **NULL** |
| 3 | Query expansion (HyDE/no-expand/SPLADE-excluded) | golden_v6 (n=45) | no-expand exact no-op (Δ=0.0000, p=1.0); HyDE ndcg −5.36pp (p=0.0636, not sig) + 17× latency | **NULL** |
| 4 | Reranker interaction (jina vs bge, at turns 1–3 config) | golden_v6 (n=45) | jina ndcg +7.85pp (p=0.0284, **significant**), recall tied; jina 2.2× faster | **CONFIRMED — jina retains its win, ADR-004 unchanged** |
| 5 | Confirmation | golden_v7 (n=216 scored / 260) | recall@10=0.9792, ndcg@10=0.7677 under unchanged current-prod config | **confirmation run, no delta to test** |

Decision rule (fixed in prereg §3): a candidate is *adopted* only if `|Δ| ≥ 0.01` on recall@10 or
ndcg@10 **and** `stats.py:PairedResult.significant` (permutation p<0.05 and bootstrap CI excludes
0). No candidate in turns 1–3 cleared this bar. Turn 4 is an interaction check, not an adoption
candidate — see prereg §1.

## Early exit and override

The prereg's early-exit rule (§3: "2 consecutive null turns → skip remaining turns, go to Turn 5")
fired correctly after Turn 2 and was applied as written in a first pass — Turn 3 and 4 were
initially marked skipped, Turn 5 not run. **The owner then explicitly directed completing all 5
turns anyway** ("complete all 5 turns instead of early exit"), overriding the early-exit shortcut
without changing the underlying adoption decision rule (§3/§4 of the prereg were left as written
and continued to govern turns 3–4's candidates). This mirrors the addendum pattern already
established in `2026-08-24-jina-reranker-v3-prereg.md` §6 — an owner override recorded after seeing
a result, not a rewrite of the original fixed rules. Full text: prereg doc, "Addendum
(2026-08-26, after Turn 2's result — owner override)".

Turns 3–5 below are the actual completed runs, not the "skipped"/"moot" reasoning from the earlier
early-exit pass.

## Turn 1 — RRF k_const

`scripts/sweep_rrf_k.py --golden golden_v6.jsonl`, k∈{40,50,60,70,80}, baseline k=60.

| k_const | doc_recall@10 | doc_ndcg@10 | Δ ndcg vs k=60 | p |
|---|---|---|---|---|
| 40 | 0.9111 | 0.7251 | −0.0050 | 1.000 |
| 50 | 0.9111 | 0.7226 | −0.0075 | 1.000 |
| **60 (baseline)** | 0.9111 | 0.7301 | — | — |
| 70 | 0.9111 | 0.7296 | −0.0005 | 1.000 |
| 80 | 0.9111 | 0.7296 | −0.0005 | 1.000 |

RRF k_const has **zero effect on doc-level set membership** at this pool depth — matches
`docs/status.md` 2026-08-12/13's prior finding ("iv-series combiners within ±1 baseline,
non-monotonic"; recall@10 ceiling-limited at 0.956). ndcg@10 moves by ≤0.75pp, never significant.

**Bug fixed en route** (pre-existing in the script, not introduced by this loop): doc-level
recall/ndcg were computed over the raw ranked-chunk list without deduping to distinct circulars
first, letting `doc_ndcg_at_10` exceed 1.0 (observed 2.05) by double-counting chunks from the same
circular. Fixed to match `benchmark.py`'s own `_unique(_doc(...))` convention. Artifact:
`eval/runs/iteration_1_rrf_tuning/results.json`.

## Turn 2 — Pool depth

`scripts/analysis/pool_depth_sweep.py` (new — calls `HybridRetriever.retrieve(k_dense=n,
k_sparse=n, top_n=n)` directly, since `bench_retrieval.py --top-n` only truncates the post-fusion
list and never varies leg depth). n∈{30,40,60,80}, baseline n=50.

| pool depth (n) | doc_recall@10 | doc_ndcg@10 | Δ ndcg vs n=50 | p |
|---|---|---|---|---|
| 30 | 0.9111 | 0.7259 | −0.0042 | 0.877 |
| 40 | 0.9111 | 0.7352 | +0.0051 | 0.251 |
| **50 (baseline)** | 0.9111 | 0.7301 | — | — |
| 60 | 0.9111 | 0.7195 | −0.0105 | 0.746 |
| 80 | 0.9111 | 0.7277 | −0.0023 | 0.873 |

Even at n=30 (40% shallower than production's 50), doc_recall@10 is unchanged — the golden_v6
relevant-doc hits in this set don't depend on pool depth across this range. Artifact:
`eval/runs/iteration_2_topk/results.json`.

## Turn 3 — Query expansion

`scripts/analysis/expansion_sweep.py` (new), golden_v6, baseline = current prod
(`expand_sparse=True`, no hyde/splade) vs no-expand vs HyDE.

| Arm | doc_recall@10 | doc_ndcg@10 | Δ ndcg vs baseline | p | latency (45q) |
|---|---|---|---|---|---|
| baseline (expand_sparse=True) | 0.9111 | 0.7301 | — | — | 2.5s |
| no-expand | 0.9111 | 0.7301 | +0.0000 | 1.000 | 1.6s |
| HyDE | 0.9111 | 0.6765 | −0.0536 | 0.0636 | 42.5s (~17×) |

SPLADE was excluded, not run as a null: no persisted sidecar exists under `data/index/` (iv11's
took ~3.7h to build and was not kept), and rebuilding it purely to re-check an already-recorded
result (iv11: +2.9pp nDCG@10, p=0.032, full corpus) was judged disproportionate — recorded as a
scope decision.

`no-expand` reproduces iv2's own "exact no-op" finding (`docs/status.md` 2026-08-12) independently
on a different golden set — a cross-check, not new information. HyDE's ndcg drop is directionally
consistent with iv8's REJECT (−2.31pp, p=0.177, 41× latency) though not itself significant at
p=0.0636; combined with the 17× latency penalty it does not clear §3. **Current prod expansion
carries forward unchanged.** Artifact: `eval/runs/iteration_3_query_expansion/results.json`.

## Turn 4 — Reranker interaction check

`scripts/analysis/reranker_interaction_check.py` (new), golden_v6, n=45, at the turns 1–3 config
(unchanged from prod, since all three were null): pool of 50 candidates reranked by
bge-reranker-v2-m3 vs jina-reranker-v3-mlx.

| Reranker | doc_recall@10 | doc_ndcg@10 | latency (45q) |
|---|---|---|---|
| bge-reranker-v2-m3 | 0.9778 | 0.7331 | 436.2s |
| jina-reranker-v3-mlx | 0.9778 | 0.8116 | 198.8s |

recall@10 is tied (Δ=0.0000, p=1.000). ndcg@10 favors jina by +0.0785 (p=0.0284, **significant**,
CI [0.0111, 0.1454], clears the 1pp bar), and jina is ~2.2× faster. This **independently confirms**
ADR-004's original golden_v7 finding (+6.76% nDCG) on a different (golden_v6) set — no config
change from turns 1–3 alters which reranker wins. Per prereg §4, this is not treated as a
re-derivation of ADR-004 and does not reopen that decision. Artifact:
`eval/runs/iteration_4_reranker/results.json`.

## Turn 5 — Confirmation (golden_v7)

Turns 1–4 adopted nothing (all null; Turn 4 is an interaction check, not an adoption candidate), so
the "adopted combo" is identical to current prod defaults. `bench_retrieval.py --golden
golden_v7.jsonl --rerank --reranker jina --out eval/runs/iteration_5_best_combo`, unmodified, n=260
(216 scored, 3 unjudged: `v7-ls-038/039/040`).

| Metric | Turn 5 (golden_v7, n=216 scored) |
|---|---|
| recall_at_10 | 0.9792 |
| ndcg_at_10 | 0.7677 |
| avg_retrieval_latency_s | 4.52 |

*Note: `bench_retrieval.py`'s `recall_at_10`/`ndcg_at_10` field names are doc-level (deduped to
distinct circulars via `_unique` inside `run_retrieval_benchmark`), equivalent in meaning to
`doc_recall_at_10`/`doc_ndcg_at_10` used in turns 1–4's own field naming — the underlying metric is
the same, only the artifact's key name differs.*

No paired delta is reported: this run *is* the current-prod config, just measured on the full n=260
set instead of golden_v6's n=45. **Not compared against `gate_v7.json` floors** (recall_at_10
0.906, ndcg_at_10 0.6512) as pass/fail per §3/§4 and `.claude/rules/refusal-criteria.md` — those
floors were derived under this same config already (2026-08-13, MLX generator); this is a fresh
point measurement, not a new candidate being gated against them.

For context only (not a claim this loop produced it): both numbers sit above the
`eval/runs/full-eval-2026-08-19.json` reference (recall_at_10 0.943, ndcg_at_10 0.697) captured
*before* ADR-004's jina adoption (2026-08-24) — that uplift is attributable to ADR-004, already
recorded there, not to anything discovered in turns 1–4 of this sweep. Artifact:
`eval/runs/iteration_5_best_combo/results.json`.

## Recommendation

**No parameter change.** Across all 5 turns:

- RRF k_const and hybrid-retrieval pool depth are flat/non-significant across every tested value on
  golden_v6 — reproducing, on an independent quick set, what the project's earlier iv-series
  already established on the full corpus (retrieval-stage levers exhausted; recall@10 is
  ceiling-limited).
- Query expansion: no-expand is an exact no-op (independently reproducing iv2), HyDE underperforms
  with a large latency penalty (directionally consistent with iv8's reject) — current prod
  expansion setting stands.
- Reranker choice (jina, ADR-004) is independently reconfirmed as a significant winner over bge on
  a second golden set, unaffected by anything from turns 1–3.
- Turn 5's golden_v7 confirmation shows current-prod retrieval performing at recall@10=0.979,
  ndcg@10=0.768 — consistent with, and not contradicted by, any of turns 1–4.

Five turns of parameter search (RRF fusion constant, pool depth, query expansion, reranker choice)
found no lever in this space that clears the preregistered 1pp+significance adoption bar beyond
what ADR-004 already shipped. **This is itself the informative result of running all 5 turns
rather than exiting early**: the null results at turns 1–3 are now supported by an independent
reranker reconfirmation (Turn 4) and a larger-n retrieval snapshot (Turn 5), not left as an
early-exit inference.

**Where headroom might still exist** (out of this loop's scope, flagged for a future prereg):
citation selection/attribution, not retrieval — matching `docs/status.md` 2026-08-12's own
conclusion ("bottleneck is citation selection, not retrieval") and the pending R7 conformal
calibration work already in flight.

## Artifacts

- `eval/runs/iteration_1_rrf_tuning/results.json`
- `eval/runs/iteration_2_topk/results.json`
- `eval/runs/iteration_3_query_expansion/results.json`
- `eval/runs/iteration_4_reranker/results.json`
- `eval/runs/iteration_5_best_combo/results.json`
- `docs/superpowers/specs/2026-08-26-retrieval-param-sweep-prereg.md` (full recorded outcomes incl.
  Addendum, §5)
- `scripts/sweep_rrf_k.py` (extended: `--golden`/`--out`, per-query capture, paired stats, doc-dedupe bugfix)
- `scripts/analysis/pool_depth_sweep.py`, `scripts/analysis/expansion_sweep.py`,
  `scripts/analysis/reranker_interaction_check.py`, `scripts/analysis/_metrics.py` (new)
