import logging
import secrets

import httpx
from sqlmodel import Session

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import User
from app.repositories import user_repository

# Dummy hash to use for timing attack prevention when user is not found.
# This is an Argon2 hash of a random password.
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"

logger = logging.getLogger(__name__)


class GoogleAuthError(RuntimeError):
    def __init__(self, detail: str, status_code: int = 400) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def _verify_google_id_token(*, id_token: str) -> dict[str, str]:
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    if not client_id or not client_id.strip():
        raise GoogleAuthError("Google login is not configured", status_code=503)

    try:
        response = httpx.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
            timeout=settings.GOOGLE_AUTH_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as exc:
        logger.warning("Google token verification HTTP error: %s", exc)
        raise GoogleAuthError(
            "Google token verification failed", status_code=502
        ) from exc

    if response.status_code >= 400:
        logger.warning(
            "Google token verification rejected (status=%s): %s",
            response.status_code,
            response.text[:500],
        )
        raise GoogleAuthError("Invalid Google login token", status_code=401)

    payload = response.json()
    if not isinstance(payload, dict):
        raise GoogleAuthError("Invalid Google token response", status_code=502)

    audience = str(payload.get("aud", "")).strip()
    if audience != client_id:
        logger.warning(
            "Google token audience mismatch (expected=%s got=%s)",
            client_id,
            audience,
        )
        raise GoogleAuthError("Invalid Google token audience", status_code=401)

    return {str(k): str(v) for k, v in payload.items()}


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


def authenticate_google_id_token(*, session: Session, id_token: str) -> User:
    payload = _verify_google_id_token(id_token=id_token)

    email = payload.get("email", "").strip().lower()
    email_verified = payload.get("email_verified", "").strip().lower() == "true"
    full_name = payload.get("name", "").strip() or None

    if not email:
        raise GoogleAuthError("Google account email is missing", status_code=401)
    if not email_verified:
        raise GoogleAuthError("Google account email is not verified", status_code=401)

    user = user_repository.get_by_email(session=session, email=email)
    if user is None:
        random_password = secrets.token_urlsafe(24)
        logger.info("Creating local user from Google login (email=%s)", email)
        user = user_repository.create(
            session=session,
            user=User(
                email=email,
                full_name=full_name,
                hashed_password=get_password_hash(random_password),
            ),
        )
    elif not user.is_active:
        raise GoogleAuthError("Inactive user", status_code=400)
    elif not user.full_name and full_name:
        user.full_name = full_name
        user = user_repository.save(session=session, user=user)

    logger.info("Google login successful (email=%s user_id=%s)", user.email, user.id)
    return user
