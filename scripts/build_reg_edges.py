"""Build circular -> regulation edges and annotate the corpus (offline).

No network, no model weights, idempotent. Ordering matters: repealed stubs are
synthesised BEFORE edges are built, because an edge may target a stub.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/build_reg_edges.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.reg_lineage import (annotate_regulation_fields,  # noqa: E402
                                  build_regulation_edges,
                                  synthesise_repealed_stubs)


def load_jsonl(path: str | Path) -> list[dict]:
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def write_jsonl(path: str | Path, records: list[dict]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", default="data/corpus/circulars.jsonl")
    ap.add_argument("--regulations", default="data/corpus/regulations.jsonl")
    ap.add_argument("--edges", default="data/manifests/regulation_edges.jsonl")
    ap.add_argument("--report", default="reports/unresolved_regulations.txt")
    args = ap.parse_args(argv)

    reg_path = Path(args.regulations)
    if not reg_path.exists():
        print(f"ERROR: {reg_path} not found. Run `make scrape-regs` first.",
              file=sys.stderr)
        return 2

    circulars = load_jsonl(args.corpus)
    regulations = load_jsonl(reg_path)
    print(f"Loaded {len(circulars)} circulars, {len(regulations)} regulations.")

    stubs = synthesise_repealed_stubs(circulars, regulations)
    if stubs:
        regulations.extend(stubs)
        n_repealed = sum(s["status"] == "repealed" for s in stubs)
        print(f"Synthesised {len(stubs)} stub(s): "
              f"{n_repealed} repealed, {len(stubs) - n_repealed} unknown.")
    write_jsonl(reg_path, regulations)

    edges, unresolved = build_regulation_edges(circulars, regulations)
    write_jsonl(args.edges, edges)
    changed = annotate_regulation_fields(circulars, edges, regulations)
    write_jsonl(args.corpus, circulars)

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{c}\t{name}\t{year}" for (name, year), c
             in sorted(unresolved.items(), key=lambda kv: -kv[1])]
    report.write_text("count\tname\tyear\n" + "\n".join(lines) + "\n",
                      encoding="utf-8")

    linked = sum(1 for c in circulars if c.get("regulations"))
    basis = {}
    for c in circulars:
        k = c.get("regulatory_basis_status", "unknown")
        basis[k] = basis.get(k, 0) + 1
    print(f"\nEdges: {len(edges)} across {linked} circulars "
          f"({linked / max(len(circulars), 1):.1%} of corpus).")
    print(f"Annotated (changed): {changed}")
    print(f"regulatory_basis_status: {basis}")
    print(f"Unresolved names: {len(unresolved)} -> {report}")
    print("\nNext: make audit-regs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
