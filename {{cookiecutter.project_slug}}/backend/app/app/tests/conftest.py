import pytest

from app.core import config
from app.tests.utils.utils import get_server_api, get_superuser_token_headers
from app.tests.utils.user import byemail_authentication_token


@pytest.fixture(scope="module")
def server_api():
    return get_server_api()


@pytest.fixture(scope="module")
def superuser_token_headers():
    return get_superuser_token_headers()


@pytest.fixture(scope="module")
def normaluser_token_headers():
    return byemail_authentication_token(config.EMAIL_TEST_USER)
