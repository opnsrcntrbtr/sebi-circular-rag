#!/usr/bin/env python3
"""CLI for automated metric collection via sebi_rag.measure.

Usage:
    python scripts/bench_metrics.py                          # run all metrics
    python scripts/bench_metrics.py --metrics mrr recall     # specific metrics
    python scripts/bench_metrics.py --smoke                  # fast offline mode
    python scripts/bench_metrics.py --json out.json          # JSONL output
    python scripts/bench_metrics.py --md report.md           # markdown output
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dataclasses import asdict
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

for k, v in {
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(k, v)

from sebi_rag.measure import (  # noqa: E402
    ALL_METRICS,
    MeasureReport,
    run_all_metrics,
)
from sebi_rag.embeddings import BGEM3Embedder, HashEmbedder  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.generate import ExtractiveStubGenerator  # noqa: E402
from sebi_rag.lineage import build_lineage, load_records  # noqa: E402
from sebi_rag.pipeline import RAGPipeline  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker, LexicalReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402

CORPUS = ROOT / "data" / "corpus" / "circulars.jsonl"
GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
INDEX = ROOT / "data" / "index"
DATA_DIR = ROOT / "data"


def smoke_pipeline() -> RAGPipeline:
    """Build a lightweight pipeline for --smoke mode.

    Uses a stub retriever (no FAISS) so retrieval metrics gracefully
    return 0 recall without crashing on dimension mismatches.
    """
    from unittest.mock import MagicMock

    retriever = MagicMock()
    retriever.retrieve.return_value = []
    reranker = LexicalReranker()
    generator = ExtractiveStubGenerator()
    lineage = []
    return RAGPipeline(
        retriever=retriever,
        reranker=reranker,
        generator=generator,
        lineage=lineage,
    )


def real_pipeline() -> RAGPipeline:
    """Build the full pipeline with real models."""
    from sebi_rag.settings import Settings
    from sebi_rag.api import _compute_kwargs, _embed_kwargs

    settings = Settings.load()
    ck = _compute_kwargs(settings)
    embedder = BGEM3Embedder(**_embed_kwargs(settings))
    retriever = HybridRetriever.load(INDEX, embedder)
    reranker = CrossEncoderReranker(**ck)
    generator = ExtractiveStubGenerator()
    lineage = build_lineage(load_records(CORPUS))
    return RAGPipeline(
        retriever=retriever,
        reranker=reranker,
        generator=generator,
        lineage=lineage,
    )


def metrics_to_markdown(results: list, elapsed: float) -> str:
    """Format results as a markdown table."""
    lines = [
        "# SEBI RAG — Metric Collection Report",
        f"\nGenerated: {datetime.now(timezone.utc).isoformat()}",
        f"\nElapsed: {elapsed:.1f}s\n",
        "| Metric | Value | Sample Size |",
        "|---|---|---|",
    ]
    for r in results:
        val_str = json.dumps(r.value, default=str)
        lines.append(f"| {r.metric} | {val_str} | {r.sample_size} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Automated metric collection for SEBI RAG pipeline"
    )
    ap.add_argument(
        "--metrics",
        nargs="+",
        default=list(ALL_METRICS.keys()),
        help="Metrics to run (default: all)",
    )
    ap.add_argument(
        "--smoke",
        action="store_true",
        help="Use lightweight smoke pipeline (HashEmbedder + LexicalReranker)",
    )
    ap.add_argument(
        "--json",
        dest="json_out",
        metavar="FILE",
        help="Write JSONL results to file",
    )
    ap.add_argument(
        "--md",
        dest="md_out",
        metavar="FILE",
        help="Write markdown summary to file",
    )
    ap.add_argument(
        "--data-dir",
        default=str(DATA_DIR),
        help="Data directory (default: data/)",
    )
    ap.add_argument(
        "--corpus",
        default=str(CORPUS),
        help="Corpus path (default: data/corpus/circulars.jsonl)",
    )
    ap.add_argument(
        "--golden",
        default=str(GOLDEN),
        help="Golden set path (default: eval/golden/golden_v7.jsonl)",
    )
    args = ap.parse_args()

    # Validate metric names
    invalid = [m for m in args.metrics if m not in ALL_METRICS]
    if invalid:
        print(f"ERROR: unknown metrics: {invalid}", file=sys.stderr)
        print(f"Available: {list(ALL_METRICS.keys())}", file=sys.stderr)
        sys.exit(1)

    # Build pipeline
    build_fn = smoke_pipeline if args.smoke else real_pipeline
    print(f"Building pipeline (smoke={args.smoke})...", flush=True)
    t_start = time.time()
    pipeline = build_fn()
    t_build = time.time() - t_start
    print(f"Pipeline built in {t_build:.1f}s", flush=True)

    # Load golden
    print(f"Loading golden set: {args.golden}", flush=True)
    golden_rows = load_golden(args.golden)
    print(f"Loaded {len(golden_rows)} golden rows", flush=True)

    # Run metrics
    print(f"Running metrics: {args.metrics}", flush=True)
    results = run_all_metrics(
        pipeline=pipeline,
        golden_rows=golden_rows,
        corpus_path=args.corpus,
        data_dir=args.data_dir,
        metrics=args.metrics,
    )

    elapsed = time.time() - t_start

    # Print results
    print(f"\n{'='*60}", flush=True)
    print(f"Metrics collected in {elapsed:.1f}s (pipeline build: {t_build:.1f}s)", flush=True)
    print(f"{'='*60}", flush=True)

    for r in results:
        print(f"\n[{r.metric}] sample_size={r.sample_size}", flush=True)
        print(f"  value={json.dumps(r.value, default=str, indent=4)}", flush=True)

    # JSONL output
    if args.json_out:
        out_path = Path(args.json_out)
        report = MeasureReport.from_results(results, root=args.data_dir)
        records = [
            {
                "type": "report",
                "data": asdict(report),
            },
            *[
                {
                    "type": "metric",
                    "metric": r.metric,
                    "value": r.value,
                    "sample_size": r.sample_size,
                }
                for r in results
            ],
        ]
        with out_path.open("w") as f:
            for rec in records:
                f.write(json.dumps(rec, default=str) + "\n")
        print(f"\nJSONL written to {out_path}", flush=True)

    # Markdown output
    if args.md_out:
        md = metrics_to_markdown(results, elapsed)
        out_path = Path(args.md_out)
        out_path.write_text(md, encoding="utf-8")
        print(f"Markdown written to {out_path}", flush=True)

    # Print markdown to stdout too
    print(f"\n{metrics_to_markdown(results, elapsed)}", flush=True)


if __name__ == "__main__":
    main()
