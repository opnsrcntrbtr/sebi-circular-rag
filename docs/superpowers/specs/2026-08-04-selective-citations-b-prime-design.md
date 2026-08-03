# Design: Selective Citations B′ — Post-hoc Cross-Encoder Filter

**Date:** 2026-08-04
**Status:** Design approved; ready for implementation plan
**Supersedes:** Issue-3 section of `2026-08-03-golden-v7-eval-artifacts-remediation.md`
(tasks #2/#4/#5) and the inert Option A in `2026-08-03-selective-citations-design.md`.

## Problem

`answer_with_abstention()` populates `Answer.citations` from **all** deduped
contexts. Option A (parse the model's `[ID]` brackets) was implemented uncommitted
(`generate.py:446-455`) but is a **100% no-op**: a probe (50 golden rows, real
MLXGenerator) showed Qwen2.5-1.5B emits parseable brackets **0/48** times, so it
always falls back to citing every context; and `ExtractiveStubGenerator` bracket-
cites all contexts, defeating it in eval too. Result: citation_precision stays at
mechanical-noise levels (0.119 at top_k=10) in both eval and production.

## Goal

Cite only the contexts the answer actually rests on, **model-agnostically**, so that
eval (stub) and production (MLX) measure the same behavior. Improve citation_precision
without collapsing citation_recall; re-arm the gate honestly.

## Key Decisions (locked)

1. **Selection rule: relative margin, keep ≥1.** Keep contexts whose answer-relevance
   score is within `margin` of the top context's score; always keep the single highest.
   Self-calibrating per query, robust to the cross-encoder's uncalibrated score scale,
   and never emits zero citations on a grounded answer.
2. **Gate policy: re-derive floors + add a `citation_precision` floor.** Re-derive
   recall/citation_recall/abstention floors at the new operating point AND add
   citation_precision to the gated metrics, so the gate protects the metric B′ improves
   and catches a future regression of the precision win.

## Mechanism (no new model, no new method)

`CrossEncoderReranker.rerank(query, candidates)` scores `[query, c.text]` pairs
(`rerank.py:134`). Passing the **answer** as `query` yields per-context answer-relevance
scores directly. The same `Reranker` the pipeline already holds is reused — CrossEncoder
in prod/eval, `LexicalReranker` in tests (deterministic).

### New pure function (`generate.py`)

```python
def select_citations(answer_text: str, contexts: list[Chunk],
                     scorer: Reranker, margin: float) -> list[str]:
    """Context ids the answer rests on: score each context's answer-relevance
    via scorer.rerank(answer_text, contexts), keep those within `margin` of the
    top score, always keep >=1 (the top). Empty contexts -> []. Ids returned in
    the contexts' original order (stable output)."""
    if not contexts:
        return []
    scored = scorer.rerank(answer_text, contexts)          # [(chunk, score)] desc
    top = scored[0][1]
    kept = [c for c, s in scored if s >= top - margin] or [scored[0][0]]
    order = {c.id: i for i, c in enumerate(contexts)}
    return sorted((c.id for c in kept), key=order.get)
```

### Wiring

- `answer_with_abstention(..., citation_scorer: Reranker | None = None, citation_margin: float = _CITATION_MARGIN_DEFAULT)`.
  `None` → current behavior (all context ids; backward-compatible, off by default).
  Set → `citations = select_citations(text, contexts, citation_scorer, citation_margin)`.
  This **replaces** the inert Option A block at `generate.py:446-455`.
  `_CITATION_MARGIN_DEFAULT` is a module constant (provisional value in the plan, finalized
  by calibration).
- `RAGPipeline` gains `selective_citations: bool = False` and `citation_margin: float = _CITATION_MARGIN_DEFAULT`.
  `query()` (`pipeline.py:75`) passes `citation_scorer=self.reranker if self.selective_citations else None`
  and `citation_margin=self.citation_margin`.
- Enable in eval/prod via env `SEBI_RAG_SELECTIVE_CITATIONS` (on/off) and
  `SEBI_RAG_CITATION_MARGIN` (override the default), parsed in `Settings` /
  `build_default_pipeline` / `eval_json.py` / `derive_thresholds.py`, once the gate re-arms.

### Supersede Option A

- Delete the bracket-parse block (`generate.py:446-455`).
- Revert `ExtractiveStubGenerator.generate()` to `return contexts[0].text` (no brackets).
  With B′, citations come from `select_citations`, not bracket parsing. `faithfulness()`
  stays as the invented-id guard on real model output; on the bracket-free stub it returns
  `(1.0, [])`, which is correct.
- `pipeline.py`'s `_BRACKET.sub(...)` supersession/repealed-note text scan becomes near-moot
  (model rarely brackets). **Left unchanged in v1**; flagged as a follow-up to key those
  notes off `ans.citations` instead of raw-text scanning.

## Eval / Gate

- `eval_json.py` and `derive_thresholds.py` build the pipeline with `ExtractiveStubGenerator`
  + `CrossEncoderReranker`. Set `selective_citations=True` there so the citation metrics
  reflect the production filter (same cross-encoder) → eval == production.
- `derive_thresholds.py`: add `citation_precision` to `_GATED_METRICS` and `_FLOOR_NAMES`
  (`{"citation_precision": "citation_precision"}`). No other change: `gate_select.floors_ok`
  iterates `floors.items()` generically (verified), and `eval_json.py` already emits
  `citation_precision` in its gate_report — so both consume the new floor with zero edits.
- Re-run `make golden-v7-gate` with B′ enabled to re-derive and re-arm `gate_v7.json`.

## v1 Scope Choices

- **Full-answer scoring** (not per-sentence): simpler, deterministic, ~one extra rerank
  batch of latency. Per-sentence attribution deferred.
- **`margin` scale and default:** the margin is on the **sigmoid (0–1) score scale** —
  the same scale as `abstain_threshold` (0.4) and `score_floor` (0.05), since
  `CrossEncoder.predict` on the single-label bge-reranker head returns sigmoid scores and
  `answer_with_abstention` already compares `reranked[i][1]` against those thresholds
  (NOT raw logits). "Within `margin` of top" therefore means e.g. `margin=0.15` keeps
  contexts scoring ≥ (top − 0.15) on the 0–1 scale. Provisional `_CITATION_MARGIN_DEFAULT`
  (0.15) pinned in the plan, finalized by a small `calibrate.py` sweep on the golden set
  (maximize citation_precision subject to citation_recall staying within an acceptable
  band). Tests pass `margin` explicitly.
- **Off by default** (`selective_citations=False`), flipped on only after the gate
  re-arms cleanly.
- **≥1 citation floor** is non-negotiable (protects faithfulness UX and bounds recall loss).

## Testing (TDD)

Offline unit (LexicalReranker / fakes — deterministic):
1. `select_citations` keeps only within-margin contexts.
2. `select_citations` always keeps ≥1 when all are below margin.
3. `select_citations` empty contexts → `[]`.
4. `select_citations` returns ids in stable (original context) order.
5. `answer_with_abstention` with `citation_scorer` set → filtered citations (fewer than
   all when contexts vary in relevance).
6. `answer_with_abstention` without scorer → unchanged (all context ids) — backward compat.
7. `RAGPipeline.query(selective_citations=True)` → filtered citations end-to-end.
8. `ExtractiveStubGenerator.generate()` returns plain top-context text (no brackets);
   update any test asserting the old bracket output.
9. `derive_thresholds.derive_floors` emits a `citation_precision` floor from a synthetic
   vector (gated-metric wiring).

Scripted verification (needs MPS + persisted index — not in offline suite):
- `make golden-v7-gate` with B′ → gate_v7.json gains a citation_precision floor,
  citation_recall floor drops but stays > 0, gate arms; `make eval-asof` / `eval_json`
  report passes `floors_ok`.

## Constraints Honored

- No `CircularMeta` fields added (`.claude/rules/circular-meta.md`).
- No `*_spaces.py` touched (`.claude/rules/two-paths.md`).
- Reuses the existing cross-encoder — no new model/dependency.
- Offline suite (654 tests) stays green; adds the tests above.

## Risks

- **Latency.** B′ adds one extra `reranker.rerank(answer, contexts)` call per answered
  query (on top of the existing question-vs-candidates rerank). For CrossEncoder that is a
  single batched `predict` over `top_k` pairs (bounded by `batch_size`) — measurable but
  small (~tens of ms). Abstain rows skip it (no answer to score).
- **Recall drop below a usable level.** Mitigated by keep-≥1 and the calibration sweep; if
  the sweep can't hold citation_recall in band, revisit margin or fall back to top-N.
- **Cross-encoder(answer, context) as a support proxy.** It scores relevance, not strict
  entailment; acceptable for v1 (design Option B), revisit with NLI if precision underperforms.
- **Gate masking.** Re-deriving citation_recall lower is honest only because we simultaneously
  add a citation_precision floor; document both floors' rationale in `gate_v7.json` context.
