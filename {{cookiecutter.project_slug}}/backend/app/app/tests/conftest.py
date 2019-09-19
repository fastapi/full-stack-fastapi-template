import pytest

from app.core import config
from app.tests.utils.user import byemail_authentication_token
from app.tests.utils.utils import get_server_api, get_superuser_token_headers


@pytest.fixture(scope="module")
def server_api():
    return get_server_api()


@pytest.fixture(scope="module")
def superuser_token_headers():
    return get_superuser_token_headers()


@pytest.fixture(scope="module")
def normaluser_token_headers():
    return byemail_authentication_token(config.EMAIL_TEST_USER)


@pytest.fixture(scope="module")
def normaluser(normaluser_token_headers):
    user = crud.user.get_by_email(db_session, email=config.EMAIL_TEST_USER)
    if not user:
        user_in = schemas_user.UserCreate(
            email=config.EMAIL_TEST_USER, password=fake.password(), city_id=51
        )
        user = crud.user.create(db_session=db_session, obj_in=user_in)
    return user
