# B′ Selective Citations — Margin Sweep (gate re-arm, Task 7)

**Date:** 2026-08-04
**Status:** COMPLETE — margin 0.35 chosen; gate re-armed under B′ (2026-08-04).
**Goal:** pick `citation_margin` for B′ (post-hoc cross-encoder citation filter), then
re-derive `eval/golden/gate_v7.json` at that margin.

## Setup

- Set: `golden_v7.jsonl` adjudicated subset (n=260), scored via the REAL
  `golden_v7.score.score_row` (same path `derive_thresholds.py` / `eval_json.py` use).
- Pipeline: persisted index + `CrossEncoderReranker` (bge-reranker-v2-m3, MPS) +
  `SubjectSimJudge` (0.42/0.60) + `ExtractiveStubGenerator`; `top_k=10`,
  `abstain_threshold=0.05`.
- `citation_margin` is on the **sigmoid 0–1 score scale**. `select_citations` keeps
  contexts scoring ≥ (top − margin), always ≥1. Margin 0.0 in the table = the
  mechanical baseline (`citation_scorer=None`, cite-all).
- `n_cited_rows=219` (answered rows; abstain/abstained rows carry no citation metric).

## Results so far (full-pass sweep, TIGHT end)

| margin | citation_precision | citation_recall | recall@k | abstention |
|---|---|---|---|---|
| mechanical (cite-all) | 0.1189 | 0.8881 | 0.9429 | 0.9615 |
| 0.30 | 0.2406 | 0.7466 | 0.9429 | 0.9615 |
| 0.20 | 0.2741 | 0.6941 | 0.9429 | 0.9615 |
| 0.15 | 0.2919 | 0.6461 | 0.9429 | 0.9615 |

`recall@k` and `abstention` are unchanged across margins by construction — B′ only
rewrites `Answer.citations`, never retrieval or the abstention gate.

## Analysis

- **Monotonic precision↔recall trade-off.** Tightening the margin lifts precision
  (0.119 → 0.292) but drops citation_recall fast (0.888 → 0.646). Precision gains
  taper (+0.033 from 0.30→0.20, +0.018 from 0.20→0.15) while recall keeps falling — the
  tight end is a poor trade.
- **Knee is at the LOOSE end.** The best trade observed is margin **0.30**: precision
  ~2× (0.119 → 0.241) for a ~16% relative recall drop (0.888 → 0.747). Since keep-all
  ≡ mechanical (R=0.888), margins between 0.30 and 1.0 (looser than 0.30) should recover
  recall toward ~0.80 at some precision cost — that region was NOT swept here.
- **Legal-domain band (recall-priority):** missing a governing circular (recall loss)
  is worse than an extra tangential citation (precision loss). Target: largest precision
  where **mean citation_recall ≥ 0.75** so the bootstrap gate floor (lower bound − 0.005
  cushion) lands ≈ 0.70. Margin 0.30 (R=0.747) is right at that line; a slightly looser
  margin (~0.35–0.45) is expected to clear it with a smaller precision gain.
- **Decision still pending the loose-end curve (margins 0.35–0.60).**

## Cost / why the sweep was cut short

Each full pass re-runs the entire pipeline (retrieve + cross-encoder rerank of ~50
candidates + judge + generate + the answer-relevance rerank) over 260 rows — measured at
**~20 min/pass** (~4.6 s/row, MPS cross-encoder bound). The original run was killed after
4 passes; the remaining tight-end margins (0.10, 0.05) were dropped as unhelpful, and the
loose end is being explored via a cheaper capture-once script instead (see below).

## How to rerun the full-pass sweep

Script preserved at `scripts/analysis/sweep_citation_margin.py`. Edit the `margins`
tuple as needed, then:

```bash
TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=1 PYTORCH_ENABLE_MPS_FALLBACK=1 \
HF_HUB_DISABLE_XET=1 PYTHONPATH=src .venv/bin/python scripts/analysis/sweep_citation_margin.py
```

⚠️ ~20 min per margin. For a wider sweep prefer the capture-once variant
(`scripts/analysis/sweep_citation_margin_capture.py`, added next): one ~20-min pipeline
pass caches per-row answer-relevance scores, then sweeps all margins instantly. It is
validated by reproducing the four real points above (0.0 / 0.30 / 0.20 / 0.15).

## Full curve (capture-once, validated)

`scripts/analysis/sweep_citation_margin_capture.py` — one pipeline pass caches per-row
answer-relevance scores (via the REAL `pipeline.query`), then sweeps all margins instantly.
**Validation:** reproduced the four full-pass points EXACTLY (mechanical 0.1189/0.8881,
0.30 0.2406/0.7466, 0.20 0.2741/0.6941, 0.15 0.2919/0.6461), so the loose-end points below
are trustworthy. n=219 answerable adjudicated rows.

| margin | citation_precision | citation_recall |
|---|---|---|
| mechanical | 0.1189 | 0.8881 |
| 0.60 | 0.1604 | 0.8402 |
| 0.50 | 0.1761 | 0.8265 |
| 0.45 | 0.1865 | 0.8082 |
| 0.40 | 0.2021 | 0.7877 |
| **0.35 (chosen)** | **0.2241** | **0.7831** |
| 0.30 | 0.2406 | 0.7466 |
| 0.25 | 0.2615 | 0.7260 |
| 0.20 | 0.2741 | 0.6941 |
| 0.15 | 0.2919 | 0.6461 |

## Decision (2026-08-04)

- **Band:** mean citation_recall ≥ 0.75 (legal-domain recall priority — missing a governing
  circular is worse than a tangential citation). Guardrail: reject if gate floor < 0.70.
- **Chosen margin: 0.35.** Precision 0.224 mean (~1.9× the mechanical 0.119) while
  citation_recall stays 0.783 mean (−12% rel). 0.35 dominates 0.40 (higher precision at
  essentially equal recall); tightening to 0.30 drops recall below band for +0.017 precision.
- **Re-armed gate (real `derive_thresholds`, n=260 adjudicated, margin 0.35):**

  | floor | before (mechanical) | after (B′ @ 0.35) |
  |---|---|---|
  | recall_at_k | 0.906 | 0.906 |
  | citation_recall | 0.8397 | **0.7233** |
  | abstention_accuracy | 0.9335 | 0.9335 |
  | citation_precision | (ungated) | **0.1896** |

  citation_recall floor 0.7233 ≥ 0.70 guardrail; citation_precision now floored at 0.1896
  (was effectively ungated at ~0.119). `floors_ok` passes by construction (floor =
  bootstrap-lower-bound − 0.005 cushion, below the observed mean on the same `score_row` path).
- **Enabled:** `config.toml [service] citation_scorer_enabled = true`, `citation_margin = 0.35`;
  code defaults `_CITATION_MARGIN_DEFAULT = 0.35` / `Settings.citation_margin = 0.35`.
- **Monitor:** per-query citation_recall variance is wide (mean 0.783 → floor 0.7233). If
  production citation_recall clusters near the floor, tighten the margin later.
- **Coupling:** the gate now requires B′ ON to pass (citation_precision floor 0.1896 > the
  mechanical ~0.119). Eval/CI must run with `citation_scorer_enabled=true`.
