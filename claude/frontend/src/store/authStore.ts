/**
 * Authentication state management with Zustand
 */

import { create } from 'zustand';
import { authApi, User } from '../lib/api';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  checkAuth: () => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true, // Start as loading to check auth on mount
  error: null,

  setUser: (user) =>
    set({
      user,
      isAuthenticated: !!user,
      isLoading: false,
    }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error, isLoading: false }),

  clearError: () => set({ error: null }),

  checkAuth: async () => {
    set({ isLoading: true, error: null });
    try {
      const user = await authApi.getCurrentUser();
      set({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch {
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null, // Don't set error for unauthenticated state
      });
    }
  },

  logout: async () => {
    try {
      await authApi.logout();
      set({
        user: null,
        isAuthenticated: false,
        error: null,
      });
    } catch {
      // Even if logout fails, clear local state
      set({
        user: null,
        isAuthenticated: false,
        error: 'Logout failed, but local session cleared',
      });
    }
  },
}));

// Helper hooks for common checks
export const useIsOwner = () => {
  const user = useAuthStore((state) => state.user);
  return user?.role === 'owner';
};

export const useIsAdmin = () => {
  const user = useAuthStore((state) => state.user);
  return user?.role === 'owner' || user?.role === 'admin';
};

export const useCanModify = () => {
  const user = useAuthStore((state) => state.user);
  return user?.role === 'owner' || user?.role === 'admin';
};

export const useIsViewer = () => {
  const user = useAuthStore((state) => state.user);
  return user?.role === 'viewer';
};
