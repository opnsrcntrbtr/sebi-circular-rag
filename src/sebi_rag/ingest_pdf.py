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


def normalize_circular_number(n: str) -> str:
    """Canonical COMPARISON key for a circular number: strip whitespace and
    trailing punctuation, drop the optional leading 'SEBI/', casefold.
    Never store this form — stored numbers keep the document's own spelling
    (chunk IDs and lineage keys must stay stable)."""
    n = re.sub(r"\s+", "", n).strip(".,;:")
    if n.upper().startswith("SEBI/"):
        n = n[len("SEBI/"):]
    return n.casefold()

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


# Single source of truth for the 2026 departmental-order grammar: reuse
# _NEW_FMT2 (optional SEBI/ prefix) instead of restating it inline.
DEPT_ORDER_RE = re.compile(_NEW_FMT2)
PREFIXED_DEPT_ORDER_RE = re.compile(
    r"SEBI/HO/[A-Za-z0-9_()\-]+/\(\d+\)\d{4}-[A-Za-z0-9_()\-]+")
YEAR_FIRST_RE = re.compile(r"\d{4}/[A-Za-z0-9_()\-/]+?/\d+")


def _rejoin_split(header: str) -> str:
    """Rejoin numbers split by a space after a slash, e.g. "CIR/ 2025/104" or
    "HO/ (79)2026-MRD" (PDF layout inserts a space mid-number)."""
    return re.sub(r"/\s+(?=[A-Za-z0-9(])", "/", header)


def _s_header_token(header: str) -> str:
    """Standard formats (old CIR, new SEBI/HO, free-form 2026): first
    slash-heavy HO/CIR-prefixed header token."""
    for tok in header.split():
        t = tok.strip(".,;:")
        if HEADER_TOKEN_RE.match(t) and t.count("/") >= 3 and re.search(r"\d", t):
            return t
    return ""


def _s_dept_only(header: str) -> str:
    """Department-only prefixes without HO/CIR anchor,
    e.g. AFD/P/CIR/2022/125."""
    for tok in header.split():
        t = tok.strip(".,;:")
        if t.count("/") >= 4 and "CIR" in t:
            return t
    return ""


def _s_anchor_merge(header: str) -> str:
    """References split across tokens: merge up to 4 tokens after the first
    HO/CIR/year anchor, then look for a well-formed or year-first reference."""
    parts = header.split()
    for i, tok in enumerate(parts):
        t = tok.strip(".,;:")
        if HEADER_TOKEN_RE.match(t) or re.match(r"^\d{4}/", t):
            merged = _rejoin_split(" ".join(parts[i:i + 4]))
            m = REF_RE.search(merged) or YEAR_FIRST_RE.search(merged)
            return m.group(0) if m else ""
    return ""


def _s_dept_order(header: str) -> str:
    """2026 departmental orders, bare or SEBI/HO-prefixed — no /CIR/ and
    possibly the only token on the line."""
    m = DEPT_ORDER_RE.search(header) or PREFIXED_DEPT_ORDER_RE.search(header)
    return m.group(0) if m else ""


_PRIMARY_STRATEGIES = (_s_header_token, _s_dept_only, _s_anchor_merge, _s_dept_order)


def _primary_number(header: str, full: str) -> str:
    header = _rejoin_split(header)
    for strategy in _PRIMARY_STRATEGIES:
        n = strategy(header)
        if n:
            return n
    # Last resort (risk R3, plan 2026-07-08 B.4): earliest well-formed
    # reference anywhere in the text — may be a CITED circular, not the
    # document's own number. Output is checked by scripts/validate_corpus.py.
    m = REF_RE.search(full)
    return m.group(0) if m else ""


def _labeled_date(header: str, label_re: re.Pattern) -> str:
    m = label_re.search(header)
    return _iso_date(m.group(1)) if m else ""


def parse_meta(text: str) -> dict:
    header = _header(text)
    primary = _primary_number(header, text)
    # lineage = well-formed references in the body, minus the primary
    # (compared under normalization so a SEBI/-prefixed spelling of the
    # document's own number can't leak in as a self-reference)
    lineage = []
    primary_key = normalize_circular_number(primary) if primary else ""
    for m in REF_RE.finditer(text):
        n = m.group(0)
        if normalize_circular_number(n) != primary_key and n not in lineage:
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
            nums.add(normalize_circular_number(
                json.loads(line).get("circular_number", "")))
    return nums


def _rewrite_replacing(corpus_path: Path, rec: dict) -> None:
    lines = corpus_path.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if (normalize_circular_number(json.loads(line).get("circular_number", ""))
                == normalize_circular_number(rec["circular_number"])):
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
    if normalize_circular_number(rec["circular_number"]) in _existing_numbers(corpus_path):
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
