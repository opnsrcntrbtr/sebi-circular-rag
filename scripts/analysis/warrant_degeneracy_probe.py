"""R1 §3.3 degeneracy probe: does the warrant judge return a parseable reply?

Spec: docs/superpowers/specs/2026-08-20-warrant-citation-scorer-prereg.md §3.3.
Must run BEFORE the §4/§6 cohort measurement and can abort the arm before it.

On the frozen 50-row eval/probes/screen_v1.jsonl (the same set mechanism_screen.py
uses for R0/T-Screen), for every answered row: take the production answer and its
post-rerank context window, prompt the warrant judge at 7B (the only size measured
to follow a prompted instruction — T-Screen 2026-08-20: 47.6% firing rate vs 0.0%
at 1.5B), and check whether its raw reply is parseable JSON.

Parseable is measured directly against the raw model reply (fence-stripped
json.loads), not against citations selected downstream. `parse_warrant_scores`
(generate.py) silently returns [0.0]*n on a decode failure, which is
indistinguishable from a legitimate all-zero warrant judgment once it reaches
select_citations — this probe exists precisely so that ambiguity never becomes
the measurement.

Two phases, run as two separate process invocations so the 1.5B answer generator
and the 7B judge are never resident at the same time (untested combination; the
R0 cost probe measured each model loaded alone alongside the embedder/reranker,
not two MLX models loaded together):

  1. answers — production pipeline (embedder + reranker + 1.5B generator) answers
     the 50 rows; dumps {id, query, answer_text, context_ids} per row.
  2. judge    — embedder + retriever (for chunk lookup by id) + 7B judge only;
     reads the phase-1 dump, prompts the judge, scores parseability.

Decision rule (§3.3): parseable-reply rate >= 80% on judged rows -> proceed to
the §4/§6 cohort run. Below 80% -> the arm is ABANDONED before the cohort run,
recorded as a no-op, not a negative result.

Usage:
  PYTHONPATH=src python scripts/analysis/warrant_degeneracy_probe.py --phase answers
  PYTHONPATH=src python scripts/analysis/warrant_degeneracy_probe.py --phase judge \
      [--judge-model mlx-community/Qwen2.5-7B-Instruct-4bit]
"""
from __future__ import annotations

import argparse
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

SCREEN = ROOT / "eval" / "probes" / "screen_v1.jsonl"
GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
ANSWERS_DUMP = ROOT / "reports" / "warrant-degeneracy-answers.json"
POOL, TOP_K = 50, 10
PARSEABLE_FLOOR = 0.80
DEFAULT_JUDGE_MODEL = "mlx-community/Qwen2.5-7B-Instruct-4bit"


def _load_screen() -> list[dict]:
    if not SCREEN.exists():
        raise SystemExit(f"{SCREEN} missing — run mechanism_screen.py first to freeze it")
    from sebi_rag.eval_harness import load_golden

    ids = {json.loads(l)["id"] for l in SCREEN.read_text().splitlines() if l.strip()}
    all_rows = {r["id"]: r for r in load_golden(GOLDEN)}
    missing = ids - set(all_rows)
    if missing:
        raise SystemExit(f"screen ids not found in golden_v7: {sorted(missing)}")
    return [all_rows[i] for i in sorted(ids)]


def _is_parseable(text: str) -> bool:
    """Mirrors generate.parse_warrant_scores' cleaning exactly, but reports
    whether the JSON decode itself succeeded rather than collapsing a failure
    to [0.0]*n — a parse failure and a legitimate all-zero judgment must stay
    distinguishable for this probe to mean anything."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(l for l in lines if not l.strip().startswith("```"))
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return False
    return isinstance(data, list) and len(data) > 0


def run_answers() -> None:
    from sebi_rag.api import build_default_pipeline

    screen = _load_screen()
    print(f"probe rows: {len(screen)} (from {SCREEN.name})", file=sys.stderr)
    print("building production pipeline (retriever + reranker + 1.5B generator)...",
          file=sys.stderr)
    pipe = build_default_pipeline()

    rows, t0 = [], time.time()
    for n, it in enumerate(screen, 1):
        ans, _ = pipe.query(it["query"], pool=POOL, top_k=TOP_K)
        rows.append({
            "id": it["id"], "task_type": it.get("task_type"), "query": it["query"],
            "abstained": bool(ans.abstained), "answer_text": ans.text,
            "context_ids": list(ans.context_ids),
        })
        if n % 10 == 0:
            print(f"  {n}/{len(screen)}", file=sys.stderr)

    out = {"generator_model": pipe.generator.__class__.__name__,
           "runtime_s": round(time.time() - t0, 1), "rows": rows}
    ANSWERS_DUMP.parent.mkdir(parents=True, exist_ok=True)
    ANSWERS_DUMP.write_text(json.dumps(out, indent=2), encoding="utf-8")
    n_answered = sum(1 for r in rows if not r["abstained"])
    print(f"wrote {ANSWERS_DUMP} ({n_answered}/{len(rows)} answered, "
          f"{out['runtime_s']}s)", file=sys.stderr)


def run_judge(judge_model: str, max_tokens: int = 512) -> None:
    if not ANSWERS_DUMP.exists():
        raise SystemExit(f"{ANSWERS_DUMP} missing — run --phase answers first")
    from sebi_rag.embeddings import BGEM3Embedder
    from sebi_rag.generate import WarrantJudge, _warrant_prompt
    from sebi_rag.retrieve import HybridRetriever
    from sebi_rag.settings import Settings

    dump = json.loads(ANSWERS_DUMP.read_text())
    s = Settings.load()
    print("loading embedder + retriever (chunk lookup only, no reranker/generator)...",
          file=sys.stderr)
    embedder = BGEM3Embedder()
    retriever = HybridRetriever.load(Path(s.index_dir), embedder)
    chunk_by_id = {c.id: c for c in retriever.chunks}
    print(f"loading warrant judge at {judge_model} (max_tokens={max_tokens}) ...",
          file=sys.stderr)
    judge = WarrantJudge(model=judge_model, max_tokens=max_tokens)

    rows, t0 = [], time.time()
    for n, r in enumerate(dump["rows"], 1):
        if r["abstained"] or not r["context_ids"]:
            rows.append({**{k: r[k] for k in ("id", "task_type")},
                         "abstained": True, "parseable": None})
            continue
        contexts = [chunk_by_id[cid] for cid in r["context_ids"] if cid in chunk_by_id]
        if not contexts:
            rows.append({**{k: r[k] for k in ("id", "task_type")},
                         "abstained": False, "parseable": None,
                         "note": "context_ids not found in the live chunk store"})
            continue
        prompt = _warrant_prompt(r["query"], r["answer_text"], contexts)
        reply = judge._reply(prompt)
        ok = _is_parseable(reply)
        rows.append({"id": r["id"], "task_type": r["task_type"], "abstained": False,
                     "parseable": ok, "n_contexts": len(contexts),
                     "reply_chars": len(reply), "reply_head": reply[:200]})
        if n % 10 == 0:
            print(f"  {n}/{len(dump['rows'])}", file=sys.stderr)

    judged = [r for r in rows if r["parseable"] is not None]
    ok_rows = [r for r in judged if r["parseable"]]
    rate = len(ok_rows) / max(len(judged), 1)
    verdict = ("PROCEED to §4/§6 cohort run" if rate >= PARSEABLE_FLOOR
               else "ABANDON — arm does not proceed to the cohort run (§3.3)")
    spec = ("docs/superpowers/specs/2026-08-20-warrant-citation-scorer-prereg.md §3.3"
            if max_tokens == 512 else
            "docs/superpowers/specs/2026-08-23-warrant-degeneracy-max-tokens-prereg.md")
    out = {
        "spec": spec,
        "endpoint": "parseable-reply rate on the frozen 50-row screen — gates whether "
                    "the cohort run happens; not itself a gated metric",
        "judge_model": judge_model,
        "max_tokens": max_tokens,
        "answer_generator": dump.get("generator_model"),
        "n_screen": len(rows),
        "n_judged": len(judged),
        "n_abstained_or_missing_context": len(rows) - len(judged),
        "n_parseable": len(ok_rows),
        "parseable_rate": round(rate, 3),
        "floor": PARSEABLE_FLOOR,
        "verdict": verdict,
        "runtime_s": round(time.time() - t0, 1),
        "rows": rows,
    }
    suffix = "" if max_tokens == 512 else f"-mt{max_tokens}"
    dest = ROOT / "reports" / f"warrant-degeneracy-probe-{judge_model.split('/')[-1]}{suffix}.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["answers", "judge"], required=True)
    ap.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    ap.add_argument("--max-tokens", type=int, default=512,
                     help="Judge output budget. 512 reproduces the original §3.3 result "
                          "(ABANDONED, 38.1%%); the 2026-08-23 retry preregisters 1024.")
    args = ap.parse_args()
    if args.phase == "answers":
        run_answers()
    else:
        run_judge(args.judge_model, args.max_tokens)


if __name__ == "__main__":
    main()
