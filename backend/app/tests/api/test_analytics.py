from fastapi.testclient import TestClient
from sqlmodel import Session # For potential future use with fixtures
import pytest # For potential future use with fixtures

from app.core.config import settings
# Assuming your FastAPI app instance is named 'app' in 'app.main'
# Adjust the import if your app instance is located elsewhere for tests
# from app.main import app 

# Expected Pydantic response models (adjust import path if they are moved)
# from app.api.routes.analytics import UserAnalyticsSummary, ItemAnalyticsTrends 

# Test for User Analytics Summary
def test_get_user_summary(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/analytics/user-summary")
    assert response.status_code == 200
    data = response.json()

    assert "total_users" in data
    assert isinstance(data["total_users"], int)

    assert "signup_trends" in data
    assert isinstance(data["signup_trends"], list)

    assert "activity_summary" in data
    assert "active_users" in data["activity_summary"]
    assert "inactive_users" in data["activity_summary"]
    assert isinstance(data["activity_summary"]["active_users"], int)
    assert isinstance(data["activity_summary"]["inactive_users"], int)

    # Check if signup_trends items have the correct structure if not empty
    if data["signup_trends"]:
        trend_item = data["signup_trends"][0]
        assert "signup_date" in trend_item
        assert "count" in trend_item
        assert isinstance(trend_item["count"], int)


# Test for Item Analytics Trends
def test_get_item_trends(client: TestClient) -> None:
    response = client.get(f"{settings.API_V1_STR}/analytics/item-trends")
    assert response.status_code == 200
    data = response.json()

    assert "total_items" in data
    assert isinstance(data["total_items"], int)

    assert "creation_trends" in data
    assert isinstance(data["creation_trends"], list)

    # Check if creation_trends items have the correct structure if not empty
    if data["creation_trends"]:
        trend_item = data["creation_trends"][0]
        assert "creation_date" in trend_item
        assert "count" in trend_item
        assert isinstance(trend_item["count"], int)
