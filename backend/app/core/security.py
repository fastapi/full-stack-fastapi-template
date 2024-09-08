from datetime import datetime, timedelta
from typing import Any, Union

import jwt
from passlib.context import CryptContext


from app.core.config import settings
from app.models import Token, User, UserPublic

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_token(subject: Union[str, Any], expires_delta: timedelta, token_type: str = "access") -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def generate_jwt_token(user: User) -> Token:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    access_token = create_token(user.id, access_token_expires, "access")
    refresh_token = create_token(user.id, refresh_token_expires, "refresh")
    return Token(
        access_token= access_token,
        refresh_token=refresh_token,
        user=UserPublic(**user.dict())
    )
