import logging
from collections.abc import Callable, Iterable
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from psycopg2.extensions import connection

from app.checks import run_checks
from app.config import CHECKS_DIR, Settings
from app.db import db_connection
from app.errors import ConfigError
from app.extract.http import ApiClient
from app.extract.moex import get_history_range, iter_history, iter_securities
from app.extract.raw import raw_path, write_jsonl
from app.load.staging import load_history_file, load_securities_file
from app.state import get_watermark, log_load
from app.transform.core import load_core_daily_quotes, load_core_securities
from app.transform.marts import (
    build_daily_returns,
    build_market_daily,
    build_top_movers,
)

logger = logging.getLogger(__name__)

MOSCOW = ZoneInfo("Europe/Moscow")
HISTORY = "history"
SECURITIES = "securities"
BOARD = "TQBR"


def _date_range(start: date, end: date) -> list[date]:
    """Return all calendar days from start to end inclusive."""
    days = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(days)]


def _resolve_dates(
    *,
    watermark: date | None,
    available_from: date,
    available_till: date,
    date_from: date | None,
    date_to: date | None,
) -> list[date]:
    """Decide which trade dates this run should load."""
    if date_to is None:
        date_to = available_till
    elif date_to > available_till:
        logger.warning(
            "Data is published only up to %s; using it instead of date_to %s",
            available_till,
            date_to,
        )
        date_to = available_till

    if date_from is None:
        if watermark is None:
            raise ConfigError("No load history found; pass date_from explicitly")
        date_from = watermark + timedelta(days=1)
    elif date_from < available_from:
        logger.warning(
            "No data before %s; using it instead of date_from %s",
            available_from,
            date_from,
        )
        date_from = available_from

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
        try:
            with db_connection(settings.db) as conn:
                log_load(conn, dataset, BOARD, as_of_date, "failed", error=error)
        except Exception:
            logger.exception("Could not record failure in load_log")
        raise


def _build_marts(settings: Settings) -> None:
    """Rebuild all marts, run data quality checks and publish in one transaction."""
    with db_connection(settings.db) as conn:
        returns = build_daily_returns(conn)
        market = build_market_daily(conn)
        top_movers = build_top_movers(conn)

        run_checks(conn, CHECKS_DIR)

    logger.info(
        "Rebuilt marts: daily_returns=%d, market_daily=%d, top_movers=%d rows",
        returns,
        market,
        top_movers,
    )


def run(
    settings: Settings, date_from: date | None = None, date_to: date | None = None
) -> None:
    """Refresh the reference snapshot, load pending trade dates and rebuild marts."""
    with ApiClient(settings.moex_base_url) as client:
        _ingest(
            settings,
            SECURITIES,
            datetime.now(MOSCOW).date(),
            iter_securities(client, BOARD),
            load_securities_file,
            load_core_securities,
        )

        available_from, available_till = get_history_range(client, BOARD)
        logger.info("History available from %s till %s", available_from, available_till)

        with db_connection(settings.db) as conn:
            watermark = get_watermark(conn, HISTORY, BOARD)

        dates = _resolve_dates(
            watermark=watermark,
            available_from=available_from,
            available_till=available_till,
            date_from=date_from,
            date_to=date_to,
        )

        if dates:
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
        else:
            logger.info("No new trade dates to load")

    _build_marts(settings)
