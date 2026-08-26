"""SPIKE/GATE (throwaway, not preregistered) — R5's own precondition from the roadmap doc:

"Attribute the numeric_table zero-cite rows to fragmentation before paying [full re-ingest +
re-chunk + re-encode cost]. If those rows are demotion- or B'-caused, this buys nothing — and
R2/R1 would already fix them."

This does not reconstruct a fragmentation detector (table_frag_probe.py that produced the
2026-08-19 291-fragmented-chunks count was itself throwaway and no longer exists). Instead it
answers the cheaper, decisive half of the gate: for each numeric_table row that is currently
zero-cite, was the relevant document even IN the context window (ans.context_ids)?

  - In context_ids but NOT cited -> downstream of retrieval (citation selection: B', reranker
    ordering, demotion). R5 (an ingest-time fix) cannot touch this; R1/R2-class interventions
    would already have to fix it, and both are currently exhausted/rejected. Counts AGAINST R5.
  - NOT in context_ids (missing pool or missing top_k window) -> a genuine retrieval miss.
    Consistent with (not proof of) a fragmentation cause, since a table split across chunk
    boundaries is exactly the kind of thing that could push the informative fragment out of the
    retrieved window. Counts FOR investigating R5 further (not proof — still needs the actual
    fragmentation check before paying the re-ingest cost, per the roadmap's own caution against
    over-attributing without checking).

Usage: PYTHONPATH=src python scratchpad/r5_numeric_table_gate.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

for _k, _v in {
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(_k, _v)

GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
POOL, TOP_K = 50, 10


def main() -> None:
    from sebi_rag.api import build_default_pipeline
    from sebi_rag.eval_harness import _doc, load_golden

    pipe = build_default_pipeline()
    rows = [r for r in load_golden(GOLDEN) if r.get("task_type") == "numeric_table"
            and not r.get("abstain") and not r.get("as_of") and r.get("relevant_circulars")]
    print(f"numeric_table eligible rows: {len(rows)}", file=sys.stderr)

    results, t0 = [], time.time()
    for n, it in enumerate(rows, 1):
        relevant = set(it["relevant_circulars"])
        ans, _ = pipe.query(it["query"], pool=POOL, top_k=TOP_K)
        context_docs = {_doc(c) for c in ans.context_ids}
        cited_docs = {_doc(c) for c in ans.citations} if not ans.abstained else set()
        zero_cite = not (cited_docs & relevant)
        in_context = bool(context_docs & relevant)
        cand = pipe.retriever.retrieve(it["query"], top_n=POOL)
        pool_docs = {_doc(c.id) for c, _ in cand}
        in_pool = bool(pool_docs & relevant)
        results.append({
            "id": it["id"], "zero_cite": zero_cite, "abstained": bool(ans.abstained),
            "relevant_in_pool": in_pool, "relevant_in_context_window": in_context,
        })
        if n % 10 == 0:
            print(f"  {n}/{len(rows)}  ({time.time()-t0:.0f}s)", file=sys.stderr)

    zc = [r for r in results if r["zero_cite"]]
    print(f"\nnumeric_table rows: {len(results)}, zero_cite: {len(zc)}")
    for r in zc:
        cause = ("missing_from_pool" if not r["relevant_in_pool"]
                 else "in_pool_not_in_context_window" if not r["relevant_in_context_window"]
                 else "in_context_window_not_cited (B'/reranker/demotion — R5 can't fix this)")
        print(f"  {r['id']}: abstained={r['abstained']} cause={cause}")

    downstream = sum(1 for r in zc if r["relevant_in_context_window"] and not r["abstained"])
    upstream = len(zc) - downstream
    print(f"\ndownstream-of-retrieval (R5 cannot fix): {downstream}")
    print(f"upstream / retrieval-miss (R5-consistent, not proven): {upstream}")

    Path(ROOT / "reports" / "r5-numeric-table-gate-2026-08-26.json").write_text(
        json.dumps({"rows": results, "zero_cite_n": len(zc),
                    "downstream_of_retrieval": downstream, "upstream_retrieval_miss": upstream},
                   indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
