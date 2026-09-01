# Spec — golden set statistical power (design only, no rows generated)

**Written 2026-09-01**, following the bge-m3 fine-tuning null
(`.claude/plans/deep-analyse-and-research-bright-dawn.md`, Finding 4). This document scopes
the problem and estimates cost; it does not expand `golden_v7`. No adjudication, generation,
or seeding work has started.

## 1. The problem, stated precisely

Paired-difference SD measured across `golden_v7`'s 216 scored rows
(`scripts/finetune/eval_phase0.py`'s `score_run`, using `src/sebi_rag/eval.py`'s
`recall_at_k`/`ndcg_at_k`):

| Metric | paired-diff SD | n for 80% power @ α=.05 |
|---|---|---|
| | | **1pp** | **2pp** | **3pp** | **5pp** |
| ndcg@10 | 0.2063 | 3,338 | **834** | 371 | 134 |
| recall@10 | 0.2405 | 4,535 | 1,134 | 504 | 181 |

At n=216, `golden_v7` resolves nothing smaller than a ~4pp ndcg@10 swing. Every retrieval
intervention this repo has actually run — this fine-tune (Δndcg ≈ -0.02), the `iv-series` A/B
runs (`iv-series-verdicts-unpowered` memory) — moved metrics in the 1–2pp range. The set is
not merely noisy for these; it is structurally incapable of resolving them, at any α.

## 2. Target

Detect a **2pp ndcg@10 delta at 80% power** → **n≈834** scored rows, ~3.9× the current 216.
Chosen as the smallest round target that clears the actual observed effect sizes (both this
intervention and `iv-series` cluster at 1–2pp) rather than the largest — a 1pp target
(n≈3,338) is named for completeness but is not the recommendation; see §5.

## 3. Row provenance

The corpus grew from 730 → 1,490 circulars during this intervention's Phase −1 (bounded
scrape, frozen snapshot). That is the raw material `golden_v7` (built against the 730-doc
corpus) never had access to. Reuse, not rebuild:

- `scripts/golden_v7/mine_strata.py` — candidate mining per task_type stratum, existing tool.
- `scripts/golden_v7/build_pool.py`, `make_packet.py` — pooling and packet assembly, existing.
- `scripts/golden_v7/local_adjudicate.py` — the `Qwen3.8-27B-oQ4e-mtp` leg, repointed in this
  intervention's Phase −2 (`8ee4763`'s ancestor). **Available now**, not new work.
- `scripts/golden_v7/gemini_adjudicate.py` — the paired second-annotator leg, if a two-leg
  design is kept (open question, §5).
- `scripts/golden_v7/agreement.py`, `derive_thresholds.py` — downstream, unchanged.

## 4. Contamination boundary carried forward

`data/finetune/holdout_docs.json`'s pattern (document-level exclusion, ~30% of gold circulars
never mined for training pairs) is a golden-set concern, not a fine-tuning-specific one — any
future embedder/reranker work needs the same boundary. New rows drawn from the post-scrape
760 circulars not in the original 730 are automatically clean of this specific intervention's
training data (Phase 0/2 mined only from the frozen pre-scrape snapshot); a fresh holdout
split should still be drawn and recorded before any future training run reuses this larger set.

## 5. Cost — the actual constraint, stated honestly

Generation (query synthesis) is cheap and already proven at scale: Phase 1 of this
intervention generated 6,263 queries via `Qwen3.8-27B-oQ4e-mtp` in ~9h serial. **Adjudication,
not generation, is what gates this.**

Measured `local_adjudicate.py` throughput on the same 27B model (this intervention's Phase −2
probe): 17.7 tok/s median decode, 9.1s latency per 3-query call, **~1,190 rows/hr ceiling**
(`max_concurrent_requests: 1` serializes everything — no concurrency to exploit on this
hardware).

| Design | rows needed | adjudication legs | est. wall-clock |
|---|---|---|---|
| Single-leg (27B only, current `local_adjudicate.py` shape) | ~834 new | 1 | ~0.7h |
| Two-leg (27B + Gemini, current golden_v7 design) | ~834 new | 2, second leg is API-cost not wall-clock | ~0.7h local + Gemini API spend |
| From scratch to n=834 (not incremental) | 834 total | 1 | ~0.7h |

**This is materially cheaper than Phase 1's 9h synthesis run** — the 27B leg alone does not
gate the decision. The real open costs are upstream of adjudication: mining ~834 well-
distributed candidate rows across `golden_v7`'s 7 task_type strata (so the new set doesn't
just inflate `title_direct`/n, which is already saturated at 40/40 recall in every arm
measured so far) and, if the two-leg design is kept, Gemini API spend for the second
annotator — not estimated here, pricing-dependent, and worth pricing before committing.

## 6. Explicitly not decided here

- **Single-leg vs two-leg adjudication.** `golden_v7`'s existing design uses two independent
  annotators (`gemini_adjudicate.py` + `local_adjudicate.py`) reconciled via `agreement.py`.
  Keeping that design for the expansion preserves comparability but doubles the non-27B cost.
  Dropping to single-leg for the expansion only would create a mixed-provenance set requiring
  the same kind of provenance stamping `local_adjudicate.py`'s Phase −2 repoint already does
  for its own mixed-model rows.
- **Stratum allocation for the new ~618 rows.** A naive proportional split preserves current
  strata's SD structure; a targeted split (more `numeric_table`/`lineage_supersession`, the
  historically weak strata) would improve power exactly where it's needed but changes what
  the set represents. Needs a decision, not an assumption.
- **Whether n≈834 is funded at all.** ~0.7h of local decode is cheap; the mining, packet
  assembly, and (if two-leg) Gemini spend are the real budget line. This spec estimates the
  arithmetic; it does not recommend spending it without a named next intervention to spend it
  on — Finding 4 says "you can't measure your next attempt," not "build the eval set now
  regardless of what comes next."

## 7. Verification, if this is funded

1. New rows pass `scripts/golden_v7/validate_golden.py` unchanged.
2. `agreement.py` reports inter-annotator agreement on the new rows in the same range as the
   existing 216 (a large gap would mean the mining/pooling introduced a distribution shift).
3. Re-derive the paired-diff SD on the expanded set and confirm it actually clears the n≈834
   target for a 2pp ndcg delta — the SD is empirical, not guaranteed to hold as n grows.
4. `derive_thresholds.py` re-run before treating the expanded set as a new reporting gate.
