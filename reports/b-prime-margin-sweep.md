# B′ Selective Citations — Margin Sweep (gate re-arm, Task 7)

**Date:** 2026-08-04
**Status:** IN PROGRESS — margin not yet chosen; gate NOT yet re-armed under B′.
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

## Next steps

1. Run capture-once → full curve incl. loose end (0.35–0.60).
2. Pick margin at the recall≥0.75 knee; set `_CITATION_MARGIN_DEFAULT` (generate.py) +
   `Settings.citation_margin`.
3. Re-derive the gate: `SEBI_RAG_CITATION_SCORER_ENABLED=1 make golden-v7-gate` — the
   authoritative floors come from this real run, not the sweep.
4. Verify `eval_json` passes the new floors; confirm citation_recall floor ≥ ~0.70 and a
   material citation_precision floor. Then flip `config.toml [service] citation_scorer_enabled`.
