from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Create a password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define the algorithm used for JWT encoding and decoding
ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """
    Create an access token for the given subject with an expiration time.

    This function creates a JWT access token for the given subject with the specified expiration time.
    It's not protected and can be used by any part of the application that needs to generate access tokens.

    Args:
        subject (str | Any): The subject of the token, typically a user identifier.
        expires_delta (timedelta): The time delta after which the token will expire.

    Returns:
        str: The encoded JWT access token.

    Raises:
        None

    Notes:
        Uses the SECRET_KEY from settings and the ALGORITHM constant for encoding.
    """
    # Calculate the expiration time
    expire = datetime.now(timezone.utc) + expires_delta
    # Create a payload with expiration time and subject
    to_encode = {"exp": expire, "sub": str(subject)}
    # Encode the payload into a JWT
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the plain password matches the hashed password.

    This function checks if a given plain text password matches a hashed password.
    It's not protected and can be used by any part of the application that needs to verify passwords.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.

    Raises:
        None

    Notes:
        Uses the pwd_context for password verification.
    """
    # Use the password context to verify the plain password against the hashed password
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Get the hash of the given password.

    This function generates a hash for a given plain text password.
    It's not protected and can be used by any part of the application that needs to hash passwords.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.

    Raises:
        None

    Notes:
        Uses the pwd_context for password hashing.
    """
    # Use the password context to hash the given password
    return pwd_context.hash(password)
