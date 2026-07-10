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
class SpacesSettings:
    """[spaces] table: Hugging Face Spaces demo (CPU-only, HF-dataset corpus).

    Never read by the Apple-Silicon path; build_default_pipeline() ignores it.
    Env override prefix: SEBI_RAG_SPACES_<FIELD>.
    """

    dataset_repo: str = "opnsrcntrbtrian/sebi-circulars"
    index_repo: str = ""            # HF dataset repo holding prebuilt data/index artifacts
    default_config: str = "chunks"  # "chunks" | "corpus"
    default_subset: str = "full"    # "full" | "recent"
    recent_years: tuple[int, ...] = (2025, 2026)
    external_space: str = ""        # HF Space id for primary generation ("" = fallback only)
    external_api_name: str = "/predict"
    external_timeout_s: float = 20.0
    hf_model: str = "Qwen/Qwen2.5-0.5B-Instruct"  # CPU fallback generator
    max_tokens: int = 200
    temperature: float = 0.2
    top_p: float = 0.9
    top_k: int = 3
    timeout_s: float = 60.0
    abstain_threshold: float = 0.05
    superseded_penalty: float = 0.3


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
    spaces: SpacesSettings | None = None  # populated only by load_spaces()

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

    @classmethod
    def load_spaces(cls, config_path: str | Path | None = None) -> "Settings":
        """Settings.load() plus the [spaces] table as settings.spaces.*

        Load order per spaces field:
          env SEBI_RAG_SPACES_<FIELD>  >  [spaces] in config.toml  >  default.
        """
        import dataclasses

        base = cls.load(config_path)
        p = Path(config_path or os.environ.get("SEBI_RAG_CONFIG", ROOT / "config.toml"))
        tbl: dict = {}
        if p.exists():
            tbl = tomllib.loads(p.read_text(encoding="utf-8")).get("spaces", {})

        def get(key: str, default):
            return os.environ.get("SEBI_RAG_SPACES_" + key.upper(), tbl.get(key, default))

        d = SpacesSettings()  # defaults
        years = get("recent_years", list(d.recent_years))
        if isinstance(years, str):  # env override, e.g. "2025,2026"
            years = [y for y in years.replace(",", " ").split() if y]
        sp = SpacesSettings(
            dataset_repo=str(get("dataset_repo", d.dataset_repo)),
            index_repo=str(get("index_repo", d.index_repo)),
            default_config=str(get("default_config", d.default_config)),
            default_subset=str(get("default_subset", d.default_subset)),
            recent_years=tuple(int(y) for y in years),
            external_space=str(get("external_space", d.external_space)),
            external_api_name=str(get("external_api_name", d.external_api_name)),
            external_timeout_s=float(get("external_timeout_s", d.external_timeout_s)),
            hf_model=str(get("hf_model", d.hf_model)),
            max_tokens=int(get("max_tokens", d.max_tokens)),
            temperature=float(get("temperature", d.temperature)),
            top_p=float(get("top_p", d.top_p)),
            top_k=int(get("top_k", d.top_k)),
            timeout_s=float(get("timeout_s", d.timeout_s)),
            abstain_threshold=float(get("abstain_threshold", d.abstain_threshold)),
            superseded_penalty=float(get("superseded_penalty", d.superseded_penalty)),
        )
        return dataclasses.replace(base, spaces=sp)
