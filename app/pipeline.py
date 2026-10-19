import logging
from collections.abc import Callable, Iterable
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from psycopg2.extensions import connection

from app.config import Settings
from app.db import db_connection
from app.errors import ConfigError
from app.extract.http import ApiClient
from app.extract.moex import iter_history, iter_securities
from app.extract.raw import raw_path, write_jsonl
from app.load.staging import load_history_file, load_securities_file
from app.state import get_watermark, log_load
from app.transform.core import load_core_daily_quotes, load_core_securities

logger = logging.getLogger(__name__)

HISTORY = "history"
SECURITIES = "securities"
BOARD = "TQBR"


def _date_range(start: date, end: date) -> list[date]:
    """Return all calendar days from start to end inclusive."""
    days = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(days)]


def _resolve_dates(
    conn: connection, date_from: date | None, date_to: date | None
) -> list[date]:
    """Decide which trade dates this run should load."""
    yesterday = date.today() - timedelta(days=1)

    if date_to is None:
        date_to = yesterday
    elif date_to > yesterday:
        logger.warning(
            "date_to %s is not complete yet, using %s instead", date_to, yesterday
        )
        date_to = yesterday

    if date_from is None:
        watermark = get_watermark(conn, HISTORY, BOARD)
        if watermark is None:
            raise ConfigError("No load history found; pass date_from explicitly")
        date_from = watermark + timedelta(days=1)

    return _date_range(date_from, date_to)


def _ingest(
    settings: Settings,
    dataset: str,
    as_of_date: date,
    records: Iterable[dict[str, Any]],
    load_staging: Callable[[connection, Path], int],
    load_core: Callable[[connection], int],
) -> None:
    """Write records to raw, load them through staging into core and log the result."""
    logger.debug("Ingesting %s for %s", dataset, as_of_date)
    try:
        path = raw_path(settings.raw_dir, dataset, BOARD, as_of_date)
        extracted = write_jsonl(path, records)

        with db_connection(settings.db) as conn:
            load_staging(conn, path)
            affected = load_core(conn)
            log_load(conn, dataset, BOARD, as_of_date, "success", affected)

        logger.info(
            "Loaded %s for %s: %d extracted, %d upserted",
            dataset,
            as_of_date,
            extracted,
            affected,
        )
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
        logger.error("Failed to load %s for %s: %s", dataset, as_of_date, error)
        with db_connection(settings.db) as conn:
            log_load(conn, dataset, BOARD, as_of_date, "failed", error=error)
        raise


def run(
    settings: Settings, date_from: date | None = None, date_to: date | None = None
) -> None:
    """Refresh the reference snapshot, then load all pending trade dates."""
    with ApiClient(settings.moex_base_url) as client:
        _ingest(
            settings,
            SECURITIES,
            date.today(),
            iter_securities(client, BOARD),
            load_securities_file,
            load_core_securities,
        )

        with db_connection(settings.db) as conn:
            dates = _resolve_dates(conn, date_from, date_to)
        if not dates:
            logger.info("Nothing to load")
            return

        logger.info("Loading %d dates: %s .. %s", len(dates), dates[0], dates[-1])
        for trade_date in dates:
            _ingest(
                settings,
                HISTORY,
                trade_date,
                iter_history(client, trade_date, BOARD),
                load_history_file,
                load_core_daily_quotes,
            )


if __name__ == "__main__":
    from app.config import load_settings

    logging.basicConfig(level=logging.INFO)
    run(load_settings())
