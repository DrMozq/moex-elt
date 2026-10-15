import logging

from psycopg2.extensions import connection

from app.config import TRANSFORM_DIR
from app.db import execute_file

logger = logging.getLogger(__name__)


def load_core_daily_quotes(conn: connection) -> int:
    """Upsert rows from stg.history into core.daily_quotes. Return the number of affected rows."""
    count = execute_file(conn, TRANSFORM_DIR / "core_daily_quotes.sql")
    logger.info("Upserted %d rows into core.daily_quotes", count)
    return count


if __name__ == "__main__":
    from app.config import load_settings
    from app.db import db_connection

    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    with db_connection(settings.db) as conn:
        print(load_core_daily_quotes(conn))
