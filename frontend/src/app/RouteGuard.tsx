/**
 * SPARK — Route Guard
 * Protects routes that require authentication.
 * Shows a loading screen while auth state is resolving.
 * Redirects to /login if unauthenticated.
 * Renders children if authenticated.
 */

import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@shared/hooks/useAuth";
import { PageSpinner } from "@shared/components/ui/Spinner";

interface RouteGuardProps {
  children: React.ReactNode;
}

export const RouteGuard: React.FC<RouteGuardProps> = ({ children }) => {
  const { isLoading, isAuthenticated } = useAuth();
  const location = useLocation();

  // While Firebase auth is resolving, show loading screen
  if (isLoading) {
    return <PageSpinner message="Loading SPARK..." />;
  }

  // Not authenticated → redirect to login
  // Save the attempted URL so we can redirect back after login
  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        state={{ from: location.pathname }}
        replace
      />
    );
  }

  // Authenticated → render page
  return <>{children}</>;
};

RouteGuard.displayName = "RouteGuard";