/**
 * SPARK — API Hooks
 * React Query hooks for all backend API endpoints.
 * Each hook handles loading, error, and caching automatically.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPost, apiPut, apiDelete } from "@shared/services/api.client";
import type { Task, CreateTaskRequest, UpdateTaskRequest, TaskListResponse } from "@shared/types/task.types";
import type { CompletionGenome } from "@shared/types/genome.types";

// ─── Query Keys ──────────────────────────────────────────────

export const queryKeys = {
  tasks: ["tasks"] as const,
  taskDetail: (id: string) => ["tasks", id] as const,
  taskMilestones: (id: string) => ["tasks", id, "milestones"] as const,
  taskCms: (id: string) => ["tasks", id, "cms"] as const,
  taskInterventions: (id: string) => ["tasks", id, "interventions"] as const,
  genome: ["genome"] as const,
  genomeFull: ["genome", "full"] as const,
  genomeProfile: ["genome", "profile"] as const,
  genomeInsights: ["genome", "insights"] as const,
  genomeProductivity: ["genome", "productivity"] as const,
  completionHealth: ["analytics", "completion-health"] as const,
  riskMatrix: ["analytics", "risk-matrix"] as const,
  simulation: ["analytics", "simulation"] as const,
  interventions: ["interventions"] as const,
  agents: ["agents", "status"] as const,
  memory: ["agents", "memory"] as const,
};

// ─── Task Hooks ──────────────────────────────────────────────

export function useTasks(status?: string) {
  const params = status ? `?status=${status}` : "";
  return useQuery({
    queryKey: [...queryKeys.tasks, status],
    queryFn: () => apiGet<TaskListResponse>(`/tasks${params}`),
  });
}

export function useTaskDetail(taskId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.taskDetail(taskId || ""),
    queryFn: () => apiGet<Task>(`/tasks/${taskId}`),
    enabled: !!taskId,
  });
}

export function useTaskMilestones(taskId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.taskMilestones(taskId || ""),
    queryFn: () => apiGet<{ milestones: unknown[]; task_id: string }>(`/tasks/${taskId}/milestones`),
    enabled: !!taskId,
  });
}

export function useTaskCms(taskId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.taskCms(taskId || ""),
    queryFn: () => apiGet<unknown>(`/tasks/${taskId}/cms`),
    enabled: !!taskId,
    staleTime: 60_000,
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateTaskRequest) => apiPost<Task>("/tasks", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks });
      queryClient.invalidateQueries({ queryKey: queryKeys.completionHealth });
    },
  });
}

export function useUpdateTask(taskId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: UpdateTaskRequest) => apiPut<Task>(`/tasks/${taskId}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.taskDetail(taskId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks });
    },
  });
}

export function useCompleteTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (taskId: string) => apiPost<Task>(`/tasks/${taskId}/complete`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks });
      queryClient.invalidateQueries({ queryKey: queryKeys.completionHealth });
      queryClient.invalidateQueries({ queryKey: queryKeys.genomeFull });
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (taskId: string) => apiDelete<void>(`/tasks/${taskId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks });
      queryClient.invalidateQueries({ queryKey: queryKeys.completionHealth });
    },
  });
}

export function useCompleteMilestone(taskId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (milestoneId: string) =>
      apiPost<unknown>(`/tasks/${taskId}/milestones/${milestoneId}/complete`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.taskMilestones(taskId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.taskDetail(taskId) });
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks });
    },
  });
}

export function useNextAction(taskId: string | undefined) {
  return useQuery({
    queryKey: ["tasks", taskId, "next-action"],
    queryFn: () => apiGet<unknown>(`/tasks/${taskId}/next-action`),
    enabled: !!taskId,
    staleTime: 120_000,
  });
}

// ─── Genome Hooks ────────────────────────────────────────────

export function useGenome() {
  return useQuery({
    queryKey: queryKeys.genome,
    queryFn: () => apiGet<CompletionGenome>("/genome"),
  });
}

export function useGenomeFull() {
  return useQuery({
    queryKey: queryKeys.genomeFull,
    queryFn: () => apiGet<unknown>("/genome/full"),
    staleTime: 120_000,
  });
}

export function useGenomeProfile() {
  return useQuery({
    queryKey: queryKeys.genomeProfile,
    queryFn: () => apiGet<unknown>("/genome/profile"),
    staleTime: 120_000,
  });
}

export function useGenomeInsights() {
  return useQuery({
    queryKey: queryKeys.genomeInsights,
    queryFn: () => apiGet<{ insights: unknown[]; generated_at: string }>("/genome/insights"),
    staleTime: 120_000,
  });
}

// ─── Analytics Hooks ─────────────────────────────────────────

export function useCompletionHealth() {
  return useQuery({
    queryKey: queryKeys.completionHealth,
    queryFn: () => apiGet<{
      healthScore: number;
      activeTasks: number;
      atRiskTasks: number;
      completionRate7d: number;
      avgMomentum: number;
    }>("/analytics/completion-health"),
    staleTime: 60_000,
  });
}

export function useRiskMatrix() {
  return useQuery({
    queryKey: queryKeys.riskMatrix,
    queryFn: () => apiGet<{ tasks: unknown[]; generated_at: string }>("/analytics/risk-matrix"),
    staleTime: 60_000,
  });
}

export function useSimulation() {
  return useQuery({
    queryKey: queryKeys.simulation,
    queryFn: () => apiGet<unknown>("/analytics/simulation"),
    staleTime: 300_000,
  });
}

// ─── Intervention Hooks ──────────────────────────────────────

export function useInterventions() {
  return useQuery({
    queryKey: queryKeys.interventions,
    queryFn: () => apiGet<{ interventions: unknown[]; total: number }>("/interventions"),
    staleTime: 30_000,
  });
}

export function useRespondToIntervention() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      interventionId,
      taskId,
      outcome,
    }: {
      interventionId: string;
      taskId: string;
      outcome: string;
    }) =>
      apiPost<unknown>(`/interventions/${interventionId}/respond`, {
        task_id: taskId,
        outcome,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.interventions });
    },
  });
}

export function useInterventionChat() {
  return useMutation({
    mutationFn: ({
      taskId,
      message,
      history,
    }: {
      taskId: string;
      message: string;
      history: { role: string; content: string }[];
    }) =>
      apiPost<{ response: string }>("/interventions/chat", {
        task_id: taskId,
        message,
        history,
      }),
  });
}

// ─── Bankruptcy Hooks ────────────────────────────────────────

export function useBankruptcyAssessment() {
  return useQuery({
    queryKey: ["bankruptcy", "assess"],
    queryFn: () => apiGet<unknown>("/bankruptcy/assess"),
    enabled: false,
  });
}

export function useDeclareBankruptcy() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiPost<unknown>("/bankruptcy/declare"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks });
      queryClient.invalidateQueries({ queryKey: queryKeys.completionHealth });
    },
  });
}

// ─── Agent Hooks ─────────────────────────────────────────────

export function useAgentStatus() {
  return useQuery({
    queryKey: queryKeys.agents,
    queryFn: () => apiGet<{ registered_agents: string[]; total: number }>("/agents/status"),
    staleTime: 600_000,
  });
}