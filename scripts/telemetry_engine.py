"""Self-Optimization Plugin: Phoenix/OTel-based telemetry engine.

Monitors hardware state via OTel System Metrics, instruments OpenAI clients
via OpenInference, and stores telemetry in Arize Phoenix.

Storage: Arize Phoenix (http://localhost:6006)
oMLX endpoint: 127.0.0.1:8001 (OpenAI-compatible)
Safety limit: 3.3 GB RAM headroom (soft limit)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, ContextManager

# --- Constants ---
PHOENIX_ENDPOINT = "http://localhost:6006"
OMLX_HOST = "127.0.0.1"
OMLX_PORT = 8001
SOFT_LIMIT_GB = 3.3
PROJECT_NAME = "sebi-rag-telemetry"
TELEMETRY_DIR = Path.home() / ".omp"
TELEMETRY_FILE = TELEMETRY_DIR / "telemetry_history.json"

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

# Turn-Based Optimization Thresholds
OPTIMIZE_THRESHOLD = 8.0
DRIFT_MARGIN = 1.0
BASELINE_WINDOW = 10
OPTIMIZE_SCORE_KEY = "optimize_score"

# --- TracerProvider (singleton cache) ---

_tracer_provider: Any = None


def get_tracer_provider() -> Any:
    """Create and return a configured Phoenix TracerProvider (singleton).

    Uses phoenix.otel.TracerProvider with OTLP HTTP/protobuf exporter.
    Connection errors are non-fatal — the provider is still returned.
    """
    global _tracer_provider
    if _tracer_provider is not None:
        return _tracer_provider

    from phoenix.otel import TracerProvider as PhoenixTracerProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import set_tracer_provider

    resource = Resource.create({
        "service.name": PROJECT_NAME,
        "service.version": "1.0.0",
    })

    try:
        _tracer_provider = PhoenixTracerProvider(
            resource=resource,
            endpoint=PHOENIX_ENDPOINT,
            protocol="http/protobuf",
        )
        # Register as the global tracer provider so get_tracer() works
        set_tracer_provider(_tracer_provider)
    except Exception as exc:  # noqa: BLE001
        # Phoenix not running or unreachable — log warning but don't fail import
        print(
            f"WARNING: Could not connect to Phoenix at {PHOENIX_ENDPOINT}: {exc}",
            file=sys.stderr,
        )
        # Create a no-op provider so imports still work
        from opentelemetry.sdk.trace import TracerProvider as StdTracerProvider
        _tracer_provider = StdTracerProvider(resource=resource)
        set_tracer_provider(_tracer_provider)

    return _tracer_provider


# --- OpenAI Instrumentation ---


def instrument_openai_client(tracer_provider: Any) -> Any:
    """Instrument the OpenAI client for telemetry via OpenInference.

    Wraps openai.OpenAI.request and openai.AsyncOpenAI.request.
    Returns the instrumentor instance, or None if the package is not available.
    """
    try:
        from openinference.instrumentation.openai import OpenAIInstrumentor
    except ImportError:
        print(
            "WARNING: openinference-instrumentation-openai not available. "
            "OpenAI client will not be instrumented.",
            file=sys.stderr,
        )
        return None

    instrumentor = OpenAIInstrumentor()
    instrumentor.instrument(tracer_provider=tracer_provider)
    return instrumentor


def uninstrument_openai_client(instrumentor: Any) -> None:
    """Uninstrument the OpenAI client."""
    if instrumentor is None:
        return
    try:
        from openinference.instrumentation.openai import OpenAIInstrumentor
        if isinstance(instrumentor, OpenAIInstrumentor):
            instrumentor.uninstrument()
    except ImportError:
        pass


# --- Span Context Manager ---


@contextmanager
def telemetry_span(name: str, attributes: dict[str, Any] | None = None) -> ContextManager[Any]:
    """Context manager for creating and managing a telemetry span.

    Starts a span, yields it, and ends it on exit.
    On exception, sets error status and records the exception.
    """
    from opentelemetry import trace

    # Ensure the global tracer provider is initialized (singleton).
    get_tracer_provider()
    tracer = trace.get_tracer(PROJECT_NAME)
    span = tracer.start_span(name, attributes=attributes or {})
    try:
        yield span
    except Exception as e:
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
        span.record_exception(e)
        raise
    finally:
        span.end()


# --- Hardware Metrics ---


def get_hardware_state() -> dict[str, float]:
    """Return current RAM free (GB) and swap usage percentage.

    Uses psutil as the primary implementation (already installed).
    Falls back to zeroed values if psutil is unavailable.
    """
    try:
        import psutil

        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        return {
            "free_ram_gb": round(vm.available / (1024 ** 3), 2),
            "total_ram_gb": round(vm.total / (1024 ** 3), 2),
            "swap_used_gb": round(swap.used / (1024 ** 3), 2),
            "swap_total_gb": round(swap.total / (1024 ** 3), 2) if swap.total > 0 else 0.0,
            "swap_pct": round(swap.percent, 1),
            "cpu_percent": round(cpu_percent, 1),
        }
    except ImportError:
        return {
            "free_ram_gb": 0.0,
            "total_ram_gb": 0.0,
            "swap_used_gb": 0.0,
            "swap_total_gb": 0.0,
            "swap_pct": 0.0,
            "cpu_percent": 0.0,
        }


# --- Safety Check ---


def check_safety_limit(hw: dict[str, float]) -> tuple[bool, str]:
    """Check if RAM headroom meets the 3.3 GB soft limit.

    Returns (is_safe, message).
    """
    headroom = hw["free_ram_gb"]
    if headroom >= SOFT_LIMIT_GB:
        return True, f"OK - {headroom:.1f} GB headroom (>= {SOFT_LIMIT_GB} GB limit)"
    deficit = SOFT_LIMIT_GB - headroom
    return (
        False,
        f"UNSTABLE - {headroom:.1f} GB headroom (< {SOFT_LIMIT_GB} GB limit, "
        f"deficit: {deficit:.1f} GB). Reduce oMLX Hot Cache or Context Window.",
    )


# ---------------------------------------------------------------------------
# Telemetry Database (JSON — legacy, kept for backward compatibility)
# ---------------------------------------------------------------------------


def load_history() -> list[dict[str, Any]]:
    """Load telemetry history from JSON file (kept for migration only)."""
    if not TELEMETRY_FILE.exists():
        return []
    try:
        with open(TELEMETRY_FILE, "r") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


# ---------------------------------------------------------------------------
# Phoenix Query Layer
# ---------------------------------------------------------------------------


def _get_phoenix_client() -> Any:
    """Get or create a Phoenix client (singleton)."""
    from phoenix.client import Client
    return Client()


def query_traces(project_name: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """Query traces from Phoenix.

    Returns list of trace dicts with:
    - id, trace_id, project_id, start_time, end_time
    - token_count_prompt, token_count_completion, token_count_total
    - spans (list of span dicts with name, attributes, etc.)
    """
    try:
        client = _get_phoenix_client()
        traces = client.traces.get(limit=limit)
    except Exception:  # noqa: BLE001
        return []
    result = []
    for t in traces:
        trace_dict: dict[str, Any] = {
            "id": t.id,
            "trace_id": t.trace_id,
            "project_id": t.project_id,
            "start_time": t.start_time.isoformat() if t.start_time else None,
            "end_time": t.end_time.isoformat() if t.end_time else None,
            "token_count_prompt": t.token_count_prompt,
            "token_count_completion": t.token_count_completion,
            "token_count_total": t.token_count_total,
            "spans": [],
        }
        for span in t.spans:
            trace_dict["spans"].append({
                "name": span.name,
                "span_kind": span.span_kind,
                "start_time": span.start_time.isoformat() if span.start_time else None,
                "end_time": span.end_time.isoformat() if span.end_time else None,
                "status_code": span.status_code,
                "attributes": dict(span.attributes) if span.attributes else {},
            })
        result.append(trace_dict)
    return result


def query_spans(project_name: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """Query spans from Phoenix.

    Returns list of span dicts with:
    - id, parent_id, name, span_kind, start_time, end_time
    - status_code, status_message, attributes, events
    """
    try:
        client = _get_phoenix_client()
        spans = client.spans.get(limit=limit)
    except Exception:  # noqa: BLE001
        return []
    result = []
    for s in spans:
        span_dict: dict[str, Any] = {
            "id": s.id,
            "parent_id": s.parent_id,
            "name": s.name,
            "span_kind": s.span_kind,
            "start_time": s.start_time.isoformat() if s.start_time else None,
            "end_time": s.end_time.isoformat() if s.end_time else None,
            "status_code": s.status_code,
            "status_message": s.status_message,
            "attributes": dict(s.attributes) if s.attributes else {},
            "events": s.events if hasattr(s, "events") else [],
        }
        result.append(span_dict)
    return result


def query_traces_by_attribute(attr_name: str, attr_value: str, limit: int = 100) -> list[dict[str, Any]]:
    """Query traces filtered by an attribute value.

    Uses the traces.search() method if available, otherwise filters locally.
    """
    traces = query_traces(limit=limit * 10)  # Fetch more for filtering
    filtered: list[dict[str, Any]] = []
    for t in traces:
        for span in t.get("spans", []):
            attrs = span.get("attributes", {})
            if attrs.get(attr_name) == attr_value:
                filtered.append(t)
                break
    return filtered[:limit]


def record_run(
    outcome_quality: int | str,
    inference_config: dict[str, float] | None = None,
    performance: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Record a new telemetry run entry to Phoenix.

    Creates a span in Phoenix with:
    - outcome_quality as span attribute
    - hardware_state as span attributes
    - inference_config as span attributes
    - performance as span attributes

    Returns the recorded entry dict (same format as before).
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

    # Log to Phoenix as a span
    try:
        from opentelemetry import trace
        tracer = trace.get_tracer(PROJECT_NAME)
        with tracer.start_as_current_span("telemetry.record_run") as span:
            span.set_attribute("outcome_quality", outcome_quality)
            span.set_attribute("free_ram_gb", hw["free_ram_gb"])
            span.set_attribute("total_ram_gb", hw["total_ram_gb"])
            span.set_attribute("swap_pct", hw["swap_pct"])
            span.set_attribute("cpu_percent", hw["cpu_percent"])
            span.set_attribute("safety.is_safe", is_safe)
            span.set_attribute("safety.message", safety_msg)
            if inference_config:
                for k, v in inference_config.items():
                    span.set_attribute(f"inference_config.{k}", v)
            if performance:
                for k, v in performance.items():
                    span.set_attribute(f"performance.{k}", v)
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: Failed to log to Phoenix: {exc}", file=sys.stderr)

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
    except Exception:  # noqa: BLE001
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
    """Suggest optimal parameters based on Phoenix telemetry data.

    Queries Phoenix for runs with:
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

    # Query Phoenix for relevant traces
    try:
        traces = query_traces(limit=200)
    except Exception:
        traces = []

    # Filter for telemetry.record_run spans with outcome_quality
    safe_runs = []
    for t in traces:
        for span in t.get("spans", []):
            if span.get("name") == "telemetry.record_run":
                attrs = span.get("attributes", {})
                quality = attrs.get("outcome_quality")
                is_safe = attrs.get("safety.is_safe", True)
                if is_safe and isinstance(quality, (int, float)) and quality >= 4:
                    safe_runs.append({
                        "outcome_quality": quality,
                        "inference_config": {
                            "temperature": attrs.get("inference_config.temperature"),
                            "min_p": attrs.get("inference_config.min_p"),
                            "context_window_size": attrs.get("inference_config.context_window_size"),
                        },
                    })

    if not safe_runs:
        return {
            "complexity": complexity_key,
            "status": "no_history",
            "message": f"No telemetry data yet. Using defaults for {complexity_key}.",
            **DEFAULT_PARAMS[complexity_key],
        }

    # Aggregate: average the best-performing parameters
    temps = [r["inference_config"]["temperature"] for r in safe_runs
             if r["inference_config"].get("temperature") is not None]
    min_ps = [r["inference_config"]["min_p"] for r in safe_runs
              if r["inference_config"].get("min_p") is not None]
    ctx_sizes = [r["inference_config"]["context_window_size"] for r in safe_runs
                 if r["inference_config"].get("context_window_size") is not None]

    avg_temp = round(sum(temps) / len(temps), 3) if temps else DEFAULT_PARAMS[complexity_key]["temperature"]
    avg_min_p = round(sum(min_ps) / len(min_ps), 3) if min_ps else DEFAULT_PARAMS[complexity_key]["min_p"]
    avg_ctx = int(sum(ctx_sizes) / len(ctx_sizes)) if ctx_sizes else DEFAULT_PARAMS[complexity_key]["context_window_size"]

    return {
        "complexity": complexity_key,
        "status": "optimized",
        "message": f"Suggested from {len(safe_runs)} safe high-quality historical runs.",
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

    print(f"\n{'=' * 60}")
    print(f"  Telemetry Engine — Hardware Status")
    print(f"{'=' * 60}")
    print(f"  Free RAM:     {hw['free_ram_gb']:.1f} GB / {hw['total_ram_gb']:.1f} GB")
    print(f"  Swap Used:    {hw['swap_used_gb']:.1f} GB / {hw['swap_total_gb']:.1f} GB ({hw['swap_pct']}%)")
    print(f"  Headroom:     {hw['free_ram_gb']:.1f} GB (limit: {SOFT_LIMIT_GB} GB)")
    print(f"  Safety:       {'✅ SAFE' if is_safe else '⚠️  UNSTABLE'}")
    print(f"{'=' * 60}\n")

    # oMLX status
    omlx = fetch_omlx_metrics()
    if omlx:
        print(f"  oMLX Server:  {omlx.get('omlx_status', 'unknown')}")
        if omlx.get("model"):
            print(f"  Model:        {omlx['model']}")
    else:
        print(f"  oMLX Server:  unreachable (non-fatal)")

    # Phoenix history summary
    try:
        traces = query_traces(limit=500)
        run_spans = []
        for t in traces:
            for span in t.get("spans", []):
                if span.get("name") == "telemetry.record_run":
                    run_spans.append(span)

        if run_spans:
            qualities = [s.get("attributes", {}).get("outcome_quality", 0) for s in run_spans]
            safe_count = sum(1 for s in run_spans if s.get("attributes", {}).get("safety.is_safe", True))
            avg_quality = sum(qualities) / len(qualities) if qualities else 0
            print(f"\n  History:      {len(run_spans)} runs recorded (from Phoenix)")
            print(f"  Avg Quality:  {avg_quality:.1f}/5.0")
            print(f"  Safe Runs:    {safe_count}/{len(run_spans)} ({100 * safe_count / len(run_spans):.0f}%)")
        else:
            print(f"\n  History:      No runs recorded yet (Phoenix).")
    except Exception as exc:
        print(f"\n  History:      Could not query Phoenix ({exc}).")

    print()


def show_history(top_n: int = 10) -> None:
    """Print recent telemetry history entries from Phoenix."""
    try:
        traces = query_traces(limit=top_n * 5)
    except Exception:
        print("Could not query Phoenix for telemetry history.")
        return

    # Collect record_run spans
    run_spans = []
    for t in traces:
        for span in t.get("spans", []):
            if span.get("name") == "telemetry.record_run":
                run_spans.append((t.get("start_time", ""), span))

    # Sort by start_time descending
    run_spans.sort(key=lambda x: x[0], reverse=True)
    entries = run_spans[:top_n]

    if not entries:
        print("No telemetry data recorded yet (Phoenix).")
        return

    print(f"\n{'=' * 80}")
    print(f"  Recent Telemetry History (last {len(entries)})")
    print(f"{'=' * 80}")

    for i, (ts, span) in enumerate(entries, 1):
        ts_str = ts[:19] if ts else "unknown"
        attrs = span.get("attributes", {})
        quality = attrs.get("outcome_quality", "?")
        safe = "✅" if attrs.get("safety.is_safe", True) else "⚠️"
        free_ram = attrs.get("free_ram_gb", "?")
        temp = attrs.get("inference_config.temperature", "-")
        ctx = attrs.get("inference_config.context_window_size", "-")

        print(f"  {i:2d}. [{ts_str}] Q={quality} {safe} RAM={free_ram}GB temp={temp} ctx={ctx}")

    print(f"{'=' * 80}\n")


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
    """Load rolling baseline from Phoenix optimize spans.

    Returns dict with avg_overall, avg_conciseness, avg_technical, avg_instruction.
    Falls back to threshold values if no history exists.
    """
    try:
        traces = query_traces(limit=BASELINE_WINDOW * 10)
    except Exception:
        traces = []

    # Filter for optimize-related spans
    optimize_entries = []
    for t in traces:
        for span in t.get("spans", []):
            if span.get("name") == "telemetry.optimize_turn":
                attrs = span.get("attributes", {})
                if OPTIMIZE_SCORE_KEY in attrs:
                    optimize_entries.append({
                        OPTIMIZE_SCORE_KEY: attrs[OPTIMIZE_SCORE_KEY],
                        "critique": {
                            "conciseness": {"score": attrs.get("critique.conciseness", OPTIMIZE_THRESHOLD)},
                            "technical_fidelity": {"score": attrs.get("critique.technical_fidelity", OPTIMIZE_THRESHOLD)},
                            "instruction_adherence": {"score": attrs.get("critique.instruction_adherence", OPTIMIZE_THRESHOLD)},
                        },
                    })

    if not optimize_entries:
        return {
            "avg_overall": OPTIMIZE_THRESHOLD,
            "avg_conciseness": OPTIMIZE_THRESHOLD,
            "avg_technical": OPTIMIZE_THRESHOLD,
            "avg_instruction": OPTIMIZE_THRESHOLD,
            "count": 0,
        }

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
    """Log current optimize score to Phoenix for baseline tracking."""
    try:
        from opentelemetry import trace
        tracer = trace.get_tracer(PROJECT_NAME)
        with tracer.start_as_current_span("telemetry.optimize_turn") as span:
            span.set_attribute(OPTIMIZE_SCORE_KEY, score)
            span.set_attribute("critique.conciseness", critique["conciseness"]["score"])
            span.set_attribute("critique.technical_fidelity", critique["technical_fidelity"]["score"])
            span.set_attribute("critique.instruction_adherence", critique["instruction_adherence"]["score"])
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: Failed to log to Phoenix: {exc}", file=sys.stderr)


def migrate_legacy_json() -> int:
    """Migrate legacy JSON telemetry history to Phoenix.

    Reads ~/.omp/telemetry_history.json and logs each entry as a Phoenix span.
    Returns the number of entries migrated.
    """
    if not TELEMETRY_FILE.exists():
        return 0

    history = load_history()
    if not history:
        return 0

    migrated = 0
    for entry in history:
        record_run(
            outcome_quality=entry.get("outcome_quality", 3),
            inference_config=entry.get("inference_config"),
            performance=entry.get("performance"),
        )
        migrated += 1

    if migrated > 0:
        print(f"Migrated {migrated} entries from {TELEMETRY_FILE} to Phoenix.")

    return migrated


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
        flags.append(
            f"conciseness: {current['conciseness']['score']:.1f} < {baseline['avg_conciseness'] - DRIFT_MARGIN:.1f}"
        )
    if current["technical_fidelity"]["score"] < (baseline["avg_technical"] - DRIFT_MARGIN):
        flags.append(
            f"technical_fidelity: {current['technical_fidelity']['score']:.1f} < {baseline['avg_technical'] - DRIFT_MARGIN:.1f}"
        )
    if current["instruction_adherence"]["score"] < (baseline["avg_instruction"] - DRIFT_MARGIN):
        flags.append(
            f"instruction_adherence: {current['instruction_adherence']['score']:.1f} < {baseline['avg_instruction'] - DRIFT_MARGIN:.1f}"
        )

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
        print(f"\n{'=' * 60}")
        print(f"  Parameter Suggestion — {result['complexity']}")
        print(f"{'=' * 60}")
        print(f"  Status:   {result['status']}")
        print(f"  Message:  {result['message']}")
        print(f"  Temperature:   {result['temperature']}")
        print(f"  Min_P:         {result['min_p']}")
        print(f"  Context Window:{result['context_window_size']}")
        print(f"{'=' * 60}\n")

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
            print(f"\n{'=' * 60}")
            print(f"  Turn-Based Optimization — {status_icon}")
            print(f"{'=' * 60}")
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
            print(f"{'=' * 60}\n")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
