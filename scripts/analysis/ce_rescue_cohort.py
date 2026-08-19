"""Preregistered cohort measurement for the CE paraphrase rescue.

Spec: `docs/superpowers/specs/2026-08-19-ce-paraphrase-rescue-prereg.md` §4.

Cohort: the 31 non-as-of golden_v7 rows whose production `rerank_top` falls
below the 0.05 score floor, fixed in `reports/score-floor-utility-2026-08-19.json`
BEFORE the rewriter existed — 2 answerable (the targets) and 29 correctly
abstaining (the guardrail).

Endpoints reported:
  PRIMARY   rescued            of 2, lifted to >= floor with a chunk from the
                               relevant circular as argmax
  GUARDRAIL false_positive     of 29, lifted to >= floor
  SECONDARY rewrite_degenerate rewrites rejected as empty/unchanged/overlong
  COST      rescue_latency_ms  median added latency where the rescue fires

Read-only with respect to production config: constructs the rewriter directly
rather than reading `paraphrase_rescue`, so the flag stays off while measuring.

Usage: PYTHONPATH=src python scripts/analysis/ce_rescue_cohort.py
"""
from __future__ import annotations

import json
import os
import statistics
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
from sebi_rag.paraphrase_rescue import MLXQueryRewriter, is_degenerate  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.settings import Settings  # noqa: E402

COHORT = ROOT / "reports" / "score-floor-utility-2026-08-19.json"
DEST = ROOT / "reports" / "ce-rescue-cohort-2026-08-19.json"
POOL = 50


def main() -> None:
    s = Settings.load()
    floor = s.abstain_threshold
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    below = [r for r in cohort["rows"] if r["below_floor"]]
    targets = {r["id"] for r in below if not r["abstain"]}
    guards = {r["id"] for r in below if r["abstain"]}
    print(f"floor={floor}  cohort={len(below)}  "
          f"targets={len(targets)}  guardrail={len(guards)}", file=sys.stderr)

    recs = load_records(s.corpus_path)
    lin = build_lineage(recs)
    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(s.index_dir, emb)
    rer = CrossEncoderReranker(device="mps")
    rewriter = MLXQueryRewriter(model=s.mlx_model)

    golden = {r["id"]: r for r in
              load_golden(ROOT / "eval" / "golden" / "golden_v7.jsonl")}

    rows, latencies = [], []
    for rid in [r["id"] for r in below]:
        item = golden[rid]
        q = item["query"]
        rel = set(item.get("relevant_circulars") or [])

        cand = retr.retrieve(q, top_n=POOL)
        pool_chunks = [c for c, _ in cand]
        reranked = demote_superseded(rer.rerank(q, pool_chunks), lin,
                                     s.superseded_penalty)

        t0 = time.time()
        rewritten = rewriter.rewrite(q, [c for c, _ in reranked])
        degenerate = is_degenerate(q, rewritten)
        new_top, argmax_rel = None, False
        if not degenerate:
            alt = demote_superseded(rer.rerank(str(rewritten).strip(), pool_chunks),
                                    lin, s.superseded_penalty)
            new_top = float(alt[0][1])
            argmax_rel = alt[0][0].doc_id in rel
        latencies.append((time.time() - t0) * 1000)

        opened = bool(new_top is not None and new_top >= floor)
        rows.append({
            "id": rid,
            "is_target": rid in targets,
            "query": q,
            "rewritten": rewritten,
            "degenerate": degenerate,
            "rerank_top_before": round(float(reranked[0][1]), 4),
            "rerank_top_after": None if new_top is None else round(new_top, 4),
            "gate_opens": opened,
            "argmax_is_relevant": argmax_rel,
            "rescued": bool(opened and argmax_rel and rid in targets),
            "false_positive": bool(opened and rid in guards),
        })
        tag = ("TARGET " if rid in targets else "guard  ")
        print(f"{tag}{rid:16s} {rows[-1]['rerank_top_before']:.4f} -> "
              f"{'DEGEN' if degenerate else f'{new_top:.4f}'}"
              f"{'  OPENS' if opened else ''}"
              f"{'  [RESCUED]' if rows[-1]['rescued'] else ''}"
              f"{'  [FALSE POSITIVE]' if rows[-1]['false_positive'] else ''}")
        if not degenerate:
            print(f"        rewrite: {rewritten}")

    fired = [r for r in rows if not r["degenerate"]]
    summary = {
        "floor": floor,
        "cohort_n": len(rows),
        "n_targets": len(targets),
        "n_guardrail": len(guards),
        "rescued": sum(r["rescued"] for r in rows),
        "false_positive": sum(r["false_positive"] for r in rows),
        "rewrite_degenerate": sum(r["degenerate"] for r in rows),
        "rewrite_degenerate_pct": round(
            100.0 * sum(r["degenerate"] for r in rows) / max(len(rows), 1), 1),
        "rescue_latency_ms_median": round(statistics.median(latencies), 1),
        "rescued_ids": [r["id"] for r in rows if r["rescued"]],
        "false_positive_ids": [r["id"] for r in rows if r["false_positive"]],
        "fired_n": len(fired),
    }
    print("\n=== PREREG §4 ENDPOINTS ===")
    print(json.dumps(summary, indent=2))
    print("\n=== §6 DECISION ===")
    if summary["false_positive"] > 0:
        print("REJECT — guardrail breached (rule 1: zero false positives).")
    elif summary["rewrite_degenerate_pct"] >= 50:
        print("INCONCLUSIVE — rewriter too small (rule 3), not a null result.")
    elif summary["rescued"] == summary["n_targets"]:
        print("PROCEED to §7 full-eval confirmation (rules 1+2 met).")
    else:
        print(f"REJECT — rescued {summary['rescued']} of {summary['n_targets']} "
              "(rule 2 requires all).")

    DEST.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2),
                    encoding="utf-8")
    print(f"\nwrote {DEST}", file=sys.stderr)


if __name__ == "__main__":
    main()
