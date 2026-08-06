"""bench_retrieval must emit valid TREC alongside the legacy runfile."""
import re
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "bench_retrieval.py"


def test_bench_retrieval_writes_all_four_artifacts():
    src = SCRIPT.read_text(encoding="utf-8")
    for name in ("run.trec", "run.chunk.trec", "run.doc.trec", "docids.tsv"):
        assert re.search(rf'["\']{re.escape(name)}["\']', src), f"{name} not written"


def test_bench_retrieval_imports_the_valid_writers():
    src = SCRIPT.read_text(encoding="utf-8")
    assert "from sebi_rag.autoresearch.trecio import" in src
    for fn in ("write_run_chunk", "write_run_doc", "write_docids"):
        assert fn in src
