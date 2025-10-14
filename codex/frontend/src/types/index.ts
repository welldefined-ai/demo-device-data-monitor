export type DeviceStatus = 'offline' | 'online' | 'error';

export type Device = {
  id: number;
  name: string;
  description: string;
  unit: string;
  sampling_interval: number;
  thresholds: Record<string, unknown>;
  modbus_config: Record<string, unknown>;
  status: DeviceStatus;
  last_reading_at: string | null;
  created_at: string;
  updated_at: string;
};

export type Group = {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
};

