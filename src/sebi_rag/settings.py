"""Central configuration: config.toml defaults, overridden by SEBI_RAG_* env vars.

Secrets (API key) are env-only and never read from the file. Load order per field:
  env SEBI_RAG_<FIELD>  >  [service] in config.toml  >  built-in default.
"""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    corpus_path: str
    index_dir: str
    generator: str = "mlx"
    mlx_model: str = "mlx-community/Qwen2.5-1.5B-Instruct-4bit"
    top_k: int = 3
    abstain_threshold: float = 0.05  # score floor; near-domain gate = SubjectSimJudge
    superseded_penalty: float = 0.3
    rate_per_min: int = 60
    timeout_s: float = 30.0

    @classmethod
    def load(cls, config_path: str | Path | None = None) -> "Settings":
        p = Path(config_path or os.environ.get("SEBI_RAG_CONFIG", ROOT / "config.toml"))
        svc: dict = {}
        if p.exists():
            svc = tomllib.loads(p.read_text(encoding="utf-8")).get("service", {})

        def get(key: str, default):
            return os.environ.get("SEBI_RAG_" + key.upper(), svc.get(key, default))

        return cls(
            corpus_path=str(get("corpus_path", str(ROOT / "data" / "corpus" / "circulars.jsonl"))),
            index_dir=str(get("index_dir", str(ROOT / "data" / "index"))),
            generator=str(get("generator", "mlx")),
            mlx_model=str(get("mlx_model", "mlx-community/Qwen2.5-1.5B-Instruct-4bit")),
            top_k=int(get("top_k", 3)),
            abstain_threshold=float(get("abstain_threshold", 0.05)),
            superseded_penalty=float(get("superseded_penalty", 0.3)),
            rate_per_min=int(get("rate_per_min", 60)),
            timeout_s=float(get("timeout_s", 30.0)),
        )
