"""External annotation slice: local-model leg via oMLX - the PRIMARY leg
since 2026-07-26, replacing the Gemini leg (ON HOLD: its free tier allows
~20 requests/day/model against this task's 100).

Same blind protocol as the gemini leg - build_prompt, parse_reply, the
cache, and the votes.jsonl rewrite are imported from gemini_adjudicate.py,
which stays the protocol's home. What is different here is only transport
and identity: replies come from an Anthropic-compatible server on localhost
(oMLX serving Qwen3.6-35B-A3B-MLX-4bit), votes carry annotator "qwen", and
each cache entry records the exact local model id. Qwen is a second model
family (Alibaba, not Anthropic), so spec sec7's independence requirement
holds exactly as it would have with Gemini.

Blindness is structural: the annotator model only ever sees the lettered
prompt over HTTP - never the repo, never claude's votes.

Env (all defaulted): GOLDEN_LOCAL_BASE_URL (http://127.0.0.1:8000),
GOLDEN_LOCAL_MODEL (Qwen3.6-35B-A3B-MLX-4bit), GOLDEN_LOCAL_AUTH_TOKEN
(falls back to ANTHROPIC_AUTH_TOKEN - the oMLX launch command sets it),
GOLDEN_LOCAL_MAX_TOKENS (4096: Qwen thinking spends output tokens before
the answer, so a tight cap truncates mid-think and every row parse-fails),
GOLDEN_LOCAL_TIMEOUT_S (600: the first call may load ~20 GB of weights).

NOTE: `make serve` also binds port 8000 - do not run the FastAPI service
and oMLX together, or override PORT for one of them.

Pilot (measure agreement vs claude BEFORE spending the full pass - the
5-row gemini probe caught a prompt-protocol bug exactly this way):
    .venv/bin/python scripts/golden_v7/local_adjudicate.py --pilot 5
Real run (all 100 external ids, resumable, cache-backed):
    make golden-v7-local
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from sebi_rag.eval_harness import load_golden  # noqa: E402

from golden_v7.gemini_adjudicate import (  # noqa: E402
    DEFAULT_GOLDEN_PATH,
    DEFAULT_POOLS_PATH,
    DEFAULT_SAMPLE_PATH,
    DEFAULT_VOTES_PATH,
    _parse_error_ids,
    _replace_annotator_votes,
    _should_retry,
    _shuffled_candidates,
    adjudicate,
)

ANNOTATOR = "qwen"
DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_MODEL = "Qwen3.6-35B-A3B-MLX-4bit"
DEFAULT_CACHE_DIR = ROOT / "eval" / "golden" / "v7_annotations" / "qwen"

_MAX_ATTEMPTS = 4
_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL)


def _current_model() -> str:
    return os.environ.get("GOLDEN_LOCAL_MODEL", DEFAULT_MODEL)


def _strip_thinking(text: str) -> str:
    """Qwen-family models may emit <think>...</think> reasoning as inline
    text, depending on the server's chat template. The strict parser reads
    the FIRST non-blank line as the letter choice, so unstripped reasoning
    would fail-closed on every single row. Stripping happens at the
    transport layer - the protocol itself stays byte-identical to the
    gemini leg's."""
    return _THINK_RE.sub("", text).strip()


def _extract_text(payload: dict) -> str:
    """Anthropic Messages response -> reply text: concatenates `text`
    content blocks, skipping `thinking` blocks if the server surfaces
    reasoning that way instead of inline tags."""
    return "".join(b.get("text", "") for b in payload.get("content", [])
                   if b.get("type") == "text").strip()


def _post_local(prompt: str) -> str:
    """One blind-protocol call to the oMLX server. Sends both auth header
    styles (x-api-key and Bearer) - Anthropic clients use either, and which
    one oMLX checks is configuration-dependent. Retries transport errors
    and 5xx with linear backoff: the first call after server start triggers
    the model load (~20 GB), and a second client hitting the server mid-load
    can see transient failures. No daily-quota concept exists locally."""
    token = (os.environ.get("GOLDEN_LOCAL_AUTH_TOKEN")
             or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
    if not token:
        raise RuntimeError(
            "no oMLX token: set GOLDEN_LOCAL_AUTH_TOKEN (or launch inside a "
            "session that sets ANTHROPIC_AUTH_TOKEN)")
    base = os.environ.get("GOLDEN_LOCAL_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    timeout = float(os.environ.get("GOLDEN_LOCAL_TIMEOUT_S", "600"))
    max_tokens = int(os.environ.get("GOLDEN_LOCAL_MAX_TOKENS", "4096"))

    last: Exception | None = None
    for attempt in range(_MAX_ATTEMPTS):
        try:
            resp = httpx.post(
                f"{base}/v1/messages",
                headers={"x-api-key": token,
                         "Authorization": f"Bearer {token}",
                         "anthropic-version": "2023-06-01"},
                json={"model": _current_model(), "max_tokens": max_tokens,
                      "messages": [{"role": "user", "content": prompt}]},
                timeout=timeout)
            if _should_retry(resp.status_code) and attempt < _MAX_ATTEMPTS - 1:
                time.sleep(5 * (attempt + 1))
                continue
            resp.raise_for_status()
            return _strip_thinking(_extract_text(resp.json()))
        except httpx.TransportError as e:
            last = e
            if attempt == _MAX_ATTEMPTS - 1:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"local call failed after {_MAX_ATTEMPTS} attempts: {last}")


def _pilot_ids(rows_by_id: dict, ids: list[str], n: int) -> list[str]:
    """First `n` non-abstain external ids, distinct strata first: five rows
    from five strata measure more than five from one."""
    picked: list[str] = []
    seen_types: set[str] = set()
    for rid in ids:
        row = rows_by_id[rid]
        if row.get("abstain") or row["task_type"] in seen_types:
            continue
        seen_types.add(row["task_type"])
        picked.append(rid)
        if len(picked) == n:
            return picked
    for rid in ids:  # fill remaining slots ignoring stratum novelty
        if rid in picked or rows_by_id[rid].get("abstain"):
            continue
        picked.append(rid)
        if len(picked) == n:
            break
    return picked


def pilot(rows: list[dict], pools: list[dict], ids: list[str],
          claude_votes: dict[str, list[str]], post, n: int,
          cache_dir: str | Path) -> list[dict]:
    """Adjudicates `n` non-abstain rows and compares exact governing sets
    against claude's votes. Never touches votes.jsonl - a pilot informs the
    go/no-go decision, it must not half-populate the real artifact. Rows it
    caches are reused free by the full run."""
    rows_by_id = {r["id"]: r for r in rows}
    chosen = _pilot_ids(rows_by_id, ids, n)
    votes = adjudicate(rows, pools, chosen, post, cache_dir=cache_dir,
                       annotator=ANNOTATOR, model=_current_model())
    pools_by_id = {p["id"]: p for p in pools}
    results = []
    for v in votes:
        rid = v["id"]
        letters = {c["chunk_id"]: chr(ord("A") + i) for i, c in
                   enumerate(_shuffled_candidates(rid, pools_by_id.get(rid)))}
        claude = claude_votes.get(rid, [])
        results.append({
            "id": rid, "task_type": rows_by_id[rid]["task_type"],
            "claude": sorted(letters.get(c, "?") for c in claude),
            ANNOTATOR: sorted(letters.get(c, "?") for c in v["governing"]),
            "match": frozenset(claude) == frozenset(v["governing"]),
        })
    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", type=int, default=0, metavar="N",
                    help="adjudicate N non-abstain rows (distinct strata "
                         "first), print agreement vs claude, and exit "
                         "WITHOUT writing votes.jsonl")
    args = ap.parse_args()

    rows = load_golden(DEFAULT_GOLDEN_PATH)
    pools = [json.loads(line) for line in
             DEFAULT_POOLS_PATH.read_text(encoding="utf-8").splitlines()
             if line.strip()]
    sample = json.loads(DEFAULT_SAMPLE_PATH.read_text(encoding="utf-8"))
    ids = sample["external"]

    if args.pilot:
        claude_votes = {}
        for line in DEFAULT_VOTES_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                v = json.loads(line)
                if v["annotator"] == "claude":
                    claude_votes[v["id"]] = v["governing"]
        results = pilot(rows, pools, ids, claude_votes, _post_local,
                        args.pilot, DEFAULT_CACHE_DIR)
        matches = sum(r["match"] for r in results)
        for r in results:
            print(f"{r['id']:<14} {r['task_type']:<22} "
                  f"claude={','.join(r['claude']) or '-':<10} "
                  f"{ANNOTATOR}={','.join(r[ANNOTATOR]) or 'NONE':<14} "
                  f"{'MATCH' if r['match'] else 'differ'}")
        print(f"\nexact-set agreement: {matches}/{len(results)} "
              f"(model {_current_model()})")
        return

    qwen_votes = adjudicate(rows, pools, ids, _post_local,
                            cache_dir=DEFAULT_CACHE_DIR,
                            annotator=ANNOTATOR, model=_current_model())

    bad_ids = _parse_error_ids(ids, DEFAULT_CACHE_DIR)
    if bad_ids:
        print(f"WARNING: {len(bad_ids)} of {len(ids)} row(s) had an "
              f"unparseable reply (parse_error=true in cache), "
              f"needs a human look: {bad_ids}")

    existing = []
    if DEFAULT_VOTES_PATH.exists():
        existing = [json.loads(line) for line in
                    DEFAULT_VOTES_PATH.read_text(encoding="utf-8").splitlines()
                    if line.strip()]
    all_votes = _replace_annotator_votes(existing, qwen_votes, ANNOTATOR)

    with DEFAULT_VOTES_PATH.open("w", encoding="utf-8") as f:
        for v in all_votes:
            f.write(json.dumps(v, ensure_ascii=False) + "\n")

    print(f"{ANNOTATOR} votes: {len(qwen_votes)} (of {len(ids)} ids) "
          f"-> {DEFAULT_VOTES_PATH}")


if __name__ == "__main__":
    main()
