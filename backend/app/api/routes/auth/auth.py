from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.db import get_db
from app.models import User
from app.schemas.auth import Token, UserLogin, UserRegister, UserOut, PasswordResetRequest, PasswordResetConfirm
from app.crud import create_user, get_user, get_user_by_email, update_user

router = APIRouter()

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(
    *,
    db: Session = Depends(get_db),
    user_in: UserRegister,
) -> Any:
    """
    Create new user with email and password.
    """
    # Check if user with this email already exists
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    
    # Create new user
    user = create_user(db, user_in)
    
    # TODO: Send verification email
    
    return user

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Authenticate user
    user = security.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Generate tokens
    tokens = security.generate_token_response(str(user.id))
    
    # Store refresh token in database
    # TODO: Implement refresh token storage
    
    return tokens

@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    Refresh access token using a valid refresh token.
    """
    # Verify refresh token
    try:
        token_data = security.verify_refresh_token(refresh_token)
    except HTTPException as e:
        raise e
    
    # Get user
    user = get_user(session=db, user_id=token_data["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Generate new tokens
    tokens = security.generate_token_response(str(user.id))
    
    # TODO: Update refresh token in database
    
    return tokens

@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
def forgot_password(
    password_reset: PasswordResetRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    Request password reset.
    """
    user = get_user_by_email(db, email=password_reset.email)
    if not user:
        # Don't reveal that the user doesn't exist
        return {"message": "If your email is registered, you will receive a password reset link."}
    
    # TODO: Generate password reset token and send email
    
    return {"message": "If your email is registered, you will receive a password reset link."}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db),
) -> Any:
    """
    Reset password using a valid token.
    """
    # TODO: Verify reset token
    # TODO: Update user password
    
    return {"message": "Password updated successfully"}

@router.get("/me", response_model=UserOut)
def read_users_me(
    current_user: User = Depends(security.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user
