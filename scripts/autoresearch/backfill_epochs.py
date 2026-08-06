"""Assign epochs to the archived runs and write the epoch registry.

Every run's results.json already pins corpus_sha256 and golden_sha256, so the
archive can be retro-labelled rather than discarded. Runs without those fields
are recorded with epoch null and excluded from all comparisons.

    .venv/bin/python scripts/autoresearch/backfill_epochs.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.autoresearch.epoch import assign_epochs, frame_of  # noqa: E402

RUNS_DIR = ROOT / "eval" / "runs"
REGISTRY = ROOT / "eval" / "epochs" / "epochs.jsonl"


def load_runs(runs_dir: Path) -> list[tuple[str, dict]]:
    runs = []
    for run_dir in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
        results = run_dir / "results.json"
        if not results.exists() or not results.stat().st_size:
            runs.append((run_dir.name, {}))
            continue
        runs.append((run_dir.name, json.loads(results.read_text(encoding="utf-8"))))
    return runs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs-dir", type=Path, default=RUNS_DIR)
    ap.add_argument("--registry", type=Path, default=REGISTRY)
    args = ap.parse_args()

    runs = load_runs(args.runs_dir)
    epochs = assign_epochs(runs)

    members: dict[str, list[str]] = {e: [] for e in epochs.values()}
    unframed: list[str] = []
    for name, results in runs:
        frame = frame_of(results, epochs)
        if frame is None:
            unframed.append(name)
        else:
            members[frame.epoch].append(name)

    first_ts: dict[str, str] = {}
    full_sha: dict[str, str] = {}
    for _name, results in runs:
        meta = results.get("metadata") or {}
        corpus, ts = meta.get("corpus_sha256"), meta.get("ts")
        if not corpus or not ts:
            continue
        key = corpus[:8]
        full_sha[key] = corpus
        if key not in first_ts or ts < first_ts[key]:
            first_ts[key] = ts

    args.registry.parent.mkdir(parents=True, exist_ok=True)
    with args.registry.open("w", encoding="utf-8") as f:
        for corpus, epoch in sorted(epochs.items(), key=lambda kv: kv[1]):
            f.write(
                json.dumps(
                    {
                        "epoch": epoch,
                        "corpus_sha256": full_sha[corpus],
                        "first_seen": first_ts[corpus],
                        "runs": sorted(members[epoch]),
                        "status": "open",
                    }
                )
                + "\n"
            )

    for epoch in sorted(set(epochs.values())):
        print(f"{epoch}: {len(members[epoch])} runs")
    print(f"unframed (excluded from comparisons): {len(unframed)} {sorted(unframed)}")


if __name__ == "__main__":
    main()
