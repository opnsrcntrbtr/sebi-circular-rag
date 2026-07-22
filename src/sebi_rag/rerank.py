"""Stage-2 reranking (mandatory, D4). Cross-encoder in production; a
deterministic lexical reranker for offline tests.
"""
from __future__ import annotations

import re
from typing import Protocol, runtime_checkable

from .segment import Chunk

_TOK = re.compile(r"[a-z0-9]+")


@runtime_checkable
class Reranker(Protocol):
    def rerank(
        self, query: str, candidates: list[Chunk]
    ) -> list[tuple[Chunk, float]]:
        ...


class LexicalReranker:
    """Deterministic query-coverage reranker (test/fallback).

    Score = fraction of (content) query terms found in the candidate. Robust to
    candidate length, ~0 for out-of-domain queries, so it pairs cleanly with the
    abstention threshold. Not for production — see CrossEncoderReranker.
    """

    _STOP = frozenset(
        "the a an of to in on for and or is are be by under with within "
        "what which how when into did do does as at from".split()
    )

    def rerank(self, query: str, candidates: list[Chunk]) -> list[tuple[Chunk, float]]:
        q = {t for t in _TOK.findall(query.lower()) if t not in self._STOP}
        denom = len(q) or 1
        scored = []
        for c in candidates:
            toks = set(_TOK.findall(c.text.lower()))
            scored.append((c, len(q & toks) / denom))
        scored.sort(key=lambda cs: -cs[1])
        return scored


# --- Qwen3-Reranker (MLX) — F2 benchmark candidate (ADR-001, D2 amendment) ---
# Causal-LM reranker: score = P("yes") vs P("no") at the final position of a
# judge prompt (per the Qwen/Qwen3-Reranker model card). Not a classification
# head — do not load via CrossEncoder.

_QWEN3_PREFIX = (
    '<|im_start|>system\nJudge whether the Document meets the requirements '
    'based on the Query and the Instruct provided. Note that the answer can '
    'only be "yes" or "no".<|im_end|>\n<|im_start|>user\n'
)
_QWEN3_SUFFIX = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
_QWEN3_INSTRUCTION = (
    "Given a query about SEBI (Securities and Exchange Board of India) "
    "regulations, judge whether the document is from the circular that "
    "governs or directly answers the query."
)


def qwen3_rerank_prompt(
    query: str, doc: str, instruction: str = _QWEN3_INSTRUCTION
) -> str:
    return (
        f"{_QWEN3_PREFIX}<Instruct>: {instruction}\n"
        f"<Query>: {query}\n<Document>: {doc}{_QWEN3_SUFFIX}"
    )


class Qwen3MLXReranker:
    """Qwen3-Reranker via MLX (Apple-Silicon native). Benchmark candidate only
    (D2 as amended); production baseline remains CrossEncoderReranker until
    benchmark evidence says otherwise.

    Pinned candidates: mlx-community/Qwen3-Reranker-0.6B-mxfp8,
                       mlx-community/Qwen3-Reranker-4B-mxfp8.
    """

    def __init__(
        self,
        model_id: str = "mlx-community/Qwen3-Reranker-0.6B-mxfp8",
        max_doc_chars: int = 1500,
    ) -> None:
        from mlx_lm import load  # lazy: mlx only needed when actually used

        import mlx.core as mx

        self._mx = mx
        self._model, self._tok = load(model_id)
        self._yes = self._tok.convert_tokens_to_ids("yes")
        self._no = self._tok.convert_tokens_to_ids("no")
        self.max_doc_chars = max_doc_chars

    def _score(self, query: str, doc: str) -> float:
        mx = self._mx
        prompt = qwen3_rerank_prompt(query, doc)
        ids = self._tok.encode(prompt)
        logits = self._model(mx.array([ids]))[0, -1, :]
        pair = mx.softmax(
            mx.array([logits[self._no], logits[self._yes]]).astype(mx.float32)
        )
        return float(pair[1])

    def rerank(self, query: str, candidates: list[Chunk]) -> list[tuple[Chunk, float]]:
        scored = [
            (c, self._score(query, c.text[: self.max_doc_chars])) for c in candidates
        ]
        scored.sort(key=lambda cs: -cs[1])
        return scored


class CrossEncoderReranker:
    """Production reranker: bge-reranker-v2-m3 via sentence-transformers
    CrossEncoder on MPS (validated Step 10). NOTE: FlagReranker is incompatible
    with transformers 5.x; CrossEncoder is the supported API.
    """

    def __init__(
        self, model: str = "BAAI/bge-reranker-v2-m3", device: str = "mps",
        use_fp16: bool = False, batch_size: int = 32
    ) -> None:
        from sentence_transformers import CrossEncoder

        model_kwargs = {"torch_dtype": "float16"} if use_fp16 else {}
        self._ce = CrossEncoder(model, device=device, model_kwargs=model_kwargs)
        self._batch_size = batch_size

    def rerank(self, query: str, candidates: list[Chunk]) -> list[tuple[Chunk, float]]:
        if not candidates:
            return []
        scores = self._ce.predict([[query, c.text] for c in candidates],
                                  batch_size=self._batch_size)
        paired = list(zip(candidates, (float(s) for s in scores)))
        paired.sort(key=lambda cs: -cs[1])
        return paired
