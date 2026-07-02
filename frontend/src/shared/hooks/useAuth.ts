/**
 * SPARK — useAuth Hook
 * Provides access to the current auth state throughout the app.
 * Firebase auth subscription is set up in AuthProvider (Phase 4).
 * This hook is the consumer interface.
 */

import { useAuthStore } from "@shared/stores/auth.store";
import type { AuthUser } from "@shared/types/user.types";

export interface UseAuthReturn {
  isLoading: boolean;
  isAuthenticated: boolean;
  user: AuthUser | null;
}

export function useAuth(): UseAuthReturn {
  const authState = useAuthStore((s) => s.authState);

  return {
    isLoading: authState.status === "loading",
    isAuthenticated: authState.status === "authenticated",
    user: authState.status === "authenticated" ? authState.user : null,
  };
}