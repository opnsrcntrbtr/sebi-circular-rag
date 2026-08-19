"""Ground truth: what do the 4 CE_MISMATCH rows actually DO in production?

The 2026-08-18 score-floor diagnostic classified rows by comparing the
cross-encoder `ce_top` against 0.42. 0.42 is the *SubjectSimJudge* threshold
(`generate.py:322`), a cosine subject-similarity floor on a different scale.
The cross-encoder score floor is `Settings.abstain_threshold` = **0.05**
(`settings.py:66`, `config.toml [service]`), used by both the API
(`api.py:150`) and the eval harness (`eval_json.py:66`).

This script replaces classification-by-constant with observation: it builds the
production pipeline exactly as `eval_json.py` does and reports, per row, what
the pipeline actually returns — abstained or not, the abstention reason, and
the confidence signals the gates fired on.

Read-only. Usage: PYTHONPATH=src python scripts/analysis/abstention_reason_check.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

for _k, _v in {
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(_k, _v)

from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.generate import (  # noqa: E402
    SubjectSimJudge, citation_scorer_for, eval_generator_for,
)
from sebi_rag.lineage import build_lineage, load_records  # noqa: E402
from sebi_rag.pipeline import RAGPipeline  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.settings import Settings  # noqa: E402

TARGET_IDS = ["para-mfmaster", "para-glitch", "para-mfborrow", "para-pricedata"]
DEST = ROOT / "reports" / "abstention-reason-check-2026-08-19.json"


def main() -> None:
    s = Settings.load()
    print(f"abstain_threshold (CE score floor) = {s.abstain_threshold}", file=sys.stderr)
    recs = load_records(s.corpus_path)
    lin = build_lineage(recs)
    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(s.index_dir, emb)
    rer = CrossEncoderReranker(device="mps")
    judge = SubjectSimJudge(emb, threshold=0.42, section_threshold=0.60)
    pipeline = RAGPipeline(
        retriever=retr, reranker=rer,
        generator=eval_generator_for(s.eval_generator, s.mlx_model),
        abstain_threshold=s.abstain_threshold, lineage=lin, judge=judge,
        citation_scorer=citation_scorer_for(s.citation_scorer_enabled, rer,
                                            s.citation_scorer_backend),
        citation_margin=s.citation_margin)

    golden = {r["id"]: r for r in
              load_golden(ROOT / "eval" / "golden" / "golden_v7.jsonl")}

    out = {"abstain_threshold": s.abstain_threshold,
           "subject_sim_threshold": 0.42, "rows": []}
    for rid in TARGET_IDS:
        row = golden[rid]
        ans, _ = pipeline.query(row["query"], top_k=s.top_k)
        rel = set(row.get("relevant_circulars") or [])
        cited_docs = {c.split("#")[0] for c in ans.citations}
        entry = {
            "id": rid,
            "expected_abstain": bool(row.get("abstain", False)),
            "abstained": ans.abstained,
            "abstention_reason": ans.abstention_reason,
            "confidence": ans.confidence,
            "relevant": sorted(rel),
            "cited_relevant": sorted(cited_docs & rel),
            "n_citations": len(ans.citations),
        }
        out["rows"].append(entry)
        print(f"\n{rid}")
        print(f"  expected_abstain = {entry['expected_abstain']}")
        print(f"  abstained        = {ans.abstained}  reason={ans.abstention_reason!r}")
        print(f"  confidence       = {ans.confidence}")
        print(f"  cited relevant   = {entry['cited_relevant']} "
              f"(of {len(ans.citations)} citations)")

    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {DEST}", file=sys.stderr)


if __name__ == "__main__":
    main()
