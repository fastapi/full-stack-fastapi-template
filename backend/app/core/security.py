from datetime import datetime, timedelta, timezone
from typing import Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session
from sqlalchemy.orm import Session
from app import models
from app.core.config import settings
from app.core.session import get_db
from app.models import User
import jwt
from passlib.context import CryptContext
from uuid import UUID
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    print("!!!!! Received token:", token)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        print("Payload for User: ", payload)
        user_id = UUID(payload.get("sub"))  # ✅ force convert to UUID
    except Exception as e:
        print("❌ Token decode error:", e)
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = db.get(models.User, user_id)  # ✅ this now works
    print("User: ", user)
    if not user:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    print("user from token:", current_user)
    if not getattr(current_user, "is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user