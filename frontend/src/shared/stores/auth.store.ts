/**
 * SPARK — Auth Zustand Store
 * Holds authentication state accessible throughout the app.
 * Firebase auth state is synced into this store in Phase 4.
 */

import { create } from "zustand";
import type { AuthState, AuthUser } from "@shared/types/user.types";

interface AuthStore {
  authState: AuthState;
  // Actions
  setLoading: () => void;
  setAuthenticated: (user: AuthUser) => void;
  setUnauthenticated: () => void;
  // Selectors
  isAuthenticated: () => boolean;
  isLoading: () => boolean;
  getUser: () => AuthUser | null;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  authState: { status: "loading" },

  setLoading: () => set({ authState: { status: "loading" } }),

  setAuthenticated: (user: AuthUser) =>
    set({ authState: { status: "authenticated", user } }),

  setUnauthenticated: () =>
    set({ authState: { status: "unauthenticated" } }),

  isAuthenticated: () => get().authState.status === "authenticated",

  isLoading: () => get().authState.status === "loading",

  getUser: () => {
    const state = get().authState;
    return state.status === "authenticated" ? state.user : null;
  },
}));