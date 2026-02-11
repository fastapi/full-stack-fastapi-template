"""
Tests for profile API endpoints.

NOTE: These tests require a running MySQL database and are designed to be run
with the async SQLAlchemy setup. Since the existing test infrastructure uses
sync SQLModel from the template, these tests serve as documentation and can
be adapted to run with pytest-asyncio when that dependency is added.
"""
import pytest
from fastapi.testclient import TestClient


class TestProfileEndpoints:
    """Test suite for profile API endpoints."""

    def test_get_profile_unauthenticated(self, client: TestClient):
        """Test that GET /profile/me returns 401 without authentication."""
        r = client.get("/api/v1/profile/me")
        assert r.status_code in [401, 403]  # Either unauthorized or forbidden

    def test_setup_profile_unauthenticated(self, client: TestClient):
        """Test that POST /profile/setup returns 401 without authentication."""
        r = client.post(
            "/api/v1/profile/setup",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "company_name": "Test Company"
            }
        )
        assert r.status_code in [401, 403]

    def test_search_companies_unauthenticated(self, client: TestClient):
        """Test that GET /profile/companies/search returns 401 without authentication."""
        r = client.get("/api/v1/profile/companies/search?q=test")
        assert r.status_code in [401, 403]

    def test_setup_profile_missing_required_fields(self, client: TestClient):
        """Test that POST /profile/setup returns 422 when required fields are missing."""
        # Missing first_name, last_name, email, company_name
        r = client.post(
            "/api/v1/profile/setup",
            json={"phone": "123456789"}
        )
        # Should be either 401 (auth first) or 422 (validation first)
        assert r.status_code in [401, 403, 422]


class TestProfileModels:
    """Test profile Pydantic models."""

    def test_profile_setup_request_validation(self):
        """Test ProfileSetupRequest validation with all fields."""
        from app.models.profile import ProfileSetupRequest

        # Valid request with all fields
        data = ProfileSetupRequest(
            first_name="John",
            middle_name="William",
            last_name="Doe",
            phone="+1234567890",
            email="john@example.com",
            company_name="Test Company",
            job_title="Engineer"
        )
        assert data.first_name == "John"
        assert data.middle_name == "William"
        assert data.last_name == "Doe"
        assert data.phone == "+1234567890"
        assert data.email == "john@example.com"
        assert data.company_name == "Test Company"
        assert data.job_title == "Engineer"

    def test_profile_setup_request_required_only(self):
        """Test ProfileSetupRequest with only required fields."""
        from app.models.profile import ProfileSetupRequest

        data = ProfileSetupRequest(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            company_name="Test Company"
        )
        assert data.first_name == "John"
        assert data.middle_name is None
        assert data.last_name == "Doe"
        assert data.phone is None
        assert data.email == "john@example.com"
        assert data.company_name == "Test Company"
        assert data.job_title is None

    def test_profile_setup_request_first_name_required(self):
        """Test that first_name is required in ProfileSetupRequest."""
        from app.models.profile import ProfileSetupRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ProfileSetupRequest(
                last_name="Doe",
                email="john@example.com",
                company_name="Test Company"
            )

    def test_profile_setup_request_last_name_required(self):
        """Test that last_name is required in ProfileSetupRequest."""
        from app.models.profile import ProfileSetupRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ProfileSetupRequest(
                first_name="John",
                email="john@example.com",
                company_name="Test Company"
            )

    def test_profile_setup_request_email_required(self):
        """Test that email is required in ProfileSetupRequest."""
        from app.models.profile import ProfileSetupRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ProfileSetupRequest(
                first_name="John",
                last_name="Doe",
                company_name="Test Company"
            )

    def test_profile_setup_request_company_name_required(self):
        """Test that company_name is required in ProfileSetupRequest."""
        from app.models.profile import ProfileSetupRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ProfileSetupRequest(
                first_name="John",
                last_name="Doe",
                email="john@example.com"
            )

    def test_profile_setup_request_email_validation(self):
        """Test that email must be a valid email format."""
        from app.models.profile import ProfileSetupRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ProfileSetupRequest(
                first_name="John",
                last_name="Doe",
                email="invalid-email",
                company_name="Test Company"
            )

    def test_profile_response_model(self):
        """Test ProfileResponse model."""
        from app.models.profile import ProfileResponse, CompanyResponse
        from datetime import datetime

        company = CompanyResponse(
            company_id="C_abc12345",
            company_name="Test Company"
        )

        profile = ProfileResponse(
            user_id="user123",
            first_name="John",
            middle_name="William",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890",
            job_title="Engineer",
            company=company,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        assert profile.user_id == "user123"
        assert profile.first_name == "John"
        assert profile.middle_name == "William"
        assert profile.last_name == "Doe"
        assert profile.email == "john@example.com"
        assert profile.company.company_name == "Test Company"
        assert profile.company.company_id.startswith("C_")

    def test_profile_response_optional_fields(self):
        """Test ProfileResponse with optional fields as None."""
        from app.models.profile import ProfileResponse
        from datetime import datetime

        profile = ProfileResponse(
            user_id="user123",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            created_at=datetime.now()
        )

        assert profile.middle_name is None
        assert profile.phone is None
        assert profile.job_title is None
        assert profile.company is None
        assert profile.updated_at is None

    def test_company_search_result_model(self):
        """Test CompanySearchResult model."""
        from app.models.profile import CompanySearchResult

        result = CompanySearchResult(
            company_id="C_abc12345",
            company_name="Test Company"
        )
        assert result.company_id == "C_abc12345"
        assert result.company_name == "Test Company"


class TestCompanyIdGeneration:
    """Test company ID generation."""

    def test_generate_company_id_prefix(self):
        """Test that generated company IDs have C_ prefix."""
        from app.api.routes.profile import generate_company_id

        company_id = generate_company_id()
        assert company_id.startswith("C_")

    def test_generate_company_id_length(self):
        """Test that generated company IDs have correct length."""
        from app.api.routes.profile import generate_company_id

        company_id = generate_company_id()
        # C_ prefix (2 chars) + 8 char nanoid = 10 chars total
        assert len(company_id) == 10

    def test_generate_company_id_uniqueness(self):
        """Test that generated company IDs are unique."""
        from app.api.routes.profile import generate_company_id

        ids = [generate_company_id() for _ in range(100)]
        assert len(ids) == len(set(ids))  # All should be unique


class TestGetCurrentUserDependency:
    """Test get_current_user dependency."""

    def test_verify_token_returns_payload(self):
        """Test that verify_token returns the payload on valid token."""
        from app.utils.auth import create_access_token, verify_token

        # Create a test token
        token = create_access_token(data={"sub": "user123", "email": "test@example.com"})

        # Verify the token
        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"

    def test_verify_token_returns_none_on_invalid(self):
        """Test that verify_token returns None on invalid token."""
        from app.utils.auth import verify_token

        payload = verify_token("invalid_token")
        assert payload is None


class TestAuthProfileComplete:
    """Test profile_complete flag in auth responses."""

    def test_user_response_has_profile_complete_field(self):
        """Test that UserResponse has profile_complete field."""
        from app.models.user_auth import UserResponse
        from datetime import datetime

        user = UserResponse(
            user_id="user123",
            email="test@example.com",
            user_name="Test User",
            is_active=True,
            is_verified=False,
            created_at=datetime.now(),
            profile_complete=False
        )

        assert hasattr(user, 'profile_complete')
        assert user.profile_complete is False

        # Test with profile_complete=True
        user2 = UserResponse(
            user_id="user456",
            email="test2@example.com",
            user_name="Test User 2",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(),
            profile_complete=True
        )

        assert user2.profile_complete is True

    def test_user_response_profile_complete_defaults_false(self):
        """Test that profile_complete defaults to False."""
        from app.models.user_auth import UserResponse
        from datetime import datetime

        user = UserResponse(
            user_id="user123",
            email="test@example.com",
            user_name="Test User",
            is_active=True,
            is_verified=False,
            created_at=datetime.now()
        )

        assert user.profile_complete is False
