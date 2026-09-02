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

# Table-row shredding fix (2026-09-01, memory/nominee-count-chunker-bug.md's
# "live defect" postscript): a PDF-flattened table row ("2. Brent Crude Oil
# BBL 400,000") matches the heading regex below exactly as well as a real
# numbered heading, so without this guard each row opens its own section and
# is flushed as a one-line chunk, destroying row<->column-header association.
_TABLE_ROW = re.compile(r"^\s*(\d+(?:\.\d+)*)[.)]\s*(.*)$")
_TABLE_ROW_MAX_TRAILING_CHARS = 60  # a real section title this short but
                                     # this is only diagnostic combined with
                                     # the run-length + terminator checks below
_MIN_TABLE_RUN = 3  # a single short heading can be genuine; 3+ back-to-back
                    # with nothing else between them is not prose structure

# Gapped-table-row fix (2026-09-02, docs/status.md's 2026-09-02 scoping entry):
# a PDF-flattened table row's own wrapped label, or the tail of the previous
# row's, sits BETWEEN two candidates ("20. Total income from operations\nNet
# profit for the period\n21. before tax...") - real corpus measurement of the
# LODR results-format table (SEBI/HO/CFD/PoD2/CIR/P/0155) put every such
# filler line at <=78 chars, well short of a real body-prose sentence, so 80
# separates the two cleanly without weakening the terminator check that keeps
# genuine headings-with-body-text safe (see _is_table_row_filler).
_TABLE_ROW_FILLER_MAX_CHARS = 80
_MAX_TABLE_GAP = 2  # tolerate up to 2 consecutive filler lines between same-
                    # depth candidates; a 3rd (measured on the same real
                    # table's row-4->row-5 transition) is deliberately NOT
                    # bridged - see docs/status.md's 2026-09-02 entry.

# TOC long-title rows fix (2026-09-03, docs/status.md's 2026-09-02 scoping
# entry's item 1): a TOC row's "title + page number" text ("Registration of
# Brokers - Verification of antecedents of the applicant 10") is longer than
# a table cell value and routinely exceeds _TABLE_ROW_MAX_TRAILING_CHARS
# (60), so it never becomes a candidate at all - the gap tolerance above
# never gets a chance to run. Relaxing the trailing-length cap unconditionally
# is unsafe: corpus-measured, it also matches real body prose broken
# mid-sentence ("2.The remaining collateral of Client-3 (Rs 13 crore)...").
# Scoping the relaxed cap to a bounded window after a literal "TABLE OF
# CONTENTS" marker paragraph - the actual structural cause of this layout -
# cuts the corpus-wide false-candidate count from 2,365 to 468 (across 35
# docs), and the false positives found by manual inspection sit >6,000
# paragraphs past their nearest marker, far outside any window this size.
_TOC_MARKER = re.compile(r"^\s*(TABLE OF CONTENTS|CONTENTS|INDEX)\s*$", re.I)
_TOC_ROW_MAX_TRAILING_CHARS = 120  # vs. 60 for a table cell value; TOC
                                    # titles run longer but still end in a
                                    # bare page number, not free prose
_TOC_PAGE_NUMBER = re.compile(r"\s\d{1,3}$")  # a trailing page number, not
                                                # part of a larger token
_TOC_WINDOW = 200  # paragraphs after the marker where the relaxed candidate
                    # check applies; the longest real TOC measured (86 rows
                    # across 9 sections, SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/90)
                    # spans 192 paragraphs from its marker to its last row.
                    # Widening this to 300 was tried and reverted: it changes
                    # 11 more chunks corpus-wide (83752 -> 83741) that were
                    # never inspected - do not widen without repeating the
                    # per-doc inspection pass this value's fix received.

# F-03 fix (caveman-review, 2026-09-02): segment.py is shared by BOTH code
# paths (src/sebi_rag/corpus_spaces.py imports hierarchical_chunk directly —
# the two-paths rule only names *_spaces.py files, not shared modules like
# this one). A chunker change moves chunk boundaries without touching
# embed_model, so retrieve.py's F-01/F-02 embed_model guard can't detect it.
# Bump this string whenever hierarchical_chunk()'s output changes in a way
# that would make an index built by an older version stale — retrieve.py
# stamps it into meta.json and warns (not refuses; stale chunking is drift,
# not the silent embedding-space corruption an embed_model mismatch is) on
# a mismatch at load time. The HF Spaces prebuilt index
# (scripts/upload_spaces_index.py) is the concrete risk this closes: it is
# only ever regenerated by a manual re-run, so it silently outlives any
# local segment.py change until this warning surfaces the drift.
CHUNKER_VERSION = "2026-09-03-toc-long-title-merge"


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


def _table_row_depth(line: str) -> int | None:
    """Nesting depth of a numbered line ("2.1.3" -> 2), or None if it isn't
    one at all."""
    m = _TABLE_ROW.match(line)
    return m.group(1).count(".") if m else None


def _is_table_row_candidate(line: str) -> bool:
    """A numbered line whose own trailing text is short and does NOT end in
    a clause terminator. Genuine section titles this short almost always end
    in ':' ("6. Nomination process:") or, as full sentences, in '.' — a bare
    table cell value ("2. Brent Crude Oil BBL 400,000", "48. 119") typically
    has neither, which is what lets this distinguish the two without
    weakening the heading regex itself."""
    m = _TABLE_ROW.match(line)
    if not m:
        return False
    rest = m.group(2).strip()
    return len(rest) < _TABLE_ROW_MAX_TRAILING_CHARS and not rest.endswith(_TERMINATORS)


def _is_table_row_filler(line: str) -> bool:
    """A short, non-heading-shaped line that may sit between two same-depth
    table-row candidates without breaking the run - the wrapped tail of one
    row's label, or the lead-in to the next. Excludes anything the numbered-
    line regex matches at all (an incidentally-numbered line is handled by
    the candidate check, not treated as connective filler) and anything long
    or terminator-ending, which reads as real body prose and must still break
    the run exactly as it did before this fix - see _TABLE_ROW_FILLER_MAX_CHARS."""
    line = line.strip()
    if not line or _TABLE_ROW.match(line):
        return False
    return len(line) < _TABLE_ROW_FILLER_MAX_CHARS and not line.endswith(_TERMINATORS)


def _is_toc_row_candidate(line: str) -> bool:
    """A top-level numbered line whose trailing text ends in a bare page
    number ("Registration of Brokers ... applicant 10") - the TOC-specific
    counterpart to _is_table_row_candidate, only ever consulted within a
    marked TOC region (see _toc_region_indices). Restricted to depth 0 (no
    dot in the number) because real TOC entries are flat; a dotted number
    ("72.1.") ending mid-sentence is far more likely to be a real absorbed
    sub-clause continuation than a TOC row."""
    m = _TABLE_ROW.match(line)
    if not m or "." in m.group(1):
        return False
    rest = m.group(2).strip()
    if not rest or rest.endswith(_TERMINATORS):
        return False
    return len(rest) < _TOC_ROW_MAX_TRAILING_CHARS and bool(_TOC_PAGE_NUMBER.search(" " + rest))


def _toc_region_indices(paras: list[str]) -> set[int]:
    """Indices of paragraphs within _TOC_WINDOW paragraphs after a literal
    TOC marker paragraph - the only region where _is_toc_row_candidate's
    relaxed trailing-length cap may apply."""
    idxs: set[int] = set()
    for i, p in enumerate(paras):
        lines = p.splitlines()
        if len(lines) == 1 and _TOC_MARKER.match(lines[0]):
            idxs.update(range(i + 1, min(len(paras), i + 1 + _TOC_WINDOW)))
    return idxs


def _merge_table_rows(paras: list[str]) -> list[str]:
    """Collapse a run of >=3 same-depth table-row candidates into one
    paragraph, so hierarchical_chunk's heading-detection loop treats the
    whole run as one section instead of one chunk per row. Candidates may be
    separated by up to _MAX_TABLE_GAP short filler lines (2026-09-02 fix) -
    a row's own wrapped label commonly falls between it and the next row's
    number in a PDF-flattened table.

    Deliberately conservative: a genuine heading run is broken by real body
    prose between headings (multi-line, long, or terminator-ending - none of
    which pass _is_table_row_filler), by a depth change, or by a terminator-
    ending candidate line (a real heading awaiting a body) - the nominee-bug
    fixture's "5." / "5.1." / "5.2." / "6." sequence hits none of the
    candidate criteria at all (every line ends in ':' or '.') and is
    untouched, exactly as before this fix.
    """
    toc_idxs = _toc_region_indices(paras)

    def is_candidate(idx: int, line: str) -> bool:
        if _is_table_row_candidate(line):
            return True
        return idx in toc_idxs and _is_toc_row_candidate(line)

    out: list[str] = []
    i, n = 0, len(paras)
    while i < n:
        para = paras[i]
        lines = para.splitlines()
        if len(lines) == 1 and is_candidate(i, lines[0]):
            depth = _table_row_depth(lines[0])
            j, n_candidates, run_end = i + 1, 1, i + 1
            while j < n:
                pl = paras[j].splitlines()
                if (
                    len(pl) == 1
                    and is_candidate(j, pl[0])
                    and _table_row_depth(pl[0]) == depth
                ):
                    j += 1
                    n_candidates += 1
                    run_end = j
                    continue
                k = j
                while (
                    k < n
                    and k - j < _MAX_TABLE_GAP
                    and len(paras[k].splitlines()) == 1
                    and _is_table_row_filler(paras[k].splitlines()[0])
                ):
                    k += 1
                if (
                    k < n
                    and len(paras[k].splitlines()) == 1
                    and is_candidate(k, paras[k].splitlines()[0])
                    and _table_row_depth(paras[k].splitlines()[0]) == depth
                ):
                    j, n_candidates, run_end = k + 1, n_candidates + 1, k + 1
                    continue
                break
            if n_candidates >= _MIN_TABLE_RUN:
                out.append("\n".join(paras[i:run_end]))
                i = run_end
                continue
        out.append(para)
        i += 1
    return out


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
                # Check if gov is already in body to avoid duplicating absorbed text.
                # Use startswith check because carry may be truncated (80 chars) but
                # gov is the full absorbed text — we need to detect if body already
                # starts with gov (even if truncated in carry).
                _body_lines = body.split('\n')[:3]
                _gov_stripped = gov.strip()
                _already_has_gov = (_gov_stripped in body or
                                    any(_line.startswith(_gov_stripped) or _gov_stripped.startswith(_line.strip())
                                        for _line in _body_lines if _line.strip()))
                if not _already_has_gov:
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
    paras = _merge_table_rows(_paragraphs(text, max_chars))
    i = 0
    while i < len(paras):
        para = paras[i]
        first_line = para.splitlines()[0]
        m = heading.match(first_line)
        if m:
            hnum = m.group(1)
            is_child = hnum.startswith(f"{section_num}.") if section_num else False
            if buf:
                # A section whose own body is only its heading (content lives
                # entirely in subsections) must not become a standalone chunk:
                # the leading ordinal ("5. Number of nominees:") reads as a value
                # to extractive generators. When the incoming heading is this
                # section's direct child, defer the bare heading as a prefix for
                # the child chunk instead of emitting it alone.
                if is_child and buf.strip() == section_head:
                    # Parent heading was buffered as its own chunk body.
                    # Defer it as a prefix for the child chunk instead.
                    carry = f"{carry}\n{buf.strip()}".strip() if carry else buf.strip()
                elif section_name == "preamble" and not is_child:
                    # Flush the preamble without trying to include the next
                    # paragraph — it may be a continuation of the heading,
                    # not actual content. Let absorption handle it.
                    flush(section_name, buf)
                elif is_child:
                    # Parent heading was buffered (buf != empty) but doesn't match
                    # section_head exactly — flush with whatever we have.
                    flush(section_name, buf)
                else:
                    flush(section_name, buf)
                buf = ""
            elif is_child:
                # Direct child of current section.
                # NOTE: We intentionally DO NOT set carry here — flush() already
                # prepends ancestor headings via gov lookup. Setting carry from
                # parent_head causes duplication because gov prepending adds it again.
                pass
            else:
                # Not a direct child of current section, but may be a child of
                # an ancestor (e.g., 4.1.2 is child of 4.1.1, not 4.1.1.1).
                # Check all ancestors in heads for absorbed text to carry.
                for anc_num in reversed(list(heads.keys())):
                    if hnum.startswith(f"{anc_num}.") and anc_num != section_num:
                        anc_head = heads[anc_num]
                        if anc_head and (not carry or anc_head != carry):
                            carry = anc_head.strip()
                        break
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
                # Do NOT add absorbed continuation text to buf — it belongs
                # to the heading's governing clause, not to section content.
                i += 1
                continue
            else:
                open_num = ""
        if len(buf) + len(para) + 1 > max_chars and buf:
            flush(section_name, buf)
            buf = buf[-overlap_chars:] + "\n" + para
        else:
            buf = (buf + "\n" + para) if buf else para
        i += 1
    flush(section_name, buf)
    return chunks
