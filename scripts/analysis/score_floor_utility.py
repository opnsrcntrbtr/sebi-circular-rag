"""What does the 0.05 cross-encoder score floor actually catch?

`Settings.abstain_threshold` = 0.05 is the far-domain score floor: if the top
reranked chunk scores below it, `answer_with_abstention` returns
`score_floor` before the subject-sim judge is ever consulted.

This measures the floor's utility over the whole of golden_v7 by computing
`rerank_top` exactly as production does (retrieve -> rerank -> supersession
demotion) and crossing it with each row's `abstain` label:

  true_positive   abstain=True  and rerank_top < floor  -> floor earns its keep
  false_abstention abstain=False and rerank_top < floor -> floor costs an answer
  (rows at or above the floor are decided by the downstream gates, not here)

Generation is never invoked — only the gate signal is needed, so this runs in
minutes rather than the ~38 min of a full eval.

Read-only. Usage: PYTHONPATH=src python scripts/analysis/score_floor_utility.py
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

from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.lineage import build_lineage, demote_superseded, load_records  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.settings import Settings  # noqa: E402

DEST = ROOT / "reports" / "score-floor-utility-2026-08-19.json"
POOL = 50


def main() -> None:
    s = Settings.load()
    floor = s.abstain_threshold
    print(f"score floor (Settings.abstain_threshold) = {floor}", file=sys.stderr)
    recs = load_records(s.corpus_path)
    lin = build_lineage(recs)
    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(s.index_dir, emb)
    rer = CrossEncoderReranker(device="mps")

    golden = load_golden(ROOT / "eval" / "golden" / "golden_v7.jsonl")
    rows = []
    t0 = time.time()
    for i, item in enumerate(golden, 1):
        # as_of rows take a different branch in pipeline.query; excluded so the
        # signal is comparable across the cohort.
        if item.get("as_of"):
            continue
        q = item["query"]
        cand = retr.retrieve(q, top_n=POOL)
        reranked = rer.rerank(q, [c for c, _ in cand])
        reranked = demote_superseded(reranked, lin, s.superseded_penalty)
        top = float(reranked[0][1]) if reranked else 0.0
        rows.append({
            "id": item["id"],
            "abstain": bool(item.get("abstain", False)),
            "rerank_top": round(top, 4),
            "below_floor": bool(top < floor),
        })
        if i % 25 == 0:
            print(f"  {i}/{len(golden)}  ({time.time() - t0:.0f}s)", file=sys.stderr)

    tp = [r for r in rows if r["abstain"] and r["below_floor"]]
    fa = [r for r in rows if not r["abstain"] and r["below_floor"]]
    abstain_rows = [r for r in rows if r["abstain"]]
    answerable = [r for r in rows if not r["abstain"]]

    summary = {
        "floor": floor,
        "n_scored": len(rows),
        "n_abstain_rows": len(abstain_rows),
        "n_answerable_rows": len(answerable),
        "true_positive": len(tp),
        "false_abstention": len(fa),
        "true_positive_ids": [r["id"] for r in tp],
        "false_abstention_ids": [r["id"] for r in fa],
    }
    print("\n=== score floor utility ===")
    print(json.dumps(summary, indent=2))
    print("\nrerank_top of abstain=True rows, ascending (first 15):")
    for r in sorted(abstain_rows, key=lambda r: r["rerank_top"])[:15]:
        print(f"  {r['id']:16s} {r['rerank_top']:.4f}"
              f"{'  <- below floor' if r['below_floor'] else ''}")

    DEST.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2),
                    encoding="utf-8")
    print(f"\nwrote {DEST}", file=sys.stderr)


if __name__ == "__main__":
    main()
