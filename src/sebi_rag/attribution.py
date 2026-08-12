"""NLI attribution scoring for B' citation selection.

B' asks "does this context support the answer". The production reranker
(bge-reranker-v2-m3) answers a different question — "is this document relevant
to this query" — and reusing it as an attribution scorer is a model-task
mismatch. Measured 2026-08-12 over the 206 golden_v7 rows where retrieval found
every relevant document: 34 cite nothing relevant, 19 of them solely because of
B', and on 14 of those the relevant document is not even top-3 by
answer-relevance. No margin setting recovers a scorer ranking the wrong
quantity.

This module scores entailment(premise=context, hypothesis=answer) instead, and
satisfies the same `Reranker` protocol so it drops into `select_citations`
unchanged.
"""
from __future__ import annotations

import math

from .segment import Chunk

DEFAULT_NLI_MODEL = "cross-encoder/nli-deberta-v3-base"


def entailment_index(id2label: dict) -> int:
    """Index of the entailment class in a model's label map.

    Read from the checkpoint rather than assumed: MNLI variants disagree on
    class order, and taking the wrong index silently inverts the scorer —
    a bug that reads as a null experimental result rather than a failure.
    """
    for idx, label in id2label.items():
        if str(label).strip().lower() == "entailment":
            return int(idx)
    raise ValueError(
        f"no 'entailment' label in id2label={id2label!r}; refusing to guess a class index")


def _softmax(xs: list[float]) -> list[float]:
    m = max(xs)
    exps = [math.exp(x - m) for x in xs]
    total = sum(exps)
    return [e / total for e in exps]


class NLIAttributionScorer:
    """Scores each context by P(entailment) of the answer given that context.

    Implements the `Reranker` protocol: `rerank(answer_text, contexts)` returns
    (chunk, probability) descending. Probabilities, not logits, because
    `select_citations` compares scores against a sigmoid-scale margin.
    """

    def __init__(self, model, entail_idx: int, batch_size: int = 32) -> None:
        self._model = model
        self._entail = entail_idx
        self._batch_size = batch_size

    @classmethod
    def from_model(cls, model, batch_size: int = 32) -> "NLIAttributionScorer":
        """Wrap an already-constructed cross-encoder (also the test seam)."""
        return cls(model, entailment_index(model.id2label), batch_size)

    @classmethod
    def load(cls, model: str = DEFAULT_NLI_MODEL, device: str = "mps",
             batch_size: int = 32) -> "NLIAttributionScorer":
        from sentence_transformers import CrossEncoder

        ce = CrossEncoder(model, device=device)
        id2label = getattr(ce.model.config, "id2label", None)
        if not id2label:
            raise ValueError(f"{model} exposes no id2label; cannot locate the entailment class")
        return cls(ce, entailment_index(id2label), batch_size)

    def rerank(self, query: str, candidates: list[Chunk]) -> list[tuple[Chunk, float]]:
        # `query` is the answer text here: B' calls scorer.rerank(answer, contexts).
        if not candidates:
            return []
        raw = self._model.predict([[c.text, query] for c in candidates],
                                  batch_size=self._batch_size)
        scored = []
        for chunk, row in zip(candidates, raw):
            probs = _softmax([float(x) for x in row])
            scored.append((chunk, probs[self._entail]))
        scored.sort(key=lambda cs: -cs[1])
        return scored
