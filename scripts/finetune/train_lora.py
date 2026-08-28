"""Phase 0 (bge-m3 SEBI fine-tuning, .claude/plans/deep-analyse-and-research-
bright-dawn.md): LoRA fine-tune bge-m3's dense path on mined SEBI pairs.

LoRA over full fine-tuning by design (locked decision #3): full FT gains
~6 MRR@10 on train but only 0.4 on dev while LoRA wins on independent test
sets - full FT overfits, the dominant risk on a 730-1490-document corpus.
Dense path only - sparse_linear.pt / colbert_linear.pt are never touched,
production only reads return_dense=True (embeddings.py:69-71).

Mechanics verified empirically before writing this script (a throwaway
smoke test, not kept): SentenceTransformer.add_adapter(LoraConfig(...))
correctly reduces trainable params to ~1.25% of the full model (7.1M of
567.8M at r=16 on query/key/value/dense), and model.save_pretrained()
after training saves ONLY the adapter (~28 MB of weights, not the 2.27 GB
base model).

Data format: each line of --pairs is {"query": str, "positive": str,
"neg": [str, ...], "template": str, "source_doc": str} - the schema
mine_structural_pairs.py emits (and synthesize_queries.py / roundtrip_
filter.py will emit in Phase 1, for the same consumer). Only "query",
"positive", and the first --n-negs entries of "neg" are used here;
"template"/"source_doc" are provenance, not model input.

sentence-transformers' MultipleNegativesRankingLoss consumes a `Dataset`
whose columns are (anchor, positive, negative_1, ..., negative_n) IN THAT
ORDER - role is positional, not name-matched, so column construction order
here is significant, not cosmetic.

⚠️ Do not run this alongside a resident oMLX model. oMLX's own memory
guard (memory_guard_custom_ceiling_gb) and this training run both want
real headroom on a 48 GB machine; the plan requires them sequenced, never
concurrent.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/finetune/train_lora.py
"""
from __future__ import annotations

import argparse
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

DEFAULT_PAIRS = [ROOT / "data" / "finetune" / "pairs_structural.jsonl"]
DEFAULT_OUTPUT = ROOT / "models" / "bge-m3-sebi-v1-adapter"
DEFAULT_BASE_MODEL = "BAAI/bge-m3"

# Locked config (plan's "Why LoRA, and why merged" + Phase 2 defaults).
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.1
LORA_TARGET_MODULES = ["query", "key", "value", "dense"]  # standard RoBERTa
                                                            # attention naming,
                                                            # confirmed against
                                                            # the loaded model
                                                            # (see docstring)
N_NEGATIVES = 4  # 1 positive + 4 hard negatives, per the plan's Phase 2 spec;
                  # mine_structural_pairs.py mines 5 per query, the 5th is
                  # unused buffer, never a silent pad
LEARNING_RATE = 1e-5
TEMPERATURE = 0.02  # MNRL's `scale` is 1/temperature (verified against the
                    # installed sentence-transformers: scale=20.0 default
                    # <-> temperature=0.05) -> scale = 50.0
MNRL_SCALE = 1.0 / TEMPERATURE
QUERY_MAX_LEN = 512
PASSAGE_MAX_LEN = 512


def load_pairs(paths: list[Path], n_negatives: int) -> list[dict]:
    rows = []
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if len(r["neg"]) < n_negatives:
                continue  # defensive; mine_structural_pairs.py already
                          # guarantees >=5, but a hand-edited/foreign file
                          # might not
            rows.append(r)
    return rows


def build_dataset(rows: list[dict], n_negatives: int):
    """Column order is significant (see module docstring) - anchor,
    positive, then negative_1..negative_n, built in that literal order."""
    import datasets

    cols: dict[str, list[str]] = {
        "anchor": [r["query"] for r in rows],
        "positive": [r["positive"] for r in rows],
    }
    for i in range(n_negatives):
        cols[f"negative_{i + 1}"] = [r["neg"][i] for r in rows]
    return datasets.Dataset.from_dict(cols)


def check_trainable_ratio(trainable: int, total: int, target_modules: list[str],
                          r: int, max_fraction: float = 0.1) -> None:
    """Pure guard, factored out of apply_lora so it's testable without a
    real model load. Catches two distinct failure modes: (a) trainable=0 -
    target_modules matched nothing in the model's architecture (a classic
    PEFT footgun - it fails silently, not with an error, unless checked);
    (b) trainable params are a large fraction of the full model - a
    LoraConfig that accidentally targets far more than intended stops being
    "LoRA" (parameter-efficient) and becomes a full fine-tune in disguise,
    with none of the overfitting protection that was the point of using
    LoRA over full FT here (see module docstring)."""
    if trainable == 0:
        raise RuntimeError(
            f"LoRA applied but zero trainable parameters - target_modules "
            f"{target_modules} matched nothing in this model's architecture")
    if trainable > total * max_fraction:
        raise RuntimeError(
            f"LoRA trainable params ({trainable:,}) are >{100 * max_fraction:.0f}% "
            f"of the full model ({total:,}) - target_modules {target_modules} is "
            f"probably too broad for a rank-{r} adapter to be genuinely "
            f"parameter-efficient")


def apply_lora(model, r: int = LORA_R, alpha: int = LORA_ALPHA,
               dropout: float = LORA_DROPOUT,
               target_modules: list[str] = LORA_TARGET_MODULES) -> None:
    """Mutates `model` in place; see check_trainable_ratio for the
    validation this applies after add_adapter."""
    from peft import LoraConfig, TaskType

    total = sum(p.numel() for p in model.parameters())
    model.add_adapter(LoraConfig(
        r=r, lora_alpha=alpha, lora_dropout=dropout,
        target_modules=target_modules, bias="none",
        task_type=TaskType.FEATURE_EXTRACTION,
    ))
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    check_trainable_ratio(trainable, total, target_modules, r)
    print(f"trainable params: {trainable:,} / {total:,} "
          f"({100 * trainable / total:.2f}%)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="+", default=[str(p) for p in DEFAULT_PAIRS],
                    help="one or more pairs JSONL files (Phase 1 will pass "
                         "both structural and synthesized pair files here)")
    ap.add_argument("--base-model", default=DEFAULT_BASE_MODEL)
    ap.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    ap.add_argument("--epochs", type=float, default=1.0,
                    help="1-2 per the plan; NOT 3 - NVIDIA's recipe notes 3 "
                         "is calibrated for toy datasets, not real corpora")
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--lr", type=float, default=LEARNING_RATE)
    ap.add_argument("--n-negatives", type=int, default=N_NEGATIVES)
    ap.add_argument("--device", default=None, help="None = auto-detect (mps else cpu)")
    ap.add_argument("--gradient-checkpointing", action="store_true", default=True)
    ap.add_argument("--no-gradient-checkpointing", dest="gradient_checkpointing",
                    action="store_false")
    args = ap.parse_args()

    import datasets  # noqa: F401 - import-order guard: fail fast if missing,
                     # before the slow model load below
    from sebi_rag.device import pick_device
    from sentence_transformers import (
        SentenceTransformer,
        SentenceTransformerTrainer,
        SentenceTransformerTrainingArguments,
    )
    from sentence_transformers.losses import MultipleNegativesRankingLoss

    device = pick_device(args.device)
    print(f"device: {device}")

    rows = load_pairs([Path(p) for p in args.pairs], args.n_negatives)
    if not rows:
        raise SystemExit(f"no pairs with >= {args.n_negatives} negatives found "
                         f"in {args.pairs}")
    print(f"training pairs: {len(rows)}")
    ds = build_dataset(rows, args.n_negatives)

    model = SentenceTransformer(args.base_model, device=device)
    model.max_seq_length = QUERY_MAX_LEN  # single shared encoder for both
                                          # query and passage (bi-encoder
                                          # symmetric truncation); passage
                                          # side is also capped at 512 by
                                          # this same setting - bge-m3 uses
                                          # one tokenizer/model for both
    apply_lora(model)

    loss = MultipleNegativesRankingLoss(model, scale=MNRL_SCALE)
    training_args = SentenceTransformerTrainingArguments(
        output_dir=str(Path(args.output_dir) / "trainer_state"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        learning_rate=args.lr,
        gradient_checkpointing=args.gradient_checkpointing,
        report_to="none",  # the string sentinel HF Trainer actually
                           # defaults to - an earlier version of this script
                           # passed [] (empty list) here, which is not the
                           # same value and left the first Phase 0 training
                           # run with zero {'loss': ...} lines through 277
                           # steps despite logging_steps=50; harmless to
                           # training itself (verified via the downstream
                           # retrieval eval, not loss-curve inspection), but
                           # a real loss-visibility gap worth not repeating
        logging_steps=50,
        logging_first_step=True,  # a log line at step 1, not just step 50 -
                                  # confirms the loss path is actually wired
                                  # before waiting through the first interval
        disable_tqdm=True,  # the tqdm progress bar's \r-based rendering is
                            # unhelpful once stdout is redirected to a log
                            # file (as every run in this pipeline is) - one
                            # line per logging_steps is more legible there
        save_strategy="no",  # we save the adapter ourselves, once, at the end
    )
    trainer = SentenceTransformerTrainer(
        model=model, args=training_args, train_dataset=ds, loss=loss)
    train_result = trainer.train()
    print(f"final train metrics: {train_result.metrics}")

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(out))
    print(f"adapter saved -> {out}")


if __name__ == "__main__":
    main()
