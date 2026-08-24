"""Retrieval-only benchmark with TREC runfile and reproducibility metadata.

Use --smoke for fast offline tests with HashEmbedder/LexicalReranker. Without
--smoke, this loads the persisted real index and bge-m3 embedder.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(k, v)

from sebi_rag.autoresearch.trecio import (  # noqa: E402
    write_docids,
    write_run_chunk,
    write_run_doc,
)
from sebi_rag.benchmark import (  # noqa: E402
    run_metadata,
    run_retrieval_benchmark,
    validate_golden,
    write_trec_run,
)
from sebi_rag.embeddings import BGEM3Embedder, HashEmbedder  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.generate import ExtractiveStubGenerator  # noqa: E402
from sebi_rag.lineage import build_lineage, load_records  # noqa: E402
from sebi_rag.pipeline import RAGPipeline  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker, LexicalReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.segment import CircularMeta, hierarchical_chunk  # noqa: E402


def smoke_pipeline() -> RAGPipeline:
    meta = CircularMeta(
        circular_number="SMOKE/1",
        issue_date="2026-01-01",
        subject="nomination norms for demat accounts",
    )
    chunks = hierarchical_chunk(
        "1. Nomination\nInvestors may nominate a beneficiary or opt out.",
        meta,
    )
    return RAGPipeline.build(
        chunks=chunks,
        embedder=HashEmbedder(dim=128),
        reranker=LexicalReranker(),
        generator=ExtractiveStubGenerator(),
        lineage=None,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", default=str(ROOT / "eval" / "golden" / "golden_v6.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "eval" / "runs" / "baseline_retrieval"))
    ap.add_argument("--top-n", type=int, default=50)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--hyde", action="store_true")
    ap.add_argument("--splade", action="store_true")
    # iv2 control arm: glossary expansion is ON in the production retriever,
    # so the only way to measure it is to run the arm that turns it off.
    ap.add_argument("--no-expand", dest="no_expand", action="store_true",
                    help="disable iv2 glossary expansion on the BM25 leg")
    # iv9/iv10 build a headered index beside the production one; without this
    # the bench would measure data/index under the arm's run name.
    ap.add_argument("--index-dir", dest="index_dir", default=None,
                    help="index directory to bench (default: data/index)")
    # Fusion order is re-sorted by the cross-encoder in production
    # (pipeline.query reranks the whole pool), so a fusion-only measurement
    # describes a stage the user never sees.
    ap.add_argument("--rerank", action="store_true",
                    help="measure the cross-encoder reranked order, as production serves it")
    # ADR-004: the reranker was hardcoded to CrossEncoderReranker, so no arm
    # could bench an alternative without editing this script.
    ap.add_argument("--reranker", choices=["crossencoder", "jina"], default="crossencoder",
                    help="which reranker orders the pool (--rerank must also be set "
                         "for this to affect the measured order)")
    args = ap.parse_args()

    started = time.time()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.smoke:
        golden = [{
            "id": "smoke",
            "query": "nomination beneficiary demat account",
            "relevant_circulars": ["SMOKE/1"],
            "relevant_chunks": [],
            "abstain": False,
            "task_type": "body_paraphrase",
            "difficulty": "easy",
            "expected_citation_level": "circular",
            "must_contain": ["nomination"],
            "must_not_contain": [],
            "rationale": "Offline smoke item.",
            "label_source": "synthetic",
            "review_status": "reviewed",
        }]
        pipeline = smoke_pipeline()
        corpus_path = ROOT / "data" / "corpus" / "circulars.jsonl"
        index_dir = ROOT / "data" / "index"
        models = {"embedder": "HashEmbedder", "reranker": "LexicalReranker"}
    else:
        golden = load_golden(args.golden)
        issues = validate_golden(golden)
        for issue in issues:
            level = getattr(issue, "severity", "error").upper()
            print(f"{level} {issue.item_id}: {issue.message}", file=sys.stderr)
        # Warnings are handled conditions (unjudged rows are excluded from the
        # metric, not scored 0); only corruption blocks measurement.
        if any(getattr(i, "severity", "error") == "error" for i in issues):
            raise SystemExit(1)
        from sebi_rag.api import _compute_kwargs
        from sebi_rag.settings import Settings

        ck = _compute_kwargs(Settings.load())
        emb = BGEM3Embedder(**ck)
        index_dir = Path(args.index_dir) if args.index_dir else ROOT / "data" / "index"
        retr = HybridRetriever.load(index_dir, emb)
        lin = build_lineage(load_records(ROOT / "data" / "corpus" / "circulars.jsonl"))
        if args.reranker == "jina":
            from sebi_rag.rerank import JinaMLXReranker

            reranker = JinaMLXReranker()
            reranker_name = "jinaai/jina-reranker-v3-mlx"
        else:
            reranker = CrossEncoderReranker(**ck)
            reranker_name = "BAAI/bge-reranker-v2-m3"
        pipeline = RAGPipeline(
            retriever=retr,
            reranker=reranker,
            generator=ExtractiveStubGenerator(),
            lineage=lin,
        )
        corpus_path = ROOT / "data" / "corpus" / "circulars.jsonl"
        # index_dir already resolved above from --index-dir; do not reset it
        # here or the metadata would credit the production index for an arm.
        models = {
            "embedder": "BAAI/bge-m3",
            "retriever": "FAISS+BM25/RRF",
            "reranker": reranker_name,
        }

    if args.no_expand:

        class _NoExpandRetriever:
            """iv2 control arm: force the BM25 leg to see the raw query.

            Innermost wrapper, so the HyDE/SPLADE wrappers below compose on
            top of it and their kwargs still reach HybridRetriever.retrieve.
            """

            def __init__(self, inner):
                object.__setattr__(self, "inner", inner)

            def retrieve(self, query: str, **kw):
                return self.inner.retrieve(query, expand_sparse=False, **kw)

            def __getattr__(self, name):
                return getattr(object.__getattribute__(self, "inner"), name)

            def __setattr__(self, name, value):
                setattr(object.__getattribute__(self, "inner"), name, value)

        pipeline.retriever = _NoExpandRetriever(pipeline.retriever)  # pyright: ignore[reportAttributeAccessIssue]

    hyde_log: dict[str, str] = {}
    if args.hyde:
        from sebi_rag.hyde import HydeExpander

        # --smoke stays offline: stub passage instead of loading MLX.
        expander = (
            HydeExpander(lambda p: "nomination of beneficiary provision")
            if args.smoke
            else HydeExpander.load()
        )

        class _HydeRetriever:
            def __init__(self, inner):
                self.inner = inner

            def retrieve(self, query: str, top_n: int = 50):
                h = expander.hypothesize(query)
                hyde_log[query] = h
                return self.inner.retrieve(query, top_n=top_n,
                                           hyde_text=h or None)

        pipeline.retriever = _HydeRetriever(pipeline.retriever)  # pyright: ignore[reportAttributeAccessIssue]

    if args.splade:
        from sebi_rag.splade import SpladeIndex
        from sebi_rag.splade_encoder import SpladeEncoder

        # --smoke stays offline: a trivial fake encoder over a tiny vocab.
        if args.smoke:
            import numpy as np
            from scipy.sparse import csr_matrix
            n = len(pipeline.retriever.chunks)
            fake_mat = csr_matrix(np.ones((n, 4), dtype="float32"))
            si = SpladeIndex(lambda ts: csr_matrix(np.ones((len(ts), 4), "float32")), 4)
            si.matrix = fake_mat
        else:
            enc = SpladeEncoder.load()
            si = SpladeIndex.load(index_dir, enc,
                                  expected_n=len(pipeline.retriever.chunks))
        pipeline.retriever.splade = si  # pyright: ignore[reportAttributeAccessIssue]

        class _SpladeRetriever:
            def __init__(self, inner):
                self.inner = inner
                self.chunks = inner.chunks

            def retrieve(self, query: str, top_n: int = 50):
                return self.inner.retrieve(query, top_n=top_n, use_splade=True)

        pipeline.retriever = _SpladeRetriever(pipeline.retriever)

    if args.rerank:

        class _RerankedRetriever:
            """Outermost wrapper: mirrors pipeline.query's retrieve->rerank.

            Applied last so it reranks whatever pool the arms below produced.
            """

            def __init__(self, inner, reranker):
                self.inner = inner
                self.reranker = reranker

            def retrieve(self, query: str, top_n: int = 50, **kw):
                cands = self.inner.retrieve(query, top_n=top_n, **kw)
                return self.reranker.rerank(query, [c for c, _ in cands])

        pipeline.retriever = _RerankedRetriever(pipeline.retriever, pipeline.reranker)  # pyright: ignore[reportAttributeAccessIssue]

    result = run_retrieval_benchmark(
        pipeline, golden, top_n=args.top_n, run_name="baseline-retrieval"
    )
    write_trec_run(out / "run.trec", "baseline-retrieval", result["rankings"])
    # Valid 6-field TREC alongside the legacy file, which embeds headings in the
    # doc id and cannot be read by trec_eval / ir_measures.
    write_run_chunk(out / "run.chunk.trec", "baseline-retrieval", result["rankings"])
    write_run_doc(out / "run.doc.trec", "baseline-retrieval", result["rankings"])
    write_docids(out / "docids.tsv", result["rankings"])
    result_no_rankings = {k: v for k, v in result.items() if k != "rankings"}
    meta = run_metadata(
        root=ROOT,
        corpus_path=corpus_path,
        index_dir=index_dir,
        golden_path=args.golden if not args.smoke else corpus_path,
        run_name="baseline-retrieval",
        models=models,
        params={"top_n": args.top_n, "smoke": args.smoke, "hyde": args.hyde,
                "splade": args.splade, "expand_sparse": not args.no_expand,
                "rerank": args.rerank},
        started_at=started,
    )
    (out / "results.json").write_text(
        json.dumps({"metrics": result_no_rankings, "metadata": meta}, indent=2),
        encoding="utf-8",
    )
    if args.hyde:
        with (out / "hyde.jsonl").open("w", encoding="utf-8") as f:
            for item in golden:
                f.write(json.dumps({
                    "id": item["id"],
                    "query": item["query"],
                    "hyde": hyde_log.get(item["query"], ""),
                }, ensure_ascii=False) + "\n")
    print(json.dumps({"out": str(out), **result_no_rankings}, indent=2))


if __name__ == "__main__":
    main()
