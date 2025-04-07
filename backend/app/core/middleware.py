import logging
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp

from app.core.config import settings

logger = logging.getLogger(__name__)


class CustomCORSMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        super().__init__(app)
        self.allowed_origins = settings.all_cors_origins
        logger.info(f"Configured CORS origins: {self.allowed_origins}")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        origin = request.headers.get("origin", "")
        logger.info(f"Request from origin: {origin}")
        
        # Handle preflight OPTIONS requests explicitly
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            self._set_cors_headers(response, origin)
            return response
            
        # For all other requests, continue with normal processing
        response = await call_next(request)
        
        # Add CORS headers to response
        self._set_cors_headers(response, origin)
        
        return response
    
    def _set_cors_headers(self, response: Response, origin: str) -> None:
        if not origin:
            return
            
        # Force add origin if in production environment
        if settings.ENVIRONMENT != "local" and origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept"
            response.headers["Access-Control-Max-Age"] = "3600"
            logger.info(f"Added CORS headers for origin: {origin}")
        elif origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept"
            response.headers["Access-Control-Max-Age"] = "3600"
            logger.info(f"Added CORS headers for origin: {origin}")
        else:
            logger.warning(f"Origin not allowed: {origin}")


def setup_cors(app: FastAPI) -> None:
    """Configure CORS for the application."""
    
    # Remove any existing CORS middleware
    app.middleware_stack = app.build_middleware_stack()
    
    # Add our custom CORS middleware
    app.add_middleware(CustomCORSMiddleware)
    
    logger.info("Custom CORS middleware configured")
