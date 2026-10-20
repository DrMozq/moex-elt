import logging

from psycopg2.extensions import connection

from app.config import MART_DIR
from app.db import execute_file

logger = logging.getLogger(__name__)


def build_daily_returns(conn: connection) -> int:
    """Rebuild mart.daily_returns from core. Return the number of rows."""
    return execute_file(conn, MART_DIR / "daily_returns.sql")


if __name__ == "__main__":
    from app.config import load_settings
    from app.db import db_connection

    logging.basicConfig(level=logging.DEBUG)
    settings = load_settings()
    with db_connection(settings.db) as conn:
        print(build_daily_returns(conn))
