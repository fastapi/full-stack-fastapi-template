from importlib import import_module

from sqlmodel import Session, create_engine, select

from app.config import settings
from app.constants import APP_PATH
from app.users import service as user_service
from app.users.models import User
from app.users.schemas import UserCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported before initializing DB otherwise, SQLModel
# might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28\
for model_file in APP_PATH.glob("*/models.py"):
    import_module(f"app.{model_file.parent.name}.models")


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel # noqa: ERA001

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine) # noqa: ERA001
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER),
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = user_service.create_user(session=session, user_create=user_in)
