"""
Utilities for blackbox testing using httpx against a running server.

This module provides helper functions and classes to interact with a running API server
without any knowledge of its implementation details. It exclusively uses HTTP requests
against the API's public endpoints.
"""
import json
import os
import time
import uuid
from typing import Dict, Optional, Any, Tuple, List, Union

import httpx

# Default server details - can be overridden with environment variables
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 30.0  # seconds

# Get server details from environment or use defaults
BASE_URL = os.environ.get("TEST_SERVER_URL", DEFAULT_BASE_URL)
TIMEOUT = float(os.environ.get("TEST_REQUEST_TIMEOUT", DEFAULT_TIMEOUT))

class BlackboxClient:
    """
    Client for blackbox testing of the API.
    
    This client uses httpx to make HTTP requests to a running API server,
    handling authentication tokens and providing helper methods for common operations.
    """
    
    def __init__(
        self, 
        base_url: str = BASE_URL, 
        timeout: float = TIMEOUT,
    ):
        """
        Initialize the blackbox test client.
        
        Args:
            base_url: Base URL of the API server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.token: Optional[str] = None
        self.client = httpx.Client(timeout=timeout)
        
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with client cleanup."""
        self.client.close()

    def url(self, path: str) -> str:
        """Build a full URL from a path."""
        # Ensure path starts with a slash
        if not path.startswith('/'):
            path = f'/{path}'
        return f"{self.base_url}{path}"
        
    def headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Build request headers, including auth token if available.
        
        Args:
            additional_headers: Additional headers to include
            
        Returns:
            Dictionary of headers
        """
        result = {"Content-Type": "application/json"}
        
        if self.token:
            result["Authorization"] = f"Bearer {self.token}"
            
        if additional_headers:
            result.update(additional_headers)
            
        return result
    
    # HTTP Methods
    
    def get(self, path: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """
        Make a GET request to the API.
        
        Args:
            path: API endpoint path
            params: URL parameters
            headers: Additional headers
            
        Returns:
            Response from the API
        """
        url = self.url(path)
        all_headers = self.headers(headers)
        return self.client.get(url, params=params, headers=all_headers)
    
    def post(self, path: str, json_data: Optional[Dict[str, Any]] = None,
             data: Optional[Dict[str, Any]] = None, 
             headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """
        Make a POST request to the API.
        
        Args:
            path: API endpoint path
            json_data: JSON data to send
            data: Form data to send
            headers: Additional headers
            
        Returns:
            Response from the API
        """
        url = self.url(path)
        all_headers = self.headers(headers)
        
        # Handle form data vs JSON data
        if data:
            # For form data, remove the Content-Type: application/json header
            if "Content-Type" in all_headers:
                all_headers.pop("Content-Type")
            return self.client.post(url, data=data, headers=all_headers)
        
        return self.client.post(url, json=json_data, headers=all_headers)
    
    def put(self, path: str, json_data: Dict[str, Any], 
            headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """
        Make a PUT request to the API.
        
        Args:
            path: API endpoint path
            json_data: JSON data to send
            headers: Additional headers
            
        Returns:
            Response from the API
        """
        url = self.url(path)
        all_headers = self.headers(headers)
        return self.client.put(url, json=json_data, headers=all_headers)
    
    def patch(self, path: str, json_data: Dict[str, Any],
              headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """
        Make a PATCH request to the API.
        
        Args:
            path: API endpoint path
            json_data: JSON data to send
            headers: Additional headers
            
        Returns:
            Response from the API
        """
        url = self.url(path)
        all_headers = self.headers(headers)
        return self.client.patch(url, json=json_data, headers=all_headers)
    
    def delete(self, path: str, headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """
        Make a DELETE request to the API.
        
        Args:
            path: API endpoint path
            headers: Additional headers
            
        Returns:
            Response from the API
        """
        url = self.url(path)
        all_headers = self.headers(headers)
        return self.client.delete(url, headers=all_headers)
    
    # Authentication helpers
    
    def sign_up(self, email: Optional[str] = None, password: str = "testpassword123",
                full_name: str = "Test User") -> Tuple[httpx.Response, Dict[str, str]]:
        """
        Sign up a new user.
        
        Args:
            email: User email (random if not provided)
            password: User password
            full_name: User full name
            
        Returns:
            Tuple of (response, credentials)
        """
        if not email:
            email = f"test-{uuid.uuid4()}@example.com"
            
        user_data = {
            "email": email,
            "password": password,
            "full_name": full_name
        }
        
        response = self.post("/api/v1/users/signup", json_data=user_data)
        return response, user_data
    
    def login(self, email: str, password: str) -> httpx.Response:
        """
        Log in a user and store the token.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Login response
        """
        login_data = {
            "username": email,
            "password": password
        }
        
        response = self.post("/api/v1/login/access-token", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data.get("access_token")
            
        return response
    
    def create_and_login_user(
        self, 
        email: Optional[str] = None, 
        password: str = "testpassword123", 
        full_name: str = "Test User"
    ) -> Dict[str, Any]:
        """
        Create a new user and log in.
        
        Args:
            email: User email (random if not provided)
            password: User password
            full_name: User full name
            
        Returns:
            Dict containing user data and credentials
        """
        signup_response, credentials = self.sign_up(
            email=email, 
            password=password, 
            full_name=full_name
        )
        
        if signup_response.status_code != 200:
            raise ValueError(f"Failed to sign up user: {signup_response.text}")
        
        login_response = self.login(credentials["email"], credentials["password"])
        
        if login_response.status_code != 200:
            raise ValueError(f"Failed to log in user: {login_response.text}")
            
        return {
            "signup_response": signup_response.json(),
            "credentials": credentials,
            "login_response": login_response.json(),
            "token": self.token
        }
    
    # Item management helpers
    
    def create_item(self, title: str, description: Optional[str] = None) -> httpx.Response:
        """
        Create a new item.
        
        Args:
            title: Item title
            description: Item description
            
        Returns:
            Response from the API
        """
        item_data = {
            "title": title
        }
        if description:
            item_data["description"] = description
            
        return self.post("/api/v1/items/", json_data=item_data)
    
    def wait_for_server(self, max_retries: int = 30, delay: float = 1.0) -> bool:
        """
        Wait for the server to be ready by polling the docs endpoint.
        
        Args:
            max_retries: Maximum number of retries
            delay: Delay between retries in seconds
            
        Returns:
            True if server is ready, False otherwise
        """
        docs_url = self.url("/docs")
        
        for attempt in range(max_retries):
            try:
                response = httpx.get(docs_url, timeout=self.timeout)
                if response.status_code == 200:
                    print(f"✓ Server ready at {self.base_url}")
                    return True
                
                print(f"Attempt {attempt + 1}/{max_retries}: Server returned {response.status_code}")
            except httpx.RequestError as e:
                print(f"Attempt {attempt + 1}/{max_retries}: {e}")
                
            time.sleep(delay)
            
        print(f"✗ Server not ready after {max_retries} attempts")
        return False


def random_email() -> str:
    """Generate a random email address for testing."""
    return f"test-{uuid.uuid4()}@example.com"


def random_string(length: int = 10) -> str:
    """Generate a random string for testing."""
    return str(uuid.uuid4())[:length]


def assert_uuid_format(value: str) -> bool:
    """Check if a string is a valid UUID format."""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False