from __future__ import annotations

from abc import ABC, abstractmethod


class BaseRateLimiter(ABC):
    """Interface for pluggable rate limiter strategies."""

    @abstractmethod
    async def allow_request(self, key: str, limit: int, window_seconds: int, member_id: str | None = None) -> tuple[bool, int | None]:
        """
        Return (allowed: bool, retry_after_seconds: Optional[int]).
        If allowed True -> retry_after_seconds is None.
        If allowed False -> retry_after_seconds is seconds until next allowed request.
        """
        raise NotImplementedError
