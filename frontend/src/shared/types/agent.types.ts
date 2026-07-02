/**
 * SPARK — Agent & Intervention Types
 */

export type InterventionLevel = 0 | 1 | 2 | 3 | 4 | 5;

export type InterventionType =
  | "suggestion"
  | "momentum"
  | "collaboration"
  | "critical"
  | "recovery";

export type InterventionTrigger =
  | "risk_threshold"
  | "ponr_approaching"
  | "stalled"
  | "bankrupt"
  | "manual";

export type InterventionOutcome =
  | "accepted"
  | "dismissed"
  | "completed"
  | "ignored"
  | null;

export interface AgentResponse {
  nextAction: string;
  rationale: string;
  estimatedTimeToComplete: number;
}

export interface Intervention {
  id: string;
  taskId: string;
  userId: string;
  level: InterventionLevel;
  type: InterventionType;
  trigger: InterventionTrigger;
  message: string;
  actionRequired: string | null;
  agentResponse: AgentResponse | null;
  outcome: InterventionOutcome;
  effectivenessScore: number | null;
  createdAt: string;
  resolvedAt: string | null;
}

export interface BankruptcyEmailDraft {
  taskId: string;
  recipientHint: string;
  subject: string;
  body: string;
}

export interface Bankruptcy {
  id: string;
  userId: string;
  declaredAt: string;
  allTaskIds: string[];
  prioritizedTaskIds: string[];
  sacrificedTaskIds: string[];
  rationale: string;
  recoveryPlan: string;
  emailDrafts: BankruptcyEmailDraft[];
  resolved: boolean;
  resolvedAt: string | null;
}

export interface AgentRunStatus {
  agentName: string;
  status: "running" | "completed" | "failed";
  startedAt: string;
  completedAt: string | null;
  error: string | null;
}

// ─── Analytics types ──────────────────────────

export interface CompletionHealthData {
  healthScore: number;
  activeTasks: number;
  atRiskTasks: number;
  completionRate7d: number;
}

export interface RiskMatrixTask {
  taskId: string;
  title: string;
  failureRisk: number;
  momentum: number;
  deadline: string;
  riskLevel: "critical" | "high" | "medium" | "low";
}

export interface WorkloadSimulation {
  runAt: string;
  horizon: number;
  taskCollisions: {
    taskIds: string[];
    collisionDate: string;
    severity: "low" | "medium" | "critical";
  }[];
  overloadDates: string[];
  taskBankruptcyRisk: boolean;
  recommendedActions: string[];
}