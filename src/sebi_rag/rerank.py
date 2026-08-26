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


# --- jina-reranker-v3-mlx — ADR-004 benchmark candidate (2026-08-24) ---------
# Listwise reranker: causal self-attention across the WHOLE candidate set in one
# forward pass ("last but not late interaction", arXiv:2509.25085), vs
# CrossEncoderReranker's pointwise (query, doc) scoring. Official MLX port,
# BEIR nDCG@10 61.85 vs bge-reranker-v2-m3's 56.51 in the paper's own benchmark
# (same 0.6B weight class) — a hypothesis this ADR's benchmark tests on SEBI
# data, not evidence on its own. CC BY-NC 4.0 (weights and the vendor's
# reference inference code) — non-commercial use only.

class JinaMLXReranker:
    """jina-reranker-v3-mlx wrapped to this project's Reranker protocol.

    The vendor ships model weights alongside their own inference module
    (rerank.py, not a standard mlx_lm-loadable causal LM — it adds an MLP
    projector and custom listwise prompt formatting) rather than a pip
    package. This loads that module dynamically from the downloaded snapshot,
    the same way any trust_remote_code model's code is treated as a model
    asset rather than vendored source — no copy of Jina's code lives in this
    repo.

    Benchmark candidate only (ADR-004); production baseline remains
    CrossEncoderReranker until benchmark evidence says otherwise (D1/D2's
    bar: >=10% measurable benefit, no recall regression).
    """

    def __init__(self, model_id: str = "jinaai/jina-reranker-v3-mlx") -> None:
        import importlib.util

        from huggingface_hub import snapshot_download

        snapshot_dir = snapshot_download(model_id)
        spec = importlib.util.spec_from_file_location(
            "_jina_reranker_v3_mlx", f"{snapshot_dir}/rerank.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self._reranker = module.MLXReranker(
            model_path=snapshot_dir,
            projector_path=f"{snapshot_dir}/projector.safetensors")

    def rerank(self, query: str, candidates: list[Chunk]) -> list[tuple[Chunk, float]]:
        if not candidates:
            return []
        docs = [c.text for c in candidates]
        results = self._reranker.rerank(query, docs)
        # The vendor's results are pre-sorted and carry 'index' into `docs` —
        # map back by index rather than assuming position, since a listwise
        # reranker's output order IS the ranking, not the input order.
        by_index = {r["index"]: float(r["relevance_score"]) for r in results}
        scored = [(c, by_index.get(i, 0.0)) for i, c in enumerate(candidates)]
        scored.sort(key=lambda cs: -cs[1])
        return scored


def retrieval_reranker_for(model: str, bge_reranker: "Reranker",
                           jina_loader=None) -> "Reranker":
    """ADR-004: the single decision for which model orders the RETRIEVAL pool
    (pipeline.reranker). Every pipeline builder routes through this so eval and
    production can never disagree about which reranker produced an ordering —
    the same guarantee citation_scorer_for gives for citation scoring.

    Deliberately separate from citation_scorer_for: R1 (2026-08-23) showed the
    citation-scoring role can fail independently of retrieval-reranking
    quality, so citation_scorer_for is always built against `bge_reranker`
    directly and is never routed through this function's choice.
    """
    if model == "bge":
        return bge_reranker
    if model == "jina":
        if jina_loader is None:
            jina_loader = JinaMLXReranker
        return jina_loader()
    raise ValueError(f"unknown reranker model: {model!r}")


class CrossEncoderReranker:
    """Production reranker: bge-reranker-v2-m3 via sentence-transformers
    CrossEncoder on MPS (validated Step 10). NOTE: FlagReranker is incompatible
    with transformers 5.x; CrossEncoder is the supported API.
    """

    def __init__(
        self, model: str = "BAAI/bge-reranker-v2-m3", device: str | None = None,
        use_fp16: bool = False, batch_size: int = 32
    ) -> None:
        from sentence_transformers import CrossEncoder

        # MPS crashes CrossEncoder (segfault 139); default to CPU.
        if device is None:
            import torch
            device = "cpu"  # MPS unavailable for CrossEncoder on this hardware

        model_kwargs = {"torch_dtype": "float16"} if use_fp16 else {}
        self._ce = CrossEncoder(model, device=device, model_kwargs=model_kwargs)
        self._batch_size = batch_size

    def rerank(self, query: str, candidates: list[Chunk | dict]) -> list[tuple[Chunk | dict, float]]:
        """Score candidates with CrossEncoder.

        Accepts Chunk objects (with .text) or dicts (with 'text' key).
        Returns list of (original_candidate, score) tuples.
        """
        if not candidates:
            return []

        def _text(c: Chunk | dict) -> str:
            return c.text if isinstance(c, Chunk) else c.get("text", "")

        try:
            scores = self._ce.predict([[query, _text(c)] for c in candidates],
                                      batch_size=self._batch_size)
        except Exception:
            # Fallback: lexical reranking if CE fails at inference time
            q = {t for t in _TOK.findall(query.lower()) if t not in LexicalReranker()._STOP}
            denom = len(q) or 1
            scored = []
            for c in candidates:
                toks = set(_TOK.findall(_text(c).lower()))
                scored.append((c, len(q & toks) / denom))
            scored.sort(key=lambda cs: -cs[1])
            return scored

        paired = list(zip(candidates, (float(s) for s in scores)))
        paired.sort(key=lambda cs: -cs[1])
        return paired


# --- Set-Encoder (lightning-ir) — benchmark candidate (2026-08-26 spec) -----
# Listwise cross-encoder with permutation-invariant inter-passage attention
# (Schlatt et al., ECIR 2025, arXiv:2404.06912). Apache 2.0. HF checkpoint
# webis/set-encoder-base (0.1B params, electra-base-discriminator backbone),
# via the vendor's own inference package `lightning-ir`
# (github.com/webis-de/lightning-ir), a normal pip dependency (not a
# trust_remote_code snapshot like JinaMLXReranker). Report-only per
# docs/superpowers/specs/2026-08-26-set-encoder-prereg.md — NOT wired into
# retrieval_reranker_for/config.toml; benchmark candidate only, matching
# what ADR-004 tested Jina/bge for.

class SetEncoderReranker:
    """webis/set-encoder-base via lightning-ir, wrapped to this project's
    Reranker protocol. Benchmark candidate only (2026-08-26 spec); production
    baseline remains whatever retrieval_reranker_for/config.toml selects
    until benchmark evidence says otherwise (same "benchmark candidate only"
    framing JinaMLXReranker carries for ADR-004).
    """

    def __init__(self, model: str = "webis/set-encoder-base", device: str | None = None) -> None:
        from lightning_ir import CrossEncoderModule

        # Matches CrossEncoderReranker's own documented reason (MPS crashes
        # CrossEncoder-family models on this hardware, segfault 139): default
        # to CPU unless the caller explicitly opts into another device. MPS
        # was not empirically verified stable for lightning-ir specifically —
        # see the prereg doc's environment-verification note — so CPU stays
        # the safe default here too.
        if device is None:
            device = "cpu"
        self._module = CrossEncoderModule(model)
        self._module = self._module.to(device)
        self._module.eval()

    def rerank(self, query: str, candidates: list[Chunk]) -> list[tuple[Chunk, float]]:
        """Score candidates with lightning-ir's CrossEncoderModule.score.

        Mirrors CrossEncoderReranker's pairing/sorting idiom: pair each
        candidate with its score, sort descending, return the pairs.
        """
        if not candidates:
            return []
        import torch

        docs = [c.text for c in candidates]
        with torch.no_grad():
            output = self._module.score(query, docs)
        scores = output.scores.detach().to("cpu").float().tolist()
        paired = list(zip(candidates, scores))
        paired.sort(key=lambda cs: -cs[1])
        return paired
