from datetime import date
from pathlib import Path

import pytest

from app.extract.raw import raw_path, read_jsonl, write_jsonl


def test_raw_path_builds_dataset_board_date_path() -> None:
    path = raw_path(Path("data/raw"), "history", "TQBR", date(2026, 10, 6))
    assert path == Path("data/raw/history/TQBR/2026-10-06.jsonl")


def test_write_and_read_jsonl_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "records.jsonl"
    records = [
        {"SECID": "SBER", "SHORTNAME": "Сбербанк", "CLOSE": 287.5},
        {"SECID": "AMEZ", "SHORTNAME": "АшинскийМЗ", "CLOSE": None},
    ]
    assert write_jsonl(path, records) == 2
    assert list(read_jsonl(path)) == records


def test_write_jsonl_creates_empty_file_for_no_records(tmp_path: Path) -> None:
    path = tmp_path / "records.jsonl"
    assert write_jsonl(path, []) == 0
    assert path.exists()
    assert list(read_jsonl(path)) == []


def test_write_jsonl_leaves_no_file_on_error(tmp_path: Path) -> None:
    path = tmp_path / "records.jsonl"

    def broken_records():
        yield {"SECID": "SBER"}
        raise RuntimeError("source failed")

    with pytest.raises(RuntimeError):
        write_jsonl(path, broken_records())

    assert not path.exists()
    assert list(tmp_path.iterdir()) == []
