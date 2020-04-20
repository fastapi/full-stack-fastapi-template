import pytest

from app.core.config import settings
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_server_api, get_superuser_token_headers

from ..db.session import SessionLocal


@pytest.fixture(scope="session")
def db():
    yield SessionLocal()


@pytest.fixture(scope="module")
def server_api():
    return get_server_api()


@pytest.fixture(scope="module")
def superuser_token_headers():
    return get_superuser_token_headers()


@pytest.fixture(scope="module")
def normal_user_token_headers():
    return authentication_token_from_email(settings.EMAIL_TEST_USER)
