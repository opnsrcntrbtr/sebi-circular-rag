"""Phase 1 (systematic-debugging) evidence gathering for the 2026-09-03
abstention_accuracy gate failure (observed 0.919 vs armed floor 0.9373,
eval/runs/live-stack-eval-2026-09-03.json).

CORRECTED 2026-09-03: the first version of this script copied
`derive_thresholds.py`'s pipeline-construction pattern verbatim, which passes
`reranker=rer` (the raw CrossEncoderReranker, i.e. bge) directly - a pattern
that is CORRECT for derive_thresholds.py (deliberate, fixed bge floor
baseline, docs/status.md:907) but WRONG for a script meant to reproduce what
`eval_json.py`/production actually measure. This version routes through
`retrieval_reranker_for(s.reranker_model, rer)`, exactly like `api.py` and
`eval_json.py` do, so it measures the jina-reranked system that actually
failed the gate, not the bge one the gate's floors are fixed to.

Records, per golden_v7 row: expected vs. actual abstain decision,
`abstention_reason`, and the full `confidence` dict (rerank_top, margin,
subject_sim, section_sim) for every mismatch - the inputs to
`answer_with_abstention`'s gate logic in generate.py.

Usage:
    PYTHONPATH=src python scripts/analysis/abstention_mismatch_audit.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

GOLDEN_PATH = ROOT / "eval" / "golden" / "golden_v7.jsonl"
OUT_PATH = ROOT / "reports" / "abstention-mismatch-audit-jina-2026-09-03.json"


def main() -> None:
    from sebi_rag.embeddings import BGEM3Embedder
    from sebi_rag.eval_harness import load_golden
    from sebi_rag.generate import SubjectSimJudge, citation_scorer_for, eval_generator_for
    from sebi_rag.lineage import build_lineage, load_records
    from sebi_rag.pipeline import RAGPipeline
    from sebi_rag.rerank import CrossEncoderReranker, retrieval_reranker_for
    from sebi_rag.retrieve import HybridRetriever
    from sebi_rag.settings import Settings

    s = Settings.load()
    recs = load_records(s.corpus_path)
    lin = build_lineage(recs)
    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(s.index_dir, emb)
    rer = CrossEncoderReranker(device="mps")
    # ADR-004: which model orders the RETRIEVAL pool must match what api.py /
    # eval_json.py use, or this script silently measures a configuration
    # production no longer serves (the exact bug this script had until
    # 2026-09-03 - see module docstring).
    retrieval_reranker = retrieval_reranker_for(s.reranker_model, rer)
    _sect = os.environ.get("SEBI_RAG_SECT_THRESHOLD", "0.60")
    judge = SubjectSimJudge(
        emb, threshold=float(os.environ.get("SEBI_RAG_SUBJ_THRESHOLD", "0.42")),
        section_threshold=(None if _sect.lower() in ("off", "0") else float(_sect)))
    pipeline = RAGPipeline(
        retriever=retr, reranker=retrieval_reranker,
        generator=eval_generator_for(s.eval_generator, s.mlx_model),
        abstain_threshold=s.abstain_threshold, lineage=lin, judge=judge,
        citation_scorer=citation_scorer_for(s.citation_scorer_enabled, rer,
                                            s.citation_scorer_backend),
        citation_margin=s.citation_margin)

    rows = load_golden(GOLDEN_PATH)
    per_row = []
    mismatches = []
    for item in rows:
        expected_abstain = bool(item.get("abstain"))
        ans, _ = pipeline.query(item["query"], top_k=s.top_k, as_of=item.get("as_of"))
        correct = ans.abstained == expected_abstain
        rec = {
            "id": item["id"],
            "task_type": item.get("task_type"),
            "review_status": item.get("review_status"),
            "expected_abstain": expected_abstain,
            "actual_abstained": ans.abstained,
            "correct": correct,
            "abstention_reason": ans.abstention_reason,
            "confidence": ans.confidence,
        }
        per_row.append(rec)
        if not correct:
            mismatches.append(rec)
        print(f"{'OK ' if correct else 'MISS'} {item['id']:20} "
              f"expected={expected_abstain} actual={ans.abstained} "
              f"reason={ans.abstention_reason!r}", file=sys.stderr)

    n = len(per_row)
    n_correct = sum(1 for r in per_row if r["correct"])
    payload = {
        "derived_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "n": n,
        "n_correct": n_correct,
        "abstention_accuracy": n_correct / n if n else 0.0,
        "n_mismatches": len(mismatches),
        "mismatches": mismatches,
        "per_row": per_row,
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT_PATH}", file=sys.stderr)
    print(json.dumps({k: v for k, v in payload.items()
                       if k not in ("per_row", "mismatches")}, indent=2))
    print(json.dumps(mismatches, indent=2))


if __name__ == "__main__":
    main()
