"""Export SEBI RAG data into publishable dataset configs (HF/Kaggle/Zenodo/AIKosh).

Task 1 scope (Fable): pipeline scaffold + `corpus` config. Later tasks add
chunks/lineage/eval (Sonnet) and cards/packaging (Haiku). Spec:
docs/superpowers/specs/2026-07-09-sebi-public-datasets-design.md.

Stages: validate (reuse validate_corpus invariants) -> transform (pure
per-config builders) -> emit (Parquet + JSONL under dist/datasets/<config>/
plus manifest.json with source checksums and snapshot version).

Usage: uv run python scripts/export_datasets.py \
    [--corpus data/corpus/circulars.jsonl] [--out dist/datasets]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_corpus import validate  # noqa: E402

# Column order is the published schema (spec Config 1). provenance is replaced
# by extraction_date (local PDF filenames have no research value); empty
# amendment_history is not exported.
CORPUS_SCHEMA = [
    "circular_number", "issue_date", "effective_date", "subject",
    "issuing_department", "supersession_status", "version_lineage",
    "source_url", "text", "excerpt", "extraction_date",
]
_EXTRACTION_DATE = re.compile(r"on (\d{4}-\d{2}-\d{2})\s*$")


def _null(v: str | None) -> str | None:
    return v if v else None


def build_corpus_rows(records: list[dict]) -> list[dict]:
    """Pure transform: corpus JSONL records -> publishable rows (CORPUS_SCHEMA)."""
    rows = []
    for r in records:
        m = _EXTRACTION_DATE.search(r.get("provenance", ""))
        rows.append({
            "circular_number": r["circular_number"],
            "issue_date": _null(r.get("issue_date")),
            "effective_date": _null(r.get("effective_date")),
            "subject": _null(r.get("subject")),
            "issuing_department": _null(r.get("issuing_department")),
            "supersession_status": _null(r.get("supersession_status")),
            "version_lineage": r.get("version_lineage", []),
            "source_url": _null(r.get("source_url")),
            "text": r.get("text", ""),
            "excerpt": bool(r.get("excerpt", False)),
            "extraction_date": m.group(1) if m else None,
        })
    return rows


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot_version(rows: list[dict]) -> str:
    dates = [r["issue_date"] for r in rows if r["issue_date"]]
    return "v" + max(dates)[:7].replace("-", ".") if dates else "v0000.00"


def _emit(rows: list[dict], config_dir: Path, name: str, schema: list[str]) -> None:
    config_dir.mkdir(parents=True, exist_ok=True)
    with (config_dir / f"{name}.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    import pyarrow as pa
    import pyarrow.parquet as pq
    table = pa.Table.from_pylist(rows).select(schema)
    pq.write_table(table, config_dir / f"{name}.parquet")


def export_corpus(corpus_path: Path, out_dir: Path) -> dict:
    """Validate -> transform -> emit the corpus config; return the manifest."""
    records = [json.loads(l) for l in
               corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    violations = validate(records)
    if violations:
        raise ValueError(f"{len(violations)} corpus violation(s); fix before "
                         f"export: {violations[:3]}")
    rows = build_corpus_rows(records)
    _emit(rows, out_dir / "corpus", "corpus", CORPUS_SCHEMA)
    manifest = {
        "version": _snapshot_version(rows),
        "configs": {"corpus": {"rows": len(rows),
                               "source": str(corpus_path),
                               "source_sha256": _sha256(corpus_path)}},
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", default="data/corpus/circulars.jsonl")
    ap.add_argument("--out", default="dist/datasets")
    args = ap.parse_args(argv)
    manifest = export_corpus(Path(args.corpus), Path(args.out))
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
