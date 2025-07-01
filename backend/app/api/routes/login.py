from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep
from app.core import security
from app.core.config import settings
from app.models import Token

router = APIRouter()


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Temporary implementation - replace with actual user validation
    if form_data.username == "admin" and form_data.password == "admin":
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return Token(
            access_token=security.create_access_token(
                form_data.username, expires_delta=access_token_expires
            )
        )
    else:
        raise HTTPException(status_code=400, detail="Incorrect email or password")


@router.post("/login/test-token")
def test_token() -> Any:
    """
    Test access token
    """
    return {"message": "Token is valid"}
