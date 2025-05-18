"""
Email routes.

This module provides API routes for email operations.
"""
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import EmailStr

from app.api.deps import CurrentSuperuser
from app.core.config import settings
from app.core.logging import get_logger
from app.models import Message  # Temporary import until Message is moved to shared
from app.modules.email.dependencies import get_email_service
from app.modules.email.domain.models import EmailRequest, TemplateData, EmailTemplateType
from app.modules.email.services.email_service import EmailService

# Configure logger
logger = get_logger("email_routes")

# Create router
router = APIRouter(prefix="/email", tags=["email"])


@router.post("/test", response_model=Message)
def test_email(
    email_to: EmailStr,
    background_tasks: BackgroundTasks,
    current_user: CurrentSuperuser = Depends(),
    email_service: EmailService = Depends(get_email_service),
) -> Any:
    """
    Test email sending.
    
    Args:
        email_to: Recipient email address
        background_tasks: Background tasks
        current_user: Current superuser
        email_service: Email service
        
    Returns:
        Success message
    """
    if not settings.emails_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sending is not configured",
        )
    
    # Send email in the background
    background_tasks.add_task(email_service.send_test_email, email_to)
    
    return Message(message="Test email sent in the background")


@router.post("/", response_model=Message)
def send_email(
    email_request: EmailRequest,
    background_tasks: BackgroundTasks,
    current_user: CurrentSuperuser = Depends(),
    email_service: EmailService = Depends(get_email_service),
) -> Any:
    """
    Send email.
    
    Args:
        email_request: Email request data
        background_tasks: Background tasks
        current_user: Current superuser
        email_service: Email service
        
    Returns:
        Success message
    """
    if not settings.emails_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sending is not configured",
        )
    
    # Send email in the background
    background_tasks.add_task(email_service.send_email, email_request)
    
    return Message(message="Email sent in the background")


@router.post("/template", response_model=Message)
def send_template_email(
    template_data: TemplateData,
    background_tasks: BackgroundTasks,
    current_user: CurrentSuperuser = Depends(),
    email_service: EmailService = Depends(get_email_service),
) -> Any:
    """
    Send email using a template.
    
    Args:
        template_data: Template data
        background_tasks: Background tasks
        current_user: Current superuser
        email_service: Email service
        
    Returns:
        Success message
    """
    if not settings.emails_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sending is not configured",
        )
    
    # Send email in the background
    background_tasks.add_task(email_service.send_template_email, template_data)
    
    return Message(message="Template email sent in the background")