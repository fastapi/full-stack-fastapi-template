from starlette.requests import Request

from app.core.rate_limiter.key_strategy.key_strategy import KeyStrategy


class IPKeyStrategy(KeyStrategy):
    """Generate rate limit key based on client IP address."""

    def get_key(self, request: Request, route_path: str) -> str:
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}:{route_path}"
