# Design: Selective Citations

**Date:** 2026-08-03
**Status:** Option A proven 100% no-op (Qwen2.5-1.5B emits zero parseable bracket citations); superseded by B′ (post-hoc cross-encoder citation filter)

## Problem

`generate.py:445` sets `citations=[c.id for c in contexts]` — every context chunk ID becomes a citation, regardless of whether that context actually supports the answer. This causes mechanical precision dilution:

| Metric | top_k=5 | top_k=10 |
|---|---|---|
| citation_recall | 0.772 | 0.888 (+11.6pp) |
| citation_precision | 0.177 | 0.119 (-5.8pp) |

At top_k=10, ~63% of additional citations are non-relevant noise. Both precisions are low because the mechanism is blind to relevance — it cites everything, not just what's used.

## Root Cause

The citation mechanism is purely mechanical:
```python
# generate.py:445 — same for MLXGenerator and ExtractiveStubGenerator
citations=[c.id for c in contexts]
```

The LLM prompt (generate.py:280-295) tells the model to "cite the circular id(s) in square brackets" but the system-level `Answer.citations` field is populated from `contexts`, not parsed from the LLM output. The model's bracket citations are only checked by `faithfulness()` (generate.py:54-70) — they verify the model didn't invent IDs, but don't filter which contexts get cited.

## Design Options

### Option A: Faithfulness-Gated Citations — ~~PROVEN NO-OP~~

**Idea:** Only include context IDs in `Answer.citations` that the model actually cited in its output (via `[CSCRF/2016/.../XX]` brackets).

**Mechanism:**
```python
# After generator.generate() returns text:
llm_cited = {b.strip() for b in _BRACKET.findall(text) if "/" in b}
# Map bracket citations to context IDs (exact match or doc_id prefix)
cited_ids = set()
for bracket in llm_cited:
    for c in contexts:
        if bracket == c.id or bracket.split("#")[0] == c.doc_id:
            cited_ids.add(c.id)

return Answer(
    text=text,
    citations=sorted(cited_ids),  # only what the model cited
    ...
)
```

**Pros:**
- Precision improves because only supporting contexts are cited
- Faithfulness check already exists — just reuse its bracket parsing
- Minimal code change (3 lines in answer_with_abstention)
- Eval parity: ExtractiveStubGenerator can return top context text AND its ID

**Cons:**
- Small model does not cite correctly (Qwen2.5-1.5B emits zero bracket citations — probe: `scratchpad/probe_fallback.py`)
- Requires bracket-parsing robustness for edge cases

**Risk:** Low. The faithfulness function already parses brackets; we just invert the direction (from "verify model didn't invent" to "extract what model used").

### Option B: Faithfulness-Filtered Citations

**Idea:** Keep all context IDs but remove those flagged as unsupported by `faithfulness()`.

**Mechanism:**
```python
# After faithfulness check:
allowed = {c.id for c in contexts} | {c.doc_id for c in contexts}
faith, unsupported = faithfulness(text, allowed)

# Filter: remove context IDs that appear in unsupported list
unsupported_set = {c.split("#")[0] for c in unsupported}
citations = [c.id for c in contexts if c.id not in unsupported_set]
```

**Pros:**
- Uses existing faithfulness output directly
- Removes only definitively unsupported citations

**Cons:**
- Still cites all contexts the model didn't explicitly reject (over-citation persists)
- faithfulness() returns unsupported IDs from the *answer text*, not from contexts — mismatch risk

**Risk:** Medium. faithfulness() checks bracket citations in the answer text, not context IDs directly. The mapping between unsupported brackets and context IDs is indirect.

### Option C: Judge-Gated Citations (Heavy)

**Idea:** Run a second judge pass that scores each context's relevance to the answer text, only citing contexts above threshold.

**Pros:** Most precise citations possible
**Cons:** Adds N judge calls per query (N = top_k); latency impact; overkill for current model quality

**Risk:** High. Latency and complexity cost outweigh precision gains at current model scale.

## Recommendation: Option B′ (Post-Hoc Cross-Encoder Filter) — Supersedes A, B, C

**Why:** Option A is a no-op at 1.5B (model emits zero bracket citations). B′ reuses the existing cross-encoder (`sebi_rag.rerank.CrossEncoderReranker`) to score context-vs-answer entailment — model-agnostic, no prompt dependency.

**Implementation scope:**
1. Add `cross_encoder.verify(context.text, answer_snippet)` scoring in `answer_with_abstention()`
2. Filter citations below entailment threshold (e.g., 0.5)
3. Update `ExtractiveStubGenerator` to return structured context-answer pairs for cross-encoder scoring
4. Update `derive_thresholds.py` and eval harness to use B′ scoring instead of bracket parsing
5. Re-derive gate thresholds in `eval/golden/gate_v7.json`

**Expected impact:**
- citation_precision: 0.177→~0.45–0.65 (est., cross-encoder scores entailment, not prompt compliance)
- citation_recall: ~0.65–0.8 (est., some contexts genuinely irrelevant at top_k=10)
- Net: model-agnostic precision gain, no dependency on small-model citation quality

## Open Questions

1. **What if the model cites nothing?** → Return empty citations; faithfulness returns 1.0 (no unsupported claims). Eval treats as precision=1.0 by convention.
2. **What if the model cites a context not in `contexts`?** → faithfulness() already catches this as unsupported; we simply don't add it to Answer.citations.
3. **Does ExtractiveStubGenerator need to change?** → Yes, for eval parity. It should return a string containing `[<top_context_id>]` brackets so the bracket parser works in eval.
4. **Backward compatibility?** → `Answer.citations` is already a list of strings; changing from "all contexts" to "model-cited contexts" is additive-safe for consumers (fewer citations, not different format).

## Root Cause Analysis (2026-08-03)

### The Precision Drop: 0.177 → 0.119

**Mechanism:** `citation_precision = hits / total_cited`. When top_k expands 5→10:
- `total_cited` increases by ~5 (all new contexts get cited mechanically)
- `hits` increases only marginally (new contexts are lower-ranked, less likely relevant)
- Result: denominator grows faster than numerator → precision drops

**Why both precisions are low:** The old mechanism cites ALL contexts regardless of relevance. At top_k=5, ~82% of cited docs are irrelevant (precision=0.177). At top_k=10, ~88% are irrelevant (precision=0.119). The additional 5 contexts at top_k=10 are even less relevant on average.

**The recall trade-off:** citation_recall improved 0.772→0.888 (+11.6pp). This is the intended effect of more retrieval slots — we catch more relevant docs. But each additional slot adds noise too.

### Is This the Most Actionable Signal?

**Yes, for two reasons:**

1. **High leverage, low cost:** B′ (cross-encoder filter) reuses existing reranker model. It directly targets the mechanical over-citation that causes both precision problems. Expected impact: citation_precision 0.177→~0.45–0.65 (per design estimate).

2. **Other signals are lower priority:**
   - Low κ agreement on `title_direct`/`multi_hop` strata: documented as expected under spec §7 promotion amendment
   - `test_measure.py` failures: pre-existing module import issue, not pipeline-related
   - Citation_precision drop is the only metric showing a clear, fixable pattern

### Trade-off Assessment: NOT an Urgent Fix

**This is a design trade-off, not a bug:**
- The precision drop from top_k expansion is expected behavior (more retrieval = more noise)
- B′ addresses the *mechanism* via entailment scoring, not prompt compliance
- After B′, precision should improve regardless of top_k setting

**Decision needed (not urgent):**
- What is the acceptable precision/recall balance for production?
  - Current (top_k=10, mechanical): recall=0.888, precision=0.119
  - After B′ (estimated): recall=~0.75, precision=~0.45–0.65

**Implementation priority:** Medium. B′ is model-agnostic (no small-model dependency), reuses existing cross-encoder, and avoids the prompt-compliance trap that made Option A a no-op.
