"""The eval canary must fit its timeout and alert on real regressions.

Measured 2026-08-12 on this machine, stub generator, golden_v7 (n=260):

    runtime            840s   (NOT the ~40s the docs claimed)
    recall_at_10       0.943
    ndcg_at_10         0.697
    citation_recall    0.783
    citation_precision 0.224
    abstention_accuracy 0.962
    injection_flagged  10

The old ~40s figure predates two changes: the reporting set moving from
golden_v5 (n=56) to golden_v7 (n=260), and B' running a cross-encoder over
every row. Neither is the generator, so pinning the stub alone does not
restore it - the timeout is what has to move.

golden_v5 would fit the old budget (183s) but carries the pre-2026-07-30
abstain labels, so it reports abstention 0.804 and would alert forever.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANARY = ROOT / "scripts" / "canary.sh"
OPS = ROOT / "scripts" / "ops_server.py"
N8N = ROOT / "automation" / "n8n" / "3_eval_canary.json"

# Measured baselines above; thresholds must sit below these or the canary
# alerts on a healthy system.
BASELINE = {
    "recall_at_10": 0.943,
    "ndcg_at_10": 0.697,
    "citation_recall": 0.783,
    "citation_precision": 0.224,
    "abstention_accuracy": 0.962,
}
MEASURED_RUNTIME_S = 840


def _ops_timeout() -> int:
    m = re.search(r'run_script\("canary\.sh",\s*(\d+)\)', OPS.read_text(encoding="utf-8"))
    assert m, "canary invocation in ops_server.py changed shape"
    return int(m.group(1))


def _canary_jscode() -> str:
    wf = json.loads(N8N.read_text(encoding="utf-8"))
    for node in wf["nodes"]:
        code = node.get("parameters", {}).get("jsCode")
        if code and "canary" in code.lower():
            return code
    raise AssertionError("no canary threshold node found in the n8n workflow")


def test_canary_pins_the_stub_generator():
    src = CANARY.read_text(encoding="utf-8")
    assert re.search(r"SEBI_RAG_EVAL_GENERATOR=stub", src), (
        "canary.sh does not pin the stub; MLX would take ~20 min")


def test_ops_timeout_fits_the_measured_runtime():
    budget = _ops_timeout()
    assert budget >= MEASURED_RUNTIME_S * 1.25, (
        f"ops budget {budget}s cannot fit a {MEASURED_RUNTIME_S}s run")


def test_n8n_timeout_not_tighter_than_the_ops_budget():
    """n8n gives up first if its budget is smaller, so the ops timeout is
    never reached and the failure looks like a network error."""
    wf = json.loads(N8N.read_text(encoding="utf-8"))
    timeouts = [n["parameters"]["options"]["timeout"]
                for n in wf["nodes"]
                if n.get("parameters", {}).get("options", {}).get("timeout")]
    assert timeouts, "no HTTP timeout found in the canary workflow"
    assert min(timeouts) >= _ops_timeout() * 1000, (
        f"n8n timeout {min(timeouts)}ms < ops budget {_ops_timeout()}s")


def test_alert_thresholds_sit_below_measured_baselines():
    """A threshold above the healthy value fires every run. citation_precision
    was 0.35 against a measured 0.224 - it would have alerted daily."""
    code = _canary_jscode()
    for metric, observed in BASELINE.items():
        m = re.search(rf"m\.{metric}\s*<\s*([0-9.]+)", code)
        assert m, f"{metric} is not checked by the canary"
        threshold = float(m.group(1))
        assert threshold < observed, (
            f"{metric} threshold {threshold} >= measured {observed}: alerts when healthy")
