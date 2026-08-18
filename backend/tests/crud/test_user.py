import pytest
from fastapi.encoders import jsonable_encoder
from pwdlib.hashers.bcrypt import BcryptHasher
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlmodel import Session

from app import crud
from app.core.security import verify_password
from app.models import User, UserCreate, UserRole, UserUpdate
from tests.utils.utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    authenticated_user = crud.authenticate(session=db, email=email, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = crud.authenticate(session=db, email=email, password=password)
    assert user is None


def test_check_if_user_is_active(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_active is True


def test_check_if_user_is_active_inactive(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_active=False)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_active is False


def test_check_if_user_is_superuser(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, role=UserRole.ADMIN)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_superuser is True


def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_superuser is False


def test_get_user(db: Session) -> None:
    password = random_lower_string()
    username = random_email()
    user_in = UserCreate(email=username, password=password, role=UserRole.ADMIN)
    user = crud.create_user(session=db, user_create=user_in)
    user_2 = db.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db: Session) -> None:
    password = random_lower_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password, role=UserRole.ADMIN)
    user = crud.create_user(session=db, user_create=user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password, role=UserRole.ADMIN)
    if user.id is not None:
        crud.update_user(session=db, db_user=user, user_in=user_in_update)
    user_2 = db.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    verified, _ = verify_password(new_password, user_2.hashed_password)
    assert verified


def test_update_user_partial_preserves_role(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, role=UserRole.MANAGER)
    user = crud.create_user(session=db, user_create=user_in)

    crud.update_user(
        session=db,
        db_user=user,
        user_in=UserUpdate(full_name="Still Manager"),
    )

    user_2 = db.get(User, user.id)
    assert user_2
    assert user_2.full_name == "Still Manager"
    assert user_2.role == UserRole.MANAGER
    assert user_2.is_superuser is False


def test_user_create_rejects_is_superuser_field() -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            email="legacy@example.com",
            password="securepass1",
            is_superuser=True,  # type: ignore[call-arg]
        )


def test_is_superuser_follows_role_changes(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = crud.create_user(
        session=db,
        user_create=UserCreate(email=email, password=password, role=UserRole.MANAGER),
    )
    assert user.is_superuser is False

    user = crud.update_user(
        session=db,
        db_user=user,
        user_in=UserUpdate(role=UserRole.ADMIN),
    )
    assert user.role == UserRole.ADMIN
    assert user.is_superuser is True


def test_is_superuser_cannot_be_written_directly(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = crud.create_user(
        session=db,
        user_create=UserCreate(email=email, password=password, role=UserRole.MEMBER),
    )
    with pytest.raises(DBAPIError):
        db.execute(
            text('UPDATE "user" SET is_superuser = true WHERE id = :id'),
            {"id": user.id},
        )
        db.commit()
    db.rollback()


def test_authenticate_user_with_bcrypt_upgrades_to_argon2(db: Session) -> None:
    """Test that a user with bcrypt password hash gets upgraded to argon2 on login."""
    email = random_email()
    password = random_lower_string()

    # Create a bcrypt hash directly (simulating legacy password)
    bcrypt_hasher = BcryptHasher()
    bcrypt_hash = bcrypt_hasher.hash(password)
    assert bcrypt_hash.startswith("$2")  # bcrypt hashes start with $2

    # Create user with bcrypt hash directly in the database
    user = User(email=email, hashed_password=bcrypt_hash)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Verify the hash is bcrypt before authentication
    assert user.hashed_password.startswith("$2")

    # Authenticate - this should upgrade the hash to argon2
    authenticated_user = crud.authenticate(session=db, email=email, password=password)
    assert authenticated_user
    assert authenticated_user.email == email

    db.refresh(authenticated_user)

    # Verify the hash was upgraded to argon2
    assert authenticated_user.hashed_password.startswith("$argon2")

    verified, updated_hash = verify_password(
        password, authenticated_user.hashed_password
    )
    assert verified
    # Should not need another update since it's already argon2
    assert updated_hash is None
