import { create } from 'zustand';
import { api } from '../lib/api';

export type Role = 'owner' | 'admin' | 'viewer';

export type User = {
  id: number;
  username: string;
  role: Role;
  language_preference: string;
  created_at: string;
  updated_at: string;
};

type AuthState = {
  user: User | null;
  loading: boolean;
  error: string | null;
  fetchMe: () => Promise<void>;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
};

export const useAuth = create<AuthState>((set, get) => ({
  user: null,
  loading: false,
  error: null,
  fetchMe: async () => {
    set({ loading: true, error: null });
    try {
      const me = await api.get<User>('/auth/me');
      set({ user: me, loading: false });
    } catch (e) {
      // Not authenticated is fine on cold start
      set({ user: null, loading: false });
    }
  },
  login: async (username, password) => {
    set({ loading: true, error: null });
    try {
      const res = await api.post<{ user: User }>('/auth/login', { username, password });
      set({ user: res.user, loading: false });
      return true;
    } catch (e: any) {
      set({ error: e?.message ?? 'Login failed', loading: false });
      return false;
    }
  },
  logout: async () => {
    await api.post<{ ok: boolean }>('/auth/logout');
    set({ user: null });
  },
}));

