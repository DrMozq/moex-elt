import logging
import time
from collections.abc import Callable
from typing import Any, Self

import requests

from app.errors import ApiError, DataError, RateLimitError, RetryableError

logger = logging.getLogger(__name__)

MAX_DELAY = 60.0  # seconds, upper bound for any pause between retries


class ApiClient:
    """HTTP client for JSON APIs."""

    def __init__(
        self,
        base_url: str,
        *,
        user_agent: str = "moex-elt/0.1",
        timeout: float = 10.0,
        attempts: int = 4,
        base_delay: float = 0.5,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if attempts < 1:
            raise ValueError(f"attempts must be >= 1, got {attempts}")
        if timeout <= 0:
            raise ValueError(f"timeout must be > 0, got {timeout}")
        if base_delay < 0:
            raise ValueError(f"base_delay must be >= 0, got {base_delay}")

        self.base_url = base_url
        self.user_agent = user_agent
        self.timeout = timeout
        self.attempts = attempts
        self.base_delay = base_delay
        self.sleep = sleep
        self.session = requests.Session()
        self.session.headers["User-Agent"] = user_agent

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.close()
        return False

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        logger.debug("GET %s params=%s", url, params)

        for attempt in range(1, self.attempts + 1):
            try:
                return self._fetch_json(url, params)
            except RetryableError as e:
                if attempt == self.attempts:
                    raise

                if isinstance(e, RateLimitError) and e.retry_after is not None:
                    delay = e.retry_after
                else:
                    delay = self.base_delay * (2 ** (attempt - 1))
                delay = min(max(delay, 0.0), MAX_DELAY)
                logger.warning(
                    "Request failed: %s. Retry %d/%d in %.1f s",
                    e,
                    attempt,
                    self.attempts - 1,
                    delay,
                )
                self.sleep(delay)

        raise AssertionError("unreachable")

    def close(self) -> None:
        self.session.close()

    def _fetch_json(
        self, url: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as e:
            raise RetryableError(f"Network error for {url}: {e}") from e

        status = response.status_code
        if 200 <= status <= 299:
            try:
                return response.json()
            except ValueError as e:
                raise DataError(f"Response from {url} is not valid JSON") from e
        elif status == 429:
            retry_after = None
            raw = response.headers.get("Retry-After")
            if raw is not None:
                try:
                    retry_after = float(raw)
                except ValueError:
                    pass  # not a number. retry_after is None
            raise RateLimitError(f"429 Too Many Requests: {url}", retry_after)
        elif 500 <= status <= 599:
            raise RetryableError(f"Server error {status} for {url}")
        else:
            raise ApiError(f"Client error {status} for {url}", status)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    with ApiClient("https://iss.moex.com/iss") as client:
        data = client.get(
            "history/engines/stock/markets/shares/boards/TQBR/securities.json",
            {"date": "2026-10-06"},
        )
    print(data["history.cursor"])

    delays: list[float] = []
    with ApiClient("http://10.255.255.1", timeout=1, sleep=delays.append) as client:
        try:
            client.get("anything")
        except RetryableError as e:
            print("gave up:", e)
    print(delays)
