# ADR-002: Certainty Signals, Abstention Reasons, and Advisory Mode

**Status:** Accepted
**Date:** 2026-07-02
**Deciders:** Ian (owner)
**Trigger:** A `/query` with `"top_k": 0` silently abstained despite perfect
retrieval (top rerank ~0.99, correct CSCRF chunks) — `reranked[:0]` produced
empty context, the subject-sim gate correctly returned False for no context,
and the response gave the client no way to see why.

## Context

The user requirement was "always generate an answer with a parameter indicating
certainty". This conflicts with D5 (never emit unsupported legal conclusions)
if read literally: eval evidence shows raw model scores are not certainty
(hard-negative hn-steward scored 0.985 on the cross-encoder; reranker AUROC
0.81). The accepted design keeps abstention authoritative while making every
response carry the certainty evidence and, on explicit opt-in, a clearly
labelled best-effort draft.

## Decision

1. **Input validation.** `top_k` is `Field(ge=1, le=10)`; `0` → HTTP 422.
   Degenerate inputs must fail loudly, not abstain silently.
2. **Confidence block on every response.** `confidence = {rerank_top, margin,
   subject_sim}` — signals already computed by the pipeline, previously
   discarded. Populated on abstentions too.
3. **`abstention_reason` enum:** `no_context | score_floor | subject_gate`.
   Distinguishes client error, far-domain, and near-domain-ungoverned.
4. **Banded `certainty` (high | medium | low), not a probability.** With 56
   golden items a fitted calibrator would overfit; bands are empirically
   anchored and auditable: **high** = passed both gates ∧ subject_sim ≥ 0.65
   (region with 100% citation recall on golden_v5, eval_gate 2026-07-02) ∧
   faithfulness 1.0; **medium** = passed gates otherwise (or no gate wired);
   **low** = any gate failed (always on abstention). Revisit a fitted
   calibrator when the golden set reaches ~200 items.
5. **Advisory mode (opt-in, per-request `"advisory": true`).** On
   `score_floor`/`subject_gate` abstention with non-empty context, the response
   additionally carries `draft_answer` prefixed "LOW CONFIDENCE — not
   regulatory guidance…". The authoritative `answer`/`abstained` fields are
   untouched (D5 preserved; compliance consumers unaffected). Never produced
   for `no_context`; never the default.

## Consequences

- Clients can always render an answer-like object with certainty metadata;
  silent abstentions are gone (reason + signals always present).
- Response schema grows four fields (additive — n8n smoketest and existing
  consumers unaffected).
- Advisory drafts are ungated LLM output over weakly-matched context: they can
  be wrong. The prefix is mandatory and the field name is deliberately not
  `answer`. UI must render it visually distinct.
- Band boundaries (0.65 subject-sim) are corpus/calibration-coupled: re-verify
  at each recalibration alongside top_k/threshold (§7 rule).

## Amendment (2026-07-02): two-tier subject/section gate

Live false abstention ("What is a regulated entity?", top_k=1): evidence was
section-level, gate was doc-subject-level. Eval on golden_v5 @ 207 circulars:
plain max(subject, section) at one threshold REJECTED (hard negatives regress,
hn-settle 0.493 crosses 0.42). ADOPTED: **grounded = subject_sim ≥ 0.42 OR
section_sim ≥ 0.60** — legit section matches scored ≥ 0.62, max section-driven
hard negative 0.493 (margin 0.107); provably additive-only on golden_v5.
`confidence` gains `section_sim`. Env: SEBI_RAG_SECT_THRESHOLD (default 0.60,
"off" disables). Re-verify both bars at each recalibration.

## Action Items

1. [x] Implementation + 6 offline certainty tests + 3 api tests (2026-07-02).
2. [ ] Re-verify the 0.65 high-band boundary at the next recalibration
       (now also the 0.42/0.60 gate bars — single review).
3. [ ] Fitted calibrator (logistic/isotonic) once golden set ≥ ~200 items.
