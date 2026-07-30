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

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
