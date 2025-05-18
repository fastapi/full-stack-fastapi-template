"""
Custom dependencies for blackbox tests.

These dependencies override the regular application dependencies
to work with the test database and simplified models.
"""
from typing import Annotated, Generator

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings

from .test_models import User

# Use the same OAuth2 password bearer as the main app
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


# We'll override this in tests via dependency injection
def get_test_db() -> Generator[Session, None, None]:
    """
    Placeholder function that will be overridden in tests.
    """
    raise NotImplementedError("This function should be overridden in tests")


TestSessionDep = Annotated[Session, Depends(get_test_db)]
TestTokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_test_user(session: TestSessionDep, token: TestTokenDep) -> User:
    """
    Get the current user from the provided token.
    This is similar to the regular get_current_user but works with our test models.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Use string ID for test User model
    user = session.exec(select(User).where(User.id == sub)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user


TestCurrentUser = Annotated[User, Depends(get_current_test_user)]


def get_current_active_test_superuser(current_user: TestCurrentUser) -> User:
    """Verify the user is a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user