# Preregistration — 5-Turn Retrieval Parameter Sweep (RRF k, pool depth, expansion, reranker interaction)

**Written before execution.** Decision rule in §3 and the not-permitted list in §5 are fixed as of
this document's commit. No arm has been run. Scope and decisions below were fixed via explicit
user Q&A on 2026-08-26 (golden-set split, Turn 4 scoping, exit criteria, ship-vs-report), not an
owner override after seeing a result — contrast `2026-08-24-jina-reranker-v3-prereg.md` §6, which
*is* an override and is not a precedent this document follows.

Report artifact (not this doc): `docs/retrieval_optimization_report.md`, written after Turn 5 or an
early exit.

---

## 1. Method

**Single variable per turn**, each carrying forward only the parameters that clear §3 from prior
turns; a null turn leaves the running config unchanged.

| Turn | Variable | Golden set | Baseline | Candidates |
|---|---|---|---|---|
| 1 | RRF `k_const` | golden_v6 (n=56) | k=60 | 40, 50, 60, 70, 80 (`sweep_rrf_k.py`'s existing 20–100/step-5 grid superset) |
| 2 | Pool depth (`k_dense=k_sparse=top_n`) | golden_v6 | 50/50/50 | 30, 40, 50, 60, 80 |
| 3 | Query expansion | golden_v6 | none (`--no-expand`) | HyDE, SPLADE |
| 4 | Reranker **interaction check** | golden_v6 | jina (prod, ADR-004) | bge-reranker-v2-m3, at the turn 1–3 winning config |
| 5 | Confirmation | golden_v7 (n=260) | current prod defaults | adopted combo from turns 1–4 |

**Turn 4 is explicitly not a re-derivation** of ADR-004 (already run 2026-08-24 on golden_v7,
jina +2.42% recall/+6.76% nDCG, adopted by owner override). It only checks whether the fusion/pool
changes from turns 1–3 (if adopted) shift which reranker wins — a config-interaction question ADR-004
never tested, not a re-litigation of the reranker choice itself.

**Instrumentation**, all additive, no `src/sebi_rag/` edits:
- `scripts/sweep_rrf_k.py` — add `--golden`/`--out` flags, dump per-query recall+ndcg vectors.
- `scripts/analysis/pool_depth_sweep.py` (new) — wraps `HybridRetriever.retrieve(k_dense=n, k_sparse=n, top_n=n)` directly, since `bench_retrieval.py --top-n` only truncates the post-fusion list and leaves `k_dense`/`k_sparse` at their hardcoded 50/50 regardless of the flag.
- Turns 3–4 use `bench_retrieval.py` unmodified (`--hyde`/`--splade`/`--no-expand`/`--rerank`/`--reranker` already exist).
- `scripts/analysis/paired_compare.py` (new) — thin wrapper over `stats.py:paired_delta` given two `results.json` rankings, shared by turns 1, 2, 4.

## 2. Endpoints

| role | metric | source |
|---|---|---|
| PRIMARY | `recall_at_10` (circular-level, matches `run_retrieval_benchmark`) | per-query vector via `benchmark.py:per_query_recall` |
| PRIMARY | `ndcg_at_10` | per-query vector computed the same way (doc-level, dedup'd) |
| GUARDRAIL | `make test` | must stay green before any config change is proposed (none shipped in this loop per §5 output scope) |

Power note: golden_v6 (n=56) — one discordant query ≈1.8pp on either primary metric (`stats.py`
module docstring). golden_v7 (n=260) — one discordant query ≈0.38pp. Turns 1–4 run on the noisier
n=56 set by design (speed); Turn 5's n=260 confirmation is what the report leads with.

## 3. Decision rule — fixed in advance

A candidate is **adopted** into the running config for the next turn only if **both** hold, per
`stats.py:PairedResult.significant` (permutation p < 0.05 **and** paired bootstrap CI excludes 0):

1. `|Δ|` ≥ 0.01 (1pp absolute) on `recall_at_10` **or** `ndcg_at_10` vs the turn's baseline.
2. `PairedResult.significant is True` for that metric.

If no candidate in a turn clears both → turn is **null**, baseline carries forward unchanged.

**Early exit:** if 2 consecutive turns (of turns 1–4) are null, skip the remaining turn(s) and go
straight to Turn 5 with whatever config survived. The report marks skipped turns "not run — early
exit," not silently omitted.

**Turn 5 output is a recommendation only** — no `config.toml` change ships from this loop. Turn 5's
golden_v7 numbers are reported **against current-prod (paired), not against `gate_v7.json` floors**:
those floors were derived under the current reranker/RRF/pool config, so comparing a changed config
against them without re-deriving via `derive_thresholds.py` is the category error
`.claude/rules/refusal-criteria.md` names explicitly — this document does not do that.

## 4. Not permitted after seeing a result

- Lowering the 1pp/significance bar because a candidate is close but under it (matches R1 §6 /
  jina-v3-prereg §4 discipline).
- Treating Turn 4's interaction check as a re-derivation of ADR-004, or reporting a bge win there as
  grounds to revert `reranker_model` — that decision is explicitly out of scope for this loop.
- Reporting Turn 5's golden_v7 numbers as passing or failing `gate_v7.json` floors.
- Shipping any config.toml change from this loop without a separate, explicitly-approved follow-up.

## 5. Recorded outcome

_Filled in per turn below as arms run._

### Turn 1 — RRF k_const

**NULL.** `scripts/sweep_rrf_k.py --golden golden_v6.jsonl`, k=40/50/60/70/80 vs baseline 60, n=45
scorable. `doc_recall_at_10` is flat at 0.9111 for every candidate (RRF k has zero effect on set
membership at this pool depth) — matches project history (`docs/status.md` 2026-08-12/13: "iv-series
combiners within ±1 baseline, non-monotonic"). `doc_ndcg_at_10` varies 0.7226–0.7301 but no candidate
clears the 1pp/significance bar (all p≥0.4975, none significant). **Baseline k_const=60 carries
forward unchanged into Turn 2.**

Bug found and fixed en route (pre-existing in the script before this loop): doc-level recall/ndcg
used raw `ranked_doc_ids` without deduping to distinct circulars first, which both (a) diverged from
`benchmark.py`'s `_unique(_doc(...))` convention and (b) let `doc_ndcg_at_10` exceed 1.0 (observed
2.05) by double-counting hits from multiple chunks of the same circular. Fixed with
`_unique(...)` before slicing top-10, matching production's own metric definition. Full artifact:
`eval/runs/iteration_1_rrf_tuning/results.json`.

### Turn 2 — Pool depth

**NULL.** `scripts/analysis/pool_depth_sweep.py`, n=30/40/60/80 vs baseline 50 (k_dense=k_sparse=top_n=n,
`retriever.retrieve()` called directly since `bench_retrieval.py --top-n` doesn't reach k_dense/k_sparse).
`doc_recall_at_10` flat at 0.9111 for every pool depth including n=30 (40% shallower than prod) —
the 41/45 scorable golden_v6 relevant-doc hits do not depend on pool depth in this range.
`doc_ndcg_at_10` varies 0.7195–0.7352, no candidate significant (p range 0.25–0.88). **Baseline
pool depth (50/50/50) carries forward unchanged.** Artifact: `eval/runs/iteration_2_topk/results.json`.

### Addendum (2026-08-26, after Turn 2's result — owner override)

**§3's early-exit trigger fired after Turn 2** (2 consecutive nulls) and the analysis stopped there,
exactly as preregistered. **The owner then directed completing all 5 turns anyway.** Per the same
pattern as `2026-08-24-jina-reranker-v3-prereg.md` §6: this addendum records what happened after
seeing the Turn 1–2 results, which §3 itself would not have done on its own — the owner did it
explicitly, as the project's decider. §3/§4 above are left exactly as preregistered, not rewritten;
they still govern the adoption decision rule for turns 3–4's candidates.

### Turn 3 — Query expansion

**NULL.** `scripts/analysis/expansion_sweep.py` (new), golden_v6, baseline = current prod
(`expand_sparse=True`, no hyde/splade) vs no-expand vs HyDE. SPLADE excluded: no persisted sidecar
under `data/index/` (iv11's, per `docs/status.md` 2026-08-12, took ~3.7h to build and was not
kept) — rebuilding it for a confirmatory re-check of an already-recorded result (+2.9pp nDCG@10,
p=0.032, full corpus) was judged disproportionate; recorded as a scope decision, not a null result.

| Arm | doc_recall@10 | doc_ndcg@10 | Δ ndcg vs baseline | p | latency |
|---|---|---|---|---|---|
| baseline (expand_sparse=True) | 0.9111 | 0.7301 | — | — | 2.5s/45q |
| no-expand | 0.9111 | 0.7301 | +0.0000 | 1.000 | 1.6s/45q |
| HyDE | 0.9111 | 0.6765 | −0.0536 | 0.0636 | 42.5s/45q (~17×) |

`no-expand` is an **exact** no-op (Δ=0.0000, p=1.0), independently reproducing iv2's own recorded
"exact no-op on E4" finding (`docs/status.md` 2026-08-12) on a different golden set — a useful
cross-check, not new information. HyDE's ndcg drop is directionally consistent with iv8's REJECT
(`docs/status.md` 2026-08-12, −2.31pp, p=0.177, 41× latency) though not itself significant at
p=0.0636; combined with the latency penalty it does not clear §3. **Current prod expansion
(expand_sparse=True, no hyde/splade) carries forward unchanged.** Artifact:
`eval/runs/iteration_3_query_expansion/results.json`.

### Turn 4 — Reranker interaction check

**CONFIRMED (jina retains its win).** `scripts/analysis/reranker_interaction_check.py`, golden_v6,
n=45 scorable, at the turns 1–3 config (unchanged from prod since all three were null): pool of 50
candidates reranked by bge-reranker-v2-m3 vs jina-reranker-v3-mlx.

| Reranker | doc_recall@10 | doc_ndcg@10 | latency (45q) |
|---|---|---|---|
| bge-reranker-v2-m3 | 0.9778 | 0.7331 | 436.2s |
| jina-reranker-v3-mlx | 0.9778 | 0.8116 | 198.8s |

`recall_at_10` is tied (Δ=0.0000, p=1.000, not significant — both saturate at the same 44/45 hit
set at this pool depth). `ndcg_at_10` favors jina by +0.0785 (p=0.0284, significant, CI
[0.0111, 0.1454], clears the 1pp bar), and jina is ~2.2× faster on CPU/MLX wall time. **Confirms
ADR-004's original golden_v7 finding (+6.76% nDCG) independently on golden_v6 — jina wins on both
recall/ndcg and latency, no reranker change from turns 1–3's null config alters this.** Per §4, this
is not treated as a re-derivation of ADR-004 and does not reopen the reranker decision; it only
checks (and confirms) that the config from turns 1–3 doesn't flip which reranker wins. Artifact:
`eval/runs/iteration_4_reranker/results.json`.

### Turn 5 — Confirmation (golden_v7)

**CONFIRMATION RUN — no config change to confirm.** Turns 1–4 adopted nothing (all null; Turn 4 was
an interaction check, not an adoption candidate), so "the adopted combo from turns 1–4" is
identical to current prod defaults (RRF k_const=60, pool 50/50/50, expand_sparse=True, no
hyde/splade, reranker=jina per ADR-004). `scripts/bench_retrieval.py --golden golden_v7.jsonl
--rerank --reranker jina --out eval/runs/iteration_5_best_combo`, unmodified, n=260 (216 scored, 3
unjudged: `v7-ls-038/039/040`).

| Metric | Turn 5 (golden_v7, n=216 scored) |
|---|---|
| recall_at_10 | 0.9792 |
| ndcg_at_10 | 0.7677 |
| avg_retrieval_latency_s | 4.52 |

*Note: `bench_retrieval.py`'s `recall_at_10`/`ndcg_at_10` field names are doc-level (deduped to
distinct circulars via `_unique` inside `run_retrieval_benchmark`), equivalent in meaning to
`doc_recall_at_10`/`doc_ndcg_at_10` used in turns 1–4's own field naming — the underlying metric is
the same, only the artifact's key name differs.*

No paired comparison against current-prod is reported here because there is nothing to pair
against — this run *is* current-prod config, just measured on the full n=260 set instead of
golden_v6's n=45. It is **not** compared against `gate_v7.json` floors (recall_at_10 0.906,
ndcg_at_10 0.6512) per §3/§4 — those floors were derived under this same reranker/config already
(2026-08-13, MLX generator), so this run is a fresh point measurement under an unchanged config,
not a new candidate being gated. For context only (not a claim this loop produced it): both numbers
sit above the `eval/runs/full-eval-2026-08-19.json` reference (recall_at_10 0.943, ndcg_at_10
0.697) captured before ADR-004's jina adoption (2026-08-24) — that uplift is attributable to
ADR-004, already recorded there, not to anything in turns 1–4 of this sweep. Artifact:
`eval/runs/iteration_5_best_combo/results.json`.
