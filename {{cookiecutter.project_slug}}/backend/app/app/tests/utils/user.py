import requests

from app import crud
from app.core import config
from app.db.session import db_session
from app.models.user import UserCreate, UserUpdate
from app.tests.utils.utils import get_server_api, random_lower_string


def user_authentication_headers(server_api, email, password):
    data = {"username": email, "password": password}

    r = requests.post(f"{server_api}{config.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=email, email=email, password=password)
    user = crud.user.create(db_session=db_session, user_in=user_in)
    return user


def byemail_authentication_token(email):
    """ 
        Return a valid token for the user with given email, eventhough the user existed in the first place or not.

        The function generated the User if necessary, and update it with a fresh password otherwise. That allows to use again and again the same user during the test (instead of creating a new one every time), without storing any password in the code.
    """
    password = random_lower_string()
    user = crud.user.get_by_email(db_session, email=email)
    if not user:
        user_in = UserCreate(username=email, email=email, password=password)
        user = crud.user.create(db_session=db_session, user_in=user_in)
    else:
        user_in = UserUpdate(password=password)
        user = crud.user.update(db_session, user=user, user_in=user_in)

    return user_authentication_headers(get_server_api(), email, password)
