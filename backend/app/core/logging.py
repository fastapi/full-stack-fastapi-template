"""
Logging configuration for the application.
"""
import logging
import logging.config
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings


class LoggingSettings(BaseSettings):
    """Logging settings."""
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    LOG_FILE: Optional[Path] = Field(None, env="LOG_FILE")
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "30 days"
    LOG_COMPRESSION: str = "zip"


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    log_format: Optional[str] = None,
    log_rotation: Optional[str] = None,
    log_retention: Optional[str] = None,
    log_compression: Optional[str] = None,
) -> logger:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file
        log_format: Log message format
        log_rotation: Log rotation configuration
        log_retention: Log retention configuration
        log_compression: Log compression configuration

    Returns:
        logger: Configured logger instance
    """
    # Get logging settings
    settings = LoggingSettings()
    
    # Apply overrides
    log_level = log_level or settings.LOG_LEVEL
    log_file = log_file or settings.LOG_FILE
    log_format = log_format or settings.LOG_FORMAT
    log_rotation = log_rotation or settings.LOG_ROTATION
    log_retention = log_retention or settings.LOG_RETENTION
    log_compression = log_compression or settings.LOG_COMPRESSION
    
    # Configure loguru logger
    logger.remove()  # Remove default handler
    
    # Add console handler
    logger.add(
        sys.stderr,
        level=log_level,
        format=log_format,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # Add file handler if log file is specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_file),
            level=log_level,
            format=log_format,
            rotation=log_rotation,
            retention=log_retention,
            compression=log_compression,
            backtrace=True,
            diagnose=True,
        )
    
    # Configure standard library logging to use loguru
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = sys._getframe(6), 6
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    # Set up logging to use loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Disable noisy loggers
    for name in [
        "asyncio",
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "sqlalchemy.engine",
    ]:
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = False
    
    # Set log level for SQLAlchemy
    logging.getLogger("sqlalchemy.engine").setLevel("WARNING")
    
    return logger


# Create a default logger instance
logger = setup_logging()
