"""Settings: defaults, config.toml, and env-override precedence."""
from __future__ import annotations

from sebi_rag.settings import Settings

ENV_KEYS = ["SEBI_RAG_GENERATOR", "SEBI_RAG_TOP_K", "SEBI_RAG_RATE_PER_MIN",
            "SEBI_RAG_TIMEOUT_S", "SEBI_RAG_MLX_MODEL"]


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


def test_toml_then_env_precedence(monkeypatch, tmp_path):
    _clear(monkeypatch)
    cfg = tmp_path / "c.toml"
    cfg.write_text("[service]\ntop_k = 5\nrate_per_min = 10\n", encoding="utf-8")
    monkeypatch.setenv("SEBI_RAG_CONFIG", str(cfg))
    s = Settings.load()
    assert s.top_k == 5 and s.rate_per_min == 10   # from file
    monkeypatch.setenv("SEBI_RAG_TOP_K", "9")
    assert Settings.load().top_k == 9              # env beats file
