"""
Shared exceptions for the application.

This module contains custom exceptions used across multiple modules.
"""
from typing import Any, Dict, Optional


class AppException(Exception):
    """Base exception for application-specific errors."""
    
    def __init__(
        self, 
        message: str = "An unexpected error occurred", 
        status_code: int = 500,
        data: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.data = data or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    """Exception raised when a resource is not found."""
    
    def __init__(
        self, 
        message: str = "Resource not found",
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, status_code=404, data=data)


class ValidationException(AppException):
    """Exception raised when validation fails."""
    
    def __init__(
        self, 
        message: str = "Validation error",
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, status_code=422, data=data)


class AuthenticationException(AppException):
    """Exception raised when authentication fails."""
    
    def __init__(
        self, 
        message: str = "Authentication failed",
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, status_code=401, data=data)


class PermissionException(AppException):
    """Exception raised when permission is denied."""
    
    def __init__(
        self, 
        message: str = "Permission denied",
        data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message=message, status_code=403, data=data)