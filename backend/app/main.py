"""
Application entry point.

This module creates and configures the FastAPI application.
"""
import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import init_api_routes
from app.core.config import settings
from app.core.logging import setup_logging


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Generate a unique ID for API routes.
    
    Args:
        route: API route
        
    Returns:
        Unique ID for the route
    """
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    # Initialize Sentry if configured and not in local environment
    if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
        sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)
    
    # Create application
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=custom_generate_unique_id,
    )
    
    # Set up logging
    setup_logging(application)
    
    # Set all CORS enabled origins
    if settings.all_cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=settings.all_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Initialize API routes
    init_api_routes(application)
    
    return application


# Create the application instance
app = create_application()