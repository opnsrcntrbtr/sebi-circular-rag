"""Pilot gate (iv11): confirm Splade_PP assigns bridging terms across the
residual paraphrase gaps BEFORE paying the ~3.5h full-corpus encode.

For each residual query + its known answer chunk text, encode both, and
print the top overlapping expansion terms (by min weight). A healthy signal
is a non-trivial shared statutory/lay term set (e.g. the AIF query and the
AIF answer chunk sharing 'fund'/'investment'/'alternative').

    PYTHONPATH=src .venv/bin/python scripts/splade_pilot.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {"TOKENIZERS_PARALLELISM": "false", "PYTORCH_ENABLE_MPS_FALLBACK": "1",
             "HF_HUB_DISABLE_XET": "1"}.items():
    os.environ.setdefault(k, v)

from transformers import AutoTokenizer

from sebi_rag.splade_encoder import SpladeEncoder

# Residual failure queries (report §5.5) with a short lay description of the
# answer text to sanity-check bridging. Full answer chunks are large; a
# representative snippet is sufficient for a go/no-go term-overlap read.
PILOT = [
    ("Category II private pooled investment vehicle registration",
     "Alternative Investment Fund AIF registered with the Board under regulations"),
    ("winding down rating agency pull ongoing assignments",
     "credit rating agency surrender of certificate not take any new clients"),
    ("which appendix serial numbers withdrawn on issuance",
     "circulars listed at Sl. No. 68-74 in the Appendix shall stand rescinded"),
]


def main() -> None:
    encode = SpladeEncoder.load()
    tok = AutoTokenizer.from_pretrained("prithivida/Splade_PP_en_v1")
    inv = {v: k for k, v in tok.get_vocab().items()}
    for q, a in PILOT:
        mq = encode([q]).tocoo()
        ma = encode([a]).tocoo()
        wq = {int(j): float(v) for j, v in zip(mq.col, mq.data)}
        wa = {int(j): float(v) for j, v in zip(ma.col, ma.data)}
        shared = sorted(
            ((min(wq[j], wa[j]), inv[j]) for j in set(wq) & set(wa)),
            reverse=True,
        )[:12]
        print(f"\nQUERY: {q}\n  shared terms: {[t for _, t in shared]}")


if __name__ == "__main__":
    main()
