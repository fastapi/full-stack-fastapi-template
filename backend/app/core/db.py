from sqlmodel import Session, create_engine

from app import crud
from app.core.config import settings
from app.models import UserCreate

# Create a SQLAlchemy engine using the database URI from settings
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    """
    Initialize the database.

    This function initializes the database by creating a superuser if one doesn't exist.
    It's not protected and can be called during application startup.

    Args:
        session (Session): The database session.

    Returns:
        None

    Raises:
        None

    Notes:
        - Tables should be created with Alembic migrations.
        - If migrations are not used, uncomment the SQLModel.metadata.create_all(engine) line. This works because the models are already imported and registered from app.models
        - Creates a superuser using settings if one doesn't exist.
    """
    # from sqlmodel import SQLModel
    # from app.core.engine import engine
    #
    # SQLModel.metadata.create_all(engine)

    # Check if a superuser already exists in the database
    user = crud.get_user_by_email(session=session, email=settings.FIRST_SUPERUSER)
    if not user:
        # If no superuser exists, create one using the settings
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        # Add the new superuser to the database
        user = crud.create_user(session=session, user_create=user_in)
