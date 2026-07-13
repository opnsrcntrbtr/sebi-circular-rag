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
