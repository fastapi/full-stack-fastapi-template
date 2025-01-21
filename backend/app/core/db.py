from sqlmodel import Session, create_engine, select

from sqlmodel import Session, create_engine, SQLModel, select
from app.core.config import settings
from app.models import User, UserCreate
from app import crud


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI),  connect_args={"check_same_thread": False}, echo=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        user: User | None = session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER)).first()
        if not user:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            user = crud.create_user(session=session, user_create=user_in)

    print("Database initialized successfully!")
