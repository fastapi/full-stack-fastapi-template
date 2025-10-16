from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate

# SQLite engine (no env, no Postgres)
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False}
)


def init_db(session: Session) -> None:
    # If not using Alembic, uncomment this to auto-create tables
     from sqlmodel import SQLModel
     SQLModel.metadata.create_all(engine)

     user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
     if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        crud.create_user(session=session, user_create=user_in)






