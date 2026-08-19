"""Probe: does query-side reformulation lift the CE score on the 4 CE_MISMATCH rows?

Hypothesis under test (H): the 4 `para-*` false abstentions are a cross-encoder
*recognition* failure driven by lay-term paraphrase — every domain term in the
query is substituted for a lay synonym ("short-term bank loan" for "intraday
borrowing"), leaving no surface anchor for bge-reranker-v2-m3. If so, rescoring
the SAME pool with a domain-vocabulary query should lift ce_top above the 0.42
gate without changing retrieval at all.

Read-only, index-free: replays the pool captured in
`reports/ce-mismatch-investigate-2026-08-18.json` and rescores it with the
production cross-encoder under four query variants:

  orig    - the golden_v7 query verbatim (control; must reproduce ce_top)
  reform  - hand-written domain-vocabulary rewrite of the same question
  title   - the relevant circular's subject line (ceiling estimate)
  subq    - max over decomposed single-intent sub-questions

Reports, per variant: ce_top over the pool, best CE score on a relevant chunk,
and whether the 0.42 score floor would open.

Usage: PYTHONPATH=src python scripts/analysis/ce_query_reform_probe.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

for _k, _v in {
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(_k, _v)

from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402

GATE = 0.42
SRC = ROOT / "reports" / "ce-mismatch-investigate-2026-08-18.json"
DEST = ROOT / "reports" / "ce-query-reform-probe-2026-08-19.json"

# Hand-written variants. `reform` uses the vocabulary a SEBI drafter would use;
# `title` is the circular's own subject line; `subq` splits compound questions.
VARIANTS: dict[str, dict[str, object]] = {
    "para-mfmaster": {
        "reform": "Master Circular for Mutual Funds consolidating all circulars "
                  "applicable to asset management companies",
        "title": "Master Circular for Mutual Funds",
        "subq": [
            "Which Master Circular applies to mutual funds and AMCs?",
            "Does a single compilation supersede prior mutual fund circulars?",
        ],
    },
    "para-glitch": {
        "reform": "framework to address technical glitches in stock brokers' "
                  "electronic trading systems and its applicability to small brokers",
        "title": "Review of Framework to address the 'technical glitches' in "
                 "Stock Brokers' Electronic Trading Systems",
        "subq": [
            "What must a stock broker do when a technical glitch occurs in its "
            "electronic trading system?",
            "Are small stock brokers exempt from the technical glitch framework?",
        ],
    },
    "para-mfborrow": {
        "reform": "intraday borrowing by mutual funds to meet redemption payout "
                  "settlement mismatch",
        "title": "Borrowing by Mutual Funds - Intraday Borrowings",
        "subq": [
            "Can a mutual fund borrow intraday to meet redemption payouts?",
            "What is the limit on intraday borrowing by mutual fund schemes?",
        ],
    },
    "para-pricedata": {
        "reform": "norms for sharing and usage of price data for educational "
                  "purposes by unregulated entities, and the applicable delay period",
        "title": "Norms for sharing and usage of price data for educational purposes",
        "subq": [
            "What delay applies to price data shared for educational purposes?",
            "Can an entity not registered with SEBI use exchange price data to "
            "teach?",
        ],
    },
}


def _pool(row: dict) -> list[dict]:
    """Top-8 pool plus every relevant chunk, de-duplicated on chunk_id."""
    seen: dict[str, dict] = {}
    for c in row["top_pool"]:
        seen.setdefault(c["chunk_id"], {"chunk_id": c["chunk_id"],
                                        "text": c["text"],
                                        "is_relevant": c["is_relevant"]})
    for c in row["relevant_in_pool"]:
        seen.setdefault(c["chunk_id"], {"chunk_id": c["chunk_id"],
                                        "text": c["text"],
                                        "is_relevant": True})
    return list(seen.values())


def _score(ce, query: str, pool: list[dict]) -> tuple[float, float, str]:
    """Return (ce_top, best relevant score, chunk_id of argmax)."""
    scores = ce._ce.predict([[query, c["text"]] for c in pool], batch_size=32)
    scores = [float(s) for s in scores]
    top_i = max(range(len(pool)), key=lambda i: scores[i])
    rel = [s for c, s in zip(pool, scores) if c["is_relevant"]]
    return scores[top_i], (max(rel) if rel else float("nan")), pool[top_i]["chunk_id"]


def main() -> None:
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    print("loading bge-reranker-v2-m3 on mps ...", file=sys.stderr)
    ce = CrossEncoderReranker(device="mps")

    out = []
    for row in rows:
        rid = row["id"]
        pool = _pool(row)
        v = VARIANTS[rid]
        queries: dict[str, list[str]] = {
            "orig": [row["query"]],
            "reform": [str(v["reform"])],
            "title": [str(v["title"])],
            "subq": list(v["subq"]),  # type: ignore[arg-type]
        }

        entry = {"id": rid, "query": row["query"], "pool_n": len(pool),
                 "recorded_ce_top": row["ce_top"], "variants": {}}
        print(f"\n=== {rid}  (pool n={len(pool)}, recorded ce_top={row['ce_top']})")
        print(f"    Q: {row['query']}")
        for name, qs in queries.items():
            results = [_score(ce, q, pool) for q in qs]
            ce_top = max(r[0] for r in results)
            rel_best = max(r[1] for r in results)
            argmax_id = max(results, key=lambda r: r[0])[2]
            entry["variants"][name] = {
                "queries": qs,
                "ce_top": round(ce_top, 4),
                "ce_relevant_best": round(rel_best, 4),
                "gate_opens": bool(ce_top >= GATE),
                "argmax_is_relevant": bool(
                    next(c["is_relevant"] for c in pool if c["chunk_id"] == argmax_id)
                ),
            }
            flag = "OPENS" if ce_top >= GATE else "shut "
            print(f"    {name:7s} ce_top={ce_top:.4f} rel_best={rel_best:.4f} "
                  f"[{flag}] argmax_relevant="
                  f"{entry['variants'][name]['argmax_is_relevant']}")
        out.append(entry)

    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {DEST}", file=sys.stderr)


if __name__ == "__main__":
    main()
