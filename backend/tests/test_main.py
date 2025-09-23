import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/v1/utils/health-check/")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}

def test_root_endpoint():
    """Test the root endpoint redirect."""
    response = client.get("/")
    # Should redirect to docs or return some response
    assert response.status_code in [200, 307, 308]

def test_docs_endpoint():
    """Test the OpenAPI docs endpoint."""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_json():
    """Test the OpenAPI JSON schema endpoint."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
