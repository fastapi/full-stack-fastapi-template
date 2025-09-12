import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.constants import (
    BAD_REQUEST_CODE,
    NOT_FOUND_CODE,
    OK_CODE,
)
from app.core.config import settings
from app.models import Item
from app.tests.utils.item import create_random_item

# Constants for commonly used strings
TEST_ITEM_TITLE = "title"
TEST_ITEM_DESCRIPTION = "description"
ITEMS_ENDPOINT = "/items/"
ERROR_DETAIL_KEY = "detail"


def _create_test_item(db: Session) -> Item:
    """Create a test item and reduce expression reuse."""
    return create_random_item(db)


def test_create_item(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    item_data = {TEST_ITEM_TITLE: "Foo", TEST_ITEM_DESCRIPTION: "Fighters"}
    response = client.post(
        f"{settings.API_V1_STR}{ITEMS_ENDPOINT}",
        headers=superuser_token_headers,
        json=item_data,
    )
    assert response.status_code == OK_CODE
    response_content = response.json()
    assert response_content[TEST_ITEM_TITLE] == item_data[TEST_ITEM_TITLE]
    assert response_content[TEST_ITEM_DESCRIPTION] == item_data[TEST_ITEM_DESCRIPTION]
    assert "id" in response_content
    assert "owner_id" in response_content


def test_read_item(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    test_item = _create_test_item(db)
    response = client.get(
        f"{settings.API_V1_STR}{ITEMS_ENDPOINT}{test_item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == OK_CODE
    response_content = response.json()
    assert response_content[TEST_ITEM_TITLE] == test_item.title
    assert response_content[TEST_ITEM_DESCRIPTION] == test_item.description
    assert response_content["id"] == str(test_item.id)
    assert response_content["owner_id"] == str(test_item.owner_id)


def test_read_item_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}{ITEMS_ENDPOINT}{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == NOT_FOUND_CODE
    response_content = response.json()
    assert response_content[ERROR_DETAIL_KEY] == "Item not found"


def test_read_item_not_enough_permissions(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    test_item = _create_test_item(db)
    response = client.get(
        f"{settings.API_V1_STR}{ITEMS_ENDPOINT}{test_item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == BAD_REQUEST_CODE
    response_content = response.json()
    assert response_content[ERROR_DETAIL_KEY] == "Not enough permissions"


def test_read_items(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    _create_test_item(db)
    _create_test_item(db)
    response = client.get(
        f"{settings.API_V1_STR}{ITEMS_ENDPOINT}",
        headers=superuser_token_headers,
    )
    assert response.status_code == OK_CODE
    response_content = response.json()
    assert len(response_content["data"]) >= 2


def test_update_item(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    test_item = _create_test_item(db)
    update_data = {
        TEST_ITEM_TITLE: "Updated title",
        TEST_ITEM_DESCRIPTION: "Updated description",
    }
    response = client.put(
        f"{settings.API_V1_STR}{ITEMS_ENDPOINT}{test_item.id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == OK_CODE
    response_content = response.json()
    assert response_content[TEST_ITEM_TITLE] == update_data[TEST_ITEM_TITLE]
    assert response_content[TEST_ITEM_DESCRIPTION] == update_data[TEST_ITEM_DESCRIPTION]
    assert response_content["id"] == str(test_item.id)
    assert response_content["owner_id"] == str(test_item.owner_id)


def test_update_item_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    update_data = {
        TEST_ITEM_TITLE: "Updated title",
        TEST_ITEM_DESCRIPTION: "Updated description",
    }
    response = client.put(
        f"{settings.API_V1_STR}{ITEMS_ENDPOINT}{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == NOT_FOUND_CODE
    response_content = response.json()
    assert response_content[ERROR_DETAIL_KEY] == "Item not found"


def test_update_item_not_enough_permissions(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    test_item = _create_test_item(db)
    update_data = {
        TEST_ITEM_TITLE: "Updated title",
        TEST_ITEM_DESCRIPTION: "Updated description",
    }
    response = client.put(
        f"{settings.API_V1_STR}{ITEMS_ENDPOINT}{test_item.id}",
        headers=normal_user_token_headers,
        json=update_data,
    )
    assert response.status_code == BAD_REQUEST_CODE
    response_content = response.json()
    assert response_content[ERROR_DETAIL_KEY] == "Not enough permissions"


def test_delete_item(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    test_item = _create_test_item(db)
    response = client.delete(
        f"{settings.API_V1_STR}{ITEMS_ENDPOINT}{test_item.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == OK_CODE
    response_content = response.json()
    assert response_content["message"] == "Item deleted successfully"


def test_delete_item_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}{ITEMS_ENDPOINT}{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == NOT_FOUND_CODE
    response_content = response.json()
    assert response_content[ERROR_DETAIL_KEY] == "Item not found"


def test_delete_item_not_enough_permissions(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    test_item = _create_test_item(db)
    response = client.delete(
        f"{settings.API_V1_STR}{ITEMS_ENDPOINT}{test_item.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == BAD_REQUEST_CODE
    response_content = response.json()
    assert response_content[ERROR_DETAIL_KEY] == "Not enough permissions"
