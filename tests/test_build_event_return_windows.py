from __future__ import annotations

from datetime import date

from semantic_ai_washing.analysis.build_event_return_windows import (
    choose_anchor_index,
    normalize_permno,
    summarize_window_coverage,
)


def test_normalize_permno_handles_integer_like_strings() -> None:
    assert normalize_permno("17137.0") == "17137"
    assert normalize_permno(" 84788 ") == "84788"
    assert normalize_permno(12558) == "12558"


def test_choose_anchor_index_uses_next_trading_day_when_needed() -> None:
    trade_dates = [date(2024, 2, 1), date(2024, 2, 2), date(2024, 2, 5)]
    assert choose_anchor_index(trade_dates, date(2024, 2, 1)) == 0
    assert choose_anchor_index(trade_dates, date(2024, 2, 3)) == 2
    assert choose_anchor_index(trade_dates, date(2024, 2, 6)) is None


def test_summarize_window_coverage_detects_complete_and_incomplete_windows() -> None:
    complete = summarize_window_coverage([-2, -1, 0, 1, 2], -2, 2)
    assert complete.is_complete is True
    assert complete.available_rows == 5
    assert complete.expected_rows == 5

    incomplete = summarize_window_coverage([-2, -1, 1, 2], -2, 2)
    assert incomplete.is_complete is False
    assert incomplete.available_rows == 4
    assert incomplete.expected_rows == 5
