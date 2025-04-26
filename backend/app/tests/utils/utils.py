import random
import string

from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.core.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_auth_cookies(client: TestClient) -> dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    return extract_cookies(r)


def extract_cookies(response: JSONResponse) -> dict[str, str]:
    cookie_header = response.headers.get("Set-Cookie")

    cookie_value = None
    if cookie_header and "http_only_auth_cookie=" in cookie_header:
        cookie_value = cookie_header.split("http_only_auth_cookie=")[1].split(";")[0]

    assert cookie_value, "Cookie value not found"

    return {"http_only_auth_cookie": cookie_value}
