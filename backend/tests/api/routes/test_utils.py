"""API route tests for utils"""

from fastapi.testclient import TestClient

from app.core.config import settings
from tests.utils.utils import get_superuser_token_headers


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint"""
    r = client.get(f"{settings.API_V1_STR}/utils/health-check/")
    assert r.status_code == 200
    assert r.json() is True


def test_get_system_info(client: TestClient) -> None:
    """Test system info endpoint"""
    r = client.get(f"{settings.API_V1_STR}/utils/system-info/")
    assert r.status_code == 200
    info = r.json()
    assert "message" in info
    assert "timestamp" in info
    assert "platform" in info
    assert "python" in info
    assert "fun_fact" in info


def test_test_email_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test email endpoint (requires superuser)"""
    from unittest.mock import patch

    with patch("app.utils.send_email", return_value=None):
        # email_to is a query parameter, not in body
        r = client.post(
            f"{settings.API_V1_STR}/utils/test-email/?email_to=test@example.com",
            headers=superuser_token_headers,
        )
        assert r.status_code == 201
        assert r.json()["message"] == "Test email sent"

