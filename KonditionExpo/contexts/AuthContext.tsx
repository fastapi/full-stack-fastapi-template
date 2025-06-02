import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiService, UserProfile, SignupRequest } from '../services/api';

type AuthContextType = {
  // Authentication state
  isAuthenticated: boolean;
  isLoading: boolean;
  user: UserProfile | null;
  token: string | null;
  
  // Authentication methods
  login: (email: string, password: string) => Promise<void>;
  signup: (userData: SignupRequest) => Promise<void>;
  logout: () => Promise<void>;
  
  // Utility methods
  checkAuthState: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // Check authentication state on app start
  useEffect(() => {
    checkAuthState();
  }, []);

  const checkAuthState = async () => {
    try {
      setIsLoading(true);
      
      // Get stored token
      const storedToken = await AsyncStorage.getItem('access_token');
      
      if (storedToken) {
        // Verify token is still valid by getting user profile
        const userProfile = await apiService.testToken();
        
        setToken(storedToken);
        setUser(userProfile);
        setIsAuthenticated(true);
      } else {
        // No token found
        setIsAuthenticated(false);
        setUser(null);
        setToken(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      // Token is invalid, clear everything
      await logout();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      
      // Call login API
      const authResponse = await apiService.login(email, password);
      
      // Store token
      await apiService.storeToken(authResponse.access_token);
      
      // Get user profile
      const userProfile = await apiService.getCurrentUser();
      
      // Update state
      setToken(authResponse.access_token);
      setUser(userProfile);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (userData: SignupRequest) => {
    try {
      setIsLoading(true);
      
      // Call signup API
      const userProfile = await apiService.signup(userData);
      
      // After successful signup, automatically log the user in
      await login(userData.email, userData.password);
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      
      // Remove token from storage
      await apiService.removeToken();
      
      // Clear state
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout failed:', error);
      // Even if logout fails, clear local state
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const value: AuthContextType = {
    isAuthenticated,
    isLoading,
    user,
    token,
    login,
    signup,
    logout,
    checkAuthState,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
