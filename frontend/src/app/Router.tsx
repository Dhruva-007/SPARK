/**
 * SPARK — Application Router
 */

import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import { RouteGuard } from "./RouteGuard";
import { Layout } from "@shared/components/layout/Layout";

import { LoginPage } from "@features/auth/pages/LoginPage";
import { DashboardPage } from "@features/dashboard/pages/DashboardPage";
import { TasksPage } from "@features/tasks/pages/TasksPage";
import { TaskDetailPage } from "@features/tasks/pages/TaskDetailPage";
import { GenomePage } from "@features/genome/pages/GenomePage";
import { AnalyticsPage } from "@features/analytics/pages/AnalyticsPage";
import { InterventionPage } from "@features/intervention/pages/InterventionPage";

export const Router: React.FC = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />

    <Route
      path="/*"
      element={
        <RouteGuard>
          <Layout>
            <Routes>
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="tasks" element={<TasksPage />} />
              <Route path="tasks/:taskId" element={<TaskDetailPage />} />
              <Route path="genome" element={<GenomePage />} />
              <Route path="analytics" element={<AnalyticsPage />} />
              <Route path="interventions" element={<InterventionPage />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Layout>
        </RouteGuard>
      }
    />

    <Route path="/" element={<Navigate to="/dashboard" replace />} />
  </Routes>
);

Router.displayName = "Router";