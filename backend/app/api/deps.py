from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
from app.repositories.items import ItemRepository
from app.repositories.users import UserRepository
from app.services.items import ItemService
from app.services.users import UserService

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_session(request: Request) -> Generator[Session, None, None]:
    """reuses the session if it already exists in the request/response cycle"""
    request_db_session = getattr(request.state, "db_session", None)
    if request_db_session and isinstance(request_db_session, Session):
        yield request_db_session
    else:
        with Session(engine) as session:
            yield session


SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


## Entities


def user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(user_repository)]


def user_service(user_repository: UserRepositoryDep) -> UserService:
    return UserService(user_repository)


UserServiceDep = Annotated[UserService, Depends(user_service)]


def item_repository(session: SessionDep) -> ItemRepository:
    return ItemRepository(session)


ItemRepositoryDep = Annotated[ItemRepository, Depends(item_repository)]


def item_service(item_repository: ItemRepositoryDep) -> ItemService:
    return ItemService(item_repository)


ItemServiceDep = Annotated[ItemService, Depends(item_service)]
