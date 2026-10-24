import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from app.errors import ConfigError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"
DDL_DIR = SQL_DIR / "ddl"
TRANSFORM_DIR = SQL_DIR / "transform"
MART_DIR = SQL_DIR / "mart"
CHECKS_DIR = SQL_DIR / "checks"


@dataclass(frozen=True)
class DbSettings:
    host: str
    port: int
    dbname: str
    user: str
    password: str = field(repr=False)


@dataclass(frozen=True)
class Settings:
    db: DbSettings
    moex_base_url: str
    raw_dir: Path


def _required(name: str, errors: list[str]) -> str:
    value = os.getenv(name, "")
    if not value:
        errors.append(f"{name} is not set")
    return value


def load_settings() -> Settings:
    load_dotenv()
    errors: list[str] = []

    host = _required("DB_HOST", errors)
    port_raw = _required("DB_PORT", errors)
    dbname = _required("DB_NAME", errors)
    user = _required("DB_USER", errors)
    password = _required("DB_PASSWORD", errors)
    moex_base_url = _required("MOEX_BASE_URL", errors)
    raw_dir = Path(_required("RAW_DIR", errors))

    port = 0
    if port_raw:
        try:
            port = int(port_raw)
        except ValueError:
            errors.append(f"DB_PORT must be an integer, got {port_raw!r}")

    if errors:
        raise ConfigError("Invalid settings: " + "; ".join(errors))

    return Settings(
        db=DbSettings(
            host=host, port=port, dbname=dbname, user=user, password=password
        ),
        moex_base_url=moex_base_url,
        raw_dir=raw_dir,
    )


if __name__ == "__main__":
    print(load_settings())
