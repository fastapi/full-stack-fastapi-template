import random
import string

from fastapi.testclient import TestClient

from app.constants import TOKEN_LENGTH
from app.core.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=TOKEN_LENGTH))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    response_data = response.json()
    access_token = response_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}
