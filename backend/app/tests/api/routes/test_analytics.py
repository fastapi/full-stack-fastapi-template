from unittest.mock import patch, MagicMock
import pytest
import polars as pl
from fastapi.testclient import TestClient

# Assuming your main FastAPI app instance is in backend.app.main
from backend.app.main import app 
# Import duckdb for duckdb.Error
import duckdb

# Define the API prefix from settings or main router, if applicable.
# For these tests, we'll assume API_V1_STR is /api/v1 as is common.
API_V1_STR = "/api/v1" 
ANALYTICS_ENDPOINT_PREFIX = f"{API_V1_STR}/analytics"

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True) # Applied to all tests in this module
def mock_otel_tracer_api(monkeypatch):
    # Mock the tracer used in analytics API routes to avoid actual tracing
    # This path should point to the tracer instance in backend.app.api.routes.analytics
    mock_tracer = MagicMock()
    mock_span = MagicMock() # Mock for the span object
    mock_span.get_context.return_value = MagicMock() # Mock context for Link if used by tracer
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span
    monkeypatch.setattr("backend.app.api.routes.analytics.tracer", mock_tracer)

# --- Tests for /analytics/items_by_user ---

def test_get_items_by_user_success(client):
    sample_df = pl.DataFrame({
        "email": ["user1@example.com", "user2@example.com"],
        "item_count": [10, 5]
    })
    expected_json = [
        {"email": "user1@example.com", "item_count": 10},
        {"email": "user2@example.com", "item_count": 5}
    ]
    # The SQL query from the actual route implementation
    expected_query = """
    SELECT u.email, COUNT(i.item_id) AS item_count
    FROM users u
    JOIN items i ON u.user_id = i.owner_id
    GROUP BY u.email
    ORDER BY item_count DESC;
    """

    with patch("backend.app.api.routes.analytics.query_duckdb", return_value=sample_df) as mock_query:
        response = client.get(f"{ANALYTICS_ENDPOINT_PREFIX}/items_by_user")
        assert response.status_code == 200
        assert response.json() == expected_json
        mock_query.assert_called_once_with(expected_query)

def test_get_items_by_user_connection_error(client):
    with patch("backend.app.api.routes.analytics.query_duckdb", side_effect=ConnectionError("Test connection error")) as mock_query:
        response = client.get(f"{ANALYTICS_ENDPOINT_PREFIX}/items_by_user")
        assert response.status_code == 503
        json_response = response.json()
        assert "Analytics service unavailable: Database connection failed." in json_response["detail"]
        assert "Test connection error" in json_response["detail"]


def test_get_items_by_user_duckdb_error(client):
    with patch("backend.app.api.routes.analytics.query_duckdb", side_effect=duckdb.Error("Test DB error")) as mock_query:
        response = client.get(f"{ANALYTICS_ENDPOINT_PREFIX}/items_by_user")
        assert response.status_code == 500
        json_response = response.json()
        assert "Analytics query failed: Test DB error" in json_response["detail"]
        
def test_get_items_by_user_generic_exception(client):
    with patch("backend.app.api.routes.analytics.query_duckdb", side_effect=Exception("Test generic error")) as mock_query:
        response = client.get(f"{ANALYTICS_ENDPOINT_PREFIX}/items_by_user")
        assert response.status_code == 500
        json_response = response.json()
        assert "An unexpected error occurred while fetching items by user." in json_response["detail"]
        assert "Test generic error" in json_response["detail"]

# --- Tests for /analytics/active_users ---

def test_get_active_users_success(client):
    sample_df = pl.DataFrame({
        "user_id": [1, 2],
        "email": ["active1@example.com", "active2@example.com"],
        "full_name": ["Active User One", "Active User Two"],
        "item_count": [20, 15]
    })
    expected_json = [
        {"user_id": 1, "email": "active1@example.com", "full_name": "Active User One", "item_count": 20},
        {"user_id": 2, "email": "active2@example.com", "full_name": "Active User Two", "item_count": 15}
    ]
    # The SQL query from the actual route implementation
    expected_query = """
    SELECT u.user_id, u.email, u.full_name, COUNT(i.item_id) AS item_count
    FROM users u
    LEFT JOIN items i ON u.user_id = i.owner_id
    GROUP BY u.user_id, u.email, u.full_name  -- Group by all selected non-aggregated columns
    ORDER BY item_count DESC
    LIMIT 10;
    """

    with patch("backend.app.api.routes.analytics.query_duckdb", return_value=sample_df) as mock_query:
        response = client.get(f"{ANALYTICS_ENDPOINT_PREFIX}/active_users")
        assert response.status_code == 200
        assert response.json() == expected_json
        mock_query.assert_called_once_with(expected_query)

def test_get_active_users_connection_error(client):
    with patch("backend.app.api.routes.analytics.query_duckdb", side_effect=ConnectionError("Test connection error")) as mock_query:
        response = client.get(f"{ANALYTICS_ENDPOINT_PREFIX}/active_users")
        assert response.status_code == 503
        json_response = response.json()
        assert "Analytics service unavailable: Database connection failed." in json_response["detail"]
        assert "Test connection error" in json_response["detail"]

def test_get_active_users_duckdb_error(client):
    with patch("backend.app.api.routes.analytics.query_duckdb", side_effect=duckdb.Error("Test DB error")) as mock_query:
        response = client.get(f"{ANALYTICS_ENDPOINT_PREFIX}/active_users")
        assert response.status_code == 500
        json_response = response.json()
        assert "Analytics query failed: Test DB error" in json_response["detail"]

def test_get_active_users_generic_exception(client):
    with patch("backend.app.api.routes.analytics.query_duckdb", side_effect=Exception("Test generic error")) as mock_query:
        response = client.get(f"{ANALYTICS_ENDPOINT_PREFIX}/active_users")
        assert response.status_code == 500
        json_response = response.json()
        assert "An unexpected error occurred while fetching active users." in json_response["detail"]
        assert "Test generic error" in json_response["detail"]

```
