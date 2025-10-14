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

// Device types
export interface ThresholdConfig {
  warning?: number;
  critical?: number;
}

export interface ModbusConfig {
  type: 'tcp' | 'rtu';
  host?: string;
  port?: number;
  serial_port?: string;
  baudrate?: number;
  register: number;
  data_type: string;
}

export interface Device {
  id: number;
  name: string;
  description?: string;
  unit: string;
  sampling_interval: number;
  thresholds?: ThresholdConfig;
  modbus_config: ModbusConfig;
  status: 'online' | 'offline' | 'error';
  last_reading_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateDeviceRequest {
  name: string;
  description?: string;
  unit: string;
  sampling_interval: number;
  thresholds?: ThresholdConfig;
  modbus_config: ModbusConfig;
}

export interface UpdateDeviceRequest {
  name?: string;
  description?: string;
  unit?: string;
  sampling_interval?: number;
  thresholds?: ThresholdConfig;
  modbus_config?: ModbusConfig;
}

export interface DevicesListResponse {
  devices: Device[];
  total: number;
}

// Group types
export interface Group {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  device_count?: number;
}

export interface CreateGroupRequest {
  name: string;
  description?: string;
}

export interface UpdateGroupRequest {
  name?: string;
  description?: string;
}

export interface GroupsListResponse {
  groups: Group[];
  total: number;
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

// Devices API
export const devicesApi = {
  list: async (): Promise<DevicesListResponse> => {
    const response = await api.get<DevicesListResponse>('/devices');
    return response.data;
  },

  create: async (deviceData: CreateDeviceRequest): Promise<Device> => {
    const response = await api.post<Device>('/devices', deviceData);
    return response.data;
  },

  get: async (deviceId: number): Promise<Device> => {
    const response = await api.get<Device>(`/devices/${deviceId}`);
    return response.data;
  },

  update: async (deviceId: number, deviceData: UpdateDeviceRequest): Promise<Device> => {
    const response = await api.patch<Device>(`/devices/${deviceId}`, deviceData);
    return response.data;
  },

  delete: async (deviceId: number): Promise<void> => {
    await api.delete(`/devices/${deviceId}`);
  },

  testConnection: async (deviceId: number): Promise<{ success: boolean; message: string }> => {
    const response = await api.post(`/devices/${deviceId}/test-connection`);
    return response.data;
  },
};

// Groups API
export const groupsApi = {
  list: async (): Promise<GroupsListResponse> => {
    const response = await api.get<GroupsListResponse>('/groups');
    return response.data;
  },

  create: async (groupData: CreateGroupRequest): Promise<Group> => {
    const response = await api.post<Group>('/groups', groupData);
    return response.data;
  },

  update: async (groupId: number, groupData: UpdateGroupRequest): Promise<Group> => {
    const response = await api.patch<Group>(`/groups/${groupId}`, groupData);
    return response.data;
  },

  delete: async (groupId: number): Promise<void> => {
    await api.delete(`/groups/${groupId}`);
  },

  assignDevice: async (groupId: number, deviceId: number): Promise<void> => {
    await api.post(`/groups/${groupId}/devices/${deviceId}`);
  },

  removeDevice: async (groupId: number, deviceId: number): Promise<void> => {
    await api.delete(`/groups/${groupId}/devices/${deviceId}`);
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
