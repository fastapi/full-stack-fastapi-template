"""Unit tests for Clerk JWT authentication module.

Tests are written FIRST (TDD) before implementation in:
  - backend/app/core/auth.py

Uses a minimal FastAPI app with exception handlers registered — does NOT
import the real app from main.py, so no DB or config fixtures are required.
The Clerk SDK is fully mocked via unittest.mock.patch to avoid real JWKS calls.

Run with:
  uv run pytest backend/tests/unit/test_auth.py -v
"""

from unittest.mock import MagicMock, patch

import pytest
from clerk_backend_api.jwks_helpers import AuthErrorReason, TokenVerificationErrorReason
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.core.auth import get_current_principal
from app.core.errors import register_exception_handlers

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_request_state(
    is_signed_in: bool,
    payload: dict | None = None,
    reason=None,
) -> MagicMock:
    """Build a mock Clerk RequestState."""
    state = MagicMock()
    state.is_signed_in = is_signed_in
    state.payload = payload
    state.reason = reason
    return state


_VALID_PAYLOAD = {
    "sub": "user_123",
    "sid": "sess_456",
    "org_id": "org_789",
    "o": {"rol": "admin"},
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _patch_authorized_parties():
    """Prevent settings from being loaded during auth tests.

    Patches _get_authorized_parties to return [] so that no environment
    variables are required for unit tests.
    """
    with patch("app.core.auth._get_authorized_parties", return_value=[]):
        yield


@pytest.fixture
def test_app() -> FastAPI:
    """Minimal FastAPI app that exposes a protected endpoint."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/protected")
    async def protected(request: Request):
        principal = await get_current_principal(request)
        return principal.model_dump()

    @app.get("/state-check")
    async def state_check(request: Request):
        principal = await get_current_principal(request)
        user_id_on_state = getattr(request.state, "user_id", None)
        return {"principal": principal.model_dump(), "state_user_id": user_id_on_state}

    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Test 1: Valid JWT returns Principal
# ---------------------------------------------------------------------------


def test_valid_jwt_returns_principal(client: TestClient):
    """Valid signed-in state returns a Principal with correct fields."""
    with patch("app.core.auth._get_clerk_sdk") as mock_get_sdk:
        mock_sdk = MagicMock()
        mock_sdk.authenticate_request.return_value = _mock_request_state(
            is_signed_in=True,
            payload=_VALID_PAYLOAD,
        )
        mock_get_sdk.return_value = mock_sdk

        response = client.get(
            "/protected", headers={"Authorization": "Bearer fake-token"}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "user_123"
    assert body["session_id"] == "sess_456"
    assert body["org_id"] == "org_789"


# ---------------------------------------------------------------------------
# Test 2: Missing auth header → 401 AUTH_MISSING_TOKEN
# ---------------------------------------------------------------------------


def test_missing_authorization_returns_401_auth_missing_token(client: TestClient):
    """No Authorization header → 401 with AUTH_MISSING_TOKEN code."""
    with patch("app.core.auth._get_clerk_sdk") as mock_get_sdk:
        mock_sdk = MagicMock()
        mock_sdk.authenticate_request.return_value = _mock_request_state(
            is_signed_in=False,
            reason=AuthErrorReason.SESSION_TOKEN_MISSING,
        )
        mock_get_sdk.return_value = mock_sdk

        response = client.get("/protected")

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "AUTH_MISSING_TOKEN"


# ---------------------------------------------------------------------------
# Test 3: Expired JWT → 401 AUTH_EXPIRED_TOKEN
# ---------------------------------------------------------------------------


def test_expired_jwt_returns_401_auth_expired_token(client: TestClient):
    """Expired JWT → 401 with AUTH_EXPIRED_TOKEN code."""
    with patch("app.core.auth._get_clerk_sdk") as mock_get_sdk:
        mock_sdk = MagicMock()
        mock_sdk.authenticate_request.return_value = _mock_request_state(
            is_signed_in=False,
            reason=TokenVerificationErrorReason.TOKEN_EXPIRED,
        )
        mock_get_sdk.return_value = mock_sdk

        response = client.get(
            "/protected", headers={"Authorization": "Bearer expired-token"}
        )

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "AUTH_EXPIRED_TOKEN"


# ---------------------------------------------------------------------------
# Test 4: Invalid signature → 401 AUTH_INVALID_TOKEN
# ---------------------------------------------------------------------------


def test_invalid_signature_returns_401_auth_invalid_token(client: TestClient):
    """Token with bad signature → 401 with AUTH_INVALID_TOKEN code."""
    with patch("app.core.auth._get_clerk_sdk") as mock_get_sdk:
        mock_sdk = MagicMock()
        mock_sdk.authenticate_request.return_value = _mock_request_state(
            is_signed_in=False,
            reason=TokenVerificationErrorReason.TOKEN_INVALID_SIGNATURE,
        )
        mock_get_sdk.return_value = mock_sdk

        response = client.get(
            "/protected", headers={"Authorization": "Bearer bad-sig-token"}
        )

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "AUTH_INVALID_TOKEN"


# ---------------------------------------------------------------------------
# Test 5: Unauthorized party → 401 AUTH_INVALID_TOKEN
# ---------------------------------------------------------------------------


def test_unauthorized_party_returns_401_auth_invalid_token(client: TestClient):
    """Token from an unauthorized party → 401 with AUTH_INVALID_TOKEN code."""
    with patch("app.core.auth._get_clerk_sdk") as mock_get_sdk:
        mock_sdk = MagicMock()
        mock_sdk.authenticate_request.return_value = _mock_request_state(
            is_signed_in=False,
            reason=TokenVerificationErrorReason.TOKEN_INVALID_AUTHORIZED_PARTIES,
        )
        mock_get_sdk.return_value = mock_sdk

        response = client.get(
            "/protected", headers={"Authorization": "Bearer wrong-party-token"}
        )

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "AUTH_INVALID_TOKEN"


# ---------------------------------------------------------------------------
# Test 6: user_id set on request.state for logging
# ---------------------------------------------------------------------------


def test_user_id_set_on_request_state(client: TestClient):
    """Successful auth sets request.state.user_id to the Clerk user ID."""
    with patch("app.core.auth._get_clerk_sdk") as mock_get_sdk:
        mock_sdk = MagicMock()
        mock_sdk.authenticate_request.return_value = _mock_request_state(
            is_signed_in=True,
            payload=_VALID_PAYLOAD,
        )
        mock_get_sdk.return_value = mock_sdk

        response = client.get(
            "/state-check", headers={"Authorization": "Bearer fake-token"}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["state_user_id"] == "user_123"


# ---------------------------------------------------------------------------
# Test 7: Clerk SDK exception → 401 AUTH_INVALID_TOKEN
# ---------------------------------------------------------------------------


def test_clerk_sdk_exception_returns_401(client: TestClient):
    """Unexpected Clerk SDK exception returns 401 AUTH_INVALID_TOKEN."""
    with patch("app.core.auth._get_clerk_sdk") as mock_get_sdk:
        mock_sdk = MagicMock()
        mock_sdk.authenticate_request.side_effect = RuntimeError("SDK boom")
        mock_get_sdk.return_value = mock_sdk

        response = client.get(
            "/protected", headers={"Authorization": "Bearer some-token"}
        )

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "AUTH_INVALID_TOKEN"


# ---------------------------------------------------------------------------
# Test 8: Default/unknown reason → 401 AUTH_INVALID_TOKEN
# ---------------------------------------------------------------------------


def test_unknown_reason_returns_401_auth_invalid_token(client: TestClient):
    """Unknown error reason falls back to AUTH_INVALID_TOKEN."""
    with patch("app.core.auth._get_clerk_sdk") as mock_get_sdk:
        mock_sdk = MagicMock()
        # Use a reason that isn't in the mapping
        mock_sdk.authenticate_request.return_value = _mock_request_state(
            is_signed_in=False,
            reason=TokenVerificationErrorReason.TOKEN_INVALID,
        )
        mock_get_sdk.return_value = mock_sdk

        response = client.get(
            "/protected", headers={"Authorization": "Bearer some-token"}
        )

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "AUTH_INVALID_TOKEN"


# ---------------------------------------------------------------------------
# Test 9: Principal roles extracted from org metadata
# ---------------------------------------------------------------------------


def test_roles_extracted_from_org_metadata(client: TestClient):
    """Roles are extracted from payload['o']['rol'] for org members."""
    payload_with_roles = {
        "sub": "user_abc",
        "sid": "sess_def",
        "org_id": "org_xyz",
        "o": {"rol": "org:admin"},
    }
    with patch("app.core.auth._get_clerk_sdk") as mock_get_sdk:
        mock_sdk = MagicMock()
        mock_sdk.authenticate_request.return_value = _mock_request_state(
            is_signed_in=True,
            payload=payload_with_roles,
        )
        mock_get_sdk.return_value = mock_sdk

        response = client.get(
            "/protected", headers={"Authorization": "Bearer fake-token"}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["roles"] == ["org:admin"]


# ---------------------------------------------------------------------------
# Test 10: No org_id → org_id is None
# ---------------------------------------------------------------------------


def test_no_org_id_returns_none(client: TestClient):
    """When payload has no org_id, Principal.org_id is None."""
    payload_no_org = {
        "sub": "user_abc",
        "sid": "sess_def",
    }
    with patch("app.core.auth._get_clerk_sdk") as mock_get_sdk:
        mock_sdk = MagicMock()
        mock_sdk.authenticate_request.return_value = _mock_request_state(
            is_signed_in=True,
            payload=payload_no_org,
        )
        mock_get_sdk.return_value = mock_sdk

        response = client.get(
            "/protected", headers={"Authorization": "Bearer fake-token"}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["org_id"] is None
    assert body["roles"] == []


# ---------------------------------------------------------------------------
# Test 11: Missing sub claim → 401 AUTH_INVALID_TOKEN
# ---------------------------------------------------------------------------


def test_missing_sub_claim_returns_401(client: TestClient):
    """Signed-in state with missing sub claim rejects with 401."""
    payload_no_sub = {"sid": "sess_def"}
    with patch("app.core.auth._get_clerk_sdk") as mock_get_sdk:
        mock_sdk = MagicMock()
        mock_sdk.authenticate_request.return_value = _mock_request_state(
            is_signed_in=True,
            payload=payload_no_sub,
        )
        mock_get_sdk.return_value = mock_sdk

        response = client.get(
            "/protected", headers={"Authorization": "Bearer fake-token"}
        )

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "AUTH_INVALID_TOKEN"


# ---------------------------------------------------------------------------
# Test 12: None payload → 401 AUTH_INVALID_TOKEN
# ---------------------------------------------------------------------------


def test_none_payload_returns_401(client: TestClient):
    """Signed-in state with None payload rejects with 401."""
    with patch("app.core.auth._get_clerk_sdk") as mock_get_sdk:
        mock_sdk = MagicMock()
        mock_sdk.authenticate_request.return_value = _mock_request_state(
            is_signed_in=True,
            payload=None,
        )
        mock_get_sdk.return_value = mock_sdk

        response = client.get(
            "/protected", headers={"Authorization": "Bearer fake-token"}
        )

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "AUTH_INVALID_TOKEN"
