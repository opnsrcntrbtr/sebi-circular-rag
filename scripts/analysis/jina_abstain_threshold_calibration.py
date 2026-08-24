"""ADR-004 adoption: calibrate abstain_threshold for jina-reranker-v3-mlx's
score scale.

Why this is needed, not optional: bge-reranker-v2-m3's scores cluster near 1.0
for confident matches (median top-score 0.982, min 0.0001, never negative,
measured 2026-08-24 on golden_v7). jina-reranker-v3's are compressed around
0.45 (median 0.4527) and CAN be negative (5 of 260 queries in the same
cohort). `abstain_threshold=0.05` was calibrated for bge's distribution
(`docs/adr-001-architecture-review-2026-07.md` action item 7, refined by
`reports/score-floor-utility-2026-08-19.json`) — applying it unchanged to a
different reranker's scale is not a hypothesis, it is measurably wrong on its
face (Jina's own p10 is 0.1856, above 0.05, so the floor would barely fire).

Method: for every golden_v7 row, compute rerank_top EXACTLY as
`answer_with_abstention` sees it — retrieve -> jina.rerank -> demote_superseded
(0.3 penalty, matching the production non-as_of path) — then sweep candidate
thresholds and report the same trade-off `score-floor-utility` used: true
abstentions caught vs false abstentions caused. `citation_scorer` and
`citation_margin` are untouched (ADR-004's decoupling: citation scoring stays
on bge-reranker-v2-m3 regardless of which reranker orders retrieval).

Usage: PYTHONPATH=src python scripts/analysis/jina_abstain_threshold_calibration.py
"""
from __future__ import annotations

import json
import os
import sys
import time
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

GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
DEST = ROOT / "reports" / "jina-abstain-threshold-calibration-2026-08-24.json"


def main() -> None:
    from sebi_rag.embeddings import BGEM3Embedder
    from sebi_rag.eval_harness import load_golden
    from sebi_rag.lineage import build_lineage, demote_superseded, load_records
    from sebi_rag.rerank import JinaMLXReranker
    from sebi_rag.retrieve import HybridRetriever
    from sebi_rag.settings import Settings

    s = Settings.load()
    golden = load_golden(GOLDEN)
    print(f"golden set: {GOLDEN} ({len(golden)} rows)", file=sys.stderr)

    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(Path(s.index_dir), emb)
    lineage = build_lineage(load_records(s.corpus_path))
    reranker = JinaMLXReranker()
    print("models loaded", file=sys.stderr)

    rows, t0 = [], time.time()
    for n, item in enumerate(golden, 1):
        cands = retr.retrieve(item["query"], top_n=50)
        reranked = reranker.rerank(item["query"], [c for c, _ in cands])
        # Matches pipeline.py's non-as_of path exactly (superseded_penalty=0.3,
        # inferred_supersession_penalty=None — production default).
        reranked = demote_superseded(reranked, lineage, s.superseded_penalty)
        top_score = float(reranked[0][1]) if reranked else float("-inf")
        rows.append({"id": item["id"], "gold_abstain": bool(item.get("abstain")),
                     "top_score": top_score})
        if n % 50 == 0:
            print(f"  {n}/{len(golden)}  ({time.time() - t0:.0f}s)", file=sys.stderr)

    scores = sorted({round(r["top_score"], 3) for r in rows if r["top_score"] > float("-inf")})
    candidates = scores  # sweep every observed score as a candidate cut point

    curve = []
    for thr in candidates:
        abstain_rows = [r for r in rows if r["gold_abstain"]]
        answerable_rows = [r for r in rows if not r["gold_abstain"]]
        caught = sum(1 for r in abstain_rows if r["top_score"] < thr)
        false_abstain = sum(1 for r in answerable_rows if r["top_score"] < thr)
        curve.append({"thr": thr, "true_abstentions_caught": caught,
                      "n_gold_abstain": len(abstain_rows),
                      "false_abstentions": false_abstain,
                      "n_gold_answerable": len(answerable_rows)})

    # Knee: the highest threshold that catches the most true abstentions
    # while costing the FEWEST false abstentions among thresholds achieving
    # that same catch count — mirrors score-floor-utility-2026-08-19's own
    # framing (29/41 caught at a cost of 2/204) rather than picking a round
    # number.
    max_caught = max(c["true_abstentions_caught"] for c in curve)
    at_max = [c for c in curve if c["true_abstentions_caught"] == max_caught]
    knee = min(at_max, key=lambda c: (c["false_abstentions"], c["thr"]))

    out = {
        "reranker": "jinaai/jina-reranker-v3-mlx",
        "superseded_penalty": s.superseded_penalty,
        "n_rows": len(rows),
        "score_distribution": {"min": min(r["top_score"] for r in rows),
                               "max": max(r["top_score"] for r in rows)},
        "curve": curve,
        "recommended_threshold": knee["thr"],
        "recommended_at": knee,
        "current_bge_threshold_for_reference": s.abstain_threshold,
        "runtime_s": round(time.time() - t0, 1),
        "rows": rows,
    }
    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("curve", "rows")}, indent=2))
    print(f"\nwrote {DEST}", file=sys.stderr)


if __name__ == "__main__":
    main()
