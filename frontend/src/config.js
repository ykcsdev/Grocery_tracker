const explicitApiUrl = import.meta.env.VITE_API_URL?.trim();
const configuredApiScheme = import.meta.env.VITE_API_SCHEME?.trim();
const configuredApiHost = import.meta.env.VITE_API_HOST?.trim();
const configuredApiPort = import.meta.env.VITE_API_PORT?.trim();
const defaultApiPort = '8080';

function isLoopbackHost(hostname) {
  return hostname === 'localhost' || hostname === '127.0.0.1';
}

function trimTrailingSlash(value) {
  return value.replace(/\/$/, '');
}

function getBrowserLocationParts() {
  if (typeof window === 'undefined') {
    return {
      protocol: configuredApiScheme || 'http',
      hostname: configuredApiHost || 'backend',
    };
  }

  const { protocol, hostname } = window.location;
  return {
    protocol: protocol.replace(':', ''),
    hostname,
  };
}

function buildBaseUrl({ protocol, hostname, port }) {
  if (!hostname) {
    return '';
  }

  const normalizedProtocol = protocol || 'http';
  const normalizedPort = port?.trim();
  const defaultPort = normalizedProtocol === 'https' ? '443' : '80';

  if (!normalizedPort || normalizedPort === defaultPort) {
    return `${normalizedProtocol}://${hostname}`;
  }

  return `${normalizedProtocol}://${hostname}:${normalizedPort}`;
}

function getDefaultApiBaseUrl() {
  const browserLocation = getBrowserLocationParts();

  return buildBaseUrl({
    protocol: configuredApiScheme || browserLocation.protocol,
    hostname: configuredApiHost || browserLocation.hostname,
    port: configuredApiPort || defaultApiPort,
  });
}

function normalizeApiBaseUrl() {
  if (!explicitApiUrl) {
    return trimTrailingSlash(getDefaultApiBaseUrl());
  }

  if (typeof window === 'undefined') {
    return trimTrailingSlash(explicitApiUrl);
  }

  try {
    const parsedUrl = new URL(explicitApiUrl);
    const { hostname: currentHostname } = window.location;

    if (isLoopbackHost(parsedUrl.hostname) && !isLoopbackHost(currentHostname)) {
      return trimTrailingSlash(
        buildBaseUrl({
          protocol: parsedUrl.protocol.replace(':', ''),
          hostname: configuredApiHost || currentHostname,
          port: parsedUrl.port || configuredApiPort || defaultApiPort,
        }) + parsedUrl.pathname
      );
    }

    return trimTrailingSlash(explicitApiUrl);
  } catch {
    return trimTrailingSlash(explicitApiUrl);
  }
}

export const API_BASE_URL = normalizeApiBaseUrl();
