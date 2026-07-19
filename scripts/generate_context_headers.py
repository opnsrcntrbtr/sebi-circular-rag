"""Generate contextual headers for deep sub-clause + annex chunks (iv9).

Resumable: chunk ids already present in --out are skipped, so an
interrupted multi-hour run continues where it stopped.

    PYTHONPATH=src .venv/bin/python scripts/generate_context_headers.py \
        [--out data/corpus/context_headers.jsonl] [--model ...] \
        [--limit N] [--ids ids.txt]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.context_headers import (  # noqa: E402
    HeaderGenerator, in_scope, load_headers,
)
from sebi_rag.corpus import load_circulars  # noqa: E402

_HEAD = re.compile(r"^\d+(?:\.\d+)*[.)]\s")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "data" / "corpus" / "context_headers.jsonl"))
    ap.add_argument("--model", default="mlx-community/Qwen2.5-1.5B-Instruct-4bit")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", default="")
    args = ap.parse_args()

    chunks = load_circulars(ROOT / "data" / "corpus" / "circulars.jsonl")
    done = set(load_headers(args.out))
    targets = [
        c for c in chunks
        if in_scope(c.id.split("#")[1]) and c.id not in done
    ]
    if args.ids:
        keep = {l.strip() for l in Path(args.ids).read_text().splitlines() if l.strip()}
        targets = [c for c in targets if c.id in keep]
    if args.limit:
        targets = targets[: args.limit]
    print(f"targets={len(targets)} (skipped {len(done)} already done)", flush=True)

    gen = HeaderGenerator.load(model=args.model)
    t0 = time.time()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "a", encoding="utf-8") as f:
        for i, c in enumerate(targets, 1):
            body = c.text.split("\n", 1)[1] if "\n" in c.text else c.text
            lines = body.splitlines()
            governing = lines[0] if lines and _HEAD.match(lines[0]) else ""
            h = gen.describe(c.meta.get("subject", ""), governing, body)
            f.write(json.dumps(
                {"chunk_id": c.id, "header": h, "model": args.model},
                ensure_ascii=False,
            ) + "\n")
            f.flush()
            if i % 100 == 0:
                rate = i / (time.time() - t0)
                print(f"{i}/{len(targets)}  {rate:.1f}/s  "
                      f"eta {((len(targets) - i) / rate) / 60:.0f} min", flush=True)
    print(f"done: {len(targets)} headers in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
