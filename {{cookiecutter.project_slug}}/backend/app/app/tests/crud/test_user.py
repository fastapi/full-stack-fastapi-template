from app import crud
from app.db.session import db_session
from app.schemas.user import User, UserCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def test_create_user():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.user.create(db_session, obj_in=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.user.create(db_session, obj_in=user_in)
    authenticated_user = crud.user.authenticate(
        db_session, email=email, password=password
    )
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user():
    email = random_lower_string()
    password = random_lower_string()
    user = crud.user.authenticate(db_session, email=email, password=password)
    assert user is None


def test_check_if_user_is_active():
    user = create_random_user()
    assert user.is_active


def test_check_if_user_is_superuser_normal_user():
    user = create_random_user()
    assert not user.is_superuser


def test_check_if_user_is_active_inactive():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_active=False)
    user = crud.user.create(db_session, obj_in=user_in)
    assert not user.is_active
    assert not user.is_active


def test_check_if_user_is_superuser():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = crud.user.create(db_session, obj_in=user_in)
    assert user.is_superuser


def test_get_user():
    user = create_random_user()
    user_2 = crud.user.get(db_session, obj_id=user.id)
    assert user.email == user_2.email
    assert user.to_schema(User) == user_2.to_schema(User)
