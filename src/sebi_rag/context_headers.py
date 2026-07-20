"""Contextual chunk headers (iv9): one lay+statutory sentence per chunk.

Index-side enrichment for deep sub-clause and annex chunks whose statutory
text lacks the vocabulary users query with (probe-par-03 class). Headers
are generated once into data/corpus/context_headers.jsonl (committed) and
merged into chunk text at index build. Failure is silent by design: any
generation error or empty output yields "", which callers treat as
no-header.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable

from .segment import Chunk

_PROMPT = (
    "You are indexing Indian securities regulations. Read this provision "
    "from a SEBI circular and describe in ONE plain sentence what it "
    "governs, naming the topic both in everyday language and in the "
    "statute's own terms. Do not use markdown, headings, dates, or "
    "circular numbers. Reply with the sentence only.\n"
    "Circular subject: {subject}\n"
    "Governing clause: {governing}\n"
    "Provision: {chunk_text}"
)

_DEEP = re.compile(r"^\d+(?:\.\d+){2,}")
_ANNEX = re.compile(r"annex|appendix|schedule", re.I)


def in_scope(section: str) -> bool:
    """Spec scope: depth>=3 numbered sub-clauses plus annex-family headings."""
    return bool(_DEEP.match(section) or _ANNEX.search(section))


def filter_targeted_rows(
    rows: list[dict], target_docs: set[str]
) -> list[dict]:
    """Keep only sidecar rows whose chunk belongs to a target document."""
    return [r for r in rows if r["chunk_id"].split("#")[0] in target_docs]


class HeaderGenerator:
    def __init__(
        self, generate: Callable[[str], str], max_chars: int = 200
    ) -> None:
        self._generate = generate
        self.max_chars = max_chars

    def describe(self, subject: str, governing: str, chunk_text: str) -> str:
        try:
            out = self._generate(_PROMPT.format(
                subject=subject, governing=governing, chunk_text=chunk_text
            ))
        except Exception:  # noqa: BLE001 — silent-failure contract (spec)
            return ""
        out = " ".join((out or "").split())
        return out.lstrip("#*>- ").strip()[: self.max_chars]

    @classmethod
    def load(
        cls,
        model: str = "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
        max_tokens: int = 80,
    ) -> "HeaderGenerator":
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


def apply_context_headers(
    chunks: list[Chunk], headers: dict[str, str]
) -> list[Chunk]:
    """Insert each chunk's header as a line below its breadcrumb line.

    Pure and id-preserving: chunk count and IDs never change; chunks with
    no (or blank) header pass through untouched.
    """
    out: list[Chunk] = []
    for c in chunks:
        h = headers.get(c.id, "").strip()
        if not h:
            out.append(c)
            continue
        if "\n" in c.text:
            first, rest = c.text.split("\n", 1)
            text = f"{first}\n{h}\n{rest}"
        else:
            text = f"{c.text}\n{h}"
        out.append(Chunk(id=c.id, doc_id=c.doc_id, section=c.section,
                         text=text, meta=c.meta))
    return out


def load_headers(path: str | Path) -> dict[str, str]:
    p = Path(path)
    if not p.exists():
        return {}
    out: dict[str, str] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["chunk_id"]] = r.get("header", "")
    return out
