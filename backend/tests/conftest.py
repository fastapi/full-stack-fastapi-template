"""Shared pytest fixtures for the backend test suite.

Modern fixtures (always available):
  - mock_supabase           — MagicMock Supabase client (function-scoped)
  - test_principal          — Principal with test user data (function-scoped)
  - client                  — TestClient with Supabase + auth overrides (function-scoped)
  - unauthenticated_client  — TestClient with only Supabase override (function-scoped)

Env var defaults are set BEFORE any app imports to satisfy module-level
Settings validation (SUPABASE_URL, SUPABASE_SERVICE_KEY, CLERK_SECRET_KEY).
"""

import os
from collections.abc import Generator
from unittest.mock import MagicMock

# IMPORTANT: these defaults MUST be set before any `from app.*` imports.
# app/core/config.py validates required settings at import time.
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-service-key")
os.environ.setdefault("CLERK_SECRET_KEY", "test-clerk-key")

import pytest
from fastapi.testclient import TestClient

from app.core.auth import get_current_principal
from app.core.supabase import get_supabase
from app.main import app
from app.models.auth import Principal

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TEST_USER_ID = "user_test123"
TEST_SESSION_ID = "sess_test"

# ---------------------------------------------------------------------------
# Modern fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_supabase() -> MagicMock:
    """Return a fresh MagicMock Supabase client for each test."""
    return MagicMock()


@pytest.fixture
def test_principal() -> Principal:
    """Return a Principal populated with deterministic test data."""
    return Principal(
        user_id=TEST_USER_ID,
        session_id=TEST_SESSION_ID,
        roles=[],
        org_id=None,
    )


@pytest.fixture
def client(
    mock_supabase: MagicMock,
    test_principal: Principal,
) -> Generator[TestClient, None, None]:
    """TestClient for the full app with Supabase and auth dependencies overridden.

    Both ``get_supabase`` and ``get_current_principal`` are replaced with
    test doubles so no real database or Clerk credentials are required.

    Dependency overrides are cleared on teardown to prevent state leakage
    between tests that share the same ``app`` instance.
    """
    app.dependency_overrides[get_supabase] = lambda: mock_supabase
    app.dependency_overrides[get_current_principal] = lambda: test_principal

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client(
    mock_supabase: MagicMock,
) -> Generator[TestClient, None, None]:
    """TestClient with only the Supabase dependency overridden.

    The real ``get_current_principal`` dependency runs, so any request to an
    authenticated endpoint without a valid Clerk JWT will receive a 401 response.

    Dependency overrides are cleared on teardown.
    """
    app.dependency_overrides[get_supabase] = lambda: mock_supabase

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client

    app.dependency_overrides.clear()
