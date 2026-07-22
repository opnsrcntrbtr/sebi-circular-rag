"""Device + precision selection for Apple-Silicon inference.

Centralizes the mps/cpu decision (previously hardcoded "mps") and the fp16
policy. bfloat16 is deliberately never selected: as of mid-2026 the MPS backend
lacks optimized bf16 kernels and is far slower than fp16/fp32 for inference.
See docs/superpowers/specs/2026-07-22-spaces-ux-and-apple-silicon-compute-design.md
(Sources).
"""
from __future__ import annotations

from typing import Callable


def _mps_available() -> bool:
    try:
        import torch
        return bool(torch.backends.mps.is_available())
    except Exception:  # noqa: BLE001 - torch missing or probe failed -> treat as no mps
        return False


def pick_device(pref: str | None = None,
                is_mps_available: Callable[[], bool] | None = None) -> str:
    """Resolve the compute device.

    A truthy explicit `pref` ("mps"/"cpu"/"cuda") wins. Otherwise prefer "mps"
    when available, else "cpu". `is_mps_available` is injectable for tests.
    """
    if pref:
        return pref
    check = is_mps_available or _mps_available
    return "mps" if check() else "cpu"


def should_use_fp16(device: str, use_fp16: bool) -> bool:
    """fp16 only on GPU-class devices; never on cpu. bf16 is never returned
    here by design (poor MPS support)."""
    return bool(use_fp16) and device in ("mps", "cuda")
