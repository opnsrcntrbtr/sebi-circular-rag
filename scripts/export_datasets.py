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
from sebi_rag.benchmark import validate_golden  # noqa: E402
from sebi_rag.ingest_pdf import normalize_circular_number  # noqa: E402

# Column order is the published schema (spec Config 1). provenance is replaced
# by extraction_date (local PDF filenames have no research value); empty
# amendment_history is not exported.
CORPUS_SCHEMA = [
    "circular_number", "issue_date", "effective_date", "subject",
    "issuing_department", "supersession_status", "version_lineage",
    "source_url", "text", "excerpt", "extraction_date",
]
_EXTRACTION_DATE = re.compile(r"on (\d{4}-\d{2}-\d{2})\s*$")

# One row per retrieval chunk. context_header is the repeated
# "{circular_number} | {truncated subject} | {section}" line every chunk's
# text starts with (see build_index chunking); split out so researchers can
# choose either representation. meta.amendment_history is empty across the
# whole corpus (verified 2026-07-09) so, like CORPUS_SCHEMA, it isn't exported.
CHUNKS_SCHEMA = [
    "chunk_id", "doc_id", "section", "context_header", "text",
    "circular_number", "issue_date", "effective_date", "subject",
    "issuing_department", "supersession_status", "version_lineage",
]

# Forward edges only (supersedes/amends); superseded_by/amended_by in
# lineage.json are the same edges inverted for fast reverse lookup at query
# time and would duplicate rows here.
LINEAGE_SCHEMA = [
    "source_circular", "relation", "target_circular",
    "source_issue_date", "target_in_corpus",
]

# Pass-through of the golden_v6 RAG schema (scripts/build_golden_v6.py).
EVAL_SCHEMA = [
    "id", "query", "relevant_circulars", "relevant_chunks", "answer_contains",
    "must_contain", "must_not_contain", "abstain", "task_type", "difficulty",
    "expected_citation_level", "rationale", "label_source", "review_status",
]


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


def build_chunk_rows(chunks: list[dict]) -> list[dict]:
    """Pure transform: chunks.jsonl records -> publishable rows (CHUNKS_SCHEMA)."""
    rows = []
    for c in chunks:
        header, _, body = c["text"].partition("\n")
        m = c["meta"]
        rows.append({
            "chunk_id": c["id"],
            "doc_id": c["doc_id"],
            "section": c["section"],
            "context_header": header,
            "text": body,
            "circular_number": m["circular_number"],
            "issue_date": _null(m.get("issue_date")),
            "effective_date": _null(m.get("effective_date")),
            "subject": _null(m.get("subject")),
            "issuing_department": _null(m.get("issuing_department")),
            "supersession_status": _null(m.get("supersession_status")),
            "version_lineage": m.get("version_lineage", []),
        })
    return rows


def build_lineage_rows(lineage: dict, corpus_index: dict[str, str]) -> list[dict]:
    """Pure transform: lineage.json forward maps -> edge list (LINEAGE_SCHEMA).

    corpus_index maps normalize_circular_number(n) -> issue_date, for every
    circular actually in the corpus (built by _load_corpus_index).
    """
    rows = []
    for relation in ("supersedes", "amends"):
        for source, targets in lineage.get(relation, {}).items():
            source_date = corpus_index.get(normalize_circular_number(source))
            for target in targets:
                rows.append({
                    "source_circular": source,
                    "relation": relation,
                    "target_circular": target,
                    "source_issue_date": source_date,
                    "target_in_corpus": normalize_circular_number(target) in corpus_index,
                })
    return rows


def build_eval_rows(golden: list[dict]) -> list[dict]:
    """Pure transform: golden_v6 records -> publishable rows (EVAL_SCHEMA)."""
    return [{field: row[field] for field in EVAL_SCHEMA} for row in golden]


def _load_corpus_index(corpus_path: Path) -> dict[str, str]:
    records = [json.loads(l) for l in
               corpus_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return {normalize_circular_number(r["circular_number"]): r.get("issue_date", "")
            for r in records}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot_version(rows: list[dict]) -> str:
    dates = [r["issue_date"] for r in rows if r["issue_date"]]
    return "v" + max(dates)[:7].replace("-", ".") if dates else "v0000.00"


def _update_manifest(out_dir: Path, config_name: str, entry: dict,
                     version: str | None = None) -> dict:
    """Merge one config's entry into the shared manifest.json and return it."""
    path = out_dir / "manifest.json"
    manifest = json.loads(path.read_text()) if path.exists() else \
        {"version": "v0000.00", "configs": {}}
    if version:
        manifest["version"] = version
    manifest["configs"][config_name] = entry
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def _config_entry(rows: list[dict], source_path: Path) -> dict:
    return {"rows": len(rows), "source": str(source_path),
            "source_sha256": _sha256(source_path)}


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
    return _update_manifest(out_dir, "corpus", _config_entry(rows, corpus_path),
                            version=_snapshot_version(rows))


def export_chunks(chunks_path: Path, out_dir: Path) -> dict:
    """Transform -> emit the chunks config; return the manifest."""
    chunks = [json.loads(l) for l in
              chunks_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = build_chunk_rows(chunks)
    _emit(rows, out_dir / "chunks", "chunks", CHUNKS_SCHEMA)
    return _update_manifest(out_dir, "chunks", _config_entry(rows, chunks_path))


def export_lineage(lineage_path: Path, corpus_path: Path, out_dir: Path) -> dict:
    """Transform -> emit the lineage config; return the manifest."""
    lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
    corpus_index = _load_corpus_index(corpus_path)
    rows = build_lineage_rows(lineage, corpus_index)
    _emit(rows, out_dir / "lineage", "lineage", LINEAGE_SCHEMA)
    return _update_manifest(out_dir, "lineage", _config_entry(rows, lineage_path))


def export_eval(golden_path: Path, out_dir: Path) -> dict:
    """Validate -> transform -> emit the eval config; return the manifest."""
    golden = [json.loads(l) for l in
              golden_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    issues = validate_golden(golden)
    if issues:
        raise ValueError(f"{len(issues)} golden issue(s); fix before export: "
                         f"{issues[:3]}")
    rows = build_eval_rows(golden)
    _emit(rows, out_dir / "eval", "eval", EVAL_SCHEMA)
    return _update_manifest(out_dir, "eval", _config_entry(rows, golden_path))


def export_all(corpus: Path, chunks: Path, lineage: Path, golden: Path,
               out_dir: Path) -> dict:
    """Run every config export in sequence; return the merged manifest."""
    export_corpus(corpus, out_dir)
    export_chunks(chunks, out_dir)
    export_lineage(lineage, corpus, out_dir)
    return export_eval(golden, out_dir)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", default="data/corpus/circulars.jsonl")
    ap.add_argument("--chunks", default="data/index/chunks.jsonl")
    ap.add_argument("--lineage", default="data/index/lineage.json")
    ap.add_argument("--golden", default="eval/golden/golden_v6.jsonl")
    ap.add_argument("--out", default="dist/datasets")
    args = ap.parse_args(argv)
    manifest = export_all(Path(args.corpus), Path(args.chunks), Path(args.lineage),
                          Path(args.golden), Path(args.out))
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
