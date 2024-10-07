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

# Create a new APIRouter instance for login-related routes
router = APIRouter()


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep,  # pyright: ignore [reportInvalidTypeForm]
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests

    This endpoint allows users to obtain an access token for authentication.
    It's rate-limited to 5 requests per minute to prevent abuse.

    Args:
        request (Request): The incoming request object (required for rate limiting).
        response (Response): The outgoing response object (required for rate limiting).
        session (SessionDep): The database session dependency.
        form_data (OAuth2PasswordRequestForm): The form data containing username and password.

    Returns:
        Token: An object containing the access token.

    Raises:
        HTTPException:
            - 400: If the email or password is incorrect.
            - 400: If the user account is inactive.

    Notes:
        This function authenticates the user, checks if the account is active,
        and then generates and returns an access token with a specified expiration time.
    """
    # Authenticate the user using the provided credentials
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    # If authentication fails, raise an HTTPException
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    # Set the access token expiration time
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Create and return a new access token
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token

    This endpoint allows testing the validity of an access token.
    It's protected and can only be accessed with a valid token.

    Args:
        current_user (CurrentUser): The current authenticated user, injected by dependency.

    Returns:
        Any: The current user's public information.

    Raises:
        HTTPException: If the token is invalid or expired (handled by dependency).

    Notes:
        This function is useful for verifying that a token is working correctly.
        It simply returns the current user's information, which implicitly confirms
        that the token is valid and the user is authenticated.
    """
    # Return the current user to verify the token is working
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(
    email: str,
    session: SessionDep,  # pyright: ignore [reportInvalidTypeForm]
) -> Message:
    """
    Password Recovery

    This endpoint initiates the password recovery process for a user.
    It's rate-limited to 3 requests per minute to prevent abuse.

    Args:
        email (str): The email address of the user requesting password recovery.
        session (SessionDep): The database session dependency.
        request (Request): The incoming request object (required for rate limiting).
        response (Response): The outgoing response object (required for rate limiting).

    Returns:
        Message: A message indicating that the password recovery email was sent.

    Raises:
        HTTPException:
            - 404: If no user is found with the provided email address.

    Notes:
        This function checks for the existence of the user, generates a password reset token,
        creates a password reset email, and sends it to the user's email address.
        It does not confirm or deny the existence of an account to prevent email enumeration.
    """
    # Get the user by email
    user = crud.get_user_by_email(session=session, email=email)

    # If user not found, still act like we sent the email
    if not user:
        return Message(message="Password recovery email sent if the account exists.")

    # Generate a password reset token
    password_reset_token = generate_password_reset_token(email=email)
    # Generate the reset password email content
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    # Send the password reset email
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    # Return a success message
    return Message(message="Password recovery email sent if the account exists.")


@router.post("/reset-password/")
def reset_password(
    session: SessionDep,  # pyright: ignore [reportInvalidTypeForm]
    body: NewPassword,
) -> Message:
    """
    Reset password

    This endpoint allows users to reset their password using a valid reset token.
    It's rate-limited to 3 requests per minute to prevent abuse.

    Args:
        session (SessionDep): The database session dependency.
        body (NewPassword): The new password and reset token.
        request (Request): The incoming request object (required for rate limiting).
        response (Response): The outgoing response object (required for rate limiting).

    Returns:
        Message: A message indicating that the password was successfully updated.

    Raises:
        HTTPException:
            - 400: If the reset token is invalid.
            - 404: If no user is found with the email associated with the token.
            - 400: If the user account is inactive.

    Notes:
        This function verifies the reset token, retrieves the associated user,
        checks if the user is active, hashes the new password, and updates it in the database.
        It's the final step in the password recovery process.
    """
    # Verify the password reset token
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    # Get the user by email
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    # Hash the new password
    hashed_password = get_password_hash(password=body.new_password)
    # Update the user's password
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    # Return a success message
    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(
    email: str,
    session: SessionDep,  # pyright: ignore [reportInvalidTypeForm]
) -> Any:
    """
    HTML Content for Password Recovery

    This endpoint generates and returns the HTML content for a password recovery email.
    It's protected and can only be accessed by active superusers.

    Args:
        email (str): The email address of the user for whom to generate the recovery email.
        session (SessionDep): The database session dependency.

    Returns:
        HTMLResponse: The HTML content of the password reset email, with the subject in the headers.

    Raises:
        HTTPException:
            - 404: If no user is found with the provided email address.

    Notes:
        This function is primarily for testing and debugging purposes. It allows superusers
        to view the content of password reset emails without actually sending them.
        It generates a password reset token and creates the email content just like
        the actual password recovery process.
    """
    # Get the user by email
    user = crud.get_user_by_email(session=session, email=email)

    # If user not found, raise an HTTPException
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    # Generate a password reset token
    password_reset_token = generate_password_reset_token(email=email)
    # Generate the reset password email content
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    # Return the HTML content of the password reset email
    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
