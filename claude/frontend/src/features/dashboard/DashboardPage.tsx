/**
 * Real-time monitoring dashboard
 */

import React, { useEffect, useState } from 'react';
import { Row, Col, Typography, Empty } from 'antd';
import { DeviceCard } from './DeviceCard';
import { Device, devicesApi, getErrorMessage } from '../../lib/api';

const { Title } = Typography;

interface DeviceReading {
  device_id: number;
  device_name: string;
  unit: string;
  value: number;
  timestamp: string;
  status: string;
  thresholds: { warning?: number; critical?: number } | null;
}

export const DashboardPage: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [readings, setReadings] = useState<Map<number, DeviceReading>>(new Map());

  useEffect(() => {
    loadDevices();
    const websocket = connectWebSocket();

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadDevices = async () => {
    try {
      const response = await devicesApi.list();
      setDevices(response.devices);
    } catch (error) {
      console.error(getErrorMessage(error));
    }
  };

  const connectWebSocket = (): WebSocket => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/live`;

    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log('WebSocket connected');
    };

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'readings' && message.data) {
        const newReadings = new Map<number, DeviceReading>();
        message.data.forEach((reading: DeviceReading) => {
          newReadings.set(reading.device_id, reading);
        });
        setReadings(newReadings);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected, reconnecting in 5s...');
      setTimeout(() => {
        connectWebSocket();
      }, 5000);
    };

    return websocket;
  };

  if (devices.length === 0) {
    return (
      <Empty
        description="No devices configured. Create devices to start monitoring."
        style={{ marginTop: 50 }}
      />
    );
  }

  return (
    <div>
      <Title level={2} style={{ marginBottom: 24 }}>
        Live Monitoring Dashboard
      </Title>
      <Row gutter={[16, 16]}>
        {devices.map((device) => {
          const reading = readings.get(device.id);
          return (
            <Col key={device.id} xs={24} sm={24} md={12} lg={12} xl={6}>
              <DeviceCard device={device} reading={reading} />
            </Col>
          );
        })}
      </Row>
    </div>
  );
};
