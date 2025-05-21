import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings

# OpenTelemetry Imports
import logging
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.trace import set_tracer_provider
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from app.core.db import engine as db_engine # Renamed to avoid conflict with sqlalchemy.engine


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

# Configure OpenTelemetry
def setup_opentelemetry(app: FastAPI):
    logger = logging.getLogger(__name__)
    try:
        SERVICE_NAME = getattr(settings, "SERVICE_NAME", "my-fastapi-app")
        resource = Resource.create({"service.name": SERVICE_NAME})
        
        provider = TracerProvider(resource=resource)
        console_exporter = ConsoleSpanExporter()
        processor = SimpleSpanProcessor(console_exporter)
        provider.add_span_processor(processor)
        set_tracer_provider(provider)
        
        logger.info(f"OpenTelemetry configured for service: {SERVICE_NAME} with ConsoleExporter")
        
        FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
        
        # Ensure db_engine.engine is the actual SQLAlchemy engine
        actual_sqlalchemy_engine = getattr(db_engine, "engine", db_engine)
        if actual_sqlalchemy_engine is None: # Should not happen if db_engine is correctly initialized
             logger.error("SQLAlchemy engine not found for OpenTelemetry instrumentation.")
             return

        SQLAlchemyInstrumentor().instrument(engine=actual_sqlalchemy_engine, tracer_provider=provider)
        logger.info("FastAPI and SQLAlchemy instrumented for OpenTelemetry.")
        
    except Exception as e:
        logger.error(f"Failed to configure OpenTelemetry: {e}", exc_info=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Call OpenTelemetry setup after app creation
setup_opentelemetry(app)

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
