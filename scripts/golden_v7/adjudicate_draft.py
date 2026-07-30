"""Adjudicate draft rows using Qwen via oMLX.

Reads draft rows from golden_v7.jsonl, builds prompts from pools,
sends to Qwen via oMLX (127.0.0.1:8001), parses responses, and
writes votes to draft_votes.jsonl.

Usage:
    .venv/bin/python scripts/golden_v7/adjudicate_draft.py

This is a one-shot pass over all draft rows that have pools.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from sebi_rag.eval_harness import load_golden  # noqa: E402

from golden_v7.gemini_adjudicate import (  # noqa: E402
    DEFAULT_GOLDEN_PATH,
    DEFAULT_POOLS_PATH,
    GOVERNING_INSTRUCTIONS,
    ABSTAIN_INSTRUCTIONS,
    _shuffled_candidates,
    build_prompt,
    parse_reply,
)

ANNOTATOR = "qwen-draft"
DEFAULT_BASE_URL = "http://127.0.0.1:8001"
DEFAULT_MODEL = "Qwen3.6-35B-A3B-MLX-4bit"
DEFAULT_CACHE_DIR = ROOT / "eval" / "golden" / "v7_annotations" / "qwen-draft"
DEFAULT_DRAFT_VOTES_PATH = ROOT / "eval" / "golden" / "v7_annotations" / "draft_votes.jsonl"

_MAX_ATTEMPTS = 4
_THINK_RE = re.compile(r"\s*", re.DOTALL)


def _current_model() -> str:
    return os.environ.get("GOLDEN_LOCAL_MODEL", DEFAULT_MODEL)


def _strip_thinking(text: str) -> str:
    return _THINK_RE.sub("", text).strip()


def _post_local(prompt: str) -> str:
    """One blind-protocol call to the oMLX server."""
    model = _current_model()
    auth_token = os.environ.get("GOLDEN_LOCAL_AUTH_TOKEN") or os.environ.get(
        "ANTHROPIC_AUTH_TOKEN", ""
    )

    last = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            resp = httpx.post(
                f"{os.environ.get('GOLDEN_LOCAL_BASE_URL', DEFAULT_BASE_URL)}/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": int(os.environ.get("GOLDEN_LOCAL_MAX_TOKENS", 4096)),
                    "temperature": 0,
                },
                headers={
                    "Authorization": f"Bearer {auth_token}" if auth_token else "",
                    "Content-Type": "application/json",
                },
                timeout=int(os.environ.get("GOLDEN_LOCAL_TIMEOUT_S", 600)),
            )
            if resp.status_code == 200:
                data = resp.json()
                return _extract_text(data)
            last = f"HTTP {resp.status_code}: {resp.text[:200]}"
            if attempt < _MAX_ATTEMPTS:
                import time

                time.sleep(2**attempt)
        except Exception as e:
            last = str(e)
            if attempt < _MAX_ATTEMPTS:
                import time

                time.sleep(2**attempt)

    raise RuntimeError(f"local call failed after {_MAX_ATTEMPTS} attempts: {last}")


def _extract_text(payload: dict) -> str:
    """Extract text from oMLX chat completion response."""
    choices = payload.get("choices", [])
    if not choices:
        return ""
    msg = choices[0].get("message", {})
    text = msg.get("content", "") or ""
    return _strip_thinking(text)


def adjudicate_draft(rows: list[dict], pools: list[dict], ids: list[str]) -> list[dict]:
    """Run blind protocol over draft rows."""
    pool_map = {p["id"]: p for p in pools}
    votes = []

    # Load existing cache
    cache_dir = DEFAULT_CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)

    for row_id in ids:
        cache_path = cache_dir / f"{row_id}.json"
        if cache_path.exists():
            cached = json.loads(cache_path.read_text())
            # Check if we already have a valid vote
            if cached.get("governing") is not None or cached.get("abstain_reason"):
                votes.append(cached)
                continue

        row = next((r for r in rows if r["id"] == row_id), None)
        if not row:
            continue

        pool = pool_map.get(row_id)
        prompt = build_prompt(row, pool)

        # Cache the prompt for debugging
        (cache_dir / f"{row_id}_prompt.txt").write_text(prompt, encoding="utf-8")

        # Call oMLX
        reply = _post_local(prompt)
        (cache_dir / f"{row_id}_reply.txt").write_text(reply, encoding="utf-8")

        # Parse
        candidates = _shuffled_candidates(row_id, pool)
        letters = [c["letter"] for c in candidates] if candidates else []

        if row.get("abstain"):
            governing, expected, parse_error = [], "[]", False
        else:
            governing, expected, parse_error = parse_reply(reply, letters)

        vote = {
            "id": row_id,
            "annotator": ANNOTATOR,
            "governing": governing,
            "expected": expected,
            "parse_error": parse_error,
            "model": _current_model(),
        }

        # Cache the vote
        json.dump(vote, open(cache_path, "w"), ensure_ascii=False)
        votes.append(vote)

    return votes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Show what would be adjudicated")
    args = ap.parse_args()

    rows = load_golden(DEFAULT_GOLDEN_PATH)
    pools = [json.loads(line) for line in DEFAULT_POOLS_PATH.read_text().splitlines() if line.strip()]

    # Get draft rows with pools
    pool_ids = {p["id"] for p in pools}
    draft_rows = [r for r in rows if r.get("review_status") == "draft" and r["id"] in pool_ids]
    ids = [r["id"] for r in draft_rows]

    if args.dry_run:
        print(f"Draft rows with pools: {len(ids)}")
        for r in draft_rows[:10]:
            print(f"  {r['id']} ({r.get('task_type')})")
        return

    print(f"Adjudicating {len(ids)} draft rows via Qwen...")
    votes = adjudicate_draft(rows, pools, ids)

    # Write votes
    with open(DEFAULT_DRAFT_VOTES_PATH, "w") as f:
        for v in votes:
            f.write(json.dumps(v, ensure_ascii=False) + "\n")

    # Summary
    parse_errors = sum(1 for v in votes if v.get("parse_error"))
    print(f"Done: {len(votes)} votes written to {DEFAULT_DRAFT_VOTES_PATH}")
    print(f"  Parse errors: {parse_errors}")


if __name__ == "__main__":
    main()
