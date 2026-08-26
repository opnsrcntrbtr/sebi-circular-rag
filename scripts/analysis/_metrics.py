"""Shared doc-level metric helpers for the retrieval parameter sweep
(docs/superpowers/specs/2026-08-26-retrieval-param-sweep-prereg.md).

Kept out of src/sebi_rag/ per the loop's scope (analysis-only, no production
code edits). Mirrors benchmark.py:run_retrieval_benchmark's doc-level
convention exactly — dedupe to distinct circulars BEFORE slicing top-k, or
ndcg_at_k can exceed 1.0 by double-counting chunks from the same circular.
"""
from __future__ import annotations

import math

import numpy as np

from sebi_rag.eval_harness import _unique  # noqa: F401 re-exported for callers


def recall_at_k(ranked_ids: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    hit = len(set(ranked_ids[:k]) & relevant)
    return hit / len(relevant)


def mrr(ranked_ids: list[str], relevant: set[str]) -> float:
    for i, cid in enumerate(ranked_ids):
        if cid in relevant:
            return 1.0 / (i + 1)
    return 0.0


def ndcg_at_k(ranked_ids: list[str], relevant: set[str], k: int) -> float:
    dcg = sum(1.0 / math.log2(i + 2) for i, cid in enumerate(ranked_ids[:k]) if cid in relevant)
    ideal = sum(1.0 / math.log2(i + 2) for i in range(min(k, len(relevant))))
    return dcg / ideal if ideal else 0.0


def doc_ids_deduped(chunks_and_scores, chunk_doc_id) -> list[str]:
    """[(chunk_idx, score), ...] -> distinct doc_ids in rank order."""
    return _unique(chunk_doc_id(i) for i, _ in chunks_and_scores)


def mean_or_none(d: dict) -> float | None:
    """None (not 0.0) when d is empty, so 'unmeasured' is never confused
    with 'measured zero' (e.g. golden_v6 rows with no relevant_chunks)."""
    return float(np.mean(list(d.values()))) if d else None


def fmt(x: float | None) -> str:
    return f"{x:.4f}" if x is not None else "n/a"
