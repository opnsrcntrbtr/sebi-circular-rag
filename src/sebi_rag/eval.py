"""Minimal retrieval metrics (subset of docs/project_context.md section 7).

Recall@k, MRR, nDCG over ranked chunk-id lists vs a relevant id set.
Citation/groundedness/abstention metrics arrive with the golden set (P1).
"""
from __future__ import annotations

import math


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
    dcg = sum(
        1.0 / math.log2(i + 2)
        for i, cid in enumerate(ranked_ids[:k])
        if cid in relevant
    )
    ideal = sum(1.0 / math.log2(i + 2) for i in range(min(k, len(relevant))))
    return dcg / ideal if ideal else 0.0
