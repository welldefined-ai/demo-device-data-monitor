/**
 * Protected route component with role-based access control
 */

import React, { useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { Spin, Result, Button } from 'antd';
import { useAuthStore } from '../store/authStore';

interface ProtectedRouteProps {
  /**
   * Required role(s) to access this route.
   * If undefined, only authentication is required.
   */
  requiredRole?: 'owner' | 'admin' | 'viewer' | ('owner' | 'admin')[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ requiredRole }) => {
  const { isAuthenticated, isLoading, user, checkAuth } = useAuthStore();

  // Check authentication on mount
  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      checkAuth();
    }
  }, [isAuthenticated, isLoading, checkAuth]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <Spin size="large" tip="Loading..." />
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Check role-based permissions if requiredRole is specified
  if (requiredRole && user) {
    const hasPermission = checkRolePermission(user.role, requiredRole);

    if (!hasPermission) {
      return (
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '100vh',
          }}
        >
          <Result
            status="403"
            title="403"
            subTitle="Sorry, you don't have permission to access this page."
            extra={
              <Button type="primary" onClick={() => window.history.back()}>
                Go Back
              </Button>
            }
          />
        </div>
      );
    }
  }

  // Render child routes
  return <Outlet />;
};

/**
 * Check if user's role meets the required role
 */
function checkRolePermission(
  userRole: 'owner' | 'admin' | 'viewer',
  requiredRole: 'owner' | 'admin' | 'viewer' | ('owner' | 'admin')[]
): boolean {
  // If requiredRole is an array, check if user's role is in the array
  if (Array.isArray(requiredRole)) {
    return requiredRole.includes(userRole as 'owner' | 'admin');
  }

  // Owner has access to everything
  if (userRole === 'owner') {
    return true;
  }

  // Admin has access to admin and viewer routes
  if (userRole === 'admin') {
    return requiredRole === 'admin' || requiredRole === 'viewer';
  }

  // Viewer only has access to viewer routes
  if (userRole === 'viewer') {
    return requiredRole === 'viewer';
  }

  return false;
}
