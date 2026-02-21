from sqlmodel import Session

from app.core.security import verify_password
from app.models import User
from app.repositories import user_repository

# Dummy hash to use for timing attack prevention when user is not found.
# This is an Argon2 hash of a random password.
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    user = user_repository.get_by_email(session=session, email=email)
    if user is None:
        verify_password(password, DUMMY_HASH)
        return None

    verified, updated_password_hash = verify_password(password, user.hashed_password)
    if not verified:
        return None

    if updated_password_hash:
        user.hashed_password = updated_password_hash
        user_repository.save(session=session, user=user)
    return user
