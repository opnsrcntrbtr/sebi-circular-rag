"""Settings: defaults, config.toml, and env-override precedence."""
from __future__ import annotations

from sebi_rag.settings import Settings

ENV_KEYS = ["SEBI_RAG_GENERATOR", "SEBI_RAG_TOP_K", "SEBI_RAG_RATE_PER_MIN",
            "SEBI_RAG_TIMEOUT_S", "SEBI_RAG_MLX_MODEL",
            "SEBI_RAG_DEVICE", "SEBI_RAG_USE_FP16", "SEBI_RAG_ENCODE_BATCH_SIZE",
            "SEBI_RAG_EMBED_BACKEND", "SEBI_RAG_RERANK_BACKEND"]


def _clear(monkeypatch):
    for k in ENV_KEYS:
        monkeypatch.delenv(k, raising=False)


def test_defaults_when_no_file(monkeypatch, tmp_path):
    _clear(monkeypatch)
    monkeypatch.setenv("SEBI_RAG_CONFIG", str(tmp_path / "none.toml"))
    s = Settings.load()
    assert s.generator == "mlx" and s.top_k == 3 and s.rate_per_min == 60


def test_env_overrides(monkeypatch, tmp_path):
    _clear(monkeypatch)
    monkeypatch.setenv("SEBI_RAG_CONFIG", str(tmp_path / "none.toml"))
    monkeypatch.setenv("SEBI_RAG_TOP_K", "7")
    monkeypatch.setenv("SEBI_RAG_GENERATOR", "ollama")
    s = Settings.load()
    assert s.top_k == 7 and s.generator == "ollama"


def test_load_spaces_defaults_and_file(monkeypatch, tmp_path):
    _clear(monkeypatch)
    monkeypatch.delenv("SEBI_RAG_SPACES_HF_MODEL", raising=False)
    cfg = tmp_path / "c.toml"
    cfg.write_text(
        "[service]\ntop_k = 5\n\n"
        "[spaces]\nexternal_space = \"user/llm-space\"\nrecent_years = [2026]\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("SEBI_RAG_CONFIG", str(cfg))
    s = Settings.load_spaces()
    assert s.top_k == 5                                   # [service] still applies
    assert s.spaces is not None
    assert s.spaces.external_space == "user/llm-space"    # from file
    assert s.spaces.recent_years == (2026,)
    assert s.spaces.hf_model == "Qwen/Qwen2.5-0.5B-Instruct"  # default
    monkeypatch.setenv("SEBI_RAG_SPACES_HF_MODEL", "acme/tiny")
    assert Settings.load_spaces().spaces.hf_model == "acme/tiny"  # env beats file
    assert Settings.load().spaces is None                 # plain load untouched


def test_toml_then_env_precedence(monkeypatch, tmp_path):
    _clear(monkeypatch)
    cfg = tmp_path / "c.toml"
    cfg.write_text("[service]\ntop_k = 5\nrate_per_min = 10\n", encoding="utf-8")
    monkeypatch.setenv("SEBI_RAG_CONFIG", str(cfg))
    s = Settings.load()
    assert s.top_k == 5 and s.rate_per_min == 10   # from file
    monkeypatch.setenv("SEBI_RAG_TOP_K", "9")
    assert Settings.load().top_k == 9              # env beats file


def test_compute_defaults(monkeypatch, tmp_path):
    _clear(monkeypatch)
    monkeypatch.setenv("SEBI_RAG_CONFIG", str(tmp_path / "none.toml"))
    s = Settings.load()
    assert s.device is None                 # auto-detect
    assert s.use_fp16 is False              # fp32 until the eval gate flips it
    assert s.encode_batch_size == 32
    assert s.embed_backend == "torch" and s.rerank_backend == "torch"


def test_compute_from_file(monkeypatch, tmp_path):
    _clear(monkeypatch)
    cfg = tmp_path / "c.toml"
    cfg.write_text(
        "[service]\ndevice = \"cpu\"\nuse_fp16 = true\n"
        "encode_batch_size = 64\nembed_backend = \"mlx\"\n",
        encoding="utf-8")
    monkeypatch.setenv("SEBI_RAG_CONFIG", str(cfg))
    s = Settings.load()
    assert s.device == "cpu" and s.use_fp16 is True
    assert s.encode_batch_size == 64 and s.embed_backend == "mlx"


def test_compute_env_overrides(monkeypatch, tmp_path):
    _clear(monkeypatch)
    monkeypatch.setenv("SEBI_RAG_CONFIG", str(tmp_path / "none.toml"))
    monkeypatch.setenv("SEBI_RAG_USE_FP16", "true")
    monkeypatch.setenv("SEBI_RAG_DEVICE", "mps")
    monkeypatch.setenv("SEBI_RAG_ENCODE_BATCH_SIZE", "16")
    s = Settings.load()
    assert s.use_fp16 is True and s.device == "mps" and s.encode_batch_size == 16
