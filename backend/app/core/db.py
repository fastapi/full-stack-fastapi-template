from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app import crud
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import User


engine = create_engine(settings.SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=True,  # Log SQL queries
)

# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def init_db(session: Session) -> None:
    """Initialize the database by creating all tables and adding a superuser if it doesn't exist."""
    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create initial superuser if it doesn't exist
    user = crud.get_user_by_email(session=session, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = {
            "email": settings.FIRST_SUPERUSER,
            "hashed_password": get_password_hash(
                settings.FIRST_SUPERUSER_PASSWORD
            ),  # Key change here
            "is_superuser": True,
        }
        user = User(**user_in)
        session.add(user)
        session.commit()


