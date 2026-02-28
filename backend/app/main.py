from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.http_client import HttpClient
from app.core.logging import get_logger, setup_logging
from app.core.middleware import RequestPipelineMiddleware
from app.core.supabase import create_supabase_client

# Configure structured logging (JSON in production, console in local dev)
setup_logging(settings)

logger = get_logger(module=__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan: initialise shared resources on startup, clean up on shutdown."""
    # Startup
    app.state.supabase = create_supabase_client(
        url=str(settings.SUPABASE_URL),
        key=settings.SUPABASE_SERVICE_KEY.get_secret_value(),
    )
    app.state.http_client = HttpClient(
        read_timeout=float(settings.HTTP_CLIENT_TIMEOUT),
        max_retries=settings.HTTP_CLIENT_MAX_RETRIES,
    )
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=str(settings.SENTRY_DSN),
            integrations=[
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
            ],
            enable_tracing=True,
            traces_sample_rate=0.1,
            send_default_pii=False,
            environment=settings.ENVIRONMENT,
        )
    logger.info(
        "app_startup",
        service_name=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION,
        environment=settings.ENVIRONMENT,
    )

    yield

    # Shutdown — order: log event, close http client, flush Sentry (AC-10)
    logger.info(
        "app_shutdown",
        service_name=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION,
        environment=settings.ENVIRONMENT,
    )
    try:
        await app.state.http_client.close()
    except Exception:
        logger.exception("http_client_close_failed")
    sentry_sdk.flush(timeout=2.0)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.SERVICE_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
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

# Operational endpoints at root level (no API prefix) — public, no auth required.
app.include_router(health_router)
