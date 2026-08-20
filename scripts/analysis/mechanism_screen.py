"""T-Screen: does the generator follow the citation instruction at all?

Spec: docs/superpowers/specs/2026-08-19-fast-gate-tier-prereg.md §2.1.
Gates R0 (docs/research-roadmap-2026-08-19.md).

`_grounded_prompt` (generate.py:380) instructs "Cite the circular id(s) in
square brackets." Qwen2.5-1.5B-Instruct-4bit emitted 0 parseable brackets over
48 rows (2026-08-03), which is what makes every instruction-dependent
mechanism in the roadmap unavailable. This screen asks one question of a
candidate generator: does the mechanism fire.

Per §2.1 the endpoint is mechanism-firing, NOT quality. A firing rate of 0
rejects the arm outright; a non-zero rate licenses T-Cohort and nothing more.
No gated metric is reported and no floor may be derived from this.

Usage: PYTHONPATH=src SEBI_RAG_MLX_MODEL=<model> python scripts/analysis/mechanism_screen.py
"""
from __future__ import annotations

import json
import os
import random
import re
import sys
import time
from collections import Counter
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
SCREEN = ROOT / "eval" / "probes" / "screen_v1.jsonl"
SEED = 20260819          # frozen; §2.1 "drawn once, seed fixed"
N = 50
POOL, TOP_K = 50, 10
BRACKET = re.compile(r"\[([^\]]+)\]")


def build_screen(items: list[dict]) -> list[dict]:
    """50 rows stratified proportionally to golden_v7's eight strata."""
    by = {}
    for it in items:
        by.setdefault(it.get("task_type") or "unknown", []).append(it)
    total = len(items)
    # largest-remainder apportionment so the strata sum to exactly N
    quota = {k: N * len(v) / total for k, v in by.items()}
    take = {k: int(q) for k, q in quota.items()}
    for k, _ in sorted(quota.items(), key=lambda kv: -(kv[1] - int(kv[1])))[:N - sum(take.values())]:
        take[k] += 1
    rng = random.Random(SEED)
    out = []
    for k in sorted(by):
        out.extend(rng.sample(sorted(by[k], key=lambda r: r["id"]), take[k]))
    return sorted(out, key=lambda r: r["id"])


def main() -> None:
    from sebi_rag.api import build_default_pipeline
    from sebi_rag.eval_harness import _doc, load_golden
    from sebi_rag.settings import Settings

    s = Settings.load()
    model = os.environ.get("SEBI_RAG_MLX_MODEL", s.mlx_model)

    items = load_golden(GOLDEN)
    if SCREEN.exists():
        ids = {json.loads(l)["id"] for l in SCREEN.read_text().splitlines() if l.strip()}
        screen = [i for i in items if i["id"] in ids]
        print(f"reusing {SCREEN.name} ({len(screen)} rows)", file=sys.stderr)
    else:
        screen = build_screen(items)
        SCREEN.parent.mkdir(parents=True, exist_ok=True)
        SCREEN.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in screen),
                          encoding="utf-8")
        print(f"wrote {SCREEN.name} ({len(screen)} rows, seed={SEED})", file=sys.stderr)
    print("strata: " + json.dumps(dict(Counter(r.get("task_type") for r in screen))),
          file=sys.stderr)

    pipe = build_default_pipeline()
    print(f"model={model}", file=sys.stderr)

    rows, t0 = [], time.time()
    for n, it in enumerate(screen, 1):
        ans, _ = pipe.query(it["query"], pool=POOL, top_k=TOP_K)
        ctx_docs = {_doc(i) for i in ans.context_ids}
        brackets = BRACKET.findall(ans.text)
        # a bracket "resolves" when its text names a circular in the context window
        resolved = [b for b in brackets
                    if any(d and (d in b or b.strip() in d) for d in ctx_docs)]
        rows.append({"id": it["id"], "task_type": it.get("task_type"),
                     "abstained": bool(ans.abstained),
                     "n_brackets": len(brackets), "n_resolved": len(resolved),
                     "brackets": brackets[:5], "chars": len(ans.text)})
        if n % 10 == 0:
            print(f"  {n}/{len(screen)}", file=sys.stderr)

    answered = [r for r in rows if not r["abstained"]]
    any_b = [r for r in answered if r["n_brackets"] > 0]
    res_b = [r for r in answered if r["n_resolved"] > 0]
    out = {
        "spec": "docs/superpowers/specs/2026-08-19-fast-gate-tier-prereg.md §2.1",
        "endpoint": "mechanism-firing only — NOT a gated metric, no floor may be derived",
        "model": model, "seed": SEED, "n_screen": len(rows),
        "runtime_s": round(time.time() - t0, 1),
        "n_answered": len(answered), "n_abstained": len(rows) - len(answered),
        "rows_with_any_bracket": len(any_b),
        "rows_with_resolved_bracket": len(res_b),
        "firing_rate_any": round(len(any_b) / max(len(answered), 1), 3),
        "firing_rate_resolved": round(len(res_b) / max(len(answered), 1), 3),
        "brackets_total": sum(r["n_brackets"] for r in answered),
        "verdict": ("REJECT — mechanism never fires" if not any_b
                    else "LICENSES T-Cohort — mechanism fires; says nothing about quality"),
        "rows": rows,
    }
    dest = ROOT / "reports" / f"mechanism-screen-{model.split('/')[-1]}.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
