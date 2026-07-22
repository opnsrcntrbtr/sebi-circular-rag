"""Device + fp16 policy selection (no real torch/mps required)."""
from __future__ import annotations

from sebi_rag.device import pick_device, should_use_fp16


def test_pick_device_honors_explicit_pref():
    assert pick_device("cpu", is_mps_available=lambda: True) == "cpu"
    assert pick_device("cuda", is_mps_available=lambda: False) == "cuda"


def test_pick_device_auto_mps_when_available():
    assert pick_device(None, is_mps_available=lambda: True) == "mps"


def test_pick_device_auto_cpu_when_no_mps():
    assert pick_device(None, is_mps_available=lambda: False) == "cpu"


def test_pick_device_empty_pref_is_auto():
    assert pick_device("", is_mps_available=lambda: False) == "cpu"


def test_should_use_fp16_matrix():
    assert should_use_fp16("mps", True) is True
    assert should_use_fp16("cuda", True) is True
    assert should_use_fp16("cpu", True) is False   # never fp16 on cpu
    assert should_use_fp16("mps", False) is False
