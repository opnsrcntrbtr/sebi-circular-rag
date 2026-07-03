"""Emit one JSON line listing SEBI circulars newer than previously seen. Uses a
state file of seen document ids (data/seen_circular_ids.txt), seeded on first run
from the corpus + current listing so it never floods on the first invocation.
No downloads; discovery logging is suppressed so stdout is pure JSON.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import scrape_sebi as S  # noqa: E402
from sebi_rag.lineage import load_records  # noqa: E402
from sebi_rag.settings import Settings  # noqa: E402

STATE = ROOT / "data" / "seen_circular_ids.txt"


def docid(u: str) -> str:
    m = re.search(r"_(\d+)\.html", u or "")
    return m.group(1) if m else ""


def title(u: str) -> str:
    seg = u.rsplit("/", 1)[-1].rsplit("_", 1)[0].replace("-", " ").strip()
    return seg[:110]


s = Settings.load()
recs = load_records(s.corpus_path)
first_run = not STATE.exists()
seen = set(filter(None, STATE.read_text().split())) if STATE.exists() else set()
if first_run:
    seen |= {docid(r.get("source_url", "")) for r in recs}   # seed from corpus
seen.discard("")

with contextlib.redirect_stdout(io.StringIO()):
    urls = S.discover("circulars", 40, 3.0)                  # newest ~40, no download
    urls += S.discover("master-circulars", 15, 3.0)          # masters drive supersession

new = [] if first_run else [u for u in urls if docid(u) not in seen]
STATE.write_text("\n".join(sorted(seen | {docid(u) for u in urls} - {""})))

print(json.dumps({
    "seeded": first_run,
    "checked": len(urls),
    "new_count": len(new),
    "items": [{"title": title(u), "url": u} for u in new[:20]],
}))
