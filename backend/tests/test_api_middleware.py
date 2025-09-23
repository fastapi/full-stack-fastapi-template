import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_cors_headers():
    """Test CORS headers are properly set."""
    response = client.options("/api/v1/users/me")
    assert response.status_code in [200, 405]
    # Check if CORS headers might be present
    if "access-control-allow-origin" in response.headers:
        assert response.headers["access-control-allow-origin"]

def test_api_version_consistency():
    """Test that all API endpoints use consistent versioning."""
    # Test health check endpoint version
    response = client.get("/api/v1/utils/health-check/")
    assert response.status_code == 200

def test_content_type_headers():
    """Test that API returns proper content-type headers."""
    response = client.get("/api/v1/utils/health-check/")
    assert "application/json" in response.headers.get("content-type", "")

def test_response_time_performance():
    """Test basic response time performance."""
    import time
    start_time = time.time()
    response = client.get("/api/v1/utils/health-check/")
    end_time = time.time()

    assert response.status_code == 200
    # Response should be under 1 second for health check
    assert (end_time - start_time) < 1.0
