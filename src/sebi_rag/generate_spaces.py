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


class ExternalSpaceGenerator:
    """Primary generator: calls a public LLM Space via gradio_client.

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
        job = client.submit(prompt, api_name=self.settings.external_api_name or None)
        result = job.result(timeout=self.settings.external_timeout_s)
        if isinstance(result, (list, tuple)):  # multi-output endpoints
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
                    "external Space %r failed (%s); falling back to %s",
                    self.settings.external_space, exc, self.settings.hf_model,
                )
        return self.fallback.generate(query, contexts)
