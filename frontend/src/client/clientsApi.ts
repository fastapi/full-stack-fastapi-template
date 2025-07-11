import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API Client instance for clients
const clientsApi = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/clients`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
clientsApi.interceptors.request.use(
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
clientsApi.interceptors.response.use(
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
export interface ClientFilters {
  skip?: number;
  limit?: number;
  client_type?: string;
  status?: string;
  search?: string;
}

export interface ClientData {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  client_type: 'buyer' | 'seller' | 'both';
  status: 'active' | 'inactive';
  notes?: string;
}

export interface Client extends ClientData {
  id: string;
  agent_id: string;
  created_at: string;
  updated_at: string;
}

export interface ClientsResponse {
  data: Client[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface ClientResponse {
  data: Client;
}

export interface ClientAnalyticsData {
  total_clients: number;
  active_clients: number;
  inactive_clients: number;
  buyers: number;
  sellers: number;
  both_types: number;
  clients_by_type: Array<{
    type: string;
    count: number;
    percentage: number;
  }>;
}

export interface ClientAnalyticsResponse {
  data: ClientAnalyticsData;
}

export interface ClientTypeOption {
  value: string;
  label: string;
}

export interface ClientTypeOptionsResponse {
  data: ClientTypeOption[];
}

// API Functions
export const getClients = async (filters: ClientFilters = {}): Promise<ClientsResponse> => {
  const response: AxiosResponse<ClientsResponse> = await clientsApi.get('', { params: filters });
  return response.data;
};

export const getClient = async (id: string): Promise<ClientResponse> => {
  const response: AxiosResponse<ClientResponse> = await clientsApi.get(`/${id}`);
  return response.data;
};

export const createClient = async (clientData: ClientData): Promise<ClientResponse> => {
  const response: AxiosResponse<ClientResponse> = await clientsApi.post('', clientData);
  return response.data;
};

export const updateClient = async (id: string, clientData: Partial<ClientData>): Promise<ClientResponse> => {
  const response: AxiosResponse<ClientResponse> = await clientsApi.patch(`/${id}`, clientData);
  return response.data;
};

export const deleteClient = async (id: string): Promise<void> => {
  await clientsApi.delete(`/${id}`);
};

export const getClientAnalytics = async (): Promise<ClientAnalyticsResponse> => {
  const response: AxiosResponse<ClientAnalyticsResponse> = await clientsApi.get('/analytics/dashboard');
  return response.data;
};

export const getClientTypeOptions = async (): Promise<ClientTypeOptionsResponse> => {
  const response: AxiosResponse<ClientTypeOptionsResponse> = await clientsApi.get('/types/options');
  return response.data;
};

export const getClientStatusOptions = async (): Promise<ClientTypeOptionsResponse> => {
  const response: AxiosResponse<ClientTypeOptionsResponse> = await clientsApi.get('/status/options');
  return response.data;
}; 