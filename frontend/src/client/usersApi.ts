import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API Client instance for users
const usersApi = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/users`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
usersApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
usersApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login if unauthorized
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface UserFilters {
  skip?: number;
  limit?: number;
}

export interface UserData {
  email: string;
  password: string;
  full_name: string;
  role: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface UserUpdate {
  email?: string;
  password?: string;
  full_name?: string;
  role?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

export interface UsersResponse {
  data: User[];
  count: number;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

export interface MessageResponse {
  message: string;
}

// API Functions
export const getUsers = async (filters: UserFilters = {}): Promise<UsersResponse> => {
  const response: AxiosResponse<UsersResponse> = await usersApi.get('', { params: filters });
  return response.data;
};

export const getUser = async (id: string): Promise<UserResponse> => {
  const response: AxiosResponse<UserResponse> = await usersApi.get(`/${id}`);
  return response.data;
};

export const createUser = async (userData: UserData): Promise<UserResponse> => {
  const response: AxiosResponse<UserResponse> = await usersApi.post('', userData);
  return response.data;
};

export const updateUser = async (id: string, userData: UserUpdate): Promise<UserResponse> => {
  const response: AxiosResponse<UserResponse> = await usersApi.patch(`/${id}`, userData);
  return response.data;
};

export const deleteUser = async (id: string): Promise<MessageResponse> => {
  const response: AxiosResponse<MessageResponse> = await usersApi.delete(`/${id}`);
  return response.data;
};

export const getCurrentUser = async (): Promise<UserResponse> => {
  const response: AxiosResponse<UserResponse> = await usersApi.get('/me');
  return response.data;
};

export const updateCurrentUser = async (userData: Partial<UserData>): Promise<UserResponse> => {
  const response: AxiosResponse<UserResponse> = await usersApi.patch('/me', userData);
  return response.data;
}; 