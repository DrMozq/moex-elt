from datetime import date

import pytest

from app.errors import ConfigError
from app.pipeline import _date_range, _resolve_dates

FIRST = date(2013, 3, 25)
TILL = date(2026, 10, 23)


def resolve(
    *,
    watermark: date | None = date(2026, 10, 20),
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[date]:
    return _resolve_dates(
        watermark=watermark,
        available_from=FIRST,
        available_till=TILL,
        date_from=date_from,
        date_to=date_to,
    )


def test_incremental_run_continues_after_watermark_up_to_till() -> None:
    assert resolve() == [date(2026, 10, 21), date(2026, 10, 22), date(2026, 10, 23)]


def test_incremental_run_returns_nothing_when_up_to_date() -> None:
    assert resolve(watermark=TILL) == []


def test_run_without_history_and_date_from_raises_config_error() -> None:
    with pytest.raises(ConfigError):
        resolve(watermark=None)


def test_date_to_after_published_range_is_capped_at_till() -> None:
    assert resolve(date_to=date(2026, 10, 30)) == [
        date(2026, 10, 21),
        date(2026, 10, 22),
        date(2026, 10, 23),
    ]


def test_date_from_before_available_data_is_moved_to_first_date() -> None:
    assert resolve(date_from=date(2010, 1, 1), date_to=date(2013, 3, 27)) == [
        date(2013, 3, 25),
        date(2013, 3, 26),
        date(2013, 3, 27),
    ]


def test_explicit_date_from_overrides_watermark() -> None:
    assert resolve(date_from=date(2026, 10, 1), date_to=date(2026, 10, 3)) == [
        date(2026, 10, 1),
        date(2026, 10, 2),
        date(2026, 10, 3),
    ]


def test_date_range_with_single_day() -> None:
    day = date(2026, 10, 6)
    assert _date_range(day, day) == [day]


def test_date_range_with_start_after_end_is_empty() -> None:
    assert _date_range(date(2026, 10, 6), date(2026, 10, 5)) == []
