from typing import Any

from sqlmodel import Session, select
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import  User, UserCreate, UserUpdate, UserPublic, OAuthRegisterPayload, UserOAuthToken


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> UserPublic:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.primary_email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user

def create_user_given_oauth(*, session: Session, user_in: OAuthRegisterPayload) -> User:
    try:
        user_db_obj = User(
            primary_email=user_in.user.primary_email,
            secondary_email = user_in.user.primary_email,
            full_name=user_in.user.full_name,
            oauth='oauth_google',
            email_verified_primary=True,
            email_verified_secondary=True,
            hashed_password = get_password_hash(settings.SECRET_KEY)
        )
        session.add(user_db_obj)
        oauth_obj = UserOAuthToken(
            access_token = user_in.accessToken,
            refresh_token =user_in.refreshToken,
            user_id=user_db_obj.id,
            expires_at=user_in.convert_date()
        )
        session.add(oauth_obj)
        session.commit()
        return user_db_obj
    except Exception as e:
        session.rollback()
        raise e
# def create_item(*, session: Session, item_in: ItemCreate, owner_id: int) -> Item:
#     db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
#     session.add(db_item)
#     session.commit()
#     session.refresh(db_item)
#     return db_item
