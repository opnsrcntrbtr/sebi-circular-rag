"""B' citation-scorer cohort measurement: control (bge, pointwise) vs J1 (jina, listwise).

Spec: docs/superpowers/specs/2026-08-25-jina-citation-scorer-prereg.md.

Cohort: golden_v7 rows that are answerable, non-as_of, have relevant_circulars, AND whose
retrieval pool (top_n=50) contains every gold document — "perfect retrieval". Recomputed on
the live index every run (spec §4 / R1 §4 precedent: not a stored artifact, index-dependent).

Arms (spec §5):
  control  citation_scorer_for(backend="reranker")  — bge-reranker-v2-m3, pointwise, production
           default when B' is armed
  J1       citation_scorer_for(backend="jina")       — jina-reranker-v3-mlx, listwise

Both arms score the SAME answer text and the SAME context window (spec §3: single variable is
the scorer object; generator, retrieval, top_k, dedup, superseded_penalty, margin, min_keep all
held fixed). The 1.5B generator is deterministic (greedy decoding), so it runs ONCE per row and
its output is reused for both arms.

Unlike scripts/analysis/warrant_scorer_cohort.py (a 7B LLM judge, run in its own process so the
1.5B generator and the 7B judge are never resident together), jina-reranker-v3-mlx is a plain
reranker forward pass with no LLM call and no residency conflict with the 1.5B generator (spec
§2, §9) — control and J1 citations are both computed in the SAME phase, immediately after each
row's answer is generated. Two phases, not three: "generate" (produces the answer once and both
arms' citations against it), "report" (reads the dump, computes deltas, applies the spec's §6
decision rule mechanically).

Usage:
  PYTHONPATH=src python scripts/analysis/jina_citation_scorer_cohort.py --phase generate
  PYTHONPATH=src python scripts/analysis/jina_citation_scorer_cohort.py --phase report
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

for _k, _v in {
    "TOKENIZERS_PARALLELISM": "false",
    "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1",
    "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(_k, _v)

GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
GATE = ROOT / "eval" / "golden" / "gate_v7.json"
GENERATE_DUMP = ROOT / "reports" / "jina-citation-cohort-generate.json"
DEST = ROOT / "reports" / "jina-citation-scorer-cohort-2026-08-25.json"

POOL, TOP_K = 50, 10
CITATION_PRECISION_EFFECT_FLOOR = 0.02  # spec §6, fixed in advance (matches R1's floor)


def eligible(item: dict) -> bool:
    """Answerable, non-as_of, with gold citations. Matches warrant_scorer_cohort.py's
    predicate exactly, for direct comparability of cohort composition across B' arms."""
    return (not item.get("abstain")
            and not item.get("as_of")
            and bool(item.get("relevant_circulars")))


def _measure(relevant: set[str], abstained: bool, context_ids: list[str],
             citations: list[str]) -> dict:
    from sebi_rag.eval_harness import _doc, _unique

    context_docs = _unique(_doc(i) for i in context_ids)
    cited = [] if abstained else _unique(_doc(c) for c in citations)
    hit = len(set(cited) & relevant)
    return {
        "zero_cite": hit == 0,
        "citation_recall": hit / len(relevant),
        "citation_precision": (hit / len(cited)) if cited else 0.0,
        "context_recall": (len(set(context_docs) & relevant) / len(relevant)
                           if context_docs else 0.0),
        "n_cited": len(cited),
    }


def phase_generate() -> None:
    from sebi_rag.api import build_default_pipeline
    from sebi_rag.eval_harness import _doc, load_golden
    from sebi_rag.generate import citation_scorer_for, select_citations
    from sebi_rag.rerank import JinaMLXReranker

    pipe = build_default_pipeline()
    # Explicit, not config-dependent: control is bge regardless of what config.toml's
    # citation_scorer_backend currently has (matches warrant_scorer_cohort.py's convention).
    # pipe.reranker may already be jina (ADR-004 production default orders retrieval); the
    # control B' scorer must always be bge regardless, so build it explicitly rather than
    # reusing pipe.reranker.
    from sebi_rag.rerank import CrossEncoderReranker
    bge = CrossEncoderReranker()
    control_scorer = citation_scorer_for(True, bge, backend="reranker")
    print("loading jina-reranker-v3-mlx for J1 citation scoring...", file=sys.stderr)
    j1_scorer = citation_scorer_for(True, None, backend="jina",
                                    jina_loader=JinaMLXReranker)
    pipe.citation_scorer = control_scorer

    items = [i for i in load_golden(GOLDEN) if eligible(i)]
    print(f"eligible answerable non-as_of rows: {len(items)}", file=sys.stderr)

    # --- cohort determination (retrieval only, arm-independent) --------------
    cohort = []
    for it in items:
        cand = pipe.retriever.retrieve(it["query"], top_n=POOL)
        pool_docs = {_doc(c.id) for c, _ in cand}
        if set(it["relevant_circulars"]).issubset(pool_docs):
            cohort.append(it)
    print(f"perfect-retrieval cohort: {len(cohort)} of {len(items)} "
          f"(recomputed on the live index; not quoted from a prior run)", file=sys.stderr)

    limit = int(os.environ.get("SEBI_COHORT_LIMIT", "0"))
    if limit:
        cohort = cohort[:limit]
        print(f"SEBI_COHORT_LIMIT set: truncated cohort to {len(cohort)} rows (smoke test)",
              file=sys.stderr)

    chunk_by_id = {c.id: c for c in pipe.retriever.chunks}  # built once, not per row
    rows, t0 = [], time.time()
    for n, it in enumerate(cohort, 1):
        ans, _ = pipe.query(it["query"], pool=POOL, top_k=TOP_K)
        relevant = set(it["relevant_circulars"])
        control_measure = _measure(relevant, ans.abstained, ans.context_ids, ans.citations)

        if ans.abstained or not ans.context_ids:
            j1_citations, j1_measure = [], _measure(relevant, ans.abstained, ans.context_ids, [])
        else:
            # preserve context_ids order, not chunk-store order
            contexts = [chunk_by_id[cid] for cid in ans.context_ids if cid in chunk_by_id]
            j1_citations = select_citations(ans.text, contexts, j1_scorer,
                                            margin=pipe.citation_margin,
                                            min_keep=pipe.citation_min_keep,
                                            query=it["query"])
            j1_measure = _measure(relevant, ans.abstained, ans.context_ids, j1_citations)

        rows.append({
            "id": it["id"], "task_type": it.get("task_type"),
            "label_tier": it.get("label_tier"), "query": it["query"],
            "relevant_circulars": it["relevant_circulars"],
            "abstained": bool(ans.abstained), "answer_text": ans.text,
            "context_ids": list(ans.context_ids),
            "control_citations": list(ans.citations), "control_measure": control_measure,
            "j1_citations": j1_citations, "j1_measure": j1_measure,
        })
        if n % 25 == 0:
            print(f"  {n}/{len(cohort)}  ({time.time() - t0:.0f}s)", file=sys.stderr)

    out = {
        "cohort_n": len(cohort), "eligible_n": len(items),
        "citation_margin": pipe.citation_margin,
        "citation_min_keep": pipe.citation_min_keep,
        "generator_model": pipe.generator.__class__.__name__,
        "runtime_s": round(time.time() - t0, 1),
        "rows": rows,
    }
    GENERATE_DUMP.parent.mkdir(parents=True, exist_ok=True)
    GENERATE_DUMP.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {GENERATE_DUMP} (cohort_n={len(cohort)}, {out['runtime_s']}s)",
          file=sys.stderr)


def _aggregate(rows: list[dict], measure_key: str) -> dict:
    n = len(rows)
    mean = lambda k: round(sum(r[measure_key][k] for r in rows) / n, 4) if n else 0.0  # noqa: E731
    return {
        "n": n,
        "zero_cite": sum(r[measure_key]["zero_cite"] for r in rows),
        "citation_recall": mean("citation_recall"),
        "citation_precision": mean("citation_precision"),
        "context_recall": mean("context_recall"),
        "abstained": sum(r["abstained"] for r in rows),
    }


def phase_report() -> None:
    if not GENERATE_DUMP.exists():
        raise SystemExit(f"{GENERATE_DUMP} missing — run --phase generate first")
    gen = json.loads(GENERATE_DUMP.read_text())
    gate_floor = json.loads(GATE.read_text())["floors"]["citation_recall"]

    rows = gen["rows"]
    control_summary = _aggregate(rows, "control_measure")
    j1_summary = _aggregate(rows, "j1_measure")
    delta = {k: round(j1_summary[k] - control_summary[k], 4) for k in
             ("zero_cite", "citation_recall", "citation_precision", "context_recall")}

    # --- confirmatory: split by label_tier (CS1) ---------------------------
    tiers: dict[str, list[dict]] = {}
    for r in rows:
        tiers.setdefault(r.get("label_tier") or "unknown", []).append(r)
    by_tier = {
        tier: {"n": len(rs), "control": _aggregate(rs, "control_measure"),
               "j1": _aggregate(rs, "j1_measure")}
        for tier, rs in sorted(tiers.items())
    }

    # --- §6 decision rule, evaluated mechanically ------------------------------
    verdict, reasons = "PROCEED to §7 full-gate confirmation", []
    precision_gain = j1_summary["citation_precision"] - control_summary["citation_precision"]
    if precision_gain < CITATION_PRECISION_EFFECT_FLOOR:
        verdict = "REJECT"
        reasons.append(f"6.1: citation_precision gained {precision_gain:.4f}, "
                        f"needs >= {CITATION_PRECISION_EFFECT_FLOOR}")
    if j1_summary["zero_cite"] > control_summary["zero_cite"]:
        verdict = "REJECT"
        reasons.append(f"6.2: zero_cite rose {control_summary['zero_cite']} -> "
                        f"{j1_summary['zero_cite']} (zero tolerance on increase)")
    if j1_summary["citation_recall"] < gate_floor:
        verdict = "REJECT"
        reasons.append(f"6.3: J1 citation_recall {j1_summary['citation_recall']} "
                        f"< armed floor {gate_floor} (gate_v7.json)")

    out = {
        "spec": "docs/superpowers/specs/2026-08-25-jina-citation-scorer-prereg.md §§4-6",
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "cohort_n": gen["cohort_n"], "eligible_n": gen["eligible_n"],
        "citation_margin": gen["citation_margin"], "citation_min_keep": gen["citation_min_keep"],
        "answer_generator": gen["generator_model"],
        "gate_floor_citation_recall": gate_floor,
        "effect_size_floor_citation_precision": CITATION_PRECISION_EFFECT_FLOOR,
        "control": control_summary, "j1": j1_summary, "delta": delta,
        "by_label_tier": by_tier,
        "verdict": verdict, "rule_failures": reasons,
        "rows": rows,
    }
    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in
                      ("cohort_n", "control", "j1", "delta", "gate_floor_citation_recall",
                       "verdict", "rule_failures", "by_label_tier")}, indent=2))
    print(f"\nwrote {DEST}", file=sys.stderr)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["generate", "report"], required=True)
    args = ap.parse_args()
    {"generate": phase_generate, "report": phase_report}[args.phase]()


if __name__ == "__main__":
    main()
