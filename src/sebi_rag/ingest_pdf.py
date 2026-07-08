"""Local PDF ingestion for SEBI circulars.

Drop a circular PDF into data/raw/ and run:

    .venv/bin/python -m sebi_rag.ingest_pdf data/raw/<file>.pdf \
        --corpus data/corpus/circulars.jsonl --source-url <official url>

Extracts the circular number, issue date, subject, issuing department and
version lineage (referenced master/parent circulars), then appends one record
to the corpus JSONL with provenance. Deterministic, fully local — no network.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

import pdfplumber

# Well-formed SEBI reference numbers (used to mine the body for cited/parent
# circulars), e.g. SEBI/HO/CFD/CFD-PoD-1/P/CIR/2023/123 or CIR/CFD/CMD/4/2015.
_NEW = r"SEBI/HO/[A-Za-z0-9_()\-/]+?/\d{4}/\d+"
_OLD = r"CIR/[A-Za-z0-9_()\-/]+?/\d+/\d{4}"
# New 2026 departmental-order format: HO/(N)YYYY-DEPT (no /CIR/, used by internal orders)
_NEW_FMT2 = r"(?:SEBI/)?HO/\(\d+\)\d{4}-[A-Za-z0-9_()\-]+"
REF_RE = re.compile(rf"(?:{_NEW}|{_OLD}|{_NEW_FMT2})")

# The document's OWN number sits in the header (before "To,"). Formats vary
# widely in 2026 (e.g. HO/47/17/12(11)2025-MRD-POD3/I/11107/2026), so we take the
# first slash-heavy header token rather than a single rigid pattern.
HEADER_TOKEN_RE = re.compile(r"^(?:SEBI/)?(?:HO|CIR)/")

MONTH_DATE_RE = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|"
    r"November|December)\s+(\d{1,2}),?\s+(\d{4})"
)
NUM_DATE_RE = re.compile(r"\b(\d{1,2})[.\-/](\d{1,2})[.\-/](20\d{2})\b")
DEPT_RE = re.compile(r"SEBI/HO/([A-Za-z0-9]+)/")
ISSUED_RE = re.compile(r"Issued on\s*:?\s*(.{0,30})", re.I)
UPDATED_RE = re.compile(r"Last updated on\s*:?\s*(.{0,30})", re.I)


def _ocr_text(pdf_path: str | Path) -> str:
    """OCR a scanned PDF. Requires pytesseract + pdf2image (+ system tesseract,
    poppler). Optional dependency — raises a clear error if unavailable."""
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError as e:  # noqa: BLE001
        raise RuntimeError(
            "OCR needs `pip install pytesseract pdf2image` plus system "
            f"tesseract + poppler. Original: {e}")
    pages = convert_from_path(str(pdf_path))
    text = "\n".join(pytesseract.image_to_string(p) for p in pages)
    return re.sub(r"[ \t]+", " ", text).strip()


def extract_text(pdf_path: str | Path, ocr: bool = False) -> str:
    parts = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    text = re.sub(r"[ \t]+", " ", "\n".join(parts)).strip()
    if not text and ocr:                       # scanned/image PDF -> OCR fallback
        text = _ocr_text(pdf_path)
    return text


def _header(text: str) -> str:
    """Text above the addressee block ('To,' / Hindi 'प्रति'), else first 600 chars."""
    m = re.search(r"\n\s*(?:To,?|प्रति)\b", text)
    return text[: m.start()] if m else text[:600]


def _iso_date(block: str) -> str:
    m = MONTH_DATE_RE.search(block)
    if m:
        try:
            return dt.datetime.strptime(
                f"{m.group(1)} {int(m.group(2))}, {m.group(3)}", "%B %d, %Y"
            ).date().isoformat()
        except ValueError:
            pass
    m = NUM_DATE_RE.search(block)  # DD.MM.YYYY (SEBI convention)
    if m:
        try:
            return dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat()
        except ValueError:
            return ""
    return ""


def _subject(text: str) -> str:
    m = re.search(r"Sub(?:ject)?\s*:\s*(.+?)(?:\n\s*\n|\n\d+\.)", text, re.S)
    if not m:
        return ""
    return re.sub(r"\s+", " ", m.group(1)).strip()


def _primary_number(header: str, full: str) -> str:
    # rejoin numbers split by a space after a slash, e.g. "CIR/ 2025/104" or
    # "DDHS-PoD-2/ I/11700/2026" (PDF layout inserts a space mid-number).
    # Rejoin tokens split by space after a slash — includes space before '(' for
    # HO/ (79)2026-style references where the parenthetical number starts with '('
    header = re.sub(r"/\s+(?=[A-Za-z0-9(])", "/", header)
    for tok in header.split():
        t = tok.strip(".,;:")
        if HEADER_TOKEN_RE.match(t) and t.count("/") >= 3 and re.search(r"\d", t):
            return t

    # FIX: Some SEBI circulars use department-only prefixes without HO/CIR.
    # e.g. "AFD/P/CIR/2022/125" or "CFD/MRD/CIR/2024/10". Accept any token
    # with ≥3 slashes that contains a well-formed reference segment.
    for tok in header.split():
        t = tok.strip(".,;:")
        if t.count("/") >= 4 and "CIR" in t:
            return t

    # FIX: Reference may be split across tokens by spaces (e.g. "HO/ (79)2026-
    # MRD" → after slash-rejoin becomes "HO/(79)2026-MRD").  Rejoin all tokens
    # that sit between the first known prefix and a date-like token, then look.
    parts = header.split()
    # Find first SEBI/HO or CIR anchor
    anchor_idx = None
    for i, tok in enumerate(parts):
        t = tok.strip(".,;:")
        if HEADER_TOKEN_RE.match(t) or re.match(r"^\d{4}/", t):
            anchor_idx = i
            break
    if anchor_idx is not None:
        # Try joining consecutive tokens from anchor and look for a slash-heavy
        # string with CIR or year pattern.  Also try the broader REF_RE as last resort.
        merged = re.sub(r"/\s+(?=[A-Za-z0-9])", "/", " ".join(parts[anchor_idx:anchor_idx + 4]))
        m = REF_RE.search(merged)
        if m:
            return m.group(0)
        # Also try a year-first pattern: YYYY/XXX/CIR...
        m = re.search(r"\d{4}/[A-Za-z0-9_()\-/]+?/\d+", merged)
        if m:
            return m.group(0)

    # New-format dept order (2026): HO/(N)YYYY-DEPT  or  SEBI/HO/DEPT/(N)YYYY-...
    # These have no /CIR/ and may be the *only* token on the line — nothing to anchor
    # to.  Catch them after all other fallbacks.
    dept_order_re = re.compile(
        r"HO/\(\d+\)\d{4}-[A-Za-z0-9_()\-]+")
    m = dept_order_re.search(header)
    if m:
        return m.group(0)

    # Also accept SEBI/HO/DEPT/(N)YYYY-... (slash-heavy with parenthetical year)
    m = re.search(r"SEBI/HO/[A-Za-z0-9_()\-]+/\(\d+\)\d{4}-[A-Za-z0-9_()\-]+", header)
    if m:
        return m.group(0)

    # Last fallback: search full document text for the earliest well-formed ref
    m = REF_RE.search(full)
    return m.group(0) if m else ""


def _labeled_date(header: str, label_re: re.Pattern) -> str:
    m = label_re.search(header)
    return _iso_date(m.group(1)) if m else ""


def parse_meta(text: str) -> dict:
    header = _header(text)
    primary = _primary_number(header, text)
    # lineage = well-formed references in the body, minus the primary
    lineage = []
    for m in REF_RE.finditer(text):
        n = m.group(0)
        if n != primary and n not in lineage:
            lineage.append(n)
    dm = DEPT_RE.search(primary) if primary else None
    # Master circulars carry "Issued on" (original) + "Last updated on" (current).
    issued = _labeled_date(header, ISSUED_RE)
    updated = _labeled_date(header, UPDATED_RE)
    return {
        "circular_number": primary,
        "issue_date": issued or _iso_date(header) or _iso_date(text),
        "effective_date": updated,
        "subject": _subject(text),
        "issuing_department": dm.group(1) if dm else "",
        "version_lineage": lineage,
    }


# F4 (ADR-001): ingestion-time scan for instruction-like content in extracted
# PDF text (indirect prompt injection, OWASP LLM01). Flags are recorded on the
# corpus record — review, don't silently drop: legal text may legitimately
# quote such phrases, and a hard reject would be a censorship bug.
_INJECTION_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"ignore\s+(?:all\s+|any\s+)?(?:previous|prior|above|earlier)\s+"
        r"(?:instructions|context|prompts?)",
        r"disregard\s+(?:all\s+|any\s+)?(?:previous|prior|above)\s+"
        r"(?:instructions|context)",
        r"\bsystem\s+prompt\b",
        r"\byou\s+are\s+now\b",
        r"\bnew\s+instructions?\s*:",
        r"\brespond\s+only\s+with\b",
        r"\bdo\s+not\s+(?:cite|mention|reveal)\b",
        r"<<<\s*(?:END\s+)?SOURCE",  # spoofing our own F4 delimiters
    )
]


def injection_scan(text: str) -> list[str]:
    """Return the list of matched instruction-like patterns (empty = clean)."""
    return [m.group(0) for pat in _INJECTION_PATTERNS if (m := pat.search(text))]


def to_record(text: str, pdf_path: str | Path, source_url: str = "") -> dict:
    meta = parse_meta(text)
    today = dt.date.today().isoformat()
    flags = injection_scan(text)
    return {
        "circular_number": meta["circular_number"],
        "issue_date": meta["issue_date"],
        "effective_date": meta.get("effective_date", ""),
        "subject": meta["subject"],
        "issuing_department": meta["issuing_department"],
        "supersession_status": "in_force",
        "amendment_history": [],
        "version_lineage": meta["version_lineage"],
        "source_url": source_url,
        "provenance": f"Parsed from PDF {Path(pdf_path).name} on {today}",
        "excerpt": False,
        "injection_flags": flags,  # F4: non-empty => review before trusting
        "text": text,
    }


def _existing_numbers(corpus_path: Path) -> set[str]:
    if not corpus_path.exists():
        return set()
    nums = set()
    for line in corpus_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            nums.add(json.loads(line).get("circular_number", ""))
    return nums


def _rewrite_replacing(corpus_path: Path, rec: dict) -> None:
    lines = corpus_path.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if json.loads(line).get("circular_number") == rec["circular_number"]:
            continue
        out.append(line)
    out.append(json.dumps(rec, ensure_ascii=False))
    corpus_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def ingest(
    pdf_path: str | Path,
    corpus_path: str | Path,
    source_url: str = "",
    replace: bool = False,
    ocr: bool = False,
) -> dict:
    corpus_path = Path(corpus_path)
    rec = to_record(extract_text(pdf_path, ocr=ocr), pdf_path, source_url)
    if not rec["circular_number"]:
        raise ValueError(f"No SEBI circular number found in {pdf_path}")
    if rec["injection_flags"]:
        print(f"WARNING: instruction-like content in {pdf_path}: "
              f"{rec['injection_flags']} (recorded in injection_flags)")
    corpus_path.parent.mkdir(parents=True, exist_ok=True)
    if rec["circular_number"] in _existing_numbers(corpus_path):
        if not replace:
            return {**rec, "_skipped": "duplicate"}
        _rewrite_replacing(corpus_path, rec)
        return {**rec, "_replaced": True}
    with corpus_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ingest a SEBI circular PDF.")
    ap.add_argument("pdf")
    ap.add_argument("--corpus", default="data/corpus/circulars.jsonl")
    ap.add_argument("--source-url", default="")
    ap.add_argument("--replace", action="store_true", help="overwrite existing record")
    ap.add_argument("--ocr", action="store_true", help="OCR fallback for scanned PDFs")
    args = ap.parse_args(argv)
    rec = ingest(args.pdf, args.corpus, args.source_url, replace=args.replace, ocr=args.ocr)
    status = rec.get("_skipped") or ("replaced" if rec.get("_replaced") else "ingested")
    print(f"{status}: {rec['circular_number']} ({rec['issue_date']}) -> {args.corpus}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
