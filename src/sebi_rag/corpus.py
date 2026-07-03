"""Load the real SEBI circular corpus (data/corpus/circulars.jsonl) into chunks."""
from __future__ import annotations

import json
from pathlib import Path

from .segment import Chunk, CircularMeta, hierarchical_chunk


def load_circulars(path: str | Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        meta = CircularMeta(
            circular_number=r["circular_number"],
            issue_date=r.get("issue_date", ""),
            effective_date=r.get("effective_date", ""),
            subject=r.get("subject", ""),
            issuing_department=r.get("issuing_department", ""),
            supersession_status=r.get("supersession_status", "in_force"),
            amendment_history=tuple(r.get("amendment_history", [])),
            version_lineage=tuple(r.get("version_lineage", [])),
        )
        chunks.extend(hierarchical_chunk(r["text"], meta))
    return chunks
