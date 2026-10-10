class PipelineError(Exception):
    """Base class for all pipeline exceptions."""

class RetryableError(PipelineError):
    """Temporary failure; retrying may help."""

class RateLimitError(RetryableError):
    """HTTP 429: too many requests, wait before retrying."""

    def __init__(self, message: str, retry_after: float | None = None) -> None: 
        super().__init__(message)
        self.retry_after = retry_after

class ApiError(PipelineError):
    """Client error (4xx other than 429); retrying will not help."""

    def __init__(self, message: str, status: int) -> None:
        super().__init__(message)
        self.status = status

class DataError(PipelineError):
    """The API returned unexpected or malformed data."""
