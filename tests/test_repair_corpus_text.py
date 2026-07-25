"""The repair map must name a real orphan PDF that parses to the
circular_number it claims to repair (2026-07-25 remediation Task 2)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from repair_corpus_text import REPAIRS  # noqa: E402
from sebi_rag.ingest_pdf import normalize_circular_number  # noqa: E402


def test_repair_map_covers_the_six_known_records():
    assert set(REPAIRS) == {
        "DOF3/P/CIR/2022/39", "DOF3/P/CIR/2022/49", "DOF3/P/CIR/2022/82",
        "DOF1/P/CIR/2022/105", "DOF2/P/CIR/2022/161", "PoD-1/P/CIR/2024/163",
    }


def test_every_mapped_pdf_exists_on_disk():
    for num, pdf in REPAIRS.items():
        assert (ROOT / "data" / "raw" / pdf).exists(), f"{num} -> {pdf} missing"


def test_mapped_pdfs_are_distinct():
    assert len(set(REPAIRS.values())) == len(REPAIRS)


def test_numbers_normalize_distinctly():
    keys = {normalize_circular_number(n) for n in REPAIRS}
    assert len(keys) == len(REPAIRS)
