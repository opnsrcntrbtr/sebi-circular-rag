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
