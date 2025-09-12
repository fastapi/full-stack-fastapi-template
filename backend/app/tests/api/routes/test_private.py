from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.constants import OK_CODE
from app.core.config import settings
from app.models import User


def test_create_user(client: TestClient, db: Session) -> None:
    # Create user data
    user_data = {
        "email": "pollo@listo.com",
        "password": "password123",
        "full_name": "Pollo Listo",
    }

    # Make request
    response = client.post(f"{settings.API_V1_STR}/private/users/", json=user_data)
    assert response.status_code == OK_CODE

    # Get response data
    response_data = response.json()

    # Verify user was created in database
    created_user = db.exec(select(User).where(User.id == response_data["id"])).first()
    assert created_user
    assert created_user.email == user_data["email"]
    assert created_user.full_name == user_data["full_name"]
