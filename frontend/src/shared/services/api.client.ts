/**
 * SPARK — Axios API Client
 * Configured Axios instance with automatic Firebase token injection.
 *
 * Every request automatically:
 * 1. Attaches the current Firebase ID token as Bearer token
 * 2. Refreshes the token if it is close to expiry (Firebase handles this)
 * 3. Handles 401 responses by redirecting to login
 *
 * Usage:
 *   import { apiClient } from "@shared/services/api.client";
 *   const response = await apiClient.get<TaskListResponse>("/tasks");
 */

import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from "axios";
import { getIdToken } from "firebase/auth";
import { auth } from "./firebase.client";

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

// Create Axios instance with base configuration
const axiosInstance: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ─── Request Interceptor ──────────────────────────────────────
// Attaches Firebase ID token to every outgoing request
axiosInstance.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    try {
      const currentUser = auth.currentUser;

      if (currentUser) {
        // getIdToken(true) forces a refresh if the token is expired
        // getIdToken() uses the cached token if still valid
        const token = await getIdToken(currentUser, false);
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      // Token fetch failure — request proceeds without auth header
      // The backend will return 401 which the response interceptor handles
      console.warn("[SPARK] Could not attach auth token:", error);
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Response Interceptor ─────────────────────────────────────
// Handles auth errors and normalizes API error format
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token is invalid or expired — sign out and redirect to login
      try {
        const { signOut } = await import("firebase/auth");
        await signOut(auth);
      } catch {
        // Ignore sign-out errors
      }
      window.location.href = "/login";
    }

    // Normalize error message from API error envelope
    const apiError =
      error.response?.data?.error?.message ||
      error.message ||
      "An unexpected error occurred";

    return Promise.reject(new Error(apiError));
  }
);

export const apiClient = axiosInstance;

// ─── Typed request helpers ────────────────────────────────────

export async function apiGet<T>(
  path: string,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.get<{ success: true; data: T }>(
    path,
    config
  );
  return response.data.data;
}

export async function apiPost<T>(
  path: string,
  body?: unknown,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.post<{ success: true; data: T }>(
    path,
    body,
    config
  );
  return response.data.data;
}

export async function apiPut<T>(
  path: string,
  body?: unknown,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.put<{ success: true; data: T }>(
    path,
    body,
    config
  );
  return response.data.data;
}

export async function apiDelete<T>(
  path: string,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.delete<{ success: true; data: T }>(
    path,
    config
  );
  return response.data.data;
}