export function makeWsUrl(path: string): string {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const host = window.location.host;
  return `${proto}://${host}${path.startsWith('/') ? path : `/${path}`}`;
}

