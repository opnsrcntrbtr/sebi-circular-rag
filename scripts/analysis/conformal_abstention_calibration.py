"""R7 conformal abstention calibration: generate -> calibrate -> report phases.

Spec: docs/superpowers/specs/2026-08-26-conformal-abstention-calibration-design.md.
Plan: docs/superpowers/plans/2026-08-26-conformal-abstention-calibration.md.

Calibrates the score-floor (Settings.abstain_threshold) and subject-gate
(SEBI_RAG_SUBJ_THRESHOLD) thresholds via Conformal Risk Control + leave-one-out data
reuse (src/sebi_rag/conformal.py), using FRESH per-row scores under current production
(Jina reranker, ADR-004; recalibrated abstain_threshold=0.12) -- not any prior dump,
which would predate that adoption.

Three phases, matching this repo's established cohort-script pattern:
  1. generate    -- full production pipeline over all 260 golden_v7 rows (both abstain
                     and answerable -- the gate fires on every row regardless of gold
                     label), captures rerank_top/subject_sim/abstention_reason plus the
                     ground-truth labels the calibration functions need.
  2. calibrate    -- no model loaded, pure computation. Runs calibrate_score_floor and
                     calibrate_subject_gate at alpha in {0.05, 0.10} (0.05 primary,
                     per the spec's Sec 6, fixed in advance -- not chosen after seeing
                     a result).
  3. report       -- applies the spec's Sec 6 decision rule mechanically.

Usage:
  PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase generate
  PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase calibrate
  PYTHONPATH=src python scripts/analysis/conformal_abstention_calibration.py --phase report
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
GENERATE_DUMP = ROOT / "reports" / "conformal-calibration-generate.json"
CALIBRATE_DUMP = ROOT / "reports" / "conformal-calibration-calibrate.json"
DEST = ROOT / "reports" / "conformal-calibration-report-2026-08-26.json"

POOL, TOP_K = 50, 10
ALPHA_PRIMARY = 0.05
ALPHA_SECONDARY = 0.10
ABSTENTION_ACCURACY_EFFECT_FLOOR = 0.01  # spec Sec 6, fixed in advance


def phase_generate() -> None:
    from sebi_rag.api import build_default_pipeline
    from sebi_rag.eval_harness import _doc, _unique, load_golden

    pipe = build_default_pipeline()
    items = list(load_golden(GOLDEN))
    print(f"golden_v7 rows: {len(items)}", file=sys.stderr)

    limit = int(os.environ.get("SEBI_ROW_LIMIT", "0"))
    if limit:
        items = items[:limit]
        print(f"SEBI_ROW_LIMIT set: truncated to {len(items)} rows (smoke test)", file=sys.stderr)

    rows, t0 = [], time.time()
    for n, it in enumerate(items, 1):
        ans, _ = pipe.query(it["query"], pool=POOL, top_k=TOP_K)
        gold_abstain = bool(it.get("abstain"))
        rerank_top = ans.confidence.get("rerank_top")
        subject_sim = ans.confidence.get("subject_sim")

        if gold_abstain:
            wrong_if_answered = True  # any answer at all is wrong for a gold-abstain row
        else:
            relevant = set(it.get("relevant_circulars") or [])
            if not relevant or ans.abstained:
                # No gold citations to check against, or this row abstained (so
                # "if answered" correctness can't be assessed from what happened) --
                # conservatively exclude from the score-floor calibration set rather
                # than guess. Flagged via wrong_if_answered=None, filtered in calibrate.
                wrong_if_answered = None
            else:
                cited = _unique(_doc(c) for c in ans.citations)
                wrong_if_answered = len(set(cited) & relevant) == 0  # zero_cite

        rows.append({
            "id": it["id"], "abstain_gold": gold_abstain,
            "abstained": bool(ans.abstained),
            "abstention_reason": ans.abstention_reason,
            "rerank_top": rerank_top, "subject_sim": subject_sim,
            "wrong_if_answered": wrong_if_answered,
            "answerable": not gold_abstain,
        })
        if n % 25 == 0:
            print(f"  {n}/{len(items)}  ({time.time() - t0:.0f}s)", file=sys.stderr)

    out = {
        "n": len(rows), "runtime_s": round(time.time() - t0, 1),
        "reranker": pipe.reranker.__class__.__name__,
        "abstain_threshold": pipe.abstain_threshold,
        "rows": rows,
    }
    GENERATE_DUMP.parent.mkdir(parents=True, exist_ok=True)
    GENERATE_DUMP.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {GENERATE_DUMP} (n={out['n']}, {out['runtime_s']}s)", file=sys.stderr)


def phase_calibrate() -> None:
    if not GENERATE_DUMP.exists():
        raise SystemExit(f"{GENERATE_DUMP} missing -- run --phase generate first")
    from sebi_rag.conformal import calibrate_score_floor, calibrate_subject_gate

    dump = json.loads(GENERATE_DUMP.read_text())
    rows = dump["rows"]

    score_floor_rows = [
        {"rerank_top": r["rerank_top"], "wrong_if_answered": r["wrong_if_answered"]}
        for r in rows if r["wrong_if_answered"] is not None
    ]
    subject_gate_rows = [
        {"subject_sim": r["subject_sim"], "answerable": r["answerable"]}
        for r in rows if r["subject_sim"] is not None
    ]
    print(f"score_floor calibration set: {len(score_floor_rows)} of {len(rows)} rows "
          f"(excludes rows where wrong_if_answered could not be determined)", file=sys.stderr)
    print(f"subject_gate calibration set: {len(subject_gate_rows)} of {len(rows)} rows "
          f"(excludes rows where subject_sim was never computed)", file=sys.stderr)

    results = {}
    for alpha in (ALPHA_PRIMARY, ALPHA_SECONDARY):
        key = f"alpha_{alpha}"
        sf = calibrate_score_floor(score_floor_rows, alpha)
        sg = calibrate_subject_gate(subject_gate_rows, alpha)
        results[key] = {
            "alpha": alpha,
            "score_floor": vars(sf),
            "subject_gate": vars(sg),
        }
        print(f"alpha={alpha}: score_floor threshold={sf.threshold:.4f} "
              f"(held-out risk {sf.held_out_risk_estimate:.4f}), "
              f"subject_gate threshold={sg.threshold:.4f} "
              f"(held-out risk {sg.held_out_risk_estimate:.4f})", file=sys.stderr)

    CALIBRATE_DUMP.write_text(json.dumps(
        {"score_floor_n": len(score_floor_rows), "subject_gate_n": len(subject_gate_rows),
         "results": results}, indent=2), encoding="utf-8")
    print(f"wrote {CALIBRATE_DUMP}", file=sys.stderr)


def _control_summary(rows: list[dict]) -> dict:
    """Current production behaviour, exactly as shipped -- no LOO recalibration, the
    fixed thresholds applied as-is (abstain_threshold and SEBI_RAG_SUBJ_THRESHOLD's
    production defaults). This is what the decision rule compares the calibrated arm
    against (design doc Sec 2.2's fairness note: the comparison is intentionally
    asymmetric, in the direction that makes adoption HARDER, not easier)."""
    n = len(rows)
    correct = sum(1 for r in rows if r["abstained"] == r["abstain_gold"])
    false_answers = sum(
        1 for r in rows
        if not r["abstained"] and r["wrong_if_answered"] is True
    )
    return {
        "n": n,
        "abstention_accuracy": round(correct / n, 4) if n else 0.0,
        "false_answer_count": false_answers,
        "false_answer_rate": round(false_answers / n, 4) if n else 0.0,
    }


def _simulated_summary(rows: list[dict], score_floor_threshold: float,
                       subject_gate_threshold: float) -> dict:
    """Re-simulates each row's abstention decision under the CALIBRATED thresholds,
    reusing the already-dumped rerank_top/subject_sim (no pipeline re-run needed --
    these are pure threshold comparisons against fixed, already-computed scores).

    Mirrors generate.py:answer_with_abstention's gate ORDER exactly (score_floor first,
    then subject_gate, both must pass to answer) but does NOT re-derive non_sebi_domain
    or the HYBRID_THRESHOLD override -- those are untouched by this arm (design doc
    Sec 1), so a row that hit either in production keeps that same outcome here; only
    rows whose production abstention_reason was "score_floor" or "subject_gate" (or
    that answered with both signals passing) are re-decided against the new thresholds.
    """
    n = len(rows)
    correct, false_answers = 0, 0
    for r in rows:
        if r["abstention_reason"] in ("no_context", "non_sebi_domain"):
            simulated_abstained = True  # untouched by this arm
        elif r["rerank_top"] is None or r["rerank_top"] < score_floor_threshold:
            simulated_abstained = True
        elif r["subject_sim"] is not None and r["subject_sim"] < subject_gate_threshold:
            simulated_abstained = True
        else:
            simulated_abstained = False
        if simulated_abstained == r["abstain_gold"]:
            correct += 1
        if not simulated_abstained and r["wrong_if_answered"] is True:
            false_answers += 1
    return {
        "n": n,
        "abstention_accuracy": round(correct / n, 4) if n else 0.0,
        "false_answer_count": false_answers,
        "false_answer_rate": round(false_answers / n, 4) if n else 0.0,
    }


def phase_report() -> None:
    if not GENERATE_DUMP.exists() or not CALIBRATE_DUMP.exists():
        raise SystemExit("both --phase generate and --phase calibrate must run first")
    gen = json.loads(GENERATE_DUMP.read_text())
    cal = json.loads(CALIBRATE_DUMP.read_text())
    gate_floors = json.loads(GATE.read_text())["floors"]

    rows = gen["rows"]
    control = _control_summary(rows)

    primary = cal["results"][f"alpha_{ALPHA_PRIMARY}"]
    sf_threshold = primary["score_floor"]["threshold"]
    sg_threshold = primary["subject_gate"]["threshold"]
    calibrated = _simulated_summary(rows, sf_threshold, sg_threshold)

    # design doc Sec 3 CONFIRMATORY (diagnostic only, not a second adoption path per
    # Sec 8): do the three documented subject_gate false abstentions flip under the
    # calibrated subject threshold?
    watch_ids = {"v7-nt-013", "v7-nt-025", "v7-ls-029"}
    by_id = {r["id"]: r for r in rows}
    row_flips = {}
    for rid in watch_ids:
        r = by_id.get(rid)
        if r is None:
            row_flips[rid] = "not_in_golden_v7_rows_dump"
            continue
        if r["subject_sim"] is None:
            row_flips[rid] = "subject_sim_never_computed_in_production"
            continue
        was_abstained = r["abstained"]
        now_abstained = (
            r["abstention_reason"] in ("no_context", "non_sebi_domain")
            or r["rerank_top"] is None or r["rerank_top"] < sf_threshold
            or r["subject_sim"] < sg_threshold
        )
        row_flips[rid] = {
            "was_abstained": was_abstained, "now_abstained": now_abstained,
            "flipped_to_answered": was_abstained and not now_abstained,
        }

    accuracy_gain = calibrated["abstention_accuracy"] - control["abstention_accuracy"]
    false_answer_increased = calibrated["false_answer_count"] > control["false_answer_count"]

    verdict, reasons = "REJECT", []
    if accuracy_gain >= ABSTENTION_ACCURACY_EFFECT_FLOOR and not false_answer_increased:
        verdict = "PROCEED to Sec 7 full-gate confirmation"
    else:
        if accuracy_gain < ABSTENTION_ACCURACY_EFFECT_FLOOR:
            reasons.append(
                f"6.1: abstention_accuracy gained {accuracy_gain:.4f}, "
                f"needs >= {ABSTENTION_ACCURACY_EFFECT_FLOOR}")
        if false_answer_increased:
            reasons.append(
                f"6.2: false_answer_count rose {control['false_answer_count']} -> "
                f"{calibrated['false_answer_count']} (zero tolerance on increase)")
        if accuracy_gain < ABSTENTION_ACCURACY_EFFECT_FLOOR and not false_answer_increased:
            # design doc Sec 6: "if 1 fails, still report the certified risk bound as
            # the qualitative deliverable" -- distinct from an adoption pass.
            verdict = "REJECT (primary null; certified risk bound reported per Sec 6)"

    out = {
        "spec": "docs/superpowers/specs/2026-08-26-conformal-abstention-calibration-design.md Sec 6",
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n": len(rows), "alpha_primary": ALPHA_PRIMARY, "alpha_secondary": ALPHA_SECONDARY,
        "effect_floor_abstention_accuracy": ABSTENTION_ACCURACY_EFFECT_FLOOR,
        "control": control, "calibrated": calibrated,
        "accuracy_gain": round(accuracy_gain, 4),
        "certified_risk_bounds_alpha_0_05": {
            "score_floor": primary["score_floor"],
            "subject_gate": primary["subject_gate"],
        },
        "certified_risk_bounds_alpha_0_10": cal["results"][f"alpha_{ALPHA_SECONDARY}"],
        "gate_floors_reference": gate_floors,
        "confirmatory_row_flips": row_flips,
        "verdict": verdict, "rule_failures": reasons,
    }
    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in
                      ("n", "control", "calibrated", "accuracy_gain", "verdict", "rule_failures")},
                     indent=2))
    print(f"\nwrote {DEST}", file=sys.stderr)
    print("\nNOTE: this verdict covers Sec 6 only. Sec 3's other gate floors "
          "(citation_recall, citation_precision, recall_at_k, context_recall, ndcg_at_10) "
          "must still be checked against a full eval_json_full run before Sec 7 "
          "confirmation -- this report does not run that eval.", file=sys.stderr)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["generate", "calibrate", "report"], required=True)
    args = ap.parse_args()
    {"generate": phase_generate, "calibrate": phase_calibrate,
     "report": phase_report}[args.phase]()


if __name__ == "__main__":
    main()
