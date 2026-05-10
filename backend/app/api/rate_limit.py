"""Redis-backed sliding-window rate limiter as a FastAPI dependency."""

from __future__ import annotations

import time
from typing import Callable

from fastapi import Depends, HTTPException, Request


def RateLimiter(max_calls: int, window_seconds: int) -> Callable:
    """Return a FastAPI dependency that enforces a per-IP rate limit via Redis.

    Falls back to in-memory limiting when Redis is unavailable.
    """
    _memory_store: dict[str, list[float]] = {}

    async def _limit(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"rl:{max_calls}:{window_seconds}:{client_ip}"

        try:
            from app.services.cache import _client

            redis = _client()
            now = time.time()
            window_start = now - window_seconds

            pipe = redis.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window_seconds + 1)
            results = await pipe.execute()
            count: int = results[2]

        except Exception:
            # Fallback: in-process sliding window
            now = time.time()
            window_start = now - window_seconds
            hits = _memory_store.get(client_ip, [])
            hits = [t for t in hits if t > window_start]
            hits.append(now)
            _memory_store[client_ip] = hits
            count = len(hits)

        if count > max_calls:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {max_calls} requests per {window_seconds}s",
            )

    return Depends(_limit)
