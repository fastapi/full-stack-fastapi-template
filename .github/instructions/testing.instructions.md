---
description: "Instructions for writing and maintaining tests for both backend (Pytest) and frontend (Playwright) in the FastAPI full-stack template."
applyTo: "**/tests/**/*"
---

# Testing Instructions

## Backend Tests (Pytest)

### Test Organization

```
backend/tests/
├── conftest.py           # Pytest fixtures
├── api/                  # API endpoint tests
│   └── routes/
│       ├── test_items.py
│       ├── test_users.py
│       └── test_login.py
├── crud/                 # CRUD operation tests
│   └── test_user.py
└── utils/                # Test utilities
    ├── user.py
    ├── item.py
    └── utils.py
```

### Fixtures (conftest.py)

Use shared fixtures from `conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

def test_example(client: TestClient, db: Session):
    # client: TestClient - FastAPI test client
    # db: Session - Database session
    pass

def test_with_auth(client: TestClient, superuser_token_headers: dict[str, str]):
    # superuser_token_headers: Auth headers for admin
    pass

def test_normal_user(client: TestClient, normal_user_token_headers: dict[str, str]):
    # normal_user_token_headers: Auth headers for regular user
    pass
```

### API Endpoint Tests

Test API endpoints in `backend/tests/api/routes/`:

```python
from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.models import ResourceCreate, User
from tests.utils.utils import random_string


def test_create_resource(
    client: TestClient, 
    superuser_token_headers: dict[str, str], 
    db: Session
) -> None:
    """Test creating a new resource."""
    data = {
        "title": random_string(),
        "description": "Test description",
    }
    response = client.post(
        "/api/v1/resources/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert "id" in content


def test_read_resource(
    client: TestClient, 
    superuser_token_headers: dict[str, str], 
    db: Session
) -> None:
    """Test reading a resource by ID."""
    # Create test resource
    resource = crud.create_resource(
        session=db,
        resource_in=ResourceCreate(title="Test", description="Test"),
        owner_id=superuser.id
    )
    
    # Read it back
    response = client.get(
        f"/api/v1/resources/{resource.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(resource.id)


def test_update_resource(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session
) -> None:
    """Test updating a resource."""
    # Create resource
    resource = crud.create_resource(...)
    
    # Update it
    update_data = {"title": "Updated Title"}
    response = client.put(
        f"/api/v1/resources/{resource.id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == update_data["title"]


def test_delete_resource(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session
) -> None:
    """Test deleting a resource."""
    resource = crud.create_resource(...)
    
    response = client.delete(
        f"/api/v1/resources/{resource.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(
        f"/api/v1/resources/{resource.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_permission_check(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session
) -> None:
    """Test permission checks - normal user cannot access other's resources."""
    # Create resource owned by someone else
    other_resource = crud.create_resource(...)
    
    # Try to access as normal user
    response = client.get(
        f"/api/v1/resources/{other_resource.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
```

### CRUD Tests

Test CRUD functions in `backend/tests/crud/`:

```python
from sqlmodel import Session

from app import crud
from app.models import ResourceCreate, ResourceUpdate
from tests.utils.utils import random_string


def test_create_resource(db: Session) -> None:
    """Test creating a resource via CRUD."""
    resource_in = ResourceCreate(
        title=random_string(),
        description="Test description",
    )
    resource = crud.create_resource(
        session=db,
        resource_in=resource_in,
        owner_id=owner.id,
    )
    assert resource.title == resource_in.title
    assert resource.owner_id == owner.id


def test_update_resource(db: Session) -> None:
    """Test updating a resource via CRUD."""
    # Create
    resource = crud.create_resource(...)
    
    # Update
    resource_in = ResourceUpdate(title="Updated")
    updated = crud.update_resource(
        session=db,
        db_obj=resource,
        resource_in=resource_in,
    )
    assert updated.title == "Updated"
    assert updated.id == resource.id


def test_get_resource_by_id(db: Session) -> None:
    """Test getting a resource by ID."""
    resource = crud.create_resource(...)
    
    fetched = crud.get_resource(session=db, resource_id=resource.id)
    assert fetched
    assert fetched.id == resource.id
```

### Test Utilities

Use utilities from `tests/utils/`:

```python
from tests.utils.utils import random_string, random_email

# Generate random test data
title = random_string()  # Random lowercase string
email = random_email()   # Random email address
```

### Best Practices for Backend Tests

1. **Use descriptive test names**: `test_create_resource_as_admin()`
2. **Test both success and failure cases**: 404, 403, 400 errors
3. **Use fixtures for setup**: Don't repeat database setup
4. **Clean up in fixtures**: Use conftest.py for cleanup
5. **Test permissions**: Superuser vs regular user access
6. **Use random data**: Avoid hard-coded test data
7. **Assert specific values**: Check IDs, fields, status codes
8. **Test edge cases**: Empty strings, None values, large inputs

### Running Backend Tests

```bash
# Run all tests
cd backend
bash scripts/test.sh

# Run specific test file
pytest tests/api/routes/test_items.py

# Run specific test
pytest tests/api/routes/test_items.py::test_create_item

# Run with coverage
pytest --cov=app tests/

# Run tests matching pattern
pytest -k "test_create"
```

## Frontend Tests (Playwright)

### Test Organization

```
frontend/tests/
├── auth.setup.ts         # Authentication setup
├── config.ts            # Test configuration
├── login.spec.ts        # Login tests
├── items.spec.ts        # Items feature tests
├── user-settings.spec.ts
└── utils/
    └── ...              # Test utilities
```

### Authentication Setup

Tests use authenticated sessions from `auth.setup.ts`:

```typescript
import { test as setup } from '@playwright/test'

// Setup runs before tests to create authenticated sessions
```

### Writing Frontend Tests

```typescript
import { test, expect } from '@playwright/test'

test.describe('Resources', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/resources')
  })

  test('should display resources list', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Resources')
    await expect(page.locator('[data-testid="resource-card"]')).toBeVisible()
  })

  test('should create new resource', async ({ page }) => {
    // Click create button
    await page.click('button:has-text("New Resource")')
    
    // Fill form
    await page.fill('input[name="title"]', 'Test Resource')
    await page.fill('textarea[name="description"]', 'Test description')
    
    // Submit
    await page.click('button[type="submit"]')
    
    // Verify success
    await expect(page.locator('text=Test Resource')).toBeVisible()
    await expect(page.locator('text=created successfully')).toBeVisible()
  })

  test('should edit resource', async ({ page }) => {
    // Click first resource
    await page.click('[data-testid="resource-card"]:first-child')
    
    // Click edit button
    await page.click('button:has-text("Edit")')
    
    // Update title
    await page.fill('input[name="title"]', 'Updated Title')
    await page.click('button:has-text("Save")')
    
    // Verify update
    await expect(page.locator('text=Updated Title')).toBeVisible()
  })

  test('should delete resource', async ({ page }) => {
    // Find and click delete button
    await page.click('[data-testid="resource-card"]:first-child button:has-text("Delete")')
    
    // Confirm deletion
    await page.click('button:has-text("Confirm")')
    
    // Verify deletion
    await expect(page.locator('text=deleted successfully')).toBeVisible()
  })

  test('should handle validation errors', async ({ page }) => {
    await page.click('button:has-text("New Resource")')
    
    // Try to submit without filling required fields
    await page.click('button[type="submit"]')
    
    // Check for error messages
    await expect(page.locator('text=Title is required')).toBeVisible()
  })

  test('should paginate results', async ({ page }) => {
    // Assuming pagination exists
    await page.click('button:has-text("Next")')
    
    // Verify URL changed
    await expect(page).toHaveURL(/page=2/)
  })
})
```

### Testing Patterns

#### Form Testing
```typescript
test('should submit form correctly', async ({ page }) => {
  await page.goto('/form-page')
  
  // Fill all fields
  await page.fill('input[name="name"]', 'Test Name')
  await page.selectOption('select[name="category"]', 'option1')
  await page.check('input[type="checkbox"]')
  
  // Submit and verify
  await page.click('button[type="submit"]')
  await expect(page.locator('.success-message')).toBeVisible()
})
```

#### Navigation Testing
```typescript
test('should navigate between pages', async ({ page }) => {
  await page.goto('/')
  
  // Click navigation link
  await page.click('a[href="/resources"]')
  
  // Verify navigation
  await expect(page).toHaveURL('/resources')
  await expect(page.locator('h1')).toContainText('Resources')
})
```

#### Authentication Testing
```typescript
test('should protect authenticated routes', async ({ page }) => {
  // Try to access protected page without auth
  await page.goto('/admin')
  
  // Should redirect to login
  await expect(page).toHaveURL('/login')
})

test('should allow access with authentication', async ({ page }) => {
  // Login is handled by auth.setup.ts
  await page.goto('/admin')
  
  // Should access the page
  await expect(page.locator('h1')).toContainText('Admin')
})
```

#### API Testing (via UI)
```typescript
test('should handle API errors gracefully', async ({ page }) => {
  // Simulate error by providing invalid data
  await page.goto('/resources')
  await page.click('button:has-text("New Resource")')
  
  // Invalid data
  await page.fill('input[name="title"]', 'x'.repeat(1000))
  await page.click('button[type="submit"]')
  
  // Should show error message
  await expect(page.locator('.error-message')).toBeVisible()
})
```

### Best Practices for Frontend Tests

1. **Use data-testid attributes**: Add to key elements for stable selectors
2. **Wait for elements**: Use `await expect().toBeVisible()`
3. **Test user journeys**: Not just individual actions
4. **Test error states**: Invalid inputs, API failures
5. **Test accessibility**: Keyboard navigation, screen readers
6. **Use page objects**: For complex pages (optional)
7. **Keep tests independent**: Each test should work in isolation
8. **Mock external APIs**: When needed (via Playwright)

### Running Frontend Tests

```bash
cd frontend

# Run all tests
bun run test:e2e

# Run in headed mode (see browser)
bun run test:e2e --headed

# Run specific test file
bun run test:e2e tests/items.spec.ts

# Run in debug mode
bun run test:e2e --debug

# Run with UI mode
bun run test:e2e --ui
```

## Test Data Best Practices

### Backend
- Use `random_string()` and `random_email()` from test utils
- Create data in test, clean up in fixtures
- Don't rely on seed data
- Test with realistic data sizes

### Frontend
- Use consistent test data
- Clean up after tests
- Don't hard-code IDs or timestamps
- Test with various screen sizes

## Continuous Integration

Tests run automatically on:
- Pull requests
- Pushes to main branch
- Via GitHub Actions (see `.github/workflows/`)

Make sure all tests pass before committing!

## Writing New Tests

### For New Backend Feature
1. Add CRUD tests in `tests/crud/`
2. Add API tests in `tests/api/routes/`
3. Test permissions (superuser vs regular user)
4. Test error cases (404, 403, 400)
5. Run: `bash scripts/test.sh`

### For New Frontend Feature
1. Add test file in `tests/`
2. Test main user flows
3. Test form validation
4. Test error states
5. Run: `bun run test:e2e`

## Common Test Patterns

### Backend: Test with Different Users
```python
def test_as_superuser(client: TestClient, superuser_token_headers: dict):
    # Test admin functionality
    pass

def test_as_normal_user(client: TestClient, normal_user_token_headers: dict):
    # Test regular user functionality
    pass

def test_without_auth(client: TestClient):
    # Test unauthenticated access (should fail)
    response = client.get("/api/v1/protected")
    assert response.status_code == 401
```

### Frontend: Test Loading States
```typescript
test('should show loading state', async ({ page }) => {
  await page.goto('/resources')
  
  // Should show loading initially
  await expect(page.locator('text=Loading')).toBeVisible()
  
  // Should show content after loading
  await expect(page.locator('[data-testid="resource-card"]')).toBeVisible()
})
```

### Frontend: Test Dark Mode
```typescript
test('should work in dark mode', async ({ page }) => {
  await page.goto('/resources')
  
  // Toggle dark mode
  await page.click('button[aria-label="Toggle theme"]')
  
  // Verify dark mode applied
  await expect(page.locator('html')).toHaveClass(/dark/)
})
```
