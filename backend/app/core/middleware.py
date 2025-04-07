import logging
from typing import Callable, List

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)

def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS for the application - must be called before app startup.
    """
    origins = settings.all_cors_origins
    
    logger.info(f"Setting up CORS middleware with origins: {origins}")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
        max_age=3600,
    )
    
    logger.info("CORS middleware configured")
