import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
from app.api.main import api_router
from app.config import settings
from app.models.prompts_schemas import HealthResponse
from app.core import db

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    logger.info(f"🚀 Starting application in {settings.environment.upper()} mode")
    logger.info(f"Database: {settings.pg_host}/{settings.pg_database}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info("Starting up - initializing database...")

    await db.init_db()
    logger.info("Database initialized successfully")

    yield
    logger.info("Shutting down...")


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


"""
if settings.SENTRY_DSN and settings.environment != "development":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)
"""


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    # generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan
)


# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"{settings.app_name} API - Ready",
        "environment": settings.environment,
        "version": settings.app_version
    }


@app.get("/config")
async def show_config():
    """Show current configuration (for debugging - remove in production!)"""
    if not settings.debug:
        return {"error": "Config endpoint disabled in production"}

    return {
        "environment": settings.environment,
        "debug": settings.debug,
        "database": {
            "host": settings.pg_host,
            "database": settings.pg_database,
            "pool_size": settings.pg_pool_size
        },
        "ai_model": settings.ai_model,
        "log_level": settings.log_level,
        "rate_limit_enabled": settings.rate_limit_enabled
    }
