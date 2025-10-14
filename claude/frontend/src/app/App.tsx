/**
 * Main application component with routing
 */

import { useEffect } from 'react';
import { ConfigProvider } from 'antd';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from '../features/auth/LoginPage';
import { DashboardPage } from '../features/dashboard/DashboardPage';
import { UsersPage } from '../features/users/UsersPage';
import { ProfilePage } from '../features/profile/ProfilePage';
import { DevicesPage } from '../features/devices/DevicesPage';
import { DeviceDetailPage } from '../features/devices/DeviceDetailPage';
import { GroupsPage } from '../features/groups/GroupsPage';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { AppLayout } from '../components/AppLayout';
import { useAuthStore } from '../store/authStore';

function App() {
  const { checkAuth } = useAuthStore();

  // Check authentication status on app mount
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <ConfigProvider>
      <BrowserRouter>
        <Routes>
          {/* Public route */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected routes with app layout */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              {/* Dashboard - accessible to all authenticated users */}
              <Route path="/" element={<DashboardPage />} />

              {/* Devices - accessible to all authenticated users */}
              <Route path="/devices" element={<DevicesPage />} />
              <Route path="/devices/:id" element={<DeviceDetailPage />} />

              {/* Groups - accessible to all authenticated users */}
              <Route path="/groups" element={<GroupsPage />} />

              {/* Profile - accessible to all authenticated users */}
              <Route path="/profile" element={<ProfilePage />} />

              {/* User management - only admin and owner */}
              <Route element={<ProtectedRoute requiredRole={['owner', 'admin']} />}>
                <Route path="/users" element={<UsersPage />} />
              </Route>
            </Route>
          </Route>

          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
