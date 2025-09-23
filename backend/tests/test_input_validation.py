import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_invalid_json_payload():
    """Test API response to invalid JSON payload."""
    headers = {"Content-Type": "application/json"}
    response = client.post("/api/v1/login/access-token",
                          data="invalid json", headers=headers)
    assert response.status_code == 422

def test_missing_required_fields():
    """Test API response when required fields are missing."""
    incomplete_data = {"email": "test@example.com"}  # Missing password
    response = client.post("/api/v1/login/access-token", json=incomplete_data)
    assert response.status_code == 422

def test_field_validation_email():
    """Test email field validation."""
    invalid_data = {"email": "not-an-email", "password": "test123"}
    response = client.post("/api/v1/users/", json=invalid_data)
    assert response.status_code == 422

def test_field_validation_password_length():
    """Test password length validation."""
    short_password_data = {"email": "test@example.com", "password": "123"}
    response = client.post("/api/v1/users/", json=short_password_data)
    assert response.status_code == 422

def test_response_schema_validation():
    """Test that API responses match expected schema."""
    response = client.get("/api/v1/utils/health-check/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data
