import random
import string

import httpx
from fastapi import Response
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


def extract_cookies(
    response: JSONResponse | httpx._models.Response | Response,
) -> dict[str, str]:
    if isinstance(response, httpx._models.Response):
        # Handle httpx Response
        cookie_value = response.cookies.get("http_only_auth_cookie")
        if cookie_value:
            return {"http_only_auth_cookie": cookie_value}
    else:
        # Handle Starlette Response
        cookie_header = response.headers.get("Set-Cookie")
        if cookie_header and "http_only_auth_cookie=" in cookie_header:
            cookie_value = cookie_header.split("http_only_auth_cookie=")[1].split(";")[
                0
            ]
            if cookie_value:
                return {"http_only_auth_cookie": cookie_value}

    raise AssertionError("Cookie value not found")
