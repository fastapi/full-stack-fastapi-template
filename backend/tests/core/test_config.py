"""Tests for application configuration."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.core.config import Settings


class TestMistralAPIConfiguration:
    """Test Mistral OCR API configuration settings."""

    def test_mistral_api_key_loaded_from_env(self):
        """Test that MISTRAL_API_KEY is loaded from environment variables."""
        with patch.dict(
            os.environ,
            {
                "MISTRAL_API_KEY": "test-mistral-key-12345",
                "PROJECT_NAME": "TestProject",
                "FIRST_SUPERUSER": "admin@test.com",
                "FIRST_SUPERUSER_PASSWORD": "testpassword123",
                "DATABASE_URL": "sqlite:///",
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_ANON_KEY": "test-anon-key",
                "SUPABASE_SERVICE_KEY": "test-service-key",
                "REDIS_PASSWORD": "test-redis-password",
                "REDIS_URL": "redis://localhost",
                "CELERY_BROKER_URL": "redis://localhost",
                "CELERY_RESULT_BACKEND": "redis://localhost",
            },
        ):
            settings = Settings()
            assert settings.MISTRAL_API_KEY == "test-mistral-key-12345"

    def test_ocr_provider_defaults_to_mistral(self):
        """Test that OCR_PROVIDER defaults to 'mistral'."""
        with patch.dict(
            os.environ,
            {
                "MISTRAL_API_KEY": "test-key",
                "PROJECT_NAME": "TestProject",
                "FIRST_SUPERUSER": "admin@test.com",
                "FIRST_SUPERUSER_PASSWORD": "testpassword123",
                "DATABASE_URL": "sqlite:///",
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_ANON_KEY": "test-anon-key",
                "SUPABASE_SERVICE_KEY": "test-service-key",
                "REDIS_PASSWORD": "test-redis-password",
                "REDIS_URL": "redis://localhost",
                "CELERY_BROKER_URL": "redis://localhost",
                "CELERY_RESULT_BACKEND": "redis://localhost",
            },
        ):
            settings = Settings()
            assert settings.OCR_PROVIDER == "mistral"

    def test_ocr_max_retries_defaults_to_3(self):
        """Test that OCR_MAX_RETRIES defaults to 3."""
        with patch.dict(
            os.environ,
            {
                "MISTRAL_API_KEY": "test-key",
                "PROJECT_NAME": "TestProject",
                "FIRST_SUPERUSER": "admin@test.com",
                "FIRST_SUPERUSER_PASSWORD": "testpassword123",
                "DATABASE_URL": "sqlite:///",
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_ANON_KEY": "test-anon-key",
                "SUPABASE_SERVICE_KEY": "test-service-key",
                "REDIS_PASSWORD": "test-redis-password",
                "REDIS_URL": "redis://localhost",
                "CELERY_BROKER_URL": "redis://localhost",
                "CELERY_RESULT_BACKEND": "redis://localhost",
            },
        ):
            settings = Settings()
            assert settings.OCR_MAX_RETRIES == 3

    def test_ocr_retry_delay_defaults_to_2(self):
        """Test that OCR_RETRY_DELAY defaults to 2 seconds."""
        with patch.dict(
            os.environ,
            {
                "MISTRAL_API_KEY": "test-key",
                "PROJECT_NAME": "TestProject",
                "FIRST_SUPERUSER": "admin@test.com",
                "FIRST_SUPERUSER_PASSWORD": "testpassword123",
                "DATABASE_URL": "sqlite:///",
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_ANON_KEY": "test-anon-key",
                "SUPABASE_SERVICE_KEY": "test-service-key",
                "REDIS_PASSWORD": "test-redis-password",
                "REDIS_URL": "redis://localhost",
                "CELERY_BROKER_URL": "redis://localhost",
                "CELERY_RESULT_BACKEND": "redis://localhost",
            },
        ):
            settings = Settings()
            assert settings.OCR_RETRY_DELAY == 2

    def test_ocr_max_pages_defaults_to_50(self):
        """Test that OCR_MAX_PAGES defaults to 50."""
        with patch.dict(
            os.environ,
            {
                "MISTRAL_API_KEY": "test-key",
                "PROJECT_NAME": "TestProject",
                "FIRST_SUPERUSER": "admin@test.com",
                "FIRST_SUPERUSER_PASSWORD": "testpassword123",
                "DATABASE_URL": "sqlite:///",
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_ANON_KEY": "test-anon-key",
                "SUPABASE_SERVICE_KEY": "test-service-key",
                "REDIS_PASSWORD": "test-redis-password",
                "REDIS_URL": "redis://localhost",
                "CELERY_BROKER_URL": "redis://localhost",
                "CELERY_RESULT_BACKEND": "redis://localhost",
            },
        ):
            settings = Settings()
            assert settings.OCR_MAX_PAGES == 50

    def test_custom_ocr_settings_from_env(self):
        """Test that custom OCR settings can be overridden via environment variables."""
        with patch.dict(
            os.environ,
            {
                "MISTRAL_API_KEY": "custom-key",
                "OCR_PROVIDER": "paddleocr",
                "OCR_MAX_RETRIES": "5",
                "OCR_RETRY_DELAY": "3",
                "OCR_MAX_PAGES": "100",
                "PROJECT_NAME": "TestProject",
                "FIRST_SUPERUSER": "admin@test.com",
                "FIRST_SUPERUSER_PASSWORD": "testpassword123",
                "DATABASE_URL": "sqlite:///",
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_ANON_KEY": "test-anon-key",
                "SUPABASE_SERVICE_KEY": "test-service-key",
                "REDIS_PASSWORD": "test-redis-password",
                "REDIS_URL": "redis://localhost",
                "CELERY_BROKER_URL": "redis://localhost",
                "CELERY_RESULT_BACKEND": "redis://localhost",
            },
        ):
            settings = Settings()
            assert settings.MISTRAL_API_KEY == "custom-key"
            assert settings.OCR_PROVIDER == "paddleocr"
            assert settings.OCR_MAX_RETRIES == 5
            assert settings.OCR_RETRY_DELAY == 3
            assert settings.OCR_MAX_PAGES == 100

    def test_mistral_api_key_missing_raises_validation_error_in_production(self):
        """Test that missing MISTRAL_API_KEY in production environment raises ValidationError."""
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "production",
                "PROJECT_NAME": "TestProject",
                "FIRST_SUPERUSER": "admin@test.com",
                "FIRST_SUPERUSER_PASSWORD": "testpassword123",
                "DATABASE_URL": "postgresql://user:pass@localhost/db",
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_ANON_KEY": "test-anon-key",
                "SUPABASE_SERVICE_KEY": "test-service-key",
                "REDIS_PASSWORD": "test-redis-password",
                "REDIS_URL": "redis://localhost",
                "CELERY_BROKER_URL": "redis://localhost",
                "CELERY_RESULT_BACKEND": "redis://localhost",
                "SECRET_KEY": "prod-secret-key-not-changethis",
            },
            clear=True,
        ):
            with pytest.raises(ValidationError, match="MISTRAL_API_KEY"):
                Settings()

    def test_mistral_api_key_missing_allowed_in_local_environment(self):
        """Test that missing MISTRAL_API_KEY is allowed in local environment (with warning)."""
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "local",
                "PROJECT_NAME": "TestProject",
                "FIRST_SUPERUSER": "admin@test.com",
                "FIRST_SUPERUSER_PASSWORD": "testpassword123",
                "DATABASE_URL": "sqlite:///",
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_ANON_KEY": "test-anon-key",
                "SUPABASE_SERVICE_KEY": "test-service-key",
                "REDIS_PASSWORD": "test-redis-password",
                "REDIS_URL": "redis://localhost",
                "CELERY_BROKER_URL": "redis://localhost",
                "CELERY_RESULT_BACKEND": "redis://localhost",
            },
            clear=True,
        ):
            # Should not raise, but may log warning
            settings = Settings()
            # MISTRAL_API_KEY should have a default or be None
            assert hasattr(settings, "MISTRAL_API_KEY")
