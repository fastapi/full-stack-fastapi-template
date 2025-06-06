# Authentication Testing Guide

## Quick Start

### 1. Start the Backend

**Option A: Using Docker Compose (Recommended)**
```bash
cd KonditionFastAPI
docker compose watch
```

**Option B: Direct Python**
```bash
cd KonditionFastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Test on Different Platforms

#### Web (Should work immediately)
```bash
cd KonditionExpo
npm run web
```

#### iOS Simulator (Should work immediately)
```bash
npm run ios
```

#### Android Emulator (Should work immediately)
```bash
npm run android
```

#### Physical Device / Expo Go
1. Find your computer's IP address:
   - **macOS**: `ifconfig | grep "inet " | grep -v 127.0.0.1`
   - **Windows**: `ipconfig`
   - **Linux**: `ip addr show`

2. Start Expo:
   ```bash
   npm start
   ```

3. Open the app and go to **Profile > Developer Tools**

4. Set custom URL: `http://[YOUR_IP]:8000/api/v1`

5. Test the connection using the "Test API Connection" button

## Testing Checklist

### Signout Functionality
- [ ] Click signout button in profile screen
- [ ] Confirmation dialog appears
- [ ] Loading state shows "Signing Out..."
- [ ] Successfully redirects to login screen
- [ ] No errors in console

### Network Connectivity
- [ ] Web platform connects to localhost:8000
- [ ] iOS Simulator connects to localhost:8000
- [ ] Android Emulator connects to 10.0.2.2:8000
- [ ] Physical device connects with custom IP
- [ ] Error messages are user-friendly

### DevTools
- [ ] Developer Tools accessible from profile
- [ ] Shows current API URL
- [ ] Connection test works
- [ ] Custom URL can be set
- [ ] Quick URL buttons work

## Common Issues & Solutions

### "Network request failed"
1. Check if backend is running: `curl http://localhost:8000/docs`
2. Verify backend is accessible externally: `curl http://[YOUR_IP]:8000/docs`
3. Check firewall settings
4. Ensure devices are on same network

### Signout not working
1. Check console for error messages
2. Clear app data/cache
3. Restart the app
4. Check AsyncStorage permissions

### DevTools not showing
1. Make sure you're on the Profile tab
2. Scroll down to "Other" section
3. Look for blue "Developer Tools" text

## Debug Information

The app now logs detailed information to help with debugging:

```
Platform detected: ios (ios_simulator)
Using API URL: http://localhost:8000/api/v1
Making request to: http://localhost:8000/api/v1/login/access-token
Starting logout process...
Logout successful
```

Check the console/logs for these messages to understand what's happening.

## Network Setup for Mobile Testing

### Step 1: Find Your IP
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig
```

### Step 2: Start Backend with External Access
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 3: Configure Mobile App
1. Open app on mobile device
2. Go to Profile > Developer Tools
3. Enter: `http://[YOUR_IP]:8000/api/v1`
4. Test connection

### Step 4: Verify Setup
- Backend accessible: `http://[YOUR_IP]:8000/docs`
- API working: Test connection in DevTools
- Authentication: Try login/logout

## Platform-Specific Notes

### Web
- Uses localhost:8000 automatically
- No additional setup required
- Best for initial development

### iOS Simulator
- Uses localhost:8000 automatically
- Behaves like web platform
- Good for iOS-specific testing

### Android Emulator
- Uses 10.0.2.2:8000 automatically
- Special IP for Android emulator networking
- No manual configuration needed

### Physical Device
- Requires manual IP configuration
- Use DevTools for easy setup
- Must be on same network as computer

## Success Indicators

✅ **Authentication Working**:
- Login redirects to main app
- Logout shows confirmation and redirects to login
- User data loads correctly
- No network errors

✅ **Platform Compatibility**:
- Web works with localhost
- Mobile works with appropriate URLs
- Error messages are helpful
- DevTools provide easy testing

✅ **User Experience**:
- Loading states show during auth actions
- Clear error messages for failures
- Smooth navigation between screens
- No crashes or freezes