/**
 * SPARK — useRealtime Hook
 * React hook for subscribing to Firestore real-time updates.
 * Handles subscription lifecycle (subscribe on mount, unsubscribe on unmount).
 *
 * Used in Phase 16 for live CMS score updates on the dashboard.
 */

import { useState, useEffect } from "react";
import type { QueryConstraint, Unsubscribe } from "firebase/firestore";
import {
  subscribeToDocument,
  subscribeToCollection,
} from "@shared/services/firestore.client";
import { useAuth } from "./useAuth";

/**
 * Subscribe to a single Firestore document.
 * Returns the document data and loading state.
 */
export function useRealtimeDocument<T>(
  collectionPath: string,
  documentId: string | null | undefined
): { data: T | null; isLoading: boolean; error: Error | null } {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!documentId) {
      setIsLoading(false);
      setData(null);
      return;
    }

    setIsLoading(true);
    let unsubscribe: Unsubscribe;

    try {
      unsubscribe = subscribeToDocument<T>(
        collectionPath,
        documentId,
        (docData) => {
          setData(docData);
          setIsLoading(false);
          setError(null);
        },
        (err) => {
          setError(err);
          setIsLoading(false);
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Subscription failed"));
      setIsLoading(false);
    }

    return () => {
      unsubscribe?.();
    };
  }, [collectionPath, documentId]);

  return { data, isLoading, error };
}

/**
 * Subscribe to a Firestore collection query.
 * Returns the collection items and loading state.
 */
export function useRealtimeCollection<T>(
  collectionPath: string,
  constraints: QueryConstraint[]
): { data: T[]; isLoading: boolean; error: Error | null } {
  const [data, setData] = useState<T[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Stringify constraints to use as dependency — constraints objects change reference each render
  const constraintKey = constraints.map((c) => JSON.stringify(c)).join("|");

  useEffect(() => {
    setIsLoading(true);
    let unsubscribe: Unsubscribe;

    try {
      unsubscribe = subscribeToCollection<T>(
        collectionPath,
        constraints,
        (items) => {
          setData(items);
          setIsLoading(false);
          setError(null);
        },
        (err) => {
          setError(err);
          setIsLoading(false);
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Subscription failed"));
      setIsLoading(false);
    }

    return () => {
      unsubscribe?.();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [collectionPath, constraintKey]);

  return { data, isLoading, error };
}

/**
 * Subscribe to the current user's tasks in real-time.
 * Convenience hook used in Phase 16 dashboard.
 */
export function useRealtimeUserTasks<T>(): {
  data: T[];
  isLoading: boolean;
  error: Error | null;
} {
  const { user } = useAuth();
  const { where, orderBy } = require("firebase/firestore");

  return useRealtimeCollection<T>("tasks", [
    where("userId", "==", user?.uid ?? ""),
    orderBy("createdAt", "desc"),
  ]);
}