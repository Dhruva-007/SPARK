/**
 * SPARK — Quick Stats Row
 * Live data from completion health API.
 */

import React from "react";
import { CheckCircle2, Clock, TrendingUp, AlertTriangle } from "lucide-react";
import { Card } from "@shared/components/ui/Card";
import { Skeleton } from "@shared/components/ui/Skeleton";
import { useCompletionHealth } from "@shared/hooks/useApi";

export const QuickStatsRow: React.FC = () => {
  const { data, isLoading } = useCompletionHealth();

  if (isLoading) {
    return (
      <div className="grid grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} padding="md">
            <Skeleton height="0.75rem" width="50%" />
            <Skeleton height="2rem" width="30%" className="mt-3" />
            <Skeleton height="0.625rem" width="60%" className="mt-2" />
          </Card>
        ))}
      </div>
    );
  }

  const stats = [
    {
      label: "Completion Health",
      value: data ? `${Math.round(data.healthScore)}%` : "—",
      subtext: data ? `${(data.completionRate7d * 100).toFixed(0)}% rate (7d)` : "Calculating...",
      icon: <CheckCircle2 className="w-4 h-4" />,
      iconBg: "bg-success-light",
      iconColor: "text-success",
    },
    {
      label: "Active Tasks",
      value: data ? String(data.activeTasks) : "—",
      subtext: data?.activeTasks === 0 ? "Create your first task" : "In progress",
      icon: <Clock className="w-4 h-4" />,
      iconBg: "bg-accent-light",
      iconColor: "text-accent",
    },
    {
      label: "Avg Momentum",
      value: data ? String(Math.round(data.avgMomentum)) : "—",
      subtext: "CMS score",
      icon: <TrendingUp className="w-4 h-4" />,
      iconBg: "bg-accent-light",
      iconColor: "text-accent",
    },
    {
      label: "At Risk",
      value: data ? String(data.atRiskTasks) : "—",
      subtext: data?.atRiskTasks === 0 ? "All on track" : "Need attention",
      icon: <AlertTriangle className="w-4 h-4" />,
      iconBg: data?.atRiskTasks ? "bg-danger-light" : "bg-success-light",
      iconColor: data?.atRiskTasks ? "text-danger" : "text-success",
    },
  ];

  return (
    <div className="grid grid-cols-4 gap-4">
      {stats.map((stat) => (
        <Card key={stat.label} padding="md">
          <div className="flex items-start justify-between mb-4">
            <span className="text-xs font-medium text-text-muted">
              {stat.label}
            </span>
            <div className={`w-7 h-7 rounded-lg ${stat.iconBg} flex items-center justify-center`}>
              <span className={stat.iconColor}>{stat.icon}</span>
            </div>
          </div>
          <p className="text-2xl font-bold text-text-primary tracking-tight">
            {stat.value}
          </p>
          <p className="text-xs text-text-muted mt-1">{stat.subtext}</p>
        </Card>
      ))}
    </div>
  );
};

QuickStatsRow.displayName = "QuickStatsRow";