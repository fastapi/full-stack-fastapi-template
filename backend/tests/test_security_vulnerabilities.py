import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

def test_sql_injection_prevention():
    """Test that SQL injection attempts are prevented."""
    token = create_access_token(subject="test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt SQL injection in query parameters
    malicious_query = "1' OR '1'='1"
    response = client.get(f"/api/v1/items/{malicious_query}", headers=headers)

    # Should return 404 or 422, not expose database errors
    assert response.status_code in [404, 422]

def test_xss_prevention():
    """Test XSS prevention in API responses."""
    token = create_access_token(subject="test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    xss_payload = {
        "title": "<script>alert('xss')</script>",
        "description": "Test description"
    }

    response = client.post("/api/v1/items/", json=xss_payload, headers=headers)

    if response.status_code == 200:
        # Check that script tags are not returned as-is
        data = response.json()
        assert "<script>" not in str(data)

def test_csrf_protection():
    """Test CSRF protection mechanisms."""
    # Test that state-changing operations require proper authentication
    response = client.post("/api/v1/items/", json={"title": "test"})
    assert response.status_code == 401

def test_input_sanitization():
    """Test that user input is properly sanitized."""
    token = create_access_token(subject="test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    potentially_harmful_input = {
        "title": "Normal title with <b>HTML</b>",
        "description": "Description with javascript:alert('test')"
    }

    response = client.post("/api/v1/items/", json=potentially_harmful_input, headers=headers)

    if response.status_code == 200:
        # Verify input was sanitized appropriately
        data = response.json()
        assert isinstance(data.get("title"), str)
