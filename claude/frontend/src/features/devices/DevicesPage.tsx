/**
 * Devices list page with CRUD operations
 */

import React, { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  message,
  Popconfirm,
  Card,
  Typography,
  Tag,
} from 'antd';
import { PlusOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  devicesApi,
  Device,
  CreateDeviceRequest,
  getErrorMessage,
} from '../../lib/api';
import { useCanModify } from '../../store/authStore';

const { Title } = Typography;
const { Option } = Select;

interface DeviceFormValues {
  name: string;
  description?: string;
  unit: string;
  sampling_interval: number;
  warning_threshold?: number;
  critical_threshold?: number;
  modbus_type: 'tcp' | 'rtu';
  modbus_host: string;
  modbus_port: number;
  modbus_register: number;
  modbus_data_type: string;
}

export const DevicesPage: React.FC = () => {
  const { t } = useTranslation();
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const canModify = useCanModify();

  useEffect(() => {
    loadDevices();
  }, []);

  const loadDevices = async () => {
    setLoading(true);
    try {
      const response = await devicesApi.list();
      setDevices(response.devices);
    } catch (error) {
      message.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (values: DeviceFormValues) => {
    try {
      const deviceData: CreateDeviceRequest = {
        name: values.name,
        description: values.description,
        unit: values.unit,
        sampling_interval: values.sampling_interval,
        thresholds:
          values.warning_threshold || values.critical_threshold
            ? {
                warning: values.warning_threshold,
                critical: values.critical_threshold,
              }
            : undefined,
        modbus_config: {
          type: values.modbus_type,
          host: values.modbus_host,
          port: values.modbus_port,
          register: values.modbus_register,
          data_type: values.modbus_data_type,
        },
      };

      await devicesApi.create(deviceData);
      message.success('Device created successfully');
      setIsModalOpen(false);
      form.resetFields();
      loadDevices();
    } catch (error) {
      message.error(getErrorMessage(error));
    }
  };

  const handleDelete = async (deviceId: number) => {
    try {
      await devicesApi.delete(deviceId);
      message.success('Device deleted successfully');
      loadDevices();
    } catch (error) {
      message.error(getErrorMessage(error));
    }
  };

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

  const columns = [
    {
      title: t('devices.id'),
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: t('devices.name'),
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: t('devices.unit'),
      dataIndex: 'unit',
      key: 'unit',
      width: 80,
    },
    {
      title: t('devices.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{t(`devices.${status}`)}</Tag>
      ),
    },
    {
      title: t('devices.samplingInterval'),
      dataIndex: 'sampling_interval',
      key: 'sampling_interval',
      width: 150,
      render: (interval: number) => `${interval}s`,
    },
    {
      title: t('devices.lastReading'),
      dataIndex: 'last_reading_at',
      key: 'last_reading_at',
      width: 180,
      render: (date: string | null) => (date ? new Date(date).toLocaleString() : '-'),
    },
    {
      title: t('devices.actions'),
      key: 'actions',
      width: 200,
      render: (_: unknown, record: Device) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/devices/${record.id}`)}
          >
            {t('devices.view')}
          </Button>
          {canModify && (
            <Popconfirm
              title={t('devices.deleteDevice')}
              description={t('devices.deleteConfirm')}
              onConfirm={() => handleDelete(record.id)}
              okText={t('common.yes')}
              cancelText={t('common.no')}
            >
              <Button type="link" danger icon={<DeleteOutlined />}>
                {t('devices.delete')}
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Card>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Title level={3}>{t('devices.title')}</Title>
        {canModify && (
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setIsModalOpen(true)}
          >
            {t('devices.createDevice')}
          </Button>
        )}
      </div>

      <Table
        columns={columns}
        dataSource={devices}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={t('devices.createNewDevice')}
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={{
            modbus_type: 'tcp',
            modbus_port: 502,
            modbus_data_type: 'float32',
            sampling_interval: 60,
          }}
        >
          <Form.Item
            name="name"
            label={t('devices.deviceName')}
            rules={[{ required: true, message: 'Please input device name!' }]}
          >
            <Input placeholder="e.g., Temperature Sensor 1" />
          </Form.Item>

          <Form.Item name="description" label={t('devices.description')}>
            <Input.TextArea rows={2} placeholder="Optional description" />
          </Form.Item>

          <Form.Item
            name="unit"
            label={t('devices.unit')}
            rules={[{ required: true, message: 'Please input unit!' }]}
          >
            <Input placeholder="e.g., °C, bar, RPM, %" />
          </Form.Item>

          <Form.Item
            name="sampling_interval"
            label={t('devices.samplingIntervalSeconds')}
            rules={[{ required: true, message: 'Please input sampling interval!' }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>

          <Title level={5}>{t('devices.thresholds')}</Title>
          <Form.Item name="warning_threshold" label={t('devices.warningThreshold')}>
            <InputNumber style={{ width: '100%' }} placeholder="Optional" />
          </Form.Item>

          <Form.Item name="critical_threshold" label={t('devices.criticalThreshold')}>
            <InputNumber style={{ width: '100%' }} placeholder="Optional" />
          </Form.Item>

          <Title level={5}>{t('devices.modbusConfiguration')}</Title>
          <Form.Item name="modbus_type" label={t('devices.type')} rules={[{ required: true }]}>
            <Select>
              <Option value="tcp">{t('devices.modbusType.tcp')}</Option>
              <Option value="rtu">{t('devices.modbusType.rtu')}</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="modbus_host"
            label={t('devices.host')}
            rules={[{ required: true, message: 'Please input host!' }]}
          >
            <Input placeholder="e.g., 192.168.1.100" />
          </Form.Item>

          <Form.Item
            name="modbus_port"
            label={t('devices.port')}
            rules={[{ required: true, message: 'Please input port!' }]}
          >
            <InputNumber min={1} max={65535} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="modbus_register"
            label={t('devices.registerAddress')}
            rules={[{ required: true, message: 'Please input register!' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="modbus_data_type"
            label={t('devices.dataType')}
            rules={[{ required: true }]}
          >
            <Select>
              <Option value="int16">INT16</Option>
              <Option value="uint16">UINT16</Option>
              <Option value="int32">INT32</Option>
              <Option value="uint32">UINT32</Option>
              <Option value="float32">FLOAT32</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => setIsModalOpen(false)}>{t('common.cancel')}</Button>
              <Button type="primary" htmlType="submit">
                {t('common.create')}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};
