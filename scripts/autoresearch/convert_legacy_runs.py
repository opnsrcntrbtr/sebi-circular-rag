"""Back-convert archived runfiles into standards-compliant TREC artifacts.

The archived `run.trec` files embed section headings inside the doc id, so a
line splits into ~15 fields and trec_eval cannot read them. `read_trec_run`
already recovers them; this writes the valid artifacts alongside. The original
`run.trec` is never modified.

    .venv/bin/python scripts/autoresearch/convert_legacy_runs.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.autoresearch.trecio import (  # noqa: E402
    write_docids,
    write_run_chunk,
    write_run_doc,
)
from sebi_rag.benchmark import read_trec_run  # noqa: E402

RUNS_DIR = ROOT / "eval" / "runs"


def _run_tag(runfile: Path) -> str:
    """Trailing field of the first line; also the whitespace precondition check."""
    for line in runfile.read_text(encoding="utf-8").splitlines():
        if line.strip():
            return line.split()[-1]
    raise ValueError("runfile is empty")


def _assert_fixed_tail(runfile: Path) -> None:
    """read_trec_run assumes qid and tag carry no whitespace. Verify per line."""
    tag = _run_tag(runfile)
    for n, line in enumerate(runfile.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 6:
            raise ValueError(f"line {n}: fewer than 6 fields")
        if parts[-1] != tag:
            raise ValueError(
                f"line {n}: run tag {parts[-1]!r} != {tag!r}; tag may contain whitespace"
            )
        try:
            int(parts[-3])
            float(parts[-2])
        except ValueError as exc:
            raise ValueError(
                f"line {n}: rank/score not at fixed tail positions"
            ) from exc


def convert_run_dir(run_dir: Path) -> dict:
    """Write run.chunk.trec, run.doc.trec and docids.tsv for one archived run."""
    runfile = run_dir / "run.trec"
    if not runfile.exists():
        return {"status": "skipped", "reason": "no run.trec", "n_lines": 0}
    try:
        _assert_fixed_tail(runfile)
        rankings = read_trec_run(runfile)
        tag = _run_tag(runfile)
    except ValueError as exc:
        return {"status": "failed", "reason": str(exc), "n_lines": 0}

    write_run_chunk(run_dir / "run.chunk.trec", tag, rankings)
    write_run_doc(run_dir / "run.doc.trec", tag, rankings)
    write_docids(run_dir / "docids.tsv", rankings)
    n = sum(len(v) for v in rankings.values())
    return {"status": "converted", "reason": "", "n_lines": n}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs-dir", type=Path, default=RUNS_DIR)
    args = ap.parse_args()

    report = {}
    for run_dir in sorted(p for p in args.runs_dir.iterdir() if p.is_dir()):
        report[run_dir.name] = convert_run_dir(run_dir)

    for name, r in report.items():
        print(f"{name:<32} {r['status']:<10} {r['reason']}")
    counts: dict[str, int] = {}
    for r in report.values():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("\n" + json.dumps(counts))
    if counts.get("failed"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
