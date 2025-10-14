/**
 * Main application layout with navigation and user menu
 */

import React from 'react';
import { Layout, Menu, Dropdown, Avatar, Typography, Space } from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  SettingOutlined,
  LogoutOutlined,
  DashboardOutlined,
  DatabaseOutlined,
  GroupOutlined,
  LineChartOutlined,
  GlobalOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore, useIsAdmin } from '../store/authStore';

const { Header, Content } = Layout;
const { Text } = Typography;

export const AppLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuthStore();
  const isAdmin = useIsAdmin();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  // User menu items
  const userMenuItems = [
    {
      key: 'profile',
      icon: <SettingOutlined />,
      label: t('nav.profile'),
      onClick: () => navigate('/profile'),
    },
    {
      key: 'language',
      icon: <GlobalOutlined />,
      label: 'Language',
      children: [
        {
          key: 'en-US',
          label: 'English',
          onClick: () => changeLanguage('en-US'),
        },
        {
          key: 'zh-CN',
          label: '中文',
          onClick: () => changeLanguage('zh-CN'),
        },
      ],
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: t('nav.logout'),
      onClick: handleLogout,
    },
  ];

  // Main navigation items
  const navItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: t('nav.dashboard'),
    },
    {
      key: '/devices',
      icon: <DatabaseOutlined />,
      label: t('nav.devices'),
    },
    {
      key: '/groups',
      icon: <GroupOutlined />,
      label: t('nav.groups'),
    },
    {
      key: '/history',
      icon: <LineChartOutlined />,
      label: t('nav.history'),
    },
    ...(isAdmin
      ? [
          {
            key: '/users',
            icon: <TeamOutlined />,
            label: t('nav.users'),
          },
        ]
      : []),
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: '#001529',
          padding: '0 24px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
          <Typography.Title
            level={4}
            style={{ color: 'white', margin: 0, marginRight: 32 }}
          >
            DDMS
          </Typography.Title>

          <Menu
            theme="dark"
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={navItems}
            onClick={({ key }) => navigate(key)}
            style={{ flex: 1, border: 'none' }}
          />
        </div>

        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <Space style={{ cursor: 'pointer' }}>
            <Avatar icon={<UserOutlined />} />
            <Text style={{ color: 'white' }}>
              {user?.username} ({user?.role})
            </Text>
          </Space>
        </Dropdown>
      </Header>

      <Content style={{ padding: '24px', background: '#f0f2f5' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <Outlet />
        </div>
      </Content>
    </Layout>
  );
};
