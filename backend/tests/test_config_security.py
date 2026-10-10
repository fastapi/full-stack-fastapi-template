"""Regression tests for fail-closed secret handling.

These lock in the fix for the shipped-default-secret finding: the application
must refuse to load settings when ``SECRET_KEY`` is a known placeholder or is
too short, in *every* environment (including development). Previously the
placeholder was only a warning in development, which let the template ship a
working signing key that could be used to forge JWTs.
"""

import pytest
from pydantic import ValidationError

from app.core.config import MINIMUM_SECRET_KEY_LENGTH, Settings

VALID_SECRET = "x" * MINIMUM_SECRET_KEY_LENGTH


def _settings(**overrides: str) -> Settings:
    values = {
        "_env_file": None,
        "PROJECT_NAME": "Test Project",
        "SECRET_KEY": VALID_SECRET,
        "FIRST_SUPERUSER": "admin@example.com",
        "FIRST_SUPERUSER_PASSWORD": "a-strong-superuser-password",
        "DATABASE_URL": "postgresql://postgres:a-strong-db-password@localhost:5432/app",
    }
    values.update(overrides)
    return Settings(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("env", [None, "development"])
def test_placeholder_secret_key_is_rejected_in_every_environment(
    env: str | None,
) -> None:
    with pytest.raises(ValidationError):
        _settings(SECRET_KEY="changethis", FASTAPI_ENV=env)


def test_short_secret_key_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _settings(SECRET_KEY="too-short")


def test_placeholder_superuser_password_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _settings(FIRST_SUPERUSER_PASSWORD="changethis")


def test_placeholder_database_password_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _settings(DATABASE_URL="postgresql://postgres:changethis@localhost:5432/app")


def test_valid_secret_key_is_accepted() -> None:
    settings = _settings()
    assert settings.SECRET_KEY == VALID_SECRET
