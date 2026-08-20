"""Does answering a golden_v7 row require a circular the corpus does not hold?

Spec: docs/superpowers/specs/2026-08-20-dangling-citation-dependence-prereg.md.
Read-only. Ships no code, moves no floor.

Judge names the required circular; the NAME is checked against the corpus in
code, so a "dependent" verdict is verifiable rather than self-reported.

Usage: PYTHONPATH=src python scripts/analysis/dangling_dependence.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

ENDPOINT = os.environ.get("OMLX_URL", "http://127.0.0.1:8001/v1/chat/completions")
MODEL = os.environ.get("OMLX_MODEL", "Qwen3.6-35B-A3B-OptiQ-4bit")
WINDOW = 6000            # §2: +/- 6,000 chars around each labelled quote
CTX_CAP = 40000          # bound prefill; truncation count is reported
GOLDEN = ROOT / "eval" / "golden" / "golden_v7.jsonl"
DEST = ROOT / "reports" / "dangling-dependence-2026-08-20-run3.json"

PROMPT = """You are a strict auditor for a legal retrieval system.

Below is an excerpt from a SEBI circular, followed by a question.

Excerpt:
<<<BEGIN EXCERPT>>>
{ctx}
<<<END EXCERPT>>>

Question: {q}

Can this question be answered COMPLETELY and CORRECTLY from the excerpt alone?

If the excerpt defers to another SEBI circular for the substance of the answer -- for
example "as specified in Circular X", "in terms of Circular Y" -- then it cannot, and
you must name that circular exactly as it is written in the excerpt.

Answer with the single word SUFFICIENT if the excerpt alone suffices. Otherwise
answer with the word NEEDS, a colon, and the circular number copied from the excerpt.
Output that one line only."""


def call(prompt: str, retries: int = 2) -> tuple[str, str]:
    """Returns (answer, reasoning). The judge is a reasoning model: the oMLX API
    separates its chain of thought into `reasoning_content`, leaving `content`
    clean. Thinking is left ENABLED — this is a legal judgement and the quality
    is worth ~4 s/row — and only `content` is parsed."""
    # RUN 2 (run 1 VOID): thinking DISABLED. With it on, a real prompt needs
    # >1024 completion tokens, hits finish_reason=length mid-thought, the
    # thinking block never closes, oMLX cannot split it out, and raw reasoning
    # lands in `content` — which run 1 then parsed as if it were an answer.
    # This task is a bounded extractive classification; deliberation is not
    # required, and a single strict line is.
    # RUN 3: thinking ON. Two findings forced this shape, both verified first:
    #  * guided_grammar and thinking are MUTUALLY EXCLUSIVE here — the grammar
    #    constrains from token 0, so the thinking block is never emitted
    #    (measured: reasoning_content=0, 3 output tokens, and a flipped answer).
    #    Deliberation is the point of run 3, so grammar is off.
    #  * the run-2 answer format ("NEEDS: <circular ...>") makes the model echo
    #    the placeholder literally under thinking — 'NEEDS: <circular>', 2/2
    #    deterministic. The format is reworded to remove the angle brackets.
    # max_tokens 8192 (server default) with thinking_budget_enabled=false.
    body = json.dumps({
        "model": MODEL, "temperature": 0, "max_tokens": 8192,
        "chat_template_kwargs": {"enable_thinking": True,
                                 "reasoning_effort": "medium"},
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    for a in range(retries + 1):
        try:
            req = urllib.request.Request(
                ENDPOINT, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.loads(r.read())
            ch = d["choices"][0]
            if ch.get("finish_reason") == "length":
                # never silently accept a truncated reply again
                return ("__TRUNCATED__", "")
            m = ch["message"]
            return ((m.get("content") or "").strip(),
                    (m.get("reasoning_content") or "")[:400])
        except Exception as e:  # noqa: BLE001
            if a == retries:
                return (f"__ERROR__ {e}", "")
            time.sleep(3)
    return ("__ERROR__", "")


def _norm(x: str) -> str:
    """Uppercase, strip all whitespace — so 'CIR/MIRSD/5/ 2013' matches
    'CIR/MIRSD/5/2013'."""
    return re.sub(r"\s+", "", x).upper()


def windows(text: str, quotes: list[str]) -> str:
    spans = []
    for q in quotes:
        i = text.find(q[:120]) if q else -1
        if i < 0:
            continue
        spans.append((max(0, i - WINDOW), min(len(text), i + len(q) + WINDOW)))
    if not spans:
        return text[: 2 * WINDOW]
    spans.sort()
    merged = [list(spans[0])]
    for a, b in spans[1:]:
        if a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return "\n[...]\n".join(text[a:b] for a, b in merged)


def main() -> None:
    from sebi_rag.lineage import REF_RE, load_records
    from sebi_rag.settings import Settings

    recs = load_records(Settings.load().corpus_path)
    by = {r["circular_number"]: r for r in recs}
    held = set(by)
    golden = [json.loads(l) for l in GOLDEN.read_text().splitlines() if l.strip()]

    gold: set[str] = set()
    for g in golden:
        gold.update(g.get("relevant_circulars") or [])
    ordinary = {g for g in gold & held
                if "master" not in (by[g].get("subject") or "").lower()}
    dangling = {}
    for g in ordinary:
        outs = {m.group(0) for m in REF_RE.finditer(by[g].get("text", ""))} - {g} - held
        if outs:
            dangling[g] = outs
    clean = ordinary - set(dangling)

    groups = {
        "treatment": [r for r in golden
                      if set(r.get("relevant_circulars") or []) & set(dangling)],
        "control": [r for r in golden
                    if (set(r.get("relevant_circulars") or []) & clean)
                    and not (set(r.get("relevant_circulars") or []) & set(dangling))],
    }
    print({k: len(v) for k, v in groups.items()}, file=sys.stderr)

    out_rows = []
    for gname, rows in groups.items():
        for n, r in enumerate(rows, 1):
            docs = [c for c in (r.get("relevant_circulars") or []) if c in by]
            quotes = [c.get("quote") or "" for c in (r.get("relevant_chunks") or [])]
            ctx = "\n\n[--- next document ---]\n\n".join(
                windows(by[d].get("text", ""), quotes) for d in docs[:2])
            truncated = len(ctx) > CTX_CAP
            reply, reasoning = call(PROMPT.format(ctx=ctx[:CTX_CAP], q=r["query"]))
            # Strict parse: last non-empty line only, prefix-anchored, and the
            # circular is taken from AFTER the NEEDS marker. Run 1 used
            # `"NEEDS" in reply` + REF_RE.search(whole reply), which picked up
            # the first circular number anywhere in the text — frequently the
            # excerpt's OWN number rather than the model's answer.
            named, verdict = None, "unparseable"
            lines = [x.strip() for x in reply.splitlines() if x.strip()]
            last = lines[-1] if lines else ""
            up = last.upper()
            if up.startswith("SUFFICIENT"):
                verdict = "sufficient"
            elif up.startswith("NEEDS"):
                tail = last[last.upper().index("NEEDS") + len("NEEDS"):]
                m = REF_RE.search(tail)
                if m:
                    named = m.group(0)
                    verdict = "needs_unheld" if named not in held else "needs_held"
                else:
                    verdict = "needs_unnamed"
            out_rows.append({
                "id": r["id"], "group": gname, "task_type": r.get("task_type"),
                "verdict": verdict, "named": named,
                # Normalised containment: the judge may reformat a circular
                # number (spacing/case) without fabricating it, and a raw
                # substring test would score that as fabrication. Fixed BEFORE
                # seeing any run-2 result — the guardrail THRESHOLD (§4.4, 20%)
                # is untouched.
                "named_in_context": bool(named and _norm(named) in _norm(ctx)),
                "ctx_chars": len(ctx), "ctx_truncated": truncated,
                "reply": reply[:200],
                # kept only for verifiable-dependent rows, so a human can audit
                "reasoning": reasoning if verdict == "needs_unheld" else None,
            })
            if n % 10 == 0:
                print(f"  {gname} {n}/{len(rows)}", file=sys.stderr)

    def rate(g: str) -> tuple[int, int, float]:
        rs = [x for x in out_rows if x["group"] == g]
        dep = sum(1 for x in rs if x["verdict"] == "needs_unheld")
        return dep, len(rs), round(100 * dep / max(len(rs), 1), 1)

    t_dep, t_n, T = rate("treatment")
    c_dep, c_n, C = rate("control")
    unparse = sum(1 for x in out_rows if x["verdict"] == "unparseable")
    dep_rows = [x for x in out_rows if x["verdict"] == "needs_unheld"]
    fabricated = sum(1 for x in dep_rows if not x["named_in_context"])

    strat = {}
    for st in sorted({x["task_type"] for x in out_rows}):
        a = [x for x in out_rows if x["task_type"] == st and x["group"] == "treatment"]
        b = [x for x in out_rows if x["task_type"] == st and x["group"] == "control"]
        if a and b:
            ta = 100 * sum(1 for x in a if x["verdict"] == "needs_unheld") / len(a)
            tb = 100 * sum(1 for x in b if x["verdict"] == "needs_unheld") / len(b)
            strat[st] = {"treat_n": len(a), "treat_pct": round(ta, 1),
                         "ctrl_n": len(b), "ctrl_pct": round(tb, 1),
                         "delta_pp": round(ta - tb, 1)}

    out = {
        "spec": "docs/superpowers/specs/2026-08-20-dangling-citation-dependence-prereg.md",
        "run": 3,
        "run2": "reports/dangling-dependence-2026-08-20-run2.json — thinking OFF, "
                "T=2.4% C=0.0%; run 3 repeats with deliberation enabled",
        "run1": "VOID — reports/dangling-dependence-2026-08-20-run1-VOID.json; thinking "
                "hit finish_reason=length mid-thought, so partial reasoning landed in "
                "`content` and was parsed as an answer",
        "model": MODEL, "window_chars": WINDOW, "thinking": True,
        "reasoning_effort": "medium", "guided_grammar": False,
        "treatment": {"dependent": t_dep, "n": t_n, "pct": T},
        "control": {"dependent": c_dep, "n": c_n, "pct": C},
        "delta_pp": round(T - C, 1),
        "validity": {
            "ctx_truncated_rows": sum(1 for x in out_rows if x["ctx_truncated"]),
            "unparseable": unparse,
            "unparseable_pct": round(100 * unparse / len(out_rows), 1),
            "fabricated_names": fabricated,
            "fabricated_pct": round(100 * fabricated / max(len(dep_rows), 1), 1),
        },
        "by_stratum": strat,
        "verdict_counts": dict(Counter(x["verdict"] for x in out_rows)),
        "rows": out_rows,
    }
    DEST.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
