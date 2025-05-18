"""
SQLite UUID support for testing.

This module provides functions to convert between UUID and string
for SQLite compatibility.
"""
import uuid


def uuid_to_str(uuid_val):
    """Convert UUID to string."""
    if uuid_val is None:
        return None
    return str(uuid_val)


def str_to_uuid(str_val):
    """Convert string to UUID."""
    if str_val is None:
        return None
    if isinstance(str_val, uuid.UUID):
        return str_val
    try:
        return uuid.UUID(str_val)
    except (ValueError, AttributeError):
        return None