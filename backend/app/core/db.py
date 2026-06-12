from sqlmodel import Session, create_engine, select

from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

# make sure all SQLModel models are imported before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
def init_db(session: Session) -> None:
    # Import all models so SQLModel registers them
    from app.files.models import File  # noqa: F401
    from app.items.models import Item  # noqa: F401
    from app.users.models import User
    # ensure api_keys model is imported so SQLModel registers the table
    from app.api_keys.models import ApiKey  # noqa: F401
    from app.users.schemas import UserCreate
    from app.users.service import create_user

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        from app.users.constants import UserType

        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            user_type=UserType.ADMIN,
        )
        create_user(session=session, user_create=user_in)
