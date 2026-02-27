import warnings

import pytest
from pydantic import ValidationError


def _make_settings(monkeypatch, **overrides):
    """Helper to create Settings with required env vars + overrides."""
    defaults = {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_KEY": "test-service-key",
        "CLERK_SECRET_KEY": "test-clerk-key",
    }
    defaults.update(overrides)
    for key, value in defaults.items():
        monkeypatch.setenv(key, str(value))
    from app.core.config import Settings

    return Settings(_env_file=None)


def test_parses_required_vars(monkeypatch):
    """All 3 required vars are parsed correctly with correct types."""
    settings = _make_settings(monkeypatch)
    assert str(settings.SUPABASE_URL) == "https://test.supabase.co/"
    assert settings.SUPABASE_SERVICE_KEY.get_secret_value() == "test-service-key"
    assert settings.CLERK_SECRET_KEY.get_secret_value() == "test-clerk-key"


def test_missing_required_var_raises(monkeypatch):
    """Missing any required var raises ValidationError."""
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.delenv("SUPABASE_SERVICE_KEY", raising=False)
    monkeypatch.delenv("CLERK_SECRET_KEY", raising=False)
    from app.core.config import Settings

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_optional_vars_use_defaults(monkeypatch):
    """All optional vars have expected default values."""
    settings = _make_settings(monkeypatch)
    assert settings.ENVIRONMENT == "local"
    assert settings.SERVICE_NAME == "my-service"
    assert settings.SERVICE_VERSION == "0.1.0"
    assert settings.LOG_LEVEL == "INFO"
    assert settings.LOG_FORMAT == "json"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.BACKEND_CORS_ORIGINS == []
    assert settings.WITH_UI is False
    assert settings.CLERK_JWKS_URL is None
    assert settings.CLERK_AUTHORIZED_PARTIES == []
    assert settings.GIT_COMMIT == "unknown"
    assert settings.BUILD_TIME == "unknown"
    assert settings.HTTP_CLIENT_TIMEOUT == 30
    assert settings.HTTP_CLIENT_MAX_RETRIES == 3
    assert settings.SENTRY_DSN is None


def test_secret_str_types(monkeypatch):
    """SUPABASE_SERVICE_KEY and CLERK_SECRET_KEY are SecretStr instances."""
    from pydantic import SecretStr

    settings = _make_settings(monkeypatch)
    assert isinstance(settings.SUPABASE_SERVICE_KEY, SecretStr)
    assert isinstance(settings.CLERK_SECRET_KEY, SecretStr)


def test_production_weak_secret_raises(monkeypatch):
    """ENVIRONMENT=production + secret='changethis' raises ValueError."""
    with pytest.raises(ValueError, match="changethis"):
        _make_settings(
            monkeypatch,
            ENVIRONMENT="production",
            SUPABASE_SERVICE_KEY="changethis",
        )


def test_local_weak_secret_warns(monkeypatch):
    """ENVIRONMENT=local + secret='changethis' issues a warning, not an error."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        settings = _make_settings(
            monkeypatch,
            ENVIRONMENT="local",
            SUPABASE_SERVICE_KEY="changethis",
        )
        assert settings.ENVIRONMENT == "local"
    assert any("changethis" in str(w.message) for w in caught)


def test_production_weak_clerk_secret_raises(monkeypatch):
    """ENVIRONMENT=production + CLERK_SECRET_KEY='changethis' raises ValueError."""
    with pytest.raises(ValueError, match="changethis"):
        _make_settings(
            monkeypatch,
            ENVIRONMENT="production",
            CLERK_SECRET_KEY="changethis",
        )


def test_production_cors_wildcard_raises(monkeypatch):
    """ENVIRONMENT=production + CORS=['*'] raises ValueError."""
    with pytest.raises(ValueError, match="wildcard"):
        _make_settings(
            monkeypatch,
            ENVIRONMENT="production",
            BACKEND_CORS_ORIGINS="*",
        )


def test_frozen_immutable(monkeypatch):
    """Assigning to an attribute after creation raises ValidationError (frozen model)."""
    from pydantic import ValidationError

    settings = _make_settings(monkeypatch)
    with pytest.raises(ValidationError):
        settings.SERVICE_NAME = "changed"  # type: ignore[misc]


def test_all_cors_origins_computed(monkeypatch):
    """Computed field all_cors_origins returns a list of string URLs."""
    settings = _make_settings(
        monkeypatch,
        BACKEND_CORS_ORIGINS="https://app.example.com,https://admin.example.com",
    )
    origins = settings.all_cors_origins
    assert isinstance(origins, list)
    assert all(isinstance(o, str) for o in origins)
    assert "https://app.example.com" in origins
    assert "https://admin.example.com" in origins


def test_parse_cors_comma_separated():
    """parse_cors handles 'http://a,http://b' strings."""
    from app.core.config import parse_cors

    result = parse_cors("http://a.com,http://b.com")
    assert result == ["http://a.com", "http://b.com"]


def test_parse_cors_json_array():
    """parse_cors handles '["http://a","http://b"]' JSON array strings."""
    from app.core.config import parse_cors

    result = parse_cors('["http://a.com","http://b.com"]')
    assert result == ["http://a.com", "http://b.com"]
