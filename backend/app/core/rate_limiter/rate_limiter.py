import logging

from fastapi import HTTPException, Request

from app.core.rate_limiter.key_strategy import key_strategy_registry
from app.core.rate_limiter.key_strategy.key_strategy_enum import KeyStrategyName

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, limit: int, window_seconds: int, key_policy: KeyStrategyName = KeyStrategyName.IP):
        self.limit = limit
        self.window_seconds = window_seconds
        self.key_policy = key_policy

    async def __call__(self, request: Request) -> None:
        rate_limiter = getattr(request.app.state, "rate_limiter", None)

        if rate_limiter is None:
            return None

        # Create Key
        key_strategy = key_strategy_registry.get_key_strategy(self.key_policy)
        path: str = request.scope.get("path") or ""
        key = key_strategy.get_key(request, path)

        allowed = True
        retry_after = None
        try:
            allowed, retry_after = await rate_limiter.allow_request(
                        key, self.limit, self.window_seconds
                )
        except Exception:
                logger.exception("Error invoking rate limiter")
                if rate_limiter.get_fail_open():
                    raise HTTPException(
                        status_code=503,
                        detail={"detail": "Rate limiter unavailable"},
                    )

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Too Many Requests. Retry after {retry_after}s",
                headers={"Retry-After": str(retry_after)}
            )
