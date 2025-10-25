from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate

# Create engine with conditional configuration based on database type
database_url = str(settings.SQLALCHEMY_DATABASE_URI)

if database_url.startswith("sqlite"):
    # SQLite: Use minimal configuration (no pooling)
    engine = create_engine(
        database_url,
        echo=False,  # Set to True for SQL debugging
        connect_args={"check_same_thread": False},  # Allow multi-threaded access
    )
else:
    # PostgreSQL: Use optimal pooling for Supabase Session Mode
    # Session Mode supports prepared statements and long-lived connections
    # pool_size: max permanent connections (per worker)
    # max_overflow: additional temporary connections during load spikes
    # pool_pre_ping: verify connection health before using
    engine = create_engine(
        database_url,
        pool_size=10,  # 10 permanent connections per backend worker
        max_overflow=20,  # Up to 30 total connections during spikes
        pool_pre_ping=True,  # Verify connections are alive before using
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=False,  # Set to True for SQL debugging
    )


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
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
        user = crud.create_user(session=session, user_create=user_in)
