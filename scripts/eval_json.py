"""Emit one JSON line of retrieval/citation/abstention metrics using the
persisted index.

The generator is whatever `config.toml [service] eval_generator` names, routed
through `generate.eval_generator_for` - currently "mlx", i.e. THIS RUNS A REAL
LLM. (This docstring said "no LLM, no Ollama" until 2026-08-20; that described
the "stub" setting, which is not what the gate uses and has not been since the
2026-08-12 re-derivation. The claim had already propagated into
docs/project_context.md 7.5.)

Golden-set resolution (spec 2026-07-23 sec 8): SEBI_RAG_GOLDEN if set, else
golden_v7 once `eval/golden/gate_v7.json` arms it (adjudicated_n >= 100),
else frozen golden_v5. CI therefore keeps reporting comparable numbers on v5
until the v7 adjudicated subset is large enough to gate on.

Scoring runs through the real RAGPipeline, so
abstention matches PRODUCTION by construction rather than by re-implementing
the score floor and subject-sim gate here. `golden_v7.score.score_row` is the
same path `derive_thresholds.py` uses to set the floors these numbers are
compared against. Also reports injection_flagged (F4).

Model/progress noise goes to stderr; the single JSON object is the only
stdout line, for n8n to parse.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.generate import SubjectSimJudge, citation_scorer_for, eval_generator_for  # noqa: E402
from sebi_rag.ingest_pdf import injection_scan  # noqa: E402
from sebi_rag.lineage import build_lineage, load_records  # noqa: E402
from sebi_rag.pipeline import RAGPipeline  # noqa: E402
from sebi_rag.rerank import CrossEncoderReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.settings import Settings  # noqa: E402

from golden_v7.gate_select import floors_ok, select_golden  # noqa: E402
from golden_v7.score import score_row, vectors  # noqa: E402

GATE_PATH = ROOT / "eval" / "golden" / "gate_v7.json"
V5_PATH = ROOT / "eval" / "golden" / "golden_v5.jsonl"
V7_PATH = ROOT / "eval" / "golden" / "golden_v7.jsonl"

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
# HybridRetriever.build() and would re-embed the whole corpus instead of
# using the persisted index.
pipeline = RAGPipeline(
    retriever=retr, reranker=rer,
    generator=eval_generator_for(s.eval_generator, s.mlx_model),
    abstain_threshold=s.abstain_threshold, lineage=lin, judge=judge,
    citation_scorer=citation_scorer_for(s.citation_scorer_enabled, rer,
                                        s.citation_scorer_backend),
    citation_margin=s.citation_margin)

golden_path = select_golden(os.environ, GATE_PATH, V5_PATH, V7_PATH)
golden = load_golden(golden_path)

scored = [score_row(pipeline, item, s.top_k) for item in golden]
overall = vectors(scored)

# Opt-in per-row dump. Aggregates below are unchanged; this only stops the
# per-row records being discarded, so an arm's result can be decomposed by
# stratum / label_tier after the fact instead of needing a full re-run.
_rows_dest = os.environ.get("SEBI_RAG_EVAL_ROWS")
if _rows_dest:
    _by_id = {i.get("id"): i for i in golden}
    Path(_rows_dest).parent.mkdir(parents=True, exist_ok=True)
    Path(_rows_dest).write_text(json.dumps({
        "generator": s.mlx_model if s.eval_generator == "mlx" else s.eval_generator,
        "eval_generator": s.eval_generator,
        "golden": str(golden_path),
        "top_k": s.top_k,
        "rows": [dict(r,
                      task_type=_by_id.get(r.get("id"), {}).get("task_type"),
                      label_tier=_by_id.get(r.get("id"), {}).get("label_tier"))
                 for r in scored],
    }, indent=2), encoding="utf-8")
    print(f"wrote {len(scored)} per-row records to {_rows_dest}", file=sys.stderr)

mean = lambda xs: round(sum(xs) / len(xs), 3) if xs else 0.0

adjudicated_n = sum(1 for r in scored if r["adjudicated"])
gate_report = None
if adjudicated_n:
    g = vectors(scored, adjudicated_only=True)
    gate_report = {
        "n": adjudicated_n,
        "recall_at_k": mean(g["recall"]),
        "context_recall": mean(g["context_recall"]),
        "ndcg_at_10": mean(g["ndcg"]),
        "citation_precision": mean(g["citation_precision"]),
        "citation_recall": mean(g["citation_recall"]),
        "abstention_accuracy": mean(g["abstention"]),
    }
    # floors_ok is only meaningful when the armed gate file supplied floors;
    # on the v5 fallback there are none to check, so it stays null rather
    # than reporting a vacuous pass.
    try:
        floors = json.loads(GATE_PATH.read_text(encoding="utf-8"))["floors"]
    except (OSError, ValueError, KeyError, TypeError):
        floors = None
    gate_report["floors_ok"] = floors_ok(gate_report, floors) if floors else None

print(json.dumps({
    "ts": dt.datetime.now().isoformat(timespec="seconds"),
    "circulars": len({r["circular_number"] for r in recs}),
    "chunks": len(retr.chunks),
    "golden_items": len(golden),
    "top_k": s.top_k,
    "recall_at_10": mean(overall["recall"]),
    "context_recall": mean(overall["context_recall"]),
    "ndcg_at_10": mean(overall["ndcg"]),
    "citation_precision": mean(overall["citation_precision"]),
    "citation_recall": mean(overall["citation_recall"]),
    "abstention_accuracy": mean(overall["abstention"]),
    # live scan (older records predate the stored injection_flags field);
    # known-benign baseline = 1 (broker master's password-policy text)
    "injection_flagged": sum(1 for r in recs if injection_scan(r.get("text", ""))),
    "golden_file": str(golden_path),
    "adjudicated_n": adjudicated_n,
    "gate": gate_report,
}))
