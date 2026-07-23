"""Deterministic candidate mining for golden_v7 drafting (spec Sec 4, Sec 5).

Pure functions + a main() that writes one JSONL per stratum under
eval/golden/v7_annotations/candidates/. Seed 20260723. Oversamples 2x.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.corpus import load_circulars  # noqa: E402
from sebi_rag.lineage import load_records  # noqa: E402

NUMERIC_RE = re.compile(
    r"(?i)(\bannexure\b|\bper cent\b|\d+\s*%|\blakh\b|\bcrore\b|"
    r"within\s+\d+\s+(?:calendar\s+|working\s+)?days)")

# Near-domain topics with no governing document in the 705-circular corpus.
# Drafting batch 6E confirms absence via the top_hits the sweep attaches.
HARD_NEGATIVE_TOPICS = [
    "RBI prudential norms for NBFC gold loans",
    "IRDAI motor insurance premium filing",
    "MCA board meeting frequency for private companies",
    "Income tax TDS rates on dividend income",
    "SEBI requirements for crypto asset custodians",
    "FEMA overseas direct investment reporting by individuals",
    "Bank locker agreement stamp duty",
    "GST e-invoicing turnover threshold",
    "PFRDA NPS partial withdrawal rules",
    "Competition Commission merger notification thresholds",
    # drafting expands variations from these seeds to reach 30 rows
]
FAR_NEGATIVE_TOPICS = [
    "best sourdough fermentation schedule", "monsoon trekking routes in Sahyadris",
    "python asyncio event loop internals", "history of the Deccan sultanates",
    "cricket LBW review protocol", "EV battery thermal runaway chemistry",
    "Himalayan glacier mass balance measurement", "opera seria vocal ornamentation",
    "sous vide steak temperatures",
]


def _body(chunk_text: str) -> str:
    lines = chunk_text.split("\n", 1)
    return lines[1] if len(lines) > 1 else lines[0]


def sample_title_direct(records, n, rng):
    buckets: dict[tuple[str, str], list[dict]] = {}
    for r in records:
        key = ((r.get("issue_date") or "")[:4], r.get("issuing_department", ""))
        buckets.setdefault(key, []).append(r)
    for b in buckets.values():
        rng.shuffle(b)
    order = sorted(buckets)
    out, i = [], 0
    while len(out) < n and any(buckets[k] for k in order):
        key = order[i % len(order)]
        if buckets[key]:
            r = buckets[key].pop()
            out.append({"circular_number": r["circular_number"],
                        "subject": r.get("subject", ""),
                        "issue_date": r.get("issue_date", "")})
        i += 1
    return out


def sample_paraphrase_chunks(chunks, n, rng):
    pool = [c for c in chunks
            if "#preamble#" not in c.id and len(_body(c.text)) >= 300]
    rng.shuffle(pool)
    return [{"chunk_id": c.id, "doc": c.doc_id,
             "subject": (c.meta or {}).get("subject", ""), "text": _body(c.text)}
            for c in pool[:n]]


def mine_numeric(chunks, n, rng):
    pool = [c for c in chunks
            if "#preamble#" not in c.id and NUMERIC_RE.search(_body(c.text))]
    rng.shuffle(pool)
    return [{"chunk_id": c.id, "doc": c.doc_id,
             "subject": (c.meta or {}).get("subject", ""), "text": _body(c.text)}
            for c in pool[:n]]


def _mid(d1: str, d2: str) -> str:
    a, b = date.fromisoformat(d1), date.fromisoformat(d2)
    return (a + (b - a) / 2).isoformat()


def mine_lineage_pairs(superseded_by, records_by_id, n, rng):
    pairs = []
    for old, news in sorted(superseded_by.items()):
        for new in news:
            ro, rn = records_by_id.get(old), records_by_id.get(new)
            if not (ro and rn and ro.get("issue_date") and rn.get("issue_date")):
                continue
            if ro["issue_date"] >= rn["issue_date"]:
                continue
            pairs.append({
                "old": old, "new": new,
                "old_date": ro["issue_date"], "new_date": rn["issue_date"],
                "as_of_mid": _mid(ro["issue_date"], rn["issue_date"]),
                "as_of_before": (date.fromisoformat(ro["issue_date"])
                                 - timedelta(days=30)).isoformat(),
            })
    rng.shuffle(pairs)
    return pairs[:n]


def mine_multi_hop(edges, records_by_id, n, rng):
    """Pairs joined by a lineage reference edge (supersedes/amends), both ends
    in-corpus. Verified against the real data/index/lineage.json: edges are
    {"source", "target", "relation", ...} dicts where relation is always
    "supersedes" or "amends" (no separate generic "reference" relation) —
    matching the design doc's "reference edges (lineage edges)" wording for
    the multi_hop stratum.
    """
    pairs = []
    for e in edges:
        a, b = e.get("source"), e.get("target")
        if a and b and a != b and a in records_by_id and b in records_by_id:
            pairs.append({"a": a, "b": b,
                          "subject_a": records_by_id[a].get("subject", ""),
                          "subject_b": records_by_id[b].get("subject", "")})
    rng.shuffle(pairs)
    return pairs[:n]


def mine_repealed_basis(records, n, rng):
    pool = [r for r in records
            if r.get("regulatory_basis_status") == "repealed_basis"]
    rng.shuffle(pool)
    return [{"circular_number": r["circular_number"],
             "subject": r.get("subject", ""),
             "regulations": r.get("regulations", [])} for r in pool[:n]]


def verify_negative_absence(records, topics):
    import bm25s
    texts = [(r.get("subject", "") + " " + r.get("text", ""))[:5000] for r in records]
    bm = bm25s.BM25()
    bm.index(bm25s.tokenize(texts, stopwords="en", show_progress=False),
             show_progress=False)
    out = []
    for t in topics:
        res, _ = bm.retrieve(bm25s.tokenize(t, stopwords="en", show_progress=False),
                             k=3, show_progress=False)
        out.append({"topic": t, "top_hits": [
            {"doc": records[int(i)]["circular_number"],
             "subject": records[int(i)].get("subject", "")} for i in res[0]]})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(ROOT / "data" / "corpus" / "circulars.jsonl"))
    ap.add_argument("--lineage", default=str(ROOT / "data" / "index" / "lineage.json"))
    ap.add_argument("--out", default=str(ROOT / "eval" / "golden" / "v7_annotations" / "candidates"))
    args = ap.parse_args()
    rng = random.Random(20260723)
    records = load_records(args.corpus)
    by_id = {r["circular_number"]: r for r in records}
    chunks = load_circulars(args.corpus)
    lin = json.loads(Path(args.lineage).read_text(encoding="utf-8"))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    def write(name, rows):
        with (out / f"{name}.jsonl").open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"{name}: {len(rows)} candidates")

    write("title_direct", sample_title_direct(records, 20, rng))
    write("body_paraphrase", sample_paraphrase_chunks(chunks, 90, rng))
    write("numeric_table", mine_numeric(chunks, 60, rng))
    write("lineage_supersession", mine_lineage_pairs(lin.get("superseded_by", {}), by_id, 80, rng))
    write("multi_hop", mine_multi_hop(lin.get("edges", []), by_id, 40, rng))
    write("repealed_basis", mine_repealed_basis(records, 40, rng))
    write("hard_negative", verify_negative_absence(records, HARD_NEGATIVE_TOPICS))
    write("far_negative", [{"topic": t} for t in FAR_NEGATIVE_TOPICS])


if __name__ == "__main__":
    main()
