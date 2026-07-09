"""Export benchmark artifacts for retrieval/RAG/data-quality evaluation.

Outputs:
  dist/benchmark/retrieval-benchmark/{corpus.jsonl,queries.jsonl,qrels/test.tsv}
  dist/benchmark/rag-benchmark/golden_v6.jsonl
  dist/benchmark/dataset-quality/summary.json
  dist/benchmark/README.md
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.benchmark import export_beir, validate_golden, write_jsonl  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.lineage import build_lineage, load_records  # noqa: E402
from sebi_rag.segment import Chunk  # noqa: E402


def load_index_chunks(path: Path) -> list[Chunk]:
    return [
        Chunk(**json.loads(line))
        for line in (path / "chunks.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def dataset_quality(records: list[dict], chunks: list[Chunk], golden: list[dict]) -> dict:
    lineage = build_lineage(records)
    dept = Counter(r.get("issuing_department") or "UNKNOWN" for r in records)
    task_types = Counter(g.get("task_type", "legacy") for g in golden)
    review = Counter(g.get("review_status", "legacy") for g in golden)
    return {
        "circulars": len(records),
        "chunks": len(chunks),
        "golden_items": len(golden),
        "golden_answerable": sum(not g.get("abstain") for g in golden),
        "golden_abstain": sum(bool(g.get("abstain")) for g in golden),
        "task_types": dict(sorted(task_types.items())),
        "review_status": dict(sorted(review.items())),
        "issuing_departments": dict(dept.most_common()),
        "lineage_edges": {
            "supersedes": sum(len(v) for v in lineage.supersedes.values()),
            "amends": sum(len(v) for v in lineage.amends.values()),
        },
        "target_golden_items": 200,
    }


def write_card(path: Path, summary: dict) -> None:
    path.write_text(
        "---\n"
        "configs:\n"
        "  - config_name: retrieval-benchmark\n"
        "    data_files:\n"
        "      - split: corpus\n"
        "        path: retrieval-benchmark/corpus.jsonl\n"
        "      - split: queries\n"
        "        path: retrieval-benchmark/queries.jsonl\n"
        "      - split: qrels\n"
        "        path: retrieval-benchmark/qrels/test.tsv\n"
        "  - config_name: rag-benchmark\n"
        "    data_files:\n"
        "      - split: test\n"
        "        path: rag-benchmark/golden_v6.jsonl\n"
        "  - config_name: dataset-quality\n"
        "    data_files:\n"
        "      - split: summary\n"
        "        path: dataset-quality/summary.json\n"
        "license: cc-by-4.0\n"
        "---\n\n"
        "# SEBI Circular RAG Benchmark\n\n"
        "Domain-specific benchmark artifacts for retrieval, RAG answer quality, "
        "and dataset-quality checks over public SEBI circulars. This is not a "
        "general leaderboard; the current gold set is a curated seed intended "
        "to grow toward about 200 reviewed items.\n\n"
        f"- Circulars: {summary['circulars']}\n"
        f"- Chunks: {summary['chunks']}\n"
        f"- Golden items: {summary['golden_items']} "
        f"({summary['golden_answerable']} answerable, {summary['golden_abstain']} abstain)\n\n"
        "Underlying SEBI text remains attributable to SEBI. Derived labels, "
        "schemas, and packaging are released as CC-BY-4.0. Not legal advice; "
        "verify against sebi.gov.in before regulatory reliance.\n",
        encoding="utf-8",
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default=str(ROOT / "eval" / "golden" / "golden_v6.jsonl"))
    ap.add_argument("--index", default=str(ROOT / "data" / "index"))
    ap.add_argument("--corpus", default=str(ROOT / "data" / "corpus" / "circulars.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "dist" / "benchmark"))
    args = ap.parse_args()

    golden = load_golden(args.golden)
    issues = validate_golden(golden)
    if issues:
        for issue in issues:
            print(f"{issue.item_id}: {issue.message}", file=sys.stderr)
        raise SystemExit(1)

    chunks = load_index_chunks(Path(args.index))
    records = load_records(args.corpus)
    out = Path(args.out)
    counts = export_beir(
        chunks=chunks, golden=golden, out_dir=out / "retrieval-benchmark"
    )
    write_jsonl(out / "rag-benchmark" / "golden_v6.jsonl", golden)
    summary = dataset_quality(records, chunks, golden)
    (out / "dataset-quality").mkdir(parents=True, exist_ok=True)
    (out / "dataset-quality" / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_card(out / "README.md", summary)
    print(json.dumps({"out": str(out), **counts, **summary}, indent=2))


if __name__ == "__main__":
    main()
