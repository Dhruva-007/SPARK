/**
 * SPARK — Spinner Component
 * Minimal loading indicator.
 */

import React from "react";
import { clsx } from "clsx";
import { Loader2 } from "lucide-react";

export interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  label?: string;
}

const sizeClasses = {
  sm: "w-4 h-4",
  md: "w-5 h-5",
  lg: "w-6 h-6",
};

export const Spinner: React.FC<SpinnerProps> = ({
  size = "md",
  className,
  label = "Loading...",
}) => (
  <div
    role="status"
    aria-label={label}
    className={clsx("inline-flex items-center justify-center", className)}
  >
    <Loader2
      className={clsx("animate-spin text-accent", sizeClasses[size])}
      aria-hidden="true"
    />
    <span className="sr-only">{label}</span>
  </div>
);

Spinner.displayName = "Spinner";

/**
 * Full-page loading overlay
 */
export const PageSpinner: React.FC<{ message?: string }> = ({
  message = "Loading...",
}) => (
  <div className="min-h-screen bg-bg-primary flex flex-col items-center justify-center gap-4">
    <Spinner size="lg" />
    <p className="text-sm text-text-muted">{message}</p>
  </div>
);

PageSpinner.displayName = "PageSpinner";