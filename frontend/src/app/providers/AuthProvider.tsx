/**
 * SPARK — Auth Provider
 * Subscribes to Firebase auth state changes and syncs to Zustand store.
 * This is the single source of truth for authentication state.
 *
 * On sign-in:
 *   1. Firebase calls the subscriber with the user object
 *   2. We call GET /users/me to fetch/create the Firestore user document
 *   3. Auth store is updated to "authenticated"
 *
 * On sign-out:
 *   1. Firebase calls the subscriber with null
 *   2. Auth store is updated to "unauthenticated"
 */

import React, { useEffect } from "react";
import { onAuthStateChanged } from "firebase/auth";
import { auth } from "@shared/services/firebase.client";
import { useAuthStore } from "@shared/stores/auth.store";
import { apiGet } from "@shared/services/api.client";
import type { AuthUser } from "@shared/types/user.types";

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const { setAuthenticated, setUnauthenticated, setLoading } = useAuthStore();

  useEffect(() => {
    // Set loading state immediately — prevents flash of unauthenticated content
    setLoading();

    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        // User is signed in
        const authUser: AuthUser = {
          uid: firebaseUser.uid,
          email: firebaseUser.email,
          displayName: firebaseUser.displayName,
          photoURL: firebaseUser.photoURL,
          emailVerified: firebaseUser.emailVerified,
        };

        // Fetch or create user document in Firestore via backend
        // This ensures the user record exists before any other operation
        try {
          await apiGet("/users/me");
        } catch (error) {
          // Non-fatal — user can still use the app even if this fails
          console.warn("[SPARK] Could not sync user document:", error);
        }

        setAuthenticated(authUser);
      } else {
        // User is signed out
        setUnauthenticated();
      }
    });

    // Cleanup subscription on unmount
    return () => unsubscribe();
  }, [setAuthenticated, setUnauthenticated, setLoading]);

  return <>{children}</>;
};

AuthProvider.displayName = "AuthProvider";