"""CPU / remote generation for the Hugging Face Spaces demo.

All classes implement the Generator protocol from generate.py —
generate(query, contexts) -> str — and build the prompt with the shared
injection-hardened _grounded_prompt (F4), so answer_with_abstention,
faithfulness scoring and citation checks behave exactly as locally.

Order of preference (HybridGenerator):
  1. ExternalSpaceGenerator — a public HF Space via gradio_client (fast, free).
  2. HFGenerator — small transformers model on CPU (slow, self-contained).

Never imported by the Apple-Silicon path. gradio_client / transformers are
imported lazily so local tests need neither.
"""
from __future__ import annotations

import logging

from .generate import ABSTAIN, _grounded_prompt
from .segment import Chunk
from .settings import SpacesSettings

log = logging.getLogger(__name__)


_LLAMA2_CHAT_SYSTEM_PROMPT = (
    "You are a careful SEBI regulatory research assistant. Only use the "
    "sources given in the user message; never invent a circular number."
)

# huggingface-projects/llama-2-7b-chat's /generate signature (verified live
# 2026-07-10 via client.view_api()): message, system_prompt, max_new_tokens,
# temperature, top_p, top_k, repetition_penalty -> str. top_k/repetition_penalty
# aren't in SpacesSettings (no local equivalent), so sane fixed defaults are
# used here rather than growing the config for one external Space's API shape.
_LLAMA2_TOP_K = 50
_LLAMA2_REPETITION_PENALTY = 1.2


class ExternalSpaceGenerator:
    """Primary generator: calls a public LLM Space via gradio_client.

    Wired to huggingface-projects/llama-2-7b-chat's /generate endpoint
    (official HF org Space, Llama-2-7B-Chat, live-verified). Swapping
    spaces.external_space to a Space with a different API shape requires
    updating the client.submit(...) call below to match.

    Raises on any failure (missing space id, connection error, timeout);
    HybridGenerator handles the fallback.
    """

    def __init__(self, settings: SpacesSettings) -> None:
        self.settings = settings
        self._client = None  # lazy: connecting is a network round-trip

    def _get_client(self):
        if not self.settings.external_space:
            raise RuntimeError("spaces.external_space is not configured")
        if self._client is None:
            from gradio_client import Client

            self._client = Client(self.settings.external_space)
        return self._client

    def generate(self, query: str, contexts: list[Chunk]) -> str:
        if not contexts:
            return ABSTAIN
        prompt = _grounded_prompt(query, contexts)
        client = self._get_client()
        s = self.settings
        job = client.submit(
            prompt,
            _LLAMA2_CHAT_SYSTEM_PROMPT,
            float(s.max_tokens),
            s.temperature,
            s.top_p,
            float(_LLAMA2_TOP_K),
            _LLAMA2_REPETITION_PENALTY,
            api_name=s.external_api_name or "/generate",
        )
        result = job.result(timeout=s.external_timeout_s)
        if isinstance(result, (list, tuple)):  # defensive: other Spaces may differ
            result = next((r for r in result if isinstance(r, str)), result[0])
        return str(result).strip()


class HFGenerator:
    """Fallback generator: small instruct model via transformers on CPU."""

    def __init__(self, settings: SpacesSettings) -> None:
        self.settings = settings
        self._model = None
        self._tok = None

    def _load(self) -> None:
        if self._model is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self._tok = AutoTokenizer.from_pretrained(self.settings.hf_model)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.settings.hf_model,
            device_map="cpu",
            torch_dtype=torch.float32,  # widest CPU compatibility
        )
        self._model.eval()

    def generate(self, query: str, contexts: list[Chunk]) -> str:
        if not contexts:
            return ABSTAIN
        import torch

        self._load()
        user = _grounded_prompt(query, contexts)
        try:
            prompt = self._tok.apply_chat_template(
                [{"role": "user", "content": user}],
                add_generation_prompt=True, tokenize=False,
            )
        except Exception:  # noqa: BLE001 — mirror MLXGenerator's fallback
            prompt = user
        inputs = self._tok(prompt, return_tensors="pt")
        s = self.settings
        with torch.no_grad():
            out = self._model.generate(
                **inputs,
                max_new_tokens=s.max_tokens,
                do_sample=s.temperature > 0,
                temperature=s.temperature or None,
                top_p=s.top_p,
                pad_token_id=self._tok.eos_token_id,
            )
        new_tokens = out[0][inputs["input_ids"].shape[1]:]
        return self._tok.decode(new_tokens, skip_special_tokens=True).strip()


class HybridGenerator:
    """External Space first; on ANY failure fall back to the local CPU model.

    external/fallback are injectable for tests; defaults are built from
    settings on first use.
    """

    def __init__(
        self,
        settings: SpacesSettings,
        external: object | None = None,
        fallback: object | None = None,
    ) -> None:
        self.settings = settings
        self.external = external or ExternalSpaceGenerator(settings)
        self.fallback = fallback or HFGenerator(settings)

    def generate(self, query: str, contexts: list[Chunk]) -> str:
        if self.settings.external_space:
            try:
                return self.external.generate(query, contexts)
            except Exception as exc:  # noqa: BLE001 — deliberate catch-all fallback
                log.warning(
                    "external Space %r failed (%s: %s); falling back to %s",
                    self.settings.external_space, type(exc).__name__, exc,
                    self.settings.hf_model,
                )
        return self.fallback.generate(query, contexts)
