from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from passlib.context import CryptContext
from fastapi.responses import JSONResponse
from fastapi import Response
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def set_response_cookie(subject: str | Any, expires_delta: timedelta) -> Response:
    access_token = create_access_token(subject, expires_delta)
    response = JSONResponse(
        content={"message": "Login successful"}
    )
    response.set_cookie(
        key="http_only_auth_cookie",
        value=access_token,
        httponly=True,
        max_age=3600,
        expires=3600,
        samesite="lax",
        secure=False,
    )
    return response


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
