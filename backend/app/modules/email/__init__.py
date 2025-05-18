"""
Email module initialization.

This module handles email operations.
"""
from fastapi import APIRouter, FastAPI

from app.core.config import settings
from app.core.logging import get_logger
from app.modules.email.api.routes import router as email_router

# Import event handlers to register them
from app.modules.email.services import email_event_handlers

# Configure logger
logger = get_logger("email_module")


def get_email_router() -> APIRouter:
    """
    Get the email module's router.

    Returns:
        APIRouter for email module
    """
    return email_router


def init_email_module(app: FastAPI) -> None:
    """
    Initialize the email module.

    This function sets up routes and event handlers for the email module.

    Args:
        app: FastAPI application
    """
    # Include the email router in the application
    app.include_router(email_router, prefix=settings.API_V1_STR)

    # Set up any event handlers or startup tasks for the email module
    @app.on_event("startup")
    async def init_email():
        """Initialize email module on application startup."""
        # Log email service status
        if settings.emails_enabled:
            logger.info("Email module initialized with SMTP connection")
            logger.info(f"SMTP Host: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
            logger.info(f"From: {settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>")
        else:
            logger.warning("Email module initialized but sending is disabled")
            logger.warning("To enable, configure SMTP settings in environment variables")

        # Log event handlers registration
        logger.info("Email event handlers registered for: user.created")