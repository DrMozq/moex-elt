import argparse
import logging
import sys
from datetime import date

from app.config import DDL_DIR, load_settings
from app.db import db_connection, init_db
from app.errors import PipelineError
from app.pipeline import run

logger = logging.getLogger("app")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m app", description="MOEX ELT pipeline"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable debug logging"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("init", help="create schemas and tables")

    run_parser = commands.add_parser("run", help="load data and rebuild marts")
    run_parser.add_argument(
        "--from",
        dest="date_from",
        type=date.fromisoformat,
        metavar="YYYY-MM-DD",
        help="first trade date to load (default: day after the last loaded date)",
    )
    run_parser.add_argument(
        "--to",
        dest="date_to",
        type=date.fromisoformat,
        metavar="YYYY-MM-DD",
        help="last trade date to load (default: yesterday)",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point: parse arguments, run the command and return an exit code."""
    args = _parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        settings = load_settings()
        if args.command == "init":
            with db_connection(settings.db) as conn:
                init_db(conn, DDL_DIR)
        elif args.command == "run":
            run(settings, args.date_from, args.date_to)

    except PipelineError as e:
        logger.error("Pipeline failed: %s", e)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
