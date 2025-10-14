/**
 * Groups list page with device assignment
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  Select,
  message,
  Popconfirm,
  Card,
  Typography,
  Tag,
} from 'antd';
import { PlusOutlined, DeleteOutlined, LinkOutlined, UnorderedListOutlined, MinusCircleOutlined, DashboardOutlined } from '@ant-design/icons';
import {
  groupsApi,
  devicesApi,
  Group,
  Device,
  CreateGroupRequest,
  getErrorMessage,
} from '../../lib/api';
import { useCanModify } from '../../store/authStore';

const { Title } = Typography;

export const GroupsPage: React.FC = () => {
  const navigate = useNavigate();
  const [groups, setGroups] = useState<Group[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [isManageModalOpen, setIsManageModalOpen] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null);
  const [groupDevices, setGroupDevices] = useState<Device[]>([]);
  const [form] = Form.useForm();
  const [assignForm] = Form.useForm();
  const canModify = useCanModify();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [groupsResponse, devicesResponse] = await Promise.all([
        groupsApi.list(),
        devicesApi.list(),
      ]);
      setGroups(groupsResponse.groups);
      setDevices(devicesResponse.devices);
    } catch (error) {
      message.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGroup = async (values: CreateGroupRequest) => {
    try {
      await groupsApi.create(values);
      message.success('Group created successfully');
      setIsCreateModalOpen(false);
      form.resetFields();
      loadData();
    } catch (error) {
      message.error(getErrorMessage(error));
    }
  };

  const handleDeleteGroup = async (groupId: number) => {
    try {
      await groupsApi.delete(groupId);
      message.success('Group deleted successfully');
      loadData();
    } catch (error) {
      message.error(getErrorMessage(error));
    }
  };

  const handleAssignDevice = async (values: { device_id: number }) => {
    if (!selectedGroup) return;

    try {
      await groupsApi.assignDevice(selectedGroup.id, values.device_id);
      message.success('Device assigned to group successfully');
      setIsAssignModalOpen(false);
      assignForm.resetFields();
      setSelectedGroup(null);
      loadData();
    } catch (error) {
      message.error(getErrorMessage(error));
    }
  };

  const handleManageDevices = async (group: Group) => {
    setSelectedGroup(group);
    setIsManageModalOpen(true);
    // Fetch devices in this group
    try {
      const devices = await groupsApi.getDevices(group.id);
      setGroupDevices(devices);
    } catch (error) {
      message.error(getErrorMessage(error));
      setGroupDevices([]);
    }
  };

  const handleRemoveDevice = async (deviceId: number) => {
    if (!selectedGroup) return;

    try {
      await groupsApi.removeDevice(selectedGroup.id, deviceId);
      message.success('Device removed from group successfully');
      loadData();
      // Refresh the devices list in modal
      setGroupDevices(groupDevices.filter(d => d.id !== deviceId));
    } catch (error) {
      message.error(getErrorMessage(error));
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
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (text: string) => text || '-',
    },
    {
      title: 'Devices',
      dataIndex: 'device_count',
      key: 'device_count',
      width: 100,
      render: (count: number) => <Tag color="blue">{count || 0} devices</Tag>,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 350,
      render: (_: unknown, record: Group) => (
        <Space>
          <Button
            type="link"
            icon={<DashboardOutlined />}
            onClick={() => navigate(`/groups/${record.id}/dashboard`)}
          >
            View Dashboard
          </Button>
          <Button
            type="link"
            icon={<UnorderedListOutlined />}
            onClick={() => handleManageDevices(record)}
          >
            Manage Devices
          </Button>
          {canModify && (
            <>
              <Button
                type="link"
                icon={<LinkOutlined />}
                onClick={() => {
                  setSelectedGroup(record);
                  setIsAssignModalOpen(true);
                }}
              >
                Assign
              </Button>
              <Popconfirm
                title="Delete group"
                description="Devices will remain in system. Continue?"
                onConfirm={() => handleDeleteGroup(record.id)}
                okText="Yes"
                cancelText="No"
              >
                <Button type="link" danger icon={<DeleteOutlined />}>
                  Delete
                </Button>
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Card>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Title level={3}>Device Groups</Title>
        {canModify && (
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setIsCreateModalOpen(true)}
          >
            Create Group
          </Button>
        )}
      </div>

      <Table
        columns={columns}
        dataSource={groups}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      {/* Create Group Modal */}
      <Modal
        title="Create New Group"
        open={isCreateModalOpen}
        onCancel={() => {
          setIsCreateModalOpen(false);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateGroup}
        >
          <Form.Item
            name="name"
            label="Group Name"
            rules={[{ required: true, message: 'Please input group name!' }]}
          >
            <Input placeholder="e.g., Tank Sensors" />
          </Form.Item>

          <Form.Item name="description" label="Description">
            <Input.TextArea rows={3} placeholder="Optional description" />
          </Form.Item>

          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => setIsCreateModalOpen(false)}>Cancel</Button>
              <Button type="primary" htmlType="submit">
                Create
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Assign Device Modal */}
      <Modal
        title="Assign Device to Group"
        open={isAssignModalOpen}
        onCancel={() => {
          setIsAssignModalOpen(false);
          assignForm.resetFields();
          setSelectedGroup(null);
        }}
        footer={null}
      >
        <Form
          form={assignForm}
          layout="vertical"
          onFinish={handleAssignDevice}
        >
          <Form.Item
            name="device_id"
            label="Select Device"
            rules={[{ required: true, message: 'Please select a device!' }]}
          >
            <Select
              placeholder="Select a device"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={devices.map((device) => ({
                value: device.id,
                label: `${device.name} (${device.unit})`,
              }))}
            />
          </Form.Item>

          <Form.Item>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => setIsAssignModalOpen(false)}>Cancel</Button>
              <Button type="primary" htmlType="submit">
                Assign
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Manage Devices Modal */}
      <Modal
        title={`Devices in ${selectedGroup?.name || 'Group'}`}
        open={isManageModalOpen}
        onCancel={() => {
          setIsManageModalOpen(false);
          setSelectedGroup(null);
          setGroupDevices([]);
        }}
        footer={null}
        width={600}
      >
        {groupDevices.length === 0 ? (
          <Typography.Text type="secondary">No devices in this group</Typography.Text>
        ) : (
          <Space direction="vertical" style={{ width: '100%' }}>
            {groupDevices.map((device) => (
              <Card key={device.id} size="small">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Space direction="vertical" size={0}>
                    <Typography.Text strong>{device.name}</Typography.Text>
                    <Typography.Text type="secondary">{device.unit}</Typography.Text>
                  </Space>
                  {canModify && (
                    <Popconfirm
                      title="Remove device from group"
                      description="Device will remain in system. Continue?"
                      onConfirm={() => handleRemoveDevice(device.id)}
                      okText="Yes"
                      cancelText="No"
                    >
                      <Button
                        type="link"
                        danger
                        icon={<MinusCircleOutlined />}
                        size="small"
                      >
                        Remove
                      </Button>
                    </Popconfirm>
                  )}
                </div>
              </Card>
            ))}
          </Space>
        )}
      </Modal>
    </Card>
  );
};
