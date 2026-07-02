/**
 * SPARK — Badge Component
 * Status indicators, labels, risk levels.
 */

import React from "react";
import { clsx } from "clsx";

export type BadgeVariant =
  | "neutral"
  | "accent"
  | "success"
  | "warning"
  | "danger"
  | "info";

export type RiskLevel = "critical" | "high" | "medium" | "low";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  size?: "sm" | "md";
  dot?: boolean;
}

const variantClasses: Record<BadgeVariant, string> = {
  neutral: "badge-neutral",
  accent: "badge-accent",
  success: "badge-success",
  warning: "badge-warning",
  danger: "badge-danger",
  info: "badge-info",
};

const dotColors: Record<BadgeVariant, string> = {
  neutral: "bg-neutral-400",
  accent: "bg-accent",
  success: "bg-success",
  warning: "bg-warning",
  danger: "bg-danger",
  info: "bg-info",
};

export const Badge: React.FC<BadgeProps> = ({
  variant = "neutral",
  size = "md",
  dot = false,
  children,
  className,
  ...props
}) => (
  <span
    className={clsx(
      "badge",
      variantClasses[variant],
      size === "sm" && "text-[11px] px-2 py-0.5",
      className
    )}
    {...props}
  >
    {dot && (
      <span
        className={clsx("w-1.5 h-1.5 rounded-full shrink-0", dotColors[variant])}
        aria-hidden="true"
      />
    )}
    {children}
  </span>
);

Badge.displayName = "Badge";

/**
 * Risk Badge — semantic risk level indicator
 */
export interface RiskBadgeProps {
  level: RiskLevel;
  score?: number;
  className?: string;
}

const riskConfig: Record<
  RiskLevel,
  { label: string; className: string; dotColor: string }
> = {
  critical: {
    label: "Critical",
    className: "badge badge-danger border border-danger/20",
    dotColor: "bg-danger animate-pulse",
  },
  high: {
    label: "High Risk",
    className: "badge badge-warning border border-warning/20",
    dotColor: "bg-warning",
  },
  medium: {
    label: "Medium",
    className: "badge bg-yellow-50 text-yellow-700 border border-yellow-200",
    dotColor: "bg-yellow-500",
  },
  low: {
    label: "On Track",
    className: "badge badge-success border border-success/20",
    dotColor: "bg-success",
  },
};

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  score,
  className,
}) => {
  const config = riskConfig[level];

  return (
    <span className={clsx(config.className, className)}>
      <span className={clsx("w-1.5 h-1.5 rounded-full", config.dotColor)} />
      {config.label}
      {score !== undefined && (
        <span className="opacity-70 ml-0.5">{score}%</span>
      )}
    </span>
  );
};

RiskBadge.displayName = "RiskBadge";