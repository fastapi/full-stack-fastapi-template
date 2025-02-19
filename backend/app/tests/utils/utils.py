import random
import string
from collections.abc import Generator
from contextlib import ExitStack, contextmanager
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@contextmanager
def patch_password_hashing(*modules: str) -> Generator[None, None, None]:
    """
    Contextmanager to patch ``pwd_context`` in the given modules.
    :param modules: list of modules to patch.
    :return:
    """
    with ExitStack() as stack:
        for module in modules:
            stack.enter_context(
                patch(f"{module}.pwd_context.verify", lambda x, y: x == y)
            )
            stack.enter_context(patch(f"{module}.pwd_context.hash", lambda x: x))
        yield
