"""Preregistered cohort measurement for supersession confidence tiering.

Spec: docs/superpowers/specs/2026-08-19-supersession-confidence-tier-prereg.md

Arms (spec 5):
  Control  inferred_penalty=None  -> every superseded circular demotes at 0.3
  T1       inferred_penalty=1.0   -> circulars known superseded ONLY from the
                                     master-circular title heuristic are not demoted

Endpoints (spec 4):
  PRIMARY   zero_cite   answerable rows citing nothing relevant, EXCLUDING the
                        4 exploratory rows named in spec 0
  GUARDRAIL stale_at_1  top-ranked context chunk is from a superseded circular
  GUARDRAIL stale_at_3  same within the top-3 context chunks
  SECONDARY citation_recall, citation_precision, context_recall, context_miss
  EXPLORATORY the 4 spec-0 rows, reported separately, binding on nothing

The cohort is NOT a stored artifact: it was derived inline in the 2026-08-12/13
analyses on a 724-circular index and never persisted. It is recomputed here on
the live index and written to the DEST report, which is the cohort of record.

Usage: PYTHONPATH=src python scripts/analysis/supersession_tier_cohort.py
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

from sebi_rag.api import build_default_pipeline  # noqa: E402
from sebi_rag.eval_harness import _doc, _unique, load_golden  # noqa: E402
from sebi_rag.settings import Settings  # noqa: E402

GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
DEST = ROOT / "reports" / "supersession-tier-cohort-2026-08-19.json"

# spec 0 — the rows whose provenance generated the hypothesis. Excluded from the
# primary so adoption is decided on data that did not produce it.
EXPLORATORY = {"v7-bp-036", "v7-ls-005", "v7-mh-020", "v7-nt-014"}

POOL = 50
TOP_K = 10


def eligible(item: dict) -> bool:
    """Answerable, non-as_of, with gold citations: the rows citation metrics exist for."""
    return (not item.get("abstain")
            and not item.get("as_of")
            and bool(item.get("relevant_circulars")))


def measure(pipe, item: dict, superseded: set[str]) -> dict:
    relevant = set(item["relevant_circulars"])
    ans, retrieved_ids = pipe.query(item["query"], pool=POOL, top_k=TOP_K)

    pool_docs = _unique(_doc(i) for i in retrieved_ids)
    context_docs = _unique(_doc(i) for i in ans.context_ids)
    cited = [] if ans.abstained else _unique(_doc(c) for c in ans.citations)
    hit = len(set(cited) & relevant)

    return {
        "id": item["id"],
        "task_type": item.get("task_type"),
        "abstained": bool(ans.abstained),
        "abstention_reason": ans.abstention_reason,
        # retrieval succeeded == every gold doc reached the candidate pool
        "perfect_retrieval": relevant.issubset(set(pool_docs)),
        "zero_cite": hit == 0,
        "citation_recall": hit / len(relevant),
        "citation_precision": (hit / len(cited)) if cited else 0.0,
        "context_recall": len(set(context_docs) & relevant) / len(relevant),
        "context_miss": len(set(context_docs) & relevant) == 0,
        "stale_at_1": bool(context_docs[:1]) and context_docs[0] in superseded,
        "stale_at_3": any(d in superseded for d in context_docs[:3]),
        "n_cited": len(cited),
    }


def aggregate(rows: list[dict], label: str) -> dict:
    scored = [r for r in rows if r["id"] not in EXPLORATORY]
    n = len(scored)
    mean = lambda k: round(sum(r[k] for r in scored) / n, 4) if n else 0.0  # noqa: E731
    return {
        "arm": label,
        "n_primary": n,
        "n_exploratory": len(rows) - n,
        "zero_cite": sum(r["zero_cite"] for r in scored),
        "stale_at_1": sum(r["stale_at_1"] for r in scored),
        "stale_at_3": sum(r["stale_at_3"] for r in scored),
        "context_miss": sum(r["context_miss"] for r in scored),
        "abstained": sum(r["abstained"] for r in scored),
        "citation_recall": mean("citation_recall"),
        "citation_precision": mean("citation_precision"),
        "context_recall": mean("context_recall"),
        "exploratory_zero_cite": sum(
            r["zero_cite"] for r in rows if r["id"] in EXPLORATORY),
    }


def main() -> None:
    s = Settings.load()
    t_start = time.time()
    print(f"generator={s.generator} mlx_model={s.mlx_model} "
          f"B'={s.citation_scorer_enabled} margin={s.citation_margin}", file=sys.stderr)

    pipe = build_default_pipeline()
    assert pipe.lineage is not None, "lineage required"
    superseded = set(pipe.lineage.superseded_by)
    explicit = {e["target"] for e in pipe.lineage.edges
                if e["relation"] == "supersedes" and e["confidence"] == "explicit_text"}
    only_inferred = superseded - explicit
    print(f"superseded={len(superseded)} explicit={len(explicit)} "
          f"only_inferred={len(only_inferred)}", file=sys.stderr)

    items = [i for i in load_golden(GOLDEN) if eligible(i)]
    print(f"eligible answerable non-as_of rows: {len(items)}", file=sys.stderr)

    # --- Pass 0: cohort determination (retrieval only, arm-independent) -------
    # Demotion runs after reranking and never touches `retrieved_ids`, so the
    # cohort is identical under both arms and is fixed before either runs.
    cohort_ids = []
    for it in items:
        cand = pipe.retriever.retrieve(it["query"], top_n=POOL)
        pool_docs = {_doc(c.id) for c, _ in cand}
        if set(it["relevant_circulars"]).issubset(pool_docs):
            cohort_ids.append(it["id"])
    cohort = [i for i in items if i["id"] in set(cohort_ids)]
    print(f"perfect-retrieval cohort: {len(cohort)} of {len(items)} "
          f"(prior-index reference: 206)", file=sys.stderr)

    # --- Arms ----------------------------------------------------------------
    results = {}
    for label, inferred in (("control", None), ("T1", 1.0)):
        pipe.inferred_supersession_penalty = inferred
        rows = []
        for n, it in enumerate(cohort, 1):
            rows.append(measure(pipe, it, superseded))
            if n % 25 == 0:
                print(f"  [{label}] {n}/{len(cohort)}", file=sys.stderr)
        results[label] = {"rows": rows, "summary": aggregate(rows, label)}
        print(f"[{label}] {json.dumps(results[label]['summary'])}", file=sys.stderr)
    pipe.inferred_supersession_penalty = None  # leave the object as found

    c, t = results["control"]["summary"], results["T1"]["summary"]
    delta = {k: t[k] - c[k] for k in
             ("zero_cite", "stale_at_1", "stale_at_3", "context_miss")}

    # spec 6 decision rule, evaluated mechanically
    verdict, reasons = "ADOPT", []
    if t["stale_at_1"] > c["stale_at_1"]:
        verdict, _ = "REJECT", reasons.append(
            f"6.1 stale_at_1 rose {c['stale_at_1']}->{t['stale_at_1']}")
    if t["stale_at_3"] > c["stale_at_3"] + 5:
        verdict, _ = "REJECT", reasons.append(
            f"6.2 stale_at_3 rose {c['stale_at_3']}->{t['stale_at_3']} (>5)")
    if t["zero_cite"] > c["zero_cite"] - 2:
        verdict, _ = "REJECT", reasons.append(
            f"6.3 zero_cite {c['zero_cite']}->{t['zero_cite']} (needs >=2 improvement)")

    out = {
        "spec": "docs/superpowers/specs/2026-08-19-supersession-confidence-tier-prereg.md",
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "runtime_s": round(time.time() - t_start, 1),
        "generator": s.generator, "mlx_model": s.mlx_model,
        "citation_scorer_enabled": s.citation_scorer_enabled,
        "citation_margin": s.citation_margin,
        "superseded_penalty": s.superseded_penalty,
        "lineage": {"superseded": len(superseded), "explicit": len(explicit),
                    "only_inferred": len(only_inferred)},
        "cohort_ids": [i["id"] for i in cohort],
        "cohort_n": len(cohort),
        "eligible_n": len(items),
        "exploratory_ids": sorted(EXPLORATORY),
        "control": results["control"]["summary"],
        "T1": results["T1"]["summary"],
        "delta": delta,
        "verdict": verdict,
        "rule_failures": reasons,
        "rows": {"control": results["control"]["rows"], "T1": results["T1"]["rows"]},
    }
    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in
                      ("cohort_n", "control", "T1", "delta", "verdict", "rule_failures")},
                     indent=2))


if __name__ == "__main__":
    main()
