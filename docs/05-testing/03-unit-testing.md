# Unit Testing Guide

This guide explains how to write and run unit tests for the modular monolith backend architecture.

## Unit Testing Approach

Unit tests verify that individual components work correctly in isolation. In our modular architecture, we focus on testing these key components:

1. **Domain Models**: Testing model validation, constraints, and behaviors
2. **Services**: Testing business logic and workflow orchestration
3. **Repositories**: Testing data access and persistence logic
4. **API Routes**: Testing request handling and response formatting

## Test Directory Structure

Unit tests follow the module structure of the application:

```
backend/tests/
├── conftest.py                # Common test fixtures
├── core/                      # Tests for core functionality
│   └── test_events.py         # Tests for the event system
└── modules/                   # Tests for specific modules
    ├── users/
    │   ├── domain/            # Tests for domain models
    │   │   └── test_user_events.py
    │   └── services/          # Tests for services
    │       └── test_user_service.py
    ├── items/
    │   ├── domain/
    │   └── services/
    └── email/
        └── services/
            └── test_email_event_handlers.py
```

## Writing Unit Tests

### Testing Domain Models

Domain model tests verify that models have the correct validation rules and behaviors:

```python
# tests/modules/users/domain/test_models.py
import pytest
from pydantic import ValidationError

from app.modules.users.domain.models import UserCreate, User


def test_user_create_validation():
    # Valid user data
    user_data = {
        "email": "test@example.com",
        "password": "securepassword",
        "full_name": "Test User"
    }
    user = UserCreate(**user_data)
    assert user.email == "test@example.com"
    
    # Invalid email
    with pytest.raises(ValidationError):
        UserCreate(
            email="invalid-email",
            password="securepassword",
            full_name="Test User"
        )
    
    # Short password
    with pytest.raises(ValidationError):
        UserCreate(
            email="test@example.com",
            password="short",
            full_name="Test User"
        )
```

### Testing Services

Service tests verify business logic with mocked dependencies:

```python
# tests/modules/users/services/test_user_service.py
import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.modules.users.domain.models import UserCreate, User
from app.modules.users.services.user_service import UserService
from app.shared.exceptions import NotFoundException


def test_create_user():
    # Mock the repository
    user_repo_mock = MagicMock()
    
    # Mock user returned by create method
    mock_user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password"
    )
    user_repo_mock.create.return_value = mock_user
    
    # Create service with mocked dependencies
    service = UserService(user_repo=user_repo_mock)
    
    # Create user data
    user_create = UserCreate(
        email="test@example.com",
        password="securepassword",
        full_name="Test User"
    )
    
    # Test with password hash patch to avoid actual hashing
    with patch("app.core.security.get_password_hash", return_value="hashed_password"):
        # Call the service method
        created_user = service.create_user(user_create)
        
        # Verify result
        assert created_user.email == "test@example.com"
        assert created_user.full_name == "Test User"
        
        # Verify repository was called correctly
        user_repo_mock.create.assert_called_once()
        created_model = user_repo_mock.create.call_args[0][0]
        assert created_model.email == "test@example.com"
        assert created_model.hashed_password == "hashed_password"


def test_get_user_by_id():
    # Mock the repository
    user_repo_mock = MagicMock()
    
    # Setup the mock for get_by_id
    user_id = uuid.uuid4()
    mock_user = User(
        id=user_id,
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password"
    )
    user_repo_mock.get_by_id.return_value = mock_user
    
    # Create service with mocked dependencies
    service = UserService(user_repo=user_repo_mock)
    
    # Call the service method
    user = service.get_by_id(user_id)
    
    # Verify result
    assert user.id == user_id
    assert user.email == "test@example.com"
    
    # Verify repository was called correctly
    user_repo_mock.get_by_id.assert_called_once_with(user_id)
    
    # Test not found scenario
    user_repo_mock.get_by_id.side_effect = NotFoundException("User not found")
    with pytest.raises(NotFoundException):
        service.get_by_id(uuid.uuid4())
```

### Testing Event Handlers

Event handler tests verify that events are processed correctly:

```python
# tests/modules/email/services/test_email_event_handlers.py
import uuid
from unittest.mock import MagicMock, patch

from app.modules.users.domain.events import UserCreatedEvent
from app.modules.email.services.email_event_handlers import handle_user_created_event


def test_handle_user_created_event():
    # Create a mock event
    event = UserCreatedEvent(
        user_id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User"
    )
    
    # Mock the email service
    email_service_mock = MagicMock()
    
    # Patch the get_email_service function to return our mock
    with patch(
        "app.modules.email.services.email_event_handlers.get_email_service",
        return_value=email_service_mock
    ):
        # Call the event handler
        handle_user_created_event(event)
        
        # Verify email service was called correctly
        email_service_mock.send_new_account_email.assert_called_once_with(
            email_to="test@example.com",
            username="Test User"
        )
```

## Running Tests

### Running All Tests

```bash
# From backend directory
bash scripts/test.sh

# With pytest directly
python -m pytest
```

### Running Specific Tests

```bash
# Run tests for a specific module
python -m pytest tests/modules/users/

# Run tests for a specific file
python -m pytest tests/modules/users/services/test_user_service.py

# Run a specific test
python -m pytest tests/modules/users/services/test_user_service.py::test_create_user
```

### Test Options

```bash
# Show more detailed output
python -m pytest -v

# Stop on first failure
python -m pytest -x

# Run only tests that match a pattern
python -m pytest -k "create"

# Show test coverage
python -m pytest --cov=app
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

```python
# tests/conftest.py
import pytest
from sqlmodel import Session, SQLModel

from app.core.db import get_engine, get_session
from app.main import app
from app.api.deps import get_current_user
from app.modules.users.domain.models import User


@pytest.fixture
def db_engine():
    """Create a clean database for each test."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    """Create a database session for testing."""
    with Session(db_engine) as session:
        yield session


@pytest.fixture
def test_user():
    """Create a test user."""
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password",
        is_active=True
    )
```

## Test Coverage

To generate a test coverage report:

```bash
python -m pytest --cov=app --cov-report=html
```

This generates an HTML coverage report in `htmlcov/`. Open `htmlcov/index.html` to view it.

## Best Practices

1. **Test Isolation**: Each test should be independent of others
2. **Mock Dependencies**: Use mocks to isolate the component being tested
3. **Test Edge Cases**: Include tests for error conditions and edge cases
4. **Test One Thing**: Each test should focus on one specific behavior
5. **Clear Test Names**: Use descriptive test names that explain what is being tested
6. **Avoid Test Logic**: Keep test logic simple; avoid complex conditionals in tests
7. **Cover Failures**: Test both success and failure scenarios