import csv
import io
import logging
from pathlib import Path

from psycopg2.extensions import connection

from app.raw import read_jsonl

logger = logging.getLogger(__name__)


HISTORY_COLUMNS = (
    "boardid",
    "tradedate",
    "shortname",
    "secid",
    "numtrades",
    "value",
    "open",
    "low",
    "high",
    "legalcloseprice",
    "waprice",
    "close",
    "volume",
    "marketprice2",
    "marketprice3",
    "admittedquote",
    "mp2valtrd",
    "marketprice3tradesvalue",
    "admittedvalue",
    "waval",
    "tradingsession",
    "currencyid",
    "trendclspr",
    "trade_session_date",
)


def truncate_history(conn: connection) -> None:
    """Remove all rows from stg.history."""
    with conn.cursor() as cursor:
        cursor.execute("TRUNCATE stg.history")


def load_history_file(conn: connection, path: Path) -> int:
    """Append rows from a raw JSON Lines file to stg.history. Return the number of rows."""
    count = 0
    buf = io.StringIO()
    writer = csv.writer(buf)

    with conn.cursor() as cursor:
        columns = ", ".join((*HISTORY_COLUMNS, "source_file"))
        query = f"COPY stg.history ({columns}) FROM STDIN WITH (FORMAT csv)"
        for record in read_jsonl(path):
            row = (*(record.get(c.upper()) for c in HISTORY_COLUMNS), str(path))
            writer.writerow(row)
            count += 1

        buf.seek(0)
        cursor.copy_expert(query, buf)

    return count


if __name__ == "__main__":
    from datetime import date

    from app.config import load_settings
    from app.db import db_connection
    from app.raw import raw_path

    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    with db_connection(settings.db) as conn:
        truncate_history(conn)
        for d in (date(2026, 10, 6), date(2026, 10, 4)):
            path = raw_path(settings.raw_dir, "history", "TQBR", d)
            print(path, load_history_file(conn, path))
