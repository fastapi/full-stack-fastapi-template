from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models import User


def test_create_user(client: TestClient, db: Session) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/private/users/",
        json={
            "email": "pollo@listo.com",
            "password": "password123",
            "full_name": "Pollo Listo",
        },
    )

    assert r.status_code == 200

    data = r.json()

    user = db.exec(select(User).where(User.id == data["id"])).first()

    assert user
    assert user.email == "pollo@listo.com"
    assert user.full_name == "Pollo Listo"


def test_create_user_invalid_email(client: TestClient) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/private/users/",
        json={
            "email": "not-an-email",
            "password": "password123",
            "full_name": "Bad Email",
        },
    )

    assert r.status_code == 422


def test_create_user_short_password(client: TestClient) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/private/users/",
        json={
            "email": "shortpw@example.com",
            "password": "ab",
            "full_name": "Short Password",
        },
    )

    assert r.status_code == 422


def test_create_user_duplicate_email(client: TestClient) -> None:
    payload = {
        "email": "dupe@example.com",
        "password": "password123",
        "full_name": "Dupe User",
    }

    r1 = client.post(f"{settings.API_V1_STR}/private/users/", json=payload)
    assert r1.status_code == 200

    r2 = client.post(f"{settings.API_V1_STR}/private/users/", json=payload)
    assert r2.status_code == 400
