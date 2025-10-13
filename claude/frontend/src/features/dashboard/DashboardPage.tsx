/**
 * Dashboard home page
 */

import React from 'react';
import { Card, Typography, Space, Tag } from 'antd';
import { useAuthStore } from '../../store/authStore';

const { Title, Text } = Typography;

export const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();

  if (!user) {
    return null;
  }

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

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Card>
        <Title level={2}>Welcome to DDMS</Title>
        <Space direction="vertical" size="middle">
          <div>
            <Text type="secondary">Logged in as: </Text>
            <Text strong>{user.username}</Text>
          </div>
          <div>
            <Text type="secondary">Role: </Text>
            <Tag color={getRoleColor(user.role)}>{user.role.toUpperCase()}</Tag>
          </div>
        </Space>
      </Card>

      <Card title="Getting Started">
        <Space direction="vertical" size="small">
          <Text>Device Data Monitoring System is now ready to use.</Text>

          {user.role === 'owner' || user.role === 'admin' ? (
            <>
              <Text>As an {user.role}, you can:</Text>
              <ul>
                <li>Manage users (create, update, delete)</li>
                <li>Configure monitoring devices (coming in Iteration 2)</li>
                <li>View live data and historical trends (coming in Iterations 4-5)</li>
              </ul>
            </>
          ) : (
            <>
              <Text>As a viewer, you can:</Text>
              <ul>
                <li>View dashboards and monitoring data (coming in Iteration 4)</li>
                <li>Access historical charts and export data (coming in Iteration 5)</li>
              </ul>
            </>
          )}

          <Text type="secondary" style={{ marginTop: 16, display: 'block' }}>
            Current Iteration: 1 - Authentication & Authorization ✓
          </Text>
        </Space>
      </Card>
    </Space>
  );
};
