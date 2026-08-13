"""Derive CI gate floors from the golden_v7 adjudicated subset (spec sec 8).

Writes `eval/golden/gate_v7.json`, which IS the flip switch: `eval_json.py`
reports on golden_v7 only once this file exists with adjudicated_n >= 100.

Floors are the 2.5th-percentile bootstrap lower bound minus a small cushion,
not the observed mean. Gating on the mean would fail roughly half of all
reruns that changed nothing, since resampling noise puts the next run below
it about as often as above.

Scoring goes through `golden_v7.score.score_row`, the same path `eval_json.py`
uses - floors derived under different semantics than the measurements they
gate would be silently meaningless.

Real run (needs the persisted index + MPS models):
    make golden-v7-gate
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

from golden_v7.gate_select import MIN_ADJUDICATED_N  # noqa: E402
from golden_v7.score import score_row, vectors  # noqa: E402

DEFAULT_GOLDEN_PATH = ROOT / "eval" / "golden" / "golden_v7.jsonl"
DEFAULT_GATE_PATH = ROOT / "eval" / "golden" / "gate_v7.json"

# Cushion below the bootstrap lower bound, absorbing run-to-run jitter that is
# not a real regression (reranker nondeterminism, float drift).
_FLOOR_CUSHION = 0.005

# B' gates citation_precision alongside recall/recall_tradeoff/abstention.
# The filter improves precision but lowers citation_recall; the gate now
# protects both sides of that trade-off so a future regression is caught.
# nDCG@10 joins the gate (2026-08-12): recall_at_k is ceiling-limited at
# ~0.956, leaving ~9 failing queries of 216 and ~8 discordant queries per A/B
# — too few to detect anything. nDCG@10 scores 0.7044 on the same runs and
# moves on 95+ queries, so it is the metric that can actually catch a
# ranking regression. See docs/status.md §"recall@10 is the wrong primary
# metric".
# context_recall joins 2026-08-13: `recall` measures the pre-rerank fusion
# list, which overstates delivery by ~3pp and hides complete misses caused
# downstream by reranking and supersession demotion.
_GATED_METRICS = ("recall", "context_recall", "ndcg", "citation_recall",
                  "abstention", "citation_precision")
_FLOOR_NAMES = {"recall": "recall_at_k", "context_recall": "context_recall",
                "ndcg": "ndcg_at_10",
                "citation_recall": "citation_recall",
                "abstention": "abstention_accuracy", "citation_precision": "citation_precision"}


def derive_floors(per_query: dict[str, list[float]]) -> dict[str, float]:
    """metric -> per-query score vector, into gate-floor names -> floor value.

    Metrics with no scored queries are skipped rather than floored at 0: a
    floor of 0 is not a gate, it is decoration that always passes.
    """
    from sebi_rag.stats import bootstrap_ci

    floors = {}
    for metric in _GATED_METRICS:
        values = per_query.get(metric) or []
        if not values:
            continue
        ci = bootstrap_ci(values)
        floors[_FLOOR_NAMES[metric]] = round(max(0.0, ci.lo - _FLOOR_CUSHION), 4)
    return floors


def main() -> None:
    from sebi_rag.embeddings import BGEM3Embedder
    from sebi_rag.eval_harness import load_golden
    from sebi_rag.generate import SubjectSimJudge, citation_scorer_for, eval_generator_for
    from sebi_rag.lineage import build_lineage, load_records
    from sebi_rag.pipeline import RAGPipeline
    from sebi_rag.rerank import CrossEncoderReranker
    from sebi_rag.retrieve import HybridRetriever
    from sebi_rag.settings import Settings

    rows = load_golden(DEFAULT_GOLDEN_PATH)
    adjudicated = [r for r in rows if r.get("review_status") == "adjudicated"]
    n = len(adjudicated)
    if n < MIN_ADJUDICATED_N:
        print(f"adjudicated_n={n} < {MIN_ADJUDICATED_N}: refusing to arm the gate. "
              f"CI stays on golden_v5 until the external pass and arbitration "
              f"promote more rows.", file=sys.stderr)
        raise SystemExit(1)

    s = Settings.load()
    recs = load_records(s.corpus_path)
    lin = build_lineage(recs)
    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(s.index_dir, emb)
    rer = CrossEncoderReranker(device="mps")
    _sect = os.environ.get("SEBI_RAG_SECT_THRESHOLD", "0.60")
    judge = SubjectSimJudge(
        emb, threshold=float(os.environ.get("SEBI_RAG_SUBJ_THRESHOLD", "0.42")),
        section_threshold=(None if _sect.lower() in ("off", "0") else float(_sect)))
    # Constructed directly, NOT via RAGPipeline.build(): build() calls
    # HybridRetriever.build() and would re-embed the whole corpus, discarding
    # the persisted index these floors are meant to describe.
    pipeline = RAGPipeline(
        retriever=retr, reranker=rer,
        generator=eval_generator_for(s.eval_generator, s.mlx_model),
        abstain_threshold=s.abstain_threshold, lineage=lin, judge=judge,
        citation_scorer=citation_scorer_for(s.citation_scorer_enabled, rer,
                                            s.citation_scorer_backend),
        citation_margin=s.citation_margin)

    scored = [score_row(pipeline, item, s.top_k) for item in adjudicated]
    payload = {
        "adjudicated_n": n,
        "derived_at": dt.datetime.now().isoformat(timespec="seconds"),
        "floors": derive_floors(vectors(scored)),
    }
    DEFAULT_GATE_PATH.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"armed gate on {n} adjudicated rows -> {DEFAULT_GATE_PATH}")
    print(json.dumps(payload["floors"], indent=2))


if __name__ == "__main__":
    main()
