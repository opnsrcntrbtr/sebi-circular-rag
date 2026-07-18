"""HyDE (Hypothetical Document Embeddings): query -> statutory passage.

Part B of the semantic-gap resolution (probe-par-03). The passage is
dense-searched as an additive third RRF leg — see
HybridRetriever.retrieve(hyde_text=...). Failure is silent by design: any
generation error or empty output yields "", which callers treat as no-HyDE.
"""
from __future__ import annotations

from typing import Callable

_PROMPT = (
    "Write a short passage in the style of a SEBI circular provision that "
    "would answer this question. Use formal regulatory vocabulary. "
    "Question: {query}"
)


class HydeExpander:
    def __init__(
        self, generate: Callable[[str], str], max_chars: int = 1200
    ) -> None:
        self._generate = generate
        self.max_chars = max_chars

    def hypothesize(self, query: str) -> str:
        try:
            out = self._generate(_PROMPT.format(query=query))
        except Exception:  # noqa: BLE001 — silent-failure contract (spec)
            return ""
        return (out or "").strip()[: self.max_chars]

    @classmethod
    def load(
        cls,
        model: str = "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
        max_tokens: int = 150,
    ) -> "HydeExpander":
        from mlx_lm import generate as _gen
        from mlx_lm import load

        m, tok = load(model)

        def call(prompt: str) -> str:
            try:
                p = tok.apply_chat_template(
                    [{"role": "user", "content": prompt}],
                    add_generation_prompt=True, tokenize=False,
                )
            except Exception:  # noqa: BLE001
                p = prompt
            return _gen(m, tok, prompt=p, max_tokens=max_tokens, verbose=False)

        return cls(call)
