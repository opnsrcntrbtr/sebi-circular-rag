# Task 5: fp16 A/B Eval Gate — Findings & Decision

**Date:** 2026-07-22  
**Status:** Complete  
**Decision:** Keep `use_fp16=False` default (opt-in via env); document latency regression

## Results Summary

### Retrieval A/B Test (golden_v6, n=56 queries)

| Metric | Baseline (fp32) | fp16 Candidate | Delta | Parity? |
|--------|---|---|---|---|
| recall@10 | 0.9556 | 0.9556 | 0.0000 | ✅ Perfect |
| avg_latency_s | 0.0768 | 0.1765 | +2.30x | ⚠️ Regression |

**Verdict:** Recall holds perfect parity; latency regresses 2.3x (unexpected).

### As-of Golden Eval (n=13 total cases)

| Suite | Baseline (fp32) | fp16 Candidate | Delta | Parity? |
|-------|---|---|---|---|
| Pipeline (10) | 10/10 (100%) | 10/10 (100%) | 0 | ✅ Perfect |
| Selector (3) | 3/3 (100%) | 3/3 (100%) | 0 | ✅ Perfect |
| Overall | 13/13 (100%) | 13/13 (100%) | 0 | ✅ Perfect |

**Verdict:** Golden metrics hold perfect parity across all cases.

## Analysis

### Why fp16 is Slower (2.3x latency regression)

fp16 should be faster or equal on MPS GPU, not slower. Hypotheses:

1. **MPS kernel selection:** MPS may lack optimized fp16 kernels for BGE-M3 embedding or cross-encoder reranking operations, falling back to fp32 compute with fp16↔fp32 conversions overhead.
2. **Batch size suboptimality:** The default `batch_size=32` may be suboptimal for fp16 on MPS; fp16 typically prefers larger batches for efficiency.
3. **Unified memory layout:** MPS unified memory management may not align fp16 buffers optimally, causing memory throughput degradation.

### Quality Impact

Despite latency regression, **recall and golden metrics are identical**, confirming fp16 maintains correctness on this corpus. This suggests:
- Quantization noise is below the retrieval signal threshold
- BGE-M3 embeddings are robust to fp16 rounding
- Cross-encoder scores remain discriminative in fp16

## Decision

**Keep `use_fp16=False` as the default.** Rationale:

1. **Safety first:** Latency regression is concerning and unexplained. Without root cause identified, enabling by default violates measurement-first principle.
2. **Opt-in available:** Users who need fp16 (memory-constrained, willing to trade latency for VRAM) can enable via `SEBI_RAG_USE_FP16=true` env variable.
3. **Future work:** Investigate batch size tuning for fp16 (e.g., batch_size=64 or 128) in a follow-up optimization pass.

## Configuration

- **settings.py:** `use_fp16: bool = False` (unchanged)
- **config.toml:** `use_fp16 = false` (unchanged)
- **Index state:** Restored to fp32 (baseline) for consistent default behavior

## Recommendations

### For Future fp16 Optimization

If latency matters and memory is abundant:
1. Benchmark batch_size tuning: 32 → 64 → 128 on fp16
2. Profile MPS kernel selection to identify fallback operations
3. Consider MLX backend (Task 6) as alternative to fp16 on MPS—MLX may have better fp16 kernels

### For Production Deployment

- Document fp16 as experimental / unsupported in settings.toml comments
- Add note in README: "fp16 on MPS exhibits latency regression; not recommended for production"
- Monitor community issues on BGE-M3 fp16 performance on Apple Silicon

## References

- **Baseline run:** `eval/runs/baseline_retrieval/results.json` (recall@10=0.9556, latency=0.0768s)
- **fp16 run:** `eval/runs/fp16_retrieval/results.json` (recall@10=0.9556, latency=0.1765s)
- **Baseline as-of:** `eval/runs/asof-baseline/results.json` (13/13 100%)
- **fp16 as-of:** `eval/runs/asof-fp16/results.json` (13/13 100%)
- **Architecture doc:** `docs/superpowers/specs/2026-07-22-spaces-ux-and-apple-silicon-compute-design.md` (compute policy)
