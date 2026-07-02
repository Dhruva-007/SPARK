/**
 * SPARK — Page Wrapper
 * Consistent padding and max-width for all page content.
 * Handles page-level animation.
 */

import React from "react";
import { clsx } from "clsx";

export interface PageWrapperProps {
  children: React.ReactNode;
  className?: string;
  maxWidth?: "md" | "lg" | "xl" | "2xl" | "full";
}

const maxWidthClasses = {
  md: "max-w-3xl",
  lg: "max-w-5xl",
  xl: "max-w-7xl",
  "2xl": "max-w-screen-2xl",
  full: "max-w-none",
};

export const PageWrapper: React.FC<PageWrapperProps> = ({
  children,
  className,
  maxWidth = "xl",
}) => (
  <div
    className={clsx(
      "mx-auto w-full px-8 py-8",
      maxWidthClasses[maxWidth],
      "animate-slide-up",
      className
    )}
  >
    {children}
  </div>
);

PageWrapper.displayName = "PageWrapper";