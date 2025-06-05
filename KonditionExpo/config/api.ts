import { Platform } from 'react-native';
import Constants from 'expo-constants';

// API Configuration
export const API_CONFIG = {
  // Timeout for API requests (in milliseconds)
  TIMEOUT: 10000,
  
  // Token storage key
  TOKEN_KEY: 'access_token',
  
  // API endpoints
  ENDPOINTS: {
    LOGIN: '/login/access-token',
    SIGNUP: '/users/signup',
    TEST_TOKEN: '/login/test-token',
    USER_PROFILE: '/users/me',
    WORKOUTS: '/workouts',
    WORKOUT_BY_ID: (id: string) => `/workouts/${id}`,
    // Social endpoints
    SEARCH_USERS: '/social/users/search',
    FOLLOW_USER: (userId: string) => `/social/follow/${userId}`,
    UNFOLLOW_USER: (userId: string) => `/social/unfollow/${userId}`,
    GET_FOLLOWERS: '/social/followers',
    GET_FOLLOWING: '/social/following',
    IS_FOLLOWING: (userId: string) => `/social/is-following/${userId}`,
    USER_PROFILE_EXTENDED: (userId: string) => `/social/user/${userId}/profile`,
  },
};

// Platform-specific base URLs
const API_URLS = {
  // Web platform - works with localhost
  web: 'http://localhost:8000/api/v1',
  
  // iOS Simulator - works with localhost
  ios_simulator: 'http://localhost:8000/api/v1',
  
  // Android Emulator - needs special IP
  android_emulator: 'http://10.0.2.2:8000/api/v1',
  
  // Physical device/Expo Go - needs computer's IP address
  // You'll need to replace this with your computer's actual IP address
  physical_device: 'http://192.168.1.100:8000/api/v1', // Replace with your IP
};

// Detect platform and environment
const getPlatformType = () => {
  if (Platform.OS === 'web') {
    return 'web';
  }
  
  if (Platform.OS === 'ios') {
    // Check if running on simulator
    if (Constants.platform?.ios?.simulator) {
      return 'ios_simulator';
    }
    return 'physical_device';
  }
  
  if (Platform.OS === 'android') {
    // Check if running on emulator
    if (Constants.platform?.android?.isDevice === false) {
      return 'android_emulator';
    }
    return 'physical_device';
  }
  
  // Default fallback
  return 'web';
};

// Environment-specific configuration
export const getApiBaseUrl = () => {
  const platformType = getPlatformType();
  const baseUrl = API_URLS[platformType];
  
  // Log the detected platform and URL for debugging
  console.log(`Platform detected: ${Platform.OS} (${platformType})`);
  console.log(`Using API URL: ${baseUrl}`);
  
  return baseUrl;
};

// Helper function to manually set API URL for testing
export const setCustomApiUrl = (url: string) => {
  // This can be used for testing different endpoints
  API_URLS.physical_device = url;
  console.log(`Custom API URL set: ${url}`);
};

// Get current computer's IP address instructions
export const getNetworkSetupInstructions = () => {
  return {
    title: "Network Setup for Mobile Testing",
    instructions: [
      "1. Find your computer's IP address:",
      "   - macOS: System Preferences > Network > Advanced > TCP/IP",
      "   - Windows: ipconfig in Command Prompt",
      "   - Linux: ifconfig or ip addr",
      "",
      "2. Update the physical_device URL in config/api.ts:",
      "   Replace '192.168.1.100' with your computer's IP address",
      "",
      "3. Make sure your backend is running on 0.0.0.0:8000:",
      "   uvicorn app.main:app --host 0.0.0.0 --port 8000",
      "",
      "4. Ensure your computer and mobile device are on the same network",
      "",
      "Platform-specific URLs:",
      `- Web: ${API_URLS.web}`,
      `- iOS Simulator: ${API_URLS.ios_simulator}`,
      `- Android Emulator: ${API_URLS.android_emulator}`,
      `- Physical Device: ${API_URLS.physical_device}`,
    ]
  };
};