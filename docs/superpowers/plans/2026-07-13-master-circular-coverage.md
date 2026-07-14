# Master Circular Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Model-agnostic execution (spec §5):** Any model or harness (Claude, local MLX/Ollama, other tools) may execute any task. Each task is self-contained: exact files, complete code, runnable commands, expected output. No intermediate review by any specific model is required; validation is the commands in each task. At most one minimal Fable review at the very end, only if the user requests it.
>
> Spec: `docs/superpowers/specs/2026-07-13-master-circular-coverage-design.md`

**Goal:** Ingest all ~135 SEBI master circulars from the official listing (sid=1, ssid=6), enhance master-circular metadata (identity fields + consolidation lineage), and ship a permanent `make verify-master` coverage-verification module whose statistical report confirms coverage across `data/corpus` and `dist/datasets`, propagated through to HF Hub and the live Space.

**Architecture:** A new pure library `src/sebi_rag/verify_master.py` (listing parser, diff engine, report renderer — fully offline-testable) plus a thin network CLI `scripts/verify_master.py` that reuses `scripts/scrape_sebi.py`'s session/paging. Metadata enhancements live in a new `src/sebi_rag/master_meta.py`, wired into the existing `lineage.annotate_corpus()` annotate stage. Ingestion reuses the existing scraper with `--section master-circulars`.

**Tech Stack:** Python 3.12–3.13, stdlib-only for new modules (re, json, urllib, collections), pytest (offline marker convention: `-m "not integration"`), Make, existing HF push/deploy scripts.

## Global Constraints

- Python 3.12–3.13, run via `.venv/bin/python`; `PYTHONPATH=src` (the `$(ENV)` Make prefix).
- Offline test suite must stay green at every task boundary: `make test` (baseline 212 passed). Network tests get `@pytest.mark.integration`.
- Golden as-of eval gate must stay 13/13: `make eval-asof`.
- Metadata rules are LOCKED (`src/sebi_rag/metadata.py` docstring): new corpus fields are additive; existing fields never change meaning; only `explicit_text` edges with relation `supersedes`/`amends` affect `validity_status` — `consolidates` edges must never flip validity.
- Scraper politeness: rate ≥ 3s, existing `UA` string, never bypass logins/captchas.
- Degenerate-chunk guard (nominee-bug lesson): every ingested record must have non-trivial body text; the verify report flags `text_chars < 500` as `parse_failed`.
- If `graphify-out/graph.json` exists in the working copy, run `graphify query "<question>"` before opening source files, and `graphify update .` after code changes (repo hook enforces this).
- Commit after every task (and at each marked commit step inside tasks).

## File Structure (created/modified across all tasks)

| Path | Responsibility |
|------|----------------|
| `src/sebi_rag/verify_master.py` (create) | Pure functions: listing-HTML parsing, manifest diff, summary stats, markdown rendering |
| `scripts/verify_master.py` (create) | CLI: fetch live listing pages, write manifest, run diff, write reports |
| `src/sebi_rag/master_meta.py` (create) | Master identity fields (series/edition/previous-edition) + rescission-appendix parser |
| `src/sebi_rag/lineage.py` (modify `annotate_corpus`) | Wire master fields + consolidates edges into the annotate stage |
| `Makefile` (modify) | `scrape-master`, `verify-master` targets + help lines |
| `tests/test_verify_master.py`, `tests/test_master_meta.py` (create) | Offline unit tests |
| `tests/fixtures/master_listing_page0.html` (create) | Real captured listing page 0 |
| `tests/fixtures/master_appendix_*.txt` (create, 3 files) | Rescission-appendix excerpts from real master-circular PDFs |
| `data/manifests/master_circulars.jsonl` (generated) | One row per listed master circular |
| `data/manifests/master_exceptions.jsonl` (hand-maintained) | `{"detail_url":…, "reason":…}` per unfetchable item |
| `reports/master_coverage.json` / `.md` (generated) | The statistical summary artifacts |

---

### Task 1: Listing parser (`verify_master.parse_listing`)

**Files:**
- Create: `src/sebi_rag/verify_master.py`
- Create: `tests/test_verify_master.py`
- Create: `tests/fixtures/master_listing_page0.html`

**Interfaces:**
- Consumes: nothing (pure stdlib).
- Produces: `parse_listing(html: str) -> list[dict]` — rows `{"listing_date": "YYYY-MM-DD"|None, "detail_url": str, "title": str}`, page order, deduped by URL. Later tasks rely on exactly these three keys.

- [x] **Step 1: Capture the real fixture (one-time network step)**

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
curl -s 'https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=6&smid=0' \
  -A 'SEBI-RAG-research/0.2 (local research; contact: ianpinto1980@gmail.com)' \
  -o tests/fixtures/master_listing_page0.html
grep -c 'legal/master-circulars' tests/fixtures/master_listing_page0.html
```

Expected: count ≥ 20 (each row links a master-circular detail page). If 0, the WAF served an error page — retry once after 30s; if still 0, stop and report.

- [x] **Step 2: Write the failing test**

```python
# tests/test_verify_master.py
from pathlib import Path

from sebi_rag.verify_master import parse_listing

FIXTURE = Path(__file__).parent / "fixtures" / "master_listing_page0.html"


def test_parse_listing_extracts_rows_from_real_page():
    rows = parse_listing(FIXTURE.read_text(encoding="utf-8", errors="ignore"))
    assert len(rows) >= 20
    first = rows[0]
    assert set(first) == {"listing_date", "detail_url", "title"}
    assert first["detail_url"].startswith(
        "https://www.sebi.gov.in/legal/master-circulars/")
    assert "master circular" in first["title"].lower()
    assert first["listing_date"] and len(first["listing_date"]) == 10


def test_parse_listing_dedupes_and_ignores_non_master_links():
    html = (
        '<tr><td>Jun 10, 2026</td><td><a href='
        '"https://www.sebi.gov.in/legal/master-circulars/jun-2026/x_100.html">'
        'Master Circular for Depositories</a></td></tr>'
        '<tr><td>Jun 10, 2026</td><td><a href='
        '"https://www.sebi.gov.in/legal/master-circulars/jun-2026/x_100.html">'
        'Master Circular for Depositories</a></td></tr>'
        '<a href="https://www.sebi.gov.in/legal/circulars/jun-2026/y_1.html">c</a>'
    )
    rows = parse_listing(html)
    assert len(rows) == 1
    assert rows[0] == {
        "listing_date": "2026-06-10",
        "detail_url": "https://www.sebi.gov.in/legal/master-circulars/jun-2026/x_100.html",
        "title": "Master Circular for Depositories",
    }


def test_parse_listing_empty_html():
    assert parse_listing("") == []
```

- [x] **Step 3: Run to verify failure**

Run: `.venv/bin/python -m pytest tests/test_verify_master.py -v` (with `PYTHONPATH=src`)
Expected: FAIL — `ModuleNotFoundError: No module named 'sebi_rag.verify_master'`

- [x] **Step 4: Implement**

```python
# src/sebi_rag/verify_master.py
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
        title = _WS.sub(" ", _TAG0.sub("", anchor)).strip()
        rows.append({"listing_date": _iso(ds), "detail_url": url, "title": title})
    return rows
```
(Note: _TAGS used in actual code, the dummy _TAG0 is a typo in the original plan's example code block)

- [x] **Step 5: Run to verify pass**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_verify_master.py -v`
Expected: 3 passed. If `test_parse_listing_extracts_rows_from_real_page` fails, inspect the fixture's actual row markup (`grep -o '<a [^>]*master-circulars[^<]*' tests/fixtures/master_listing_page0.html | head -3`) and adjust `_ROW` — the fixture is ground truth, not the regex.

- [x] **Step 6: Full suite + commit**

```bash
make test   # expected: 215 passed (212 baseline + 3 new)
git add src/sebi_rag/verify_master.py tests/test_verify_master.py tests/fixtures/master_listing_page0.html
git commit -m "feat(verify): master-circular listing parser with real-page fixture"
```

**Checkpoint Review:** Task 1 completed. Verified implementation of `parse_listing` with a real-page fixture. Tests passed (3/3 expected). Commit `5da45d3` finalized.


---

### Task 2: Diff engine, summary statistics, markdown report

**Files:**
- Modify: `src/sebi_rag/verify_master.py` (append)
- Modify: `tests/test_verify_master.py` (append)

**Interfaces:**
- Consumes: manifest rows from Task 1 (`listing_date`, `detail_url`, `title`, optional `pdf_url`).
- Produces (later tasks call exactly these):
  - `diff_manifest(manifest: list[dict], corpus_records: list[dict], raw_pdf_stems: frozenset[str] = frozenset(), exceptions: dict[str, str] | None = None, dist_numbers: set[str] | None = None) -> list[dict]`
  - `summarize(diffed: list[dict]) -> dict`
  - `render_markdown(summary: dict) -> str`
  - `write_reports(summary: dict, reports_dir: str | Path) -> tuple[Path, Path]`
- Status vocabulary (spec §1, exact strings): `ingested_ok | fetched_not_ingested | parse_failed | missing | unfetchable | extra_in_corpus`.

- [ ] **Step 1: Write the failing tests**

```python
# append to tests/test_verify_master.py
from sebi_rag.verify_master import (diff_manifest, render_markdown, summarize,
                                    write_reports)


def _row(url="https://www.sebi.gov.in/legal/master-circulars/jun-2026/a_1.html",
         date="2026-06-10", title="Master Circular for Depositories"):
    return {"listing_date": date, "detail_url": url, "title": title}


def _rec(url, number="SEBI/HO/MRD/2026/1", date="2026-06-10", chars=5000):
    return {"source_url": url, "circular_number": number, "issue_date": date,
            "subject": "Master Circular for Depositories", "text": "x" * chars,
            "circular_type": "MASTER_CIRCULAR", "validity_status": "current"}


def test_diff_statuses():
    m = [
        _row(),                                                    # ingested_ok
        _row("https://www.sebi.gov.in/legal/master-circulars/a_2.html"),  # parse_failed
        _row("https://www.sebi.gov.in/legal/master-circulars/a_3.html"),  # fetched_not_ingested
        _row("https://www.sebi.gov.in/legal/master-circulars/a_4.html"),  # unfetchable
        _row("https://www.sebi.gov.in/legal/master-circulars/a_5.html"),  # missing
    ]
    m[2]["pdf_url"] = "https://www.sebi.gov.in/sebi_data/attachdocs/9876.pdf"
    corpus = [
        _rec(m[0]["detail_url"]),
        _rec(m[1]["detail_url"], number="SEBI/HO/MRD/2026/2", chars=100),  # degenerate
        _rec("https://www.sebi.gov.in/legal/master-circulars/old_9.html",
             number="SEBI/HO/OLD/2020/9"),                         # extra_in_corpus
    ]
    d = diff_manifest(m, corpus, raw_pdf_stems=frozenset({"9876"}),
                      exceptions={m[3]["detail_url"]: "404 on SEBI side"},
                      dist_numbers={"SEBI/HO/MRD/2026/1"})
    by_url = {x["detail_url"]: x for x in d}
    assert by_url[m[0]["detail_url"]]["status"] == "ingested_ok"
    assert by_url[m[0]["detail_url"]]["in_dist"] is True
    assert by_url[m[1]["detail_url"]]["status"] == "parse_failed"
    assert by_url[m[1]["detail_url"]]["validation"]["degenerate_text"] is True
    assert by_url[m[2]["detail_url"]]["status"] == "fetched_not_ingested"
    assert by_url[m[3]["detail_url"]]["status"] == "unfetchable"
    assert by_url[m[3]["detail_url"]]["reason"] == "404 on SEBI side"
    assert by_url[m[4]["detail_url"]]["status"] == "missing"
    assert by_url["https://www.sebi.gov.in/legal/master-circulars/old_9.html"][
        "status"] == "extra_in_corpus"


def test_summarize_and_markdown():
    m = [_row(), _row("https://www.sebi.gov.in/legal/master-circulars/a_5.html",
                      date="2024-05-01")]
    d = diff_manifest(m, [_rec(m[0]["detail_url"])])
    s = summarize(d)
    assert s["listed_total"] == 2
    assert s["status_counts"] == {"ingested_ok": 1, "missing": 1}
    assert s["coverage_pct"] == 50.0        # of retrievable (no unfetchables)
    assert s["by_year"] == {"2026": {"listed": 1, "ingested_ok": 1},
                            "2024": {"listed": 1, "ingested_ok": 0}}
    assert s["gaps"][0]["detail_url"].endswith("a_5.html")
    md = render_markdown(s)
    assert "50.0%" in md and "missing" in md


def test_coverage_pct_excludes_unfetchable():
    m = [_row(), _row("https://www.sebi.gov.in/legal/master-circulars/a_4.html")]
    d = diff_manifest(m, [_rec(m[0]["detail_url"])],
                      exceptions={m[1]["detail_url"]: "dead link"})
    assert summarize(d)["coverage_pct"] == 100.0


def test_write_reports(tmp_path):
    d = diff_manifest([_row()], [_rec(_row()["detail_url"])])
    jp, mp = write_reports(summarize(d), tmp_path)
    assert jp.name == "master_coverage.json" and mp.name == "master_coverage.md"
    import json as _json
    assert _json.loads(jp.read_text())["coverage_pct"] == 100.0
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_verify_master.py -v`
Expected: FAIL — `ImportError: cannot import name 'diff_manifest'`

- [ ] **Step 3: Implement**

```python
# append to src/sebi_rag/verify_master.py
_ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DEGENERATE_TEXT_CHARS = 500  # nominee-bug lesson: heading-only bodies


def _validation(rec: dict) -> dict:
    text = rec.get("text") or ""
    date = rec.get("issue_date") or ""
    return {
        "has_number": bool(rec.get("circular_number")),
        "has_issue_date": bool(_ISO_RE.match(date)),
        "text_chars": len(text),
        "degenerate_text": len(text) < DEGENERATE_TEXT_CHARS,
    }


def diff_manifest(manifest: list[dict], corpus_records: list[dict],
                  raw_pdf_stems: frozenset[str] = frozenset(),
                  exceptions: dict[str, str] | None = None,
                  dist_numbers: set[str] | None = None) -> list[dict]:
    """Assign exactly one status to every listed row + extra_in_corpus rows."""
    exceptions = exceptions or {}
    by_url: dict[str, dict] = {}
    for r in corpus_records:
        u = r.get("source_url")
        if u:
            by_url.setdefault(u, r)
    out = []
    for row in manifest:
        item = dict(row)
        rec = by_url.get(row["detail_url"])
        if rec is not None:
            v = _validation(rec)
            item["validation"] = v
            item["circular_number"] = rec.get("circular_number")
            item["circular_type"] = rec.get("circular_type")
            item["validity_status"] = rec.get("validity_status")
            ok = v["has_number"] and v["has_issue_date"] and not v["degenerate_text"]
            item["status"] = "ingested_ok" if ok else "parse_failed"
            if dist_numbers is not None:
                item["in_dist"] = rec.get("circular_number") in dist_numbers
        elif row["detail_url"] in exceptions:
            item["status"] = "unfetchable"
            item["reason"] = exceptions[row["detail_url"]]
        elif (row.get("pdf_url") or "").rsplit("/", 1)[-1].removesuffix(".pdf") \
                in raw_pdf_stems and row.get("pdf_url"):
            item["status"] = "fetched_not_ingested"
        else:
            item["status"] = "missing"
        out.append(item)
    listed = {r["detail_url"] for r in manifest}
    for r in corpus_records:
        u = r.get("source_url") or ""
        if (r.get("circular_type") == "MASTER_CIRCULAR"
                and "/legal/master-circulars/" in u and u not in listed):
            out.append({"detail_url": u, "title": r.get("subject", ""),
                        "circular_number": r.get("circular_number"),
                        "status": "extra_in_corpus"})
    return out


def summarize(diffed: list[dict]) -> dict:
    listed = [d for d in diffed if d["status"] != "extra_in_corpus"]
    counts = Counter(d["status"] for d in diffed)
    ok = counts.get("ingested_ok", 0)
    retrievable = len(listed) - counts.get("unfetchable", 0)
    by_year: dict[str, dict] = defaultdict(lambda: {"listed": 0, "ingested_ok": 0})
    for d in listed:
        year = (d.get("listing_date") or "unknown")[:4]
        by_year[year]["listed"] += 1
        by_year[year]["ingested_ok"] += d["status"] == "ingested_ok"
    gap_statuses = ("missing", "fetched_not_ingested", "parse_failed")
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "listed_total": len(listed),
        "status_counts": dict(counts),
        "coverage_pct": round(100 * ok / retrievable, 1) if retrievable else 0.0,
        "dist_covered": sum(1 for d in listed if d.get("in_dist")),
        "by_year": dict(sorted(by_year.items(), reverse=True)),
        "by_validity": dict(Counter(d["validity_status"] for d in listed
                                    if d.get("validity_status"))),
        "gaps": [d for d in diffed if d["status"] in gap_statuses],
        "unfetchable": [d for d in diffed if d["status"] == "unfetchable"],
        "extra_in_corpus": [d for d in diffed if d["status"] == "extra_in_corpus"],
    }


def render_markdown(summary: dict) -> str:
    s = summary
    lines = [
        "# Master Circular Coverage Report", "",
        f"Generated: {s['generated_at']}",
        f"Listed on SEBI site: **{s['listed_total']}** | "
        f"Coverage (of retrievable): **{s['coverage_pct']}%** | "
        f"In dist/datasets: **{s['dist_covered']}**", "",
        "## Status counts", "", "| status | count |", "|---|---|",
    ]
    lines += [f"| {k} | {v} |" for k, v in sorted(s["status_counts"].items())]
    lines += ["", "## By year", "", "| year | listed | ingested_ok |", "|---|---|---|"]
    lines += [f"| {y} | {c['listed']} | {c['ingested_ok']} |"
              for y, c in s["by_year"].items()]
    if s["by_validity"]:
        lines += ["", "## Validity of ingested", "", "| validity | count |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in sorted(s["by_validity"].items())]
    for name in ("gaps", "unfetchable", "extra_in_corpus"):
        if s[name]:
            lines += ["", f"## {name} ({len(s[name])})", ""]
            lines += [f"- `{d['status']}` {d.get('title', '')} — {d['detail_url']}"
                      + (f" ({d['reason']})" if d.get("reason") else "")
                      for d in s[name]]
    return "\n".join(lines) + "\n"


def write_reports(summary: dict, reports_dir: str | Path) -> tuple[Path, Path]:
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    jp = reports_dir / "master_coverage.json"
    mp = reports_dir / "master_coverage.md"
    jp.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                  encoding="utf-8")
    mp.write_text(render_markdown(summary), encoding="utf-8")
    return jp, mp
```

- [ ] **Step 4: Run to verify pass**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_verify_master.py -v`
Expected: 7 passed.

- [ ] **Step 5: Full suite + commit**

```bash
make test   # expected: 219 passed
git add src/sebi_rag/verify_master.py tests/test_verify_master.py
git commit -m "feat(verify): diff engine + statistical summary + markdown report"
```

---

### Task 3: CLI, Make targets, baseline coverage report

**Files:**
- Create: `scripts/verify_master.py`
- Modify: `Makefile` (targets + help)
- Generated: `data/manifests/master_circulars.jsonl`, `reports/master_coverage.{json,md}`

**Interfaces:**
- Consumes: `parse_listing`, `diff_manifest`, `summarize`, `write_reports` (Tasks 1–2); `_page`, `SECTIONS`, `pdf_url_for` from `scripts/scrape_sebi.py`; `load_records` from `sebi_rag.lineage`.
- Produces: `make verify-master` (network fetch + reports) and `make verify-master OFFLINE=1` (reuse existing manifest). Exit code 0 always when the run completes (coverage gaps are report content, not failures).

- [ ] **Step 1: Write the CLI**

```python
# scripts/verify_master.py
"""Verify master-circular coverage: live ssid=6 listing vs corpus vs dist.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/verify_master.py            # fetch + report
    PYTHONPATH=src .venv/bin/python scripts/verify_master.py --offline  # reuse manifest
    ... --resolve-pdfs   # also resolve PDF URLs for unmatched rows (slower)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sebi_rag.lineage import load_records                     # noqa: E402
from sebi_rag.verify_master import (diff_manifest, parse_listing,  # noqa: E402
                                    summarize, write_reports)
from scrape_sebi import SECTIONS, _page, pdf_url_for          # noqa: E402


def fetch_manifest(rate: float, max_pages: int) -> list[dict]:
    sid, ssid, smid = SECTIONS["master-circulars"]
    rows, seen, prev_first = [], set(), None
    for page in range(max_pages):
        try:
            raw = _page(sid, ssid, smid, page, rate)
        except Exception as e:  # noqa: BLE001
            print(f"  page {page} fetch failed ({e}); stopping", flush=True)
            break
        page_rows = parse_listing(raw.decode("utf-8", "ignore"))
        if not page_rows or (page > 0 and page_rows[0]["detail_url"] == prev_first):
            break
        prev_first = page_rows[0]["detail_url"]
        rows += [r for r in page_rows if r["detail_url"] not in seen]
        seen |= {r["detail_url"] for r in page_rows}
        time.sleep(rate)
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--offline", action="store_true",
                    help="reuse existing manifest; no network")
    ap.add_argument("--resolve-pdfs", action="store_true",
                    help="resolve PDF URLs for rows not matched to corpus")
    ap.add_argument("--manifest", default="data/manifests/master_circulars.jsonl")
    ap.add_argument("--exceptions", default="data/manifests/master_exceptions.jsonl")
    ap.add_argument("--corpus", default="data/corpus/circulars.jsonl")
    ap.add_argument("--dist", default="dist/datasets/corpus/corpus.jsonl")
    ap.add_argument("--raw", default="data/raw")
    ap.add_argument("--reports", default="reports")
    ap.add_argument("--rate", type=float, default=3.0)
    ap.add_argument("--max-pages", type=int, default=10)
    args = ap.parse_args(argv)

    mpath = Path(args.manifest)
    if args.offline:
        manifest = [json.loads(x) for x in
                    mpath.read_text(encoding="utf-8").splitlines() if x.strip()]
    else:
        manifest = fetch_manifest(args.rate, args.max_pages)
        mpath.parent.mkdir(parents=True, exist_ok=True)
        mpath.write_text("\n".join(json.dumps(r, ensure_ascii=False)
                                   for r in manifest) + "\n", encoding="utf-8")
    print(f"manifest rows: {len(manifest)}", flush=True)

    corpus = load_records(args.corpus)
    corpus_urls = {r.get("source_url") for r in corpus}
    if args.resolve_pdfs and not args.offline:
        for row in manifest:
            if row["detail_url"] not in corpus_urls and "pdf_url" not in row:
                time.sleep(args.rate)
                try:
                    row["pdf_url"] = pdf_url_for(row["detail_url"], args.rate) or ""
                except Exception as e:  # noqa: BLE001
                    print(f"  pdf resolve failed {row['detail_url']}: {e}", flush=True)
        mpath.write_text("\n".join(json.dumps(r, ensure_ascii=False)
                                   for r in manifest) + "\n", encoding="utf-8")

    exceptions = {}
    epath = Path(args.exceptions)
    if epath.exists():
        for line in epath.read_text(encoding="utf-8").splitlines():
            if line.strip():
                e = json.loads(line)
                exceptions[e["detail_url"]] = e["reason"]

    dist_numbers = None
    dpath = Path(args.dist)
    if dpath.exists():
        dist_numbers = {json.loads(x)["circular_number"]
                        for x in dpath.read_text(encoding="utf-8").splitlines()
                        if x.strip()}

    stems = frozenset(p.stem for p in Path(args.raw).glob("*.pdf"))
    diffed = diff_manifest(manifest, corpus, raw_pdf_stems=stems,
                           exceptions=exceptions, dist_numbers=dist_numbers)
    summary = summarize(diffed)
    jp, mp = write_reports(summary, args.reports)
    print(f"coverage: {summary['coverage_pct']}% of retrievable "
          f"({summary['status_counts']}); reports: {jp}, {mp}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Add Make targets**

In `Makefile`: add `MAX_MASTER ?= 200` under the `MAX ?= 25` line; add `scrape-master verify-master` to `.PHONY`; add help lines `@echo "scrape-master  fetch master circulars (MAX_MASTER=$(MAX_MASTER))"` and `@echo "verify-master  coverage report vs live SEBI master-circular listing (OFFLINE=1 to skip fetch)"`; append targets:

```make
scrape-master:
	$(ENV) $(PY) scripts/scrape_sebi.py --section master-circulars --max $(MAX_MASTER) --rate 3

verify-master:
	$(ENV) $(PY) scripts/verify_master.py $(if $(OFFLINE),--offline,)
```

- [ ] **Step 3: Baseline real run**

Run: `make verify-master`
Expected output shape: `manifest rows: ~135`, `coverage: ~18% of retrievable ({'ingested_ok': ~25, 'missing': ~110, ...})`. Reports written to `reports/`. This is the **baseline** gap report — the number the ingestion loop must drive to 100%.

- [ ] **Step 4: Full suite + commit**

```bash
make test   # expected: 219 passed (CLI has no offline unit tests; library is covered)
git add scripts/verify_master.py Makefile data/manifests/master_circulars.jsonl reports/
git commit -m "feat(verify): verify-master CLI + Make targets + baseline coverage report"
```

---

### Task 4: Ingestion loop to 100% (operational)

**Files:**
- Generated: `data/raw/*.pdf`, `data/corpus/circulars.jsonl` (appended), `data/manifests/master_exceptions.jsonl` (only if needed), updated reports.

**Interfaces:**
- Consumes: `make scrape-master`, `make verify-master`, `scripts/ingest_pdf` CLI (`PYTHONPATH=src .venv/bin/python -m sebi_rag.ingest_pdf <pdf> --source-url <detail_url> [--ocr]`), `scripts/acquire_missing_pdfs.py` if needed.
- Produces: corpus where every manifest row is `ingested_ok` or documented `unfetchable`.

- [ ] **Step 1: Bulk scrape**

Run: `make scrape-master` (~135 items × ≥3 fetches × 3s ≈ 25–40 min; run in background, capture the log).
Expected tail: `Done. ingested=~110 skipped=~25 failed=<n>`.

- [ ] **Step 2: Re-verify**

Run: `make verify-master` then read `reports/master_coverage.md`.
Every remaining gap is now one of: `missing` (discovery/pagination miss), `fetched_not_ingested` (PDF in data/raw, ingest threw — usually "No SEBI circular number found"), `parse_failed` (ingested but degenerate/missing date).

- [ ] **Step 3: Fix stragglers one by one**

For each gap row (use `--resolve-pdfs` once to get PDF URLs for unmatched rows):
- `fetched_not_ingested`: retry with OCR: `PYTHONPATH=src .venv/bin/python -m sebi_rag.ingest_pdf data/raw/<stem>.pdf --source-url <detail_url> --ocr`. If the parser mis-extracts the number/date on a master-circular format variant, fix the regex in `src/sebi_rag/ingest_pdf.py` following the existing strategy pattern (`_PRIMARY_STRATEGIES`) with a unit test in `tests/test_ingest_pdf.py` reproducing the header excerpt.
- `parse_failed` with `degenerate_text`: the PDF is scanned → re-ingest with `--ocr --replace`.
- `missing`: fetch the detail page manually (`curl` with the project UA), get the PDF via the viewer URL, download to `data/raw/`, write its `.sha256`, ingest with `--source-url`.
- Genuinely dead (SEBI 404s the detail page and PDF): append `{"detail_url": "...", "reason": "..."}` to `data/manifests/master_exceptions.jsonl`.

- [ ] **Step 4: Exit criterion**

Run: `make verify-master` until `status_counts` contains only `ingested_ok` (+ possibly `unfetchable`, `extra_in_corpus`). `coverage_pct` must print **100.0**.

- [ ] **Step 5: Annotate + full suite + commit**

```bash
make annotate    # recompute supersession/validity over the grown corpus
make test        # expected: all passing (219)
make verify-master OFFLINE=1   # regenerate reports post-annotate
git add data/corpus/circulars.jsonl data/manifests/ reports/ tests/ src/
git commit -m "feat(corpus): ingest all SEBI master circulars to 100% listed coverage"
```
(`data/raw` PDFs stay untracked if the repo already ignores them — check `git check-ignore data/raw` first; follow existing convention.)

---

### Task 5: Master identity fields (`master_meta.py`)

**Files:**
- Create: `src/sebi_rag/master_meta.py`
- Create: `tests/test_master_meta.py`

**Interfaces:**
- Consumes: corpus record dicts (`circular_type`, `subject`, `issue_date`, `circular_number`).
- Produces (Task 7 calls these):
  - `master_series(subject: str | None) -> str | None`
  - `annotate_master_fields(records: list[dict]) -> int` — sets `is_master: bool`, `master_series: str|None`, `master_edition: int|None`, `previous_edition: str|None` on every record in place; returns count changed.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_master_meta.py
from sebi_rag.master_meta import annotate_master_fields, master_series


def _master(n, subj, date):
    return {"circular_number": n, "subject": subj, "issue_date": date,
            "circular_type": "MASTER_CIRCULAR"}


def test_master_series_rule_table():
    assert master_series("Master Circular for Mutual Funds") == "Mutual Funds"
    assert master_series("Master Circular for Depositories") == "Depositories"
    assert master_series("Master Circular for Stock Brokers") == "Stock Brokers"
    assert master_series(
        "Master Circular for Alternative Investment Funds (AIFs)") == "AIFs"
    assert master_series("Master Circular on something novel") is None
    assert master_series(None) is None


def test_annotate_sets_identity_and_chains_editions():
    recs = [
        _master("MF/2023/1", "Master Circular for Mutual Funds", "2023-05-19"),
        _master("MF/2024/2", "Master Circular for Mutual Funds", "2024-06-27"),
        _master("DEP/2024/3", "Master Circular for Depositories", "2024-10-06"),
        {"circular_number": "C/1", "subject": "Nomination", "issue_date":
         "2025-01-10", "circular_type": "CIRCULAR"},
    ]
    changed = annotate_master_fields(recs)
    assert changed == 4
    assert recs[0]["is_master"] and recs[0]["master_edition"] == 2023
    assert recs[0]["previous_edition"] is None
    assert recs[1]["previous_edition"] == "MF/2023/1"     # chained by series+date
    assert recs[2]["previous_edition"] is None            # different series
    assert recs[3] == {**recs[3], "is_master": False, "master_series": None,
                       "master_edition": None, "previous_edition": None}


def test_annotate_idempotent():
    recs = [_master("MF/2023/1", "Master Circular for Mutual Funds", "2023-05-19")]
    annotate_master_fields(recs)
    assert annotate_master_fields(recs) == 0
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_master_meta.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sebi_rag.master_meta'`

- [ ] **Step 3: Implement**

```python
# src/sebi_rag/master_meta.py
"""Master-circular identity metadata (spec 2026-07-13 §3).

Additive fields only (locked metadata rules): is_master, master_series,
master_edition, previous_edition. Series come from a maintained rule table;
unmatched subjects get None (surfaced by the coverage report, extend the
table as new series appear).
"""
from __future__ import annotations

import re
from collections import defaultdict

MASTER_SERIES_RULES: tuple[tuple[str, re.Pattern], ...] = tuple(
    (name, re.compile(pat, re.I)) for name, pat in (
        ("Mutual Funds", r"mutual\s+fund"),
        ("AIFs", r"alternative\s+investment\s+fund|\bAIFs?\b"),
        ("Depositories", r"depositor"),
        ("Stock Exchanges & Clearing Corporations",
         r"stock\s+exchange|clearing\s+corporation"),
        ("Stock Brokers", r"stock\s+broker"),
        ("Debenture Trustees", r"debenture\s+trustee"),
        ("REITs", r"real\s+estate\s+investment\s+trust|\bREITs?\b"),
        ("InvITs", r"infrastructure\s+investment\s+trust|\bInvITs?\b"),
        ("Portfolio Managers", r"portfolio\s+manager"),
        ("Credit Rating Agencies", r"credit\s+rating\s+agenc"),
        ("Research Analysts", r"research\s+analyst"),
        ("Investment Advisers", r"investment\s+advis"),
        ("Merchant Bankers", r"merchant\s+banker"),
        ("Custodians", r"\bcustodian"),
        ("KYC & AML", r"know\s+your\s+client|\bKYC\b|anti[- ]money\s+laundering"),
        ("Surveillance", r"\bsurveillance\b"),
        ("Online Dispute Resolution", r"online\s+dispute\s+resolution|\bODR\b"),
        ("Foreign Portfolio Investors", r"foreign\s+portfolio\s+investor|\bFPIs?\b"),
        ("Commodity Derivatives", r"commodity\s+derivative"),
        ("ESG Rating Providers", r"ESG\s+rating"),
    ))
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def master_series(subject: str | None) -> str | None:
    s = subject or ""
    for name, pat in MASTER_SERIES_RULES:
        if pat.search(s):
            return name
    return None


def annotate_master_fields(records: list[dict]) -> int:
    """Set is_master/master_series/master_edition/previous_edition in place.

    Returns the number of records whose four identity fields changed
    (idempotent: a second call on the same records returns 0).
    """
    before = [(r.get("is_master"), r.get("master_series"),
               r.get("master_edition"), r.get("previous_edition"))
              for r in records]
    by_series: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        is_master = r.get("circular_type") == "MASTER_CIRCULAR"
        series = master_series(r.get("subject")) if is_master else None
        date = r.get("issue_date") or ""
        r["is_master"] = is_master
        r["master_series"] = series
        r["master_edition"] = int(date[:4]) if is_master and _ISO.match(date) else None
        r["previous_edition"] = None
        if is_master and series and _ISO.match(date):
            by_series[series].append(r)
    for series_recs in by_series.values():
        series_recs.sort(key=lambda r: r["issue_date"])
        for prev, cur in zip(series_recs, series_recs[1:]):
            cur["previous_edition"] = prev["circular_number"]
    return sum(1 for r, b in zip(records, before)
               if (r["is_master"], r["master_series"],
                   r["master_edition"], r["previous_edition"]) != b)
```

- [ ] **Step 4: Run to verify pass**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_master_meta.py -v`
Expected: 3 passed.

- [ ] **Step 5: Full suite + commit**

```bash
make test   # expected: 222 passed
git add src/sebi_rag/master_meta.py tests/test_master_meta.py
git commit -m "feat(metadata): master identity fields (series/edition/previous-edition)"
```

---

### Task 6: Rescission-appendix parser → consolidates edges

**Files:**
- Modify: `src/sebi_rag/master_meta.py` (append)
- Modify: `tests/test_master_meta.py` (append)
- Create: `tests/fixtures/master_appendix_mf.txt`, `tests/fixtures/master_appendix_dep.txt`, `tests/fixtures/master_appendix_pre2015.txt`

**Interfaces:**
- Consumes: `REF_RE`, `normalize_circular_number` from `sebi_rag.ingest_pdf`; corpus record dicts (`circular_number`, `text`).
- Produces: `consolidation_edges(rec: dict) -> list[dict]` — edges `{"source": <master cn>, "target": <cn>, "relation": "consolidates", "confidence": "explicit_text", "evidence": "rescission_appendix"}`. Only emitted for records whose text contains a rescission heading; targets deduped under `normalize_circular_number`; self-references excluded. `consolidates` never affects `validity_status` (locked rule — `derive_validity` only looks at `supersedes`/`amends`).

- [ ] **Step 1: Extract real fixtures**

Pick three ingested master circulars of different departments/eras from the corpus (one Mutual Funds, one Depositories, one pre-2015 format). For each, extract the appendix region into a fixture:

```bash
cd "/Users/ianpinto/sebi_circular_sota_rag/SEBI circular RAG"
PYTHONPATH=src .venv/bin/python - <<'EOF'
import json, re
recs = [json.loads(l) for l in open("data/corpus/circulars.jsonl") if l.strip()]
masters = [r for r in recs if r.get("circular_type") == "MASTER_CIRCULAR"]
pat = re.compile(r"(rescind|superseded)", re.I)
for r in masters:
    m = pat.search(r["text"])
    if m:
        print(r["circular_number"], r["issue_date"], r["subject"][:60])
EOF
```

Choose three, then save `rec["text"][m.start()-200 : m.start()+4000]` for each into the three fixture files. Record which circular numbers each fixture cites (read the excerpt) — the test asserts on those real numbers.

- [ ] **Step 2: Write the failing tests**

```python
# append to tests/test_master_meta.py
from pathlib import Path

from sebi_rag.master_meta import consolidation_edges

FIXDIR = Path(__file__).parent / "fixtures"


def test_consolidation_edges_from_real_appendix():
    text = (FIXDIR / "master_appendix_mf.txt").read_text(encoding="utf-8")
    rec = {"circular_number": "SEBI/HO/IMD/MASTER/2024/1", "text": text}
    edges = consolidation_edges(rec)
    assert len(edges) >= 5           # a real appendix rescinds many circulars
    e = edges[0]
    assert e["source"] == "SEBI/HO/IMD/MASTER/2024/1"
    assert e["relation"] == "consolidates"
    assert e["confidence"] == "explicit_text"
    assert e["evidence"] == "rescission_appendix"
    # ADJUST at fixture-capture time: assert a specific known-cited number, e.g.
    # assert any("2023/74" in e["target"] for e in edges)
    targets = [e["target"] for e in edges]
    assert len(targets) == len(set(targets))          # deduped
    assert rec["circular_number"] not in targets      # no self-edge


def test_no_edges_without_rescission_heading():
    rec = {"circular_number": "X/1",
           "text": "This circular references SEBI/HO/MRD/2020/12 in passing. " * 20}
    assert consolidation_edges(rec) == []


def test_no_edges_for_empty_text():
    assert consolidation_edges({"circular_number": "X/1", "text": ""}) == []
```

Repeat `test_consolidation_edges_from_real_appendix` for the other two fixtures (same structure, their own known-cited numbers).

- [ ] **Step 3: Run to verify failure**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_master_meta.py -v`
Expected: FAIL — `ImportError: cannot import name 'consolidation_edges'`

- [ ] **Step 4: Implement**

```python
# append to src/sebi_rag/master_meta.py
from sebi_rag.ingest_pdf import REF_RE, normalize_circular_number

RESCISSION_HEADING = re.compile(
    r"(?:list\s+of\s+circulars?\s+(?:rescinded|superseded)"
    r"|circulars?\s+(?:rescinded|superseded)\s+(?:by|vide)\s+this\s+master"
    r"|stand[s]?\s+rescinded"
    r"|hereby\s+rescinded)", re.I)


def consolidation_edges(rec: dict) -> list[dict]:
    """Edges for circulars listed in a master circular's rescission appendix.

    Scans the text from the first rescission heading onward; every
    well-formed circular reference (REF_RE) after it is a consolidation
    target. explicit_text confidence: the appendix names the number itself.
    """
    text = rec.get("text") or ""
    m = RESCISSION_HEADING.search(text)
    if not m:
        return []
    source = rec["circular_number"]
    source_key = normalize_circular_number(source)
    seen, edges = set(), []
    for ref in REF_RE.finditer(text[m.start():]):
        n = ref.group(0)
        key = normalize_circular_number(n)
        if key == source_key or key in seen:
            continue
        seen.add(key)
        edges.append({"source": source, "target": n,
                      "relation": "consolidates",
                      "confidence": "explicit_text",
                      "evidence": "rescission_appendix"})
    return edges
```

- [ ] **Step 5: Run to verify pass, tune fixtures**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_master_meta.py -v`
Expected: all passed. If a real-fixture test finds < 5 edges, inspect the fixture — if its appendix genuinely lists fewer, lower that assertion to the true count; if `REF_RE` misses a legacy number format present in the appendix, extend `RESCISSION_HEADING`/window handling only (do NOT modify `REF_RE` in `ingest_pdf.py` — it feeds primary-number extraction; note the miss in the commit message instead).

- [ ] **Step 6: Full suite + commit**

```bash
make test   # expected: all passed
git add src/sebi_rag/master_meta.py tests/test_master_meta.py tests/fixtures/master_appendix_*.txt
git commit -m "feat(metadata): rescission-appendix parser -> consolidates edges"
```

---

### Task 7: Wire master metadata into `annotate_corpus`

**Files:**
- Modify: `src/sebi_rag/lineage.py` — `annotate_corpus()` (currently at `src/sebi_rag/lineage.py:240`)
- Modify: `tests/test_lineage.py` (append)

**Interfaces:**
- Consumes: `annotate_master_fields`, `consolidation_edges` (Tasks 5–6).
- Produces: after `make annotate`, every corpus record carries the four identity fields, and master records' `supersession_edges` include their `consolidates` edges. Summary dict gains `"masters"` and `"consolidates_edges"` counts. `validity_status` values are unchanged by this task.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_lineage.py
def test_annotate_corpus_adds_master_fields_and_consolidates_edges(tmp_path):
    import json
    from sebi_rag.lineage import annotate_corpus
    master = {
        "circular_number": "SEBI/HO/IMD/MASTER/2024/1",
        "subject": "Master Circular for Mutual Funds",
        "issue_date": "2024-06-27",
        "text": ("Chapter 1 ... This Master Circular supersedes the circulars "
                 "listed at Appendix A.\nAppendix A: List of Circulars rescinded\n"
                 "1. SEBI/HO/IMD/DF2/CIR/P/2020/175 dated September 17, 2020\n"
                 "2. SEBI/HO/IMD/IMD-I/DOF5/P/CIR/2021/553 dated April 28, 2021\n"
                 + "body " * 200),
        "source_url": "https://www.sebi.gov.in/legal/master-circulars/x_1.html",
    }
    plain = {"circular_number": "SEBI/HO/IMD/DF2/CIR/P/2020/175",
             "subject": "Product labelling", "issue_date": "2020-09-17",
             "text": "body " * 200, "source_url": ""}
    p = tmp_path / "c.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in (master, plain)) + "\n")
    summary = annotate_corpus(p)
    recs = [json.loads(l) for l in p.read_text().splitlines()]
    m = next(r for r in recs if r["circular_number"] == master["circular_number"])
    q = next(r for r in recs if r["circular_number"] == plain["circular_number"])
    assert m["is_master"] is True
    assert m["master_series"] == "Mutual Funds"
    assert m["master_edition"] == 2024
    cons = [e for e in m["supersession_edges"] if e["relation"] == "consolidates"]
    assert {e["target"] for e in cons} >= {"SEBI/HO/IMD/DF2/CIR/P/2020/175"}
    assert q["is_master"] is False
    assert summary["masters"] == 1
    assert summary["consolidates_edges"] == len(cons)
    # locked rule: consolidates never flips validity
    assert q["validity_status"] in ("current", "unknown")
```

- [ ] **Step 2: Run to verify failure**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lineage.py -k master_fields -v`
Expected: FAIL — `KeyError: 'is_master'` (or missing summary keys).

- [ ] **Step 3: Implement**

In `src/sebi_rag/lineage.py`, import at the top of the file with the other imports:

```python
from sebi_rag.master_meta import annotate_master_fields, consolidation_edges
```

In `annotate_corpus()` (line 240), after `lin = build_lineage(records)` and before the per-record loop:

```python
    master_changed = annotate_master_fields(records)
    cons_edges = []
    for r in records:
        if r.get("circular_type") == "MASTER_CIRCULAR" or classify_circular_type(
                r.get("subject")) == "MASTER_CIRCULAR":
            cons_edges += consolidation_edges(r)
    lin.edges.extend(cons_edges)
    changed = master_changed
```

(Replace the existing `changed = 0` initialization with `changed = master_changed`. The `classify_circular_type` fallback covers first-ever annotate runs where `circular_type` isn't set yet — it's already imported in this module.)

Extend the returned summary dict with:

```python
        "masters": sum(1 for r in records if r.get("is_master")),
        "consolidates_edges": len(cons_edges),
```

- [ ] **Step 4: Run to verify pass**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lineage.py tests/test_metadata.py -v`
Expected: all passed — including every pre-existing lineage/validity test (this is the locked-rules regression check).

- [ ] **Step 5: Annotate real corpus + full suite + commit**

```bash
make annotate    # summary now prints masters=~135, consolidates_edges=<n> (expect hundreds)
make test        # expected: all passed
git add src/sebi_rag/lineage.py tests/test_lineage.py data/corpus/circulars.jsonl
git commit -m "feat(lineage): wire master identity fields + consolidates edges into annotate"
```

---

### Task 8: Reindex + full local validation gate

**Files:** generated index artifacts only (`data/index/`).

**Interfaces:**
- Consumes: everything above.
- Produces: GO/NO-GO evidence for propagation. **Do not proceed to Task 9 unless every check below passes.**

- [ ] **Step 1:** `make reindex` — completes without error; note chunk count (was 34,883 before this work; will grow substantially with ~110 large PDFs).
- [ ] **Step 2:** `make test` — all passed.
- [ ] **Step 3:** `make eval-asof` — expected **13/13** (as-of golden gate; regression guard for the July-13 supersession-timing fixes).
- [ ] **Step 4:** `make verify-master OFFLINE=1` — coverage_pct **100.0**; `dist_covered` will still show the OLD dist count (dist regenerates in Task 9 — this is expected, note it).
- [ ] **Step 5:** End-to-end sanity on the real index — ask the pipeline one master-circular question:

```bash
PYTHONPATH=src .venv/bin/python - <<'EOF'
from sebi_rag.api import build_default_pipeline
p = build_default_pipeline()
r = p.query("What does the Master Circular for Mutual Funds say about nomination?")
print(r["answer"][:400]); print([c.get("circular_number") for c in r.get("citations", [])])
EOF
```
Expected: non-abstained answer citing a Mutual Funds master circular. (If `RAGPipeline`'s query API differs, check `graphify query "RAGPipeline query citations"` and adapt the driver — the acceptance criterion is the cited master circular, not the exact call shape.)
- [ ] **Step 6:** Commit index metadata/reports changes: `git add -A data/index reports && git commit -m "chore(index): reindex with full master-circular corpus"` (respect existing .gitignore — only commit what the repo already tracks).

---

### Task 9: Export datasets + push to HF Hub + dist verification

- [ ] **Step 1:** `make export-datasets` — all 6 configs regenerate under `dist/datasets/`; corpus/lineage/supersession configs now include the new records, identity fields, and consolidates edges.
- [ ] **Step 2:** `make test` — export tests (`tests/test_export_datasets.py`, `tests/test_export_integration.py`) still pass.
- [ ] **Step 3:** `make verify-master OFFLINE=1` — now `dist_covered` equals the `ingested_ok` count (dist closes the loop).
- [ ] **Step 4:** Dry-run push: `.venv/bin/python scripts/push_datasets.py` — upload plan lists 6 config dirs + README + manifest + metadata + provenance script, no errors.
- [ ] **Step 5:** Real push: `.venv/bin/python scripts/push_datasets.py --yes` — pushes to `opnsrcntrbtrian/sebi-circulars`. Also push the rebuilt index to the index repo following `docs/superpowers/plans/2026-07-12-hf-dataset-push-runbook.md` (the same runbook used on July 13 for the segment fix: `sebi-circulars-index`).
- [ ] **Step 6:** Commit dist + reports: `git add dist/datasets reports && git commit -m "feat(datasets): export + push corpus with full master-circular coverage"` (again: only what the repo already tracks).

---

### Task 10: Redeploy Space + live smoke test

- [ ] **Step 1:** `.venv/bin/python scripts/deploy_space.py --repo opnsrcntrbtrian/sebi-circular-rag-demo` — deploys app.py, src/, config, requirements.
- [ ] **Step 2:** Wait for the Space to rebuild (poll the Space page or `huggingface_hub`'s `space_info` runtime stage until RUNNING).
- [ ] **Step 3:** Live smoke test — three queries against the running Space (via `gradio_client`, same method as the July-13 Task-5 smoke test):
  1. Master-circular question: "What does the Master Circular for Mutual Funds say about nomination?" → answer cites a Mutual Funds master circular.
  2. Nominee regression: "What is the maximum number of nominees allowed in mutual fund folios?" → answer consistent with the Jan-2025 rule ("up to 10"), not "5".
  3. As-of query with As-of date 2025-01-10 → does not abstain, cites the January 2025 circular.
- [ ] **Step 4:** Record raw smoke-test output in `docs/superpowers/2026-07-XX-master-coverage-completion.md` (actual date), with the final coverage numbers from `reports/master_coverage.json`.

---

### Task 11: Docs + final report + close-out

- [ ] **Step 1:** Update `CLAUDE.md`: add `make scrape-master` and `make verify-master` to the Quick Start command list; add `verify_master.py` and `master_meta.py` rows to the Source Structure table (one line each, match existing table style).
- [ ] **Step 2:** Update `README-spaces.md` only if the Space's corpus size/blurb is stated there (it mentions corpus stats — refresh numbers).
- [ ] **Step 3:** Regenerate the knowledge graph: `graphify update .`
- [ ] **Step 4:** Final coverage statement — paste the `reports/master_coverage.md` summary table into the completion doc from Task 10 Step 4. This document is the spec's "confirms with statistical summary" deliverable.
- [ ] **Step 5:** Commit: `git add CLAUDE.md README-spaces.md docs/ graphify-out && git commit -m "docs: master-circular coverage completion report"`.
- [ ] **Step 6 (optional, user-triggered):** Minimal final review — whole-branch diff review (e.g. `/code-review` on the branch) by Fable if and only if the user asks. Not a gate; Tasks 1–11's command-level acceptance criteria are the validation of record.
