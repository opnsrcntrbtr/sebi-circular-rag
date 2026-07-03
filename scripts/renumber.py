"""Re-derive circular number + dates from each record's stored text and rewrite
the corpus. Use after improving the ingest_pdf parser, to fix existing records
without re-downloading/re-parsing PDFs. Then run `make reindex`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sebi_rag.ingest_pdf import parse_meta  # noqa: E402

CORPUS = Path(__file__).resolve().parents[1] / "data" / "corpus" / "circulars.jsonl"
recs = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line.strip()]

changed = 0
for r in recs:
    m = parse_meta(r["text"])
    if m["circular_number"] and m["circular_number"] != r.get("circular_number"):
        print(f"  {r['circular_number']} -> {m['circular_number']}", flush=True)
        r["circular_number"] = m["circular_number"]
        r["issue_date"] = m["issue_date"]
        r["effective_date"] = m["effective_date"]
        changed += 1

CORPUS.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in recs) + "\n",
                  encoding="utf-8")
print(f"updated {changed} records. Next: make reindex", flush=True)
