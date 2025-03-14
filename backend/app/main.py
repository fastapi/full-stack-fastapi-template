import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router as api_v1_router
from app.core.config import settings
from app.core.errors import add_exception_handlers
from app.schemas import StandardResponse


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate a unique ID for API routes to improve Swagger documentation."""
    if route.tags and len(route.tags) > 0:
        return f"{route.tags[0]}-{route.name}"
    else:
        return f"root-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI Backend Template",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Add exception handlers
add_exception_handlers(app)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include the v1 API router directly with the version prefix
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/", response_model=StandardResponse[dict])
async def root():
    """Root endpoint providing basic API information."""
    return StandardResponse(
        data={"message": "Welcome to the FastAPI Backend Template"},
        message="API is running"
    )

@app.get("/health", response_model=StandardResponse[dict])
async def health_check():
    """Health check endpoint for monitoring."""
    return StandardResponse(
        data={"status": "healthy"},
        message="API is healthy"
    )
