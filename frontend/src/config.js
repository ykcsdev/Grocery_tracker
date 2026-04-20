const explicitApiUrl = import.meta.env.VITE_API_URL;

function getDefaultApiBaseUrl() {
  if (typeof window === 'undefined') {
    return 'http://localhost:8080';
  }

  const { protocol, hostname } = window.location;
  return `${protocol}//${hostname}:8080`;
}

export const API_BASE_URL = explicitApiUrl || getDefaultApiBaseUrl();
