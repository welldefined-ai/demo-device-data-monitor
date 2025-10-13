/**
 * Profile settings page - update password and language preference
 */

import React from 'react';
import { Card, Form, Input, Button, message, Typography, Select, Space } from 'antd';
import { LockOutlined, GlobalOutlined } from '@ant-design/icons';
import { useAuthStore } from '../../store/authStore';
import { usersApi, getErrorMessage, UpdateUserRequest } from '../../lib/api';

const { Title, Text } = Typography;
const { Option } = Select;

export const ProfilePage: React.FC = () => {
  const { user, checkAuth } = useAuthStore();
  const [passwordForm] = Form.useForm();
  const [preferencesForm] = Form.useForm();

  const handlePasswordChange = async (values: { password: string }) => {
    if (!user) return;

    try {
      const updateData: UpdateUserRequest = {
        password: values.password,
      };
      await usersApi.update(user.id, updateData);
      message.success('Password updated successfully');
      passwordForm.resetFields();
    } catch (error) {
      message.error(getErrorMessage(error));
    }
  };

  const handlePreferencesUpdate = async (values: { language_preference: string }) => {
    if (!user) return;

    try {
      const updateData: UpdateUserRequest = {
        language_preference: values.language_preference,
      };
      await usersApi.update(user.id, updateData);
      message.success('Language preference updated successfully');
      // Refresh user data to reflect changes
      await checkAuth();
    } catch (error) {
      message.error(getErrorMessage(error));
    }
  };

  if (!user) {
    return null;
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%', maxWidth: 800 }}>
      <Card>
        <Title level={3}>Profile Settings</Title>
        <Space direction="vertical" size="small">
          <Text strong>Username:</Text>
          <Text>{user.username}</Text>
          <Text strong style={{ marginTop: 8 }}>Role:</Text>
          <Text>{user.role.toUpperCase()}</Text>
          <Text strong style={{ marginTop: 8 }}>Account Created:</Text>
          <Text>{new Date(user.created_at).toLocaleString()}</Text>
        </Space>
      </Card>

      <Card title="Change Password">
        <Form
          form={passwordForm}
          layout="vertical"
          onFinish={handlePasswordChange}
          style={{ maxWidth: 400 }}
        >
          <Form.Item
            name="password"
            label="New Password"
            rules={[
              { required: true, message: 'Please input your new password!' },
              { min: 5, message: 'Password must be at least 5 characters' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Enter new password"
              autoComplete="new-password"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            label="Confirm Password"
            dependencies={['password']}
            rules={[
              { required: true, message: 'Please confirm your password!' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Passwords do not match!'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Confirm new password"
              autoComplete="new-password"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit">
              Update Password
            </Button>
          </Form.Item>
        </Form>
      </Card>

      <Card title="Language Preferences">
        <Form
          form={preferencesForm}
          layout="vertical"
          onFinish={handlePreferencesUpdate}
          initialValues={{ language_preference: user.language_preference }}
          style={{ maxWidth: 400 }}
        >
          <Form.Item
            name="language_preference"
            label="Language"
            rules={[{ required: true, message: 'Please select a language!' }]}
          >
            <Select prefix={<GlobalOutlined />}>
              <Option value="en-US">English (en-US)</Option>
              <Option value="zh-CN">Chinese (zh-CN)</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit">
              Update Language
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </Space>
  );
};
