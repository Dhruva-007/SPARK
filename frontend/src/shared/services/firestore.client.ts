/**
 * SPARK — Firestore Client Helpers
 * Typed helper functions for common Firestore operations.
 * Used directly by frontend real-time listeners in Phase 16.
 *
 * Backend repositories handle all write operations.
 * Frontend only reads from Firestore directly for real-time updates.
 */

import {
  collection,
  doc,
  onSnapshot,
  query,
  where,
  orderBy,
  type QueryConstraint,
  type Unsubscribe,
} from "firebase/firestore";
import { db } from "./firebase.client";

/**
 * Subscribe to a single document with real-time updates.
 * Returns an unsubscribe function — call it on component unmount.
 */
export function subscribeToDocument<T>(
  collectionPath: string,
  documentId: string,
  onData: (data: T | null) => void,
  onError?: (error: Error) => void
): Unsubscribe {
  const docRef = doc(db, collectionPath, documentId);

  return onSnapshot(
    docRef,
    (snapshot) => {
      if (snapshot.exists()) {
        onData({ id: snapshot.id, ...snapshot.data() } as T);
      } else {
        onData(null);
      }
    },
    (error) => {
      console.error(
        `[SPARK] Firestore listener error (${collectionPath}/${documentId}):`,
        error
      );
      onError?.(error);
    }
  );
}

/**
 * Subscribe to a collection query with real-time updates.
 * Returns an unsubscribe function — call it on component unmount.
 */
export function subscribeToCollection<T>(
  collectionPath: string,
  constraints: QueryConstraint[],
  onData: (items: T[]) => void,
  onError?: (error: Error) => void
): Unsubscribe {
  const collectionRef = collection(db, collectionPath);
  const q = query(collectionRef, ...constraints);

  return onSnapshot(
    q,
    (snapshot) => {
      const items = snapshot.docs.map((d) => ({
        id: d.id,
        ...d.data(),
      })) as T[];
      onData(items);
    },
    (error) => {
      console.error(
        `[SPARK] Firestore collection listener error (${collectionPath}):`,
        error
      );
      onError?.(error);
    }
  );
}

/**
 * Build a tasks subscription for a specific user.
 * Used in Phase 16 for real-time dashboard updates.
 */
export function subscribeToUserTasks<T>(
  userId: string,
  onData: (tasks: T[]) => void,
  onError?: (error: Error) => void
): Unsubscribe {
  return subscribeToCollection<T>(
    "tasks",
    [
      where("userId", "==", userId),
      orderBy("createdAt", "desc"),
    ],
    onData,
    onError
  );
}

// Re-export Firestore query helpers for use in Phase 16
export { where, orderBy, collection, doc };