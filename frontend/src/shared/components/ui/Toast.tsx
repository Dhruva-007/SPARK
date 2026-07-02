/**
 * SPARK — Toast Notifications
 * Renders toasts from the UI store.
 */

import React from "react";
import { X, CheckCircle2, AlertTriangle, AlertCircle, Info } from "lucide-react";
import { clsx } from "clsx";
import { useUIStore } from "@shared/stores/ui.store";

const icons = {
  success: <CheckCircle2 className="w-4 h-4 text-success" />,
  error: <AlertCircle className="w-4 h-4 text-danger" />,
  warning: <AlertTriangle className="w-4 h-4 text-warning" />,
  info: <Info className="w-4 h-4 text-info" />,
};

const bgColors = {
  success: "bg-success-light border-success/20",
  error: "bg-danger-light border-danger/20",
  warning: "bg-warning-light border-warning/20",
  info: "bg-info-light border-info/20",
};

export const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useUIStore();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-6 right-6 z-toast space-y-2 max-w-sm">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={clsx(
            "flex items-start gap-3 px-4 py-3 rounded-xl border shadow-lg animate-slide-up",
            bgColors[toast.type]
          )}
        >
          <span className="shrink-0 mt-0.5">{icons[toast.type]}</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-text-primary">{toast.title}</p>
            {toast.description && (
              <p className="text-xs text-text-secondary mt-0.5">{toast.description}</p>
            )}
          </div>
          <button
            onClick={() => removeToast(toast.id)}
            className="shrink-0 text-text-muted hover:text-text-primary"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
};

ToastContainer.displayName = "ToastContainer";