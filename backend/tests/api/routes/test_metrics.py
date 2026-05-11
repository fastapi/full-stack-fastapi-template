from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import UserRole
from tests.utils.user import create_user_with_role, user_authentication_headers


def test_manager_can_read_metrics(client: TestClient, db: Session) -> None:
    manager, password = create_user_with_role(db=db, role=UserRole.manager)
    headers = user_authentication_headers(
        client=client, email=manager.email, password=password
    )

    r = client.get(f"{settings.API_V1_STR}/metrics/", headers=headers)

    assert r.status_code == 200
    assert "users" in r.json()
    assert "items" in r.json()


def test_member_cannot_read_metrics(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/metrics/", headers=normal_user_token_headers)

    assert r.status_code == 403
    assert r.json()["detail"] == "The user doesn't have enough privileges"
