"""R1 §4/§6 cohort measurement: control (cross-encoder) vs W1 (warrant judge).

Spec: docs/superpowers/specs/2026-08-20-warrant-citation-scorer-prereg.md §§4-6.
Amendment: docs/superpowers/specs/2026-08-23-warrant-degeneracy-max-tokens-prereg.md
(max_tokens 512->1024; cleared §3.3 at 97.6% parseable on 2026-08-23).

Cohort: golden_v7 rows that are answerable, non-as_of, have relevant_circulars,
AND whose retrieval pool (top_n=50) contains every gold document — "perfect
retrieval". Recomputed on the live index every run (§4: "not a stored
artifact... recompute, never quote" — the prior-index reference of 206 was
itself wrong, R2 measured 201/204 on the index that preceded this one).

Arms (§5):
  control  citation_scorer_for(backend="reranker")  — bge-reranker-v2-m3, production today
  W1       citation_scorer_for(backend="warrant", warrant_max_tokens=1024)  — 7B judge

Both arms score the SAME answer text and the SAME context window (§3: "Single
variable: the scorer B' consults. Everything else is held... same generator").
The 1.5B generator is deterministic (greedy decoding), so it is run ONCE per
row in the `generate` phase and its output reused for both arms — this also
means a difference between arms is attributable only to the scorer, never to
generation noise.

Endpoints (§4):
  PRIMARY       citation_precision   +0.02 absolute effect-size floor (§6)
  GUARDRAIL     zero_cite            zero tolerance on increase (§6.2)
  GUARDRAIL     citation_recall      must not fall below the armed gate floor
                                     (§6.3; read from eval/golden/gate_v7.json,
                                     not a hardcoded/quoted value)
  CONFIRMATORY  primary + guardrails split by label_tier (CS1: 68.8% of the
                gate is model-labelled — not decisive per §4, reported alongside)

Three phases, run as three separate process invocations so the 1.5B answer
generator and the 7B judge are never resident together — same rationale as
warrant_degeneracy_probe.py's phase split:

  1. generate  — full production pipeline (embedder + reranker + 1.5B generator),
                 control citation_scorer active. Computes the cohort, generates
                 each row's answer once, captures control's citations in the
                 same pass (its scorer needs no extra model).
  2. judge     — embedder + retriever (chunk lookup only) + 7B judge, shared
                 across all rows (loaded once, not per row). Reads the
                 generate-phase dump and re-scores each row's FIXED
                 (answer_text, contexts) pair with the warrant judge.
  3. report    — no models loaded. Reads both dumps, computes deltas, applies
                 the §6 decision rule mechanically, writes the final report.

Usage:
  PYTHONPATH=src python scripts/analysis/warrant_scorer_cohort.py --phase generate
  PYTHONPATH=src python scripts/analysis/warrant_scorer_cohort.py --phase judge
  PYTHONPATH=src python scripts/analysis/warrant_scorer_cohort.py --phase report
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
GENERATE_DUMP = ROOT / "reports" / "warrant-cohort-generate.json"
JUDGE_DUMP = ROOT / "reports" / "warrant-cohort-judge.json"
DEST = ROOT / "reports" / "warrant-scorer-cohort-2026-08-23.json"

POOL, TOP_K = 50, 10
WARRANT_MODEL = "mlx-community/Qwen2.5-7B-Instruct-4bit"
WARRANT_MAX_TOKENS = 1024
CITATION_PRECISION_EFFECT_FLOOR = 0.02  # §6, fixed in advance


def eligible(item: dict) -> bool:
    """Answerable, non-as_of, with gold citations: the rows citation metrics
    exist for. Matches supersession_tier_cohort.py's predicate exactly."""
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
    from sebi_rag.generate import citation_scorer_for

    pipe = build_default_pipeline()
    # Explicit, not config-dependent: control is the cross-encoder backend
    # regardless of what config.toml currently has citation_scorer_backend set to.
    pipe.citation_scorer = citation_scorer_for(True, pipe.reranker, backend="reranker")
    print(f"citation_margin={pipe.citation_margin} citation_min_keep={pipe.citation_min_keep}",
          file=sys.stderr)

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

    rows, t0 = [], time.time()
    for n, it in enumerate(cohort, 1):
        ans, _ = pipe.query(it["query"], pool=POOL, top_k=TOP_K)
        relevant = set(it["relevant_circulars"])
        m = _measure(relevant, ans.abstained, ans.context_ids, ans.citations)
        rows.append({
            "id": it["id"], "task_type": it.get("task_type"),
            "label_tier": it.get("label_tier"), "query": it["query"],
            "relevant_circulars": it["relevant_circulars"],
            "abstained": bool(ans.abstained), "answer_text": ans.text,
            "context_ids": list(ans.context_ids),
            "control_citations": list(ans.citations), "control_measure": m,
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


def phase_judge() -> None:
    if not GENERATE_DUMP.exists():
        raise SystemExit(f"{GENERATE_DUMP} missing — run --phase generate first")
    from sebi_rag.embeddings import BGEM3Embedder
    from sebi_rag.generate import MLXGenerator, citation_scorer_for, select_citations
    from sebi_rag.retrieve import HybridRetriever
    from sebi_rag.settings import Settings

    dump = json.loads(GENERATE_DUMP.read_text())
    s = Settings.load()
    print("loading embedder + retriever (chunk lookup only, no reranker/1.5B generator)...",
          file=sys.stderr)
    embedder = BGEM3Embedder()
    retriever = HybridRetriever.load(Path(s.index_dir), embedder)
    chunk_by_id = {c.id: c for c in retriever.chunks}
    print(f"loading warrant judge at {WARRANT_MODEL} (shared across all rows, "
          f"max_tokens={WARRANT_MAX_TOKENS}) ...", file=sys.stderr)
    warrant_gen = MLXGenerator(WARRANT_MODEL)
    w1_scorer = citation_scorer_for(True, None, backend="warrant",
                                    warrant_shared=warrant_gen,
                                    warrant_max_tokens=WARRANT_MAX_TOKENS)
    margin, min_keep = dump["citation_margin"], dump["citation_min_keep"]

    rows, t0 = [], time.time()
    for n, r in enumerate(dump["rows"], 1):
        if r["abstained"] or not r["context_ids"]:
            rows.append({"id": r["id"], "w1_citations": [], "parse_note": "abstained_or_no_context"})
            continue
        contexts = [chunk_by_id[cid] for cid in r["context_ids"] if cid in chunk_by_id]
        if not contexts:
            rows.append({"id": r["id"], "w1_citations": [],
                        "parse_note": "context_ids not found in the live chunk store"})
            continue
        w1_citations = select_citations(r["answer_text"], contexts, w1_scorer,
                                        margin=margin, min_keep=min_keep, query=r["query"])
        rows.append({"id": r["id"], "w1_citations": w1_citations, "parse_note": None})
        if n % 25 == 0:
            print(f"  {n}/{len(dump['rows'])}  ({time.time() - t0:.0f}s)", file=sys.stderr)

    out = {"judge_model": WARRANT_MODEL, "max_tokens": WARRANT_MAX_TOKENS,
           "runtime_s": round(time.time() - t0, 1), "rows": rows}
    JUDGE_DUMP.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {JUDGE_DUMP} ({len(rows)} rows, {out['runtime_s']}s)", file=sys.stderr)


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
    if not GENERATE_DUMP.exists() or not JUDGE_DUMP.exists():
        raise SystemExit("both --phase generate and --phase judge must run first")
    gen = json.loads(GENERATE_DUMP.read_text())
    judge = json.loads(JUDGE_DUMP.read_text())
    gate_floor = json.loads(GATE.read_text())["floors"]["citation_recall"]

    w1_by_id = {r["id"]: r for r in judge["rows"]}
    combined = []
    for r in gen["rows"]:
        w1 = w1_by_id.get(r["id"], {"w1_citations": [], "parse_note": "missing_from_judge_dump"})
        relevant = set(r["relevant_circulars"])
        w1_measure = _measure(relevant, r["abstained"], r["context_ids"], w1["w1_citations"])
        combined.append({**r, "w1_citations": w1["w1_citations"],
                         "w1_parse_note": w1["parse_note"], "w1_measure": w1_measure})

    control_summary = _aggregate(combined, "control_measure")
    w1_summary = _aggregate(combined, "w1_measure")
    delta = {k: round(w1_summary[k] - control_summary[k], 4) for k in
             ("zero_cite", "citation_recall", "citation_precision", "context_recall")}

    # --- §4 CONFIRMATORY: split by label_tier (CS1) ---------------------------
    tiers: dict[str, list[dict]] = {}
    for r in combined:
        tiers.setdefault(r.get("label_tier") or "unknown", []).append(r)
    by_tier = {
        tier: {
            "n": len(rs),
            "control": _aggregate(rs, "control_measure"),
            "w1": _aggregate(rs, "w1_measure"),
        }
        for tier, rs in sorted(tiers.items())
    }

    # --- §6 decision rule, evaluated mechanically ------------------------------
    verdict, reasons = "PROCEED to §7 full-gate confirmation", []
    precision_gain = w1_summary["citation_precision"] - control_summary["citation_precision"]
    if precision_gain < CITATION_PRECISION_EFFECT_FLOOR:
        verdict = "REJECT"
        reasons.append(f"6.1: citation_precision gained {precision_gain:.4f}, "
                        f"needs >= {CITATION_PRECISION_EFFECT_FLOOR}")
    if w1_summary["zero_cite"] > control_summary["zero_cite"]:
        verdict = "REJECT"
        reasons.append(f"6.2: zero_cite rose {control_summary['zero_cite']} -> "
                        f"{w1_summary['zero_cite']} (zero tolerance on increase)")
    if w1_summary["citation_recall"] < gate_floor:
        verdict = "REJECT"
        reasons.append(f"6.3: W1 citation_recall {w1_summary['citation_recall']} "
                        f"< armed floor {gate_floor} (gate_v7.json)")

    out = {
        "spec": "docs/superpowers/specs/2026-08-20-warrant-citation-scorer-prereg.md §§4-6",
        "amendment": "docs/superpowers/specs/2026-08-23-warrant-degeneracy-max-tokens-prereg.md",
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "cohort_n": gen["cohort_n"], "eligible_n": gen["eligible_n"],
        "citation_margin": gen["citation_margin"], "citation_min_keep": gen["citation_min_keep"],
        "answer_generator": gen["generator_model"],
        "warrant_judge_model": judge["judge_model"], "warrant_max_tokens": judge["max_tokens"],
        "gate_floor_citation_recall": gate_floor,
        "effect_size_floor_citation_precision": CITATION_PRECISION_EFFECT_FLOOR,
        "control": control_summary, "w1": w1_summary, "delta": delta,
        "by_label_tier": by_tier,
        "verdict": verdict, "rule_failures": reasons,
        "rows": combined,
    }
    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in
                      ("cohort_n", "control", "w1", "delta", "gate_floor_citation_recall",
                       "verdict", "rule_failures", "by_label_tier")}, indent=2))
    print(f"\nwrote {DEST}", file=sys.stderr)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["generate", "judge", "report"], required=True)
    args = ap.parse_args()
    {"generate": phase_generate, "judge": phase_judge, "report": phase_report}[args.phase]()


if __name__ == "__main__":
    main()
