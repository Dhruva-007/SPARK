/**
 * SPARK — Sidebar Navigation
 */

import React from "react";
import { NavLink, useLocation } from "react-router-dom";
import { clsx } from "clsx";
import {
  LayoutDashboard,
  CheckSquare,
  Dna,
  BarChart3,
  Zap,
  LogOut,
} from "lucide-react";
import { useAuth } from "@shared/hooks/useAuth";
import { useGoogleAuth } from "@features/auth/hooks/useGoogleAuth";
import { getInitials } from "@shared/utils/format.utils";
import { Tooltip } from "@shared/components/ui/Tooltip";

interface NavItem {
  label: string;
  path: string;
  icon: React.ReactNode;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", path: "/dashboard", icon: <LayoutDashboard className="w-4 h-4" /> },
  { label: "Tasks", path: "/tasks", icon: <CheckSquare className="w-4 h-4" /> },
  { label: "Genome", path: "/genome", icon: <Dna className="w-4 h-4" /> },
  { label: "Analytics", path: "/analytics", icon: <BarChart3 className="w-4 h-4" /> },
  { label: "Interventions", path: "/interventions", icon: <Zap className="w-4 h-4" /> },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const { user } = useAuth();
  const { signOut, isSigningOut } = useGoogleAuth();

  const displayName = user?.displayName || user?.email || "User";
  const email = user?.email || "";
  const initials = getInitials(displayName);

  const isActive = (path: string) =>
    location.pathname === path || location.pathname.startsWith(path + "/");

  return (
    <aside className="w-60 shrink-0 h-screen sticky top-0 flex flex-col bg-bg-secondary border-r border-neutral-100">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-neutral-100">
        <div className="flex items-center gap-2.5">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
            style={{
              background: "linear-gradient(135deg, #4F7BFF 0%, #3E67F5 100%)",
            }}
          >
            <span className="text-white font-bold text-sm">S</span>
          </div>
          <div className="min-w-0">
            <span className="font-semibold text-text-primary text-sm tracking-tight">
              SPARK
            </span>
            <p className="text-[10px] text-text-muted leading-none mt-0.5">
              Completion Intelligence
            </p>
          </div>
        </div>
      </div>

      {/* Main navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p className="text-[10px] font-semibold text-text-muted uppercase tracking-wider px-3 mb-2">
          Workspace
        </p>
        {NAV_ITEMS.map((item) => {
          const active = isActive(item.path);
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={clsx("nav-item", active && "nav-item-active")}
            >
              <span className={clsx(active ? "text-accent" : "text-text-muted")}>
                {item.icon}
              </span>
              <span className="flex-1 text-sm">{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User profile + sign out */}
      <div className="px-3 py-4 border-t border-neutral-100">
        <div className="flex items-center gap-2 px-1">
          <div className="flex items-center gap-2 flex-1 min-w-0 px-2 py-1.5">
            {user?.photoURL ? (
              <img
                src={user.photoURL}
                alt={displayName}
                className="w-7 h-7 rounded-full object-cover shrink-0"
                referrerPolicy="no-referrer"
              />
            ) : (
              <div className="w-7 h-7 rounded-full bg-accent-light flex items-center justify-center shrink-0">
                <span className="text-accent text-xs font-semibold">
                  {initials}
                </span>
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-text-primary truncate">
                {displayName}
              </p>
              {email && (
                <p className="text-[10px] text-text-muted truncate">{email}</p>
              )}
            </div>
          </div>

          <Tooltip content="Sign out" position="right">
            <button
              onClick={signOut}
              disabled={isSigningOut}
              className="w-7 h-7 rounded-lg flex items-center justify-center text-text-muted hover:text-danger hover:bg-danger-light transition-smooth shrink-0 disabled:opacity-50"
              aria-label="Sign out"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </Tooltip>
        </div>
      </div>
    </aside>
  );
};

Sidebar.displayName = "Sidebar";