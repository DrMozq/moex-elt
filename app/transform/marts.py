from psycopg2.extensions import connection

from app.config import MART_DIR
from app.db import execute_file


def build_daily_returns(conn: connection) -> int:
    """Rebuild mart.daily_returns from core. Return the number of rows."""
    return execute_file(conn, MART_DIR / "daily_returns.sql")


def build_market_daily(conn: connection) -> int:
    """Rebuild mart.market_daily from mart.daily_returns. Return the number of rows."""
    return execute_file(conn, MART_DIR / "market_daily.sql")


def build_top_movers(conn: connection) -> int:
    """Rebuild mart.top_movers from mart.daily_returns. Return the number of rows."""
    return execute_file(conn, MART_DIR / "top_movers.sql")


if __name__ == "__main__":
    from app.config import load_settings
    from app.db import db_connection

    settings = load_settings()
    with db_connection(settings.db) as conn:
        print(build_daily_returns(conn))
        print(build_market_daily(conn))
        print(build_top_movers(conn))
