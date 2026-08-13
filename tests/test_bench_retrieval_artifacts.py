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


def test_bench_retrieval_can_measure_the_reranked_order():
    """run_retrieval_benchmark calls pipeline.retriever.retrieve directly, so
    every archived run measures raw RRF fusion order. Production reranks all
    50 candidates (pipeline.query), so the order a user sees is the
    cross-encoder's, not fusion's. Without this flag the A/B programme cannot
    measure the stage that actually orders results."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert '"--rerank"' in src, "cannot measure post-rerank ordering"
    assert re.search(r'"rerank":\s*', src), "rerank arm not recorded in params"


def test_bench_retrieval_can_bench_an_alternate_index():
    """iv9/iv10 build a headered index beside data/index. Without an index
    override the bench always measures the production index, silently
    reporting the control arm's numbers under the treatment's run name."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert '"--index-dir"' in src, "cannot point the bench at an arm index"
    # The resolved dir must actually be used, not just parsed.
    assert not re.search(r'HybridRetriever\.load\(ROOT / "data" / "index"', src), (
        "loads the hardcoded production index, ignoring --index-dir")


def test_bench_retrieval_exposes_and_records_the_iv2_expansion_arm():
    # iv2 is otherwise unmeasurable: glossary expansion is unconditional in
    # HybridRetriever, so the control arm needs a flag AND that flag must land
    # in run metadata, or an archived run cannot say which arm produced it.
    src = SCRIPT.read_text(encoding="utf-8")
    assert '"--no-expand"' in src, "no CLI flag for the iv2 control arm"
    assert re.search(r'"expand_sparse":\s*', src), "arm not recorded in params"
