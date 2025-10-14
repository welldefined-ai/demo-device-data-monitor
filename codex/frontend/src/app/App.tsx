import React, { useEffect } from 'react';
import { BrowserRouter, Link, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { ConfigProvider, Layout, Menu, theme, Typography, Dropdown, Space, message } from 'antd';
import { useAuth } from '../store/auth';
import { LoginPage } from './pages/Login';
import { UsersPage } from './pages/Users';
import { ProfilePage } from './pages/Profile';
import { DevicesPage } from './pages/Devices';
import { GroupsPage } from './pages/Groups';

const { Header, Sider, Content } = Layout;

function Protected({ children, roles }: { children: React.ReactNode; roles?: Array<'owner' | 'admin' | 'viewer'> }) {
  const { user } = useAuth();
  const loc = useLocation();
  if (!user) return <Navigate to="/login" state={{ from: loc }} replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function HomePage() {
  return (
    <div>
      <Typography.Title level={3}>Welcome to DDMS</Typography.Title>
      <Typography.Paragraph>Use the navigation to get started.</Typography.Paragraph>
    </div>
  );
}

function AppShell() {
  const { user, fetchMe, logout } = useAuth();
  const [msgApi, contextHolder] = message.useMessage();

  useEffect(() => {
    void fetchMe();
  }, [fetchMe]);

  const onLogout = async () => {
    await logout();
    msgApi.success('Logged out');
  };

  const navItems = [
    { key: 'home', label: <Link to="/">Home</Link> },
    ...(user && (user.role === 'owner' || user.role === 'admin')
      ? [{ key: 'users', label: <Link to="/users">Users</Link> }]
      : []),
    ...(user ? [{ key: 'devices', label: <Link to="/devices">Devices</Link> }] : []),
    ...(user ? [{ key: 'groups', label: <Link to="/groups">Groups</Link> }] : []),
  ];

  const userMenu = {
    items: [
      { key: 'profile', label: <Link to="/profile">Profile</Link> },
      { type: 'divider' as const },
      { key: 'logout', label: <span onClick={onLogout}>Logout</span> },
    ],
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {contextHolder}
      <Sider breakpoint="lg" collapsedWidth={0}>
        <div style={{ color: '#fff', padding: 16, fontWeight: 600 }}>DDMS</div>
        <Menu theme="dark" mode="inline" items={navItems} />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', display: 'flex', justifyContent: 'flex-end', paddingInline: 24 }}>
          {user ? (
            <Dropdown menu={userMenu} trigger={["click"]}>
              <a onClick={(e) => e.preventDefault()}>
                <Space>{user.username}</Space>
              </a>
            </Dropdown>
          ) : (
            <Link to="/login">Login</Link>
          )}
        </Header>
        <Content style={{ padding: 24 }}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/users"
              element={
                <Protected roles={["owner", "admin"]}>
                  <UsersPage />
                </Protected>
              }
            />
            <Route
              path="/devices"
              element={
                <Protected>
                  <DevicesPage />
                </Protected>
              }
            />
            <Route
              path="/groups"
              element={
                <Protected>
                  <GroupsPage />
                </Protected>
              }
            />
            <Route
              path="/profile"
              element={
                <Protected>
                  <ProfilePage />
                </Protected>
              }
            />
            <Route path="/" element={<HomePage />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

function App(): JSX.Element {
  return (
    <ConfigProvider theme={{ algorithm: theme.defaultAlgorithm }}>
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
