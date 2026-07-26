"""Which golden set gates CI, and whether its adjudicated subset clears the
derived floors (spec 2026-07-23 sec 8).

Kept as its own module with no heavy imports so both `eval_json.py` (which
boots the real models) and the offline test suite can use it. The flip is a
two-key lock: golden_v7 takes over only when `gate_v7.json` exists AND
reports adjudicated_n >= 100. Anything else - missing file, corrupt file,
short subset - keeps CI on frozen golden_v5, so a partially adjudicated v7
can never quietly become the set that gates merges.
"""
from __future__ import annotations

import json
from pathlib import Path

MIN_ADJUDICATED_N = 100


def select_golden(env: dict, gate_path: Path, v5: Path, v7: Path) -> Path:
    """Resolution order: explicit SEBI_RAG_GOLDEN override, then the armed
    v7 gate, then the frozen v5 fallback.

    A malformed gate file is treated exactly like a missing one. Failing
    closed to v5 matters more than surfacing the corruption here: CI must
    keep producing comparable numbers, and an exception thrown from the
    selector would take the whole eval run down.
    """
    override = env.get("SEBI_RAG_GOLDEN")
    if override:
        return Path(override)
    try:
        payload = json.loads(Path(gate_path).read_text(encoding="utf-8"))
        n = payload["adjudicated_n"]
    except (OSError, ValueError, KeyError, TypeError):
        return v5
    return v7 if isinstance(n, int) and n >= MIN_ADJUDICATED_N else v5


def floors_ok(report_gate: dict, floors: dict) -> bool:
    """True iff every floor's metric is present in `report_gate` and meets it.

    Missing metrics fail closed. A floor naming a metric the report does not
    carry cannot be shown to hold, and treating absence as success is the
    usual way a gate rots into always-green.
    """
    for metric, floor in floors.items():
        value = report_gate.get(metric)
        if value is None or value < floor:
            return False
    return True
