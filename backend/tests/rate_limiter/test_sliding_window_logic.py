from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.rate_limiter.rate_limiting_algorithm.registry import get_rate_limiter
from app.core.rate_limiter.rate_limiting_algorithm.sliding_window import (
    SlidingWindowRateLimiter,
)

@pytest.fixture
def mock_redis_from_url():
    with patch("redis.asyncio.from_url") as mocker:
        mock_instance = MagicMock()
        mocker.return_value = mock_instance
        yield mocker

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

def test_get_rate_limiter_none_strategy(mock_redis_from_url):
    rl = get_rate_limiter(strategy="none", redis_url="redis://localhost:6379/0", fail_open=True)
    assert rl is None


def test_get_rate_limiter_empty_strategy(mock_redis_from_url):
    rl = get_rate_limiter(strategy="", redis_url="redis://localhost:6379/0", fail_open=True)
    assert rl is None


def test_get_rate_limiter_null_strategy(mock_redis_from_url):
    rl = get_rate_limiter(strategy="null", redis_url="redis://localhost:6379/0", fail_open=True)
    assert rl is None


def test_get_rate_limiter_no_strategy(mock_redis_from_url):
    rl = get_rate_limiter(strategy=None, redis_url="redis://localhost:6379/0", fail_open=True)
    assert rl is None


def test_get_rate_limiter_no_redis_url(mock_redis_from_url):
    rl = get_rate_limiter(strategy="sliding_window", redis_url="", fail_open=True)
    assert rl is None


def test_get_rate_limiter_sliding_window(mock_redis_from_url):
    rl = get_rate_limiter(strategy="sliding_window", redis_url="redis://x", fail_open=True)
    assert isinstance(rl, SlidingWindowRateLimiter)


def test_get_rate_limiter_sliding_window_dash(mock_redis_from_url):
    rl = get_rate_limiter(strategy="sliding-window", redis_url="redis://x", fail_open=False)
    assert isinstance(rl, SlidingWindowRateLimiter)
    assert rl.get_fail_open() is False


def test_get_rate_limiter_fail_open_coercion(mock_redis_from_url):
    rl = get_rate_limiter(strategy="sliding_window", redis_url="redis://x", fail_open=None)
    assert isinstance(rl, SlidingWindowRateLimiter)
    assert rl.get_fail_open() is False  # default fallback


def test_rate_limiter_unknown_strategy(mock_redis_from_url):
    with pytest.raises(ValueError) as e:
        get_rate_limiter(strategy="weird_strategy", redis_url="redis://x", fail_open=True)
    assert "Unknown rate limiter strategy" in str(e.value)
