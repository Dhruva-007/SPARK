/**
 * SPARK — Intervention Page
 * Active interventions, AI collaboration, recovery plans.
 *
 * [PLACEHOLDER] All intervention data is placeholder — replaced in Phase 15.
 */

import React from "react";
import { Zap } from "lucide-react";
import { Header } from "@shared/components/layout/Header";
import { PageWrapper } from "@shared/components/layout/PageWrapper";
import { Card } from "@shared/components/ui/Card";
import { Badge } from "@shared/components/ui/Badge";

export const InterventionPage: React.FC = () => (
  <>
    <Header
      title="Interventions"
      subtitle="Active AI interventions and completion assistance"
    />
    <PageWrapper>
      {/*
       * [PLACEHOLDER] Intervention UI — replaced in Phase 15
       * with InterventionChat, BankruptcyModal, RecoveryPlan components.
       */}
      <Card padding="lg">
        <div className="flex flex-col items-center justify-center py-16 text-center space-y-4">
          <div className="w-12 h-12 rounded-xl bg-accent-light flex items-center justify-center">
            <Zap className="w-6 h-6 text-accent" />
          </div>
          <div className="space-y-1.5">
            <h3 className="text-base font-semibold text-text-primary">
              No active interventions
            </h3>
            <p className="text-sm text-text-muted max-w-xs">
              SPARK continuously monitors your tasks. When a task is at risk,
              an intelligent intervention will appear here.
            </p>
          </div>
          <div className="flex gap-2 flex-wrap justify-center">
            <Badge variant="success">Level 0 — Monitoring</Badge>
          </div>
        </div>
      </Card>
    </PageWrapper>
  </>
);

InterventionPage.displayName = "InterventionPage";