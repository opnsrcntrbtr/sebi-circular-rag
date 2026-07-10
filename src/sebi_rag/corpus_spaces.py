"""HF-Hub corpus loading for the Hugging Face Spaces demo (CPU path).

Loads the published dataset (opnsrcntrbtrian/sebi-circulars) instead of the
local data/corpus JSONL. Two configs:

  "chunks"  — published section-aware chunks. `text` on the Hub is de-fused
              from `context_header`; we re-fuse them so retrieval sees the
              same enriched text as the local index (F1 contextual enrichment).
  "corpus"  — full circulars, re-chunked with the same hierarchical_chunk()
              as local ingestion, so retrieval behavior stays identical.

Never imported by the Apple-Silicon path (api.build_default_pipeline).
`datasets` is imported lazily so local test runs don't require it.
"""
from __future__ import annotations

from .segment import Chunk, CircularMeta, hierarchical_chunk
from .settings import Settings


def _year(issue_date: object) -> int:
    try:
        return int(str(issue_date or "")[:4])
    except ValueError:
        return 0


def _keep(row: dict, subset: str, recent_years: tuple[int, ...]) -> bool:
    return subset != "recent" or _year(row.get("issue_date")) in recent_years


def _meta_from_row(row: dict) -> CircularMeta:
    return CircularMeta(
        circular_number=row["circular_number"],
        issue_date=row.get("issue_date") or "",
        effective_date=row.get("effective_date") or "",
        subject=row.get("subject") or "",
        issuing_department=row.get("issuing_department") or "",
        supersession_status=row.get("supersession_status") or "in_force",
        version_lineage=tuple(row.get("version_lineage") or ()),
    )


def load_hf_rows(settings: Settings, config_name: str) -> list[dict]:
    """One HF dataset config as plain dicts (network; cached by `datasets`)."""
    from datasets import load_dataset

    assert settings.spaces is not None, "use Settings.load_spaces()"
    ds = load_dataset(settings.spaces.dataset_repo, config_name, split="train")
    return [dict(r) for r in ds]


def load_corpus_records_from_hf(
    settings: Settings, subset: str = "full"
) -> list[dict]:
    """Full-circular records (dicts) for build_lineage() — always the
    "corpus" config regardless of which config is indexed for retrieval."""
    assert settings.spaces is not None
    ry = settings.spaces.recent_years
    return [r for r in load_hf_rows(settings, "corpus") if _keep(r, subset, ry)]


def load_circulars_from_hf(
    settings: Settings,
    config_name: str,    # "chunks" | "corpus"
    subset: str,         # "full" | "recent"
) -> list[Chunk]:
    """HF-dataset counterpart of corpus.load_circulars() — returns Chunks
    ready for HybridRetriever.build()."""
    assert settings.spaces is not None
    if config_name not in ("chunks", "corpus"):
        raise ValueError(f"unknown config_name: {config_name!r}")
    if subset not in ("full", "recent"):
        raise ValueError(f"unknown subset: {subset!r}")

    rows = load_hf_rows(settings, config_name)
    ry = settings.spaces.recent_years
    chunks: list[Chunk] = []
    if config_name == "corpus":
        for r in rows:
            if _keep(r, subset, ry):
                chunks.extend(hierarchical_chunk(r["text"], _meta_from_row(r)))
        return chunks

    from dataclasses import asdict

    for r in rows:
        if not _keep(r, subset, ry):
            continue
        header = r.get("context_header") or ""
        body = r["text"]
        chunks.append(
            Chunk(
                id=r["chunk_id"],
                doc_id=r["doc_id"],
                section=r["section"],
                # published rows are de-fused; local Chunk.text = header\nbody
                text=f"{header}\n{body}" if header else body,
                meta=asdict(_meta_from_row(r)),
            )
        )
    return chunks
