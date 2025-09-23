import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

def test_create_item():
    """Test creating a new item."""
    token = create_access_token(subject="test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    item_data = {
        "title": "Test Item",
        "description": "Test Description"
    }

    response = client.post("/api/v1/items/", json=item_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Item"

def test_get_items():
    """Test retrieving items list."""
    token = create_access_token(subject="test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/items/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_item_by_id():
    """Test retrieving a specific item by ID."""
    token = create_access_token(subject="test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/items/1", headers=headers)
    # Should return 200 if item exists, 404 if not
    assert response.status_code in [200, 404]
