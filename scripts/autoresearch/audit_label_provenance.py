"""Report what the annotation artifacts can account for, before classifying.

golden_v7 already carries `label_source`, but as 14 free-text prose values, and
`review_status` is `adjudicated` for all 260 rows. This is read-only: it writes
a report, never the golden file. Classification rules (normalize_label_tier)
are written against these findings rather than assumed.

    .venv/bin/python scripts/autoresearch/audit_label_provenance.py
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
ANNOT = ROOT / "eval" / "golden" / "v7_annotations"
REPORT = ROOT / "reports" / "label_provenance_audit.md"


def audit(golden_rows: list[dict], artifacts: dict[str, set[str]]) -> dict:
    """Cross-tabulate label_source against which artifacts mention each row."""
    by_source: collections.Counter[str] = collections.Counter()
    coverage: dict[str, collections.Counter[str]] = {}
    unaccounted: list[str] = []

    for row in golden_rows:
        source = row.get("label_source") or "(missing)"
        by_source[source] += 1
        cov = coverage.setdefault(source, collections.Counter())
        hit = False
        for name, ids in artifacts.items():
            if row["id"] in ids:
                cov[name] += 1
                hit = True
        if not hit:
            unaccounted.append(row["id"])

    return {
        "by_source": dict(by_source),
        "coverage": {k: dict(v) for k, v in coverage.items()},
        "unaccounted": unaccounted,
    }


def _ids_from_jsonl(path: Path) -> set[str]:
    if not path.exists():
        return set()
    out = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        val = rec.get("id") or rec.get("row_id") or rec.get("qid")
        if not val and isinstance(rec.get("row"), dict):
            val = rec["row"].get("id")
        if val:
            out.add(val)
    return out


def _ids_from_dir(path: Path) -> set[str]:
    if not path.exists():
        return set()
    out = set()
    for p in path.rglob("*"):
        if p.is_file():
            out.add(p.stem)
    return out


def _ids_from_csv(path: Path, column: str = "id") -> set[str]:
    """Row ids from a human labelling packet CSV.

    packet_human/ holds a handful of packet files (template CSV, manifest,
    rendered HTML) — not one file per row — so the human-labelled ids live
    inside labels_template.csv, not in the filenames.
    """
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as f:
        return {
            row[column].strip()
            for row in csv.DictReader(f)
            if row.get(column, "").strip()
        }


def collect_artifacts(annot: Path) -> dict[str, set[str]]:
    return {
        "votes.jsonl": _ids_from_jsonl(annot / "votes.jsonl"),
        "arbitration_queue.jsonl": _ids_from_jsonl(annot / "arbitration_queue.jsonl"),
        "packet_human": _ids_from_csv(annot / "packet_human" / "labels_template.csv"),
        "gemini": _ids_from_dir(annot / "gemini"),
        "qwen": _ids_from_dir(annot / "qwen"),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", type=Path, default=GOLDEN)
    ap.add_argument("--annotations", type=Path, default=ANNOT)
    ap.add_argument("--out", type=Path, default=REPORT)
    args = ap.parse_args()

    rows = [
        json.loads(line)
        for line in args.golden.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    artifacts = collect_artifacts(args.annotations)
    result = audit(rows, artifacts)

    lines = [
        "# Label provenance audit",
        "",
        f"Rows: {len(rows)}. Artifacts scanned: "
        + ", ".join(f"{k} ({len(v)} ids)" for k, v in artifacts.items()),
        "",
        "| label_source | n | accounted by |",
        "|---|---|---|",
    ]
    for source, n in sorted(result["by_source"].items(), key=lambda kv: -kv[1]):
        cov = result["coverage"].get(source, {})
        detail = ", ".join(f"{k}={v}" for k, v in sorted(cov.items())) or "—"
        lines.append(f"| `{source}` | {n} | {detail} |")
    lines += [
        "",
        f"**Unaccounted rows: {len(result['unaccounted'])}**",
        "",
        "```",
        json.dumps(result["unaccounted"][:40], indent=1),
        "```",
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
