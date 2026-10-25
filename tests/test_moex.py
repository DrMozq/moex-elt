from datetime import date
from typing import Any

import pytest

from app.errors import DataError
from app.extract.moex import iter_history

DAY = date(2026, 10, 6)


def history_page(
    rows: list[list[Any]], start: int, total: int, page_size: int = 100
) -> dict:
    """Build a response shaped like the ISS history endpoint."""
    return {
        "history": {"columns": ["SECID", "CLOSE"], "data": rows},
        "history.cursor": {
            "columns": ["INDEX", "TOTAL", "PAGESIZE"],
            "data": [[start, total, page_size]],
        },
    }


class FakeClient:
    """Return prepared responses by the `start` parameter and record requests."""

    def __init__(self, pages: dict[int, dict]) -> None:
        self.pages = pages
        self.starts: list[int] = []

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        assert params is not None
        start = params["start"]
        self.starts.append(start)
        return self.pages[start]


def test_iter_history_follows_cursor_across_pages() -> None:
    client = FakeClient(
        {
            0: history_page(
                [["SBER", 287.5], ["GAZP", 111.6]], start=0, total=5, page_size=2
            ),
            2: history_page(
                [["LKOH", 6125], ["YDEX", 3483]], start=2, total=5, page_size=2
            ),
            4: history_page([["OZON", 3538]], start=4, total=5, page_size=2),
        }
    )

    records = list(iter_history(client, DAY))  # type: ignore[arg-type]

    assert [r["SECID"] for r in records] == ["SBER", "GAZP", "LKOH", "YDEX", "OZON"]
    assert records[0] == {"SECID": "SBER", "CLOSE": 287.5}
    assert client.starts == [0, 2, 4]


def test_iter_history_returns_nothing_for_empty_day() -> None:
    client = FakeClient({0: history_page([], start=0, total=0)})

    records = list(iter_history(client, DAY))  # type: ignore[arg-type]

    assert records == []
    assert client.starts == [0]


def test_iter_history_raises_data_error_on_unexpected_structure() -> None:
    page = {"history": {"columns": [], "data": []}}
    client = FakeClient({0: page})

    with pytest.raises(DataError):
        list(iter_history(client, DAY))  # type: ignore[arg-type]
