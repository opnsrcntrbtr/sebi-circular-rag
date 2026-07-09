"""Polite SEBI circular scraper -> data/raw -> corpus (RUN ON YOUR MACHINE).

Legality: SEBI robots.txt allows /legal/circulars and /sebi_data/attachdocs (only
/js, /css are disallowed). Self-imposed rate limit, descriptive User-Agent, backoff,
checksum dedupe, official source_url recorded. Never bypasses logins/captchas.
Review SEBI Terms of Use before bulk use. See docs/scraping_plan.md.

URL structure (since SEBI's 2026 site modernisation): detail pages remain at
/legal/circulars/<mon-yyyy>/<slug>_<id>.html; PDFs moved into month-year folders
/sebi_data/attachdocs/<mon-yyyy>/<stem>.pdf and are embedded via a viewer iframe
(src='../../../web/?file=<pdf-url>'). Flat attachdocs paths 404. extract_pdf_urls()
resolves the current URL from the detail page — never predict static PDF names.

Sections (sid=1 Legal): ssid=7 Circulars (~2.8k), ssid=6 Master Circulars (~135).

Usage:
    PYTHONPATH=src .venv/bin/python scripts/scrape_sebi.py \
        --section circulars --from 2025-01-01 --to 2026-06-30 --max 50 --rate 3

Pagination is a POST (searchFormNewsList('n', idx)); param names are best-effort and
guarded: if a page does not advance, discovery stops and logs it (verify in the
browser network tab and adjust _page_body if you need >1 page).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import http.cookiejar
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sebi_rag.ingest_pdf import ingest  # noqa: E402

UA = "SEBI-RAG-research/0.2 (local research; contact: ianpinto1980@gmail.com)"
BASE = "https://www.sebi.gov.in"
SECTIONS = {"circulars": (1, 7, 0), "master-circulars": (1, 6, 0)}
CIRCULAR_HREF = re.compile(
    r'https://www\.sebi\.gov\.in/legal/(?:circulars|master-circulars)/[^"\'\s>]+\.html')
PDF_HREF = re.compile(
    r'https://www\.sebi\.gov\.in/sebi_data/attachdocs/[^"\'\s>]+\.pdf', re.I)
ROW_PAIR = re.compile(
    r'([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})'                      # date cell
    r'.*?(https://www\.sebi\.gov\.in/legal/(?:circulars|master-circulars)/'
    r'[^"\'\s>]+\.html)', re.S)                                # nearest circular href

# 2026 migration: detail pages embed the PDF via a viewer iframe
# (src='../../../web/?file=<pdf-url>'); PDFs live under
# /sebi_data/attachdocs/<mon-yyyy>/<stem>.pdf (flat legacy paths 404).
SRC_ATTR = re.compile(
    r"<(?:iframe|embed|object)[^>]*?\bsrc\s*=\s*"
    r"(?:\"([^\"]+)\"|'([^']+)'|([^\s>]+))", re.I | re.S)
HREF_PDF = re.compile(
    r"<a[^>]*?\bhref\s*=\s*"
    r"(?:\"([^\"]+\.pdf)\"|'([^']+\.pdf)'|([^\s>]+\.pdf))", re.I | re.S)
VIEWER_FILE = re.compile(r"[?&]file=([^&\"'\s>]+)", re.I)


def _parse_date(s: str) -> dt.date | None:
    m = re.match(r"([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})", s)
    if not m:
        return None
    try:
        return dt.datetime.strptime(
            f"{m.group(1)[:3]} {int(m.group(2))}, {m.group(3)}", "%b %d, %Y").date()
    except ValueError:
        return None


def parse_rows(html: str) -> list[tuple[dt.date | None, str]]:
    """Extract (date, circular_url) pairs from a listing page, in page order."""
    out, seen = [], set()
    for ds, url in ROW_PAIR.findall(html):
        if url in seen:
            continue
        seen.add(url)
        out.append((_parse_date(ds), url))
    return out


# Shared opener with a cookie jar so the session cookie from the page-0 GET is
# carried into the pagination POST (SEBI's WAF 530-blocks cookie-less POSTs).
_OPENER = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def fetch(url: str, rate: float, data: bytes | None = None,
          headers: dict | None = None, tries: int = 4) -> bytes:
    h = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*"}
    if headers:
        h.update(headers)
    delay = rate
    for attempt in range(tries):
        try:
            with _OPENER.open(urllib.request.Request(url, data=data, headers=h),
                              timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            if attempt == tries - 1:
                raise
            print(f"  retry ({e}) backoff {delay:.0f}s", flush=True)
            time.sleep(delay)
            delay *= 2
    return b""


# Pagination mechanism (confirmed via the page's searchFormNewsList JS): a POST to
# the AJAX endpoint below with doDirect=<0-based page index>. Page 0 uses the GET
# listing (also establishes the JSESSIONID cookie the POST needs).
AJAX = BASE + "/sebiweb/ajax/home/getnewslistinfo.jsp"


def _listing_url(sid: int, ssid: int, smid: int) -> str:
    return f"{BASE}/sebiweb/home/HomeAction.do?doListing=yes&sid={sid}&ssid={ssid}&smid={smid}"


def _page(sid: int, ssid: int, smid: int, page: int, rate: float) -> bytes:
    listing = _listing_url(sid, ssid, smid)
    if page == 0:
        return fetch(listing, rate)  # GET: page 0 + session cookie
    body = urllib.parse.urlencode({
        "nextValue": page, "next": "n", "search": "",
        "fromDate": "", "toDate": "", "fromYear": "", "toYear": "", "deptId": "",
        "sid": sid, "ssid": ssid, "smid": smid, "ssidhidden": ssid, "intmid": -1,
        "sText": "", "ssText": "", "smText": "", "doDirect": page,
    }).encode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": listing,
    }
    return fetch(AJAX, rate, data=body, headers=headers)


def discover(section: str, max_count: int, rate: float,
             date_from: dt.date | None = None, date_to: dt.date | None = None,
             max_pages: int = 130) -> list[str]:
    sid, ssid, smid = SECTIONS[section]
    out, seen, prev_first = [], set(), None
    for page in range(max_pages):
        try:
            raw = _page(sid, ssid, smid, page, rate)
        except Exception as e:  # noqa: BLE001  (e.g. 530 BLOCKED on POST pagination)
            print(f"  page {page} fetch failed ({e}); stopping with {len(out)} found "
                  "(SEBI may block programmatic pagination — see docs)", flush=True)
            break
        rows = parse_rows(raw.decode("utf-8", "ignore"))
        if not rows:
            break
        if page > 0 and rows[0][1] == prev_first:
            print(f"  pagination did not advance at page {page}; stopping "
                  "(verify POST params in _page())", flush=True)
            break
        prev_first = rows[0][1]
        for d, url in rows:
            if date_from and d and d < date_from:
                continue
            if date_to and d and d > date_to:
                continue
            if url not in seen:
                seen.add(url)
                out.append(url)
                if len(out) >= max_count:
                    return out
        if date_from and rows[-1][0] and rows[-1][0] < date_from:
            break  # reverse-chronological: past the window
        time.sleep(rate)
    return out


def extract_pdf_urls(html: str, base_url: str) -> list[str]:
    """All SEBI-hosted PDF URLs on a detail page, in page order, deduped.

    Handles the web/?file=<target> viewer wrapper (absolute, relative, or
    URL-encoded targets), direct .pdf anchors, and falls back to the legacy
    absolute-URL regex. Same-origin only (www.sebi.gov.in).
    """
    found: list[str] = []

    def add(candidate: str) -> None:
        url = urllib.parse.urljoin(base_url, candidate.strip())
        if (url.lower().endswith(".pdf")
                and urllib.parse.urlsplit(url).netloc == "www.sebi.gov.in"
                and url not in found):
            found.append(url)

    for m in SRC_ATTR.finditer(html):
        src = m.group(1) or m.group(2) or m.group(3) or ""
        fm = VIEWER_FILE.search(src)
        add(urllib.parse.unquote(fm.group(1)) if fm else src)
    for m in HREF_PDF.finditer(html):
        add(m.group(1) or m.group(2) or m.group(3) or "")
    for m in PDF_HREF.finditer(html):
        add(m.group(0))
    return found


def looks_like_pdf(data: bytes) -> bool:
    """Reject HTML error pages served with a .pdf URL (e.g. WAF/404 bodies)."""
    return data.startswith(b"%PDF")


def pdf_url_for(detail_url: str, rate: float) -> str | None:
    urls = extract_pdf_urls(fetch(detail_url, rate).decode("utf-8", "ignore"),
                            detail_url)
    if len(urls) > 1:
        print(f"  note: {len(urls) - 1} additional attachment(s) not ingested "
              f"(one record per circular): {urls[1:]}", flush=True)
    return urls[0] if urls else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--section", choices=list(SECTIONS), default="circulars")
    ap.add_argument("--from", dest="date_from", default=None, help="YYYY-MM-DD")
    ap.add_argument("--to", dest="date_to", default=None, help="YYYY-MM-DD")
    ap.add_argument("--max", type=int, default=25)
    ap.add_argument("--rate", type=float, default=3.0)
    ap.add_argument("--out", default="data/raw")
    ap.add_argument("--corpus", default="data/corpus/circulars.jsonl")
    ap.add_argument("--ocr", action="store_true", help="OCR fallback for scanned PDFs")
    args = ap.parse_args(argv)
    df = dt.date.fromisoformat(args.date_from) if args.date_from else None
    dtto = dt.date.fromisoformat(args.date_to) if args.date_to else None

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    seen_sha = {p.read_text().strip() for p in out_dir.glob("*.sha256")}

    print(f"Discovering up to {args.max} {args.section} (rate {args.rate}s)...", flush=True)
    details = discover(args.section, args.max, args.rate, df, dtto)
    print(f"Found {len(details)} circular pages.", flush=True)

    ingested = skipped = failed = 0
    for i, detail in enumerate(details, 1):
        time.sleep(args.rate)
        try:
            pdf_url = pdf_url_for(detail, args.rate)
            if not pdf_url:
                print(f"[{i}] no PDF link: {detail}", flush=True)
                failed += 1
                continue
            time.sleep(args.rate)
            data = fetch(pdf_url, args.rate)
            if not looks_like_pdf(data):
                print(f"[{i}] not a PDF payload: {pdf_url}", flush=True)
                failed += 1
                continue
            sha = hashlib.sha256(data).hexdigest()
            if sha in seen_sha:
                skipped += 1
                continue
            name = pdf_url.rsplit("/", 1)[-1]
            pdf_path = out_dir / name
            pdf_path.write_bytes(data)
            (out_dir / (Path(name).stem + ".sha256")).write_text(sha)
            seen_sha.add(sha)
            rec = ingest(pdf_path, args.corpus, source_url=detail, ocr=args.ocr)
            status = rec.get("_skipped") or "ingested"
            print(f"[{i}] {status}: {rec['circular_number']} ({rec['issue_date']})", flush=True)
            ingested += status == "ingested"
        except Exception as e:  # noqa: BLE001
            print(f"[{i}] FAILED {detail}: {e}", flush=True)
            failed += 1

    print(f"\nDone. ingested={ingested} skipped={skipped} failed={failed}", flush=True)
    print("Next: make reindex (annotate lineage + rebuild index), then make calibrate", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
