/**
 * User management page - list, create, and delete users
 */

import React, { useEffect, useState } from 'react';
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
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { usersApi, User, getErrorMessage, CreateUserRequest } from '../../lib/api';
import { useAuthStore } from '../../store/authStore';

const { Title } = Typography;
const { Option } = Select;

export const UsersPage: React.FC = () => {
  const { t } = useTranslation();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const currentUser = useAuthStore((state) => state.user);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await usersApi.list();
      setUsers(response.users);
    } catch (error) {
      message.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (values: CreateUserRequest) => {
    try {
      await usersApi.create(values);
      message.success('User created successfully');
      setIsModalOpen(false);
      form.resetFields();
      loadUsers();
    } catch (error) {
      message.error(getErrorMessage(error));
    }
  };

  const handleDelete = async (userId: number) => {
    try {
      await usersApi.delete(userId);
      message.success('User deleted successfully');
      loadUsers();
    } catch (error) {
      message.error(getErrorMessage(error));
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'owner':
        return 'gold';
      case 'admin':
        return 'blue';
      case 'viewer':
        return 'default';
      default:
        return 'default';
    }
  };

  const columns = [
    {
      title: t('users.id'),
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: t('users.username'),
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: t('users.role'),
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => <Tag color={getRoleColor(role)}>{t(`users.${role}`)}</Tag>,
    },
    {
      title: t('users.language'),
      dataIndex: 'language_preference',
      key: 'language_preference',
    },
    {
      title: t('users.createdAt'),
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: t('users.actions'),
      key: 'actions',
      render: (_: unknown, record: User) => {
        const canDelete = record.id !== currentUser?.id && record.role !== 'owner';
        return (
          <Space>
            {canDelete ? (
              <Popconfirm
                title="Delete user"
                description="Are you sure you want to delete this user?"
                onConfirm={() => handleDelete(record.id)}
                okText={t('common.yes')}
                cancelText={t('common.no')}
              >
                <Button type="link" danger icon={<DeleteOutlined />}>
                  {t('users.delete')}
                </Button>
              </Popconfirm>
            ) : (
              <Button type="link" disabled>
                {t('users.cannotDelete')}
              </Button>
            )}
          </Space>
        );
      },
    },
  ];

  return (
    <Card>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Title level={3}>{t('users.title')}</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setIsModalOpen(true)}
        >
          {t('users.createUser')}
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={users}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10 }}
      />

      <Modal
        title={t('users.createNewUser')}
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={{ role: 'viewer', language_preference: 'en-US' }}
        >
          <Form.Item
            name="username"
            label={t('users.username')}
            rules={[
              { required: true, message: 'Please input username!' },
              { min: 3, message: 'Username must be at least 3 characters' },
            ]}
          >
            <Input placeholder="Enter username" />
          </Form.Item>

          <Form.Item
            name="password"
            label={t('users.password')}
            rules={[
              { required: true, message: 'Please input password!' },
              { min: 5, message: 'Password must be at least 5 characters' },
            ]}
          >
            <Input.Password placeholder="Enter password" />
          </Form.Item>

          <Form.Item
            name="role"
            label={t('users.role')}
            rules={[{ required: true, message: 'Please select a role!' }]}
          >
            <Select>
              <Option value="viewer">{t('users.viewer')}</Option>
              <Option value="admin">{t('users.admin')}</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="language_preference"
            label={t('users.languagePreference')}
            rules={[{ required: true }]}
          >
            <Select>
              <Option value="en-US">English (en-US)</Option>
              <Option value="zh-CN">Chinese (zh-CN)</Option>
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
