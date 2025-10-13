/**
 * API client for backend communication
 */

import axios, { AxiosError } from 'axios';

// API base URL - uses relative path that will be proxied by nginx
const API_BASE_URL = '/api';

// Create axios instance with default config
export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for sending cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  username: string;
  role: string;
}

export interface User {
  id: number;
  username: string;
  role: 'owner' | 'admin' | 'viewer';
  language_preference: string;
  created_at: string;
  updated_at: string;
}

export interface CreateUserRequest {
  username: string;
  password: string;
  role: 'owner' | 'admin' | 'viewer';
  language_preference?: string;
}

export interface UpdateUserRequest {
  username?: string;
  password?: string;
  role?: 'owner' | 'admin' | 'viewer';
  language_preference?: string;
}

export interface UsersListResponse {
  users: User[];
  total: number;
}

export interface ApiError {
  detail: string;
}

// Auth API
export const authApi = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login', credentials);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

// Users API
export const usersApi = {
  list: async (): Promise<UsersListResponse> => {
    const response = await api.get<UsersListResponse>('/users');
    return response.data;
  },

  create: async (userData: CreateUserRequest): Promise<User> => {
    const response = await api.post<User>('/users', userData);
    return response.data;
  },

  update: async (userId: number, userData: UpdateUserRequest): Promise<User> => {
    const response = await api.patch<User>(`/users/${userId}`, userData);
    return response.data;
  },

  delete: async (userId: number): Promise<void> => {
    await api.delete(`/users/${userId}`);
  },
};

// Error handling helper
export const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiError>;
    return axiosError.response?.data?.detail || axiosError.message || 'An error occurred';
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
};
