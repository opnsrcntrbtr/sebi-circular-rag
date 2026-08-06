"""Epoch and frame identity for comparable measurement.

The corpus drifts on a weekly n8n refresh, so it needs a controlled identity:
an *epoch* is a corpus snapshot keyed by corpus_sha256. An *eval set* is a
golden file keyed by golden_sha256. A *frame* is the pair, and two runs are
comparable if and only if they share one.

Epoch is keyed on the corpus alone: `golden`, `probes` and `asof` are separate
instruments applied to the same corpus, not separate corpora.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

EPOCH_REGISTRY = "eval/epochs/epochs.jsonl"


class IncomparableFramesError(RuntimeError):
    """Raised when a paired comparison spans two frames."""


@dataclass(frozen=True)
class Frame:
    epoch: str
    eval_set: str

    def __str__(self) -> str:  # pragma: no cover - formatting only
        return f"{self.epoch}/{self.eval_set[:8]}"


def frame_of(results: dict, epoch_by_corpus: dict[str, str]) -> Frame | None:
    """Derive a run's frame from its results.json payload.

    Returns None when the run predates fingerprinting or its corpus is not in
    the registry — such runs are excluded from comparisons rather than guessed.
    """
    meta = results.get("metadata") or {}
    corpus = meta.get("corpus_sha256")
    golden = meta.get("golden_sha256")
    if not corpus or not golden:
        return None
    epoch = epoch_by_corpus.get(corpus[:8]) or epoch_by_corpus.get(corpus)
    if not epoch:
        return None
    return Frame(epoch=epoch, eval_set=golden[:8])


def assert_comparable(
    a: Frame | None,
    b: Frame | None,
    *,
    label_a: str,
    label_b: str,
) -> None:
    """Raise unless both runs sit in the same frame."""
    if a is None or b is None:
        missing = label_a if a is None else label_b
        raise IncomparableFramesError(
            f"cannot compare {label_a} with {label_b}: {missing} has no frame"
        )
    if a.epoch != b.epoch:
        raise IncomparableFramesError(
            f"cannot compare {label_a} (epoch {a.epoch}) with "
            f"{label_b} (epoch {b.epoch}): different corpora"
        )
    if a.eval_set != b.eval_set:
        raise IncomparableFramesError(
            f"cannot compare {label_a} (eval set {a.eval_set}) with "
            f"{label_b} (eval set {b.eval_set}): different golden files"
        )


def assign_epochs(runs: list[tuple[str, dict]]) -> dict[str, str]:
    """Number corpora E1..En by earliest observed run timestamp.

    Deterministic and order-independent, so re-running the backfill never
    renumbers an existing epoch.
    """
    first_seen: dict[str, str] = {}
    for _name, results in runs:
        meta = results.get("metadata") or {}
        corpus = meta.get("corpus_sha256")
        ts = meta.get("ts")
        if not corpus or not ts:
            continue
        key = corpus[:8]
        if key not in first_seen or ts < first_seen[key]:
            first_seen[key] = ts
    ordered = sorted(first_seen.items(), key=lambda kv: (kv[1], kv[0]))
    return {corpus: f"E{i}" for i, (corpus, _ts) in enumerate(ordered, start=1)}


def load_epoch_registry(path: str | Path) -> dict[str, str]:
    """Read `eval/epochs/epochs.jsonl` into `{corpus_sha256[:8]: epoch}`."""
    p = Path(path)
    if not p.exists():
        return {}
    out: dict[str, str] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        out[rec["corpus_sha256"][:8]] = rec["epoch"]
    return out
