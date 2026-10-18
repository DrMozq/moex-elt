import logging
from datetime import date, timedelta

from psycopg2.extensions import connection

from app.config import Settings
from app.db import db_connection
from app.errors import ConfigError
from app.extract.http import ApiClient
from app.extract.moex import iter_history
from app.extract.raw import raw_path, write_jsonl
from app.load.staging import load_history_file, truncate_history
from app.state import get_watermark, log_load
from app.transform.core import load_core_daily_quotes

logger = logging.getLogger(__name__)

DATASET = "history"
BOARD = "TQBR"


def date_range(start: date, end: date) -> list[date]:
    """Return all calendar days from start to end inclusive."""
    days = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(days)]


def resolve_dates(
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
        watermark = get_watermark(conn, DATASET, BOARD)
        if watermark is None:
            raise ConfigError("No load history found; pass date_from explicitly")
        date_from = watermark + timedelta(days=1)

    return date_range(date_from, date_to)


def run(
    settings: Settings, date_from: date | None = None, date_to: date | None = None
) -> None:
    """Extract, load and transform each date of the run in its own transaction."""
    with db_connection(settings.db) as conn:
        dates = resolve_dates(conn, date_from, date_to)
        if not dates:
            logger.info("Nothing to load")
            return

    logger.info("Loading %d dates: %s .. %s", len(dates), dates[0], dates[-1])

    with ApiClient(settings.moex_base_url) as client:
        for trade_date in dates:
            try:
                # extract
                path = raw_path(settings.raw_dir, DATASET, BOARD, trade_date)
                extracted = write_jsonl(path, iter_history(client, trade_date, BOARD))

                # load + transform
                with db_connection(settings.db) as conn:
                    truncate_history(conn)
                    load_history_file(conn, path)
                    rows_loaded = load_core_daily_quotes(conn)
                    log_load(conn, DATASET, BOARD, trade_date, "success", rows_loaded)

                logger.info(
                    "Loaded %s: %d extracted, %d upserted",
                    trade_date,
                    extracted,
                    rows_loaded,
                )

            except Exception as e:
                error = f"{type(e).__name__}: {e}"
                logger.error("Failed to load %s: %s", trade_date, error)
                with db_connection(settings.db) as conn:
                    log_load(conn, DATASET, BOARD, trade_date, "failed", error=error)
                raise


if __name__ == "__main__":
    from app.config import load_settings

    logging.basicConfig(level=logging.INFO)
    run(load_settings())
