import logging

from psycopg2.extensions import connection

from app.config import TRANSFORM_DIR
from app.db import execute_file

logger = logging.getLogger(__name__)


def load_core_daily_quotes(conn: connection) -> int:
    """Upsert rows from stg.history into core.daily_quotes.

    Return the number of affected rows.
    """
    upserted = execute_file(conn, TRANSFORM_DIR / "core_daily_quotes.sql")
    logger.debug("Upserted %d rows into core.daily_quotes", upserted)
    return upserted


def load_core_securities(conn: connection) -> int:
    """Upsert rows from stg.securities into core.securities.

    Return the number of affected rows.
    """
    upserted = execute_file(conn, TRANSFORM_DIR / "core_securities.sql")
    logger.debug("Upserted %d rows into core.securities", upserted)
    return upserted


if __name__ == "__main__":
    from app.config import load_settings
    from app.db import db_connection

    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    with db_connection(settings.db) as conn:
        print(load_core_daily_quotes(conn))
        print(load_core_securities(conn))
