import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, Role, RoleCreate, User, UserCreate, UserUpdate


# Role CRUD operations
def create_role(*, session: Session, role_create: RoleCreate) -> Role:
    db_obj = Role.model_validate(role_create)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_role_by_name(*, session: Session, name: str) -> Role | None:
    statement = select(Role).where(Role.name == name)
    return session.exec(statement).first()


def get_or_create_role(*, session: Session, role_name: str, description: str | None = None) -> Role:
    """Get existing role or create it if it doesn't exist."""
    role = get_role_by_name(session=session, name=role_name)
    if not role:
        role = create_role(
            session=session,
            role_create=RoleCreate(name=role_name, description=description)
        )
    return role


def assign_role_to_user(*, session: Session, user: User, role: Role) -> User:
    """Assign a role to a user."""
    if role not in user.roles:
        user.roles.append(role)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def remove_role_from_user(*, session: Session, user: User, role: Role) -> User:
    """Remove a role from a user."""
    if role in user.roles:
        user.roles.remove(role)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def user_has_role(user: User, role_name: str) -> bool:
    """Check if user has a specific role."""
    return any(role.name == role_name for role in user.roles)


def user_has_any_role(user: User, role_names: list[str]) -> bool:
    """Check if user has any of the specified roles."""
    return any(role.name in role_names for role in user.roles)


# User CRUD operations


def create_user(*, session: Session, user_create: UserCreate, default_role: str | None = "runner") -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    # Assign default role if specified
    if default_role:
        role = get_role_by_name(session=session, name=default_role)
        if role:
            assign_role_to_user(session=session, user=db_obj, role=role)

    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
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
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        # Prevent timing attacks by running password verification even when user doesn't exist
        # This ensures the response time is similar whether or not the email exists
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
