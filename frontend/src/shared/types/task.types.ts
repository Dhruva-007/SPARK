/**
 * SPARK — Task Domain Types
 * Mirrors Firestore schema exactly.
 */

export type TaskStatus =
  | "pending"
  | "active"
  | "in_progress"
  | "completed"
  | "failed"
  | "bankrupt";

export type TaskPriority = "critical" | "high" | "medium" | "low";
export type TaskCategory = "academic" | "work" | "personal";
export type TaskComplexity = "low" | "medium" | "high";
export type CMSTrend = "improving" | "stable" | "declining" | "critical";
export type RiskLevel = "critical" | "high" | "medium" | "low";
export type MilestoneStatus = "pending" | "in_progress" | "completed";

export interface TaskProgress {
  percentage: number;
  lastUpdatedAt: string;
  milestonesCurrent: number;
  milestonesTotal: number;
}

export interface TaskCMS {
  score: number;
  momentum: number;
  failureRisk: number;
  completionProbability: number;
  lastCalculatedAt: string;
  trend: CMSTrend;
}

export interface TaskPONR {
  calculatedAt: string | null;
  ponrTime: string | null;
  ponrPassed: boolean;
  remainingWorkHours: number;
  remainingAvailableHours: number;
}

export interface TaskActivation {
  isActivated: boolean;
  googleDocId: string | null;
  googleDocUrl: string | null;
  checklistGenerated: boolean;
  outlineGenerated: boolean;
  activatedAt: string | null;
}

export interface Task {
  id: string;
  userId: string;
  title: string;
  description: string;
  category: TaskCategory;
  priority: TaskPriority;
  status: TaskStatus;

  deadline: string;           // ISO datetime string
  estimatedHours: number;
  actualHoursSpent: number;

  complexity: TaskComplexity;

  progress: TaskProgress;
  cms: TaskCMS;
  ponr: TaskPONR;
  activation: TaskActivation;

  tags: string[];
  googleCalendarEventId: string | null;
  googleTaskId: string | null;

  createdAt: string;
  updatedAt: string;
  completedAt: string | null;
}

export interface Milestone {
  id: string;
  taskId: string;
  title: string;
  description: string;
  order: number;
  estimatedMinutes: number;
  actualMinutes: number | null;
  status: MilestoneStatus;
  isNextAction: boolean;
  completedAt: string | null;
  createdAt: string;
}

// ─── Request/Response types ───────────────────

export interface CreateTaskRequest {
  title: string;
  description: string;
  category: TaskCategory;
  priority: TaskPriority;
  deadline: string;
  estimatedHours: number;
  complexity: TaskComplexity;
  tags?: string[];
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  priority?: TaskPriority;
  deadline?: string;
  estimatedHours?: number;
  tags?: string[];
}

export interface UpdateProgressRequest {
  percentage: number;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

// ─── UI helpers ──────────────────────────────

/**
 * Derives a semantic risk level from a CMS score.
 * Used purely for UI color mapping — not business logic.
 */
export function getRiskLevel(failureRisk: number): RiskLevel {
  if (failureRisk >= 80) return "critical";
  if (failureRisk >= 60) return "high";
  if (failureRisk >= 40) return "medium";
  return "low";
}

/**
 * Derives momentum color class from CMS score.
 */
export function getMomentumVariant(
  score: number
): "critical" | "high" | "medium" | "good" | "peak" {
  if (score <= 30) return "critical";
  if (score <= 50) return "high";
  if (score <= 70) return "medium";
  if (score <= 85) return "good";
  return "peak";
}