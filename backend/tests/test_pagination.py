import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

def test_pagination_default_params():
    """Test pagination with default parameters."""
    token = create_access_token(subject="test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/items/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) or "items" in data

def test_pagination_custom_limit():
    """Test pagination with custom limit parameter."""
    token = create_access_token(subject="test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/items/?limit=5", headers=headers)
    assert response.status_code == 200

def test_pagination_skip_parameter():
    """Test pagination with skip parameter."""
    token = create_access_token(subject="test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/items/?skip=10&limit=5", headers=headers)
    assert response.status_code == 200

def test_pagination_invalid_parameters():
    """Test pagination with invalid parameters."""
    token = create_access_token(subject="test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/items/?limit=-1", headers=headers)
    assert response.status_code in [200, 422]  # Should handle invalid params gracefully
