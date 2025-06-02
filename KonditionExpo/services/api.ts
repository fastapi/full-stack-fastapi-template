import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_CONFIG, getApiBaseUrl } from '../config/api';

// Types for API requests and responses
export interface LoginRequest {
  username: string; // FastAPI OAuth2 expects 'username' field for email
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface ApiError {
  detail: string;
}

// API Service Class
class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = getApiBaseUrl()) {
    this.baseUrl = baseUrl;
  }

  // Helper method to get stored token
  private async getToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(API_CONFIG.TOKEN_KEY);
    } catch (error) {
      console.error('Error getting token:', error);
      return null;
    }
  }

  // Helper method to make authenticated requests
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const token = await this.getToken();

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    // Add authorization header if token exists
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const config: RequestInit = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData: ApiError = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network request failed');
    }
  }

  // Authentication Methods
  async login(email: string, password: string): Promise<AuthResponse> {
    // FastAPI OAuth2 expects form data with 'username' field
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${this.baseUrl}${API_CONFIG.ENDPOINTS.LOGIN}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }

    return await response.json();
  }

  async signup(userData: SignupRequest): Promise<UserProfile> {
    return this.makeRequest<UserProfile>(API_CONFIG.ENDPOINTS.SIGNUP, {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser(): Promise<UserProfile> {
    return this.makeRequest<UserProfile>(API_CONFIG.ENDPOINTS.USER_PROFILE);
  }

  async testToken(): Promise<UserProfile> {
    return this.makeRequest<UserProfile>(API_CONFIG.ENDPOINTS.TEST_TOKEN, {
      method: 'POST',
    });
  }

  // Token Management
  async storeToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem(API_CONFIG.TOKEN_KEY, token);
    } catch (error) {
      console.error('Error storing token:', error);
      throw new Error('Failed to store authentication token');
    }
  }

  async removeToken(): Promise<void> {
    try {
      await AsyncStorage.removeItem(API_CONFIG.TOKEN_KEY);
    } catch (error) {
      console.error('Error removing token:', error);
      throw new Error('Failed to remove authentication token');
    }
  }

  async hasValidToken(): Promise<boolean> {
    try {
      const token = await this.getToken();
      if (!token) return false;

      // Test if token is still valid
      await this.testToken();
      return true;
    } catch (error) {
      // Token is invalid or expired
      await this.removeToken();
      return false;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;