/**
 * SPARK — Skeleton Loader Components
 * Placeholder content shown while data is loading.
 * Always use skeletons instead of spinners for content areas.
 */

import React from "react";
import { clsx } from "clsx";

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  width?: string | number;
  height?: string | number;
  rounded?: "sm" | "md" | "lg" | "full";
}

const roundedClasses = {
  sm: "rounded",
  md: "rounded-lg",
  lg: "rounded-xl",
  full: "rounded-full",
};

export const Skeleton: React.FC<SkeletonProps> = ({
  width,
  height,
  rounded = "md",
  className,
  style,
  ...props
}) => (
  <div
    className={clsx("skeleton", roundedClasses[rounded], className)}
    style={{
      width: width ?? "100%",
      height: height ?? "1rem",
      ...style,
    }}
    aria-hidden="true"
    {...props}
  />
);

Skeleton.displayName = "Skeleton";

/**
 * Skeleton for a card — common pattern
 */
export const CardSkeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={clsx("card p-5 space-y-4", className)}>
    <div className="flex items-center justify-between">
      <Skeleton width="40%" height="1rem" />
      <Skeleton width="16%" height="1.5rem" rounded="full" />
    </div>
    <Skeleton height="0.75rem" />
    <Skeleton height="0.75rem" width="80%" />
    <div className="flex gap-2 mt-2">
      <Skeleton width="25%" height="1.5rem" rounded="full" />
      <Skeleton width="20%" height="1.5rem" rounded="full" />
    </div>
  </div>
);

CardSkeleton.displayName = "CardSkeleton";

/**
 * Skeleton for a text line — common pattern
 */
export const TextSkeleton: React.FC<{
  lines?: number;
  className?: string;
}> = ({ lines = 3, className }) => (
  <div className={clsx("space-y-2", className)}>
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton
        key={i}
        height="0.75rem"
        width={i === lines - 1 ? "65%" : "100%"}
      />
    ))}
  </div>
);

TextSkeleton.displayName = "TextSkeleton";

/**
 * Skeleton for a stat block
 */
export const StatSkeleton: React.FC<{ className?: string }> = ({ className }) => (
  <div className={clsx("card p-5 space-y-2", className)}>
    <Skeleton width="50%" height="0.75rem" />
    <Skeleton width="35%" height="2rem" />
    <Skeleton width="60%" height="0.625rem" />
  </div>
);

StatSkeleton.displayName = "StatSkeleton";