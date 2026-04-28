"""Database connection setup using SQLAlchemy with async support."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import async_sessionmaker
from sqlmodel import select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate

# Create an asynchronous engine using the database URL from settings
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,
)

# Create a configured "AsyncSession" class
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


async def init_db(session: AsyncSession) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    result = await session.execute(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    )
    user = result.first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = await crud.create_user(session=session, user_create=user_in)
