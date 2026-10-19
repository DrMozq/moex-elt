import json
import os
from collections.abc import Iterable, Iterator
from datetime import date
from pathlib import Path
from typing import Any


def raw_path(root: Path, dataset: str, board: str, as_of_date: date) -> Path:
    """Return the path of a raw file, e.g. root/history/TQBR/2026-10-06.jsonl."""
    return root / dataset / board / f"{as_of_date.isoformat()}.jsonl"


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> int:
    """Write records to a JSON Lines file atomically. Return the number of records."""
    path_tmp = path.with_name(path.name + ".tmp")
    path_tmp.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path_tmp, "w", encoding="utf-8") as f:
            cnt = 0
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                cnt += 1
    except BaseException:
        path_tmp.unlink(missing_ok=True)
        raise

    os.replace(path_tmp, path)
    return cnt


def read_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """Yield records from a JSON Lines file, one at a time."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            jsonl = line.strip()
            if not jsonl:
                continue
            yield json.loads(jsonl)


if __name__ == "__main__":
    from app.config import load_settings
    from app.extract.http import ApiClient
    from app.extract.moex import iter_history, iter_securities

    root = Path("data/raw")
    with ApiClient("https://iss.moex.com/iss") as client:
        # history
        for d in (date(2026, 10, 6), date(2026, 10, 4)):
            path = raw_path(root, "history", "TQBR", d)
            n = write_jsonl(path, iter_history(client, d))
            print(path, n)
            
        print(next(read_jsonl(raw_path(root, "history", "TQBR", date(2026, 10, 6)))))

        # securities
        settings = load_settings()
        path = raw_path(settings.raw_dir, "securities", "TQBR", date.today())
        print(write_jsonl(path, iter_securities(client)))
