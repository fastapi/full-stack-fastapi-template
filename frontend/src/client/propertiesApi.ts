import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API Client instance for properties
const propertiesApi = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/properties`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
propertiesApi.interceptors.request.use(
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
propertiesApi.interceptors.response.use(
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
export interface PropertyFilters {
  skip?: number;
  limit?: number;
  property_type?: string;
  status?: string;
  min_price?: number;
  max_price?: number;
  city?: string;
}

export interface PropertyData {
  title: string;
  description: string;
  property_type: 'apartment' | 'house' | 'commercial' | 'land' | 'office';
  status: 'available' | 'reserved' | 'sold' | 'rented' | 'under_construction';
  price: number;
  currency: string;
  area: number;
  bedrooms?: number;
  bathrooms?: number;
  parking_spaces?: number;
  address: string;
  city: string;
  state: string;
  country: string;
  zip_code?: string;
  features?: string[];
  amenities?: string[];
  images?: string[];
  latitude?: number;
  longitude?: number;
  year_built?: number;
  condition?: string;
}

export interface Property extends PropertyData {
  id: string;
  created_at: string;
  updated_at: string;
  views: number;
  favorites: number;
  visits: number;
}

export interface PropertiesResponse {
  data: Property[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface PropertyResponse {
  data: Property;
}

export interface AnalyticsData {
  total_properties: number;
  available_properties: number;
  sold_properties: number;
  rented_properties: number;
  total_inventory_value: number;
  average_property_price: number;
  total_sales_this_month: number;
  commission_earned_this_month: number;
  properties_by_city: Array<{
    city: string;
    count: number;
    average_price: number;
  }>;
  properties_by_type: Array<{
    type: string;
    count: number;
    percentage: number;
  }>;
}

export interface AnalyticsResponse {
  data: AnalyticsData;
}

// API Functions
export const getProperties = async (filters: PropertyFilters = {}): Promise<PropertiesResponse> => {
  const response: AxiosResponse<PropertiesResponse> = await propertiesApi.get('', { params: filters });
  return response.data;
};

export const getProperty = async (id: string): Promise<PropertyResponse> => {
  const response: AxiosResponse<PropertyResponse> = await propertiesApi.get(`/${id}`);
  return response.data;
};

export const createProperty = async (propertyData: PropertyData): Promise<PropertyResponse> => {
  const response: AxiosResponse<PropertyResponse> = await propertiesApi.post('', propertyData);
  return response.data;
};

export const updateProperty = async (id: string, propertyData: Partial<PropertyData>): Promise<PropertyResponse> => {
  const response: AxiosResponse<PropertyResponse> = await propertiesApi.patch(`/${id}`, propertyData);
  return response.data;
};

export const deleteProperty = async (id: string): Promise<void> => {
  await propertiesApi.delete(`/${id}`);
};

export const getPropertyAnalytics = async (): Promise<AnalyticsResponse> => {
  const response: AxiosResponse<AnalyticsResponse> = await propertiesApi.get('/analytics/dashboard');
  return response.data;
}; 