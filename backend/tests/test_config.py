import pytest
from unittest.mock import patch
from app.core.config import Settings

def test_settings_initialization():
    """Test settings class initialization."""
    settings = Settings()
    assert hasattr(settings, 'SECRET_KEY')
    assert hasattr(settings, 'PROJECT_NAME')

def test_database_url_construction():
    """Test database URL construction."""
    settings = Settings()
    # Should have postgres in the URL
    assert 'postgresql' in str(settings.SQLALCHEMY_DATABASE_URI)

def test_cors_origins_parsing():
    """Test CORS origins parsing."""
    with patch.dict('os.environ', {'BACKEND_CORS_ORIGINS': '["http://localhost:3000", "http://localhost:8000"]'}):
        settings = Settings()
        assert isinstance(settings.BACKEND_CORS_ORIGINS, list)

def test_environment_validation():
    """Test environment variable validation."""
    settings = Settings()
    assert settings.ENVIRONMENT in ['local', 'staging', 'production']
