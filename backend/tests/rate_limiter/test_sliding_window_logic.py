from unittest.mock import AsyncMock

import pytest

from app.core.rate_limiter.rate_limiting_algorithm.sliding_window import (
    SlidingWindowRateLimiter,
)


@pytest.mark.asyncio
async def test_allow_first_request():
    redis = AsyncMock()
    redis.evalsha.return_value = [1, 0]  # allowed

    limiter = SlidingWindowRateLimiter(redis, True)
    allowed, retry_after = await limiter.allow_request("key1", 5, 60)

    assert allowed is True
    assert retry_after is None


@pytest.mark.asyncio
async def test_block_when_limit_reached():
    redis = AsyncMock()
    redis.evalsha.return_value = [3, 20]  # blocked

    limiter = SlidingWindowRateLimiter(redis, True)
    allowed, retry_after = await limiter.allow_request("key1", 1, 60)

    assert allowed is False


@pytest.mark.asyncio
async def test_fail_open_allows_requests():
    redis = AsyncMock()
    redis.evalsha.side_effect = Exception("Redis down")

    limiter = SlidingWindowRateLimiter(redis, fail_open=True)
    allowed, retry_after = await limiter.allow_request("key", 5, 60)

    assert allowed is True
    assert retry_after is None
