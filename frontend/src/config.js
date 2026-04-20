const explicitApiUrl = import.meta.env.VITE_API_URL?.trim();
const configuredApiPort = import.meta.env.VITE_API_PORT?.trim() || '8080';

function isLoopbackHost(hostname) {
  return hostname === 'localhost' || hostname === '127.0.0.1';
}

function getDefaultApiBaseUrl() {
  if (typeof window === 'undefined') {
    return `http://localhost:${configuredApiPort}`;
  }

  const { protocol, hostname } = window.location;
  return `${protocol}//${hostname}:${configuredApiPort}`;
}

function normalizeApiBaseUrl() {
  if (!explicitApiUrl) {
    return getDefaultApiBaseUrl();
  }

  if (typeof window === 'undefined') {
    return explicitApiUrl.replace(/\/$/, '');
  }

  try {
    const parsedUrl = new URL(explicitApiUrl);
    const { hostname: currentHostname } = window.location;

    if (isLoopbackHost(parsedUrl.hostname) && !isLoopbackHost(currentHostname)) {
      const port = parsedUrl.port || configuredApiPort;
      return `${parsedUrl.protocol}//${currentHostname}:${port}${parsedUrl.pathname}`.replace(/\/$/, '');
    }

    return explicitApiUrl.replace(/\/$/, '');
  } catch {
    return explicitApiUrl.replace(/\/$/, '');
  }
}

export const API_BASE_URL = normalizeApiBaseUrl();
