import requests

from app import crud
from app.core import config
from app.db.session import db_session
from app.models.user import UserCreate
from faker import Faker

fake = Faker(config.LOCALE_FOR_TESTS)


def user_authentication_headers(server_api, email, password):
    data = {"username": email, "password": password}

    r = requests.post(f"{server_api}{config.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user():
    password = fake.password()

    # generate random data for user
    user_in = UserCreate(
        email=fake.email(),
        full_name=fake.name(),
        password=password,
        created_at=fake.date_time_this_month(),
    )

    # create and return user
    # the generated password is added to the object for conveniency
    # it will disappear permanently once the object will be garbage-collected
    created = crud.user.create(db_session=db_session, user_in=user_in)
    created.password = password
    return created
