import React, { useState } from 'react';
import { Button, Card, Form, Input, Typography, Alert } from 'antd';
import { useAuth } from '../../store/auth';
import { useLocation, useNavigate } from 'react-router-dom';

export function LoginPage(): JSX.Element {
  const { login, error } = useAuth();
  const [form] = Form.useForm();
  const [localError, setLocalError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const loc = useLocation() as any;

  const onFinish = async () => {
    const { username, password } = await form.validateFields();
    setLocalError(null);
    setSubmitting(true);
    const ok = await login(username, password);
    setSubmitting(false);
    if (ok) {
      const dest = loc.state?.from?.pathname ?? '/';
      navigate(dest, { replace: true });
    } else {
      setLocalError('Invalid username or password');
    }
  };

  return (
    <div style={{ display: 'grid', placeItems: 'center', minHeight: '60vh' }}>
      <Card title={<Typography.Title level={3} style={{ margin: 0 }}>Sign in</Typography.Title>} style={{ width: 360 }}>
        {(localError || error) && (
          <Alert type="error" message={localError || error || ''} style={{ marginBottom: 16 }} />
        )}
        <Form form={form} layout="vertical" onFinish={onFinish}>
          <Form.Item name="username" label="Username" rules={[{ required: true }]}>
            <Input autoFocus autoComplete="username" />
          </Form.Item>
          <Form.Item name="password" label="Password" rules={[{ required: true }]}>
            <Input.Password autoComplete="current-password" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={submitting}>
            Sign in
          </Button>
        </Form>
      </Card>
    </div>
  );
}
