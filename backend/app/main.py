import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Generate unique IDs for API routes.

    Creates a unique identifier for each API route by combining the route's tag and name.

    Args:
        route: The APIRoute object for which to generate a unique ID.

    Returns:
        A string representing the unique ID for the given route.

    Notes:
        This function is used as a custom generator for FastAPI's route IDs.
    """
    return f"{route.tags[0]}-{route.name}"


# Initialize Sentry for error tracking if DSN is provided and not in local environment
if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

# Create FastAPI application instance with custom settings
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    version="v1",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set up CORS middleware if origins are specified in settings
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include the main API router with the specified prefix
app.include_router(api_router, prefix=settings.API_V1_STR)
