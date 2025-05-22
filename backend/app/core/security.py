"""
Security utilities for authentication and authorization.

This module provides functions for password hashing, JWT token generation and verification,
and user authentication utilities.
"""
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union, Dict, List

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jose import JWTError, jwt as jose_jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session, select

from app.core.config import settings
from app.core.logging import logger
from app.db import get_db, get_async_db
from app.models import TokenPayload, User, UserRole

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scopes={
        "me": "Read information about the current user.",
        "users:read": "Read user information.",
        "users:write": "Create and update users.",
        "users:delete": "Delete users.",
        "admin": "Admin access.",
    },
    auto_error=False,
)

# JWT token types
class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"
    VERIFY_EMAIL = "verify_email"

def create_token(
    subject: Union[str, Any],
    token_type: str,
    expires_delta: Optional[timedelta] = None,
    data: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a JWT token.

    Args:
        subject: The subject of the token (usually user ID)
        token_type: Type of token (access, refresh, reset_password, verify_email)
        expires_delta: Optional timedelta for token expiration
        data: Additional data to include in the token

    Returns:
        str: Encoded JWT token
    """
    now = datetime.now(timezone.utc)
    
    # Set default expiration based on token type
    if expires_delta is None:
        if token_type == TokenType.ACCESS:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        elif token_type == TokenType.REFRESH:
            expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        elif token_type == TokenType.RESET_PASSWORD:
            expires_delta = timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        else:  # VERIFY_EMAIL and others
            expires_delta = timedelta(days=1)
    
    expire = now + expires_delta
    
    # Prepare token data
    to_encode = {
        "exp": expire,
        "iat": now,
        "sub": str(subject),
        "type": token_type,
        "jti": secrets.token_urlsafe(16),  # Unique token identifier
    }
    
    # Add additional data if provided
    if data:
        to_encode.update(data)
    
    # Encode and return the token
    encoded_jwt = jose_jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return encoded_jwt


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    scopes: Optional[List[str]] = None,
    **data: Any,
) -> str:
    """
    Create an access token.

    Args:
        subject: The subject of the token (usually user ID)
        expires_delta: Optional timedelta for token expiration
        scopes: List of scopes for the token
        **data: Additional data to include in the token

    Returns:
        str: Encoded JWT access token
    """
    token_data = {}
    if scopes:
        token_data["scopes"] = scopes
    if data:
        token_data.update(data)
    
    return create_token(
        subject=subject,
        token_type=TokenType.ACCESS,
        expires_delta=expires_delta,
        data=token_data,
    )

def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    **data: Any,
) -> str:
    """
    Create a refresh token.

    Args:
        subject: The subject of the token (usually user ID)
        expires_delta: Optional timedelta for token expiration
        **data: Additional data to include in the token

    Returns:
        str: Encoded JWT refresh token
    """
    return create_token(
        subject=subject,
        token_type=TokenType.REFRESH,
        expires_delta=expires_delta,
        data=data,
    )


def create_password_reset_token(email: str) -> str:
    """
    Create a password reset token.

    Args:
        email: User's email address

    Returns:
        str: Encoded JWT password reset token
    """
    return create_token(
        subject=email,
        token_type=TokenType.RESET_PASSWORD,
        expires_delta=timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS),
    )


def create_email_verification_token(email: str) -> str:
    """
    Create an email verification token.

    Args:
        email: User's email address

    Returns:
        str: Encoded JWT email verification token
    """
    return create_token(
        subject=email,
        token_type=TokenType.VERIFY_EMAIL,
        expires_delta=timedelta(days=7),  # 7 days to verify email
    )


def verify_token(
    token: str,
    token_type: Optional[str] = None,
    expected_subject: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Verify a JWT token and return its payload.

    Args:
        token: The JWT token to verify
        token_type: Expected token type (access, refresh, etc.)
        expected_subject: Expected subject (user ID or email)

    Returns:
        Dict[str, Any]: Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jose_jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
        
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
            
        # Verify token type if specified
        if token_type and payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Verify subject if expected_subject is provided
        if expected_subject and str(subject) != str(expected_subject):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return payload
        
    except jose_jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jose_jwt.JWTError, ValidationError):
        raise credentials_exception

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: The plain text password
        hashed_password: The hashed password

    Returns:
        bool: True if the password matches, False otherwise
    """
    if not plain_password or not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a password hash.

    Args:
        password: The plain text password

    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def generate_password() -> str:
    """
    Generate a random password.

    Returns:
        str: A random password
    """
    # Generate a random password with letters, digits, and special characters
    import random
    import string
    
    length = 12
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))


def check_password_strength(password: str) -> dict:
    """
    Check the strength of a password.

    Args:
        password: The password to check

    Returns:
        dict: A dictionary with password strength information
    """
    import re
    
    # Initialize result
    result = {
        'length': len(password) >= 8,
        'has_uppercase': bool(re.search(r'[A-Z]', password)),
        'has_lowercase': bool(re.search(r'[a-z]', password)),
        'has_digit': bool(re.search(r'[0-9]', password)),
        'has_special': bool(re.search(r'[^A-Za-z0-9]', password)),
        'is_strong': True,
    }
    
    # Check if all conditions are met
    result['is_strong'] = all([
        result['length'],
        result['has_uppercase'],
        result['has_lowercase'],
        result['has_digit'],
        result['has_special'],
    ])
    
    return result

async def get_current_user(
    security_scopes: SecurityScopes,
    db: AsyncSession = Depends(get_async_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Get the current user from the JWT token.

    Args:
        security_scopes: Security scopes required for the endpoint
        db: Database session
        token: JWT token from the Authorization header

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: If the token is invalid or user not found
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope=\"{security_scopes.scope_str}\"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    # Verify the token
    try:
        payload = verify_token(token, TokenType.ACCESS)
        token_data = TokenPayload(**payload)
        
        # Get user from database
        result = await db.execute(select(User).where(User.id == token_data.sub))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise credentials_exception
            
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
            
        # Check scopes
        if security_scopes.scopes:
            token_scopes = payload.get("scopes", [])
            for scope in security_scopes.scopes:
                if scope not in token_scopes:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Not enough permissions",
                        headers={"WWW-Authenticate": authenticate_value},
                    )
        
        return user
        
    except (jose_jwt.JWTError, ValidationError) as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise credentials_exception from e


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active user.

    Args:
        current_user: The current authenticated user

    Returns:
        User: The active user

    Raises:
        HTTPException: If the user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active superuser.

    Args:
        current_user: The current authenticated user

    Returns:
        User: The superuser

    Raises:
        HTTPException: If the user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


def generate_token_response(
    user: User,
    access_token_expires: Optional[timedelta] = None,
    refresh_token_expires: Optional[timedelta] = None,
) -> dict:
    """
    Generate access and refresh tokens for a user.

    Args:
        user: The user to generate tokens for
        access_token_expires: Optional expiration time for access token
        refresh_token_expires: Optional expiration time for refresh token

    Returns:
        dict: Dictionary containing access and refresh tokens
    """
    # Define user scopes based on role
    scopes = ["me"]
    if user.is_superuser:
        scopes.extend(["users:read", "users:write", "users:delete", "admin"])
    
    # Create tokens
    access_token = create_access_token(
        subject=str(user.id),
        scopes=scopes,
        expires_delta=access_token_expires,
        is_superuser=user.is_superuser,
        email=user.email,
    )
    
    refresh_token = create_refresh_token(
        subject=str(user.id),
        expires_delta=refresh_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "expires_in": (
            access_token_expires.total_seconds()
            if access_token_expires
            else settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
    }

async def verify_refresh_token(
    token: str, db: AsyncSession = Depends(get_async_db)
) -> User:
    """
    Verify a refresh token and return the associated user.

    Args:
        token: The refresh token to verify
        db: Database session

    Returns:
        User: The user associated with the refresh token

    Raises:
        HTTPException: If the token is invalid or user not found
    """
    try:
        payload = verify_token(token, TokenType.REFRESH)
        token_data = TokenPayload(**payload)
        
        # Get user from database
        result = await db.execute(select(User).where(User.id == token_data.sub))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
            
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
            
        return user
        
    except (jose_jwt.JWTError, ValidationError) as e:
        logger.error(f"Refresh token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from e


def get_authorization_scheme_param(authorization_header_value: str) -> tuple[str, str]:
    """
    Parse the authorization header and return the scheme and token.

    Args:
        authorization_header_value: The value of the Authorization header

    Returns:
        tuple: A tuple of (scheme, token)
    """
    if not authorization_header_value:
        return "", ""
    
    parts = authorization_header_value.split()
    if len(parts) != 2:
        return "", ""
        
    scheme, token = parts
    return scheme, token


def get_token_from_request(request: Request) -> Optional[str]:
    """
    Extract token from request headers or cookies.

    Args:
        request: The incoming request

    Returns:
        Optional[str]: The token if found, None otherwise
    """
    # Try to get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header:
        scheme, token = get_authorization_scheme_param(auth_header)
        if scheme.lower() == "bearer":
            return token
    
    # Try to get token from cookie
    token = request.cookies.get("access_token")
    if token:
        return token
    
    return None


def get_current_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise return None.
    
    This is useful for endpoints that work for both authenticated and unauthenticated users.
    
    Args:
        request: The incoming request
        db: Database session

    Returns:
        Optional[User]: The current user if authenticated, None otherwise
    """
    token = get_token_from_request(request)
    if not token:
        return None
    
    try:
        payload = verify_token(token, TokenType.ACCESS)
        token_data = TokenPayload(**payload)
        
        # Get user from database
        result = db.execute(select(User).where(User.id == token_data.sub))
        user = result.scalar_one_or_none()
        
        if user is None or not user.is_active:
            return None
            
        return user
        
    except (jose_jwt.JWTError, ValidationError):
        return None
