from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, UserRole

engine = create_engine(str(settings.DATABASE_URL))


def _ensure_user(
    session: Session,
    *,
    email: str,
    password: str,
    role: UserRole,
) -> None:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        user_in = UserCreate(
            email=email,
            password=password,
            role=role,
            is_superuser=role == UserRole.ADMIN,
        )
        crud.create_user(session=session, user_create=user_in)


def init_db(session: Session) -> None:
    _ensure_user(
        session,
        email=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        role=UserRole.ADMIN,
    )
    _ensure_user(
        session,
        email=settings.MANAGER_USER,
        password=settings.MANAGER_USER_PASSWORD,
        role=UserRole.MANAGER,
    )
    _ensure_user(
        session,
        email=settings.MEMBER_USER,
        password=settings.MEMBER_USER_PASSWORD,
        role=UserRole.MEMBER,
    )
