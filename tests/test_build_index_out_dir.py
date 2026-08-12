"""build_index must be able to target a scratch index directory.

The iv9/iv10 header arms need a headered index built *beside* the production
one. Without an output override the script overwrites `data/index` (1.0 GB)
in place, and the only way back is another full re-encode — with the
production stack left in the treatment state if anything fails midway.
"""
import re
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_index.py"


def test_build_index_exposes_an_output_dir_flag():
    src = SCRIPT.read_text(encoding="utf-8")
    assert '"--out"' in src, "no way to build an index outside data/index"


def test_build_index_saves_to_the_resolved_out_dir_not_the_constant():
    """A --out flag that is parsed but ignored is worse than none: it reads
    as safe and still clobbers the production index."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert not re.search(r"retriever\.save\(INDEX\)", src), (
        "saves to the hardcoded INDEX constant, ignoring --out")
    assert re.search(r"retriever\.save\(\s*OUT\s*\)", src), (
        "must save to the resolved output directory")


def test_lineage_follows_the_out_dir():
    """lineage.json lands next to the index it describes; writing it into
    data/index while the index goes elsewhere splits the artifact."""
    src = SCRIPT.read_text(encoding="utf-8")
    assert not re.search(r"save\(INDEX / \"lineage\.json\"\)", src)
    assert re.search(r"save\(OUT / \"lineage\.json\"\)", src)
