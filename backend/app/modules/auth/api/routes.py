"""
Auth routes.

This module provides API routes for authentication operations.
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentSuperuser, CurrentUser
from app.core.config import settings
from app.core.logging import get_logger
from app.modules.users.domain.models import UserPublic
from app.shared.models import Message  # Using shared Message model
from app.modules.auth.dependencies import get_auth_service
from app.modules.auth.domain.models import NewPassword, PasswordReset, Token
from app.modules.auth.services.auth_service import AuthService
from app.shared.exceptions import AuthenticationException, NotFoundException

# Initialize logger
logger = get_logger("auth_routes")

# Create router
router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.

    Args:
        form_data: OAuth2 form data
        auth_service: Auth service

    Returns:
        Token object
    """
    try:
        return auth_service.login(
            email=form_data.username, password=form_data.password
        )
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token endpoint.

    Args:
        current_user: Current authenticated user

    Returns:
        User object
    """
    return current_user


@router.post("/password-recovery")
def recover_password(
    body: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service),
) -> Message:
    """
    Password recovery endpoint.

    Args:
        body: Password reset request
        auth_service: Auth service

    Returns:
        Message object
    """
    auth_service.request_password_reset(email=body.email)

    # Always return success to prevent email enumeration
    return Message(message="Password recovery email sent")


@router.post("/reset-password")
def reset_password(
    body: NewPassword,
    auth_service: AuthService = Depends(get_auth_service),
) -> Message:
    """
    Reset password endpoint.

    Args:
        body: New password data
        auth_service: Auth service

    Returns:
        Message object
    """
    try:
        auth_service.reset_password(token=body.token, new_password=body.new_password)
        return Message(message="Password updated successfully")
    except (AuthenticationException, NotFoundException) as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e),
        )


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(CurrentSuperuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(
    email: str,
) -> Any:
    """
    HTML content for password recovery (for testing/debugging).

    This endpoint is only available to superusers and is intended for
    testing and debugging the password recovery email template.

    Args:
        email: User email
        auth_service: Auth service

    Returns:
        HTML content of password recovery email
    """
    from app.modules.email.dependencies import get_email_service
    from app.modules.email.domain.models import TemplateData, EmailTemplateType
    from app.core.security import generate_password_reset_token

    # Generate a dummy token for template preview
    token = generate_password_reset_token(email)

    # Get email service
    email_service = get_email_service()

    # Create template data
    template_data = TemplateData(
        template_type=EmailTemplateType.RESET_PASSWORD,
        context={
            "username": email,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": f"{settings.FRONTEND_HOST}/reset-password?token={token}",
        },
        email_to=email,
    )

    # Get template content
    template_content = email_service.get_template_content(template_data)

    return HTMLResponse(
        content=template_content.html_content,
        headers={"subject": template_content.subject},
    )