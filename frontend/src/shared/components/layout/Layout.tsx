/**
 * SPARK — Root Layout
 * Sidebar + main content area.
 * Used for all authenticated pages.
 */

import React from "react";
import { Sidebar } from "./Sidebar";

export interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => (
  <div className="flex min-h-screen bg-bg-primary">
    <Sidebar />
    <main className="flex-1 min-w-0 overflow-y-auto">
      {children}
    </main>
  </div>
);

Layout.displayName = "Layout";