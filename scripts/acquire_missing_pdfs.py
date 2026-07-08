"""Download the 14 circular PDFs identified as missing in the 2026-07-08
audit (never downloaded; blocked corpus completion of the '19 unparseable'
issue), then ingest each into the corpus.

Polite: reuses scrape_sebi.fetch (rate-limited). Idempotent: skips stems
already present in data/raw/ and relies on ingest()'s dedup.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from scrape_sebi import fetch            # noqa: E402
from sebi_rag.ingest_pdf import ingest   # noqa: E402

MISSING_STEMS = [
    "1705319176210", "1706306045806", "1708533481758", "1709691276891",
    "1709783974409", "1710751501256", "1711441070499", "1711642358729",
    "1711994539797", "1713433746620", "1714509677753", "1714919308556",
    "1724114634944", "1737774327832",
]
RAW = ROOT / "data/raw"
CORPUS = ROOT / "data/corpus/circulars.jsonl"
RATE = 3.0  # seconds between requests


def main() -> int:
    ok = failed = skipped = 0
    for stem in MISSING_STEMS:
        dest = RAW / f"{stem}.pdf"
        url = f"https://www.sebi.gov.in/sebi_data/attachdocs/{stem}.pdf"
        if not dest.exists():
            try:
                dest.write_bytes(fetch(url, RATE))
            except Exception as e:
                print(f"FAIL download {stem}: {e}")
                failed += 1
                continue
        try:
            rec = ingest(dest, CORPUS, source_url=url)
            status = rec.get("_skipped") or ("replaced" if rec.get("_replaced") else "ingested")
            print(f"{status}: {stem} -> {rec['circular_number']}")
            skipped += status == "duplicate"
            ok += status != "duplicate"
        except Exception as e:
            print(f"FAIL ingest {stem}: {e}")
            failed += 1
    print(f"ok={ok} duplicate={skipped} failed={failed} of {len(MISSING_STEMS)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
