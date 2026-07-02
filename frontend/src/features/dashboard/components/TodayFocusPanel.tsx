/**
 * SPARK — Today's Focus Panel
 * Shows active interventions and AI insights.
 */

import React from "react";
import { Brain, AlertTriangle, CheckCircle2 } from "lucide-react";
import { Card } from "@shared/components/ui/Card";
import { Badge } from "@shared/components/ui/Badge";
import { Button } from "@shared/components/ui/Button";
import { Skeleton } from "@shared/components/ui/Skeleton";
import { useInterventions, useRespondToIntervention } from "@shared/hooks/useApi";
import { useToast } from "@shared/stores/ui.store";

export const TodayFocusPanel: React.FC = () => {
  const { data, isLoading } = useInterventions();
  const respondMutation = useRespondToIntervention();
  const toast = useToast();

  const interventions = (data?.interventions ?? []) as Array<{
    id: string;
    taskId: string;
    taskTitle?: string;
    level: number;
    message: string;
    actionRequired?: string;
  }>;

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton height="1.25rem" width="40%" />
        <Card padding="md">
          <Skeleton height="4rem" />
        </Card>
      </div>
    );
  }

  const handleRespond = async (
    interventionId: string,
    taskId: string,
    outcome: string
  ) => {
    try {
      await respondMutation.mutateAsync({ interventionId, taskId, outcome });
      toast.success("Response recorded");
    } catch {
      toast.error("Failed to respond");
    }
  };

  return (
    <div className="space-y-3">
      <h2 className="section-title">Today's Focus</h2>

      {interventions.length > 0 ? (
        <div className="space-y-2">
          {interventions.slice(0, 3).map((iv) => (
            <Card key={iv.id} padding="md" className="border-warning/20">
              <div className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-lg bg-warning-light flex items-center justify-center shrink-0">
                  <AlertTriangle className="w-3.5 h-3.5 text-warning" />
                </div>
                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <Badge variant="warning" size="sm">
                      Level {iv.level}
                    </Badge>
                    {iv.taskTitle && (
                      <span className="text-xs text-text-muted truncate">
                        {iv.taskTitle}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-text-secondary leading-relaxed">
                    {iv.message}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="primary"
                      size="xs"
                      icon={<CheckCircle2 className="w-3 h-3" />}
                      onClick={() => handleRespond(iv.id, iv.taskId, "accepted")}
                    >
                      Accept
                    </Button>
                    <Button
                      variant="ghost"
                      size="xs"
                      onClick={() => handleRespond(iv.id, iv.taskId, "dismissed")}
                    >
                      Dismiss
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card
          padding="md"
          className="border-accent/20 bg-gradient-to-br from-accent-light/40 to-white"
        >
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
              <Brain className="w-4 h-4 text-accent" />
            </div>
            <div className="flex-1">
              <p className="text-xs font-semibold text-accent uppercase tracking-wider">
                All Clear
              </p>
              <p className="text-sm font-medium text-text-primary mt-1">
                No active interventions
              </p>
              <p className="text-xs text-text-secondary leading-relaxed mt-1">
                SPARK is monitoring all your tasks. Interventions will appear
                here when a task needs attention.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

TodayFocusPanel.displayName = "TodayFocusPanel";