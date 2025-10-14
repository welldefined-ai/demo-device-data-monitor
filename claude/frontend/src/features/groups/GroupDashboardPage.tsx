/**
 * Group-specific dashboard showing live monitoring for group devices
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Spin, message, Typography, Space, Empty, Row, Col } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { DeviceCard } from '../dashboard/DeviceCard';
import { Device, Group, getErrorMessage } from '../../lib/api';

const { Title, Text } = Typography;

interface DeviceReading {
  device_id: number;
  device_name: string;
  unit: string;
  value: number;
  timestamp: string;
  status: string;
  thresholds: { warning?: number; critical?: number } | null;
}

export const GroupDashboardPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [group, setGroup] = useState<Group | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [readings, setReadings] = useState<Map<number, DeviceReading>>(new Map());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadGroupData(parseInt(id));
      const websocket = connectWebSocket();

      return () => {
        if (websocket) {
          websocket.close();
        }
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const loadGroupData = async (groupId: number) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/groups/${groupId}/overview`, {
        credentials: 'include',
      }).then(res => res.json());

      setGroup(response.group);
      setDevices(response.devices);
    } catch (error) {
      message.error(getErrorMessage(error));
      navigate('/groups');
    } finally {
      setLoading(false);
    }
  };

  const connectWebSocket = (): WebSocket => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/live`;

    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log('WebSocket connected for group dashboard');
    };

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'readings' && message.data) {
        const newReadings = new Map<number, DeviceReading>();
        // Filter to only devices in this group
        const groupDeviceIds = devices.map(d => d.id);
        message.data.forEach((reading: DeviceReading) => {
          if (groupDeviceIds.includes(reading.device_id)) {
            newReadings.set(reading.device_id, reading);
          }
        });
        setReadings(newReadings);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected, reconnecting in 5s...');
      setTimeout(() => connectWebSocket(), 5000);
    };

    return websocket;
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 50 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!group || devices.length === 0) {
    return (
      <Card>
        <Empty description="No devices in this group" />
        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Button onClick={() => navigate('/groups')}>Back to Groups</Button>
        </div>
      </Card>
    );
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/groups')}>
            Back to Groups
          </Button>
          <div>
            <Title level={2} style={{ margin: 0 }}>{group.name}</Title>
            {group.description && <Text type="secondary">{group.description}</Text>}
          </div>
        </Space>
        <Text type="secondary">{devices.length} device(s)</Text>
      </div>

      <Card title="Live Monitoring">
        <Row gutter={[16, 16]}>
          {devices
            .sort((a, b) => a.id - b.id)
            .map((device) => {
              const reading = readings.get(device.id);
              return (
                <Col key={device.id} xs={24} sm={24} md={12} lg={12} xl={6}>
                  <DeviceCard device={device} reading={reading} />
                </Col>
              );
            })}
        </Row>
      </Card>

      <Card title="Historical View">
        <div style={{ textAlign: 'center', padding: 30 }}>
          <Text type="secondary">
            For historical analysis of these {devices.length} device(s), use the History page with multi-device selection.
          </Text>
          <br />
          <Button
            type="primary"
            onClick={() => navigate('/history')}
            style={{ marginTop: 16 }}
          >
            Go to History Page
          </Button>
        </div>
      </Card>
    </Space>
  );
};
