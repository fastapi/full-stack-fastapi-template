from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Message, NewPassword, Token, UserPublic
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login.
    
    This endpoint authenticates a user and returns an access token for future requests.
    
    Parameters:
    - **username**: Required. The user's email address
    - **password**: Required. The user's password
    
    Returns an access token that should be included in the Authorization header
    of subsequent requests as a Bearer token.
    
    Example:
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    
    Raises:
    - 400: If the email or password is incorrect
    - 400: If the user account is inactive
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token validity.
    
    This endpoint verifies that the provided access token is valid and returns
    the user's profile information.
    
    Returns the user profile associated with the provided token.
    
    Note: This endpoint can be used to validate tokens or to retrieve the current
    user's information.
    """
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Initiate password recovery process.
    
    This endpoint sends a password recovery email to the specified email address
    if it belongs to a registered user.
    
    Parameters:
    - **email**: Required. The email address of the user requesting password recovery
    
    Returns a message indicating that the recovery email has been sent.
    
    Note: For security reasons, the same success message is returned even if the
    email doesn't exist in the system.
    """
    user = crud.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset user password using a token.
    
    This endpoint allows users to set a new password using a token received via email.
    
    Parameters:
    - **token**: Required. The password reset token received via email
    - **new_password**: Required. The new password to set
    
    Returns a success message if the password was updated successfully.
    
    Raises:
    - 400: If the token is invalid
    - 404: If the user associated with the token doesn't exist
    - 400: If the user account is inactive
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    Get HTML content for password recovery email.
    
    This endpoint generates and returns the HTML content that would be sent in a
    password recovery email. This is primarily for testing and debugging purposes.
    
    Parameters:
    - **email**: Required. The email address of the user
    
    Returns the HTML content of the password recovery email.
    
    Note: This endpoint is restricted to superusers only.
    """
    user = crud.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
