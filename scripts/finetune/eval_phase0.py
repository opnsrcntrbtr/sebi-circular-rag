"""Phase A eval (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-
research-bright-dawn.md): the only measurement that decides Phase 0.

bench_retrieval.py already produces control/treatment runs and an
aggregate metrics file, but the plan's gate reads PER-STRATUM deltas
(numeric_table/multi_hop/lineage_supersession specifically, not aggregate
recall@10) AND per held-out/in-corpus/mixed subset (Decision #8's
contamination policy) - neither breakdown exists in bench_retrieval.py's
own output, so this script builds them from its run.doc.trec files.

Reuses recall_at_k/ndcg_at_k from src/sebi_rag/eval.py verbatim - the
plan's own stated metric source - rather than recomputing scoring logic.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/finetune/eval_phase0.py \
        --control eval/runs/ft-phase0-control/run.doc.trec \
        --treatment eval/runs/ft-phase0-treatment/run.doc.trec
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.eval import ndcg_at_k, recall_at_k  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402

DEFAULT_GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
DEFAULT_HOLDOUT = ROOT / "data" / "finetune" / "holdout_docs.json"
GATE_STRATA = ("numeric_table", "multi_hop", "lineage_supersession")


def parse_run_doc(path: Path) -> dict[str, list[str]]:
    """run.doc.trec is a VALID 6-field TREC file at circular level
    (trecio.py:write_run_doc) - circular numbers never contain whitespace,
    so a plain split() is safe here (unlike the legacy chunk-level file,
    whose doc ids embed section headings with spaces)."""
    out: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split()
        qid, _q0, docid, rank = parts[0], parts[1], parts[2], int(parts[3])
        out[qid].append((rank, docid))
    return {qid: [d for _, d in sorted(ranked)] for qid, ranked in out.items()}


def score_run(ranked_by_qid: dict[str, list[str]], golden: list[dict],
             k: int = 10) -> dict[str, dict]:
    """Per-query recall@k/ndcg@k for every non-abstain, judged golden row.
    Returns {row_id: {"recall": .., "ndcg": .., "task_type": ..}}."""
    out = {}
    for row in golden:
        if row.get("abstain"):
            continue
        relevant = set(row.get("relevant_circulars") or [])
        if not relevant:
            continue
        ranked = ranked_by_qid.get(row["id"], [])
        out[row["id"]] = {
            "recall": recall_at_k(ranked, relevant, k),
            "ndcg": ndcg_at_k(ranked, relevant, k),
            "task_type": row["task_type"],
        }
    return out


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def compare(control: dict[str, dict], treatment: dict[str, dict],
           holdout: dict) -> dict:
    row_split = holdout["row_split"]
    subset_of = {}
    for subset, ids in row_split.items():
        for rid in ids:
            subset_of[rid] = subset

    common_ids = sorted(set(control) & set(treatment))

    def group_stats(ids: list[str]) -> dict:
        c_recall = [control[i]["recall"] for i in ids]
        t_recall = [treatment[i]["recall"] for i in ids]
        c_ndcg = [control[i]["ndcg"] for i in ids]
        t_ndcg = [treatment[i]["ndcg"] for i in ids]
        return {
            "n": len(ids),
            "control_recall": round(_mean(c_recall), 4),
            "treatment_recall": round(_mean(t_recall), 4),
            "delta_recall": round(_mean(t_recall) - _mean(c_recall), 4),
            "control_ndcg": round(_mean(c_ndcg), 4),
            "treatment_ndcg": round(_mean(t_ndcg), 4),
            "delta_ndcg": round(_mean(t_ndcg) - _mean(c_ndcg), 4),
        }

    by_stratum = defaultdict(list)
    for rid in common_ids:
        by_stratum[control[rid]["task_type"]].append(rid)

    by_subset = defaultdict(list)
    for rid in common_ids:
        by_subset[subset_of.get(rid, "unclassified")].append(rid)

    return {
        "overall": group_stats(common_ids),
        "by_stratum": {t: group_stats(ids) for t, ids in sorted(by_stratum.items())},
        "by_holdout_subset": {s: group_stats(ids) for s, ids in sorted(by_subset.items())},
    }


def gate_verdict(by_stratum: dict) -> tuple[str, list[str]]:
    """Preregistered asymmetric directional screen (n=20-40/stratum is a
    directional signal, not a significance test - iv-series-verdicts-
    unpowered applies): PROCEED unless numeric_table, multi_hop, AND
    lineage_supersession are ALL flat-or-negative on recall@10. Any one of
    the three showing a positive lift is enough to proceed to Phase 1."""
    positive = []
    for stratum in GATE_STRATA:
        stats = by_stratum.get(stratum)
        if stats and stats["delta_recall"] > 0:
            positive.append(stratum)
    verdict = "PROCEED" if positive else "STOP (structural pairs show no signal)"
    return verdict, positive


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--control", required=True)
    ap.add_argument("--treatment", required=True)
    ap.add_argument("--golden", default=str(DEFAULT_GOLDEN))
    ap.add_argument("--holdout", default=str(DEFAULT_HOLDOUT))
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    golden = load_golden(args.golden)
    holdout = json.loads(Path(args.holdout).read_text(encoding="utf-8"))

    control_ranked = parse_run_doc(Path(args.control))
    treatment_ranked = parse_run_doc(Path(args.treatment))
    control_scored = score_run(control_ranked, golden, args.k)
    treatment_scored = score_run(treatment_ranked, golden, args.k)

    result = compare(control_scored, treatment_scored, holdout)
    verdict, positive_strata = gate_verdict(result["by_stratum"])
    result["gate"] = {"verdict": verdict, "positive_strata": positive_strata,
                      "gate_strata": list(GATE_STRATA)}

    print(json.dumps(result, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"-> {args.out}")


if __name__ == "__main__":
    main()
