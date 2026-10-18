from datetime import date

from psycopg2.extensions import connection

VALID_STATUSES = ("success", "failed")


def get_watermark(conn: connection, dataset: str, board: str) -> date | None:
    """Return the latest successfully loaded trade date, or None if nothing was loaded yet."""
    query = """
        SELECT max(trade_date)
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
    trade_date: date,
    status: str,
    rows_loaded: int | None = None,
    error: str | None = None,
) -> None:
    """Append one entry to meta.load_log."""
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {VALID_STATUSES}, got {status!r}")

    query = """
        INSERT INTO meta.load_log (
            dataset, board, trade_date, status, rows_loaded, error
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (dataset, board, trade_date, status, rows_loaded, error))


if __name__ == "__main__":
    from app.config import load_settings
    from app.db import db_connection

    settings = load_settings()
    with db_connection(settings.db) as conn:
        print("before:", get_watermark(conn, "history", "TQBR"))
        log_load(conn, "history", "TQBR", date(2026, 10, 6), "success", rows_loaded=507)
        print("after:", get_watermark(conn, "history", "TQBR"))

        try:
            log_load(conn, "history", "TQBR", date(2026, 10, 6), "sucess")
        except ValueError as e:
            print("rejected:", e)
