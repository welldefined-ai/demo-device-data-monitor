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
import { useTranslation } from 'react-i18next';
import { devicesApi, Device, getErrorMessage } from '../../lib/api';

const { Title } = Typography;

export const DeviceDetailPage: React.FC = () => {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [device, setDevice] = useState<Device | null>(null);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    if (id) {
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
      loadDevice(parseInt(id));
    }
  }, [id, navigate]);

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
        {t('devices.backToDevices')}
      </Button>

      <Card
        title={
          <Space>
            <Title level={3} style={{ margin: 0 }}>
              {device.name}
            </Title>
            <Tag color={getStatusColor(device.status)}>{t(`devices.${device.status}`)}</Tag>
          </Space>
        }
        extra={
          <Button
            icon={<ApiOutlined />}
            onClick={handleTestConnection}
            loading={testing}
          >
            {t('devices.testConnection')}
          </Button>
        }
      >
        <Descriptions column={2} bordered>
          <Descriptions.Item label={t('devices.id')}>{device.id}</Descriptions.Item>
          <Descriptions.Item label={t('devices.unit')}>{device.unit}</Descriptions.Item>
          <Descriptions.Item label={t('devices.samplingInterval')}>
            {device.sampling_interval} seconds
          </Descriptions.Item>
          <Descriptions.Item label={t('devices.status')}>
            <Tag color={getStatusColor(device.status)}>{t(`devices.${device.status}`)}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label={t('devices.lastReading')} span={2}>
            {device.last_reading_at
              ? new Date(device.last_reading_at).toLocaleString()
              : t('devices.noReadingsYet')}
          </Descriptions.Item>
          <Descriptions.Item label={t('devices.description')} span={2}>
            {device.description || '-'}
          </Descriptions.Item>
        </Descriptions>

        <Divider>{t('devices.thresholds')}</Divider>
        <Descriptions column={2} bordered>
          <Descriptions.Item label={t('devices.warningThreshold')}>
            {device.thresholds?.warning ?? '-'}
          </Descriptions.Item>
          <Descriptions.Item label={t('devices.criticalThreshold')}>
            {device.thresholds?.critical ?? '-'}
          </Descriptions.Item>
        </Descriptions>

        <Divider>{t('devices.modbusConfiguration')}</Divider>
        <Descriptions column={2} bordered>
          <Descriptions.Item label={t('devices.type')}>
            {t(`devices.modbusType.${device.modbus_config.type}`)}
          </Descriptions.Item>
          <Descriptions.Item label={t('devices.host')}>{device.modbus_config.host}</Descriptions.Item>
          <Descriptions.Item label={t('devices.port')}>{device.modbus_config.port}</Descriptions.Item>
          <Descriptions.Item label={t('devices.registerAddress')}>
            {device.modbus_config.register}
          </Descriptions.Item>
          <Descriptions.Item label={t('devices.dataType')} span={2}>
            {device.modbus_config.data_type}
          </Descriptions.Item>
        </Descriptions>

        <Divider />
        <Descriptions column={2} bordered size="small">
          <Descriptions.Item label={t('devices.created')}>
            {new Date(device.created_at).toLocaleString()}
          </Descriptions.Item>
          <Descriptions.Item label={t('devices.updated')}>
            {new Date(device.updated_at).toLocaleString()}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </Space>
  );
};
