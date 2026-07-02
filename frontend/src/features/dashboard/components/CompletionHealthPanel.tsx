/**
 * SPARK — Completion Health Panel
 * Shows genome-derived health score and behavioral metrics.
 */

import React from "react";
import { Card } from "@shared/components/ui/Card";
import { CircularProgress, ProgressBar } from "@shared/components/ui/Progress";
import { Skeleton } from "@shared/components/ui/Skeleton";
import { useGenomeProfile } from "@shared/hooks/useApi";

export const CompletionHealthPanel: React.FC = () => {
  const { data: profile, isLoading } = useGenomeProfile();

  if (isLoading) {
    return (
      <div className="space-y-3">
        <Skeleton height="1.25rem" width="50%" />
        <Card padding="md">
          <div className="flex flex-col items-center py-4 space-y-4">
            <Skeleton width={88} height={88} rounded="full" />
            <div className="w-full space-y-3">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} height="0.375rem" />
              ))}
            </div>
          </div>
        </Card>
      </div>
    );
  }

  const p = profile as Record<string, unknown> | null;
  const healthScore = (p?.health_score as number) ?? 0;
  const successRate = (p?.success_rate as number) ?? 0;
  const focusDuration = (p?.focus_duration as number) ?? 0;
  const streakCurrent = (p?.streak_current as number) ?? 0;
  const maturity = (p?.maturity as string) ?? "initializing";

  const metrics = [
    { label: "Success Rate", value: successRate },
    { label: "Focus Duration", value: Math.min(100, (focusDuration / 90) * 100) },
    { label: "Streak", value: Math.min(100, streakCurrent * 20) },
  ];

  return (
    <div className="space-y-3">
      <h2 className="section-title">Completion Genome</h2>
      <Card padding="md">
        <div className="flex flex-col items-center py-4 space-y-5">
          <div className="text-center">
            <CircularProgress
              value={healthScore}
              size={88}
              strokeWidth={7}
              variant="momentum"
              label={`${Math.round(healthScore)}%`}
              sublabel="Health"
            />
            <p className="text-xs text-text-muted mt-3 capitalize">
              Genome: {maturity}
            </p>
          </div>
          <div className="w-full space-y-3">
            {metrics.map((metric) => (
              <ProgressBar
                key={metric.label}
                label={metric.label}
                value={metric.value}
                showValue
                variant="momentum"
              />
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
};

CompletionHealthPanel.displayName = "CompletionHealthPanel";