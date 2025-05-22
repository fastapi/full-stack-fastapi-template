"""
Utility functions and helpers for the application.

This module contains various utility functions that are used throughout the application
for common tasks such as string manipulation, data validation, and more.
"""
import base64
import hashlib
import json
import logging
import os
import random
import re
import string
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast

import jwt
from fastapi import HTTPException, Request, status
from jose import jwe
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, ValidationError

from app.core.config import settings
from app.core.logging import logger

# Type variable for generic function return type
T = TypeVar('T')

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Email validation regex
EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9]'
    r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
    r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$'
)

# URL validation regex
URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE
)


def generate_uuid() -> str:
    """Generate a UUID4 string.
    
    Returns:
        str: A UUID4 string
    """
    return str(uuid.uuid4())


def generate_random_string(length: int = 32) -> str:
    """Generate a random alphanumeric string of specified length.
    
    Args:
        length: Length of the string to generate (default: 32)
        
    Returns:
        str: A random alphanumeric string
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_random_number(length: int = 6) -> str:
    """Generate a random numeric string of specified length.
    
    Args:
        length: Length of the number to generate (default: 6)
        
    Returns:
        str: A random numeric string
    """
    return ''.join(random.choice(string.digits) for _ in range(length))


def get_timestamp() -> int:
    """Get the current Unix timestamp.
    
    Returns:
        int: Current Unix timestamp in seconds
    """
    return int(time.time())


def get_datetime() -> datetime:
    """Get the current UTC datetime.
    
    Returns:
        datetime: Current UTC datetime
    """
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object as a string.
    
    Args:
        dt: Datetime object to format
        format_str: Format string (default: "%Y-%m-%d %H:%M:%S")
        
    Returns:
        str: Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_datetime(datetime_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse a datetime string into a datetime object.
    
    Args:
        datetime_str: Datetime string to parse
        format_str: Format string (default: "%Y-%m-%d %H:%M:%S")
        
    Returns:
        datetime: Parsed datetime object
        
    Raises:
        ValueError: If the datetime string cannot be parsed
    """
    return datetime.strptime(datetime_str, format_str).replace(tzinfo=timezone.utc)


def is_valid_email(email: str) -> bool:
    """Check if a string is a valid email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if the email is valid, False otherwise
    """
    return bool(EMAIL_REGEX.match(email))


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    return bool(URL_REGEX.match(url))


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    if not plain_password or not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def generate_jwt_token(
    data: dict,
    expires_delta: Optional[int] = None,
    secret_key: Optional[str] = None,
    algorithm: str = "HS256"
) -> str:
    """Generate a JWT token.
    
    Args:
        data: Data to include in the token
        expires_delta: Expiration time in seconds (default: 1 hour)
        secret_key: Secret key for signing the token (default: settings.SECRET_KEY)
        algorithm: Algorithm to use for signing (default: HS256)
        
    Returns:
        str: Encoded JWT token
    """
    secret_key = secret_key or settings.SECRET_KEY
    expires_delta = expires_delta or 3600  # 1 hour default
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def decode_jwt_token(
    token: str,
    secret_key: Optional[str] = None,
    algorithms: List[str] = ["HS256"]
) -> dict:
    """Decode a JWT token.
    
    Args:
        token: JWT token to decode
        secret_key: Secret key used for signing (default: settings.SECRET_KEY)
        algorithms: List of allowed algorithms (default: ["HS256"])
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    secret_key = secret_key or settings.SECRET_KEY
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def encrypt_data(data: Union[dict, str], key: Optional[str] = None) -> str:
    """Encrypt data using JWE.
    
    Args:
        data: Data to encrypt (dict or JSON string)
        key: Encryption key (default: settings.SECRET_KEY)
        
    Returns:
        str: Encrypted data as a string
    """
    key = key or settings.SECRET_KEY
    if isinstance(data, dict):
        data = json.dumps(data)
    return jwe.encrypt(data.encode(), key).decode()


def decrypt_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """Decrypt data using JWE.
    
    Args:
        encrypted_data: Encrypted data as a string
        key: Decryption key (default: settings.SECRET_KEY)
        
    Returns:
        str: Decrypted data as a string
    """
    key = key or settings.SECRET_KEY
    return jwe.decrypt(encrypted_data.encode(), key).decode()


def to_camel_case(snake_str: str) -> str:
    """Convert a snake_case string to camelCase.
    
    Args:
        snake_str: Snake case string to convert
        
    Returns:
        str: Camel case string
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def to_snake_case(camel_str: str) -> str:
    """Convert a camelCase string to snake_case.
    
    Args:
        camel_str: Camel case string to convert
        
    Returns:
        str: Snake case string
    """
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', camel_str).lower()


def dict_to_camel_case(data: dict) -> dict:
    """Convert all keys in a dictionary to camelCase.
    
    Args:
        data: Dictionary with snake_case keys
        
    Returns:
        dict: Dictionary with camelCase keys
    """
    return {to_camel_case(k): v for k, v in data.items()}


def dict_to_snake_case(data: dict) -> dict:
    """Convert all keys in a dictionary to snake_case.
    
    Args:
        data: Dictionary with camelCase keys
        
    Returns:
        dict: Dictionary with snake_case keys
    """
    return {to_snake_case(k): v for k, v in data.items()}


def get_client_ip(request: Request) -> str:
    """Get the client's IP address from the request.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        str: Client's IP address
    """
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Get the user agent from the request.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        str: User agent string
    """
    return request.headers.get("User-Agent", "unknown")


def get_domain_from_email(email: str) -> str:
    """Extract the domain from an email address.
    
    Args:
        email: Email address
        
    Returns:
        str: Domain part of the email
    """
    if "@" not in email:
        return ""
    return email.split("@")[1].lower()


def mask_email(email: str) -> str:
    """Mask an email address for display.
    
    Example: test@example.com -> t***@e******.com
    
    Args:
        email: Email address to mask
        
    Returns:
        str: Masked email address
    """
    if "@" not in email:
        return email
    
    username, domain = email.split("@")
    masked_username = f"{username[0]}{'*' * (len(username) - 1)}" if len(username) > 1 else username
    
    if "." in domain:
        domain_parts = domain.split(".")
        masked_domain = f"{domain_parts[0][0]}{'*' * (len(domain_parts[0]) - 1)}.{'.'.join(domain_parts[1:])}"
    else:
        masked_domain = domain
    
    return f"{masked_username}@{masked_domain}"


def mask_phone(phone: str) -> str:
    """Mask a phone number for display.
    
    Example: +1234567890 -> +1******890
    
    Args:
        phone: Phone number to mask
        
    Returns:
        str: Masked phone number
    """
    if not phone:
        return ""
    
    # Keep country code and last 3 digits
    if len(phone) > 4:
        return f"{phone[:2]}******{phone[-3:]}"
    return "*" * len(phone)


def paginate(
    items: List[T],
    page: int = 1,
    page_size: int = 10,
    total: Optional[int] = None
) -> Dict[str, Any]:
    """Paginate a list of items.
    
    Args:
        items: List of items to paginate
        page: Current page number (1-based)
        page_size: Number of items per page
        total: Total number of items (if None, uses len(items))
        
    Returns:
        dict: Dictionary with pagination metadata and items
    """
    if total is None:
        total = len(items)
    
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
    
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }
