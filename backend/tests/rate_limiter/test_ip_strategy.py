from starlette.requests import Request

from app.core.rate_limiter.key_strategy.ip_key_strategy import IPKeyStrategy


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
