from collections.abc import Generator

import pytest

# Integration test fixtures require database and legacy settings that are being
# migrated away (AYG-65 through AYG-74). Guard imports so unit tests can run
# without --noconftest while integration fixtures are unavailable.
try:
    from fastapi.testclient import TestClient
    from sqlmodel import Session, delete

    from app.core.config import settings
    from app.core.db import engine, init_db
    from app.main import app
    from app.models import Item, User
    from tests.utils.user import authentication_token_from_email
    from tests.utils.utils import get_superuser_token_headers

    _INTEGRATION_DEPS_AVAILABLE = True
except (ImportError, AttributeError, Exception):
    _INTEGRATION_DEPS_AVAILABLE = False


if _INTEGRATION_DEPS_AVAILABLE:

    @pytest.fixture(scope="session", autouse=True)
    def db() -> Generator[Session, None, None]:  # type: ignore[type-arg]
        with Session(engine) as session:
            init_db(session)
            yield session
            statement = delete(Item)
            session.execute(statement)
            statement = delete(User)
            session.execute(statement)
            session.commit()

    @pytest.fixture(scope="module")
    def client() -> Generator[TestClient, None, None]:
        with TestClient(app) as c:
            yield c

    @pytest.fixture(scope="module")
    def superuser_token_headers(client: TestClient) -> dict[str, str]:
        return get_superuser_token_headers(client)

    @pytest.fixture(scope="module")
    def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
        return authentication_token_from_email(
            client=client, email=settings.EMAIL_TEST_USER, db=db
        )
