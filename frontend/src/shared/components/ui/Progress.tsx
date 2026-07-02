/**
 * SPARK — Progress Components
 * Linear progress bar and circular progress ring.
 * Used for CMS momentum visualization.
 */

import React from "react";
import { clsx } from "clsx";

// ─────────────────────────────────────────────
// Linear Progress Bar
// ─────────────────────────────────────────────

export interface ProgressBarProps {
  value: number;          // 0-100
  max?: number;
  label?: string;
  showValue?: boolean;
  size?: "xs" | "sm" | "md";
  variant?: "default" | "momentum";
  animated?: boolean;
  className?: string;
}

function getMomentumColor(value: number): string {
  if (value <= 30) return "bg-momentum-critical";
  if (value <= 50) return "bg-momentum-high";
  if (value <= 70) return "bg-momentum-medium";
  if (value <= 85) return "bg-momentum-good";
  return "bg-momentum-peak";
}

const sizeClasses = {
  xs: "h-1",
  sm: "h-1.5",
  md: "h-2",
};

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  label,
  showValue = false,
  size = "sm",
  variant = "default",
  animated = true,
  className,
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  const fillColor =
    variant === "momentum" ? getMomentumColor(percentage) : "bg-accent";

  return (
    <div className={clsx("space-y-1.5", className)}>
      {(label || showValue) && (
        <div className="flex items-center justify-between">
          {label && (
            <span className="text-xs text-text-muted font-medium">{label}</span>
          )}
          {showValue && (
            <span className="text-xs font-semibold text-text-primary tabular-nums">
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}
      <div
        className={clsx("progress-track", sizeClasses[size])}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
      >
        <div
          className={clsx(
            "progress-fill",
            fillColor,
            animated && "transition-all duration-700 ease-out"
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

ProgressBar.displayName = "ProgressBar";

// ─────────────────────────────────────────────
// Circular Progress Ring
// ─────────────────────────────────────────────

export interface CircularProgressProps {
  value: number;          // 0-100
  size?: number;          // diameter in px
  strokeWidth?: number;
  variant?: "default" | "momentum";
  label?: string;
  sublabel?: string;
  className?: string;
}

function getMomentumStroke(value: number): string {
  if (value <= 30) return "#DC2626";
  if (value <= 50) return "#F59E0B";
  if (value <= 70) return "#EAB308";
  if (value <= 85) return "#16A34A";
  return "#2563EB";
}

export const CircularProgress: React.FC<CircularProgressProps> = ({
  value,
  size = 120,
  strokeWidth = 8,
  variant = "default",
  label,
  sublabel,
  className,
}) => {
  const percentage = Math.min(Math.max(value, 0), 100);
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const strokeColor =
    variant === "momentum"
      ? getMomentumStroke(percentage)
      : "#3F6DF6";

  return (
    <div
      className={clsx("relative inline-flex items-center justify-center", className)}
      style={{ width: size, height: size }}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="-rotate-90"
        aria-hidden="true"
      >
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
        />
        {/* Fill */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{
            transition: "stroke-dashoffset 0.7s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.3s ease",
          }}
        />
      </svg>

      {/* Center content */}
      {(label || sublabel) && (
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          {label && (
            <span className="text-lg font-bold text-text-primary leading-none">
              {label}
            </span>
          )}
          {sublabel && (
            <span className="text-xs text-text-muted mt-0.5">{sublabel}</span>
          )}
        </div>
      )}
    </div>
  );
};

CircularProgress.displayName = "CircularProgress";