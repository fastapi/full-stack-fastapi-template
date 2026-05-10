import json
import logging
import time
from typing import Any, Callable

import jwt
import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings

logger = logging.getLogger("app.access")

ALGORITHM = "HS256"


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:  # type: ignore[override]
        start = time.monotonic()
        response = await call_next(request)
        elapsed_ms = round((time.monotonic() - start) * 1000, 2)

        user_id: str | None = None
        try:
            auth = request.headers.get("authorization", "")
            if auth.startswith("Bearer "):
                payload = jwt.decode(
                    auth[7:],
                    settings.SECRET_KEY,
                    algorithms=[ALGORITHM],
                    options={"verify_exp": False},
                )
                user_id = payload.get("sub")
        except Exception:
            pass

        logger.info(
            json.dumps({
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": elapsed_ms,
                "user_id": user_id,
            })
        )
        return response


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Structured request logging (add before CORS so it wraps everything)
app.add_middleware(StructuredLoggingMiddleware)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
