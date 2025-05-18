"""
Centralized logging configuration for the application.

This module provides a consistent logging setup across all modules.
"""
import logging
import sys
from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from app.core.config import settings


class LogConfig(BaseModel):
    """Configuration for application logging."""
    
    LOGGER_NAME: str = "app"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(module)s | %(message)s"
    LOG_LEVEL: str = "INFO"
    
    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: Dict[str, Dict[str, str]] = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: Dict[str, Dict[str, Any]] = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers: Dict[str, Dict[str, Any]] = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }


def get_logger(name: str) -> logging.Logger:
    """
    Get a module-specific logger.
    
    Args:
        name: Module name for the logger
        
    Returns:
        Logger instance
    """
    logger_name = f"{LogConfig().LOGGER_NAME}.{name}"
    return logging.getLogger(logger_name)


def setup_logging(app: Optional[FastAPI] = None) -> None:
    """
    Configure logging for the application.
    
    Args:
        app: FastAPI application (optional)
    """
    # Set log level from settings
    log_config = LogConfig()
    log_config.LOG_LEVEL = settings.LOG_LEVEL
    
    # Configure logging
    import logging.config
    logging.config.dictConfig(log_config.dict())
    
    # Add startup and shutdown event handlers if app is provided
    if app:
        @app.on_event("startup")
        async def startup_logging_event():
            root_logger = logging.getLogger()
            root_logger.info(f"Application starting up in {settings.ENVIRONMENT} environment")
            
        @app.on_event("shutdown")
        async def shutdown_logging_event():
            root_logger = logging.getLogger()
            root_logger.info("Application shutting down")


def get_module_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        module_name: Name of the module
        
    Returns:
        Module-specific logger
    """
    return get_logger(module_name)