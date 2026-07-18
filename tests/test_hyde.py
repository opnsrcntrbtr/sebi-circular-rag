"""HyDE expander (Part B): query -> hypothetical statutory passage.

Offline only — generation is an injected callable; mlx_lm never loads here.
"""
from __future__ import annotations

from sebi_rag.hyde import HydeExpander


def test_prompt_contains_query_and_style_cue():
    seen: dict[str, str] = {}

    def fake(prompt: str) -> str:
        seen["prompt"] = prompt
        return "  The CRA shall not take any new clients.  "

    out = HydeExpander(fake).hypothesize(
        "can companies pull their rating assignments?"
    )
    assert "can companies pull their rating assignments?" in seen["prompt"]
    assert "SEBI circular" in seen["prompt"]
    assert out == "The CRA shall not take any new clients."


def test_generation_error_returns_empty():
    def boom(prompt: str) -> str:
        raise RuntimeError("mlx exploded")

    assert HydeExpander(boom).hypothesize("any query") == ""


def test_whitespace_output_returns_empty():
    assert HydeExpander(lambda p: "   \n ").hypothesize("any query") == ""


def test_output_truncated_to_max_chars():
    ex = HydeExpander(lambda p: "x" * 5000, max_chars=1200)
    assert len(ex.hypothesize("any query")) == 1200
