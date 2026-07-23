"""Polite SEBI regulations scraper -> data/corpus/regulations.jsonl (RUN LOCALLY).

Legality: same posture as scripts/scrape_sebi.py — SEBI robots.txt allows
/legal and /sebi_data/attachdocs; /js and /css are disallowed and are never
fetched. Self-imposed rate limit, descriptive User-Agent, checksum dedupe,
official source_url recorded.

Section sid=1 ssid=3 is "List of All SEBI Regulations (Updated)": 42 in-force
regulations on a SINGLE page with no pagination, so the doDirect POST machinery
in scrape_sebi.py is not used here. Detail pages embed the PDF through the same
`web/?file=` viewer iframe, so extract_pdf_urls() is reused unchanged.

Repealed regulations sit behind a `showHistory()` control defined in external
JS under /js, which robots.txt disallows. They are therefore NOT scraped;
reg_lineage.synthesise_repealed_stubs() derives them from corpus citations.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/scrape_regulations.py --rate 3
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from scrape_sebi import extract_pdf_urls, fetch, looks_like_pdf  # noqa: E402
from sebi_rag.regulations import RegulationMeta, reg_id  # noqa: E402

BASE = "https://www.sebi.gov.in"
LISTING_URL = (f"{BASE}/sebiweb/home/HomeAction.do"
               "?doListing=yes&sid=1&ssid=3&smid=0")

# <tr><td>2026</td><td><a href="...">Title [Last amended on ...]</a></td></tr>
ROW_RE = re.compile(
    r"<tr>\s*<td>\s*(\d{4})\s*</td>\s*<td>\s*"
    r"<a\s+href=\"(https://www\.sebi\.gov\.in/legal/regulations/[^\"]+)\""
    r"[^>]*>(.*?)</a>", re.S | re.I)

# Amendment phrases seen verbatim in the live listing, including SEBI's own
# typos: "on on", a repeated "Last amended on", "Last amendment on", lowercase,
# and "amended as on". A trailing duplicate prefix is absorbed by allowing the
# preamble to repeat.
LAST_AMENDED_RE = re.compile(
    r"(?:last\s+amend(?:ed|ment)|amended\s+as)\s+on\s+"
    r"(?:(?:last\s+amend(?:ed|ment)\s+)?on\s+)?"
    r"([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})", re.I)

# The short name is the LAST bracketed group immediately preceding
# "Regulations". Three real forms occur in the listing and all must work:
#   SEBI (Mutual Funds) Regulations, 2026
#   Securities Contracts (Regulation) (Stock Exchanges and Clearing
#       Corporations) Regulations, 2018   <- no SEBI prefix, two groups
#   SEBI {KYC (Know Your Client) Registration Agency} Regulations, 2011
#       <- curly braces, nested parens
# A prefix-anchored regex cannot express this, so match the closer and walk
# back to its partner counting depth.
CLOSER_BEFORE_REGS = re.compile(r"[)}]\s*Regulations?\b", re.I)
_PARTNER = {")": "(", "}": "{"}


def _text(html_fragment: str) -> str:
    s = re.sub(r"<[^>]+>", " ", html_fragment)
    s = (s.replace("&amp;", "&").replace("&nbsp;", " ")
          .replace("&#39;", "'").replace("&quot;", '"'))
    return re.sub(r"\s+", " ", s).strip()


def parse_last_amended(title: str) -> str | None:
    """ISO date of the last amendment, or None when the title carries none."""
    m = LAST_AMENDED_RE.search(title)
    if not m:
        return None
    try:
        d = dt.datetime.strptime(
            f"{m.group(1)[:3]} {int(m.group(2))}, {m.group(3)}", "%b %d, %Y").date()
    except ValueError:
        return None
    return d.isoformat()


def short_name_of(title: str) -> str | None:
    """The bracketed short name, e.g. 'Mutual Funds'.

    Takes the LAST bracket group before 'Regulations' and walks back to its
    partner counting depth, so nested groups survive: the real entry
    '(Procedure for making, amending and reviewing of Regulations) Regulations,
    2025' keeps its inner word, and '{KYC (Know Your Client) Registration
    Agency}' is not truncated at the inner ')'.
    """
    last = None
    for m in CLOSER_BEFORE_REGS.finditer(title):
        last = m
    if last is None:
        return None
    close = last.start()
    closer = title[close]
    opener = _PARTNER[closer]
    depth = 0
    for i in range(close, -1, -1):
        if title[i] == closer:
            depth += 1
        elif title[i] == opener:
            depth -= 1
            if depth == 0:
                return re.sub(r"\s+", " ", title[i + 1:close]).strip() or None
    return None


def parse_listing(html: str) -> list[dict]:
    """(year, url, title, short_name, last_amended) per listing row, in order."""
    rows, seen = [], set()
    for year, url, raw_title in ROW_RE.findall(html):
        if url in seen:
            continue
        seen.add(url)
        title = _text(raw_title)
        rows.append({
            "year": int(year),
            "url": url,
            "title": title,
            "short_name": short_name_of(title) or "",
            "last_amended": parse_last_amended(title),
        })
    return rows


def _record(row: dict, pdf_url: str | None, pdf_path: str | None,
            sha: str | None, fetched: str) -> dict:
    meta = RegulationMeta(
        reg_id=reg_id(row["short_name"], row["year"]),
        title=row["title"],
        short_name=row["short_name"],
        year=row["year"],
        status="in_force",
        last_amended=row["last_amended"],
        source_url=row["url"],
        pdf_url=pdf_url,
        pdf_sha256=sha,
        pdf_path=pdf_path,
        provenance=f"SEBI Updated List, fetched {fetched}",
    )
    return asdict(meta)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rate", type=float, default=3.0)
    ap.add_argument("--out", default="data/corpus/regulations.jsonl")
    ap.add_argument("--raw", default="data/raw/regulations")
    ap.add_argument("--skip-pdfs", action="store_true",
                    help="identity only; do not download regulation PDFs")
    args = ap.parse_args(argv)

    raw_dir = Path(args.raw)
    raw_dir.mkdir(parents=True, exist_ok=True)
    fetched = dt.date.today().isoformat()

    print(f"Fetching listing (rate {args.rate}s)...", flush=True)
    rows = parse_listing(fetch(LISTING_URL, args.rate).decode("utf-8", "ignore"))
    if not rows:
        # Never truncate a good corpus file with an empty fetch.
        print("ERROR: listing returned 0 rows; leaving existing file untouched",
              flush=True)
        return 1
    print(f"Found {len(rows)} regulations.", flush=True)

    records, no_pdf = [], 0
    for i, row in enumerate(rows, 1):
        pdf_url = pdf_path = sha = None
        if not args.skip_pdfs:
            try:
                html = fetch(row["url"], args.rate).decode("utf-8", "ignore")
                urls = extract_pdf_urls(html, row["url"])
                if urls:
                    data = fetch(urls[0], args.rate)
                    if looks_like_pdf(data):
                        pdf_url = urls[0]
                        sha = hashlib.sha256(data).hexdigest()
                        dest = raw_dir / pdf_url.rsplit("/", 1)[-1]
                        dest.write_bytes(data)
                        pdf_path = str(dest)
                    else:
                        print(f"[{i}] not a PDF payload: {urls[0]}", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"[{i}] PDF fetch failed ({e}); keeping identity only",
                      flush=True)
        if pdf_url is None:
            no_pdf += 1
        records.append(_record(row, pdf_url, pdf_path, sha, fetched))
        print(f"[{i}/{len(rows)}] {records[-1]['reg_id']}", flush=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nWrote {len(records)} regulations to {out} "
          f"({no_pdf} without a PDF).", flush=True)
    print("Next: make reg-edges", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
