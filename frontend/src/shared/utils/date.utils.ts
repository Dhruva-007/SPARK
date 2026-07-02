/**
 * SPARK — Date Utility Functions
 */

import { formatDistanceToNow, format, isPast, differenceInHours } from "date-fns";

/**
 * Format a date string as a human-readable relative time.
 * e.g. "2 hours ago", "in 3 days"
 */
export function formatRelative(dateString: string): string {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true });
  } catch {
    return "Unknown";
  }
}

/**
 * Format a date string as a short display date.
 * e.g. "Jan 15", "Dec 31"
 */
export function formatShortDate(dateString: string): string {
  try {
    return format(new Date(dateString), "MMM d");
  } catch {
    return "—";
  }
}

/**
 * Format a date string as a full display date.
 * e.g. "January 15, 2025"
 */
export function formatFullDate(dateString: string): string {
  try {
    return format(new Date(dateString), "MMMM d, yyyy");
  } catch {
    return "—";
  }
}

/**
 * Format a date string as date + time.
 * e.g. "Jan 15, 9:00 AM"
 */
export function formatDateTime(dateString: string): string {
  try {
    return format(new Date(dateString), "MMM d, h:mm a");
  } catch {
    return "—";
  }
}

/**
 * Returns true if the date has passed.
 */
export function isOverdue(dateString: string): boolean {
  try {
    return isPast(new Date(dateString));
  } catch {
    return false;
  }
}

/**
 * Returns hours remaining until deadline.
 * Negative if overdue.
 */
export function hoursUntilDeadline(deadlineString: string): number {
  try {
    return differenceInHours(new Date(deadlineString), new Date());
  } catch {
    return 0;
  }
}

/**
 * Returns a deadline urgency label.
 */
export function getDeadlineLabel(deadlineString: string): {
  label: string;
  urgent: boolean;
} {
  const hours = hoursUntilDeadline(deadlineString);

  if (hours < 0) return { label: "Overdue", urgent: true };
  if (hours < 2) return { label: `${Math.round(hours * 60)}m left`, urgent: true };
  if (hours < 24) return { label: `${Math.round(hours)}h left`, urgent: true };
  if (hours < 48) return { label: "Tomorrow", urgent: false };
  const days = Math.round(hours / 24);
  return { label: `${days} days`, urgent: false };
}

/**
 * Format working hours from number to string.
 * e.g. 9 → "9:00 AM", 14 → "2:00 PM"
 */
export function formatHour(hour: number): string {
  const date = new Date();
  date.setHours(hour, 0, 0, 0);
  return format(date, "h:mm a");
}