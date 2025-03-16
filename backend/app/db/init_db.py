from sqlmodel import Session, select

from app.services.repositories import user as user_repository
from app.core.config import settings
from app.db.models.user import User
from app.schemas.user import UserCreate


def init_db(session: Session) -> None:
    """
    Initialize the database with initial data.
    
    This function is called when the application starts.
    It creates a superuser if it doesn't exist yet.
    """
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel
    # from app.db.session import engine
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = user_repository.create_user(session=session, user_create=user_in)


async def init_mongodb() -> None:
    """
    Initialize MongoDB with any required initial data or indexes.
    
    This function is called when the application starts.
    It sets up indexes and any initial data required for MongoDB collections.
    """
    # This will be implemented as needed when MongoDB collections are defined
    pass 