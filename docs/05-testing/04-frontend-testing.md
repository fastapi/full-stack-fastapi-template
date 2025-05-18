# Frontend Testing Guide

This guide explains how to write and run tests for the React frontend application using Playwright for end-to-end testing.

## Testing Approach

The frontend testing strategy focuses on end-to-end (E2E) tests using Playwright, which allows us to test the application as a user would interact with it through a real browser environment.

## Playwright Test Setup

### Directory Structure

Frontend tests are organized in the following structure:

```
frontend/
├── tests/
│   ├── auth.setup.ts              # Authentication setup for tests
│   ├── config.ts                  # Testing configuration
│   ├── login.spec.ts              # Login functionality tests
│   ├── reset-password.spec.ts     # Password reset tests
│   ├── sign-up.spec.ts            # Sign-up functionality tests
│   ├── user-settings.spec.ts      # User settings tests
│   └── utils/                     # Testing utilities
│       ├── mailcatcher.ts         # Email testing utilities
│       ├── privateApi.ts          # Backend API testing utilities 
│       ├── random.ts              # Random data generators
│       └── user.ts                # User management utilities
```

### Running Tests

To run Playwright tests:

```bash
# From frontend directory
# Run all tests
npx playwright test

# Run tests with UI for debugging
npx playwright test --ui

# Run a specific test file
npx playwright test tests/login.spec.ts

# Run a specific test by title
npx playwright test -g "should login with valid credentials"
```

## Writing Tests

### Authentication Setup

Playwright allows for authentication state to be shared across tests:

```typescript
// tests/auth.setup.ts
import { test as setup } from '@playwright/test';
import { ADMIN_USER, STANDARD_USER, storeTestUsers } from './utils/user';

// Store login state for reuse in tests
setup('authenticate admin', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(ADMIN_USER.email);
  await page.getByLabel('Password').fill(ADMIN_USER.password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  
  // Wait for successful login
  await page.waitForURL('/dashboard');
  
  // Store authentication state for "admin" user
  await page.context().storageState({ path: './auth-admin.json' });
});

// Similarly for standard user
setup('authenticate standard user', async ({ page }) => {
  // ...similar code for standard user
  await page.context().storageState({ path: './auth-user.json' });
});
```

### Example Test File

```typescript
// tests/login.spec.ts
import { test, expect } from '@playwright/test';
import { getRandomEmail } from './utils/random';

test.describe('Login', () => {
  test('should show validation errors for empty form', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Submit without filling form
    await page.getByRole('button', { name: 'Sign in' }).click();
    
    // Check validation messages
    await expect(page.getByText('Email is required')).toBeVisible();
    await expect(page.getByText('Password is required')).toBeVisible();
  });
  
  test('should show error for invalid credentials', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Fill invalid credentials
    await page.getByLabel('Email').fill('wrong@example.com');
    await page.getByLabel('Password').fill('wrongpassword');
    await page.getByRole('button', { name: 'Sign in' }).click();
    
    // Check error message
    await expect(page.getByText('Incorrect email or password')).toBeVisible();
  });
  
  test('should login with valid credentials', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Fill valid credentials
    await page.getByLabel('Email').fill('user@example.com');
    await page.getByLabel('Password').fill('password123');
    await page.getByRole('button', { name: 'Sign in' }).click();
    
    // Verify redirect to dashboard after successful login
    await page.waitForURL('/dashboard');
    
    // Verify user is logged in
    await expect(page.getByText('Welcome')).toBeVisible();
  });
});
```

### Testing Email Flows

For features that involve emails (like password reset), we use a mock email service:

```typescript
// tests/reset-password.spec.ts
import { test, expect } from '@playwright/test';
import { getRandomEmail } from './utils/random';
import { getLastEmail } from './utils/mailcatcher';

test.describe('Password Reset', () => {
  test('should send password reset email', async ({ page }) => {
    const testEmail = getRandomEmail();
    
    // Create test user
    // ...code to create user with API
    
    // Navigate to password reset page
    await page.goto('/recover-password');
    
    // Request password reset
    await page.getByLabel('Email').fill(testEmail);
    await page.getByRole('button', { name: 'Send Reset Link' }).click();
    
    // Verify success message
    await expect(page.getByText('Password reset link sent')).toBeVisible();
    
    // Get reset link from email
    const email = await getLastEmail(testEmail);
    const resetLink = extractResetLink(email.html);
    
    // Navigate to reset link
    await page.goto(resetLink);
    
    // Set new password
    await page.getByLabel('New Password').fill('newpassword123');
    await page.getByLabel('Confirm Password').fill('newpassword123');
    await page.getByRole('button', { name: 'Reset Password' }).click();
    
    // Verify success
    await expect(page.getByText('Password has been reset')).toBeVisible();
    
    // Try logging in with new password
    await page.goto('/login');
    await page.getByLabel('Email').fill(testEmail);
    await page.getByLabel('Password').fill('newpassword123');
    await page.getByRole('button', { name: 'Sign in' }).click();
    
    // Verify successful login
    await page.waitForURL('/dashboard');
  });
});
```

## Testing Utilities

### Random Data Generation

```typescript
// tests/utils/random.ts
export function getRandomEmail(): string {
  return `test-${Math.random().toString(36).substring(2, 10)}@example.com`;
}

export function getRandomName(): string {
  return `Test User ${Math.random().toString(36).substring(2, 7)}`;
}

export function getRandomPassword(): string {
  return `password-${Math.random().toString(36).substring(2, 10)}`;
}
```

### API Testing Utilities

```typescript
// tests/utils/privateApi.ts
import axios from 'axios';
import { API_URL } from '../config';

// Create an API client for backend operations during testing
export const apiClient = axios.create({
  baseURL: API_URL,
  validateStatus: () => true, // Don't throw on error status
});

// Create a test user directly via API
export async function createTestUser(email: string, password: string, fullName: string) {
  const response = await apiClient.post('/api/v1/users/open', {
    email,
    password,
    full_name: fullName,
  });
  
  return response.data;
}

// Get authentication token
export async function getAuthToken(email: string, password: string) {
  const response = await apiClient.post('/api/v1/login/access-token', {
    username: email,
    password,
  }, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  
  return response.data.access_token;
}
```

## Playwright Configuration

The Playwright configuration file (`playwright.config.ts`) sets up browsers, testing options, and global setup:

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  
  // Run tests in files in parallel
  fullyParallel: true,
  
  // Failing tests retries
  retries: process.env.CI ? 2 : 0,
  
  // Limit the number of failures
  maxFailures: process.env.CI ? 10 : undefined,
  
  // Reporters for CI and local development
  reporter: process.env.CI ? 'github' : 'html',
  
  // Shared settings for all projects
  use: {
    // Base URL for navigation
    baseURL: 'http://localhost:5173',
    
    // Record trace on failure
    trace: 'on-first-retry',
    
    // Record video on failure
    video: 'on-first-retry',
  },
  
  // Configure projects for different browsers
  projects: [
    // Setup project
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    
    // Main project - Chrome with auth
    {
      name: 'authenticated chrome',
      use: { 
        ...devices['Desktop Chrome'],
        storageState: './auth-user.json',
      },
      dependencies: ['setup'],
    },
    
    // Test with admin auth
    {
      name: 'authenticated admin',
      use: { 
        ...devices['Desktop Chrome'],
        storageState: './auth-admin.json',
      },
      dependencies: ['setup'],
    },
    
    // Test with Firefox
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    
    // Mobile Safari
    {
      name: 'mobile safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  
  // Local development web server
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
  },
});
```

## CI Integration

Frontend tests are integrated into CI/CD workflows:

```yaml
# .github/workflows/frontend-tests.yml
name: Frontend Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: 'frontend/package-lock.json'
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Install Playwright browsers
      run: |
        cd frontend
        npx playwright install --with-deps
    
    - name: Run Playwright tests
      run: |
        cd frontend
        npx playwright test
    
    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: playwright-report
        path: frontend/playwright-report/
        retention-days: 30
```

## Best Practices

1. **Use Page Objects**: Define page objects for complex pages to encapsulate selectors and actions
2. **Test User Flows**: Focus on complete user journeys rather than isolated UI components
3. **Keep Tests Independent**: Each test should be self-contained and not rely on state from other tests
4. **Realistic Test Data**: Use realistic data to simulate actual user behavior
5. **Visual Testing**: Consider adding visual regression tests for UI components
6. **Performance Testing**: Include performance metrics collection for critical user flows
7. **Accessibility Testing**: Add accessibility tests to ensure the application is accessible