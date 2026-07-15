"""Central configuration: config.toml defaults, overridden by SEBI_RAG_* env vars.

Secrets (API key) are env-only and never read from the file. Load order per field:
  env SEBI_RAG_<FIELD>  >  [service] in config.toml  >  built-in default.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11 (e.g. HF Spaces default image)
    import tomli as tomllib  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[2]


def _get(key: str, default, prefix: str, svc: dict) -> object:
    """Resolve a setting: env var > config dict > default."""
    return os.environ.get(prefix + key.upper(), svc.get(key, default))


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

        return cls(
            corpus_path=str(_get("corpus_path", str(ROOT / "data" / "corpus" / "circulars.jsonl"), "SEBI_RAG_", svc)),
            index_dir=str(_get("index_dir", str(ROOT / "data" / "index"), "SEBI_RAG_", svc)),
            generator=str(_get("generator", "mlx", "SEBI_RAG_", svc)),
            mlx_model=str(_get("mlx_model", "mlx-community/Qwen2.5-1.5B-Instruct-4bit", "SEBI_RAG_", svc)),
            top_k=int(_get("top_k", 3, "SEBI_RAG_", svc)),
            abstain_threshold=float(_get("abstain_threshold", 0.05, "SEBI_RAG_", svc)),
            superseded_penalty=float(_get("superseded_penalty", 0.3, "SEBI_RAG_", svc)),
            rate_per_min=int(_get("rate_per_min", 60, "SEBI_RAG_", svc)),
            timeout_s=float(_get("timeout_s", 30.0, "SEBI_RAG_", svc)),
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

        d = SpacesSettings()  # defaults
        years = _get("recent_years", list(d.recent_years), "SEBI_RAG_SPACES_", tbl)
        if isinstance(years, str):  # env override, e.g. "2025,2026"
            years = [y for y in years.replace(",", " ").split() if y]
        sp = SpacesSettings(
            dataset_repo=str(_get("dataset_repo", d.dataset_repo, "SEBI_RAG_SPACES_", tbl)),
            index_repo=str(_get("index_repo", d.index_repo, "SEBI_RAG_SPACES_", tbl)),
            default_config=str(_get("default_config", d.default_config, "SEBI_RAG_SPACES_", tbl)),
            default_subset=str(_get("default_subset", d.default_subset, "SEBI_RAG_SPACES_", tbl)),
            recent_years=tuple(int(y) for y in years),
            external_space=str(_get("external_space", d.external_space, "SEBI_RAG_SPACES_", tbl)),
            external_api_name=str(_get("external_api_name", d.external_api_name, "SEBI_RAG_SPACES_", tbl)),
            external_timeout_s=float(_get("external_timeout_s", d.external_timeout_s, "SEBI_RAG_SPACES_", tbl)),
            hf_model=str(_get("hf_model", d.hf_model, "SEBI_RAG_SPACES_", tbl)),
            max_tokens=int(_get("max_tokens", d.max_tokens, "SEBI_RAG_SPACES_", tbl)),
            temperature=float(_get("temperature", d.temperature, "SEBI_RAG_SPACES_", tbl)),
            top_p=float(_get("top_p", d.top_p, "SEBI_RAG_SPACES_", tbl)),
            top_k=int(_get("top_k", d.top_k, "SEBI_RAG_SPACES_", tbl)),
            timeout_s=float(_get("timeout_s", d.timeout_s, "SEBI_RAG_SPACES_", tbl)),
            abstain_threshold=float(_get("abstain_threshold", d.abstain_threshold, "SEBI_RAG_SPACES_", tbl)),
            superseded_penalty=float(_get("superseded_penalty", d.superseded_penalty, "SEBI_RAG_SPACES_", tbl)),
        )
        return dataclasses.replace(base, spaces=sp)
