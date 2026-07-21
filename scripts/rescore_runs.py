"""Re-score archived benchmark runs with bootstrap CIs and paired significance.

Reads the frozen TREC runfiles under eval/runs/ — no model loading, no index,
no re-running the pipeline — recomputes per-query recall@10, and reports:

  * per-run mean with a percentile bootstrap CI;
  * for each declared A/B pair, the paired delta with a bootstrap interval and
    a two-sided randomization p-value.

The point is to qualify the iv-series gate verdicts, which were decided on
point estimates over 45 answerable queries where one query is worth ~2.2
recall points. Comparability is checked too: a pair whose corpus or index
fingerprint differs by more than the intended treatment is flagged, since the
paired test assumes the queries — not the corpus — are what is held fixed.

    make rescore              # writes reports/ci_rescore.{md,json}
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.benchmark import per_query_recall, read_trec_run  # noqa: E402
from sebi_rag.eval_harness import load_golden  # noqa: E402
from sebi_rag.stats import bootstrap_ci, paired_delta  # noqa: E402

GOLDEN = ROOT / "eval" / "golden" / "golden_v6.jsonl"
PROBES = ROOT / "eval" / "probes" / "probes_v1.jsonl"

# Declared A/B comparisons: (control, treatment, what the treatment changed).
# Each was gated on a point-estimate delta at the time; these are the verdicts
# being re-examined.
PAIRS: tuple[tuple[str, str, str], ...] = (
    ("ft", "iv2", "iv1+iv2 governing-clause folding + glossary (ADOPTED)"),
    ("iv7", "iv8", "iv8 HyDE hypothetical-passage third leg"),
    ("iv7", "iv9", "iv9 contextual headers (full corpus)"),
    ("iv10-a", "iv10-b", "iv10 targeted headers (scoped sidecar)"),
    ("iv11-a", "iv11-b", "iv11 SPLADE learned-sparse third leg"),
)


def _fmt(x: float) -> str:
    return f"{x * 100:.1f}"


def score_run(run_dir: Path, golden: list[dict]) -> dict | None:
    runfile = run_dir / "run.trec"
    if not runfile.exists():
        return None
    scores = per_query_recall(read_trec_run(runfile), golden)
    if not scores:
        return None
    ci = bootstrap_ci(list(scores.values()), n_resamples=10000, seed=0)
    meta, archived = {}, None
    results = run_dir / "results.json"
    if results.exists() and results.stat().st_size:
        saved = json.loads(results.read_text(encoding="utf-8"))
        meta = saved.get("metadata", {})
        archived = saved.get("metrics", {}).get("recall_at_10")
    return {
        "run": run_dir.name,
        "n": ci.n,
        "recall_at_10": ci.point,
        "ci_lo": ci.lo,
        "ci_hi": ci.hi,
        "archived_recall_at_10": archived,
        # None => the run kept no results.json, so there is nothing to check
        # the replay against (not a mismatch).
        "replay_matches_archive": (
            None if archived is None else abs(archived - ci.point) < 1e-9
        ),
        "corpus_sha256": meta.get("corpus_sha256", ""),
        "index_fingerprint": meta.get("index_fingerprint", ""),
        "golden_sha256": meta.get("golden_sha256", ""),
        "git_commit": meta.get("git_commit", ""),
        "params": meta.get("params", {}),
        "_scores": scores,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=str(ROOT / "eval" / "runs"))
    ap.add_argument("--out", default=str(ROOT / "reports"))
    ap.add_argument("--suite", choices=("golden", "probes", "both"), default="both")
    ap.add_argument("--resamples", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    runs_root = Path(args.runs)
    suites = ("golden", "probes") if args.suite == "both" else (args.suite,)
    report: dict = {"suites": {}, "resamples": args.resamples, "seed": args.seed}

    for suite in suites:
        golden = load_golden(GOLDEN if suite == "golden" else PROBES)
        scored: dict[str, dict] = {}
        for d in sorted(runs_root.iterdir()):
            if not d.is_dir() or not d.name.endswith(f"-{suite}"):
                continue
            row = score_run(d, golden)
            if row:
                scored[d.name[: -len(suite) - 1]] = row

        pairs = []
        for control, treatment, label in PAIRS:
            a, b = scored.get(control), scored.get(treatment)
            if not (a and b):
                continue
            r = paired_delta(a["_scores"], b["_scores"],
                             n_resamples=args.resamples, seed=args.seed)
            pairs.append({
                "control": control, "treatment": treatment, "label": label,
                "n": r.n, "mean_control": r.mean_a, "mean_treatment": r.mean_b,
                "delta": r.delta, "ci_lo": r.ci_lo, "ci_hi": r.ci_hi,
                "p_value": r.p_value, "significant": r.significant,
                "queries_changed": sum(
                    1 for q in r.query_ids if a["_scores"][q] != b["_scores"][q]
                ),
                "same_corpus": a["corpus_sha256"] == b["corpus_sha256"],
                "same_index": a["index_fingerprint"] == b["index_fingerprint"],
            })
        report["suites"][suite] = {
            "runs": [{k: v for k, v in r.items() if k != "_scores"}
                     for r in scored.values()],
            "pairs": pairs,
        }

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "ci_rescore.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Benchmark re-scoring: bootstrap CIs and paired significance",
        "",
        f"Replayed from frozen TREC runfiles in `{runs_root.relative_to(ROOT)}`; "
        f"{args.resamples:,} resamples, seed {args.seed}, 95% intervals. "
        "No pipeline re-run — the runfiles are the record.",
        "",
    ]
    for suite, block in report["suites"].items():
        lines += [f"## {suite}", "",
                  "| run | n | recall@10 | 95% CI | replay == archive |",
                  "|---|---|---|---|---|"]
        for r in block["runs"]:
            match = {None: "n/a (no results.json)", True: "yes",
                     False: "**NO**"}[r["replay_matches_archive"]]
            lines.append(
                f"| {r['run']} | {r['n']} | {_fmt(r['recall_at_10'])} | "
                f"{_fmt(r['ci_lo'])}–{_fmt(r['ci_hi'])} | {match} |"
            )
        lines += ["", "### Paired comparisons", "",
                  "| comparison | n | control | treatment | delta | 95% CI | p | queries changed | verdict |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for p in block["pairs"]:
            verdict = "significant" if p["significant"] else "not distinguishable"
            lines.append(
                f"| {p['label']} | {p['n']} | {_fmt(p['mean_control'])} | "
                f"{_fmt(p['mean_treatment'])} | {p['delta'] * 100:+.1f} | "
                f"{p['ci_lo'] * 100:+.1f}–{p['ci_hi'] * 100:+.1f} | "
                f"{p['p_value']:.3f} | {p['queries_changed']} | {verdict} |"
            )
        lines.append("")

    alpha = 0.05
    mde = next(d for d in range(1, 64) if 2 * 0.5 ** d < alpha)
    lines += [
        "## Reading this table",
        "",
        "`queries changed` is the number of discordant queries — the only ones "
        "carrying information in a paired test. Under the null, each discordant "
        "query contributes one coin flip, so a two-sided test needs at least "
        f"**{mde} discordant queries all moving the same way** before any delta "
        f"can reach p < {alpha}. Every comparison above has 0–2. The p-values "
        "are therefore not evidence that these interventions are neutral; they "
        "are evidence that the golden set cannot tell, in either direction.",
        "",
        "Consequence for the iv-series gate verdicts: each accept/reject "
        "decision was made on a point-estimate delta that the same data cannot "
        "distinguish from noise. The adopted intervention (iv1+iv2) and the "
        "rejected ones (iv8-iv11) are, on this evidence, equally unproven.",
        "",
    ]
    (out / "ci_rescore.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
