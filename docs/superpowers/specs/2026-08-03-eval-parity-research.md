# Research: Eval Pipeline Citation Parity

**Date:** 2026-08-03
**Status:** Option A proven no-op (Qwen2.5-1.5B emits zero bracket citations); stub changes must support B′ cross-encoder scoring, not bracket parsing

## Current State

### Citation Mechanism (generate.py:445)
```python
citations=[c.id for c in contexts]  # ALL context IDs, regardless of generator
```

This is **decoupled from the generator**. Both `ExtractiveStubGenerator` and `MLXGenerator` produce identical `Answer.citations` — every context ID becomes a citation.

### Generator Behaviors

| Generator | `generate()` output | `Answer.citations` source |
|---|---|---|
| `ExtractiveStubGenerator` | `contexts[0].text` (raw top context) | `[c.id for c in contexts]` (all contexts) |
| `MLXGenerator` | Bracket-cited answer text `[CSCRF/.../XX]` | `[c.id for c in contexts]` (all contexts) |

### Usage Distribution

| Script | Generator | Purpose |
|---|---|---|
| `bench_generators.py` | `MLXGenerator` | Model comparison (faithfulness, citation metrics) |
| `eval_json.py` | `ExtractiveStubGenerator` | Golden-set scoring (v5, v7) |
| `derive_thresholds.py` | `ExtractiveStubGenerator` | Floor derivation |
| `bench_retrieval.py` | `ExtractiveStubGenerator` | Retrieval-only benchmarks |
| `bench_metrics.py` | `ExtractiveStubGenerator` | Metric comparison (retrieval/rerank) |
| `eval_asof.py` | `ExtractiveStubGenerator` | As-of-date evaluation |
| API `/query?mode=retrieval_only` | `ExtractiveStubGenerator` | Retrieval-only API mode |

## The Parity Question

**Should `ExtractiveStubGenerator` mirror production citation behavior?**

### Current Answer: No (but changing)

Currently, the stub doesn't need to mirror production because **the citation mechanism is already decoupled** — `answer_with_abstention()` sets citations from contexts regardless of generator. The stub's job is to return deterministic text for retrieval testing; citations are a pipeline concern, not a generator concern.

### After B′ (Post-Hoc Cross-Encoder Filter) — Supersedes Option A

B′ scores each context-vs-answer pair via the existing `CrossEncoderReranker`. The stub **must** change because:
1. `answer_with_abstention()` will call cross-encoder on each context vs answer text
2. The stub returns raw text with no structured context-answer pairs → cross-encoder can't score
3. Eval citation metrics would be meaningless (no scoring possible)

### Recommendation: Align with B′-Ready Stub Modification

**Update the stub to return structured context-answer pairs for cross-encoder scoring:**

```python
class ExtractiveStubGenerator:
    """Deterministic: returns top context text with structured citation info for B′ scoring."""

    def generate(self, query: str, contexts: list[Chunk]) -> dict | str:
        if not contexts:
            return ABSTAIN
        # Return a dict with text and context metadata so B′ cross-encoder
        # can score each context-vs-answer entailment.
        top = contexts[0]
        return {
            "text": f"[{top.id}] {top.text}",
            "context_id": top.id,
            "context_text": top.text,
        }
```

**Why this is safe:**
- The stub still returns deterministic output (no model dependency)
- Structured format enables B′ cross-encoder scoring of context-vs-answer entailment
- Eval citation metrics become meaningful (stub cites top context, which is the only "used" context)
- Retrieval benchmarks unaffected (they test `recall_at_k`, `mrr`, `ndcg` on retrieved docs, not citations)


### Alternative: Keep Divergent (Not Recommended)

Keep stub returning raw text and accept that citation metrics are only measured with `MLXGenerator`. This means:
- Golden-set scoring (eval_json.py, derive_thresholds.py) reports citation metrics from a mechanism that doesn't exist in the stub
- Benchmarks report different numbers depending on which generator is wired
- Harder to reason about whether a citation metric change came from the mechanism or the generator

**Verdict:** Divergence is confusing. Aligning via a one-line stub change is cleaner.

## Impact Assessment

| Metric | Before (all contexts) | After B′ + aligned stub |
|---|---|---|
| citation_precision (stub) | 0.177-0.119 (mechanical noise) | ~0.8-0.95 (stub cites top context, which is relevant) |
| citation_precision (MLX) | 0.177-0.119 | ~0.45-0.65 (est., cross-encoder scores entailment) |
| citation_recall (stub) | 0.772-0.888 | ~0.5-0.7 (stub only cites top context) |
| citation_recall (MLX) | 0.772-0.888 | ~0.65-0.8 (est., cross-encoder filters low-scoring contexts) |

**Key insight:** The stub's citation_recall will drop because it only cites the top context. This is actually *more honest* — the stub returns one chunk's text, so citing only that chunk is correct behavior. The current mechanical "cite all contexts" was misleading for the stub.

## Implementation Order (for B′ adoption)

1. Update `ExtractiveStubGenerator.generate()` to return structured context-answer pairs for cross-encoder scoring
2. Add `cross_encoder.verify(context.text, answer_snippet)` in `answer_with_abstention()` (B′)
3. Update eval harness: handle cross-encoder scoring in stub mode; keep `cprec=1.0` when no contexts scored above threshold
4. Re-run `bench_generators.py` to measure new citation metrics across models with B′ filtering
