"""
Test client utilities for API testing.
"""
from typing import Dict, Any, Optional

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import User


class TestClientWrapper:
    """
    A wrapper around FastAPI TestClient that provides helper methods for testing.
    """
    
    def __init__(self, client: TestClient):
        self.client = client
        self.base_url = settings.API_V1_STR
    
    def get_url(self, path: str) -> str:
        """Get the full URL for a given API path."""
        return f"{self.base_url}{path}"
    
    def get(self, path: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Any:
        """Make a GET request to the API."""
        return self.client.get(self.get_url(path), headers=headers, **kwargs)
    
    def post(self, path: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Any:
        """Make a POST request to the API."""
        return self.client.post(self.get_url(path), headers=headers, **kwargs)
    
    def put(self, path: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Any:
        """Make a PUT request to the API."""
        return self.client.put(self.get_url(path), headers=headers, **kwargs)
    
    def patch(self, path: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Any:
        """Make a PATCH request to the API."""
        return self.client.patch(self.get_url(path), headers=headers, **kwargs)
    
    def delete(self, path: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Any:
        """Make a DELETE request to the API."""
        return self.client.delete(self.get_url(path), headers=headers, **kwargs)
    
    def login(self, email: str, password: str) -> Dict[str, str]:
        """
        Login with the given credentials and return the authentication headers.
        """
        login_data = {
            "username": email,
            "password": password,
        }
        r = self.client.post(
            self.get_url("/login/access-token"), 
            data=login_data
        )
        tokens = r.json()
        access_token = tokens["access_token"]
        return {"Authorization": f"Bearer {access_token}"}
    
    def login_user(self, user: User, password: str) -> Dict[str, str]:
        """
        Login with a user object and return the authentication headers.
        """
        return self.login(user.email, password)


def get_test_client_wrapper(client: TestClient) -> TestClientWrapper:
    """Get a TestClientWrapper instance for the given TestClient."""
    return TestClientWrapper(client)


def assert_successful_response(response, status_code=200):
    """Assert that a response was successful."""
    assert response.status_code == status_code, f"Response: {response.json()}"
    return response.json()


def assert_error_response(response, status_code=400):
    """Assert that a response was an error."""
    assert response.status_code == status_code, f"Response: {response.json()}"
    return response.json()