"""Segmentation: hierarchical chunking + metadata + stable citation IDs.

Minimal, deterministic, clause-boundary aware (splits on blank lines / sentence
ends, never mid-line). Mirrors docs/project_context.md section 4.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass(frozen=True)
class CircularMeta:
    circular_number: str
    issue_date: str = ""
    effective_date: str = ""
    subject: str = ""
    issuing_department: str = ""
    supersession_status: str = "in_force"  # in_force | superseded | amended
    amendment_history: tuple[str, ...] = ()
    version_lineage: tuple[str, ...] = ()
    circular_type: str = ""          # metadata migration 2026-07: see metadata.py
    validity_status: str = ""        # current | superseded | partially_superseded | unknown
    superseded_by_id: tuple[str, ...] = ()  # explicit_text tier only


@dataclass(frozen=True)
class Chunk:
    id: str            # stable retrieval id, used for citation
    doc_id: str        # circular_number
    section: str       # hierarchy path: doc/section/paragraph
    text: str
    meta: dict[str, Any] = field(default_factory=dict)


def _paragraphs(text: str, max_chars: int) -> list[str]:
    """Split into units each <= max_chars.

    PDF-extracted text often lacks blank-line paragraph breaks, so fall back to
    single newlines, then to sentence boundaries, then to hard character windows.
    Clause boundaries are preserved wherever a natural break exists.
    """
    units: list[str] = []

    def add(seg: str) -> None:
        seg = seg.strip()
        if not seg:
            return
        if len(seg) <= max_chars:
            units.append(seg)
            return
        # too long: try sentence split, else hard char windows
        sentences = re.split(r"(?<=[.;:])\s+", seg)
        if len(sentences) > 1:
            for s in sentences:
                add(s)
        else:
            for i in range(0, len(seg), max_chars):
                units.append(seg[i : i + max_chars].strip())

    for block in re.split(r"\n\s*\n", text.strip()):
        block = block.strip()
        if not block:
            continue
        if len(block) <= max_chars:
            units.append(block)
        else:
            for line in block.split("\n"):
                add(line)
    return units


def hierarchical_chunk(
    text: str,
    meta: CircularMeta,
    max_chars: int = 1200,
    overlap_chars: int = 150,
) -> list[Chunk]:
    """Document -> section -> paragraph chunks with stable IDs.

    A "section" is detected by a leading heading line (e.g. "2. Applicability");
    paragraphs within are packed up to max_chars with character overlap.
    """
    chunks: list[Chunk] = []
    section_name = "preamble"
    buf = ""
    para_idx = 0

    def flush(sec: str, body: str) -> None:
        nonlocal para_idx
        body = body.strip()
        if not body:
            return
        cid = f"{meta.circular_number}#{sec}#{para_idx}"
        # F1 (ADR-001): contextual enrichment — prepend document identity so
        # dense/sparse indexing can disambiguate topically-overlapping circulars.
        header = " | ".join(
            p for p in (meta.circular_number, meta.subject.strip()[:120], sec) if p
        )
        chunks.append(
            Chunk(
                id=cid,
                doc_id=meta.circular_number,
                section=f"{meta.circular_number}/{sec}/p{para_idx}",
                text=f"{header}\n{body}",
                meta=asdict(meta),
            )
        )
        para_idx += 1

    heading = re.compile(r"^\s*(\d+(\.\d+)*)[.)]\s+\S")
    for para in _paragraphs(text, max_chars):
        first_line = para.splitlines()[0]
        if heading.match(first_line):
            if buf:
                flush(section_name, buf)
                buf = ""
            section_name = first_line.strip()[:60]
        if len(buf) + len(para) + 1 > max_chars and buf:
            flush(section_name, buf)
            buf = buf[-overlap_chars:] + "\n" + para
        else:
            buf = (buf + "\n" + para) if buf else para
    flush(section_name, buf)
    return chunks
