"""Offline tests for the missing-PDF recovery logic (no network)."""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import acquire_missing_pdfs as M  # noqa: E402

STEM = "1705319176210"  # 2024-01-15 UTC
DETAIL = "https://www.sebi.gov.in/legal/circulars/jan-2024/x_1.html"
PDF = f"https://www.sebi.gov.in/sebi_data/attachdocs/jan-2024/{STEM}.pdf"
HTML = f"<iframe src='../../../web/?file={PDF}'>"


def test_month_window_pads_one_month_each_side():
    start, end = M.month_window(STEM)
    assert start == dt.date(2023, 12, 1)
    assert end == dt.date(2024, 2, 29)   # leap year


def test_stem_of_strips_path_and_extension():
    assert M.stem_of(PDF) == STEM


def test_resolve_stems_matches_by_stem():
    def fake_discover(section, max_count, rate, date_from=None, date_to=None):
        assert date_from == dt.date(2023, 12, 1) and date_to == dt.date(2024, 2, 29)
        return [DETAIL]

    resolved = M.resolve_stems([STEM], rate=0.0, discover_fn=fake_discover,
                               fetch_fn=lambda u, r: HTML.encode())
    assert resolved == {STEM: (PDF, DETAIL)}


def test_resolve_stems_reports_nothing_for_unmatched():
    resolved = M.resolve_stems([STEM], rate=0.0,
                               discover_fn=lambda *a, **k: [DETAIL],
                               fetch_fn=lambda u, r: b"<p>no pdf here</p>")
    assert resolved == {}


def test_resolve_stems_survives_detail_fetch_error():
    def bad_fetch(u, r):
        raise RuntimeError("HTTP Error 530: BLOCKED")

    resolved = M.resolve_stems([STEM], rate=0.0,
                               discover_fn=lambda *a, **k: [DETAIL],
                               fetch_fn=bad_fetch)
    assert resolved == {}
