from starlette.requests import Request

from app.core.rate_limiter.key_strategy.key_strategy import KeyStrategy


class HeaderKeyStrategy(KeyStrategy):
    def __init__(self, header_name: str = "X-Client-ID"):
        self.header_name = header_name

    def get_key(self, request: Request, route_path: str) -> str:
        value = request.headers.get(self.header_name, "unknown")
        return f"header:{self.header_name}:{value}:{route_path}"
