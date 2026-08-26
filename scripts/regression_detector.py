#!/usr/bin/env python3
"""Eval regression detector — flag when metrics drop below gate floors.

Checks:
1. Load floors from gate_v7.json
2. Scan eval/runs/ for recent evaluation results
3. Flag any metric that dropped below the floor
4. Report delta for each regressed metric

Exit 0 = no regressions, exit 1 = regression detected.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GATE_PATH = PROJECT_ROOT / "eval" / "golden" / "gate_v7.json"
RUNS_DIR = PROJECT_ROOT / "eval" / "runs"

# Metric display names (gate_v7.json keys -> human-readable)
METRIC_LABELS = {
    "recall_at_k": "recall_at_10",
    "context_recall": "context_recall",
    "ndcg_at_10": "ndcg_at_10",
    "citation_recall": "citation_recall",
    "abstention_accuracy": "abstention_accuracy",
    "citation_precision": "citation_precision",
}


def load_floors() -> dict[str, float]:
    """Load floors from gate_v7.json."""
    try:
        gate = json.loads(GATE_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        print(f"FAIL: Cannot load {GATE_PATH}", file=sys.stderr)
        sys.exit(1)

    floors = gate.get("floors", {})
    if not floors:
        print("FAIL: No floors in gate_v7.json", file=sys.stderr)
        sys.exit(1)

    return floors


def load_latest_runs() -> list[dict]:
    """Load most recent eval runs sorted by timestamp."""
    if not RUNS_DIR.exists():
        return []

    runs = []
    for f in sorted(RUNS_DIR.glob("*.json"), reverse=True):
        try:
            data = json.loads(f.read_text())
            # Only consider runs with gate metrics
            if "recall_at_10" in data or ("gate" in data and "recall_at_k" in data.get("gate", {})):
                runs.append({"path": f, "data": data})
        except (json.JSONDecodeError, OSError):
            continue

    # Sort by timestamp if available
    runs.sort(key=lambda r: r["data"].get("ts", ""), reverse=True)
    return runs[:10]  # Last 10 runs


def extract_metrics(run: dict) -> dict[str, float]:
    """Extract metric values from a run."""
    data = run["data"]
    # Prefer top-level metrics (newer format)
    if "recall_at_10" in data:
        return {
            "recall_at_k": data["recall_at_10"],
            "context_recall": data["context_recall"],
            "ndcg_at_10": data["ndcg_at_10"],
            "citation_recall": data["citation_recall"],
            "abstention_accuracy": data["abstention_accuracy"],
            "citation_precision": data["citation_precision"],
        }
    # Fall back to gate sub-object (older format)
    gate = data.get("gate", {})
    return {
        "recall_at_k": gate.get("recall_at_k"),
        "context_recall": gate.get("context_recall"),
        "ndcg_at_10": gate.get("ndcg_at_10"),
        "citation_recall": gate.get("citation_recall"),
        "abstention_accuracy": gate.get("abstention_accuracy"),
        "citation_precision": gate.get("citation_precision"),
    }


def main() -> int:
    floors = load_floors()
    runs = load_latest_runs()

    if not runs:
        print("WARN: No eval runs found in eval/runs/", file=sys.stderr)
        print("REGRESSION_DETECTOR status=no_runs", flush=True)
        return 0

    regressions = []
    for run in runs:
        metrics = extract_metrics(run)
        run_regressions = []

        for metric, floor in floors.items():
            value = metrics.get(metric)
            if value is None:
                continue

            if value < floor:
                delta = value - floor
                label = METRIC_LABELS.get(metric, metric)
                run_regressions.append({
                    "metric": label,
                    "value": round(value, 4),
                    "floor": floor,
                    "delta": round(delta, 4),
                })

        if run_regressions:
            regressions.append({
                "run": run["path"].name,
                "ts": run["data"].get("ts", "unknown"),
                "regressions": run_regressions,
            })

    # Output summary
    if regressions:
        print(f"REGRESSION_DETECTOR status=regression detected={len(regressions)}", flush=True)
        for reg in regressions:
            print(f"REGRESSION_DETECTOR run={reg['run']} ts={reg['ts']}", flush=True)
            for r in reg["regressions"]:
                print(f"  {r['metric']}: {r['value']} < {r['floor']} (delta: {r['delta']:+.4f})", flush=True)
        return 1

    print(f"REGRESSION_DETECTOR status=clean runs_checked={len(runs)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
