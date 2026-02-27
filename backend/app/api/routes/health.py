"""Operational endpoints: health, readiness, and version.

These endpoints are public (no authentication required) and are used by
container orchestrators for liveness/readiness probes and by API gateways
for service registration and discovery.
"""

from __future__ import annotations

import anyio
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(module=__name__)

router = APIRouter(tags=["operations"])


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    """Liveness probe — returns 200 immediately with no dependency checks."""
    return {"status": "ok"}


def _check_supabase(request: Request) -> str:
    """Check Supabase connectivity via a lightweight PostgREST HEAD request.

    Returns ``"ok"`` if the server is reachable (even if the probe table does
    not exist) or ``"error"`` if the connection cannot be established.
    """
    try:
        client = request.app.state.supabase
        client.table("_health_check").select("*", head=True).execute()
        return "ok"
    except APIError:
        # PostgREST returned an HTTP error (e.g. table not found).
        # The server IS reachable — the check passes.
        return "ok"
    except AttributeError:
        logger.error("supabase_client_not_initialized", check="supabase")
        return "error"
    except Exception as exc:
        logger.warning(
            "readiness_check_failed",
            check="supabase",
            error_type=type(exc).__name__,
        )
        return "error"


@router.get("/readyz")
async def readyz(request: Request) -> JSONResponse:
    """Readiness probe — checks Supabase connectivity."""
    supabase_status = await anyio.to_thread.run_sync(lambda: _check_supabase(request))
    is_ready = supabase_status == "ok"
    return JSONResponse(
        status_code=200 if is_ready else 503,
        content={
            "status": "ready" if is_ready else "not_ready",
            "checks": {"supabase": supabase_status},
        },
    )


@router.get("/version")
async def version() -> dict[str, str]:
    """Build metadata from environment variables for gateway discoverability."""
    return {
        "service_name": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "commit": settings.GIT_COMMIT,
        "build_time": settings.BUILD_TIME,
        "environment": settings.ENVIRONMENT,
    }
