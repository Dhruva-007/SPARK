/**
 * SPARK — React Query Provider
 * Configures TanStack Query with sensible defaults for SPARK.
 */

import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Data is considered fresh for 30 seconds
      staleTime: 30_000,
      // Keep data in cache for 5 minutes after component unmounts
      gcTime: 5 * 60 * 1000,
      // Retry failed requests once before showing error
      retry: 1,
      // Do not refetch on window focus (prevents jarring updates)
      refetchOnWindowFocus: false,
    },
    mutations: {
      // Do not retry mutations — they may have side effects
      retry: false,
    },
  },
});

interface QueryProviderProps {
  children: React.ReactNode;
}

export const QueryProvider: React.FC<QueryProviderProps> = ({ children }) => (
  <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

QueryProvider.displayName = "QueryProvider";