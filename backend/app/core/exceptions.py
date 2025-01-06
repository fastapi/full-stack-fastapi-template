import logging

from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    """Catch all exceptions and log, do not expose to the client"""
    logger.error(f"exception_handler: {exc}")
    return JSONResponse(status_code=500, content="something went wrong")
