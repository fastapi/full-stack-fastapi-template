"""Tests asserting JWTs are rejected when they lack a required `exp` claim.

Companion hardening for the shipped-default-secret finding: even once the
signing key is fail-closed, a token that carries no expiry should never be
accepted. These tests mint tokens with the application's own key and assert that
access-token and password-reset verification both require `exp`.
"""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core import security
from app.core.config import settings
from app.utils import verify_password_reset_token
from tests.utils.utils import random_email


def _encode(claims: dict, *, key: str | None = None) -> str:
    return jwt.encode(
        claims,
        key or settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )


def test_access_token_without_exp_is_rejected(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    # Locate the superuser id from a valid session first.
    me = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    assert me.status_code == 200
    superuser_id = me.json()["id"]

    # A correctly signed token that omits `exp` must not authenticate.
    token_without_exp = _encode({"sub": superuser_id})
    r = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers={"Authorization": f"Bearer {token_without_exp}"},
    )
    assert r.status_code in (401, 403)


def test_access_token_with_exp_is_accepted(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    me = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    assert me.status_code == 200
    superuser_id = me.json()["id"]

    exp = datetime.now(UTC) + timedelta(minutes=30)
    token_with_exp = _encode({"sub": superuser_id, "exp": exp})
    r = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers={"Authorization": f"Bearer {token_with_exp}"},
    )
    assert r.status_code == 200


def test_password_reset_token_requires_exp() -> None:
    email = random_email()
    assert verify_password_reset_token(_encode({"sub": email})) is None

    exp = datetime.now(UTC) + timedelta(hours=1)
    assert verify_password_reset_token(_encode({"sub": email, "exp": exp})) == email


def test_token_signed_with_wrong_key_is_rejected(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    me = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    assert me.status_code == 200
    superuser_id = me.json()["id"]

    # Even with an `exp`, a token signed with the wrong key must fail.
    exp = datetime.now(UTC) + timedelta(minutes=30)
    forged = _encode({"sub": superuser_id, "exp": exp}, key="not-the-real-key")
    r = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers={"Authorization": f"Bearer {forged}"},
    )
    assert r.status_code in (401, 403)
