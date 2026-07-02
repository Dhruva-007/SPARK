/**
 * SPARK — Analytics Page
 * Completion history, risk matrix, workload simulation.
 *
 * [PLACEHOLDER] All analytics data is placeholder — replaced in Phase 16 + 17.
 */

import React from "react";
import { BarChart3 } from "lucide-react";
import { Header } from "@shared/components/layout/Header";
import { PageWrapper } from "@shared/components/layout/PageWrapper";
import { Card } from "@shared/components/ui/Card";
import { Badge } from "@shared/components/ui/Badge";

export const AnalyticsPage: React.FC = () => (
  <>
    <Header
      title="Analytics"
      subtitle="Historical completion data and workload simulation"
    />
    <PageWrapper>
      {/*
       * [PLACEHOLDER] Analytics UI — replaced in Phase 16
       * with CompletionTrend, RiskMatrix, WorkloadSimulation components.
       */}
      <Card padding="lg">
        <div className="flex flex-col items-center justify-center py-16 text-center space-y-4">
          <div className="w-12 h-12 rounded-xl bg-accent-light flex items-center justify-center">
            <BarChart3 className="w-6 h-6 text-accent" />
          </div>
          <div className="space-y-1.5">
            <h3 className="text-base font-semibold text-text-primary">
              Analytics building
            </h3>
            <p className="text-sm text-text-muted max-w-xs">
              Complete tasks to see your completion trends, risk patterns,
              and workload simulations.
            </p>
          </div>
          <div className="flex gap-2 flex-wrap justify-center">
            <Badge variant="accent">Completion Trends</Badge>
            <Badge variant="warning">Risk Matrix</Badge>
            <Badge variant="neutral">Workload Simulation</Badge>
          </div>
        </div>
      </Card>
    </PageWrapper>
  </>
);

AnalyticsPage.displayName = "AnalyticsPage";