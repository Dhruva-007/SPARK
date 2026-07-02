/**
 * SPARK — useEmailAuth Hook
 * Email/password sign-in and sign-up via Firebase.
 */

import { useState } from "react";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  updateProfile,
} from "firebase/auth";
import { auth } from "@shared/services/firebase.client";
import { useToast } from "@shared/stores/ui.store";

export interface UseEmailAuthReturn {
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, name: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export function useEmailAuth(): UseEmailAuthReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  const signIn = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (err) {
      const message = _getErrorMessage(err);
      setError(message);
      toast.error("Sign in failed", message);
    } finally {
      setIsLoading(false);
    }
  };

  const signUp = async (
    email: string,
    password: string,
    name: string
  ): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await createUserWithEmailAndPassword(auth, email, password);
      await updateProfile(result.user, { displayName: name });
    } catch (err) {
      const message = _getErrorMessage(err);
      setError(message);
      toast.error("Sign up failed", message);
    } finally {
      setIsLoading(false);
    }
  };

  return { signIn, signUp, isLoading, error };
}

function _getErrorMessage(error: unknown): string {
  if (error && typeof error === "object" && "code" in error) {
    const code = (error as { code: string }).code;
    const messages: Record<string, string> = {
      "auth/email-already-in-use": "An account with this email already exists.",
      "auth/invalid-email": "Invalid email address.",
      "auth/user-not-found": "No account found with this email.",
      "auth/wrong-password": "Incorrect password.",
      "auth/weak-password": "Password must be at least 6 characters.",
      "auth/too-many-requests": "Too many attempts. Please wait and try again.",
      "auth/invalid-credential": "Invalid email or password.",
    };
    return messages[code] || "Authentication failed. Please try again.";
  }
  return "Authentication failed. Please try again.";
}