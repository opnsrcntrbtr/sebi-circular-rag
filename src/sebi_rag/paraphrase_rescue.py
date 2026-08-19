"""Paraphrase rescue for the cross-encoder score floor.

Preregistered in `docs/superpowers/specs/2026-08-19-ce-paraphrase-rescue-prereg.md`.

Two answerable golden_v7 rows abstain with `reason=score_floor` because the
query substitutes lay vocabulary for statutory vocabulary ("short-term bank
loan" for "intraday borrowing"). The relevant document is retrieved and ranked
*first* by the cross-encoder, which then scores it 0.0114-0.0296 against a 0.05
floor. Rescoring the same pool with a domain-vocabulary query lifts those
chunks to 0.977-0.994 (`reports/ce-query-reform-probe-2026-08-19.json`), so the
reranker is capable — it is being asked the wrong question.

The floor itself cannot be tuned around: it catches 29 of 41 correct
abstentions, and the two false abstentions sit *inside* that band
(`reports/score-floor-utility-2026-08-19.json`).

Design constraints, all load-bearing:

- Fires ONLY below the floor. Rows that already answer are untouched.
- Re-scores the SAME pool. Retrieval is not re-run, so a rescue can never be
  credited for repairing a recall failure.
- Keeps the rescued list only if it clears the floor, so the gate signal is
  monotone: a rescue can raise `rerank_top`, never lower it.
- A degenerate rewrite is rejected before the reranker is invoked.
"""
from __future__ import annotations

from typing import Protocol

from .segment import Chunk

# A rewrite longer than this is treated as the model having rambled rather than
# rewritten; 40 words is ~2.5x the longest target query (15 words).
MAX_REWRITE_WORDS = 40

# How many reranked chunks the rewriter sees as pseudo-relevance feedback.
PRF_CHUNKS = 5

_PROMPT = """You rewrite questions into the vocabulary used by SEBI circulars.

Below are extracts from SEBI circulars that may be relevant. Rewrite the \
question using the terminology those extracts use, so it can be matched \
against them. Keep it to one line. Output ONLY the rewritten question, with \
no preamble, quotes or explanation.

Extracts:
{extracts}

Question: {query}
Rewritten question:"""


class QueryRewriter(Protocol):
    """Rewrites a lay-vocabulary query into statutory vocabulary.

    Returns None when it cannot produce a usable rewrite; the caller then
    leaves the abstention untouched.
    """

    def rewrite(self, query: str, chunks: list[Chunk]) -> str | None: ...


class StaticQueryRewriter:
    """Fixed rewrite, for tests and for replaying a preregistered rewrite."""

    def __init__(self, rewritten: str | None) -> None:
        self._rewritten = rewritten

    def rewrite(self, query: str, chunks: list[Chunk]) -> str | None:
        return self._rewritten


def is_degenerate(query: str, rewritten: str | None) -> bool:
    """True when `rewritten` is unusable and the rescue should be abandoned.

    Degenerate means: absent, blank, identical to the input up to case and
    surrounding whitespace, or longer than MAX_REWRITE_WORDS.
    """
    if rewritten is None:
        return True
    stripped = rewritten.strip()
    if not stripped:
        return True
    if stripped.casefold() == query.strip().casefold():
        return True
    return len(stripped.split()) > MAX_REWRITE_WORDS


def _extracts(chunks: list[Chunk]) -> str:
    lines = []
    for c in chunks[:PRF_CHUNKS]:
        subject = str(c.meta.get("subject") or "").strip()
        head = " ".join(c.text.split())[:300]
        lines.append(f"- {subject}: {head}" if subject else f"- {head}")
    return "\n".join(lines)


class MLXQueryRewriter:
    """Local MLX-LM rewriter. Greedy decoding -> deterministic."""

    def __init__(
        self,
        model: str = "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
        max_tokens: int = 48,
    ) -> None:
        from mlx_lm import load

        self._model, self._tok = load(model)
        self.max_tokens = max_tokens

    def rewrite(self, query: str, chunks: list[Chunk]) -> str | None:
        from mlx_lm import generate as _gen

        if not chunks:
            return None
        user = _PROMPT.format(extracts=_extracts(chunks), query=query)
        try:
            prompt = self._tok.apply_chat_template(
                [{"role": "user", "content": user}],
                add_generation_prompt=True, tokenize=False,
            )
        except Exception:  # noqa: BLE001
            prompt = user
        out = _gen(self._model, self._tok, prompt=prompt,
                   max_tokens=self.max_tokens, verbose=False)
        # Keep the first non-empty line: the model often continues past the
        # rewrite with commentary the prompt asked it to omit.
        for line in out.strip().splitlines():
            line = line.strip().strip('"').strip()
            if line:
                return line
        return None


def query_rewriter_for(
    enabled: bool, model: str = "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
) -> QueryRewriter | None:
    """Factory mirroring `generate.citation_scorer_for`: None when disabled."""
    return MLXQueryRewriter(model=model) if enabled else None


def rescue_pool(
    query: str,
    pool: list[Chunk],
    reranked: list[tuple[Chunk, float]],
    reranker,
    rewriter: QueryRewriter | None,
    floor: float,
) -> tuple[list[tuple[Chunk, float]], str | None]:
    """Re-score `pool` with a rewritten query when `reranked` is below `floor`.

    Returns `(reranked_list, rewritten_query_or_None)`. The second element is
    non-None only when a rescue was accepted, and is recorded for audit.
    """
    if rewriter is None or not reranked or not pool:
        return reranked, None
    if float(reranked[0][1]) >= floor:
        return reranked, None

    # PRF: show the rewriter the best candidates, in reranked order.
    rewritten = rewriter.rewrite(query, [c for c, _ in reranked])
    if is_degenerate(query, rewritten):
        return reranked, None
    assert rewritten is not None  # narrowed by is_degenerate
    rewritten = rewritten.strip()

    alt = reranker.rerank(rewritten, pool)
    if alt and float(alt[0][1]) >= floor:
        return alt, rewritten
    return reranked, None
