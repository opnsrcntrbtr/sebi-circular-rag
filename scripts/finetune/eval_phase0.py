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
from sebi_rag.stats import paired_delta  # noqa: E402

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


def gate_verdict(
    control_scored: dict[str, dict],
    treatment_scored: dict[str, dict],
    *,
    confidence: float = 0.95,
    n_resamples: int = 20000,
    seed: int = 0,
) -> tuple[str, dict[str, dict]]:
    """Statistical replacement for the original asymmetric directional
    screen (2026-08-28), which PROCEEDed on ANY ONE of the three gate strata
    showing a positive point-estimate delta_recall, on n=20-40/stratum -
    exactly the failure mode `docs/status.md`'s 2026-09-01 post-hoc entry
    diagnoses: the original Phase 0 PROCEED verdict rested on one query
    moving in numeric_table (n=30) and two in multi_hop (n=20). A directional
    screen at that n is close to a coin flip, not a gate.

    This version runs `paired_delta` (Fisher randomization, the same tool
    the post-hoc reanalysis used) per gate stratum on recall@10 and only
    calls a stratum PROCEED-worthy when the effect clears statistical
    significance (`PairedResult.significant`: p < alpha AND the CI excludes
    zero), not merely a positive sign. At golden_v7's current n this will
    usually report every stratum as inconclusive - correctly, per
    `docs/superpowers/specs/2026-09-01-golden-set-power.md`: n=20-40/stratum
    cannot resolve a 1-2pp real effect at 80% power. Silence here is the
    honest answer, not a bug to work around with a looser gate.
    """
    common = sorted(set(control_scored) & set(treatment_scored))
    by_stratum: dict[str, dict] = {}
    positive_significant: list[str] = []
    negative_significant: list[str] = []

    for stratum in GATE_STRATA:
        ids = [rid for rid in common if control_scored[rid]["task_type"] == stratum]
        if len(ids) < 2:  # paired_delta needs >=1 pair; 2 to make a p-value meaningful
            by_stratum[stratum] = {"n": len(ids), "verdict": "insufficient_data"}
            continue
        a = {rid: control_scored[rid]["recall"] for rid in ids}
        b = {rid: treatment_scored[rid]["recall"] for rid in ids}
        res = paired_delta(a, b, confidence=confidence, n_resamples=n_resamples, seed=seed)
        if res.significant and res.delta > 0:
            verdict = "significant_positive"
            positive_significant.append(stratum)
        elif res.significant and res.delta < 0:
            verdict = "significant_negative"
            negative_significant.append(stratum)
        else:
            verdict = "inconclusive"
        by_stratum[stratum] = {
            "n": res.n, "delta_recall": round(res.delta, 4),
            "p_value": round(res.p_value, 4),
            "ci": [round(res.ci_lo, 4), round(res.ci_hi, 4)],
            "verdict": verdict,
        }

    if negative_significant:
        overall = f"STOP (significant regression: {', '.join(negative_significant)})"
    elif positive_significant:
        overall = f"PROCEED (significant lift: {', '.join(positive_significant)})"
    else:
        overall = ("INCONCLUSIVE (no gate stratum reached significance at "
                   f"{confidence:.0%} confidence - see golden-v7-underpowered)")
    return overall, by_stratum


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
    verdict, gate_strata_detail = gate_verdict(control_scored, treatment_scored)
    result["gate"] = {"verdict": verdict, "gate_strata": list(GATE_STRATA),
                      "by_stratum": gate_strata_detail}

    print(json.dumps(result, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"-> {args.out}")


if __name__ == "__main__":
    main()
