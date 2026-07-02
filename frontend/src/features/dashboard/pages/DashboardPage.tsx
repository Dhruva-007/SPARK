/**
 * SPARK — Dashboard Page
 * The main productivity workspace with live data.
 */

import React from "react";
import { Plus } from "lucide-react";
import { Header } from "@shared/components/layout/Header";
import { PageWrapper } from "@shared/components/layout/PageWrapper";
import { QuickStatsRow } from "../components/QuickStatsRow";
import { TaskMomentumList } from "../components/TaskMomentumList";
import { CompletionHealthPanel } from "../components/CompletionHealthPanel";
import { TodayFocusPanel } from "../components/TodayFocusPanel";
import { TaskCreator } from "@features/tasks/components/TaskCreator";
import { useTaskStore } from "@shared/stores/task.store";

export const DashboardPage: React.FC = () => {
  const openCreateTaskModal = useTaskStore((s) => s.openCreateTaskModal);

  return (
    <>
      <Header
        title="Dashboard"
        subtitle="Your completion intelligence workspace"
        action={{
          label: "New Task",
          onClick: openCreateTaskModal,
          icon: <Plus className="w-4 h-4" />,
        }}
      />

      <PageWrapper>
        <div className="space-y-8">
          <QuickStatsRow />

          <div className="grid grid-cols-12 gap-6">
            <div className="col-span-7 space-y-6">
              <TaskMomentumList />
            </div>
            <div className="col-span-5 space-y-6">
              <CompletionHealthPanel />
              <TodayFocusPanel />
            </div>
          </div>
        </div>
      </PageWrapper>

      <TaskCreator />
    </>
  );
};

DashboardPage.displayName = "DashboardPage";