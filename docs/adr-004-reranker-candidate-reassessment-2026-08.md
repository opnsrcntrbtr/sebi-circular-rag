# ADR-004: Reranker candidate reassessment — jina-reranker-v3-mlx (Aug 2026)

**Status:** Accepted — candidate sanctioned, benchmarked, and **ADOPTED 2026-08-24 by
explicit owner override** of this ADR's own §Method decision rule. See §Owner override
below. Production reranker is jina-reranker-v3-mlx as of this date.
**Date:** 2026-08-24
**Deciders:** Ian (owner)

## Context

ADR-001 D2 (2026-07-02) names the sanctioned reranker benchmark candidates as
Qwen3-Reranker-0.6B/4B via MLX. That candidate was tried and **rejected**
(2026-07-02): AUROC 0.799 vs the bge-reranker-v2-m3 baseline's 0.812, worse
citation precision (0.72 vs 0.80 @top_k=3), 4.82 vs 2.24 s/query. D2's
sanctioned-candidate list has not been revisited since — it predates
`jina-reranker-v3` (arXiv:2509.25085, published Sept 2025) entirely, and the
project's own 2026-08-19/20 research roadmap independently flagged the same
architectural gap (R4: "reranker architecture — inter-passage attention",
pointing at the academic Set-Encoder paper) without connecting it to a
shipped, MLX-native model that already exists.

## Decision

Add **`jina-reranker-v3-mlx`** (`jinaai/jina-reranker-v3-mlx` on Hugging Face)
to D2's sanctioned reranker benchmark candidates. Same evidence bar as every
prior candidate: **adoption only on measured benefit on SEBI data, not on the
vendor's own benchmark.**

**Why this candidate, verified against primary sources (not aggregator
listicles — see rationale below):**

- **Listwise, not pointwise.** Causal self-attention across up to 64
  candidates in one forward pass ("last but not late interaction"), vs
  bge-reranker-v2-m3's independent (query, doc) pairs. This is the same
  property R4 wanted from Set-Encoder, but as a pretrained, shipped model
  rather than a from-scratch implementation.
- **BEIR nDCG@10 61.85 vs bge-reranker-v2-m3's 56.51** (same 0.6B weight
  class) — paper's own number, a **hypothesis this ADR's benchmark tests**,
  not evidence for SEBI circulars. No legal/regulatory-domain evaluation
  appears in the paper (BEIR/MIRACL/MKQA/CoIR only).
- **Official MLX port** (`jinaai/jina-reranker-v3-mlx`): matches the
  original's scores exactly, 1.2 GB quantized, `mlx` + `mlx-lm` only (already
  a project dependency via `MLXGenerator`) — no new heavy dependency, and it
  meets ADR-003's MLX-native preference directly rather than requiring a
  PyTorch/MPS path like `CrossEncoderReranker` (which already needed a CPU
  fallback for MPS segfaults, 2026-08-23).
- **License: CC BY-NC 4.0** — weights and the vendor's reference inference
  code, non-commercial use only. Confirmed acceptable for this project
  (local-first research use, no commercial distribution). Revisit this ADR if
  that changes.

**A discarded finding, recorded so it isn't re-searched.** A first broad
research pass returned mostly SEO-listicle content ("Best Reranker Models
2026" aggregator blogs) with unverifiable or inconsistent claims. None of
that is cited above — every claim in this ADR was checked against the arXiv
paper and the actual Hugging Face model card/repo file listing, matching this
project's standing rule (`docs/research-synthesis-2026-08-19.md`) that
external claims need primary-source verification before they inform a
decision.

## Method (binding on the benchmark, per D1/D2's evidence bar)

**Two isolated arms, not one conflated measurement.** `bge-reranker-v2-m3`
currently plays two roles: `pipeline.reranker` (orders the retrieval pool)
*and*, via `citation_scorer_for(backend="reranker")`, the scorer B′ uses to
select citations. R1 (2026-08-23, rejected) showed the citation-scoring role
is independently fragile — a scorer that improves retrieval ordering is not
guaranteed to improve citation selection, and conflating the two would make a
failure uninterpretable (which role broke it?).

- **Arm 1 (primary, decisive).** Swap only `pipeline.reranker`. Citation
  scoring stays on the existing bge-reranker-v2-m3, explicitly, not by
  following whatever `pipeline.reranker` becomes. Measured via
  `bench_retrieval.py --rerank --reranker jina` (recall@10, nDCG@10) against
  the existing `--reranker crossencoder` baseline, same methodology as the
  2026-08-22 E5 benchmark (recall@10 0.9560).
- **Arm 2 (exploratory, non-decisive).** Same cohort methodology R1 just used
  (`scripts/analysis/warrant_scorer_cohort.py`'s pattern), Jina as the
  citation scorer instead of the warrant judge or cross-encoder. Reported,
  but does not gate Arm 1's adoption decision — if interesting, it is a
  **separate future preregistration**, exactly as R1 was for the warrant
  criterion.

**Decision rule, fixed in advance:** adopt Arm 1 only on **≥10% measurable
benefit** (recall@10 or nDCG@10 — D1's own language) **with no recall
regression**, confirmed on golden_v7/E4, not the paper's BEIR number.
**Guardrail:** full `make test` + `eval-asof` + `validate-corpus` must stay
green before anything touches `config.toml`.

## Owner override (2026-08-24, after Arm 1's result)

Arm 1 measured recall@10 +2.42% and nDCG@10 +6.76% vs bge-reranker-v2-m3, both positive, no
regression on either metric — but neither cleared the §Method decision rule's preregistered
≥10% relative bar, so the run was recorded as **REJECTED** on 2026-08-24
(`docs/status.md` 2026-08-24, "ADR-004 Arm 1... REJECTED").

**The owner (Ian) explicitly directed overriding that bar and adopting jina-reranker-v3-mlx
anyway**, on the following rationale:

1. **The measured result is a real, consistent, non-regressive improvement**, not noise in the
   wrong direction or a mixed result. The ≥10% bar (inherited from ADR-001 D1) is a self-imposed
   discipline threshold, not a correctness requirement — the owner judged a smaller-but-real gain
   worth taking for a project without competing candidates under active development.
2. **The candidate's claims were verified against primary sources before this decision**, not
   taken from aggregator content: the arXiv paper (2509.25085) directly, and the actual Hugging
   Face model repository file listing and model card (`jinaai/jina-reranker-v3-mlx`), fetched and
   read rather than summarized secondhand. This is the same standard `docs/research-synthesis-2026-08-19.md`
   established after catching misattributed claims in an earlier agent-produced synthesis — the
   Jina v3 evidence in this ADR's §Decision was held to it before adoption was ever on the table,
   not retrofitted to justify the override afterward.
3. **No regression, confirmed empirically, not assumed.** Arm 1's own numbers already show no
   regression on the two measured retrieval metrics. Adoption is further gated on the guardrail
   this ADR always required regardless of the primary bar (§Method: "full `make test` +
   `eval-asof` + `validate-corpus` must stay green") plus a full-gate check against
   `eval/golden/gate_v7.json`'s existing floors — recorded in `docs/status.md` 2026-08-24 alongside
   this adoption, not skipped because the owner authorized the bar override.

**This is recorded as a deliberate deviation, not a retroactive rewrite.** The original §Method
decision rule text above is unchanged and still describes what was preregistered and what Arm 1's
result actually was against it — matching this project's standing practice (e.g. the
`superseded_penalty` confirmatory run, "recorded as a deviation rather than rewritten"). The
preregistration document itself
(`docs/superpowers/specs/2026-08-24-jina-reranker-v3-prereg.md`) carries a dated addendum
recording the same override at the level of that document, rather than editing §3/§4's original
text.

**New acceptance criterion, in force from this date for reranker candidates:** positive delta on
recall@10 or nDCG@10, no regression on either, per owner decision — not a numeric floor. This
does not retroactively re-open Qwen3-Reranker (rejected 2026-07-02 on a *negative* AUROC delta,
which fails this criterion too, not just the old one).

**Score-scale consequence, handled before shipping, not after.** jina-reranker-v3's score
distribution is not bge-reranker-v2-m3's (median top-score 0.45 vs 0.98; can be negative, bge
never is — measured on this same golden_v7 cohort). `abstain_threshold` was recalibrated
specifically for Jina's distribution before adoption
(`scripts/analysis/jina_abstain_threshold_calibration.py`,
`reports/jina-abstain-threshold-calibration-2026-08-24.json`): 0.12, catching 25 of 41 true
abstentions at a cost of 1 of 219 false abstentions (bge's 0.05 catches 29/41 at a cost of 2/204 —
Jina's abstain/answerable populations separate less cleanly on this signal alone, so the owner's
choice among the measured operating points trades catch rate for an even lower false-abstention
cost). `citation_margin` (0.35) is untouched — citation scoring stays on bge-reranker-v2-m3 per
the Arm 1/Arm 2 decoupling design, unaffected by this change.

## Consequences

- Easier: a listwise reranker is now benchmarkable without implementing one
  from scratch (Set-Encoder, R4's academic candidate, remains available if
  this arm fails or if a permissively-licensed alternative is later needed).
- Harder: CC BY-NC 4.0 constrains where this can ship if the project's use
  case ever changes; `--reranker jina` adds a `huggingface_hub` snapshot
  download + dynamic module load, a slightly heavier dependency surface than
  `CrossEncoderReranker`'s `sentence-transformers` import.
- Revisit: if Arm 1 fails, D2's candidate list still has Set-Encoder (R4) as
  an unexplored, permissively-licensed alternative with the same
  inter-passage rationale.

## References

- arXiv:2509.25085 — jina-reranker-v3: Last but Not Late Interaction for
  Document Reranking
- `jinaai/jina-reranker-v3-mlx` (Hugging Face) — official MLX port
- `docs/research-roadmap-2026-08-19.md` R4 — the academic alternative
  (Set-Encoder, arXiv:2404.06912) this ADR's candidate substitutes a shipped
  model for
- `docs/status.md` 2026-08-23 — R1 warrant-scorer rejection, the source of
  this ADR's Arm 1/Arm 2 decoupling requirement
