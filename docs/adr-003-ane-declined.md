# ADR-003: Apple Neural Engine (ANE/NPU) declined for the local RAG pipeline

**Date:** 2026-07-22
**Status:** Accepted

## Context
The local pipeline runs on Apple Silicon. Beyond the GPU (MPS/MLX) already in
use, the Apple Neural Engine (ANE) is available as a third compute engine. We
evaluated whether to target it for the embedder/reranker (and generation).

## Decision
We do NOT target the ANE. The pipeline stays on MLX (generation) and MPS/MLX
(embeddings/reranker).

## Rationale (as of 22 July 2026)
- ANE is an **energy-efficiency** engine (~2 W vs ~20 W GPU), not a throughput
  engine. For raw speed on a plugged-in Mac, MLX on the GPU wins (published
  comparisons: ~93+ tok/s vs ~9 tok/s on an 8B model).
- ANE access requires **Core ML conversion** (apple/ml-ane-transformers) with
  finicky operator support and significant engineering cost.
- This is a **server RAG on plugged-in Apple Silicon** — throughput-oriented,
  not battery/thermal/always-on constrained. ANE does not win the metric that
  matters here.

## Consequences
- No Core ML conversion pipeline to maintain.
- Revisit ONLY if battery life, thermal envelope, or always-on background
  inference becomes an explicit goal.

## References
See docs/superpowers/specs/2026-07-22-spaces-ux-and-apple-silicon-compute-design.md
(Sources — ANE/NPU) for the underlying research.
