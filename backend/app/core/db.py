from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app import crud
from app.core.config import settings
from app.models import Base, User, UserCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# make sure all SQLAlchemy models are imported (app.models) before initializing DB
# otherwise, SQLAlchemy might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: SessionLocal) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # Base.metadata.create_all(bind=engine)

    # This works because the models are already imported and registered from app.models
    
    result = session.execute(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    )
    user = result.scalar_one_or_none()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
