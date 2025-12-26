import pytest
from starlette.requests import Request

from app.core.rate_limiter.key_strategy.header_key_strategy import HeaderKeyStrategy
from app.core.rate_limiter.key_strategy.ip_key_strategy import IPKeyStrategy
from app.core.rate_limiter.key_strategy.key_strategy_enum import KeyStrategyName
from app.core.rate_limiter.key_strategy.key_strategy_registry import get_key_strategy


def test_ip_strategy_build_key():
    strat = IPKeyStrategy()

    scope = {
        "client": ("127.0.0.1", 5050),
        "method": "GET",
        "path": "/api/test",
        "headers": [],
        "type": "http"
    }
    request = Request(scope)

    key = strat.get_key(request, scope.get('path'))

    assert key.startswith("ip:127.0.0.1")
    assert ":/api/test" in key

def test_get_key_strategy_header_default():
    """
    Should return HeaderKeyStrategy with default header name
    when header_name is not provided.
    """
    ks = get_key_strategy(KeyStrategyName.HEADER)
    assert isinstance(ks, HeaderKeyStrategy)
    assert ks.header_name == "X-Client-ID"


def test_get_key_strategy_header_custom():
    """Should use user-supplied custom header name."""
    ks = get_key_strategy(KeyStrategyName.HEADER, header_name="X-Auth-ID")
    assert isinstance(ks, HeaderKeyStrategy)
    assert ks.header_name == "X-Auth-ID"


def test_get_key_strategy_invalid():
    """Should throw ValueError for unsupported key strategies."""
    with pytest.raises(ValueError) as e:
        get_key_strategy("UNKNOWN")  # type: ignore[arg-type]

    assert "Unsupported key strategy" in str(e.value)
