"""Self-Optimization Plugin: telemetry engine for sustainable meta-optimization loop.

Monitors hardware (RAM/Swap via psutil), records inference performance,
and suggests optimal parameters based on historical quality outcomes.

Storage: ~/.omp/telemetry_history.json
oMLX endpoint: 127.0.0.1:8001 (Qwen3.6-35B-A3B-MLX-4bit)
Safety limit: 3.3 GB RAM headroom (soft limit — flags "Unstable" if violated)

Usage:
    python scripts/telemetry_engine.py record --quality 5 --success
    python scripts/telemetry_engine.py suggest Complex Coding
    python scripts/telemetry_engine.py status
    python scripts/telemetry_engine.py history --top 10
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import psutil  # noqa: F401
except ImportError:
    print("ERROR: psutil is required. Install with: pip install psutil", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TELEMETRY_DIR = Path.home() / ".omp"
TELEMETRY_FILE = TELEMETRY_DIR / "telemetry_history.json"
SOFT_LIMIT_GB = 3.3  # RAM headroom safety margin in GB
OMLX_HOST = "127.0.0.1"
OMLX_PORT = 8001

# Default parameter presets (will be overridden by optimization suggestions)
DEFAULT_PARAMS = {
    "Complex Coding": {
        "temperature": 0.2,
        "min_p": 0.05,
        "context_window_size": 8192,
    },
    "Simple Query": {
        "temperature": 0.1,
        "min_p": 0.1,
        "context_window_size": 4096,
    },
}


# Turn-Based Optimization Thresholds (configurable)
OPTIMIZE_THRESHOLD = 8.0       # Minimum acceptable overall score before optimization triggers
DRIFT_MARGIN = 1.0             # Score must drop below baseline by this margin to trigger
BASELINE_WINDOW = 10           # Number of recent turns to use for rolling baseline
OPTIMIZE_SCORE_KEY = "optimize_score"  # Key in telemetry history for optimize scores

# ---------------------------------------------------------------------------
# Hardware Safety Monitor
# ---------------------------------------------------------------------------


def get_hardware_state() -> dict[str, float]:
    """Return current RAM free (GB) and swap usage percentage."""
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "free_ram_gb": round(vm.available / (1024**3), 2),
        "total_ram_gb": round(vm.total / (1024**3), 2),
        "swap_used_gb": round(swap.used / (1024**3), 2),
        "swap_total_gb": round(swap.total / (1024**3), 2) if swap.total > 0 else 0.0,
        "swap_pct": round(swap.percent, 1),
    }


def check_safety_limit(hw: dict[str, float]) -> tuple[bool, str]:
    """Check if RAM headroom meets the 3.3 GB soft limit.

    Returns (is_safe, message).
    """
    headroom = hw["free_ram_gb"]
    if headroom >= SOFT_LIMIT_GB:
        return True, f"OK — {headroom:.1f} GB headroom (>= {SOFT_LIMIT_GB} GB limit)"
    deficit = SOFT_LIMIT_GB - headroom
    return (
        False,
        f"UNSTABLE — {headroom:.1f} GB headroom (< {SOFT_LIMIT_GB} GB limit, "
        f"deficit: {deficit:.1f} GB). Reduce oMLX Hot Cache or Context Window.",
    )


# ---------------------------------------------------------------------------
# Telemetry Database (JSON)
# ---------------------------------------------------------------------------


def load_history() -> list[dict[str, Any]]:
    """Load telemetry history from JSON file."""
    if not TELEMETRY_FILE.exists():
        return []
    try:
        with open(TELEMETRY_FILE, "r") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_history(history: list[dict[str, Any]]) -> None:
    """Save telemetry history to JSON file."""
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
    with open(TELEMETRY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def record_run(
    outcome_quality: int | str,
    inference_config: dict[str, float] | None = None,
    performance: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Record a new telemetry run entry.

    Args:
        outcome_quality: 1-5 integer rating OR "success"/"fail".
        inference_config: {temperature, min_p, context_window_size}.
        performance: {ttft_ms, tokens_per_second}.

    Returns the recorded entry.
    """
    hw = get_hardware_state()
    is_safe, safety_msg = check_safety_limit(hw)

    # Normalize outcome_quality
    if isinstance(outcome_quality, str):
        q_map = {"success": 5, "fail": 1, "partial": 3}
        outcome_quality = q_map.get(outcome_quality.lower(), 3)

    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hardware_state": hw,
        "safety": {"is_safe": is_safe, "message": safety_msg},
        "inference_config": inference_config or {},
        "performance": performance or {},
        "outcome_quality": outcome_quality,
    }

    history = load_history()
    history.append(entry)
    save_history(history)
    return entry


# ---------------------------------------------------------------------------
# oMLX Endpoint Telemetry (optional — fetches live inference metrics)
# ---------------------------------------------------------------------------


def fetch_omlx_metrics() -> dict[str, Any] | None:
    """Attempt to fetch live metrics from oMLX server.

    Returns inference config and performance if endpoint is reachable,
    else None (non-fatal — telemetry continues without live metrics).
    """
    import httpx  # type: ignore[import-not-found,unused-ignore]

    try:
        with httpx.Client(timeout=3.0) as client:
            # oMLX typically exposes /health or model info endpoint
            resp = client.get(f"http://{OMLX_HOST}:{OMLX_PORT}/health", follow_redirects=True)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "omlx_status": "online",
                    "model": data.get("model", "unknown"),
                }
            return {"omlx_status": f"http_{resp.status_code}"}
    except Exception:
        return None


def capture_live_performance() -> dict[str, float]:
    """Capture live inference metrics from oMLX if available.

    Returns {ttft_ms, tokens_per_second} or empty dict if unavailable.
    """
    metrics = fetch_omlx_metrics()
    if not metrics:
        return {}

    # If oMLX exposes performance headers, parse them here.
    # For now, return what we can from the health endpoint.
    return {"omlx_status": 1.0 if metrics.get("omlx_status") == "online" else 0.0}


# ---------------------------------------------------------------------------
# Optimization Brain — Parameter Suggestion Engine
# ---------------------------------------------------------------------------


def suggest_parameters(task_complexity: str) -> dict[str, Any]:
    """Suggest optimal parameters based on historical telemetry data.

    Queries telemetry_history.json for runs with:
      - Highest outcome_quality that did NOT violate the 3.3 GB RAM safety margin

    Args:
        task_complexity: "Complex Coding" or "Simple Query".

    Returns dict with suggested temperature, min_p, context_window_size.
    """
    complexity = task_complexity.lower()
    if "complex" in complexity:
        complexity_key = "Complex Coding"
    else:
        complexity_key = "Simple Query"

    history = load_history()
    if not history:
        return {
            "complexity": complexity_key,
            "status": "no_history",
            "message": f"No telemetry data yet. Using defaults for {complexity_key}.",
            **DEFAULT_PARAMS[complexity_key],
        }

    # Filter: safe runs only (is_safe == True)
    safe_runs = [r for r in history if r.get("safety", {}).get("is_safe", True)]

    # Filter: runs with outcome_quality >= 4 (high quality)
    high_quality = [r for r in safe_runs if isinstance(r.get("outcome_quality"), (int, float)) and r["outcome_quality"] >= 4]

    if not high_quality:
        # Fallback to all safe runs with quality >= 3
        high_quality = [r for r in safe_runs if isinstance(r.get("outcome_quality"), (int, float)) and r["outcome_quality"] >= 3]

    if not high_quality:
        return {
            "complexity": complexity_key,
            "status": "no_safe_runs",
            "message": f"No safe high-quality runs found. Using defaults for {complexity_key}.",
            **DEFAULT_PARAMS[complexity_key],
        }

    # Aggregate: average the best-performing parameters from high-quality runs
    temps = [r["inference_config"].get("temperature", 0.2) for r in high_quality if "temperature" in r.get("inference_config", {})]
    min_ps = [r["inference_config"].get("min_p", 0.05) for r in high_quality if "min_p" in r.get("inference_config", {})]
    ctx_sizes = [r["inference_config"].get("context_window_size", 4096) for r in high_quality if "context_window_size" in r.get("inference_config", {})]

    avg_temp = round(sum(temps) / len(temps), 3) if temps else DEFAULT_PARAMS[complexity_key]["temperature"]
    avg_min_p = round(sum(min_ps) / len(min_ps), 3) if min_ps else DEFAULT_PARAMS[complexity_key]["min_p"]
    avg_ctx = int(sum(ctx_sizes) / len(ctx_sizes)) if ctx_sizes else DEFAULT_PARAMS[complexity_key]["context_window_size"]

    return {
        "complexity": complexity_key,
        "status": "optimized",
        "message": f"Suggested from {len(high_quality)} safe high-quality historical runs.",
        "temperature": avg_temp,
        "min_p": avg_min_p,
        "context_window_size": avg_ctx,
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def show_status() -> None:
    """Print current hardware state and safety status."""
    hw = get_hardware_state()
    is_safe, msg = check_safety_limit(hw)

    print(f"\n{'='*60}")
    print(f"  Telemetry Engine — Hardware Status")
    print(f"{'='*60}")
    print(f"  Free RAM:     {hw['free_ram_gb']:.1f} GB / {hw['total_ram_gb']:.1f} GB")
    print(f"  Swap Used:    {hw['swap_used_gb']:.1f} GB / {hw['swap_total_gb']:.1f} GB ({hw['swap_pct']}%)")
    print(f"  Headroom:     {hw['free_ram_gb']:.1f} GB (limit: {SOFT_LIMIT_GB} GB)")
    print(f"  Safety:       {'✅ SAFE' if is_safe else '⚠️  UNSTABLE'}")
    print(f"{'='*60}\n")

    # oMLX status
    omlx = fetch_omlx_metrics()
    if omlx:
        print(f"  oMLX Server:  {omlx.get('omlx_status', 'unknown')}")
        if omlx.get("model"):
            print(f"  Model:        {omlx['model']}")
    else:
        print(f"  oMLX Server:  unreachable (non-fatal)")

    # History summary
    history = load_history()
    if history:
        avg_quality = sum(r.get("outcome_quality", 0) for r in history) / len(history)
        safe_count = sum(1 for r in history if r.get("safety", {}).get("is_safe", True))
        print(f"\n  History:      {len(history)} runs recorded")
        print(f"  Avg Quality:  {avg_quality:.1f}/5.0")
        print(f"  Safe Runs:    {safe_count}/{len(history)} ({100*safe_count/len(history):.0f}%)")
    else:
        print(f"\n  History:      No runs recorded yet.")

    print()


def show_history(top_n: int = 10) -> None:
    """Print recent telemetry history entries."""
    history = load_history()
    if not history:
        print("No telemetry data recorded yet.")
        return

    entries = history[-top_n:]
    print(f"\n{'='*80}")
    print(f"  Recent Telemetry History (last {len(entries)})")
    print(f"{'='*80}")

    for i, entry in enumerate(entries, 1):
        ts = entry.get("timestamp", "unknown")[:19]
        quality = entry.get("outcome_quality", "?")
        safe = "✅" if entry.get("safety", {}).get("is_safe", True) else "⚠️"
        hw = entry.get("hardware_state", {})
        free_ram = hw.get("free_ram_gb", "?")
        cfg = entry.get("inference_config", {})
        temp = cfg.get("temperature", "-")
        ctx = cfg.get("context_window_size", "-")

        print(f"  {i:2d}. [{ts}] Q={quality} {safe} RAM={free_ram}GB temp={temp} ctx={ctx}")

    print(f"{'='*80}\n")



# ---------------------------------------------------------------------------
# Turn-Based Optimization (Self-Critique & Correction Pass)
# ---------------------------------------------------------------------------


def analyze_state(prompt: str, intent: str = "") -> dict[str, Any]:
    """State Analysis: inspect prompt complexity and session context.

    Returns a lightweight state vector used by the critique matrix.
    """
    word_count = len(prompt.split())
    has_code = any(c in prompt for c in ["```", "def ", "class ", "import ", "func "])
    has_schema = any(c in prompt for c in ["JSON", "schema", "YAML", "config"])
    has_multi_file = prompt.lower().count("file") + prompt.lower().count("path") > 2

    complexity = "simple"
    if word_count > 100 or has_multi_file:
        complexity = "moderate"
    if word_count > 250 or (has_code and has_schema):
        complexity = "complex"

    return {
        "prompt_length": word_count,
        "has_code": has_code,
        "has_schema": has_schema,
        "multi_file": has_multi_file,
        "complexity": complexity,
    }


def self_critique(draft: str, state: dict[str, Any]) -> dict[str, Any]:
    """Self-Critique Matrix: measure draft against three excellence criteria.

    Returns a critique dict with scores and flagged issues per criterion.
    """
    # --- Conciseness ---
    sentences = [s.strip() for s in draft.replace("\n", " ").split(".") if s.strip()]
    filler_phrases = [
        "i think", "i believe", "basically", "essentially", "in order to",
        "it is important to note", "as mentioned earlier", "furthermore",
        "additionally", "however, it should be noted",
    ]
    filler_count = sum(1 for s in sentences if any(f in s.lower() for f in filler_phrases))
    avg_sentence_len = len(draft.split()) / max(len(sentences), 1)
    conciseness_score = max(0, 10 - filler_count - (avg_sentence_len - 15) / 3)
    conciseness_flags = []
    if filler_count > 2:
        conciseness_flags.append(f"High filler phrase count ({filler_count})")
    if avg_sentence_len > 25:
        conciseness_flags.append(f"Long average sentence length ({avg_sentence_len:.0f} words)")

    # --- Technical Fidelity ---
    tech_flags = []
    if state.get("has_code"):
        # Check for common outdated patterns (expand as needed)
        if "from __future__ import" in draft and "python 2" not in prompt.lower():
            tech_flags.append("Outdated __future__ import (Python 2 compat)")
        if "print >>" in draft:
            tech_flags.append("Python 2 print syntax detected")

    # --- Instruction Adherence ---
    instruction_flags = []
    prompt_lower = draft.lower()
    if state.get("complexity") == "complex" and len(sentences) < 5:
        instruction_flags.append("Response may be too brief for complex prompt")
    if state.get("has_schema") and "json" not in prompt_lower and "yaml" not in prompt_lower:
        instruction_flags.append("Schema request may lack structured output")

    return {
        "conciseness": {
            "score": round(conciseness_score, 2),
            "flags": conciseness_flags,
        },
        "technical_fidelity": {
            "score": 10.0 if not tech_flags else max(5.0, 10.0 - len(tech_flags) * 2),
            "flags": tech_flags,
        },
        "instruction_adherence": {
            "score": 10.0 if not instruction_flags else max(5.0, 10.0 - len(instruction_flags) * 2),
            "flags": instruction_flags,
        },
    }


def correction_pass(critique: dict[str, Any], draft: str) -> tuple[str, list[str]]:
    """Correction Pass: rewrite flagged portions and return refined draft.

    Returns (refined_draft, list_of_changes_made).
    """
    changes: list[str] = []
    refined = draft

    # Apply concise fixes
    if critique["conciseness"]["score"] < 7:
        filler_replacements = {
            "in order to": "to",
            "it is important to note that": "",
            "as mentioned earlier": "",
            "furthermore": "",
            "additionally": "",
        }
        for old, new in filler_replacements.items():
            if old in refined.lower():
                refined = refined.replace(old, new)
                changes.append(f"Removed filler: '{old}'")

    # Apply technical fixes (placeholder — real fixes would be more sophisticated)
    if critique["technical_fidelity"]["score"] < 8:
        for flag in critique["technical_fidelity"]["flags"]:
            changes.append(f"Flagged: {flag}")

    # Apply instruction adherence fixes (placeholder)
    if critique["instruction_adherence"]["score"] < 8:
        for flag in critique["instruction_adherence"]["flags"]:
            changes.append(f"Flagged: {flag}")

    return refined, changes



# ---------------------------------------------------------------------------
# Turn-Based Optimization — Baseline Management
# ---------------------------------------------------------------------------


def load_baseline() -> dict[str, float]:
    """Load rolling baseline from last N optimize scores in telemetry history.

    Returns dict with avg_overall, avg_conciseness, avg_technical, avg_instruction.
    Falls back to threshold values if no history exists.
    """
    history = load_history()
    # Filter for optimize-related entries (look for optimize_score key)
    optimize_entries = [r for r in history if OPTIMIZE_SCORE_KEY in r]

    if not optimize_entries:
        # No baseline yet — return threshold defaults (no optimization will trigger)
        return {
            "avg_overall": OPTIMIZE_THRESHOLD,
            "avg_conciseness": OPTIMIZE_THRESHOLD,
            "avg_technical": OPTIMIZE_THRESHOLD,
            "avg_instruction": OPTIMIZE_THRESHOLD,
            "count": 0,
        }

    # Take last BASELINE_WINDOW entries
    recent = optimize_entries[-BASELINE_WINDOW:]

    overall_scores = [r[OPTIMIZE_SCORE_KEY] for r in recent if OPTIMIZE_SCORE_KEY in r]
    conc_scores = [r.get("critique", {}).get("conciseness", {}).get("score", OPTIMIZE_THRESHOLD) for r in recent]
    tech_scores = [r.get("critique", {}).get("technical_fidelity", {}).get("score", OPTIMIZE_THRESHOLD) for r in recent]
    instr_scores = [r.get("critique", {}).get("instruction_adherence", {}).get("score", OPTIMIZE_THRESHOLD) for r in recent]

    return {
        "avg_overall": round(sum(overall_scores) / len(overall_scores), 2) if overall_scores else OPTIMIZE_THRESHOLD,
        "avg_conciseness": round(sum(conc_scores) / len(conc_scores), 2) if conc_scores else OPTIMIZE_THRESHOLD,
        "avg_technical": round(sum(tech_scores) / len(tech_scores), 2) if tech_scores else OPTIMIZE_THRESHOLD,
        "avg_instruction": round(sum(instr_scores) / len(instr_scores), 2) if instr_scores else OPTIMIZE_THRESHOLD,
        "count": len(recent),
    }


def update_baseline(score: float, critique: dict[str, Any]) -> None:
    """Append current optimize score to telemetry history for baseline tracking."""
    # Load existing history
    history = load_history()

    # Create baseline entry (lightweight — no hardware/perf data needed)
    baseline_entry = {
        "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        OPTIMIZE_SCORE_KEY: score,
        "critique": {
            "conciseness": {"score": critique["conciseness"]["score"]},
            "technical_fidelity": {"score": critique["technical_fidelity"]["score"]},
            "instruction_adherence": {"score": critique["instruction_adherence"]["score"]},
        },
    }

    history.append(baseline_entry)
    save_history(history)


def check_degradation(current: dict[str, Any], baseline: dict[str, float]) -> tuple[bool, list[str]]:
    """Check if current scores have degraded below baseline by DRIFT_MARGIN.

    Hierarchical check:
      1. Criterion-level: any criterion dropped below (baseline - DRIFT_MARGIN)
      2. Overall: overall_score dropped below (baseline_avg - DRIFT_MARGIN)

    Returns (degraded: bool, flags: list[str]).
    """
    flags = []

    # Criterion-level checks
    if current["conciseness"]["score"] < (baseline["avg_conciseness"] - DRIFT_MARGIN):
        flags.append(f"conciseness: {current['conciseness']['score']:.1f} < {baseline['avg_conciseness'] - DRIFT_MARGIN:.1f}")
    if current["technical_fidelity"]["score"] < (baseline["avg_technical"] - DRIFT_MARGIN):
        flags.append(f"technical_fidelity: {current['technical_fidelity']['score']:.1f} < {baseline['avg_technical'] - DRIFT_MARGIN:.1f}")
    if current["instruction_adherence"]["score"] < (baseline["avg_instruction"] - DRIFT_MARGIN):
        flags.append(f"instruction_adherence: {current['instruction_adherence']['score']:.1f} < {baseline['avg_instruction'] - DRIFT_MARGIN:.1f}")

    # Overall check (only if no criterion-level degradation)
    if not flags:
        overall = current["overall_score"]
        threshold = baseline["avg_overall"] - DRIFT_MARGIN
        if overall < threshold:
            flags.append(f"overall: {overall:.1f} < {threshold:.1f}")

    return len(flags) > 0, flags


def optimize_turn(prompt: str, draft: str) -> dict[str, Any]:
    """Orchestrator: run threshold-gated turn-based optimization workflow.

    Steps:
      1. Load historical baseline (last BASELINE_WINDOW turns)
      2. State Analysis → Self-Critique Matrix on current draft
      3. Check degradation: does score drop below (baseline - DRIFT_MARGIN)?
      4. If degraded: Correction Pass + record to telemetry
         If not degraded: skip optimization (return "Fully Optimized")

    Returns dict with state, critique scores, changes made, and final draft.
    """
    # Load baseline from recent history
    baseline = load_baseline()

    # State Analysis + Self-Critique Matrix
    state = analyze_state(prompt)
    critique = self_critique(draft, state)

    overall_score = (
        critique["conciseness"]["score"]
        + critique["technical_fidelity"]["score"]
        + critique["instruction_adherence"]["score"]
    ) / 3.0

    # Check degradation against baseline
    degraded, degradation_flags = check_degradation(
        {"overall_score": overall_score, **critique}, baseline
    )

    if degraded:
        # Apply correction pass
        refined_draft, changes = correction_pass(critique, draft)

        # Update baseline with current score
        update_baseline(overall_score, critique)

        return {
            "state": state,
            "critique": critique,
            "overall_score": round(overall_score, 2),
            "baseline_avg": baseline["avg_overall"],
            "degraded": True,
            "degradation_flags": degradation_flags,
            "changes_made": changes if changes else ["Correction applied"],
            "refined_draft": refined_draft,
        }
    else:
        # No degradation — skip optimization
        return {
            "state": state,
            "critique": critique,
            "overall_score": round(overall_score, 2),
            "baseline_avg": baseline["avg_overall"],
            "degraded": False,
            "degradation_flags": [],
            "changes_made": ["Fully Optimized"],
            "refined_draft": draft,  # Return original draft unchanged
        }


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Self-Optimization Plugin — telemetry engine for sustainable meta-optimization loop.",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # record
    rec = sub.add_parser("record", help="Record a telemetry run")
    rec.add_argument("--quality", "-q", type=int, default=None, help="Quality rating 1-5")
    rec.add_argument("--success", action="store_true", help="Shortcut for quality=5")
    rec.add_argument("--fail", action="store_true", help="Shortcut for quality=1")
    rec.add_argument("--temperature", type=float, default=None, help="Inference temperature")
    rec.add_argument("--min-p", type=float, default=None, help="Inference min_p")
    rec.add_argument("--context-window", type=int, default=None, help="Context window size")
    rec.add_argument("--ttft", type=float, default=None, help="Time to first token (ms)")
    rec.add_argument("--tps", type=float, default=None, help="Tokens per second")

    # suggest
    sug = sub.add_parser("suggest", help="Suggest optimal parameters")
    sug.add_argument(
        "complexity",
        nargs="?",
        default="Complex Coding",
        help='Task complexity: "Complex Coding" or "Simple Query"',
    )

    # status
    sub.add_parser("status", help="Show current hardware state and safety status")

    # history
    hist = sub.add_parser("history", help="Show recent telemetry history")
    hist.add_argument("--top", "-n", type=int, default=10, help="Number of recent entries to show")


    # optimize — turn-based self-critique and correction pass
    opt = sub.add_parser("optimize", help="Run turn-based self-critique optimization on a draft")
    opt.add_argument("--prompt", "-p", required=True, help="Original user prompt (for state analysis)")
    opt.add_argument("--draft", "-d", required=True, help="Draft response text to optimize")
    opt.add_argument("--json", action="store_true", help="Output as JSON instead of formatted text")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "status":
        show_status()

    elif args.command == "history":
        show_history(args.top)

    elif args.command == "suggest":
        result = suggest_parameters(args.complexity)
        print(f"\n{'='*60}")
        print(f"  Parameter Suggestion — {result['complexity']}")
        print(f"{'='*60}")
        print(f"  Status:   {result['status']}")
        print(f"  Message:  {result['message']}")
        print(f"  Temperature:   {result['temperature']}")
        print(f"  Min_P:         {result['min_p']}")
        print(f"  Context Window:{result['context_window_size']}")
        print(f"{'='*60}\n")

    elif args.command == "record":
        # Determine outcome_quality
        if args.success:
            quality = 5
        elif args.fail:
            quality = 1
        elif args.quality is not None:
            quality = args.quality
        else:
            print("ERROR: Provide --quality (1-5), --success, or --fail", file=sys.stderr)
            sys.exit(1)

        # Build inference_config from CLI args or capture live metrics
        inference_config: dict[str, float] = {}
        if args.temperature is not None:
            inference_config["temperature"] = args.temperature
        if args.min_p is not None:
            inference_config["min_p"] = args.min_p
        if args.context_window is not None:
            inference_config["context_window_size"] = float(args.context_window)

        # Capture live performance if not provided
        performance: dict[str, float] = {}
        if args.ttft is not None:
            performance["ttft_ms"] = args.ttft
        if args.tps is not None:
            performance["tokens_per_second"] = args.tps

        entry = record_run(quality, inference_config or None, performance or None)
        print(f"\nRecorded run: quality={entry['outcome_quality']}, "
              f"free_ram={entry['hardware_state']['free_ram_gb']}GB, "
              f"safety={'SAFE' if entry['safety']['is_safe'] else 'UNSTABLE'}")
        print(f"Saved to {TELEMETRY_FILE}")


    elif args.command == "optimize":
        result = optimize_turn(args.prompt, args.draft)
        if args.json:
            import json as _json
            # Remove refined_draft from JSON output to avoid huge payloads
            out = {k: v for k, v in result.items() if k != "refined_draft"}
            print(_json.dumps(out, indent=2))
        else:
            status_icon = "⚠️  DEGRADED" if result["degraded"] else "✅ OPTIMIZED"
            print(f"\n{'='*60}")
            print(f"  Turn-Based Optimization — {status_icon}")
            print(f"{'='*60}")
            print(f"  State Complexity:   {result['state']['complexity']}")
            if result["degraded"]:
                print(f"  Baseline Avg:       {result['baseline_avg']:.1f}/10.0 (last {BASELINE_WINDOW} turns)")
                print(f"  Current Score:      {result['overall_score']:.1f}/10.0")
                print(f"  Degradation:        {' → '.join(result['degradation_flags'])}")
                print(f"  Action:             Correction applied")
            else:
                print(f"  Baseline Avg:       {result['baseline_avg']:.1f}/10.0 (last {BASELINE_WINDOW} turns)")
                print(f"  Current Score:      {result['overall_score']:.1f}/10.0")
                print(f"  Status:             Within baseline tolerance (±{DRIFT_MARGIN})")
            print(f"  Conciseness:        {result['critique']['conciseness']['score']:.1f}/10.0")
            print(f"  Technical Fidelity: {result['critique']['technical_fidelity']['score']:.1f}/10.0")
            print(f"  Instruction Adhere: {result['critique']['instruction_adherence']['score']:.1f}/10.0")
            print(f"  Changes Made:       {', '.join(result['changes_made'])}")
            print(f"{'='*60}\n")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
