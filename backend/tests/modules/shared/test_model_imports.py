"""
Tests for model imports.

This module tests that models can be imported from their modular locations.
"""
import pytest

# Test shared models
def test_shared_models_imports():
    """Test that shared models can be imported from app.shared.models."""
    from app.shared.models import Message, BaseModel, TimestampedModel, UUIDModel, PaginatedResponse
    
    assert Message
    assert BaseModel
    assert TimestampedModel
    assert UUIDModel
    assert PaginatedResponse


# Test auth models
def test_auth_models_imports():
    """Test that auth models can be imported from app.modules.auth.domain.models."""
    from app.modules.auth.domain.models import (
        TokenPayload,
        Token,
        NewPassword,
        PasswordReset,
        LoginRequest,
        RefreshToken,
    )
    
    assert TokenPayload
    assert Token
    assert NewPassword
    assert PasswordReset
    assert LoginRequest
    assert RefreshToken


# Test users models (non-table models)
def test_users_models_imports():
    """Test that user models can be imported from app.modules.users.domain.models."""
    from app.modules.users.domain.models import (
        UserBase,
        UserCreate,
        UserRegister,
        UserUpdate,
        UserUpdateMe,
        UpdatePassword,
        UserPublic,
        UsersPublic,
    )
    
    assert UserBase
    assert UserCreate
    assert UserRegister
    assert UserUpdate
    assert UserUpdateMe
    assert UpdatePassword
    assert UserPublic
    assert UsersPublic


# Test items models (non-table models)
def test_items_models_imports():
    """Test that item models can be imported from app.modules.items.domain.models."""
    from app.modules.items.domain.models import (
        ItemBase,
        ItemCreate,
        ItemUpdate,
        ItemPublic,
        ItemsPublic,
    )
    
    assert ItemBase
    assert ItemCreate
    assert ItemUpdate
    assert ItemPublic
    assert ItemsPublic


# Test email models
def test_email_models_imports():
    """Test that email models can be imported from app.modules.email.domain.models."""
    from app.modules.email.domain.models import (
        EmailTemplateType,
        EmailContent,
        EmailRequest,
        TemplateData,
    )
    
    assert EmailTemplateType
    assert EmailContent
    assert EmailRequest
    assert TemplateData
