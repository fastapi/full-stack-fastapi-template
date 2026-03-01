import uuid

from sqlmodel import Session

from app.core.security import get_password_hash, verify_password
from app.models import (
    User,
    UserCreate,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
)
from app.repositories import item_repository, user_repository
from app.services.exceptions import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)


def list_users(
    *, session: Session, skip: int = 0, limit: int = 100
) -> tuple[list[User], int]:
    return user_repository.list_users(session=session, skip=skip, limit=limit)


def get_user_by_email(*, session: Session, email: str) -> User | None:
    return user_repository.get_by_email(session=session, email=email)


def get_user_by_id(*, session: Session, user_id: uuid.UUID) -> User | None:
    return user_repository.get_by_id(session=session, user_id=user_id)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    user = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    return user_repository.create(session=session, user=user)


def create_user_for_admin(*, session: Session, user_in: UserCreate) -> User:
    existing_user = get_user_by_email(session=session, email=user_in.email)
    if existing_user:
        raise BadRequestError("The user with this email already exists in the system.")
    return create_user(session=session, user_create=user_in)


def register_user(*, session: Session, user_in: UserRegister) -> User:
    existing_user = get_user_by_email(session=session, email=user_in.email)
    if existing_user:
        raise BadRequestError("The user with this email already exists in the system")
    user_create = UserCreate.model_validate(user_in)
    return create_user(session=session, user_create=user_create)


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        if isinstance(password, str):
            extra_data["hashed_password"] = get_password_hash(password)
    db_user.sqlmodel_update(user_data, update=extra_data)
    return user_repository.save(session=session, user=db_user)


def update_user_me(
    *, session: Session, current_user: User, user_in: UserUpdateMe
) -> User:
    if user_in.email:
        existing_user = get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise ConflictError("User with this email already exists")

    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    return user_repository.save(session=session, user=current_user)


def update_password_me(
    *, session: Session, current_user: User, current_password: str, new_password: str
) -> None:
    verified, _ = verify_password(current_password, current_user.hashed_password)
    if not verified:
        raise BadRequestError("Incorrect password")
    if current_password == new_password:
        raise BadRequestError("New password cannot be the same as the current one")

    current_user.hashed_password = get_password_hash(new_password)
    user_repository.save(session=session, user=current_user)


def delete_user_me(*, session: Session, current_user: User) -> None:
    if current_user.is_superuser:
        raise ForbiddenError("Super users are not allowed to delete themselves")
    user_repository.delete(session=session, user=current_user)


def get_user_for_read(
    *, session: Session, user_id: uuid.UUID, current_user: User
) -> User:
    user = get_user_by_id(session=session, user_id=user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise ForbiddenError("The user doesn't have enough privileges")
    if user is None:
        raise NotFoundError("User not found")
    return user


def update_user_by_admin(
    *, session: Session, user_id: uuid.UUID, user_in: UserUpdate
) -> User:
    db_user = get_user_by_id(session=session, user_id=user_id)
    if db_user is None:
        raise NotFoundError("The user with this id does not exist in the system")

    if user_in.email:
        existing_user = get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise ConflictError("User with this email already exists")

    return update_user(session=session, db_user=db_user, user_in=user_in)


def delete_user_by_admin(
    *, session: Session, current_user: User, user_id: uuid.UUID
) -> None:
    user = get_user_by_id(session=session, user_id=user_id)
    if user is None:
        raise NotFoundError("User not found")
    if user == current_user:
        raise ForbiddenError("Super users are not allowed to delete themselves")

    item_repository.delete_by_owner(session=session, owner_id=user_id)
    session.delete(user)
    session.commit()


def create_private_user(
    *, session: Session, email: str, password: str, full_name: str
) -> User:
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
    )
    return user_repository.create(session=session, user=user)


def ensure_superuser_exists(*, session: Session, email: str, password: str) -> User:
    existing_user = get_user_by_email(session=session, email=email)
    if existing_user:
        return existing_user

    user_in = UserCreate(
        email=email,
        password=password,
        is_superuser=True,
    )
    return create_user(session=session, user_create=user_in)
