export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

const BASE = '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), 15000);
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    signal: controller.signal,
    ...init,
  }).finally(() => clearTimeout(id));
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  // Handle no-content responses gracefully (e.g., 204)
  if (res.status === 204 || res.status === 205) {
    return undefined as unknown as T;
  }
  const ct = res.headers.get('content-type') || '';
  if (!ct.includes('application/json')) {
    // Fallback: if body is empty, return undefined; otherwise return text
    const text = await res.text();
    return (text ? (text as unknown as T) : (undefined as unknown as T));
  }
  const text = await res.text();
  if (!text) {
    return undefined as unknown as T;
  }
  return JSON.parse(text) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) => request<T>(path, { method: 'POST', body: JSON.stringify(body ?? {}) }),
  put: <T>(path: string, body?: unknown) => request<T>(path, { method: 'PUT', body: JSON.stringify(body ?? {}) }),
  patch: <T>(path: string, body?: unknown) => request<T>(path, { method: 'PATCH', body: JSON.stringify(body ?? {}) }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
};
