# Authentication System Implementation

This document describes the complete authentication system implemented for the Kondition mobile app.

## Overview

The authentication system provides:
- User registration (signup)
- User login
- Secure token storage
- Protected routes
- Automatic token validation
- User session management
- Logout functionality

## Architecture

### Components

1. **API Service** (`services/api.ts`)
   - Handles all backend communication
   - Manages JWT token storage and retrieval
   - Provides authentication methods (login, signup, logout)
   - Handles API errors and network requests

2. **AuthContext** (`contexts/AuthContext.tsx`)
   - Manages global authentication state
   - Provides authentication methods to components
   - Handles token persistence across app restarts
   - Manages user profile data

3. **ProtectedRoute** (`components/ProtectedRoute.tsx`)
   - Protects authenticated routes
   - Redirects unauthenticated users to login
   - Handles navigation based on auth state

4. **Authentication Screens**
   - Login screen (`app/login.tsx`)
   - Signup screen (`app/signup.tsx`)
   - Profile screen with logout (`app/(tabs)/profile.tsx`)

### API Integration

The system integrates with the FastAPI backend using these endpoints:

- `POST /api/v1/login/access-token` - User login
- `POST /api/v1/users/signup` - User registration
- `POST /api/v1/login/test-token` - Token validation
- `GET /api/v1/users/me` - Get current user profile

### Token Management

- JWT tokens are stored securely using AsyncStorage
- Tokens are automatically included in API requests
- Token validation happens on app startup
- Invalid/expired tokens are automatically cleared

## Usage

### Login Flow

1. User enters email and password
2. App validates form data
3. API call to backend login endpoint
4. Token stored locally on success
5. User profile fetched and stored
6. Navigation to main app

### Signup Flow

1. User enters registration details
2. Form validation (email format, password strength)
3. API call to backend signup endpoint
4. Automatic login after successful signup
5. Navigation to main app

### Logout Flow

1. User confirms logout action
2. Token removed from local storage
3. Auth state cleared
4. Navigation to login screen

### Protected Routes

Routes are automatically protected based on authentication state:

- **Protected**: `/(tabs)`, `/workout`, `/profile`, `/home`
- **Public**: `/login`, `/signup`
- **Index**: Redirects based on auth state

## Configuration

API configuration is centralized in `config/api.ts`:

```typescript
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api/v1',
  TOKEN_KEY: 'access_token',
  ENDPOINTS: {
    LOGIN: '/login/access-token',
    SIGNUP: '/users/signup',
    // ...
  }
};
```

## Error Handling

- Network errors are caught and displayed to users
- Invalid credentials show appropriate error messages
- Token expiration is handled gracefully
- Loading states prevent multiple simultaneous requests

## Security Features

- Passwords are never stored locally
- JWT tokens are stored securely
- API requests include proper authentication headers
- Token validation on app startup
- Automatic logout on token expiration

## Testing

To test the authentication system:

1. Start the FastAPI backend server
2. Run the mobile app
3. Test signup with new user credentials
4. Test login with existing credentials
5. Verify protected route access
6. Test logout functionality
7. Verify token persistence across app restarts

## Future Enhancements

Potential improvements:
- Biometric authentication
- Remember me functionality
- Password reset flow
- Social login integration
- Refresh token implementation
- Enhanced security measures