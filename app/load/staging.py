import csv
import io
import logging
from collections.abc import Sequence
from pathlib import Path

from psycopg2 import sql
from psycopg2.extensions import connection

from app.extract.raw import read_jsonl

logger = logging.getLogger(__name__)


HISTORY_COLUMNS = (
    "BOARDID",
    "TRADEDATE",
    "SHORTNAME",
    "SECID",
    "NUMTRADES",
    "VALUE",
    "OPEN",
    "LOW",
    "HIGH",
    "LEGALCLOSEPRICE",
    "WAPRICE",
    "CLOSE",
    "VOLUME",
    "MARKETPRICE2",
    "MARKETPRICE3",
    "ADMITTEDQUOTE",
    "MP2VALTRD",
    "MARKETPRICE3TRADESVALUE",
    "ADMITTEDVALUE",
    "WAVAL",
    "TRADINGSESSION",
    "CURRENCYID",
    "TRENDCLSPR",
    "TRADE_SESSION_DATE",
)

SECURITIES_COLUMNS = (
    "SECID",
    "BOARDID",
    "SHORTNAME",
    "PREVPRICE",
    "LOTSIZE",
    "FACEVALUE",
    "STATUS",
    "BOARDNAME",
    "DECIMALS",
    "SECNAME",
    "REMARKS",
    "MARKETCODE",
    "INSTRID",
    "SECTORID",
    "MINSTEP",
    "PREVWAPRICE",
    "FACEUNIT",
    "PREVDATE",
    "ISSUESIZE",
    "ISIN",
    "LATNAME",
    "REGNUMBER",
    "PREVLEGALCLOSEPRICE",
    "CURRENCYID",
    "SECTYPE",
    "LISTLEVEL",
    "SETTLEDATE",
)


def _replace_from_jsonl(
    conn: connection, path: Path, table: str, source_columns: Sequence[str]
) -> int:
    """Replace the contents of a staging table with records from a JSONL file."""
    table_id = sql.Identifier(*table.split("."))
    column_ids = sql.SQL(", ").join(
        sql.Identifier(name)
        for name in (*map(str.lower, source_columns), "source_file")
    )
    truncate_query = sql.SQL("TRUNCATE {}").format(table_id)
    copy_query = sql.SQL("COPY {} ({}) FROM STDIN WITH (FORMAT csv)").format(
        table_id, column_ids
    )

    buf = io.StringIO()
    writer = csv.writer(buf)
    count = 0
    for record in read_jsonl(path):
        writer.writerow((*(record.get(c) for c in source_columns), str(path)))
        count += 1
    buf.seek(0)

    with conn.cursor() as cursor:
        cursor.execute(truncate_query)
        cursor.copy_expert(copy_query.as_string(conn), buf)

    logger.debug("Loaded %d rows from %s into %s", count, path.name, table)
    return count


def load_history_file(conn: connection, path: Path) -> int:
    """Replace stg.history with the given raw file."""
    return _replace_from_jsonl(conn, path, "stg.history", HISTORY_COLUMNS)


def load_securities_file(conn: connection, path: Path) -> int:
    """Replace stg.securities with the given raw file."""
    return _replace_from_jsonl(conn, path, "stg.securities", SECURITIES_COLUMNS)


if __name__ == "__main__":
    from datetime import date

    from app.config import load_settings
    from app.db import db_connection
    from app.extract.raw import raw_path

    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    with db_connection(settings.db) as conn:
        # history
        d = date(2026, 10, 9)
        path_history = raw_path(settings.raw_dir, "history", "TQBR", d)
        print(path_history, load_history_file(conn, path_history))

        # securities
        d = date(2026, 10, 19)
        path_securities = raw_path(settings.raw_dir, "securities", "TQBR", d)
        print(path_securities, load_securities_file(conn, path_securities))
