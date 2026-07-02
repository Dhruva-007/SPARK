/**
 * SPARK — useDashboard Hook
 */

import { useCompletionHealth } from "@shared/hooks/useApi";

export function useDashboard() {
  const healthQuery = useCompletionHealth();

  return {
    health: healthQuery.data ?? null,
    isLoading: healthQuery.isLoading,
    error: healthQuery.error,
  };
}