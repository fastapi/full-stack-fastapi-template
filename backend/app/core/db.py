from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, UserRole

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    _ensure_user(
        session,
        email=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        role=UserRole.ADMIN,
        is_superuser=True,
    )

    # Seed test users for non-admin roles in local development only.
    # These make it trivial for reviewers and tests to exercise RBAC paths.
    if settings.ENVIRONMENT == "local":
        _ensure_user(
            session,
            email=settings.TEST_MANAGER_EMAIL,
            password=settings.TEST_MANAGER_PASSWORD,
            role=UserRole.MANAGER,
        )
        _ensure_user(
            session,
            email=settings.TEST_MEMBER_EMAIL,
            password=settings.TEST_MEMBER_PASSWORD,
            role=UserRole.MEMBER,
        )


def _ensure_user(
    session: Session,
    *,
    email: str,
    password: str,
    role: UserRole,
    is_superuser: bool = False,
) -> User:
    """Create a user if one with the given email does not already exist."""
    user = session.exec(select(User).where(User.email == email)).first()
    if user:
        return user

    user_in = UserCreate(
        email=email,
        password=password,
        role=role,
        is_superuser=is_superuser,
    )
    return crud.create_user(session=session, user_create=user_in)