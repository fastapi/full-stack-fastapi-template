from sqlmodel import Session
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.core.db import engine


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, excluded_paths: list[str] | None = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or []

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip DB session for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)

        response = Response("Internal server error", status_code=500)
        with Session(engine) as session:
            request.state.db_session = session
            response = await call_next(request)
        return response
