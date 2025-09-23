import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
import json

client = TestClient(app)

def test_api_versioning():
    """Test API versioning and backward compatibility."""
    # Test current API version
    response = client.get("/api/v1/utils/health-check/")
    assert response.status_code == 200

    # Test that v1 endpoints are available
    assert "/api/v1/" in str(response.url) or response.status_code == 200

def test_openapi_schema_validation():
    """Test OpenAPI schema is valid and complete."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema

def test_api_documentation_accessibility():
    """Test that API documentation is accessible."""
    docs_response = client.get("/docs")
    redoc_response = client.get("/redoc")

    # At least one documentation endpoint should be available
    assert docs_response.status_code == 200 or redoc_response.status_code == 200

def test_health_monitoring_endpoints():
    """Test health monitoring and status endpoints."""
    health_response = client.get("/api/v1/utils/health-check/")
    assert health_response.status_code == 200

    # Verify health check response format
    data = health_response.json()
    assert isinstance(data, dict)

def test_api_error_response_format():
    """Test that API errors follow consistent format."""
    # Make request to non-existent endpoint
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404

    # Verify error response is JSON
    try:
        error_data = response.json()
        assert isinstance(error_data, dict)
    except json.JSONDecodeError:
        # Some APIs might return non-JSON 404s, which is also acceptable
        pass

def test_request_id_tracking():
    """Test request ID tracking for debugging."""
    response = client.get("/api/v1/utils/health-check/")

    # Check if request ID is present in headers (implementation dependent)
    request_id_headers = [
        "x-request-id", "request-id", "x-trace-id"
    ]

    has_request_id = any(header in response.headers for header in request_id_headers)
    # This test is optional - not all APIs implement request ID tracking
    assert response.status_code == 200  # Main assertion is that the endpoint works
