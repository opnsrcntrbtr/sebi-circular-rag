"""Precision audit for circular -> regulation edges (spec 2026-07-23 §7).

Emits a hand-labelling worksheet stratified by evidence tier, then scores a
completed worksheet with a Clopper-Pearson exact interval. Precision, not
coverage, is the gate: a regex that over-matches would score perfectly on
coverage alone.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/audit_reg_edges.py            # emit
    PYTHONPATH=src .venv/bin/python scripts/audit_reg_edges.py --score \
        reports/reg_edge_audit.md
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.reg_citations import EVIDENCE_TIERS  # noqa: E402
from sebi_rag.stats import ProportionCI, clopper_pearson_ci  # noqa: E402

LABEL_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*\[([ xX])\]", re.M)


def stratified_sample(edges: list[dict], n: int, seed: int) -> list[dict]:
    """Up to `n` edges, spread as evenly as possible across evidence tiers.

    Tiers with fewer edges than their share give up the remainder to the others,
    so a corpus with only two populated tiers still yields a full sample.
    """
    rng = random.Random(seed)
    buckets = {t: [e for e in edges if e.get("evidence") == t]
               for t in EVIDENCE_TIERS}
    for b in buckets.values():
        rng.shuffle(b)
    out, quota = [], n
    tiers = sorted(EVIDENCE_TIERS, key=lambda t: len(buckets[t]))
    for i, t in enumerate(tiers):
        share = min(len(buckets[t]), -(-quota // (len(tiers) - i)))
        out.extend(buckets[t][:share])
        quota -= share
    return out


def score(labels: dict[str, bool]) -> ProportionCI:
    """Clopper-Pearson interval over hand-labelled edge correctness."""
    values = list(labels.values())
    return clopper_pearson_ci(sum(1 for v in values if v), len(values))


def _emit(edges: list[dict], circ_by_num: dict[str, dict],
          reg_by_id: dict[str, dict], n: int, seed: int, out: Path) -> None:
    sample = stratified_sample(edges, n, seed)
    lines = [
        "# Regulation edge precision audit",
        "",
        f"Sample: {len(sample)} of {len(edges)} edges, stratified by evidence "
        f"tier, seed={seed}.",
        "",
        "Mark `[x]` when the circular genuinely cites that regulation. "
        "Then run:",
        "",
        "    PYTHONPATH=src .venv/bin/python scripts/audit_reg_edges.py "
        f"--score {out}",
        "",
        "| edge | evidence / clause | correct |",
        "| --- | --- | --- |",
    ]
    for e in sample:
        subj = (circ_by_num.get(e["source"], {}).get("subject", "") or "")[:70]
        title = (reg_by_id.get(e["target"], {}).get("title", e["target"]))[:70]
        lines.append(
            f"| {e['source']} -> {e['target']} | {e['evidence']}"
            f"{' / ' + e['clause'] if e.get('clause') else ''} | [ ] |")
        lines.append(f"| <sub>{subj}</sub> | <sub>{title}</sub> | |")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote worksheet with {len(sample)} edges to {out}")
    print("Label each row, then re-run with --score.")


def _score_file(path: Path) -> int:
    labels = {}
    for i, m in enumerate(LABEL_RE.finditer(path.read_text(encoding="utf-8"))):
        if "->" not in m.group(1):
            continue
        labels[f"{i}:{m.group(1)}"] = m.group(3).lower() == "x"
    ci = score(labels)
    print(f"Labelled: {ci.n}   correct: {ci.successes}")
    print(f"Precision: {ci.point:.1%}  "
          f"95% CI [{ci.lo:.1%}, {ci.hi:.1%}]  ({ci.method})")
    passed = ci.n > 0 and ci.point >= 0.95
    print("GATE: " + ("PASS" if passed else "FAIL (target >= 95%)"))
    return 0 if passed else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--edges", default="data/manifests/regulation_edges.jsonl")
    ap.add_argument("--corpus", default="data/corpus/circulars.jsonl")
    ap.add_argument("--regulations", default="data/corpus/regulations.jsonl")
    ap.add_argument("--out", default="reports/reg_edge_audit.md")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=20260723)
    ap.add_argument("--score", metavar="WORKSHEET", default=None)
    args = ap.parse_args(argv)

    if args.score:
        return _score_file(Path(args.score))

    def _load(p):
        return [json.loads(x) for x in Path(p).read_text(
            encoding="utf-8").splitlines() if x.strip()]

    edges = _load(args.edges)
    circ = {c["circular_number"]: c for c in _load(args.corpus)}
    regs = {r["reg_id"]: r for r in _load(args.regulations)}
    _emit(edges, circ, regs, args.n, args.seed, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
