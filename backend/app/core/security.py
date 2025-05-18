"""
Security utilities.

This module provides utilities for handling passwords, JWT tokens, and other
security-related functionality.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.logging import get_logger

# Configure logger
logger = get_logger("security")

# Password hash configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(
    subject: str | Any, 
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Subject of the token (usually user ID)
        expires_delta: Token expiration time (default from settings)
        extra_claims: Additional claims to include in the token
        
    Returns:
        Encoded JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    expire = datetime.now(timezone.utc) + expires_delta
    
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Add any extra claims
    if extra_claims:
        to_encode.update(extra_claims)
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating JWT token: {e}")
        raise


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary of decoded token claims
        
    Raises:
        jwt.PyJWTError: If token validation fails
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as e:
        logger.warning(f"JWT token validation failed: {e}")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches hash, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token.
    
    Args:
        email: User email address
        
    Returns:
        Encoded JWT token for password reset
    """
    expires = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    return create_access_token(
        subject=email, 
        expires_delta=expires,
        extra_claims={"purpose": "password_reset"}
    )


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token.
    
    Args:
        token: Password reset token
        
    Returns:
        Email address if token is valid, None otherwise
    """
    try:
        decoded_token = decode_access_token(token)
        # Verify token purpose
        if decoded_token.get("purpose") != "password_reset":
            return None
        return decoded_token["sub"]
    except jwt.PyJWTError:
        return None