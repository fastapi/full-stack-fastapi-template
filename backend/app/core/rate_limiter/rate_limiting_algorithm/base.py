from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple, Optional

class BaseRateLimiter(ABC):
    """Interface for pluggable rate limiter strategies."""

    @abstractmethod
    async def allow_request(self, key: str, limit: int, window_seconds: int, member_id: Optional[str] = None) -> Tuple[bool, Optional[int]]:
        """
        Return (allowed: bool, retry_after_seconds: Optional[int]).
        If allowed True -> retry_after_seconds is None.
        If allowed False -> retry_after_seconds is seconds until next allowed request.
        """
        raise NotImplementedError
