#!/usr/bin/env python3
"""Pre-commit validator for golden_v7 gate.

Checks:
1. gate_v7.json exists and is valid JSON with adjudicated_n >= 100
2. Golden set file (golden_v7.jsonl) exists and is parseable
3. All entries have required fields
4. Floors in gate_v7.json are non-empty and reasonable

Exit 0 = all checks pass, exit 1 = any check fails.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
GATE_PATH = PROJECT_ROOT / "eval" / "golden" / "gate_v7.json"
GOLDEN_PATH = PROJECT_ROOT / "eval" / "golden" / "golden_v7.jsonl"

MIN_ADJUDICATED_N = 100
REQUIRED_FIELDS = {
    "id", "query", "relevant_circulars", "relevant_chunks",
    "abstain", "task_type", "difficulty",
}


def check_gate() -> list[str]:
    errors = []
    if not GATE_PATH.exists():
        return [f"FAIL: {GATE_PATH} does not exist — v5 fallback active"]

    try:
        gate = json.loads(GATE_PATH.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return [f"FAIL: {GATE_PATH} is corrupt: {e}"]

    n = gate.get("adjudicated_n")
    if not isinstance(n, int) or n < MIN_ADJUDICATED_N:
        errors.append(
            f"FAIL: adjudicated_n={n} < {MIN_ADJUDICATED_N} — gate not armed"
        )

    floors = gate.get("floors", {})
    if not floors:
        errors.append("FAIL: 'floors' key missing or empty in gate_v7.json")

    return errors


def check_golden_set() -> list[str]:
    errors = []
    if not GOLDEN_PATH.exists():
        return [f"FAIL: {GOLDEN_PATH} does not exist"]

    try:
        entries = [json.loads(line) for line in GOLDEN_PATH.read_text().splitlines() if line.strip()]
    except json.JSONDecodeError as e:
        return [f"FAIL: {GOLDEN_PATH} contains invalid JSON: {e}"]

    missing_fields = set()
    for i, entry in enumerate(entries):
        for field in REQUIRED_FIELDS:
            if field not in entry:
                missing_fields.add(f"{field} (line {i + 1})")

    if missing_fields:
        errors.append(f"FAIL: Missing required fields: {sorted(missing_fields)[:10]}")

    return errors


def main() -> int:
    errors = []
    errors.extend(check_gate())
    errors.extend(check_golden_set())

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        print(f"\nVALIDATE_GOLDEN status=FAIL errors={len(errors)}", flush=True)
        return 1

    print("VALIDATE_GOLDEN status=PASS", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
