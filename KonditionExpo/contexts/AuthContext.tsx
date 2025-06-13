import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

type AuthContextType = {
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  token: string | null;
  loading: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false); // ⬅ NOT add loading

  const login = async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    formData.append('grant_type', 'password'); // Required by FastAPI even if blank
  
    const res = await fetch('http://localhost:8000/api/v1/login/access-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    });
  
    const data = await res.json();
    if (res.ok) {
      await AsyncStorage.setItem('access_token', data.access_token);
      setToken(data.access_token);
    } else {
      console.error('Failed Login Res:', res); // Log actual error from FastAPI
      console.error('Failed Login Data:', data); // Log actual error from FastAPI
      throw new Error(data.detail || 'Login failed');
    }
  };
  
  

  const logout = async () => {
    await AsyncStorage.removeItem('access_token');
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ login, logout, token, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
  
export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
};
