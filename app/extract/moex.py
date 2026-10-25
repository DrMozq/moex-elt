import logging
from collections.abc import Iterator
from datetime import date
from typing import Any

from app.errors import DataError
from app.extract.http import ApiClient

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
                f"Unexpected response structure for {board} history {trade_date}: {e!r}"
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


def iter_securities(client: ApiClient, board: str = "TQBR") -> Iterator[dict[str, Any]]:
    """Yield the current reference data for all securities on a board."""
    path = f"engines/stock/markets/shares/boards/{board}/securities.json"
    params = {"iss.meta": "off", "iss.only": "securities"}
    response = client.get(path, params)

    try:
        columns = response["securities"]["columns"]
        data = response["securities"]["data"]
    except KeyError as e:
        raise DataError(
            f"Unexpected response structure for {board} securities: {e!r}"
        ) from e

    logger.debug("Securities for %s: rows=%d", board, len(data))
    for row in data:
        yield dict(zip(columns, row))


def get_history_range(client: ApiClient, board: str = "TQBR") -> tuple[date, date]:
    """Return the first and last dates with published trading results for a board."""
    path = f"history/engines/stock/markets/shares/boards/{board}/dates.json"
    response = client.get(path, {"iss.meta": "off"})

    try:
        block = response["dates"]
        row = dict(zip(block["columns"], block["data"][0]))
        first, last = row["from"], row["till"]
    except (KeyError, IndexError) as e:
        raise DataError(
            f"Unexpected response structure for {board} dates: {e!r}"
        ) from e

    return date.fromisoformat(first), date.fromisoformat(last)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    with ApiClient("https://iss.moex.com/iss") as client:
        # history
        for d in (date(2026, 10, 6), date(2026, 10, 4), date(2026, 3, 6)):
            print(d, len(list(iter_history(client, d))))

        # securities
        records = list(iter_securities(client))
        print(len(records))
        print(records[0])

        # dates
        print(get_history_range(client))
