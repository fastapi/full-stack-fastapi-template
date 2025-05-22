"""
Core functionality for the Copilot backend application.

This package contains core components and utilities used throughout the application,
including configuration, logging, database connections, security utilities, and helpers.
"""

# Import core modules to make them available when importing from app.core
from .config import settings  # noqa: F401
from .logging import logger, setup_logging  # noqa: F401

# Database
from .db import (  # noqa: F401
    get_db,
    get_async_db,
    get_sync_session,
    get_async_session,
    init_db,
    async_init_db,
    sync_engine,
    async_engine,
    SessionLocal,
    AsyncSessionLocal,
)

# Security
from .security import (  # noqa: F401
    TokenType,
    create_token,
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    create_email_verification_token,
    verify_token,
    verify_password,
    get_password_hash,
    generate_password,
    check_password_strength,
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
    get_token_from_request,
    get_current_user_optional,
    generate_token_response,
    verify_refresh_token,
)

# Utils
from .utils import (  # noqa: F401
    generate_uuid,
    generate_random_string,
    generate_random_number,
    get_timestamp,
    get_datetime,
    format_datetime,
    parse_datetime,
    is_valid_email,
    is_valid_url,
    hash_password,
    generate_jwt_token,
    decode_jwt_token,
    encrypt_data,
    decrypt_data,
    to_camel_case,
    to_snake_case,
    dict_to_camel_case,
    dict_to_snake_case,
    get_client_ip,
    get_user_agent,
    get_domain_from_email,
    mask_email,
    mask_phone,
    paginate,
)

# Define what's available when importing from app.core
__all__ = [
    # Configuration and logging
    'settings',
    'logger',
    'setup_logging',
    
    # Database
    'get_db',
    'get_async_db',
    'get_sync_session',
    'get_async_session',
    'init_db',
    'async_init_db',
    
    # Security
    'TokenType',
    'create_token',
    'create_access_token',
    'create_refresh_token',
    'create_password_reset_token',
    'create_email_verification_token',
    'verify_token',
    'verify_password',
    'get_password_hash',
    'generate_password',
    'check_password_strength',
    'get_current_user',
    'get_current_active_user',
    'get_current_active_superuser',
    'get_token_from_request',
    'get_current_user_optional',
    'generate_token_response',
    'verify_refresh_token',
    
    # Utils
    'generate_uuid',
    'generate_random_string',
    'generate_random_number',
    'get_timestamp',
    'get_datetime',
    'format_datetime',
    'parse_datetime',
    'is_valid_email',
    'is_valid_url',
    'hash_password',
    'generate_jwt_token',
    'decode_jwt_token',
    'encrypt_data',
    'decrypt_data',
    'to_camel_case',
    'to_snake_case',
    'dict_to_camel_case',
    'dict_to_snake_case',
    'get_client_ip',
    'get_user_agent',
    'get_domain_from_email',
    'mask_email',
    'mask_phone',
    'paginate',
]