"""The eval canary must stay LLM-free.

`ops_server.py` runs canary.sh under a hard 300s timeout and the n8n workflow
sets the same 5-minute budget. `eval_json.py` now defaults to the MLX generator
(config.toml eval_generator="mlx") so the gate matches production, which takes
~20 minutes over 260 rows - six times the canary's budget.

The canary is a fast regression tripwire, not the gate. It pins the stub
explicitly so a change to the shared default cannot silently blow the timeout.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANARY = ROOT / "scripts" / "canary.sh"
OPS = ROOT / "scripts" / "ops_server.py"


def test_canary_pins_the_stub_generator():
    src = CANARY.read_text(encoding="utf-8")
    assert re.search(r"SEBI_RAG_EVAL_GENERATOR=stub", src), (
        "canary.sh does not pin the stub; it inherits eval_generator=mlx and "
        "will exceed the 300s ops timeout")


def test_canary_budget_still_matches_the_ops_timeout():
    """If someone raises the canary to a slow generator, this is the second
    tripwire: the ops server's timeout is the real constraint."""
    ops = OPS.read_text(encoding="utf-8")
    m = re.search(r'run_script\("canary\.sh",\s*(\d+)\)', ops)
    assert m, "canary invocation in ops_server.py changed shape"
    budget = int(m.group(1))
    canary = CANARY.read_text(encoding="utf-8")
    if "SEBI_RAG_EVAL_GENERATOR=stub" not in canary:
        assert budget >= 1800, (
            f"canary runs a non-stub generator under a {budget}s timeout")
