"""
Utils routes.

This module provides API routes for utility operations.
"""
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import EmailStr

from app.api.deps import CurrentSuperuser
from app.core.config import settings
from app.core.logging import get_logger
from app.shared.models import Message  # Using shared Message model

# Configure logger
logger = get_logger("utils_routes")

# Create router
router = APIRouter(prefix="/utils", tags=["utils"])


@router.get("/health-check/", response_model=bool)
def health_check() -> Any:
    """
    Health check endpoint.
    
    Returns:
        True if the API is running
    """
    return True


@router.post("/test-email/", response_model=Message)
def test_email(
    current_user: CurrentSuperuser,
    email_to: EmailStr,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Test email sending.
    
    Args:
        email_to: Recipient email address
        background_tasks: Background tasks
        current_user: Current superuser
        
    Returns:
        Success message
    """
    # This endpoint is now handled by the email module
    # Redirect to the email module's test endpoint
    raise HTTPException(
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
        detail="This endpoint has moved to /api/v1/email/test",
        headers={"Location": f"{settings.API_V1_STR}/email/test?email_to={email_to}"},
    )
