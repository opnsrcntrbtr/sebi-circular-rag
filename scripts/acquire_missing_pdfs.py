"""Recover the 14 circular PDFs missed in the 2026-07-08 audit by resolving
their detail pages (plan Task 11, unblocked 2026-07-09).

SEBI's 2026 site modernisation moved PDFs from flat /sebi_data/attachdocs/
{stem}.pdf into month-year subfolders behind a web/?file= viewer iframe;
numeric stems are preserved but flat URLs 404 and blind month reconstruction
is unreliable. Each stem is therefore resolved by sweeping the circular
listings over its month window (±1 month) and extracting the current PDF URL
from the detail page. Polite (3 s rate via scrape_sebi.fetch), idempotent
(skips stems already in data/raw/; ingest() dedups). See
docs/superpowers/specs/2026-07-09-sebi-semantic-routing-alignment-design.md.
"""
import datetime as dt
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from scrape_sebi import discover, extract_pdf_urls, fetch, looks_like_pdf  # noqa: E402
from sebi_rag.ingest_pdf import ingest                                     # noqa: E402

MISSING_STEMS = [
    "1705319176210", "1706306045806", "1708533481758", "1709691276891",
    "1709783974409", "1710751501256", "1711441070499", "1711642358729",
    "1711994539797", "1713433746620", "1714509677753", "1714919308556",
    "1724114634944", "1737774327832",
]
RAW = ROOT / "data/raw"
CORPUS = ROOT / "data/corpus/circulars.jsonl"
RATE = 3.0  # seconds between requests
SECTIONS = ("circulars", "master-circulars")


def _add_months(d: dt.date, n: int) -> dt.date:
    m = d.month - 1 + n
    return dt.date(d.year + m // 12, m % 12 + 1, 1)


def month_window(stem: str, pad: int = 1) -> tuple[dt.date, dt.date]:
    """[first day of month-pad, last day of month+pad] around the stem's epoch."""
    d = dt.datetime.fromtimestamp(int(stem) / 1000, tz=dt.timezone.utc).date()
    return _add_months(d, -pad), _add_months(d, pad + 1) - dt.timedelta(days=1)


def stem_of(pdf_url: str) -> str:
    return pdf_url.rsplit("/", 1)[-1].removesuffix(".pdf")


def resolve_stems(stems: list[str], rate: float = RATE,
                  discover_fn=discover, fetch_fn=fetch) -> dict[str, tuple[str, str]]:
    """Map each stem to (current pdf_url, detail_url) via listing sweeps."""
    todo = set(stems)
    resolved: dict[str, tuple[str, str]] = {}
    seen_pages: set[str] = set()
    for start, end in sorted({month_window(s) for s in stems}):
        for section in SECTIONS:
            if not todo:
                return resolved
            for detail in discover_fn(section, 500, rate,
                                      date_from=start, date_to=end):
                if detail in seen_pages:
                    continue
                seen_pages.add(detail)
                try:
                    html = fetch_fn(detail, rate).decode("utf-8", "ignore")
                except Exception as e:  # noqa: BLE001
                    print(f"  skip {detail}: {e}", flush=True)
                    continue
                for url in extract_pdf_urls(html, detail):
                    s = stem_of(url)
                    if s in todo:
                        resolved[s] = (url, detail)
                        todo.discard(s)
                if not todo:
                    return resolved
    return resolved


def check_robots(rate: float = RATE) -> None:
    """Log-only re-verification that our paths are still crawlable."""
    try:
        txt = fetch("https://www.sebi.gov.in/robots.txt", rate).decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        print(f"robots.txt check skipped ({e})", flush=True)
        return
    for line in txt.splitlines():
        rule = line.strip().lower()
        if not rule.startswith("disallow:"):
            continue
        path = rule.split(":", 1)[1].strip()
        for ours in ("/legal", "/sebi_data/attachdocs"):
            if path and ours.startswith(path.rstrip("*")):
                print(f"WARNING: robots.txt now disallows '{path}' covering {ours}; "
                      "stop and review before continuing", flush=True)


def main() -> int:
    check_robots()
    ok = failed = 0
    todo = [s for s in MISSING_STEMS if not (RAW / f"{s}.pdf").exists()]
    resolved = resolve_stems(todo) if todo else {}
    for stem in MISSING_STEMS:
        dest = RAW / f"{stem}.pdf"
        if stem in resolved:
            pdf_url, source = resolved[stem]
            try:
                data = fetch(pdf_url, RATE)
                if not looks_like_pdf(data):
                    raise ValueError(f"non-PDF payload from {pdf_url}")
                dest.write_bytes(data)
                (RAW / f"{stem}.sha256").write_text(hashlib.sha256(data).hexdigest())
            except Exception as e:  # noqa: BLE001
                print(f"FAIL download {stem}: {e}", flush=True)
                failed += 1
                continue
        elif dest.exists():
            # already downloaded on a previous run; re-ingest is a dedup no-op
            source = f"https://www.sebi.gov.in/sebi_data/attachdocs/{stem}.pdf"
        else:
            print(f"UNRESOLVED {stem}: no detail page in month window "
                  "(possibly withdrawn — document in plan)", flush=True)
            failed += 1
            continue
        try:
            rec = ingest(dest, CORPUS, source_url=source)
            status = rec.get("_skipped") or ("replaced" if rec.get("_replaced") else "ingested")
            print(f"{status}: {stem} -> {rec['circular_number']}", flush=True)
            ok += 1
        except Exception as e:  # noqa: BLE001
            print(f"FAIL ingest {stem}: {e}", flush=True)
            failed += 1
    print(f"resolved={len(resolved)} ok={ok} failed={failed} of {len(MISSING_STEMS)}",
          flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
