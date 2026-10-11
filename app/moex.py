import logging
from collections.abc import Iterator
from datetime import date
from typing import Any

from app.errors import DataError
from app.http import ApiClient

logger = logging.getLogger(__name__)


def iter_history(
    client: ApiClient,
    trade_date: date,
    board: str = "TQBR",
) -> Iterator[dict[str, Any]]:
    """Yield daily trading results for all securities on a board, one record at a time."""
    path = f"history/engines/stock/markets/shares/boards/{board}/securities.json"
    params: dict[str, Any] = {"date": trade_date.isoformat()}
    start = 0
    while True:
        params["start"] = start
        response = client.get(path, params)
        try:
            columns = response["history"]["columns"]
            cursor_block = response["history.cursor"]
            data = response["history"]["data"]
            cursor = dict(zip(cursor_block["columns"], cursor_block["data"][0]))
        except (KeyError, IndexError) as e:
            raise DataError(
                f"Unexpected response structure for {trade_date}: {e!r}"
            ) from e

        logger.debug(
            "Page for %s: start=%d, rows=%d, total=%d",
            trade_date,
            start,
            len(data),
            cursor["TOTAL"],
        )
        for row in data:
            yield dict(zip(columns, row))

        start += cursor["PAGESIZE"]
        if start >= cursor["TOTAL"]:
            break
