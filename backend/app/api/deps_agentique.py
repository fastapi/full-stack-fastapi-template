from typing import Annotated

import jwt
from fastapi import Depends, Request
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.api.deps import SessionDep
from app.core import security
from app.core.config import settings
from app.models import TokenPayload, User


def get_current_user_optional(request: Request, session: SessionDep) -> User | None:
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except InvalidTokenError, ValidationError:
        return None

    user = session.get(User, token_data.sub)
    if not user or not user.is_active:
        return None
    return user


CurrentUserOptional = Annotated[User | None, Depends(get_current_user_optional)]
