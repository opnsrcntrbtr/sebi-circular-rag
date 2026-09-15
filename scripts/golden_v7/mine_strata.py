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

# Same pattern as scripts/finetune/synthesize_queries.py's BOILERPLATE_RE/_has_boilerplate
# (measured there: up to 11.5% of multi_hop, 2.1% of lineage_supersession, 1.3% of
# numeric_table candidates matched). golden-set-power expansion (2026-09-15): the first
# drafting sample surfaced the same failure here - a chunk matching NUMERIC_RE only via
# its "Annexure-A" mention, trailing into a signature block ("Yours faithfully... Page 2
# of 4"), got a boilerplate page-footer number drafted as its "numeric answer" instead of
# a substantive figure. Duplicated rather than imported to keep this script standalone,
# matching its existing no-cross-script-import style.
BOILERPLATE_RE = re.compile(
    r"Yours (faithfully|sincerely)|available on (the )?SEBI website", re.IGNORECASE)


def _has_boilerplate(text: str) -> bool:
    return bool(BOILERPLATE_RE.search(text))

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
    # golden-set-power expansion (2026-09-15, docs/superpowers/specs/2026-09-01-golden-set-power.md):
    # 3 new seeds, same near-domain-but-ungoverned pattern, user-approved before mining.
    "RERA project registration extension grounds",
    "EPFO employer contribution default penalty provisions",
    "CBIC customs valuation rules for related-party imports",
]
FAR_NEGATIVE_TOPICS = [
    "best sourdough fermentation schedule", "monsoon trekking routes in Sahyadris",
    "python asyncio event loop internals", "history of the Deccan sultanates",
    "cricket LBW review protocol", "EV battery thermal runaway chemistry",
    "Himalayan glacier mass balance measurement", "opera seria vocal ornamentation",
    "sous vide steak temperatures",
    # golden-set-power expansion (2026-09-15): 4 new seeds, same unrelated-domain
    # pattern, added for headroom/diversity though the count already met target.
    "medieval European guild trade regulations", "coral reef bleaching recovery timelines",
    "jazz improvisation modal theory", "Rust borrow-checker lifetime elision rules",
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


# golden-set-power expansion (2026-09-15): readability filter, added after the first
# expansion mining pass surfaced shredded-table chunks in numeric_table candidates (e.g.
# "Number of 100 100 / units 32.92" - table-row text broken across many short fragment
# lines, the same shredding failure the 2026-09-01/02/03 chunker fixes target). A chunk
# that reads as mostly short numeric/whitespace fragments makes an unreliable basis for
# an LLM-drafted question - the answer itself may be garbled. Calibrated against the
# 140-candidate 2026-09-15 numeric_table mining pass: median fragment ratio 0.083, only
# 2/140 exceeded 0.5 (the visibly-bad cases); threshold 0.3 catches 11/140 (~8%) without
# being aggressive on ordinary prose.
def _is_readable(text: str, max_short_line_ratio: float = 0.3, min_lines: int = 5) -> bool:
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if len(lines) < min_lines:
        # Too few lines for the ratio to be meaningful - e.g. a "1. Heading:" line
        # followed by one paragraph is 2 lines and looks 50% "short" by pure ratio,
        # but is ordinary prose, not shredding (which needs many fragment lines to
        # manifest at all). Caught the false-positive via test_golden_v7_mine.py's
        # existing 2-line fixtures.
        return True
    short = sum(1 for ln in lines if len(ln) <= 12)
    return (short / len(lines)) <= max_short_line_ratio


def sample_paraphrase_chunks(chunks, n, rng):
    pool = [c for c in chunks
            if "#preamble#" not in c.id and len(_body(c.text)) >= 300
            and _is_readable(_body(c.text)) and not _has_boilerplate(_body(c.text))]
    rng.shuffle(pool)
    return [{"chunk_id": c.id, "doc": c.doc_id,
             "subject": (c.meta or {}).get("subject", ""), "text": _body(c.text)}
            for c in pool[:n]]


def mine_numeric(chunks, n, rng):
    pool = [c for c in chunks
            if "#preamble#" not in c.id and NUMERIC_RE.search(_body(c.text))
            and _is_readable(_body(c.text)) and not _has_boilerplate(_body(c.text))]
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
    # Per-stratum candidate counts (pre-adjudication, ~2x oversampled). Defaults reproduce the
    # original golden_v7 mining pass exactly; pass overrides for a targeted expansion instead of
    # editing these defaults in place, so a bare re-run stays reproducible.
    # golden-set-power expansion (2026-09-15, docs/superpowers/specs/2026-09-01-golden-set-power.md
    # + the approved plan in .claude/plans/ultra-synchronous-pony.md): invoke with
    # --n-title-direct 60 --n-body-paraphrase 120 --n-numeric-table 140
    # --n-lineage-supersession 160 --n-multi-hop 60 --n-repealed-basis 50
    ap.add_argument("--n-title-direct", type=int, default=20)
    ap.add_argument("--n-body-paraphrase", type=int, default=90)
    ap.add_argument("--n-numeric-table", type=int, default=60)
    ap.add_argument("--n-lineage-supersession", type=int, default=80)
    ap.add_argument("--n-multi-hop", type=int, default=40)
    ap.add_argument("--n-repealed-basis", type=int, default=40)
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

    write("title_direct", sample_title_direct(records, args.n_title_direct, rng))
    write("body_paraphrase", sample_paraphrase_chunks(chunks, args.n_body_paraphrase, rng))
    write("numeric_table", mine_numeric(chunks, args.n_numeric_table, rng))
    write("lineage_supersession",
          mine_lineage_pairs(lin.get("superseded_by", {}), by_id, args.n_lineage_supersession, rng))
    write("multi_hop", mine_multi_hop(lin.get("edges", []), by_id, args.n_multi_hop, rng))
    write("repealed_basis", mine_repealed_basis(records, args.n_repealed_basis, rng))
    write("hard_negative", verify_negative_absence(records, HARD_NEGATIVE_TOPICS))
    write("far_negative", [{"topic": t} for t in FAR_NEGATIVE_TOPICS])


if __name__ == "__main__":
    main()
