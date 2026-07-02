/**
 * SPARK — Formatting Utility Functions
 */

/**
 * Format a number as a percentage string.
 * e.g. 0.76 → "76%" or 76 → "76%"
 */
export function formatPercent(value: number, isDecimal = false): string {
  const pct = isDecimal ? value * 100 : value;
  return `${Math.round(pct)}%`;
}

/**
 * Format hours as a human-readable duration.
 * e.g. 1.5 → "1h 30m", 0.5 → "30m", 2 → "2h"
 */
export function formatDuration(hours: number): string {
  if (hours < 0) return "—";
  const h = Math.floor(hours);
  const m = Math.round((hours - h) * 60);
  if (h === 0) return `${m}m`;
  if (m === 0) return `${h}h`;
  return `${h}h ${m}m`;
}

/**
 * Format a CMS score for display.
 * Adds leading context label.
 */
export function formatCMSScore(score: number): string {
  return `${Math.round(score)}`;
}

/**
 * Capitalize first letter of a string.
 */
export function capitalize(str: string): string {
  if (!str) return "";
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Convert snake_case or kebab-case to Title Case.
 * e.g. "task_not_found" → "Task Not Found"
 */
export function toTitleCase(str: string): string {
  return str
    .replace(/[-_]/g, " ")
    .replace(/\w\S*/g, (word) =>
      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    );
}

/**
 * Truncate a string to a maximum length with ellipsis.
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - 3) + "...";
}

/**
 * Format a number with comma separators.
 * e.g. 1234567 → "1,234,567"
 */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat().format(value);
}

/**
 * Get initials from a display name.
 * e.g. "John Doe" → "JD", "Alice" → "A"
 */
export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n.charAt(0).toUpperCase())
    .slice(0, 2)
    .join("");
}

/**
 * Priority to display label mapping.
 */
export const priorityLabels: Record<string, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
};

/**
 * Category to display label mapping.
 */
export const categoryLabels: Record<string, string> = {
  academic: "Academic",
  work: "Work",
  personal: "Personal",
};

/**
 * Status to display label mapping.
 */
export const statusLabels: Record<string, string> = {
  pending: "Pending",
  active: "Active",
  in_progress: "In Progress",
  completed: "Completed",
  failed: "Failed",
  bankrupt: "Bankrupt",
};