/**
 * SPARK — Task Detail Page
 * Full task view with milestones, CMS, and actions.
 */

import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft, CheckCircle2, AlertTriangle,
} from "lucide-react";
import { Header } from "@shared/components/layout/Header";
import { PageWrapper } from "@shared/components/layout/PageWrapper";
import { Card, CardHeader } from "@shared/components/ui/Card";
import { Button } from "@shared/components/ui/Button";
import { Badge, RiskBadge } from "@shared/components/ui/Badge";
import { CircularProgress } from "@shared/components/ui/Progress";
import { PageSpinner } from "@shared/components/ui/Spinner";
import {
  useTaskDetail,
  useTaskMilestones,
  useCompleteMilestone,
  useCompleteTask,
} from "@shared/hooks/useApi";
import { useToast } from "@shared/stores/ui.store";
import { getRiskLevel } from "@shared/types/task.types";
import type { Task } from "@shared/types/task.types";
import { getDeadlineLabel, formatDateTime } from "@shared/utils/date.utils";
import { formatDuration, priorityLabels } from "@shared/utils/format.utils";

interface MilestoneData {
  id: string;
  title: string;
  description: string;
  order: number;
  estimatedMinutes: number;
  status: string;
  isNextAction: boolean;
  completedAt: string | null;
}

interface MilestonesResponse {
  milestones: MilestoneData[];
  task_id: string;
}

export const TaskDetailPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const toast = useToast();

  const { data: task, isLoading: taskLoading } = useTaskDetail(taskId);
  const { data: milestonesData } = useTaskMilestones(taskId);
  const completeMilestoneMutation = useCompleteMilestone(taskId || "");
  const completeTaskMutation = useCompleteTask();

  if (taskLoading || !task) return <PageSpinner message="Loading task..." />;

  const t = task as Task;
  const milestones = ((milestonesData as MilestonesResponse | undefined)?.milestones) ?? [];
  const cmsScore = t.cms?.score ?? 0;
  const failureRisk = t.cms?.failureRisk ?? 0;
  const riskLevel = getRiskLevel(failureRisk);
  const deadlineInfo = getDeadlineLabel(t.deadline);

  const handleCompleteMilestone = async (milestoneId: string) => {
    try {
      await completeMilestoneMutation.mutateAsync(milestoneId);
      toast.success("Milestone completed!");
    } catch {
      toast.error("Failed to complete milestone");
    }
  };

  const handleCompleteTask = async () => {
    if (!confirm("Mark this task as complete?")) return;
    try {
      await completeTaskMutation.mutateAsync(taskId!);
      toast.success("Task completed! SPARK is running reflection analysis...");
    } catch {
      toast.error("Failed to complete task");
    }
  };

  return (
    <>
      <Header title={t.title} />
      <PageWrapper>
        <div className="space-y-6">
          <Button
            variant="ghost"
            size="sm"
            icon={<ArrowLeft className="w-4 h-4" />}
            onClick={() => navigate("/tasks")}
          >
            Back to Tasks
          </Button>

          {/* Task header */}
          <div className="flex items-start justify-between gap-6">
            <div className="space-y-2">
              <h2 className="text-xl font-bold text-text-primary">{t.title}</h2>
              {t.description && (
                <p className="text-sm text-text-secondary">{t.description}</p>
              )}
              <div className="flex gap-2 flex-wrap">
                <Badge variant={
                  t.priority === "critical" ? "danger" :
                  t.priority === "high" ? "warning" : "neutral"
                }>
                  {priorityLabels[t.priority] ?? t.priority}
                </Badge>
                <Badge variant="neutral">{t.category}</Badge>
                <Badge variant="neutral">{t.complexity} complexity</Badge>
                <RiskBadge level={riskLevel} score={Math.round(failureRisk)} />
              </div>
            </div>
            <div className="shrink-0">
              <CircularProgress
                value={cmsScore}
                size={80}
                strokeWidth={6}
                variant="momentum"
                label={`${Math.round(cmsScore)}`}
                sublabel="CMS"
              />
            </div>
          </div>

          <div className="grid grid-cols-12 gap-6">
            {/* Left column — milestones */}
            <div className="col-span-7 space-y-4">
              <CardHeader title="Milestones" subtitle={`${milestones.length} total`} />
              {milestones.length === 0 ? (
                <Card padding="md">
                  <p className="text-sm text-text-muted text-center py-4">
                    No milestones generated yet
                  </p>
                </Card>
              ) : (
                <div className="space-y-2">
                  {milestones.map((ms) => {
                    const isCompleted = ms.status === "completed";
                    const isNext = ms.isNextAction;

                    return (
                      <Card
                        key={ms.id}
                        padding="sm"
                        className={isNext ? "border-accent/30 bg-accent-light/20" : ""}
                      >
                        <div className="flex items-center gap-3 px-2 py-1">
                          <button
                            onClick={() => !isCompleted && handleCompleteMilestone(ms.id)}
                            disabled={isCompleted}
                            className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 transition-smooth ${
                              isCompleted
                                ? "bg-success border-success"
                                : "border-neutral-300 hover:border-accent"
                            }`}
                          >
                            {isCompleted && <CheckCircle2 className="w-3 h-3 text-white" />}
                          </button>
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm ${isCompleted ? "line-through text-text-muted" : "text-text-primary"}`}>
                              {ms.title}
                            </p>
                            <p className="text-xs text-text-muted">
                              {ms.estimatedMinutes} min
                              {isNext && <span className="text-accent ml-2 font-medium">← Next action</span>}
                            </p>
                          </div>
                        </div>
                      </Card>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Right column — stats */}
            <div className="col-span-5 space-y-4">
              <Card padding="md">
                <CardHeader title="Task Info" />
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-text-muted">Deadline</span>
                    <span className={`font-medium ${deadlineInfo.urgent ? "text-danger" : "text-text-primary"}`}>
                      {formatDateTime(t.deadline)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-text-muted">Estimated</span>
                    <span className="text-text-primary">{formatDuration(t.estimatedHours)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-text-muted">Progress</span>
                    <span className="text-text-primary">{Math.round(t.progress?.percentage ?? 0)}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-text-muted">Momentum</span>
                    <span className="text-text-primary">{t.cms?.trend ?? "stable"}</span>
                  </div>
                  {t.ponr?.ponrPassed && (
                    <div className="px-3 py-2 bg-danger-light rounded-lg flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-danger" />
                      <span className="text-xs font-medium text-danger">
                        Point of No Return passed
                      </span>
                    </div>
                  )}
                </div>
              </Card>

              {t.status !== "completed" && (
                <Button
                  variant="primary"
                  fullWidth
                  icon={<CheckCircle2 className="w-4 h-4" />}
                  onClick={handleCompleteTask}
                  loading={completeTaskMutation.isPending}
                >
                  Mark Complete
                </Button>
              )}

              {t.status === "completed" && (
                <Card padding="md" className="bg-success-light border-success/20">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-success" />
                    <span className="text-sm font-medium text-success">
                      Task completed
                    </span>
                  </div>
                </Card>
              )}
            </div>
          </div>
        </div>
      </PageWrapper>
    </>
  );
};

TaskDetailPage.displayName = "TaskDetailPage";