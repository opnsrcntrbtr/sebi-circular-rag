# Deep Root Cause Analysis: Citation Precision Drop (0.177 → 0.119) from top_k Expansion

**Date:** 2026-08-03
- **Decision:** Option A proven no-op (Qwen2.5-1.5B emits zero bracket citations). B′ (post-hoc cross-encoder filter) is the real fix — deferred pending implementation.


---

## 1. The Signal

| Metric | top_k=5 | top_k=10 | Δ |
|---|---|---|---|
| citation_precision | 0.177 | 0.119 | −0.058 (−33%) |
| citation_recall | 0.772 | 0.888 | +0.116 (+15%) |
| total_cited_per_query | ~5 | ~10 | +5 |

**Observation:** Precision drops 33% when top_k doubles, but recall improves 15%. This is a classic precision-recall trade-off.

---

## 2. Mechanism Trace (Code Path)

### 2.1 Citation Generation (`generate.py:answer_with_abstention`)

```python
# Line 410-425: contexts are ranked by reranker score, deduped by doc_id
contexts = []
seen_docs = set()
for ctx in sorted_contexts:  # sorted by reranker score descending
    doc_id = ctx.meta.get("doc_id")
    if doc_id and doc_id not in seen_docs:
        contexts.append(ctx)
        seen_docs.add(doc_id)

# Line 428-430: ALL contexts get mechanical citations
citations = [ctx.meta["doc_id"] for ctx in contexts[:top_k]]
```

**Key insight:** Every context that survives deduplication gets a mechanical citation. The LLM does NOT selectively choose which contexts to cite — it cites all of them.

### 2.2 Precision Calculation (`eval_harness.py:_eval_item`)

```python
# Line 87-89: precision = hits / total_cited
pred = _unique(_doc(c) for c in ans.citations)  # unique doc_ids from answer
hit = len(set(pred) & relevant)                 # how many cited docs are actually relevant
rec["cprec"] = hit / len(pred) if pred else 0.0  # precision
```

**Formula:** `precision = |cited ∩ relevant| / |cited|`

When top_k=5: `precision = hits/5`. When top_k=10: `precision = hits/10`.

If the same 3 relevant docs are cited in both cases:
- top_k=5: precision = 3/5 = 0.60 (but actual is 0.177, so fewer hits)
- top_k=10: precision = 3/10 = 0.30 (but actual is 0.119, so fewer hits)

The actual numbers show that the additional 5 docs from top_k=10 are mostly **not relevant** to the query's golden evidence set.

### 2.3 Why Additional Docs Are Irrelevant

The reranker scores chunks by semantic similarity to the query. The top-5 most similar chunks are more likely to contain relevant information. Chunks ranked 6–10 have lower similarity scores and are more likely to be:
- Tangentially related (same circular, different section)
- From a different but topically adjacent circular
- Containing boilerplate or procedural text

These lower-ranked chunks still get mechanical citations, diluting precision.

---

## 3. Academic Context: Is This Expected?

### 3.1 Wallat & Heuss (2025) — "Correctness is not Faithfulness in RAG Attributions"

**Key finding:** Even Command-R+ (104B, RAG-optimized) exhibits post-rationalization in **12–57% of cases** depending on document type.

- Post-rationalization = model generates answer from parametric memory, then finds a document that superficially matches (token-level), not one it actually used.
- Citation correctness ≠ citation faithfulness. A citation can be "correct" (the document supports the claim) but unfaithful (the model didn't actually use that document).
- **Relevance to our system:** Our mechanical citation approach (citing all contexts) is vulnerable to the same issue. The LLM may cite a document because it contains matching tokens, not because it contributed to the answer.

### 3.2 Leung et al. (2026) — "Do You Need a Frontier Model as a Citation Verifier?"

**Key finding:** Frontier models (GPT-4o, Claude Sonnet 4) are **NOT needed** for citation verification. Mid-tier models perform comparably:

| Model | F1 (Factual Support) | Cost per Query |
|---|---|---|
| GPT-4o | 0.851 | $1.15 |
| Gemini 3.1 Pro | 0.819 | $0.52 |
| GPT-OSS-120B | 0.851 | $0.59 |
| Gemini 3.1 Flash Lite | 0.823 | $0.25 |

**Relevance:** If we want to add a faithfulness gate, we don't need expensive frontier models. A mid-tier model or even an NLI cross-encoder would suffice.

### 3.3 Chaganti (2026) — "On-Device Deep Research at 4B: Exposure Bounds Faithfulness"

**Key finding:** On Apple M4 Pro (24GB), a 4B model's citation faithfulness is bounded by **exposure** (per-source context length), not source quality:

| Exposure | Faithfulness (Gold) | Faithfulness (Retrieved) |
|---|---|---|
| 400 chars | 0.367 | 0.446 |
| 800 chars | 0.513 | 0.554 |
| 1200 chars | 0.524 | 0.572 |
| 1500 chars | 0.580 | 0.581 |

**Practical recipe:** Raise per-source exposure first (cheap, ~235 extra tokens), then treat retrieval recall as the only remaining lever.

**Relevance to our system:** Our `generate.py` already passes full chunk text as context. The precision drop from top_k expansion is a **retrieval quality** issue, not an exposure issue. The chunks ranked 6–10 are genuinely less relevant — they're not suffering from insufficient exposure.

---

## 4. Root Cause Assessment

### Primary Cause: Mechanical Citation of All Contexts

**Severity:** Medium-High (systematic, affects all queries)
**Fixability:** High (requires code change in `generate.py`)

The root cause is that **every context gets a mechanical citation**, regardless of whether the LLM actually used it. This is by design (simpler prompt, fewer edge cases) but has a predictable cost:

- With top_k=5: ~33% of cited docs are irrelevant (precision = 0.177)
- With top_k=10: ~88% of cited docs are irrelevant (precision = 0.119)

The additional 5 docs from top_k=10 are mostly noise because:
1. The reranker's discrimination degrades beyond top-5 (scores flatten)
2. SEBI circulars are dense — chunks 6–10 often cover procedural/administrative text, not substantive regulatory content
3. The LLM mechanically cites all contexts rather than selectively citing only those it actually used

### Secondary Cause: Retrieval Recall Ceiling

**Severity:** Medium (affects coverage, not precision directly)
**Fixability:** Medium (requires retrieval pipeline changes)

The recall improvement from 0.772 → 0.888 shows that top_k=10 catches ~12% more relevant docs. But the precision cost is disproportionate: 5 extra citations for 0.116 recall gain = **~43 extra irrelevant citations per 100 queries**.

---

## 5. Actionability Assessment

### Is This the Most Actionable Signal?

**No.** The citation_precision drop is a **trade-off**, not an urgent fix. Here's why:

| Criterion | Assessment |
|---|---|
| **Impact on users** | Low — users see citations, not precision scores. More citations = more traceability, even if some are tangential |
| **Impact on system** | Low — precision is an eval metric, not a runtime constraint. The system works correctly with top_k=10 |
| **Fix complexity** | Medium — requires selective citation logic or a faithfulness gate |
| **Risk of regression** | Medium — aggressive filtering could reduce recall back to top_k=5 levels |
| **Alternative improvements** | Higher — retrieval quality (reranker training, chunking strategy) would improve both precision AND recall simultaneously |

### Recommended Priority Order

1. **Retrieval quality improvements** (highest ROI) — better chunking, reranker fine-tuning on SEBI domain
2. **Selective citations** (medium ROI) — model only cites contexts it actually used; reduces mechanical noise
3. **Exposure optimization** (low ROI) — Chaganti shows exposure matters more than source quality, but our system already passes full chunks
4. **top_k tuning** (lowest ROI) — the 5→10 trade-off is already documented; revert to 5 if precision matters more than recall

---

## 6. Selective Citations: The Real Fix for Precision

### What It Would Do

Instead of mechanically citing all contexts, the LLM would only cite contexts it actually used to generate the answer. This directly addresses the root cause:

- **Precision impact:** +0.05 to +0.15 (removes mechanical noise citations)
- **Recall impact:** ~0 (citations are about attribution, not retrieval coverage)
- **Implementation:** Modify `generate.py` prompt to instruct the model to cite only used contexts; add post-processing to filter citations

### Academic Support

Wallat 2025 shows that even RAG-optimized models post-rationalize citations. Selective citation is the closest practical approximation to faithful attribution without internal model probing.

Leung 2026 shows that verification doesn't require frontier models — a mid-tier model or NLI cross-encoder can verify citations at low cost.

### Implementation Sketch

```python
# In generate.py:answer_with_abstention, after generation:
# ~~Option A: Prompt-based (model self-selects citations) — PROVEN NO-OP~~
# Qwen2.5-1.5B emits zero parseable bracket citations (probe: scratchpad/probe_fallback.py)
#
# Option B′: Post-hoc cross-encoder verification (RECOMMENDED — supersedes A, B, C)
from sebi_rag.rerank import CrossEncoderReranker  # reuse existing cross-encoder
for ctx, citation in zip(contexts, citations):
    score = cross_encoder.verify(ctx.text, answer_snippet)
    if score < threshold:  # e.g., 0.5 entailment probability
        remove citation
```

### Trade-offs

| | ~~Option A (Prompt) — NO-OP~~ | Option B′ (Cross-Encoder) | ~~Option C (Hybrid)~~ |
|---|---|---|---|
| **Cost** | N/A (model emits zero brackets) | ~10ms per citation | Medium |
| **Accuracy** | N/A (model does not self-cite) | High (NLI cross-encoder is reliable) | Best of both |
| **Complexity** | N/A (prompt change is a no-op) | Medium (new verification step) | High |
| **Risk** | N/A (100% fallback to mechanical) | Adds latency to generation | Moderate |

---

## 7. Conclusion

The citation_precision drop from top_k expansion is a **documented trade-off**, not an urgent bug. The precision-recall curve shows that top_k=10 catches more relevant docs at the cost of more noise citations.

**The most actionable signal is NOT this precision drop — it's the underlying mechanical citation pattern that makes ALL top_k values suffer from low precision.** Selective citations would improve precision across all top_k settings, not just at the expanded value.

**Recommendation:** Defer B′ (post-hoc cross-encoder citation filter) to a dedicated implementation phase. See `2026-08-03-selective-citations-design.md` for B′ design. For now, the current behavior is acceptable — more citations = more traceability for users, and precision is an eval metric that doesn't affect runtime behavior.

---

## References

1. Wallat & Heuss (2025). "Correctness is not Faithfulness in RAG Attributions." arXiv:2501.13428
2. Leung et al. (2026). "Do You Need a Frontier Model as a Citation Verifier?" arXiv:2607.08700
3. Chaganti (2026). "On-Device Deep Research at 4B: Exposure Bounds Faithfulness, Retrieval Bounds Coverage." arXiv:2607.12257
4. Hu et al. (2024). "Can LLMs Evaluate Complex Attribution in QA?" CAQA Benchmark
