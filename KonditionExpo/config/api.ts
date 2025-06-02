// API Configuration
export const API_CONFIG = {
  // Base URL for the FastAPI backend
  BASE_URL: 'http://localhost:8000/api/v1',
  
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
  },
};

// Environment-specific configuration
export const getApiBaseUrl = () => {
  // In a real app, you might want to use different URLs for different environments
  // For now, we'll use localhost for development
  return API_CONFIG.BASE_URL;
};