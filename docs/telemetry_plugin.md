# Self-Optimization Plugin — Usage Reference

> On-demand reference. Not injected per turn. Read when working with hardware-aware parameter optimization.
> Last updated: 2026-07-30

## Architecture Overview

```
┌──────────────┐    ┌───────────────────┐    ┌─────────────────┐
│  Hardware     │───▶│  Safety Monitor    │───▶│ Quality Memory  │
│  (M4 48GB)   │    │  psutil RAM/Swap   │    │ ~/.omp/         │
│              │◄───│  3.3GB soft limit  │◄───│ telemetry_      │
└──────────────┘    └───────────────────┘    │ history.json    │
                                              └────────┬────────┘
                                                       │
                                              ┌───────▼────────┐
                                              │  Optimization  │
                                              │     Brain      │
                                              └───────┬────────┘
                                                       │
                                              ┌───────▼────────┐
                                              │   oMLX Server  │
                                              │ :8001          │
                                              └────────────────┘
```

**Goal:** Sustainable meta-optimization loop between hardware constraints, inference parameters, and coding output quality.

## Components

### 1. Hardware-Aware Safety Monitor (The "Red Line")

Monitors system RAM and Swap via `psutil`. Enforces a **3.3 GB headroom soft limit**.

**Logic:**
```python
headroom = free_ram_gb  # from psutil.virtual_memory().available
if headroom >= 3.3:
    status = "SAFE"
else:
    status = "UNSTABLE"  # deficit = 3.3 - headroom
```

**Actions on violation:**
- Flags the run as `UNSTABLE` in telemetry history
- Recommends reducing oMLX Hot Cache or Context Window for next run
- Records the violation but **excludes** from optimization suggestions (only safe runs inform parameter tuning)

**Why 3.3 GB?**
- M4 Pro has 48 GB unified memory
- oMLX (Qwen3.6-35B-A3B-MLX-4bit) typically uses 18-22 GB during inference
- OS + background processes use ~5-8 GB
- 3.3 GB headroom prevents swap thrashing and OOM kills during complex coding sessions

### 2. Persistent Quality Memory (JSON Database)

**Location:** `~/.omp/telemetry_history.json`
**Schema:** Per-run JSON object with hardware state, inference config, performance metrics, and outcome quality.

```json
{
  "timestamp": "2026-07-30T12:25:21.000Z",
  "hardware_state": {
    "free_ram_gb": 11.26,
    "total_ram_gb": 48.0,
    "swap_used_gb": 9.79,
    "swap_total_gb": 11.0,
    "swap_pct": 89.0
  },
  "safety": {
    "is_safe": true,
    "message": "OK — 11.3 GB headroom (>= 3.3 GB limit)"
  },
  "inference_config": {
    "temperature": 0.2,
    "min_p": 0.05,
    "context_window_size": 8192.0
  },
  "performance": {
    "ttft_ms": 120.5,
    "tokens_per_second": 45.2
  },
  "outcome_quality": 5
}
```

**Field semantics:**
| Field | Type | Description |
|---|---|---|
| `timestamp` | ISO 8601 UTC | When the run was recorded |
| `hardware_state.free_ram_gb` | float | Available RAM at recording time |
| `hardware_state.swap_pct` | float | Swap usage percentage (0-100) |
| `safety.is_safe` | bool | True if headroom >= 3.3 GB |
| `inference_config.temperature` | float | Model temperature (0.0-1.0) |
| `inference_config.min_p` | float | Min-p sampling parameter (0.0-1.0) |
| `inference_config.context_window_size` | float | Context window in tokens |
| `performance.ttft_ms` | float | Time to first token in milliseconds |
| `performance.tokens_per_second` | float | Generation throughput |
| `outcome_quality` | int (1-5) or string | User-rated quality: 1=fail, 2=poor, 3=partial, 4=good, 5=excellent |

**Lifecycle:**
- File created on first `record` command
- Appended to (never overwritten) — grows as a time-series log
- No automatic cleanup — manual rotation recommended after ~100 entries

### 3. The Optimization Brain (Parameter Suggestion Engine)

**Algorithm:** `suggest_parameters(task_complexity)`

```
Input:  task_complexity ("Complex Coding" or "Simple Query")
Output: {temperature, min_p, context_window_size}

Steps:
1. Load ~/.omp/telemetry_history.json
2. Filter runs where safety.is_safe == True  (exclude unstable runs)
3. Filter runs where outcome_quality >= 4    (high quality only)
   → Fallback: if no results, use outcome_quality >= 3 (good or better)
4. Aggregate: compute mean of temperature, min_p, context_window_size
   from filtered runs that have inference_config populated
5. Return averaged parameters + metadata (count of supporting runs)

Edge cases:
- No history → return DEFAULT_PARAMS for the complexity level
- No safe runs → return DEFAULT_PARAMS with status="no_safe_runs"
- No quality >= 4 runs → fallback to quality >= 3
```

**Default parameters (used when no history exists):**

| Complexity | Temperature | Min_P | Context Window |
|---|---|---|---|
| Complex Coding | 0.2 | 0.05 | 8192 |
| Simple Query | 0.1 | 0.1 | 4096 |

**Why these defaults?**
- Complex Coding: lower temperature (0.2) for deterministic code generation, wider context (8192) for multi-file reasoning
- Simple Query: slightly higher temperature (0.1) for flexibility, narrower context (4096) to conserve RAM

## CLI Usage

### Commands

| Command | Description |
|---|---|
| `python scripts/telemetry_engine.py status` | Hardware state, safety margin, oMLX connectivity |
| `python scripts/telemetry_engine.py record --quality N` | Record outcome (1-5 scale) |
| `python scripts/telemetry_engine.py record --success` | Shortcut for quality=5 |
| `python scripts/telemetry_engine.py record --fail` | Shortcut for quality=1 |
| `python scripts/telemetry_engine.py suggest "Complex Coding"` | Get optimized parameters from history |
| `python scripts/telemetry_engine.py suggest "Simple Query"` | Get optimized parameters for simple tasks |
| `python scripts/telemetry_engine.py history --top N` | Show last N telemetry entries |

### Full record command with all options

```bash
python scripts/telemetry_engine.py record \
  --quality 5 \
  --temperature 0.2 \
  --min-p 0.05 \
  --context-window 8192 \
  --ttft 120.5 \
  --tps 45.2
```

### Makefile shortcut

```bash
make telemetry record --quality 5
make telemetry suggest "Complex Coding"
make telemetry status
```

## Oh-My-Pi / Claude Code Integration

### Slash Commands (config.yml)

Add to your OMP/Claude Code config for slash-command access:

```yaml
slash_commands:
  optimize:
    description: "Run the telemetry engine"
    script: scripts/telemetry_engine.py

  optimize_success:
    description: "Record successful coding session"
    command: "python scripts/telemetry_engine.py record --success"

  optimize_fail:
    description: "Record failed coding session"
    command: "python scripts/telemetry_engine.py record --fail"

  optimize_suggest:
    description: "Get optimized parameters"
    command: "python scripts/telemetry_engine.py suggest {complexity}"

  optimize_status:
    description: "Show hardware status"
    command: "python scripts/telemetry_engine.py status"

  optimize_history:
    description: "Show telemetry history"
    command: "python scripts/telemetry_engine.py history --top {n}"
```

### Usage in Oh-My-Pi sessions

1. **Before complex coding:** `/optimize suggest "Complex Coding"` → get optimal params
2. **During session:** `/optimize status` → verify RAM headroom stays above 3.3 GB
3. **After session:** `/optimize_success` or `/optimize_quality 4` → log outcome
4. **Review trends:** `/optimize_history --top 20` → see parameter-quality correlation

### AGENTS.md Integration

The plugin is documented in `AGENTS.md` under "Self-Optimization Plugin (Telemetry Engine)". Agents reading AGENTS.md will encounter these rules when working with hardware-aware optimization tasks.

## AI Native Engineer Workflow

### Daily Routine

```
Morning:  /optimize status          → Check hardware state before starting
Session:  /optimize suggest "Complex Coding"  → Get params for complex task
          [code, test, iterate]     → Work with recommended parameters
End:      /optimize_success         → Log successful session (or --fail)

Weekly:   /optimize_history --top 30 → Review trends, identify patterns
          Adjust defaults if needed → Update DEFAULT_PARAMS in telemetry_engine.py
```

### Interpreting Results

**Good session indicators:**
- `safety.is_safe: true` — RAM headroom was sufficient
- `outcome_quality >= 4` — High quality output
- Low swap_pct (<50%) — No memory pressure

**Warning signs:**
- `safety.is_safe: false` — RAM headroom violated 3.3 GB limit
- High swap_pct (>80%) — System under memory pressure
- Declining outcome_quality over time → parameters may need adjustment

**Optimization feedback loop:**
```
Record high-quality safe runs → Brain averages best parameters → Suggest better params next time
                                                              ↓
                                              If new params cause instability, they're excluded from future averages
```

## Data Maintenance

### Rotation (manual)

After ~100 entries, consider rotating old data:
```bash
# Keep last 50 entries, archive the rest
python -c "
import json
from pathlib import Path
data = json.loads(Path.home() / '.omp/telemetry_history.json'.read_text())
recent = data[-50:]
old = data[:-50]
Path.home() / '.omp/telemetry_history.json'.write_text(json.dumps(recent, indent=2))
Path.home() / '.omp/telemetry_history_old.json'.write_text(json.dumps(old, indent=2))
print(f'Kept {len(recent)}, archived {len(old)}')
"
```

### Export for analysis

```bash
# Export to CSV for spreadsheet analysis
python -c "
import json, csv
from pathlib import Path
data = json.loads(Path.home() / '.omp/telemetry_history.json'.read_text())
with open('telemetry_export.csv', 'w') as f:
    w = csv.writer(f)
    w.writerow(['timestamp', 'free_ram_gb', 'swap_pct', 'is_safe', 'temperature', 'min_p', 'context_window', 'outcome_quality'])
    for r in data:
        hw = r['hardware_state']
        cfg = r.get('inference_config', {})
        w.writerow([
            r['timestamp'], hw['free_ram_gb'], hw['swap_pct'],
            r['safety']['is_safe'], cfg.get('temperature',''), cfg.get('min_p',''),
            cfg.get('context_window_size',''), r['outcome_quality']
        ])
"
```

## Error Handling

| Scenario | Behavior |
|---|---|
| `psutil` not installed | Exits with error: "pip install psutil" |
| `~/.omp/` doesn't exist | Auto-created on first `record` |
| `telemetry_history.json` corrupted | Returns empty list, continues without history |
| oMLX server unreachable | Non-fatal — telemetry continues without live metrics |
| No inference_config provided | Records with empty config, still usable for hardware tracking |

## Dependencies

- `psutil` — System monitoring (RAM, Swap)
- `httpx` — oMLX endpoint health check (optional, non-fatal if missing)
- Standard library: `json`, `argparse`, `datetime`, `pathlib`, `sys`

No external cloud APIs. All data stays local on the M4 Pro machine.

## Turn-Based Optimization (Auto-Run After Every Turn)

### Overview

A self-critique and correction pass that runs automatically at the conclusion of **every conversational turn**, before rendering final output to the user.

**Threshold-gated:** Only applies corrections when degradation is detected (score drops below baseline by DRIFT_MARGIN).

### Lifecycle Trigger

- **Execution Cadence:** Every turn, no explicit request needed
- **Interception Point:** After internal draft generation, before output stream rendering

### Threshold Configuration (configurable in telemetry_engine.py)

| Constant | Default | Description |
|---|---|---|
| `OPTIMIZE_THRESHOLD` | 8.0/10.0 | Minimum acceptable score when no baseline exists |
| `DRIFT_MARGIN` | 1.0 | Score must drop below baseline by this amount to trigger optimization |
| `BASELINE_WINDOW` | 10 | Number of recent turns for rolling baseline average |

**Trigger Logic:**
```python
if current_score < (baseline_avg - DRIFT_MARGIN):
    trigger_optimization()
```

Example: baseline_avg = 8.5, DRIFT_MARGIN = 1.0 → optimization triggers when score < 7.5

### Workflow (4 Hidden Steps)

```
┌──────────────┐    ┌───────────────────┐    ┌─────────────────────┐
│  State       │───▶│  Draft            │───▶│  Self-Critique      │
│  Analysis    │    │  Generation       │    │  Matrix (3 criteria)│
└──────────────┘    └───────────────────┘    └─────────┬───────────┘
                                                       │
                                              ┌──────▼──────────┐
                                              │  Degradation    │
                                              │  Check          │
                                              └──────┬──────────┘
                                                     │
                                    ┌────────────────┼────────────────┐
                          degraded?  Yes             │            No
                                    │                │               │
                              ┌─────▼──────┐         │        ┌────▼─────────┐
                              │ Correction │         │        │ Skip (return │
                              │  Pass      │         │        │ "Fully       │
                              └─────┬──────┘         │        │ Optimized")  │
                                    │                │        └──────────────┘
                              ┌─────▼──────┐         │
                              │ Record to  │         │
                              │ Telemetry  │         │
                              └────────────┘         │
                                                     │
                                              ┌────▼──────────┐
                                              │  Output       │
                                              │  Schema Block │
                                              └───────────────┘
```

### Step Details

**1. State Analysis (`analyze_state`)**
- Inspects prompt for complexity indicators: word count, code presence, schema requests, multi-file scope
- Classifies as `simple`, `moderate`, or `complex`

**2. Draft Generation (`generate_draft`)**
- Produces optimal structural candidate response (handled by the AI model itself)

**3. Self-Critique Matrix (`self_critique`)**
- Scores draft against three criteria (0-10 scale each):

| Criterion | What It Measures | Penalties |
|---|---|---|
| **Conciseness** | Filler phrases, sentence length | -1 per filler phrase, -0.33 per word over 15 avg sentence length |
| **Technical Fidelity** | Outdated patterns, syntax errors | -2 per flag (e.g., Python 2 print syntax) |
| **Instruction Adherence** | Response matches prompt requirements | -2 per flag (e.g., too brief for complex prompt) |

**4. Degradation Check (`check_degradation`)**
- Hierarchical check:
  1. Criterion-level: any criterion dropped below (baseline_avg - DRIFT_MARGIN)
  2. Overall: overall_score dropped below (baseline_avg - DRIFT_MARGIN)

**5. Correction Pass (`correction_pass`)**
- Only runs if degradation detected
- Rewrites flagged portions seamlessly
- Removes filler phrases ("in order to" → "to", etc.)
- Flags technical issues for manual review

**6. Baseline Update (`update_baseline`)**
- Appends current score to telemetry_history.json for future baseline calculations

### Output Schema

Rendered directly above the primary response:

**No degradation (skip optimization):**
```
[⚙️ Plugin Optimizations: Fully Optimized]

<original response>
```

**Degradation detected (apply correction):**
```
[⚙️ Plugin Optimizations: Degraded conciseness 5.9→7.2, corrected]

<corrected response>
```

### CLI Access (Manual Testing)

```bash
# Run optimization on a draft
python scripts/telemetry_engine.py optimize   --prompt "Write a Python function to calculate Fibonacci numbers"   --draft "I think this is a good approach. In order to calculate Fibonacci numbers, we can use recursion."

# JSON output for programmatic access
python scripts/telemetry_engine.py optimize   --prompt "..."   --draft "..."   --json

# JSON output shows degradation status and baseline info:
{
  "state": { "complexity": "simple" },
  "critique": { ... },
  "overall_score": 8.7,
  "baseline_avg": 9.2,
  "degraded": true,
  "degradation_flags": ["conciseness: 5.9 < 7.0"],
  "changes_made": ["Removed filler: 'in order to'"]
}
```

### Integration with Hardware Telemetry

The turn-based optimization runs **independently** of the hardware-aware telemetry:
- Hardware telemetry monitors RAM/Swap and suggests inference parameters (temperature, min_p)
- Turn-based optimization critiques output quality and refines the response text
- Both feed into the same `telemetry_history.json` when records are saved

### Design Rationale

**Why threshold-gated instead of always optimizing?**
- Avoids unnecessary rewrites when output quality is already good
- Reduces context window pollution from redundant corrections
- Focuses optimization effort where it's needed most

**Why historical baseline drift instead of fixed threshold?**
- Adapts to your quality level over time (no manual tuning needed)
- Detects relative degradation, not absolute scores
- A baseline of 9.0 with DRIFT_MARGIN=1.0 means optimize when < 8.0
- A baseline of 7.0 with DRIFT_MARGIN=1.0 means optimize when < 6.0

**Why hierarchical degradation detection?**
- Catches specific failure modes (e.g., conciseness drops while technical fidelity stays high)
- Provides actionable feedback ("conciseness dropped" vs just "overall score dropped")

**Why 10-turn lookback window?**
- Balances stability (not too noisy) with responsiveness (detects real degradation quickly)
- Configurable via BASELINE_WINDOW constant

**Why score 0-10 instead of pass/fail?**
- Granular scores enable trend analysis over time
- Allows gradual improvement tracking across sessions
- Enables A/B testing of different optimization strategies
**Why score 0-10 instead of pass/fail?**
- Granular scores enable trend analysis over time
- Allows gradual improvement tracking across sessions
- Enables A/B testing of different optimization strategies

