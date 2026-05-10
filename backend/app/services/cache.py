"""Redis cache helpers with JSON serialisation."""

from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

_pool: aioredis.ConnectionPool | None = None


def _get_pool() -> aioredis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = aioredis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)
    return _pool


def _client() -> aioredis.Redis:  # type: ignore[type-arg]
    return aioredis.Redis(connection_pool=_get_pool())


async def cache_get(key: str) -> Any | None:
    try:
        value = await _client().get(key)
        if value is None:
            return None
        return json.loads(value)
    except Exception:
        logger.warning("cache_get failed for key %s", key)
        return None


async def cache_set(key: str, value: Any, ttl: int) -> None:
    try:
        await _client().set(key, json.dumps(value), ex=ttl)
    except Exception:
        logger.warning("cache_set failed for key %s", key)


async def cache_delete_pattern(pattern: str) -> None:
    try:
        client = _client()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
    except Exception:
        logger.warning("cache_delete_pattern failed for pattern %s", pattern)
