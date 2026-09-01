"""Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-
bright-dawn.md): merge a trained LoRA adapter into base bge-m3 weights and
save a full standalone model directory.

The merge is REQUIRED, not optional: FlagEmbedding's BGEM3FlagModel (what
BGEM3Embedder wraps, embeddings.py:51-56) has no PEFT-adapter-loading path
- it only ever loads a plain model directory. A LoRA adapter alone is
useless to production; only a merged directory is.

Mechanics verified empirically on the REAL trained adapter before writing
this for real (a throwaway smoke test, not kept): PeftModel.from_pretrained
+ merge_and_unload folds the adapter's delta into the base weights (a
non-trivial embedding shift confirmed - 0.75 L2 distance on unit vectors,
out of a max of 2.0), the merged model saves at ~2.18 GB (matching the base
model's own scale, not the ~44 MB adapter), and reloading it fresh from
disk reproduces bit-identical output to the merged in-memory model.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/finetune/merge_adapter.py
Output:
    models/bge-m3-sebi-v1/ (~2.2 GB, loadable by
    BGEM3Embedder(model_path="models/bge-m3-sebi-v1") unchanged)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
for k, v in {
    "TOKENIZERS_PARALLELISM": "false", "OMP_NUM_THREADS": "1",
    "PYTORCH_ENABLE_MPS_FALLBACK": "1", "HF_HUB_DISABLE_XET": "1",
}.items():
    os.environ.setdefault(k, v)

DEFAULT_ADAPTER_DIR = ROOT / "models" / "bge-m3-sebi-v1-adapter"
DEFAULT_BASE_MODEL = "BAAI/bge-m3"
DEFAULT_OUTPUT = ROOT / "models" / "bge-m3-sebi-v1"


def sha256_dir(path: Path) -> dict[str, str]:
    """Per-file sha256 of every file in the merged model dir - the plan's
    "sha256 into the index manifest" step. A dict (not one hash over the
    whole tree) so a single-file mismatch is diagnosable later without
    re-hashing everything."""
    out = {}
    for f in sorted(path.rglob("*")):
        if f.is_file():
            h = hashlib.sha256()
            h.update(f.read_bytes())
            out[str(f.relative_to(path))] = h.hexdigest()
    return out


def merge(base_model: str, adapter_dir: Path, output_dir: Path,
         device: str = "cpu") -> None:
    """CPU by design, not MPS: this is a one-shot weight merge, not a
    training or encoding workload where MPS throughput matters, and CPU
    avoids any MPS-specific dtype/precision quirks touching the final
    production weights."""
    from peft import PeftModel
    from sentence_transformers import SentenceTransformer

    print(f"loading base model {base_model}...")
    model = SentenceTransformer(base_model, device=device)

    print(f"loading adapter from {adapter_dir}...")
    peft_model = PeftModel.from_pretrained(model[0].auto_model, str(adapter_dir))

    print("merging...")
    merged = peft_model.merge_and_unload()
    model[0].auto_model = merged

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"saving merged model -> {output_dir}...")
    model.save(str(output_dir))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-model", default=DEFAULT_BASE_MODEL)
    ap.add_argument("--adapter-dir", default=str(DEFAULT_ADAPTER_DIR))
    ap.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()

    output_dir = Path(args.output_dir)
    merge(args.base_model, Path(args.adapter_dir), output_dir, args.device)

    print("computing sha256 manifest...")
    manifest = {
        "base_model": args.base_model,
        "adapter_dir": args.adapter_dir,
        "files": sha256_dir(output_dir),
    }
    manifest_path = output_dir / "MERGE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    total_mb = sum(f.stat().st_size for f in output_dir.rglob("*")
                  if f.is_file()) / 1024 / 1024
    print(f"-> {output_dir} ({total_mb:.0f} MB, "
         f"manifest -> {manifest_path.name})")


if __name__ == "__main__":
    main()
