/**
 * SPARK — Genome Page
 * Full behavioral intelligence profile with real data.
 */

import React from "react";
import { Brain } from "lucide-react";
import { Header } from "@shared/components/layout/Header";
import { PageWrapper } from "@shared/components/layout/PageWrapper";
import { Card, CardHeader } from "@shared/components/ui/Card";
import { Badge } from "@shared/components/ui/Badge";
import { CircularProgress } from "@shared/components/ui/Progress";
import { PageSpinner } from "@shared/components/ui/Spinner";
import { useGenomeFull } from "@shared/hooks/useApi";

interface GenomeProfile {
  health_score: number;
  maturity: string;
  maturity_level: number;
  total_tasks_analyzed: number;
  is_peak_hour: boolean;
  peak_hours: number[];
  success_rate: number;
  streak_current: number;
  streak_best: number;
  focus_duration: number;
  version: number;
}

interface GenomeInsight {
  category: string;
  title: string;
  description: string;
  actionable: string;
  priority: string;
}

interface HourlyProductivity {
  hour: number;
  label: string;
  score: number;
  is_peak: boolean;
  is_current: boolean;
}

interface ComplexityCalibration {
  factor: number;
  label: string;
}

interface GenomeFullData {
  profile: GenomeProfile;
  insights: GenomeInsight[];
  productivity_data: {
    hourly_productivity: HourlyProductivity[];
  };
  estimation_data: {
    underestimation_factor: number;
    accuracy_percentage: number;
    complexity_calibration: Record<string, ComplexityCalibration>;
  };
  completion_data: {
    success_rate: number;
    total_completed: number;
    total_failed: number;
    streak_current: number;
    streak_best: number;
  };
  intervention_data: {
    total_interventions: number;
    effectiveness_rate: number;
    most_effective_level: number;
  };
}

export const GenomePage: React.FC = () => {
  const { data: rawData, isLoading } = useGenomeFull();

  if (isLoading) return <PageSpinner message="Loading genome..." />;
  if (!rawData) return null;

  const genome = rawData as GenomeFullData;
  const profile = genome.profile;
  const insights = genome.insights ?? [];
  const productivity = genome.productivity_data;
  const estimation = genome.estimation_data;
  const completion = genome.completion_data;
  const intervention = genome.intervention_data;

  const hourlyData = productivity?.hourly_productivity ?? [];
  const calib = estimation?.complexity_calibration ?? {};

  return (
    <>
      <Header
        title="Completion Genome"
        subtitle={`Maturity: ${profile.maturity} · Version ${profile.version}`}
      />
      <PageWrapper>
        <div className="space-y-8">
          {/* Profile header */}
          <div className="grid grid-cols-4 gap-4">
            <Card padding="md" className="flex flex-col items-center py-6">
              <CircularProgress
                value={profile.health_score}
                size={96}
                strokeWidth={7}
                variant="momentum"
                label={`${Math.round(profile.health_score)}%`}
                sublabel="Health"
              />
              <Badge variant="accent" className="mt-3">{profile.maturity}</Badge>
            </Card>
            <Card padding="md">
              <p className="text-xs text-text-muted mb-1">Success Rate</p>
              <p className="text-2xl font-bold text-text-primary">
                {completion.success_rate.toFixed(0)}%
              </p>
              <p className="text-xs text-text-muted mt-1">
                {completion.total_completed} completed / {completion.total_failed} failed
              </p>
            </Card>
            <Card padding="md">
              <p className="text-xs text-text-muted mb-1">Current Streak</p>
              <p className="text-2xl font-bold text-text-primary">
                {completion.streak_current}
              </p>
              <p className="text-xs text-text-muted mt-1">
                Best: {completion.streak_best}
              </p>
            </Card>
            <Card padding="md">
              <p className="text-xs text-text-muted mb-1">Estimation Accuracy</p>
              <p className="text-2xl font-bold text-text-primary">
                {estimation.accuracy_percentage.toFixed(0)}%
              </p>
              <p className="text-xs text-text-muted mt-1">
                Factor: {estimation.underestimation_factor.toFixed(2)}x
              </p>
            </Card>
          </div>

          <div className="grid grid-cols-12 gap-6">
            {/* Left — Insights */}
            <div className="col-span-7 space-y-4">
              <h2 className="section-title flex items-center gap-2">
                <Brain className="w-4 h-4 text-accent" />
                Behavioral Insights
              </h2>
              {insights.length === 0 ? (
                <Card padding="md">
                  <p className="text-sm text-text-muted text-center py-6">
                    Complete more tasks to unlock behavioral insights.
                  </p>
                </Card>
              ) : (
                <div className="space-y-2">
                  {insights.map((insight, i) => (
                    <Card key={i} padding="md">
                      <div className="flex items-start gap-3">
                        <Badge
                          variant={
                            insight.priority === "high" ? "danger" :
                            insight.priority === "medium" ? "warning" : "neutral"
                          }
                          size="sm"
                        >
                          {insight.category}
                        </Badge>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-text-primary">
                            {insight.title}
                          </p>
                          <p className="text-xs text-text-secondary mt-1 leading-relaxed">
                            {insight.description}
                          </p>
                          <p className="text-xs text-accent font-medium mt-2">
                            → {insight.actionable}
                          </p>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>

            {/* Right — Productivity Heatmap + Stats */}
            <div className="col-span-5 space-y-4">
              <h2 className="section-title">Productivity Hours</h2>
              <Card padding="md">
                <div className="grid grid-cols-6 gap-1">
                  {hourlyData
                    .filter((h) => h.hour >= 6 && h.hour <= 23)
                    .map((h) => {
                      let bg = "bg-neutral-100";
                      if (h.score > 80) bg = "bg-accent";
                      else if (h.score > 55) bg = "bg-accent/60";
                      else if (h.score > 30) bg = "bg-accent/25";

                      return (
                        <div
                          key={h.hour}
                          className={`aspect-square rounded-md flex items-center justify-center text-[10px] font-medium ${bg} ${
                            h.is_current ? "ring-2 ring-accent ring-offset-1" : ""
                          } ${h.is_peak ? "text-white" : "text-text-muted"}`}
                          title={`${h.label}: ${h.score}% productivity`}
                        >
                          {h.label}
                        </div>
                      );
                    })}
                </div>
                <p className="text-xs text-text-muted mt-3 text-center">
                  Peak hours highlighted · Current hour has ring
                </p>
              </Card>

              <Card padding="md">
                <CardHeader title="Complexity Calibration" />
                <div className="space-y-3">
                  {Object.entries(calib).map(([key, val]) => (
                    <div key={key} className="flex items-center justify-between text-sm">
                      <span className="text-text-muted capitalize">{key}</span>
                      <span className="font-medium text-text-primary">
                        {val.factor.toFixed(2)}x
                      </span>
                    </div>
                  ))}
                </div>
              </Card>

              <Card padding="md">
                <CardHeader title="Intervention Effectiveness" />
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-text-muted">Total interventions</span>
                    <span>{intervention.total_interventions}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-muted">Effectiveness</span>
                    <span>{intervention.effectiveness_rate.toFixed(0)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-muted">Best level</span>
                    <Badge variant="accent" size="sm">
                      Level {intervention.most_effective_level}
                    </Badge>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </PageWrapper>
    </>
  );
};

GenomePage.displayName = "GenomePage";