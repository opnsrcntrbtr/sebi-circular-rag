# SEBI Semantic-Routing Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make PDF-URL extraction viewer-structure-aware in the SEBI scraper and recover the 14 missing circular PDFs by resolving their detail pages, unblocking Task 11 of the 2026-07-08 enhancement plan.

**Architecture:** A new pure function `extract_pdf_urls(html, base_url)` in `scripts/scrape_sebi.py` parses iframe/embed/object viewer wrappers (`web/?file=<target>`), direct `.pdf` anchors, and falls back to the legacy absolute-URL regex; `pdf_url_for()` becomes a thin wrapper. `scripts/acquire_missing_pdfs.py` is rewritten to sweep circular listings over each missing stem's month window (±1 month), match stems from extracted PDF URLs, and download+ingest with detail-page provenance.

**Tech Stack:** Python 3.12–3.13, stdlib only for scraping (`urllib`, `re`, `datetime`); pytest offline tests with `monkeypatch` (existing house style in `tests/test_scrape_sebi.py`).

**Spec:** `docs/superpowers/specs/2026-07-09-sebi-semantic-routing-alignment-design.md` (approved 2026-07-09).

## Global Constraints

- Python 3.12–3.13, run via the project venv: `.venv/bin/python` (created by `uv sync`).
- Scraper scripts use **stdlib only** — no BeautifulSoup/requests.
- All new tests are **offline** (no network); network I/O is stubbed with `monkeypatch` / injectable callables.
- Politeness: every live request path reuses `scrape_sebi.fetch()` with rate ≥ 3.0 s; never bypass it.
- Same-origin guard: extracted PDF URLs must be on host `www.sebi.gov.in` exactly.
- Test suite invocation: `make test` (full offline suite) or `.venv/bin/python -m pytest <file> -v` for a single file.
- Work on feature branch `semantic-routing-alignment`; merge to `main` only after the full suite is green.
- Live network steps (Task 5) run only from this machine, sequentially, never parallelized.

---

### Task 1: `extract_pdf_urls()` — viewer-aware PDF URL extraction

**Files:**
- Modify: `scripts/scrape_sebi.py` (add regexes + `extract_pdf_urls`; replace `pdf_url_for` body at lines 159–161)
- Test: `tests/test_scrape_sebi.py` (append)

**Interfaces:**
- Consumes: existing module globals `PDF_HREF`, `fetch(url: str, rate: float, ...) -> bytes` in `scripts/scrape_sebi.py`.
- Produces: `extract_pdf_urls(html: str, base_url: str) -> list[str]` (ordered, deduped, absolute, same-origin URLs; first = primary document) and unchanged signature `pdf_url_for(detail_url: str, rate: float) -> str | None` (returns first extracted URL or `None`). Task 3 imports `extract_pdf_urls`.

- [ ] **Step 1: Create the feature branch**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
git checkout -b semantic-routing-alignment main
```

- [ ] **Step 2: Write the failing tests**

Append to `tests/test_scrape_sebi.py`:

```python
# --- extract_pdf_urls (viewer-aware PDF extraction, 2026 SEBI migration) ---

DETAIL = "https://www.sebi.gov.in/legal/circulars/jul-2026/some-slug_102639.html"
PDF_NEW = "https://www.sebi.gov.in/sebi_data/attachdocs/jul-2026/1783423471963.pdf"
PDF_ANNEX = "https://www.sebi.gov.in/sebi_data/attachdocs/jul-2026/222.pdf"
IFRAME_LIVE = ("<iframe src='../../../web/?file=" + PDF_NEW +
               "' width='100%' style='height:600px;' title=\"t\" allowfullscreen>")


def test_extract_viewer_absolute_target():
    # Live shape as of 2026-07-09: absolute URL inside single-quoted iframe src
    assert S.extract_pdf_urls(IFRAME_LIVE, DETAIL) == [PDF_NEW]


def test_extract_viewer_relative_target():
    html = "<iframe src='../../../web/?file=/sebi_data/attachdocs/jul-2026/1783423471963.pdf'>"
    assert S.extract_pdf_urls(html, DETAIL) == [PDF_NEW]


def test_extract_viewer_urlencoded_target():
    html = ("<iframe src='../../../web/?file=https%3A%2F%2Fwww.sebi.gov.in%2Fsebi_data"
            "%2Fattachdocs%2Fjul-2026%2F1783423471963.pdf'>")
    assert S.extract_pdf_urls(html, DETAIL) == [PDF_NEW]


def test_extract_anchor_absolute_and_relative():
    html = (f'<a href="{PDF_NEW}">pdf</a> '
            '<a href="/sebi_data/attachdocs/jul-2026/222.pdf">annex</a>')
    assert S.extract_pdf_urls(html, DETAIL) == [PDF_NEW, PDF_ANNEX]


def test_extract_multi_pdf_order_and_dedupe():
    html = IFRAME_LIVE + f'<a href="{PDF_ANNEX}">a</a><a href="{PDF_NEW}">dup</a>'
    assert S.extract_pdf_urls(html, DETAIL) == [PDF_NEW, PDF_ANNEX]


def test_extract_fallback_regex_scan():
    # URL appears only in a script block, not in any src/href attribute
    html = f'<script>var u = "{PDF_NEW}";</script>'
    assert S.extract_pdf_urls(html, DETAIL) == [PDF_NEW]


def test_extract_excludes_off_origin():
    html = '<a href="https://evil.example.com/x.pdf">x</a>'
    assert S.extract_pdf_urls(html, DETAIL) == []


def test_extract_no_pdf_returns_empty():
    assert S.extract_pdf_urls("<p>nothing here</p>", DETAIL) == []


def test_pdf_url_for_returns_first_or_none(monkeypatch):
    html = IFRAME_LIVE + f'<a href="{PDF_ANNEX}">a</a>'
    monkeypatch.setattr(S, "fetch", lambda url, rate, **kw: html.encode())
    assert S.pdf_url_for(DETAIL, 0.0) == PDF_NEW
    monkeypatch.setattr(S, "fetch", lambda url, rate, **kw: b"<p>no pdf</p>")
    assert S.pdf_url_for(DETAIL, 0.0) is None
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_scrape_sebi.py -v`
Expected: the 9 new tests FAIL with `AttributeError: module 'scrape_sebi' has no attribute 'extract_pdf_urls'`; the 5 existing tests PASS.

- [ ] **Step 4: Implement `extract_pdf_urls` and rewrite `pdf_url_for`**

In `scripts/scrape_sebi.py`, add below the existing `PDF_HREF` definition (line 40):

```python
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
```

Replace the body of `pdf_url_for` (lines 159–161) with:

```python
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


def pdf_url_for(detail_url: str, rate: float) -> str | None:
    urls = extract_pdf_urls(fetch(detail_url, rate).decode("utf-8", "ignore"),
                            detail_url)
    if len(urls) > 1:
        print(f"  note: {len(urls) - 1} additional attachment(s) not ingested "
              f"(one record per circular): {urls[1:]}", flush=True)
    return urls[0] if urls else None
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_scrape_sebi.py -v`
Expected: all tests PASS (14 total).

- [ ] **Step 6: Commit**

```bash
git add scripts/scrape_sebi.py tests/test_scrape_sebi.py
git commit -m "feat: viewer-aware PDF URL extraction for SEBI's 2026 semantic routing"
```

---

### Task 2: PDF magic-byte guard + docstring legality note

**Files:**
- Modify: `scripts/scrape_sebi.py` (module docstring lines 1–17; download loop in `main()` around line 196)
- Test: `tests/test_scrape_sebi.py` (append)

**Interfaces:**
- Produces: `looks_like_pdf(data: bytes) -> bool` in `scripts/scrape_sebi.py`. Task 4 imports it.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_scrape_sebi.py`:

```python
def test_looks_like_pdf_magic_bytes():
    assert S.looks_like_pdf(b"%PDF-1.5 rest of file")
    assert not S.looks_like_pdf(b"<html><head><title>404")
    assert not S.looks_like_pdf(b"")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_scrape_sebi.py::test_looks_like_pdf_magic_bytes -v`
Expected: FAIL with `AttributeError: module 'scrape_sebi' has no attribute 'looks_like_pdf'`.

- [ ] **Step 3: Implement guard and wire into `main()`**

In `scripts/scrape_sebi.py`, add next to `extract_pdf_urls`:

```python
def looks_like_pdf(data: bytes) -> bool:
    """Reject HTML error pages served with a .pdf URL (e.g. WAF/404 bodies)."""
    return data.startswith(b"%PDF")
```

In `main()`, immediately after `data = fetch(pdf_url, args.rate)` (line 196), insert:

```python
            if not looks_like_pdf(data):
                print(f"[{i}] not a PDF payload: {pdf_url}", flush=True)
                failed += 1
                continue
```

- [ ] **Step 4: Update the module docstring**

Replace lines 3–6 of the docstring ("Legality: ... docs/scraping_plan.md.") with:

```
Legality: SEBI robots.txt allows /legal/circulars and /sebi_data/attachdocs (only
/js, /css are disallowed). Self-imposed rate limit, descriptive User-Agent, backoff,
checksum dedupe, official source_url recorded. Never bypasses logins/captchas.
Review SEBI Terms of Use before bulk use. See docs/scraping_plan.md.

URL structure (since SEBI's 2026 site modernisation): detail pages remain at
/legal/circulars/<mon-yyyy>/<slug>_<id>.html; PDFs moved into month-year folders
/sebi_data/attachdocs/<mon-yyyy>/<stem>.pdf and are embedded via a viewer iframe
(src='../../../web/?file=<pdf-url>'). Flat attachdocs paths 404. extract_pdf_urls()
resolves the current URL from the detail page — never predict static PDF names.
```

- [ ] **Step 5: Run the file's tests, then full offline suite**

Run: `.venv/bin/python -m pytest tests/test_scrape_sebi.py -v` → all PASS (15).
Run: `make test` → suite green (baseline was 78 passed, 2 deselected).

- [ ] **Step 6: Commit**

```bash
git add scripts/scrape_sebi.py tests/test_scrape_sebi.py
git commit -m "feat: PDF magic-byte guard and updated URL-structure docs in scraper"
```

---

### Task 3: recovery helpers — month windows and stem resolution

**Files:**
- Modify: `scripts/acquire_missing_pdfs.py` (full rewrite of everything above `main()`)
- Test: Create `tests/test_acquire_missing.py`

**Interfaces:**
- Consumes: `discover(section, max_count, rate, date_from, date_to) -> list[str]`, `fetch(url, rate) -> bytes`, `extract_pdf_urls(html, base_url) -> list[str]` from `scripts/scrape_sebi.py` (Task 1).
- Produces (in `scripts/acquire_missing_pdfs.py`): `MISSING_STEMS: list[str]` (unchanged 14 stems), `month_window(stem: str, pad: int = 1) -> tuple[dt.date, dt.date]`, `stem_of(pdf_url: str) -> str`, `resolve_stems(stems: list[str], rate: float = RATE, discover_fn=..., fetch_fn=...) -> dict[str, tuple[str, str]]` mapping stem → `(pdf_url, detail_url)`. Task 4's `main()` uses all three.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_acquire_missing.py`:

```python
"""Offline tests for the missing-PDF recovery logic (no network)."""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import acquire_missing_pdfs as M  # noqa: E402

STEM = "1705319176210"  # 2024-01-15 UTC
DETAIL = "https://www.sebi.gov.in/legal/circulars/jan-2024/x_1.html"
PDF = f"https://www.sebi.gov.in/sebi_data/attachdocs/jan-2024/{STEM}.pdf"
HTML = f"<iframe src='../../../web/?file={PDF}'>"


def test_month_window_pads_one_month_each_side():
    start, end = M.month_window(STEM)
    assert start == dt.date(2023, 12, 1)
    assert end == dt.date(2024, 2, 29)   # leap year


def test_stem_of_strips_path_and_extension():
    assert M.stem_of(PDF) == STEM


def test_resolve_stems_matches_by_stem():
    def fake_discover(section, max_count, rate, date_from=None, date_to=None):
        assert date_from == dt.date(2023, 12, 1) and date_to == dt.date(2024, 2, 29)
        return [DETAIL]

    resolved = M.resolve_stems([STEM], rate=0.0, discover_fn=fake_discover,
                               fetch_fn=lambda u, r: HTML.encode())
    assert resolved == {STEM: (PDF, DETAIL)}


def test_resolve_stems_reports_nothing_for_unmatched():
    resolved = M.resolve_stems([STEM], rate=0.0,
                               discover_fn=lambda *a, **k: [DETAIL],
                               fetch_fn=lambda u, r: b"<p>no pdf here</p>")
    assert resolved == {}


def test_resolve_stems_survives_detail_fetch_error():
    def bad_fetch(u, r):
        raise RuntimeError("HTTP Error 530: BLOCKED")

    resolved = M.resolve_stems([STEM], rate=0.0,
                               discover_fn=lambda *a, **k: [DETAIL],
                               fetch_fn=bad_fetch)
    assert resolved == {}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_acquire_missing.py -v`
Expected: FAIL with `AttributeError: module 'acquire_missing_pdfs' has no attribute 'month_window'`.

- [ ] **Step 3: Implement the helpers**

Rewrite `scripts/acquire_missing_pdfs.py` above `main()` as:

```python
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
```

Keep the existing `main()` untouched for now (Task 4 rewrites it); if the old
module-level `from scrape_sebi import fetch` line remains anywhere, remove the
duplicate so imports appear once.

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_acquire_missing.py -v`
Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/acquire_missing_pdfs.py tests/test_acquire_missing.py
git commit -m "feat: detail-page stem resolution helpers for missing-PDF recovery"
```

---

### Task 4: recovery `main()` — download, verify, ingest, robots check

**Files:**
- Modify: `scripts/acquire_missing_pdfs.py` (replace `main()`)
- Test: `tests/test_acquire_missing.py` (append)

**Interfaces:**
- Consumes: `resolve_stems`, `month_window`, `MISSING_STEMS`, `RAW`, `CORPUS`, `RATE` (Task 3); `fetch`, `looks_like_pdf` from `scripts/scrape_sebi.py` (Tasks 1–2); `ingest(pdf_path, corpus, source_url=...) -> dict` from `sebi_rag.ingest_pdf`.
- Produces: `check_robots(rate: float = RATE) -> None` (log-only) and `main() -> int` (exit 1 if any stem unresolved/failed).

- [ ] **Step 1: Write the failing test**

Append to `tests/test_acquire_missing.py`:

```python
def test_check_robots_warns_on_disallow(capsys, monkeypatch):
    robots = "User-agent: *\nDisallow: /js\nDisallow: /sebi_data/attachdocs\n"
    monkeypatch.setattr(M, "fetch", lambda u, r: robots.encode())
    M.check_robots(rate=0.0)
    out = capsys.readouterr().out
    assert "WARNING" in out and "/sebi_data/attachdocs" in out


def test_check_robots_quiet_when_allowed(capsys, monkeypatch):
    robots = "User-agent: *\nDisallow: /js\nDisallow: /css\n"
    monkeypatch.setattr(M, "fetch", lambda u, r: robots.encode())
    M.check_robots(rate=0.0)
    assert "WARNING" not in capsys.readouterr().out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_acquire_missing.py -v`
Expected: the 2 new tests FAIL with `AttributeError: ... no attribute 'check_robots'`; the 5 Task-3 tests PASS.

- [ ] **Step 3: Implement `check_robots` and the new `main()`**

Replace `main()` in `scripts/acquire_missing_pdfs.py` with:

```python
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
```

- [ ] **Step 4: Run the file's tests, then the full offline suite**

Run: `.venv/bin/python -m pytest tests/test_acquire_missing.py -v` → 7 PASS.
Run: `make test` → suite green, no regressions.

- [ ] **Step 5: Commit**

```bash
git add scripts/acquire_missing_pdfs.py tests/test_acquire_missing.py
git commit -m "feat: recovery main() with robots re-check, magic-byte guard, detail-page provenance"
```

---

### Task 5: live verification, corpus recovery run, docs, merge

**Files:**
- Modify: `docs/superpowers/plans/2026-07-08-regai-inspired-enhancements.md` (Task 11 status)
- Data: `data/raw/*.pdf`, `data/corpus/circulars.jsonl` (grown by recovery run)

**Interfaces:**
- Consumes: everything from Tasks 1–4; `scripts/validate_corpus.py`; `make reindex`.

> Live steps: run sequentially from this machine only; each script self-rate-limits at 3 s. The recovery run takes roughly 10–20 minutes.

- [ ] **Step 1: Live smoke test of the hardened scraper**

Run: `PYTHONPATH=src .venv/bin/python scripts/scrape_sebi.py --section circulars --max 2 --rate 3`
Expected: 2 detail pages discovered; each resolves a `/sebi_data/attachdocs/<mon-yyyy>/<stem>.pdf` URL; status `ingested` or `duplicate` (both fine); `failed=0`.

- [ ] **Step 2: Run the recovery script**

Run: `.venv/bin/python scripts/acquire_missing_pdfs.py`
Expected: no robots WARNING; `resolved=N` (target 14); per-stem `ingested:`/`duplicate:` lines; exit 0. For any `UNRESOLVED` stem, record the stem and the swept window in the plan's Task 11 notes as possibly withdrawn — do not retry with guessed URLs.

- [ ] **Step 3: Validate the grown corpus**

Run: `.venv/bin/python scripts/validate_corpus.py`
Expected: 0 violations; record count ≥ 603 (603 + newly ingested).

- [ ] **Step 4: Rebuild the index**

Run: `make reindex`
Expected: completes without error; chunk/manifest counts grow accordingly (this re-embeds and can take a while on MPS).

- [ ] **Step 5: Full offline suite**

Run: `make test`
Expected: green (no regressions from the reindexed artifacts).

- [ ] **Step 6: Flip Task 11 status in the enhancement plan**

In `docs/superpowers/plans/2026-07-08-regai-inspired-enhancements.md`, change Task 11's status from BLOCKED to done, with a note:

```
Task 11 — DONE 2026-07-09 (was BLOCKED). SEBI did not delete the PDFs; the 2026
site modernisation moved them to /sebi_data/attachdocs/<mon-yyyy>/<stem>.pdf
behind a web/?file= viewer. Recovery now resolves each stem's detail page via
month-window listing sweeps. See
docs/superpowers/specs/2026-07-09-sebi-semantic-routing-alignment-design.md and
docs/superpowers/plans/2026-07-09-sebi-semantic-routing-alignment.md.
Unresolved stems (if any): <list or "none">.
```

- [ ] **Step 7: Commit data + docs, merge to main**

```bash
git add data/raw data/corpus data/index docs/superpowers/plans/2026-07-08-regai-inspired-enhancements.md
git commit -m "feat: recover missing circular PDFs via detail-page resolution (Task 11 unblocked)"
git checkout main
git merge --no-ff semantic-routing-alignment -m "Merge semantic-routing-alignment: viewer-aware extraction + missing-PDF recovery"
make test
```

Expected: merge clean, suite green on main.
