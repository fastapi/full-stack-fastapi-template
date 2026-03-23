"""Tests for weekly report download and subscription endpoints."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.db import get_db
from app.api.deps import get_current_user


def _mock_user(user_id="U_test123"):
    user = MagicMock()
    user.user_id = user_id
    user.email = "test@example.com"
    return user


def _mock_db():
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    return db


@pytest.fixture(autouse=True)
def _cleanup_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_download_report_not_found():
    mock_db = _mock_db()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: _mock_user()

    # brand access check returns a valid access row, then snapshot returns None
    access_row = MagicMock()
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=access_row)),   # brand access
        MagicMock(scalar_one_or_none=MagicMock(return_value=None)),          # snapshot
    ]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/v1/reports/weekly/brand123")
    assert r.status_code == 404
    assert "not yet available" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_download_report_forbidden():
    mock_db = _mock_db()
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: _mock_user()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/v1/reports/weekly/brand123")
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_download_report_ok(tmp_path):
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 test")

    snapshot = MagicMock()
    snapshot.pdf_path = str(pdf_file)
    snapshot.snapshot_data = {"brand_name": "Acme"}
    access_row = MagicMock()

    mock_db = _mock_db()
    mock_db.execute.side_effect = [
        MagicMock(scalar_one_or_none=MagicMock(return_value=access_row)),
        MagicMock(scalar_one_or_none=MagicMock(return_value=snapshot)),
    ]
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: _mock_user()

    with patch("app.api.routes.reports.get_report_storage") as mock_storage_factory:
        mock_storage = MagicMock()
        mock_storage.get.return_value = b"%PDF-1.4 test"
        mock_storage_factory.return_value = mock_storage

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.get("/api/v1/reports/weekly/brand123")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"


@pytest.mark.asyncio
async def test_get_subscription_returns_false_when_none():
    mock_db = _mock_db()
    mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: _mock_user()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/v1/brands/brand123/reports/weekly/subscription")
    assert r.status_code == 200
    assert r.json()["is_active"] is False


@pytest.mark.asyncio
async def test_set_subscription():
    mock_db = _mock_db()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: _mock_user()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.post(
            "/api/v1/brands/brand123/reports/weekly/subscription",
            json={"is_active": True},
        )
    assert r.status_code == 200
    assert r.json()["is_active"] is True
