/**
 * SPARK — Page Header
 */

import React from "react";
import { clsx } from "clsx";
import { Button } from "@shared/components/ui/Button";

export interface HeaderProps {
  title: string;
  subtitle?: string;
  action?: {
    label: string;
    onClick: () => void;
    icon?: React.ReactNode;
  };
  className?: string;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  action,
  className,
}) => (
  <header
    className={clsx(
      "flex items-center justify-between gap-4",
      "border-b border-neutral-100 bg-bg-secondary",
      "px-8 py-4 sticky top-0 z-sticky",
      className
    )}
  >
    <div className="min-w-0">
      <h1 className="text-lg font-semibold text-text-primary tracking-tight leading-tight">
        {title}
      </h1>
      {subtitle && (
        <p className="text-xs text-text-muted mt-0.5">{subtitle}</p>
      )}
    </div>

    <div className="flex items-center gap-2 shrink-0">
      {action && (
        <Button
          variant="primary"
          size="sm"
          icon={action.icon}
          onClick={action.onClick}
        >
          {action.label}
        </Button>
      )}
    </div>
  </header>
);

Header.displayName = "Header";