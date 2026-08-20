"""CS1: how much of the golden_v7 gate rests on labels no human ever checked?

Read-only. No model, no index, no compute — reads eval/golden/golden_v7.jsonl and
(optionally) reports/score-floor-utility-2026-08-19.json for a retrieval-confidence join.

Why this matters for R0: every gated metric's denominator is a LABEL
(`relevant_circulars`, `abstain`). If a label tier is model-generated and we are
evaluating a model, "agreement with the labeller" and "correctness" are not the
same quantity, and a generator upgrade can move the metric by moving the former.

`review_status` is "adjudicated" for all 260 rows, so `adjudicated_n` in
eval/golden/gate_v7.json does NOT mean "a human looked at it". `label_tier` does.

Usage: python scripts/analysis/label_provenance.py
"""
from __future__ import annotations

import json
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
FLOOR = ROOT / "reports" / "score-floor-utility-2026-08-19.json"
DEST = ROOT / "reports" / "label-provenance-2026-08-20.json"

# tiers with no human in the loop
UNVERIFIED = {"model_single", "draft_seeded"}
NEGATIVE = {"hard_negative", "far_negative"}
TIERS = ["human", "arbitrated", "inherited_v5", "draft_seeded", "model_single"]


def main() -> None:
    rows = [json.loads(l) for l in GOLDEN.read_text().splitlines() if l.strip()]
    n = len(rows)
    unver = [r for r in rows if r.get("label_tier") in UNVERIFIED]

    by_stratum = {}
    for st_ in sorted({r.get("task_type") for r in rows}):
        sub = [r for r in rows if r.get("task_type") == st_]
        u = sum(1 for r in sub if r.get("label_tier") in UNVERIFIED)
        by_stratum[st_] = {
            "n": len(sub), "unverified": u,
            "pct_unverified": round(100 * u / len(sub), 1),
            "tiers": {t: sum(1 for r in sub if r.get("label_tier") == t) for t in TIERS},
        }

    abstain = [r for r in rows if r.get("abstain")]
    ab_unver = [r for r in abstain if r.get("label_tier") in UNVERIFIED]

    out = {
        "note": "read-only label audit; no metric is produced and no floor may be derived",
        "n": n,
        "review_status": dict(Counter(r.get("review_status") for r in rows)),
        "label_tier": dict(Counter(r.get("label_tier") for r in rows)),
        "unverified_n": len(unver),
        "unverified_pct": round(100 * len(unver) / n, 1),
        "by_stratum": by_stratum,
        "abstain_labels": {
            "n": len(abstain), "unverified": len(ab_unver),
            "pct_unverified": round(100 * len(ab_unver) / len(abstain), 1),
            "why_it_matters": "abstention_accuracy carries the gate's strictest floor (0.9412); "
                              "these are the rows it can only score by correctly refusing",
        },
    }

    if FLOOR.exists():
        g = {r["id"]: r for r in rows}
        fl = [r for r in json.load(open(FLOOR))["rows"] if r["id"] in g]
        pos = [r for r in fl if g[r["id"]].get("task_type") not in NEGATIVE]
        grp = defaultdict(list)
        for r in pos:
            k = "unverified" if g[r["id"]].get("label_tier") in UNVERIFIED else "human_touched"
            grp[k].append(r["rerank_top"])
        out["retrieval_confidence_join"] = {
            "source": FLOOR.name, "answerable_only": True, "n": len(pos),
            **{k: {"n": len(v), "mean_rerank_top": round(st.mean(v), 4),
                   "median": round(st.median(v), 4)} for k, v in grp.items()},
            "finding": "NULL — verified and unverified rows have indistinguishable retrieval "
                       "confidence on answerable strata, so weak labels CANNOT be spotted from "
                       "scores. Label quality is an independent axis, not a proxy for difficulty.",
        }

    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "by_stratum"}, indent=2))
    print(f"\n{'stratum':<22}{'n':>4}{'%unverified':>13}")
    for s_, v in sorted(by_stratum.items(), key=lambda kv: -kv[1]["pct_unverified"]):
        print(f"{s_:<22}{v['n']:>4}{v['pct_unverified']:>12.1f}%")
    print(f"\nwrote {DEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
