import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestPipelineMiddleware

# Configure structured logging (JSON in production, console in local dev)
setup_logging(settings)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.SERVICE_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Register unified error handlers
register_exception_handlers(app)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Request pipeline middleware: request ID, correlation, security headers, logging.
# Added AFTER CORSMiddleware in code — Starlette adds middleware as a stack
# (last-added = outermost), so this wraps CORS. This ensures security headers
# and X-Request-ID are set on ALL responses, including CORS preflight OPTIONS.
app.add_middleware(RequestPipelineMiddleware, environment=settings.ENVIRONMENT)

app.include_router(api_router, prefix=settings.API_V1_STR)
