/**
 * SPARK — Task Momentum List
 * Shows all active tasks with their CMS scores from real API data.
 */

import React from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Inbox, Clock } from "lucide-react";
import { Card } from "@shared/components/ui/Card";
import { Button } from "@shared/components/ui/Button";
import { RiskBadge } from "@shared/components/ui/Badge";
import { CircularProgress, ProgressBar } from "@shared/components/ui/Progress";
import { Skeleton } from "@shared/components/ui/Skeleton";
import { useTasks } from "@shared/hooks/useApi";
import { useTaskStore } from "@shared/stores/task.store";
import { getRiskLevel } from "@shared/types/task.types";
import { getDeadlineLabel } from "@shared/utils/date.utils";
import type { Task } from "@shared/types/task.types";

export const TaskMomentumList: React.FC = () => {
  const navigate = useNavigate();
  const openCreateTaskModal = useTaskStore((s) => s.openCreateTaskModal);
  const { data, isLoading } = useTasks();

  const activeTasks =
    data?.tasks?.filter(
      (t: Task) => !["completed", "failed", "bankrupt"].includes(t.status)
    ) ?? [];

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton height="1.25rem" width="40%" />
        {[1, 2, 3].map((i) => (
          <Card key={i} padding="md">
            <div className="flex items-center gap-4">
              <Skeleton width={48} height={48} rounded="full" />
              <div className="flex-1 space-y-2">
                <Skeleton height="0.875rem" width="60%" />
                <Skeleton height="0.375rem" />
                <Skeleton height="0.625rem" width="30%" />
              </div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="section-title">Task Momentum</h2>
          <p className="section-subtitle mt-0.5">
            {activeTasks.length > 0
              ? `${activeTasks.length} active task${activeTasks.length > 1 ? "s" : ""}`
              : "No active tasks"}
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          icon={<Plus className="w-4 h-4" />}
          onClick={openCreateTaskModal}
        >
          Add Task
        </Button>
      </div>

      {activeTasks.length === 0 ? (
        <Card padding="lg">
          <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
            <div className="w-10 h-10 rounded-xl bg-neutral-100 flex items-center justify-center">
              <Inbox className="w-5 h-5 text-text-muted" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-text-primary">No tasks yet</p>
              <p className="text-xs text-text-muted max-w-xs">
                Create your first task and SPARK will generate an AI execution plan.
              </p>
            </div>
            <Button
              variant="primary"
              size="sm"
              icon={<Plus className="w-4 h-4" />}
              onClick={openCreateTaskModal}
            >
              Create First Task
            </Button>
          </div>
        </Card>
      ) : (
        <div className="space-y-2">
          {activeTasks.map((task: Task) => {
            const cmsScore = task.cms?.score ?? 0;
            const riskLevel = getRiskLevel(task.cms?.failureRisk ?? 0);
            const deadlineInfo = getDeadlineLabel(task.deadline);

            return (
              <Card
                key={task.id}
                variant="hover"
                padding="md"
                onClick={() => navigate(`/tasks/${task.id}`)}
              >
                <div className="flex items-center gap-4">
                  <CircularProgress
                    value={cmsScore}
                    size={48}
                    strokeWidth={5}
                    variant="momentum"
                    label={String(Math.round(cmsScore))}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-3 mb-2">
                      <span className="text-sm font-medium text-text-primary truncate">
                        {task.title}
                      </span>
                      <RiskBadge level={riskLevel} />
                    </div>
                    <ProgressBar
                      value={task.progress?.percentage ?? 0}
                      variant="momentum"
                      size="sm"
                    />
                    <p className="text-xs text-text-muted mt-1.5 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {deadlineInfo.label}
                      {task.progress?.milestonesTotal > 0 && (
                        <span className="ml-2">
                          · {task.progress.milestonesCurrent}/{task.progress.milestonesTotal} milestones
                        </span>
                      )}
                    </p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

TaskMomentumList.displayName = "TaskMomentumList";