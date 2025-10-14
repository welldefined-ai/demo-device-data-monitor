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
import {
  devicesApi,
  Device,
  CreateDeviceRequest,
  getErrorMessage,
} from '../../lib/api';
import { useCanModify } from '../../store/authStore';

const { Title } = Typography;
const { Option } = Select;

export const DevicesPage: React.FC = () => {
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

  const handleCreate = async (values: any) => {
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
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Unit',
      dataIndex: 'unit',
      key: 'unit',
      width: 80,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Sampling Interval',
      dataIndex: 'sampling_interval',
      key: 'sampling_interval',
      width: 150,
      render: (interval: number) => `${interval}s`,
    },
    {
      title: 'Last Reading',
      dataIndex: 'last_reading_at',
      key: 'last_reading_at',
      width: 180,
      render: (date: string | null) => (date ? new Date(date).toLocaleString() : '-'),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 200,
      render: (_: unknown, record: Device) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/devices/${record.id}`)}
          >
            View
          </Button>
          {canModify && (
            <Popconfirm
              title="Delete device"
              description="Are you sure? Historical data will be retained."
              onConfirm={() => handleDelete(record.id)}
              okText="Yes"
              cancelText="No"
            >
              <Button type="link" danger icon={<DeleteOutlined />}>
                Delete
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
        <Title level={3}>Devices</Title>
        {canModify && (
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setIsModalOpen(true)}
          >
            Create Device
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
        title="Create New Device"
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
            label="Device Name"
            rules={[{ required: true, message: 'Please input device name!' }]}
          >
            <Input placeholder="e.g., Temperature Sensor 1" />
          </Form.Item>

          <Form.Item name="description" label="Description">
            <Input.TextArea rows={2} placeholder="Optional description" />
          </Form.Item>

          <Form.Item
            name="unit"
            label="Unit"
            rules={[{ required: true, message: 'Please input unit!' }]}
          >
            <Input placeholder="e.g., °C, bar, RPM, %" />
          </Form.Item>

          <Form.Item
            name="sampling_interval"
            label="Sampling Interval (seconds)"
            rules={[{ required: true, message: 'Please input sampling interval!' }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>

          <Title level={5}>Thresholds</Title>
          <Form.Item name="warning_threshold" label="Warning Threshold">
            <InputNumber style={{ width: '100%' }} placeholder="Optional" />
          </Form.Item>

          <Form.Item name="critical_threshold" label="Critical Threshold">
            <InputNumber style={{ width: '100%' }} placeholder="Optional" />
          </Form.Item>

          <Title level={5}>Modbus Configuration</Title>
          <Form.Item name="modbus_type" label="Type" rules={[{ required: true }]}>
            <Select>
              <Option value="tcp">Modbus TCP</Option>
              <Option value="rtu">Modbus RTU</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="modbus_host"
            label="Host"
            rules={[{ required: true, message: 'Please input host!' }]}
          >
            <Input placeholder="e.g., 192.168.1.100" />
          </Form.Item>

          <Form.Item
            name="modbus_port"
            label="Port"
            rules={[{ required: true, message: 'Please input port!' }]}
          >
            <InputNumber min={1} max={65535} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="modbus_register"
            label="Register Address"
            rules={[{ required: true, message: 'Please input register!' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="modbus_data_type"
            label="Data Type"
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
              <Button onClick={() => setIsModalOpen(false)}>Cancel</Button>
              <Button type="primary" htmlType="submit">
                Create
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};
