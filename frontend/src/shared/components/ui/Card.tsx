/**
 * SPARK — Card Components
 * Base surface for all content containers.
 * Variants: default, hoverable, glass
 */

import React from "react";
import { clsx } from "clsx";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "hover" | "glass" | "flat";
  padding?: "none" | "sm" | "md" | "lg";
  as?: React.ElementType;
}

const paddingClasses = {
  none: "",
  sm: "p-4",
  md: "p-5",
  lg: "p-6",
};

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = "default",
      padding = "md",
      as: Component = "div",
      children,
      className,
      ...props
    },
    ref
  ) => {
    return (
      <Component
        ref={ref}
        className={clsx(
          paddingClasses[padding],
          variant === "default" && "card",
          variant === "hover" && "card-hover cursor-pointer",
          variant === "glass" && "glass-card p-5",
          variant === "flat" && "bg-bg-secondary rounded-xl p-5",
          className
        )}
        {...props}
      >
        {children}
      </Component>
    );
  }
);

Card.displayName = "Card";

/**
 * Card Header — title + optional action
 */
export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  title,
  subtitle,
  action,
  className,
  ...props
}) => (
  <div
    className={clsx("flex items-start justify-between gap-4 mb-4", className)}
    {...props}
  >
    <div className="space-y-0.5 min-w-0">
      <h3 className="text-sm font-semibold text-text-primary leading-tight truncate">
        {title}
      </h3>
      {subtitle && (
        <p className="text-xs text-text-muted">{subtitle}</p>
      )}
    </div>
    {action && <div className="shrink-0">{action}</div>}
  </div>
);

CardHeader.displayName = "CardHeader";

/**
 * Card Section — with optional divider above
 */
export interface CardSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  divider?: boolean;
}

export const CardSection: React.FC<CardSectionProps> = ({
  divider = false,
  children,
  className,
  ...props
}) => (
  <div
    className={clsx(divider && "border-t border-neutral-100 pt-4 mt-4", className)}
    {...props}
  >
    {children}
  </div>
);

CardSection.displayName = "CardSection";