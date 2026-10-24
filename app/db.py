import logging
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

import psycopg2
from psycopg2.extensions import connection

from app.config import DDL_DIR, DbSettings

logger = logging.getLogger(__name__)


@contextmanager
def db_connection(settings: DbSettings) -> Generator[connection]:
    conn = psycopg2.connect(**asdict(settings))
    try:
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_file(conn: connection, path: Path) -> int:
    sql = path.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.rowcount


def fetch_file(conn: connection, path: Path, limit: int) -> list[tuple]:
    """Execute a SQL file and return up to `limit` rows of its result."""
    sql = path.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchmany(limit)


def init_db(conn: connection, ddl_dir: Path) -> None:
    paths = sorted(ddl_dir.glob("*.sql"))
    if not paths:
        raise FileNotFoundError(f"No SQL files found in {ddl_dir.resolve()}")

    for path in paths:
        logger.info("Applying %s", path.name)
        execute_file(conn, path)


if __name__ == "__main__":
    from app.config import load_settings

    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    with db_connection(settings.db) as conn:
        init_db(conn, DDL_DIR)
