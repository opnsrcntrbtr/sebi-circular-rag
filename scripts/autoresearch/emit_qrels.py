"""Emit TREC qrels for an eval set, keyed by its golden_sha256.

    .venv/bin/python scripts/autoresearch/emit_qrels.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.autoresearch.trecio import write_trec_qrels  # noqa: E402
from sebi_rag.benchmark import sha256_file  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", type=Path, default=ROOT / "eval/golden/golden_v7.jsonl")
    ap.add_argument("--out-dir", type=Path, default=ROOT / "eval" / "qrels")
    args = ap.parse_args()

    rows = [
        json.loads(line)
        for line in args.golden.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    out = args.out_dir / f"{args.golden.stem}.qrels"
    n = write_trec_qrels(out, rows)
    sha = sha256_file(args.golden)
    n_abstain = sum(1 for r in rows if r.get("abstain"))
    # TREC qrels carries no comment syntax, so the eval-set key lives in a
    # sidecar. Without it a qrels file could silently be applied to a
    # different golden set.
    out.with_suffix(".qrels.meta.json").write_text(
        json.dumps(
            {
                "golden_path": str(args.golden.relative_to(ROOT)),
                "golden_sha256": sha,
                "rows": len(rows),
                "abstain_excluded": n_abstain,
                "qrels_lines": n,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"{out}: {n} lines from {len(rows)} rows ({n_abstain} abstain excluded)")
    print(f"golden_sha256={sha}")


if __name__ == "__main__":
    main()
