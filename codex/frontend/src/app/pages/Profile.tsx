import React from 'react';
import { Button, Card, Form, Input, message } from 'antd';
import { useAuth } from '../../store/auth';
import { api } from '../../lib/api';

export function ProfilePage(): JSX.Element {
  const { user, logout, fetchMe } = useAuth();
  const [form] = Form.useForm();
  const [msgApi, contextHolder] = message.useMessage();

  if (!user) return <></>;

  const onSubmit = async () => {
    const values = await form.validateFields();
    try {
      await api.patch(`/users/${user.id}`, { password: values.password });
      msgApi.success('Password updated');
      await fetchMe();
    } catch (e: any) {
      msgApi.error(e?.message || 'Failed to update');
    }
  };

  return (
    <Card title="Profile">
      {contextHolder}
      <Form form={form} layout="vertical" onFinish={onSubmit} style={{ maxWidth: 360 }}>
        <Form.Item label="Username"><Input value={user.username} disabled /></Form.Item>
        <Form.Item name="password" label="New Password" rules={[{ required: true }] }>
          <Input.Password autoComplete="new-password" />
        </Form.Item>
        <Button type="primary" htmlType="submit">Update Password</Button>
      </Form>
    </Card>
  );
}

