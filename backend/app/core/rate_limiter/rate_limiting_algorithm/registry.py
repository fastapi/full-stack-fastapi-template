from typing import Optional
from app.core.rate_limiter.rate_limiting_algorithm.base import BaseRateLimiter
from app.core.rate_limiter.rate_limiting_algorithm.sliding_window import SlidingWindowRateLimiter
import redis.asyncio as redis

def get_rate_limiter(strategy: Optional[str], redis_url: Optional[str], fail_open: Optional[str]) -> Optional[BaseRateLimiter]:
    """
    Factory: returns an instance of BaseRateLimiter or None (if disabled).
    """
    if not strategy or strategy.lower() in ("none", "null", ""):
        return None

    if not redis_url:
        return None

    rc = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    st = strategy.lower()
    if st == "sliding_window" or st == "sliding-window":
        return SlidingWindowRateLimiter(rc, fail_open or False)

    # extendable for other strategies
    raise ValueError(f"Unknown rate limiter strategy: {strategy}")