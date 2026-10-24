import logging
from pathlib import Path

from psycopg2.extensions import connection

from app.db import fetch_file
from app.errors import DataQualityError

logger = logging.getLogger(__name__)

SAMPLE_SIZE = 5


def run_checks(conn: connection, checks_dir: Path) -> None:
    """Run every check in checks_dir; raise DataQualityError if any returns rows."""
    paths = sorted(checks_dir.glob("*.sql"))
    if not paths:
        raise FileNotFoundError(f"No SQL files found in {checks_dir.resolve()}")

    failed: list[str] = []
    for path in paths:
        logger.debug("Running check %s", path.stem)
        if violations := fetch_file(conn, path, SAMPLE_SIZE):
            logger.error("Check %s failed, sample rows: %s", path.stem, violations)
            failed.append(path.stem)

    if failed:
        raise DataQualityError(f"Failed checks: {', '.join(failed)}")
    logger.info("All %d checks passed", len(paths))


if __name__ == "__main__":
    from app.config import CHECKS_DIR, load_settings
    from app.db import db_connection

    logging.basicConfig(level=logging.DEBUG)
    with db_connection(load_settings().db) as conn:
        run_checks(conn, CHECKS_DIR)
