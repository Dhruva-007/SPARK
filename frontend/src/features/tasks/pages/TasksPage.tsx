/**
 * SPARK — Tasks Page
 * Lists all tasks with real API data and task creation.
 */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Clock, Trash2 } from "lucide-react";
import { Header } from "@shared/components/layout/Header";
import { PageWrapper } from "@shared/components/layout/PageWrapper";
import { Card } from "@shared/components/ui/Card";
import { Button } from "@shared/components/ui/Button";
import { Badge, RiskBadge } from "@shared/components/ui/Badge";
import { ProgressBar } from "@shared/components/ui/Progress";
import { CardSkeleton } from "@shared/components/ui/Skeleton";
import { TaskCreator } from "../components/TaskCreator";
import { useTasks, useDeleteTask } from "@shared/hooks/useApi";
import { useTaskStore } from "@shared/stores/task.store";
import { useToast } from "@shared/stores/ui.store";
import { getRiskLevel } from "@shared/types/task.types";
import { getDeadlineLabel } from "@shared/utils/date.utils";
import { capitalize, priorityLabels, statusLabels } from "@shared/utils/format.utils";
import type { Task } from "@shared/types/task.types";

const FILTERS = ["All", "Active", "Completed", "At Risk"] as const;

export const TasksPage: React.FC = () => {
  const navigate = useNavigate();
  const openCreateTaskModal = useTaskStore((s) => s.openCreateTaskModal);
  const { data, isLoading } = useTasks();
  const deleteMutation = useDeleteTask();
  const toast = useToast();
  const [activeFilter, setActiveFilter] = useState<string>("All");

  const allTasks = (data?.tasks ?? []) as Task[];

  const filteredTasks = allTasks.filter((task) => {
    switch (activeFilter) {
      case "Active":
        return ["pending", "active", "in_progress"].includes(task.status);
      case "Completed":
        return task.status === "completed";
      case "At Risk":
        return (task.cms?.failureRisk ?? 0) > 65;
      default:
        return true;
    }
  });

  const handleDelete = async (e: React.MouseEvent, taskId: string) => {
    e.stopPropagation();
    if (!confirm("Delete this task and all its milestones?")) return;
    try {
      await deleteMutation.mutateAsync(taskId);
      toast.success("Task deleted");
    } catch {
      toast.error("Failed to delete task");
    }
  };

  return (
    <>
      <Header
        title="Tasks"
        subtitle={`${allTasks.length} total task${allTasks.length !== 1 ? "s" : ""}`}
        action={{
          label: "New Task",
          onClick: openCreateTaskModal,
          icon: <Plus className="w-4 h-4" />,
        }}
      />

      <PageWrapper>
        <div className="space-y-6">
          {/* Filter bar */}
          <div className="flex items-center gap-2">
            {FILTERS.map((filter) => (
              <button
                key={filter}
                onClick={() => setActiveFilter(filter)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-smooth ${
                  activeFilter === filter
                    ? "bg-accent-light text-accent"
                    : "text-text-muted hover:text-text-primary hover:bg-neutral-100"
                }`}
              >
                {filter}
              </button>
            ))}
          </div>

          {/* Task list */}
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <CardSkeleton key={i} />
              ))}
            </div>
          ) : filteredTasks.length === 0 ? (
            <Card padding="lg">
              <div className="flex flex-col items-center justify-center py-16 text-center space-y-4">
                <p className="text-sm text-text-muted">
                  {activeFilter === "All"
                    ? "No tasks yet. Create your first one!"
                    : `No ${activeFilter.toLowerCase()} tasks.`}
                </p>
                {activeFilter === "All" && (
                  <Button
                    variant="primary"
                    icon={<Plus className="w-4 h-4" />}
                    onClick={openCreateTaskModal}
                  >
                    Create Task
                  </Button>
                )}
              </div>
            </Card>
          ) : (
            <div className="space-y-2">
              {filteredTasks.map((task) => {
                const riskLevel = getRiskLevel(task.cms?.failureRisk ?? 0);
                const deadlineInfo = getDeadlineLabel(task.deadline);

                return (
                  <Card
                    key={task.id}
                    variant="hover"
                    padding="md"
                    onClick={() => navigate(`/tasks/${task.id}`)}
                  >
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium text-text-primary truncate">
                            {task.title}
                          </span>
                          <Badge variant={
                            task.priority === "critical" ? "danger" :
                            task.priority === "high" ? "warning" :
                            "neutral"
                          } size="sm">
                            {priorityLabels[task.priority] ?? task.priority}
                          </Badge>
                        </div>
                        <ProgressBar
                          value={task.progress?.percentage ?? 0}
                          variant="momentum"
                          size="xs"
                          className="mb-1.5"
                        />
                        <div className="flex items-center gap-3 text-xs text-text-muted">
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {deadlineInfo.label}
                          </span>
                          <span>{capitalize(task.category)}</span>
                          <span>{statusLabels[task.status] ?? task.status}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <RiskBadge level={riskLevel} />
                        <button
                          onClick={(e) => handleDelete(e, task.id)}
                          className="w-7 h-7 rounded-lg flex items-center justify-center text-text-muted hover:text-danger hover:bg-danger-light transition-smooth"
                          aria-label="Delete task"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      </PageWrapper>

      <TaskCreator />
    </>
  );
};

TasksPage.displayName = "TasksPage";