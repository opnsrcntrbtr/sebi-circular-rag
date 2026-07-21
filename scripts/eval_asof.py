"""Run eval/golden/golden_asof_v1.jsonl (selector + pipeline modes) against the
persisted index (env SEBI_RAG_GOLDEN_ASOF to override the golden file).

Selector cases exercise Lineage.governing_on directly and are regression
tests only (see sebi_rag.eval_asof module docstring: the lineage graph is one
giant connected component from master reference-list over-tagging, so
governing_on is meaningful only for these pre-verified small families).

Pipeline cases exercise RAGPipeline.query(as_of=...) end-to-end over the
persisted retriever + cross-encoder reranker. Generation uses
ExtractiveStubGenerator (no LLM dependency) since as-of filtering acts on
retrieval ranking, not generation; pipeline-case failures are eval findings,
not implementation bugs to chase.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

from sebi_rag.benchmark import run_metadata  # noqa: E402
from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.eval_asof import (  # noqa: E402
    build_report, load_golden_asof, run_pipeline_cases, run_selector_cases,
)
from sebi_rag.generate import ExtractiveStubGenerator  # noqa: E402
from sebi_rag.lineage import Lineage, load_records  # noqa: E402
from sebi_rag.pipeline import RAGPipeline  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.settings import Settings  # noqa: E402

started = time.time()
s = Settings.load()
emb = BGEM3Embedder(device="mps")
retr = HybridRetriever.load(s.index_dir, emb)
rer = CrossEncoderReranker(device="mps")
lin = Lineage.load(Path(s.index_dir) / "lineage.json")
recs = load_records(s.corpus_path)
dates = {r["circular_number"]: r.get("issue_date", "") for r in recs}

pipeline = RAGPipeline(
    retriever=retr, reranker=rer, generator=ExtractiveStubGenerator(),
    abstain_threshold=s.abstain_threshold, lineage=lin,
)

golden_path = os.environ.get(
    "SEBI_RAG_GOLDEN_ASOF", str(ROOT / "eval" / "golden" / "golden_asof_v1.jsonl"))
run_name = os.environ.get("ASOF_OUT", "baseline")

cases = load_golden_asof(golden_path)
selector_results = run_selector_cases(lin, dates, cases)
pipeline_results = run_pipeline_cases(pipeline, cases)

report = build_report(selector_results, pipeline_results, run_metadata(
    root=ROOT,
    corpus_path=s.corpus_path,
    index_dir=s.index_dir,
    golden_path=golden_path,
    run_name=f"asof-{run_name}",
    models={"embedder": "BAAI/bge-m3",
            "retriever": "FAISS+BM25/RRF",
            "reranker": "BAAI/bge-reranker-v2-m3",
            "generator": "ExtractiveStubGenerator"},
    params={"abstain_threshold": s.abstain_threshold},
    started_at=started,
))

out = ROOT / "eval" / "runs" / f"asof-{run_name}"
out.mkdir(parents=True, exist_ok=True)
(out / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

print(json.dumps({**report["metrics"], "out": str(out)}, indent=2))
