/**
 * SPARK — useGoogleAuth Hook
 * Encapsulates Google OAuth sign-in and sign-out logic.
 * Components consume this hook — never call Firebase auth directly.
 */

import { useState } from "react";
import {
  GoogleAuthProvider,
  signInWithPopup,
  signOut as firebaseSignOut,
} from "firebase/auth";
import { auth } from "@shared/services/firebase.client";
import { useToast } from "@shared/stores/ui.store";

const googleProvider = new GoogleAuthProvider();

googleProvider.addScope("https://www.googleapis.com/auth/calendar.readonly");
googleProvider.addScope("https://www.googleapis.com/auth/gmail.readonly");

googleProvider.setCustomParameters({ prompt: "select_account" });

export interface UseGoogleAuthReturn {
  signIn: () => Promise<void>;
  signOut: () => Promise<void>;
  isSigningIn: boolean;
  isSigningOut: boolean;
  error: string | null;
}

export function useGoogleAuth(): UseGoogleAuthReturn {
  const [isSigningIn, setIsSigningIn] = useState(false);
  const [isSigningOut, setIsSigningOut] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  const signIn = async (): Promise<void> => {
    setIsSigningIn(true);
    setError(null);

    try {
      await signInWithPopup(auth, googleProvider);
    } catch (err) {
      const message = _getAuthErrorMessage(err);
      setError(message);
      toast.error("Sign in failed", message);
    } finally {
      setIsSigningIn(false);
    }
  };

  const signOut = async (): Promise<void> => {
    setIsSigningOut(true);
    setError(null);

    try {
      await firebaseSignOut(auth);
    } catch (err) {
      const message = _getAuthErrorMessage(err);
      setError(message);
      toast.error("Sign out failed", message);
    } finally {
      setIsSigningOut(false);
    }
  };

  return { signIn, signOut, isSigningIn, isSigningOut, error };
}

function _getAuthErrorMessage(error: unknown): string {
  if (error && typeof error === "object" && "code" in error) {
    const code = (error as { code: string }).code;
    const messages: Record<string, string> = {
      "auth/popup-closed-by-user": "Sign in cancelled. Please try again.",
      "auth/popup-blocked":
        "Pop-up was blocked by your browser. Please allow pop-ups for this site.",
      "auth/cancelled-popup-request": "Only one sign-in window allowed at a time.",
      "auth/network-request-failed":
        "Network error. Please check your connection.",
      "auth/too-many-requests":
        "Too many attempts. Please wait a moment and try again.",
      "auth/user-disabled": "This account has been disabled.",
      "auth/operation-not-allowed": "Google sign-in is not enabled.",
    };
    return messages[code] || "Sign in failed. Please try again.";
  }
  return "Sign in failed. Please try again.";
}