"""R7 conformal abstention calibration: generate -> calibrate -> report phases.

Spec: docs/superpowers/specs/2026-08-26-conformal-abstention-calibration-design.md.
Plan: docs/superpowers/plans/2026-08-26-conformal-abstention-calibration.md.

Calibrates the score-floor (Settings.abstain_threshold) and subject-gate
(SEBI_RAG_SUBJ_THRESHOLD) thresholds via Conformal Risk Control + leave-one-out data
reuse (src/sebi_rag/conformal.py), using FRESH per-row scores under current production
(Jina reranker, ADR-004; recalibrated abstain_threshold=0.12) -- not any prior dump,
which would predate that adoption.

Three phases, matching this repo's established cohort-script pattern:
  1. generate    -- full production pipeline over all 260 golden_v7 rows (both abstain
                     and answerable -- the gate fires on every row regardless of gold
                     label), captures rerank_top/subject_sim/abstention_reason plus the
                     ground-truth labels the calibration functions need.
  2. calibrate    -- no model loaded, pure computation. Runs calibrate_score_floor and
                     calibrate_subject_gate at alpha in {0.05, 0.10} (0.05 primary,
                     per the spec's Sec 6, fixed in advance -- not chosen after seeing
                     a result).
  3. report       -- applies the spec's Sec 6 decision rule mechanically.

Usage:
  PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase generate
  PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase calibrate
  PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase report
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
GATE = ROOT / "eval" / "golden" / "gate_v7.json"
GENERATE_DUMP = ROOT / "reports" / "conformal-calibration-generate.json"
CALIBRATE_DUMP = ROOT / "reports" / "conformal-calibration-calibrate.json"
DEST = ROOT / "reports" / "conformal-calibration-report-2026-08-26.json"

POOL, TOP_K = 50, 10
ALPHA_PRIMARY = 0.05
ALPHA_SECONDARY = 0.10
ABSTENTION_ACCURACY_EFFECT_FLOOR = 0.01  # spec Sec 6, fixed in advance


def phase_generate() -> None:
    from sebi_rag.api import build_default_pipeline
    from sebi_rag.eval_harness import _doc, _unique, load_golden

    pipe = build_default_pipeline()
    items = list(load_golden(GOLDEN))
    print(f"golden_v7 rows: {len(items)}", file=sys.stderr)

    limit = int(os.environ.get("SEBI_ROW_LIMIT", "0"))
    if limit:
        items = items[:limit]
        print(f"SEBI_ROW_LIMIT set: truncated to {len(items)} rows (smoke test)", file=sys.stderr)

    rows, t0 = [], time.time()
    for n, it in enumerate(items, 1):
        ans, _ = pipe.query(it["query"], pool=POOL, top_k=TOP_K)
        gold_abstain = bool(it.get("abstain"))
        rerank_top = ans.confidence.get("rerank_top")
        subject_sim = ans.confidence.get("subject_sim")

        if gold_abstain:
            wrong_if_answered = True  # any answer at all is wrong for a gold-abstain row
        else:
            relevant = set(it.get("relevant_circulars") or [])
            if not relevant or ans.abstained:
                # No gold citations to check against, or this row abstained (so
                # "if answered" correctness can't be assessed from what happened) --
                # conservatively exclude from the score-floor calibration set rather
                # than guess. Flagged via wrong_if_answered=None, filtered in calibrate.
                wrong_if_answered = None
            else:
                cited = _unique(_doc(c) for c in ans.citations)
                wrong_if_answered = len(set(cited) & relevant) == 0  # zero_cite

        rows.append({
            "id": it["id"], "abstain_gold": gold_abstain,
            "abstained": bool(ans.abstained),
            "abstention_reason": ans.abstention_reason,
            "rerank_top": rerank_top, "subject_sim": subject_sim,
            "wrong_if_answered": wrong_if_answered,
            "answerable": not gold_abstain,
        })
        if n % 25 == 0:
            print(f"  {n}/{len(items)}  ({time.time() - t0:.0f}s)", file=sys.stderr)

    out = {
        "n": len(rows), "runtime_s": round(time.time() - t0, 1),
        "reranker": pipe.reranker.__class__.__name__,
        "abstain_threshold": pipe.abstain_threshold,
        "rows": rows,
    }
    GENERATE_DUMP.parent.mkdir(parents=True, exist_ok=True)
    GENERATE_DUMP.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {GENERATE_DUMP} (n={out['n']}, {out['runtime_s']}s)", file=sys.stderr)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["generate", "calibrate", "report"], required=True)
    args = ap.parse_args()
    {"generate": phase_generate}[args.phase]()


if __name__ == "__main__":
    main()
