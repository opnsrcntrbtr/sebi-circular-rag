"""Hybrid abstention gate sweep — preregistered analysis.

Preregistration: docs/superpowers/specs/2026-08-26-hybrid-gate-prereg.md
(written and committed before this script's first real run).

Closes out the 2026-08-13 decision "pursue hybrid gate experiment for
subject_gate rows only" (docs/status.md:1230), which was written but never
executed. This is a rewrite, not the original 2026-08-13 script, which had
two bugs fixed here:

1. Passed `abstain_threshold=0.42` to `RAGPipeline` -- 0.42 is the
   `SubjectSimJudge` subject-sim threshold, not the cross-encoder score-floor
   threshold (`Settings.abstain_threshold`). Exactly the conflation
   `.claude/rules/refusal-criteria.md` calls out. Fixed: loads
   `Settings.load().abstain_threshold` and passes that.
2. Hardcoded `CrossEncoderReranker` (bge) and swept bge-scaled candidate
   thresholds (0.85/0.80/0.75). Fixed: uses `JinaMLXReranker` (current prod,
   ADR-004, config.toml reranker_model="jina") and a jina-scaled candidate
   grid derived from the 3 target rows' own observed jina rerank_top scores
   (see prereg doc section 1).

Runs over the full golden_v7 (n=260): answerable rows to find false
abstentions and confirm the 3 target rows; the 41 gold-abstain rows as the
guardrail cohort a hybrid gate must not falsely rescue. Abstention is
decided in `answer_with_abstention` before generation runs, so
`ExtractiveStubGenerator` is faithful here and far faster than MLX
generation over 260 rows (established precedent: docs/status.md 2026-08-13).

Usage: PYTHONPATH=src python3 scripts/hybrid_gate_sweep.py [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
             "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

from sebi_rag.benchmark import validate_golden  # noqa: E402
from sebi_rag.embeddings import BGEM3Embedder  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.generate import ExtractiveStubGenerator, SubjectSimJudge  # noqa: E402
from sebi_rag.lineage import build_lineage, load_records  # noqa: E402
from sebi_rag.pipeline import RAGPipeline  # noqa: E402
from sebi_rag.rerank import JinaMLXReranker  # noqa: E402
from sebi_rag.retrieve import HybridRetriever  # noqa: E402
from sebi_rag.settings import Settings  # noqa: E402
from sebi_rag.stats import paired_delta  # noqa: E402

TARGET_IDS = ("v7-ls-029", "v7-nt-013", "v7-nt-025")
# Preregistered grid (prereg doc section 1): brackets the 3 targets' own
# jina rerank_top scores from the 2026-08-24 calibration report
# (0.3430 / 0.4432 / 0.4923), NOT the old script's bge-scaled 0.85/0.80/0.75.
T_GRID = (0.30, 0.35, 0.40, 0.45, 0.50, 0.55)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--golden", default=str(ROOT / "eval" / "golden" / "golden_v7.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "reports" / "hybrid-gate-cohort-2026-08-26.json"))
    return ap.parse_args()


def build_pipeline() -> tuple[RAGPipeline, Settings]:
    s = Settings.load()
    recs = load_records(s.corpus_path)
    lin = build_lineage(recs)
    emb = BGEM3Embedder(device="mps")
    retr = HybridRetriever.load(Path(s.index_dir), emb)
    rer = JinaMLXReranker()  # current prod reranker (ADR-004, config.toml reranker_model="jina")
    judge = SubjectSimJudge(emb, threshold=0.42, section_threshold=0.60)
    gen = ExtractiveStubGenerator()
    pipeline = RAGPipeline(
        retriever=retr, reranker=rer, generator=gen,
        abstain_threshold=s.abstain_threshold,  # loaded, never hardcoded 0.42 (bug fixed)
        lineage=lin, superseded_penalty=s.superseded_penalty,
        judge=judge, citation_scorer=None,
    )
    return pipeline, s


def run_rows(pipeline: RAGPipeline, golden: list[dict]) -> list[dict]:
    """Run every golden_v7 row once; collect gate signals + gold label."""
    rows = []
    for i, item in enumerate(golden, 1):
        ans, _ = pipeline.query(item["query"], top_k=5)
        conf = ans.confidence or {}
        rows.append({
            "id": item.get("id", "?"),
            "gold_abstain": bool(item.get("abstain")),
            "abstained": bool(ans.abstained),
            "abstention_reason": ans.abstention_reason or "",
            "subject_sim": conf.get("subject_sim"),
            "section_sim": conf.get("section_sim"),
            "rerank_top": conf.get("rerank_top"),
        })
        if i % 50 == 0:
            print(f"  {i}/{len(golden)} processed", file=sys.stderr)
    return rows


def current_gate_passes(row: dict) -> bool:
    """Reproduces the current production subject-gate OR (no hybrid override)."""
    subj = row["subject_sim"]
    sect = row["section_sim"]
    return (subj is not None and subj >= 0.42) or (sect is not None and sect >= 0.60)


def hybrid_gate_passes(row: dict, t: float) -> bool:
    top = row["rerank_top"]
    return current_gate_passes(row) or (top is not None and top >= t)


def score_floor_immune(row: dict, abstain_threshold: float) -> bool:
    """True if this row never reaches the subject-gate check at all (vetoed
    earlier by the score floor) -- structurally unaffected by any T."""
    top = row["rerank_top"]
    return top is None or top < abstain_threshold


def main() -> None:
    args = parse_args()
    golden_path = Path(args.golden)
    golden = load_golden(golden_path)
    issues = validate_golden(golden)
    errors = [i for i in issues if getattr(i, "severity", "") == "error"]
    if errors:
        print(f"validate_golden found {len(errors)} error-severity issues:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)

    pipeline, settings = build_pipeline()
    print(f"abstain_threshold (Settings.load()) = {settings.abstain_threshold}", file=sys.stderr)
    print(f"reranker_model = {settings.reranker_model}", file=sys.stderr)
    print(f"Running {len(golden)} golden_v7 rows through the pipeline...", file=sys.stderr)
    rows = run_rows(pipeline, golden)

    by_id = {r["id"]: r for r in rows}

    # --- Step A: reproduce the false-abstention set on answerable rows ---
    answerable_false_abstentions = [
        r for r in rows if not r["gold_abstain"] and r["abstained"]
    ]
    subject_gate_false_abstentions = [
        r for r in answerable_false_abstentions if r["abstention_reason"] == "subject_gate"
    ]
    found_target_ids = {r["id"] for r in subject_gate_false_abstentions}
    missing_targets = [t for t in TARGET_IDS if t not in found_target_ids]
    extra_targets = sorted(found_target_ids - set(TARGET_IDS))

    print(f"\nAnswerable false abstentions: {len(answerable_false_abstentions)} "
          f"({len(subject_gate_false_abstentions)} subject_gate)", file=sys.stderr)
    for r in subject_gate_false_abstentions:
        print(f"  {r['id']:15s} subj={r['subject_sim']} sect={r['section_sim']} "
              f"top={r['rerank_top']}", file=sys.stderr)
    if missing_targets:
        print(f"  WARNING: expected targets not reproduced: {missing_targets}", file=sys.stderr)
    if extra_targets:
        print(f"  NOTE: additional subject_gate false abstentions found (superset): "
              f"{extra_targets}", file=sys.stderr)

    # --- Step B: guardrail cohort (41 gold-abstain rows) ---
    guardrail_rows = [r for r in rows if r["gold_abstain"]]
    guardrail_immune = [r for r in guardrail_rows
                        if score_floor_immune(r, settings.abstain_threshold)]
    immune_ids = {r["id"] for r in guardrail_immune}
    guardrail_at_risk = [r for r in guardrail_rows if r["id"] not in immune_ids]
    baseline_guardrail_fps = [r for r in guardrail_at_risk if current_gate_passes(r)]
    print(f"\nGuardrail cohort: {len(guardrail_rows)} gold-abstain rows "
          f"({len(guardrail_immune)} score-floor-immune, {len(guardrail_at_risk)} at-risk)",
          file=sys.stderr)
    if baseline_guardrail_fps:
        print(f"  WARNING: {len(baseline_guardrail_fps)} guardrail rows already fail the "
              f"CURRENT (non-hybrid) gate -- baseline is not clean: "
              f"{[r['id'] for r in baseline_guardrail_fps]}", file=sys.stderr)

    # --- Step C: sweep T grid ---
    sweep = []
    for t in T_GRID:
        rescued = [r for r in subject_gate_false_abstentions
                   if not current_gate_passes(r) and hybrid_gate_passes(r, t)]
        new_guardrail_fps = [r for r in guardrail_at_risk
                             if not current_gate_passes(r) and hybrid_gate_passes(r, t)]
        eligible = len(new_guardrail_fps) == 0

        # Full-golden_v7 paired abstention-accuracy vectors (current-prod vs hybrid@T)
        base_acc, hybrid_acc = {}, {}
        for r in rows:
            qid = r["id"]
            base_answered = not r["abstained"]
            # current-prod decision is exactly r["abstained"] (already measured);
            # hybrid decision only differs from current-prod for rows that were
            # abstained under subject_gate and now pass the hybrid OR.
            if r["abstention_reason"] == "subject_gate" and not current_gate_passes(r) \
                    and hybrid_gate_passes(r, t):
                hybrid_answered = True
            else:
                hybrid_answered = base_answered
            base_acc[qid] = float(base_answered != r["gold_abstain"])
            hybrid_acc[qid] = float(hybrid_answered != r["gold_abstain"])

        cmp = paired_delta(base_acc, hybrid_acc)
        adopted = (
            eligible and len(rescued) >= 1
            and abs(cmp.delta) >= 0.01 and cmp.significant
        )
        sweep.append({
            "T": t,
            "rescued_target_ids": sorted(r["id"] for r in rescued),
            "rescued_count": len(rescued),
            "new_guardrail_false_positive_ids": sorted(r["id"] for r in new_guardrail_fps),
            "new_guardrail_false_positive_count": len(new_guardrail_fps),
            "eligible_per_step1_safety_filter": eligible,
            "abstention_accuracy_delta": cmp.delta,
            "abstention_accuracy_p_value": cmp.p_value,
            "abstention_accuracy_ci": [cmp.ci_lo, cmp.ci_hi],
            "abstention_accuracy_significant": cmp.significant,
            "adopted_per_prereg_decision_rule": adopted,
        })
        flag = "ADOPTED" if adopted else ("eligible-but-not-significant" if eligible and rescued
                                          else "disqualified" if not eligible else "no-rescue")
        print(f"T={t:.2f}  rescued={len(rescued)}/3  new_guardrail_fps={len(new_guardrail_fps)}  "
              f"acc_delta={cmp.delta:+.4f}  p={cmp.p_value:.4f}  sig={cmp.significant}  [{flag}]",
              file=sys.stderr)

    eligible_sweep = [s for s in sweep if s["eligible_per_step1_safety_filter"] and s["rescued_count"] >= 1]
    adopted_sweep = [s for s in sweep if s["adopted_per_prereg_decision_rule"]]

    if adopted_sweep:
        best = max(adopted_sweep, key=lambda s: (s["rescued_count"], -s["T"]))
        verdict = f"ADOPTED-AS-RECOMMENDATION at T={best['T']}"
    elif eligible_sweep:
        verdict = ("NULL (Global Constraints significance bar) -- eligible, safe, targeted "
                   "rescue exists but does not clear |delta|>=0.01 and significant; "
                   "anticipated per prereg Power Note, not a deviation")
    else:
        verdict = "NULL (Step 1 safety filter) -- every T that rescues >=1 target also introduces guardrail false positives"

    print(f"\nVerdict: {verdict}", file=sys.stderr)

    out = {
        "prereg": "docs/superpowers/specs/2026-08-26-hybrid-gate-prereg.md",
        "golden_file": str(golden_path),
        "n_rows": len(rows),
        "settings": {
            "abstain_threshold": settings.abstain_threshold,
            "reranker_model": settings.reranker_model,
            "superseded_penalty": settings.superseded_penalty,
        },
        "target_ids": list(TARGET_IDS),
        "targets_reproduced": sorted(found_target_ids & set(TARGET_IDS)),
        "targets_missing": missing_targets,
        "additional_subject_gate_false_abstentions": extra_targets,
        "answerable_false_abstentions": answerable_false_abstentions,
        "guardrail_cohort_size": len(guardrail_rows),
        "guardrail_score_floor_immune": len(guardrail_immune),
        "guardrail_at_risk": len(guardrail_at_risk),
        "baseline_guardrail_false_positives": [r["id"] for r in baseline_guardrail_fps],
        "T_grid": list(T_GRID),
        "sweep": sweep,
        "verdict": verdict,
        "all_rows": rows,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
