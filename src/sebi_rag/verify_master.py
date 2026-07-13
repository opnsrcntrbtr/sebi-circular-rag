"""Master-circular coverage verification (spec 2026-07-13).

Pure functions only: listing-HTML parsing, manifest<->corpus diff, summary
statistics and markdown rendering. Network lives in scripts/verify_master.py.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

# Same tolerant style as scripts/scrape_sebi.py ROW_PAIR, plus anchor text.
_ROW = re.compile(
    r'([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})'                     # date cell
    r'.*?<a[^>]*?href\s*=\s*["\']?'
    r'(https://www\.sebi\.gov\.in/legal/master-circulars/[^"\'\s>]+\.html)'
    r'["\']?[^>]*>(.*?)</a>', re.S)
_TAGS = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")


def _iso(date_str: str) -> str | None:
    m = re.match(r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})", date_str)
    if not m:
        return None
    try:
        return dt.datetime.strptime(
            f"{m.group(1)[:3]} {int(m.group(2))}, {m.group(3)}",
            "%b %d, %Y").date().isoformat()
    except ValueError:
        return None


def parse_listing(html: str) -> list[dict]:
    """(listing_date, detail_url, title) rows from one listing page, deduped."""
    rows, seen = [], set()
    for ds, url, anchor in _ROW.findall(html):
        if url in seen:
            continue
        seen.add(url)
        title = _WS.sub(" ", _TAGS.sub("", anchor)).strip()
        rows.append({"listing_date": _iso(ds), "detail_url": url, "title": title})
    return rows
