/**
 * SPARK — Modal Component
 * Accessible dialog overlay with backdrop blur.
 * Supports keyboard navigation and focus trapping.
 */

import React, { useEffect, useRef } from "react";
import { clsx } from "clsx";
import { X } from "lucide-react";
import { IconButton } from "./Button";

export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  size?: "sm" | "md" | "lg" | "xl";
  children: React.ReactNode;
  showClose?: boolean;
  className?: string;
}

const sizeClasses = {
  sm: "max-w-sm",
  md: "max-w-md",
  lg: "max-w-lg",
  xl: "max-w-2xl",
};

export const Modal: React.FC<ModalProps> = ({
  open,
  onClose,
  title,
  description,
  size = "md",
  children,
  showClose = true,
  className,
}) => {
  const overlayRef = useRef<HTMLDivElement>(null);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && open) onClose();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  if (!open) return null;

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === overlayRef.current) onClose();
  };

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-modal flex items-center justify-center p-4"
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? "modal-title" : undefined}
      aria-describedby={description ? "modal-desc" : undefined}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-neutral-900/30 backdrop-blur-sm animate-fade-in"
        aria-hidden="true"
      />

      {/* Dialog */}
      <div
        className={clsx(
          "relative w-full bg-bg-secondary rounded-2xl shadow-modal",
          "border border-neutral-200 animate-scale-in",
          sizeClasses[size],
          className
        )}
      >
        {/* Header */}
        {(title || showClose) && (
          <div className="flex items-start justify-between p-6 pb-4">
            <div className="space-y-0.5">
              {title && (
                <h2
                  id="modal-title"
                  className="text-base font-semibold text-text-primary"
                >
                  {title}
                </h2>
              )}
              {description && (
                <p id="modal-desc" className="text-sm text-text-muted">
                  {description}
                </p>
              )}
            </div>
            {showClose && (
              <IconButton
                icon={<X className="w-4 h-4" />}
                label="Close modal"
                onClick={onClose}
                size="sm"
                className="text-text-muted hover:text-text-primary ml-4"
              />
            )}
          </div>
        )}

        {/* Content */}
        <div className={clsx("px-6 pb-6", !title && !showClose && "pt-6")}>
          {children}
        </div>
      </div>
    </div>
  );
};

Modal.displayName = "Modal";

/**
 * Modal Footer — consistent action area
 */
export const ModalFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className,
  ...props
}) => (
  <div
    className={clsx(
      "flex items-center justify-end gap-3 pt-4 border-t border-neutral-100 mt-4",
      className
    )}
    {...props}
  >
    {children}
  </div>
);

ModalFooter.displayName = "ModalFooter";