# Authentication System Documentation

## Overview

This document describes the authentication system implementation for the Kondition Expo app, including recent fixes for signout functionality and network connectivity issues.

## Architecture

### Components

1. **AuthContext** (`contexts/AuthContext.tsx`)
   - Manages authentication state
   - Provides login, signup, logout functions
   - Handles token storage and validation

2. **ProtectedRoute** (`components/ProtectedRoute.tsx`)
   - Controls navigation based on authentication state
   - Redirects unauthenticated users to login
   - Redirects authenticated users away from auth screens

3. **API Service** (`services/api.ts`)
   - Handles all API communication
   - Manages token storage in AsyncStorage
   - Provides platform-aware error handling

4. **API Configuration** (`config/api.ts`)
   - Platform-specific API URL configuration
   - Automatic platform detection
   - Development tools for testing

## Recent Fixes

### 1. Signout Functionality

**Issue**: Signout button was not working properly
**Solution**: 
- Enhanced error handling in logout function
- Added detailed logging for debugging
- Improved user feedback with specific error messages
- Ensured proper token cleanup

**Implementation**:
```typescript
const handleLogout = () => {
  Alert.alert(
    'Sign Out',
    'Are you sure you want to sign out?',
    [
      {
        text: 'Cancel',
        style: 'cancel',
      },
      {
        text: 'Sign Out',
        style: 'destructive',
        onPress: async () => {
          try {
            console.log('Starting logout process...');
            await logout();
            console.log('Logout successful');
            // Navigation handled by ProtectedRoute
          } catch (error) {
            console.error('Logout error:', error);
            Alert.alert(
              'Logout Error', 
              `Failed to sign out: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`
            );
          }
        },
      },
    ]
  );
};
```

### 2. Network Connectivity Issues

**Issue**: App worked on web but failed on mobile devices with "network failed" errors
**Solution**: 
- Implemented platform-specific API URLs
- Added automatic platform detection
- Created development tools for easy testing

**Platform-Specific URLs**:
- **Web**: `http://localhost:8000/api/v1`
- **iOS Simulator**: `http://localhost:8000/api/v1`
- **Android Emulator**: `http://10.0.2.2:8000/api/v1`
- **Physical Device**: `http://[YOUR_IP]:8000/api/v1`

### 3. Development Tools

Added a DevTools component accessible from the profile screen that provides:
- Current API URL display
- Connection testing
- Custom URL configuration
- Quick URL presets
- Setup instructions

## Testing Instructions

### Web Platform
1. Start the backend: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Start the web app: `npm run web`
3. Authentication should work with `localhost:8000`

### iOS Simulator
1. Start the backend: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Start the iOS simulator: `npm run ios`
3. Authentication should work with `localhost:8000`

### Android Emulator
1. Start the backend: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Start the Android emulator: `npm run android`
3. The app automatically uses `10.0.2.2:8000` for Android emulator

### Physical Device / Expo Go

1. **Find your computer's IP address**:
   - **macOS**: System Preferences > Network > Advanced > TCP/IP
   - **Windows**: Run `ipconfig` in Command Prompt
   - **Linux**: Run `ifconfig` or `ip addr`

2. **Update the API configuration**:
   - Open the app and go to Profile > Developer Tools
   - Enter your computer's IP: `http://[YOUR_IP]:8000/api/v1`
   - Or manually edit `config/api.ts` and update the `physical_device` URL

3. **Start the backend with external access**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. **Ensure network connectivity**:
   - Computer and mobile device must be on the same network
   - Firewall should allow connections on port 8000

## API Endpoints

- **Login**: `POST /api/v1/login/access-token`
- **Signup**: `POST /api/v1/users/signup`
- **Test Token**: `POST /api/v1/login/test-token`
- **User Profile**: `GET /api/v1/users/me`

## Error Handling

### Network Errors
- Connection failures show user-friendly messages
- Automatic retry suggestions
- Platform-specific troubleshooting

### Authentication Errors
- Invalid credentials handled gracefully
- Token expiration triggers automatic logout
- Clear error messages for users

### Development Debugging
- Console logging for all authentication actions
- Network request logging with URLs
- Error details preserved for debugging

## Troubleshooting

### Common Issues

1. **"Network request failed" on mobile**
   - Check if backend is running with `--host 0.0.0.0`
   - Verify IP address in DevTools
   - Ensure devices are on same network

2. **Signout not working**
   - Check console logs for error details
   - Verify AsyncStorage permissions
   - Try force-closing and reopening the app

3. **Login works but user data not loading**
   - Check token storage in AsyncStorage
   - Verify API endpoints are accessible
   - Check network connectivity

### Development Tips

1. **Use DevTools**: Access via Profile > Developer Tools for easy testing
2. **Check Console**: All authentication actions are logged
3. **Test Connection**: Use the "Test API Connection" button in DevTools
4. **Network Setup**: Follow the setup instructions in DevTools

## Security Considerations

- Tokens stored securely in AsyncStorage
- Automatic token validation on app start
- Secure token transmission with Bearer authentication
- Proper cleanup on logout

## Future Improvements

1. **Refresh Token Implementation**: Add automatic token refresh
2. **Biometric Authentication**: Add fingerprint/face ID support
3. **Offline Support**: Cache user data for offline access
4. **Enhanced Security**: Add certificate pinning for production