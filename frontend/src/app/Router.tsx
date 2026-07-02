/**
 * SPARK — Application Router
 * Defines all routes with auth protection.
 *
 * Route structure:
 *   Public routes (no auth required):
 *     /login
 *     /signup (future)
 *
 *   Protected routes (auth required → redirect to /login):
 *     /dashboard
 *     /tasks
 *     /tasks/:taskId
 *     /genome
 *     /analytics
 *     /interventions
 *     /settings
 *
 *   Root redirect:
 *     / → /dashboard (if authenticated)
 *     / → /login (if not authenticated)
 */

import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import { RouteGuard } from "./RouteGuard";
import { Layout } from "@shared/components/layout/Layout";

// Auth pages
import { LoginPage } from "@features/auth/pages/LoginPage";

// Feature pages
import { DashboardPage } from "@features/dashboard/pages/DashboardPage";
import { TasksPage } from "@features/tasks/pages/TasksPage";
import { TaskDetailPage } from "@features/tasks/pages/TaskDetailPage";
import { GenomePage } from "@features/genome/pages/GenomePage";
import { AnalyticsPage } from "@features/analytics/pages/AnalyticsPage";
import { InterventionPage } from "@features/intervention/pages/InterventionPage";

export const Router: React.FC = () => (
  <Routes>
    {/* Public routes */}
    <Route path="/login" element={<LoginPage />} />

    {/* Protected routes — wrapped in Layout */}
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
              {/* Default redirect */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Layout>
        </RouteGuard>
      }
    />

    {/* Root redirect */}
    <Route path="/" element={<Navigate to="/dashboard" replace />} />
  </Routes>
);

Router.displayName = "Router";