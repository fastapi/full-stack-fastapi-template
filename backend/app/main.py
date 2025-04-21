import time
from datetime import datetime
import sentry_sdk
from fastapi import FastAPI, Depends
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.main import api_router
from app.core.config import settings
from app.db.session import async_session  # Make sure this import exists

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# --- Enhanced Health Check ---
async def check_db_health() -> dict:
    """Test database connectivity with latency measurement"""
    start_time = time.monotonic()
    try:
        async with async_session() as db:
            await db.execute("SELECT 1")
            return {
                "status": "ok",
                "latency_ms": int((time.monotonic() - start_time) * 1000)
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/health", tags=["health"], include_in_schema=False)  # Hidden from docs
async def health_check(verbose: bool = False):
    """Enhanced health endpoint with system diagnostics"""
    db_status = await check_db_health()
    
    response = {
        "status": "ok" if db_status["status"] == "ok" else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if verbose or db_status["status"] != "ok":
        response["details"] = {
            "database": db_status,
            # Add other checks here (redis, storage, etc.)
        }
    
    return response
# --- End Health Check ---

# Existing CORS setup
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)