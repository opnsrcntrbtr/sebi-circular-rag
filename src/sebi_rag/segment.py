"""Segmentation: hierarchical chunking + metadata + stable citation IDs.

Minimal, deterministic, clause-boundary aware (splits on blank lines / sentence
ends, never mid-line). Mirrors docs/project_context.md section 4.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Any

# Clause terminators: a recorded heading ending in one of these is complete
# and must not absorb the next physical line (wrapped-clause folding).
_TERMINATORS = (":", ";", ".", "–", "-")


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
    section_head = ""   # full (untruncated) heading line of the current section
    section_num = ""    # dotted number of the current heading, e.g. "5" or "5.1"
    carry = ""          # bare parent heading(s) deferred to prefix the next chunk
    heads: dict[str, str] = {}  # dotted num -> full heading line (governing clause)
    open_num = ""  # head still absorbing hard-wrapped continuation lines
    buf = ""
    para_idx = 0

    def flush(sec: str, body: str) -> None:
        nonlocal para_idx, carry
        body = body.strip()
        if not body:
            return
        if carry:
            body = f"{carry}\n{body}"
            carry = ""
        # Intervention #1 (2026-07-16 failure taxonomy): numbered sub-clauses
        # ("4.1.1.2. ...") are meaningless without their governing clause
        # ("4.1.1 On and from the date... the CRA shall:"). Prepend the nearest
        # recorded ancestor heading so both retrievers see the context.
        num = section_num
        while "." in num:
            num = num.rsplit(".", 1)[0]
            gov = heads.get(num, "")
            if gov:
                if gov not in body:
                    body = f"{gov}\n{body}"
                break
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
        m = heading.match(first_line)
        if m:
            hnum = m.group(1)
            if buf:
                # A section whose own body is only its heading (content lives
                # entirely in subsections) must not become a standalone chunk:
                # the leading ordinal ("5. Number of nominees:") reads as a value
                # to extractive generators. When the incoming heading is this
                # section's direct child, defer the bare heading as a prefix for
                # the child chunk instead of emitting it alone.
                is_child = hnum.startswith(f"{section_num}.") if section_num else False
                if is_child and buf.strip() == section_head:
                    carry = f"{carry}\n{buf.strip()}".strip() if carry else buf.strip()
                else:
                    flush(section_name, buf)
                buf = ""
            section_name = first_line.strip()[:60]
            section_head = first_line.strip()
            section_num = hnum
            heads[hnum] = first_line.strip()[:300]
            open_num = hnum
        elif open_num:
            # SEBI PDFs hard-wrap clause text; a non-heading paragraph right
            # after a heading is usually its continuation. Absorb it into the
            # recorded head unless the head is already terminated or capped.
            head = heads[open_num]
            if len(head) < 300 and not head.endswith(_TERMINATORS):
                heads[open_num] = f"{head} {' '.join(para.split())}"[:300]
            else:
                open_num = ""
        if len(buf) + len(para) + 1 > max_chars and buf:
            flush(section_name, buf)
            buf = buf[-overlap_chars:] + "\n" + para
        else:
            buf = (buf + "\n" + para) if buf else para
    flush(section_name, buf)
    return chunks
