from datetime import date

from psycopg2.extensions import connection

VALID_STATUSES = ("success", "failed")


def get_watermark(conn: connection, dataset: str, board: str) -> date | None:
    """Return the latest successfully loaded as-of date, or None if nothing was loaded yet."""
    query = """
        SELECT max(as_of_date)
        FROM meta.load_log
        WHERE dataset = %s AND board = %s AND status = 'success'
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (dataset, board))
        row = cursor.fetchone()
    if row is None:
        raise AssertionError("Aggregate query returned no rows")
    return row[0]


def log_load(
    conn: connection,
    dataset: str,
    board: str,
    as_of_date: date,
    status: str,
    rows_loaded: int | None = None,
    error: str | None = None,
) -> None:
    """Append one entry to meta.load_log."""
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {VALID_STATUSES}, got {status!r}")

    query = """
        INSERT INTO meta.load_log (
            dataset, board, as_of_date, status, rows_loaded, error
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (dataset, board, as_of_date, status, rows_loaded, error))


if __name__ == "__main__":
    from app.config import load_settings
    from app.db import db_connection

    with db_connection(load_settings().db) as conn:
        print("history watermark:", get_watermark(conn, "history", "TQBR"))
        print("securities watermark:", get_watermark(conn, "securities", "TQBR"))
