from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI)
)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


async def init_db(session: AsyncSession) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel, create_engine

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(
    #     create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    # )

    user = (await session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    )).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = await crud.create_user(session=session, user_create=user_in)
