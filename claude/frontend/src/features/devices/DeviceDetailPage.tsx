/**
 * Device detail view page
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  message,
  Spin,
  Typography,
  Divider,
} from 'antd';
import { ArrowLeftOutlined, ApiOutlined } from '@ant-design/icons';
import { devicesApi, Device, getErrorMessage } from '../../lib/api';

const { Title } = Typography;

export const DeviceDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [device, setDevice] = useState<Device | null>(null);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    if (id) {
      loadDevice(parseInt(id));
    }
  }, [id]);

  const loadDevice = async (deviceId: number) => {
    setLoading(true);
    try {
      const data = await devicesApi.get(deviceId);
      setDevice(data);
    } catch (error) {
      message.error(getErrorMessage(error));
      navigate('/devices');
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async () => {
    if (!device) return;

    setTesting(true);
    try {
      const result = await devicesApi.testConnection(device.id);
      if (result.success) {
        message.success(result.message);
      } else {
        message.warning(result.message);
      }
    } catch (error) {
      message.error(getErrorMessage(error));
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 50 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!device) {
    return null;
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'success';
      case 'offline':
        return 'default';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/devices')}>
        Back to Devices
      </Button>

      <Card
        title={
          <Space>
            <Title level={3} style={{ margin: 0 }}>
              {device.name}
            </Title>
            <Tag color={getStatusColor(device.status)}>{device.status.toUpperCase()}</Tag>
          </Space>
        }
        extra={
          <Button
            icon={<ApiOutlined />}
            onClick={handleTestConnection}
            loading={testing}
          >
            Test Connection
          </Button>
        }
      >
        <Descriptions column={2} bordered>
          <Descriptions.Item label="ID">{device.id}</Descriptions.Item>
          <Descriptions.Item label="Unit">{device.unit}</Descriptions.Item>
          <Descriptions.Item label="Sampling Interval">
            {device.sampling_interval} seconds
          </Descriptions.Item>
          <Descriptions.Item label="Status">
            <Tag color={getStatusColor(device.status)}>{device.status.toUpperCase()}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Last Reading" span={2}>
            {device.last_reading_at
              ? new Date(device.last_reading_at).toLocaleString()
              : 'No readings yet'}
          </Descriptions.Item>
          <Descriptions.Item label="Description" span={2}>
            {device.description || '-'}
          </Descriptions.Item>
        </Descriptions>

        <Divider>Thresholds</Divider>
        <Descriptions column={2} bordered>
          <Descriptions.Item label="Warning Threshold">
            {device.thresholds?.warning ?? '-'}
          </Descriptions.Item>
          <Descriptions.Item label="Critical Threshold">
            {device.thresholds?.critical ?? '-'}
          </Descriptions.Item>
        </Descriptions>

        <Divider>Modbus Configuration</Divider>
        <Descriptions column={2} bordered>
          <Descriptions.Item label="Type">
            {device.modbus_config.type.toUpperCase()}
          </Descriptions.Item>
          <Descriptions.Item label="Host">{device.modbus_config.host}</Descriptions.Item>
          <Descriptions.Item label="Port">{device.modbus_config.port}</Descriptions.Item>
          <Descriptions.Item label="Register">
            {device.modbus_config.register}
          </Descriptions.Item>
          <Descriptions.Item label="Data Type" span={2}>
            {device.modbus_config.data_type}
          </Descriptions.Item>
        </Descriptions>

        <Divider />
        <Descriptions column={2} bordered size="small">
          <Descriptions.Item label="Created">
            {new Date(device.created_at).toLocaleString()}
          </Descriptions.Item>
          <Descriptions.Item label="Updated">
            {new Date(device.updated_at).toLocaleString()}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </Space>
  );
};
