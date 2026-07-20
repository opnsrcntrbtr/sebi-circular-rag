"""Select + reuse iv9 headers for 3 failure-adjacent documents (iv10).

Pulls the iv9 sidecar from git history (the working tree no longer has it
after the iv9 revert), filters to the target documents, and generates one
fresh override header for probe-sup-04's chunk (excluded by iv9's
depth>=3-or-annex scope since its section id is "4.", depth 1).

    PYTHONPATH=src .venv/bin/python scripts/select_targeted_headers.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sebi_rag.context_headers import (  # noqa: E402
    HeaderGenerator, filter_targeted_rows,
)
from sebi_rag.corpus import load_circulars  # noqa: E402

TARGET_DOCS = {
    "SEBI/HO/DDHS/DDHS-POD2/P/CIR/2025/101",   # probe-par-03
    "SEBI/HO/CFD/PoD2/CIR/P/0155",             # probe-sup-04
    "SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/91",   # probe-tbl-05, probe-num-05
}
SUP04_DOC = "SEBI/HO/CFD/PoD2/CIR/P/0155"
OUT = ROOT / "data" / "corpus" / "context_headers_targeted.jsonl"


def main() -> None:
    iv9_text = subprocess.run(
        ["git", "show", "d6f323f:data/corpus/context_headers.jsonl"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    rows = [json.loads(l) for l in iv9_text.splitlines() if l.strip()]
    kept = filter_targeted_rows(rows, TARGET_DOCS)
    print(f"reused {len(kept)} rows from iv9 for {len(TARGET_DOCS)} docs", flush=True)

    chunks = load_circulars(ROOT / "data" / "corpus" / "circulars.jsonl")
    sup04_chunks = [
        c for c in chunks
        if c.doc_id == SUP04_DOC and c.id.split("#")[1].startswith("4.")
    ]
    if not sup04_chunks:
        raise SystemExit(f"no probe-sup-04 chunk found under {SUP04_DOC}")
    sup04 = sup04_chunks[0]
    body = sup04.text.split("\n", 1)[1] if "\n" in sup04.text else sup04.text
    gen = HeaderGenerator.load()
    header = gen.describe(sup04.meta.get("subject", ""), "", body)
    kept.append({"chunk_id": sup04.id, "header": header,
                 "model": "mlx-community/Qwen2.5-7B-Instruct-4bit"})
    print(f"sup-04 override chunk: {sup04.id}\n  header: {header!r}", flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(kept)} rows -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
