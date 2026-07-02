/**
 * API client configuration.
 * Uses environment variable for base URL.
 * Production: Cloud Run URL
 * Development: localhost:8000
 */

export const apiConfig = {
  baseURL:
    import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  timeout: 30_000,
};