/**
 * SPARK — Login Page
 * Google OAuth + Email/Password sign-in and sign-up.
 * Both methods are available — user chooses their preference.
 */

import React, { useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@shared/hooks/useAuth";
import { useGoogleAuth } from "../hooks/useGoogleAuth";
import { useEmailAuth } from "../hooks/useEmailAuth";
import { GoogleSignInButton } from "../components/GoogleSignInButton";
import { PageSpinner } from "@shared/components/ui/Spinner";
import { Input } from "@shared/components/ui/Input";
import { Button } from "@shared/components/ui/Button";
import {
  Zap,
  CheckCircle2,
  TrendingUp,
  Shield,
  Mail,
  ArrowRight,
} from "lucide-react";

const FEATURES = [
  {
    icon: <TrendingUp className="w-4 h-4" />,
    title: "Completion Momentum Score",
    description: "Real-time probability of finishing every task on time",
  },
  {
    icon: <Zap className="w-4 h-4" />,
    title: "Autonomous Task Activation",
    description: "Never stare at a blank page — SPARK starts work for you",
  },
  {
    icon: <Shield className="w-4 h-4" />,
    title: "Point of No Return Detection",
    description: "Intelligent intervention before failure, not after",
  },
  {
    icon: <CheckCircle2 className="w-4 h-4" />,
    title: "Completion Genome",
    description: "Learns your unique behavioral patterns over time",
  },
] as const;

type AuthTab = "signin" | "signup";

export const LoginPage: React.FC = () => {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const {
    signIn: googleSignIn,
    isSigningIn: googleLoading,
    error: googleError,
  } = useGoogleAuth();
  const {
    signIn: emailSignIn,
    signUp: emailSignUp,
    isLoading: emailLoading,
    error: emailError,
  } = useEmailAuth();
  const location = useLocation();
  const from = (location.state as { from?: string })?.from ?? "/dashboard";

  const [tab, setTab] = useState<AuthTab>("signin");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  if (authLoading) return <PageSpinner message="Loading SPARK..." />;
  if (isAuthenticated) return <Navigate to={from} replace />;

  const validate = (): boolean => {
    const errors: Record<string, string> = {};
    if (!email.trim()) errors.email = "Email is required";
    if (!password) errors.password = "Password is required";
    if (password.length > 0 && password.length < 6)
      errors.password = "Minimum 6 characters";
    if (tab === "signup" && !name.trim()) errors.name = "Name is required";
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    if (tab === "signup") {
      await emailSignUp(email.trim(), password, name.trim());
    } else {
      await emailSignIn(email.trim(), password);
    }
  };

  const isLoading = googleLoading || emailLoading;
  const authError = googleError || emailError;

  return (
    <div className="min-h-screen bg-bg-primary flex">
      {/* ── Left — Branding panel ── */}
      <div className="hidden lg:flex lg:w-[45%] flex-col justify-between p-16 bg-bg-secondary border-r border-neutral-100">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center"
            style={{
              background: "linear-gradient(135deg, #4F7BFF 0%, #3E67F5 100%)",
            }}
          >
            <span className="text-white font-bold text-base">S</span>
          </div>
          <span className="font-semibold text-text-primary text-lg tracking-tight">
            SPARK
          </span>
        </div>

        {/* Hero content */}
        <div className="space-y-10">
          <div className="space-y-5">
            <h1 className="text-4xl font-bold text-text-primary tracking-tight leading-[1.15]">
              From Intention
              <br />
              to Action.
            </h1>
            <p className="text-base text-text-secondary leading-relaxed max-w-sm">
              The AI that doesn't remind you.
              <br />
              It helps you finish.
            </p>
          </div>

          {/* Feature list */}
          <div className="space-y-5">
            {FEATURES.map((feature) => (
              <div key={feature.title} className="flex items-start gap-3.5">
                <div className="w-7 h-7 rounded-lg bg-accent-light flex items-center justify-center shrink-0 mt-0.5">
                  <span className="text-accent">{feature.icon}</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-text-primary">
                    {feature.title}
                  </p>
                  <p className="text-xs text-text-muted mt-0.5 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <p className="text-xs text-text-muted">
          © 2026 SPARK — Autonomous Completion Intelligence
        </p>
      </div>

      {/* ── Right — Sign in panel ── */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-sm space-y-6">
          {/* Mobile logo */}
          <div className="flex items-center gap-2.5 lg:hidden">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{
                background: "linear-gradient(135deg, #4F7BFF 0%, #3E67F5 100%)",
              }}
            >
              <span className="text-white font-bold text-sm">S</span>
            </div>
            <span className="font-semibold text-text-primary">SPARK</span>
          </div>

          {/* Heading */}
          <div className="space-y-2">
            <h2 className="text-2xl font-bold text-text-primary tracking-tight">
              {tab === "signin" ? "Welcome back" : "Create your account"}
            </h2>
            <p className="text-sm text-text-muted">
              {tab === "signin"
                ? "Sign in to your completion intelligence workspace."
                : "Start your journey to better task completion."}
            </p>
          </div>

          <div className="space-y-4">
            {/* ── Google Sign-In Button ── */}
            <GoogleSignInButton
              onClick={googleSignIn}
              isLoading={googleLoading}
              disabled={isLoading}
            />

            {/* Divider */}
            <div className="relative flex items-center gap-3">
              <div className="flex-1 h-px bg-neutral-200" />
              <span className="text-xs text-text-muted">or continue with email</span>
              <div className="flex-1 h-px bg-neutral-200" />
            </div>

            {/* ── Tab toggle: Sign In / Create Account ── */}
            <div className="flex bg-neutral-100 rounded-lg p-1">
              <button
                type="button"
                onClick={() => {
                  setTab("signin");
                  setFormErrors({});
                }}
                className={`flex-1 text-sm font-medium py-2 rounded-md transition-smooth ${
                  tab === "signin"
                    ? "bg-white text-text-primary shadow-xs"
                    : "text-text-muted hover:text-text-primary"
                }`}
              >
                Sign In
              </button>
              <button
                type="button"
                onClick={() => {
                  setTab("signup");
                  setFormErrors({});
                }}
                className={`flex-1 text-sm font-medium py-2 rounded-md transition-smooth ${
                  tab === "signup"
                    ? "bg-white text-text-primary shadow-xs"
                    : "text-text-muted hover:text-text-primary"
                }`}
              >
                Create Account
              </button>
            </div>

            {/* ── Email/Password Form ── */}
            <form onSubmit={handleEmailSubmit} className="space-y-4">
              {tab === "signup" && (
                <Input
                  label="Full Name"
                  placeholder="John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  error={formErrors.name}
                  disabled={isLoading}
                />
              )}

              <Input
                label="Email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={formErrors.email}
                disabled={isLoading}
                icon={<Mail className="w-4 h-4" />}
              />

              <Input
                label="Password"
                type="password"
                placeholder="Minimum 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={formErrors.password}
                disabled={isLoading}
              />

              {/* Error display */}
              {authError && (
                <div className="px-4 py-3 bg-danger-light border border-danger/20 rounded-xl">
                  <p className="text-sm text-danger">{authError}</p>
                </div>
              )}

              <Button
                type="submit"
                variant="primary"
                fullWidth
                loading={emailLoading}
                disabled={isLoading}
                icon={<ArrowRight className="w-4 h-4" />}
                iconPosition="right"
              >
                {tab === "signin" ? "Sign In" : "Create Account"}
              </Button>
            </form>

            {/* Trust indicators */}
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: "Secure Auth", sub: "Firebase" },
                { label: "No passwords", sub: "With Google" },
                { label: "Your data", sub: "Private" },
              ].map((item) => (
                <div
                  key={item.label}
                  className="text-center p-2.5 bg-neutral-50 rounded-xl"
                >
                  <p className="text-xs font-medium text-text-primary">
                    {item.label}
                  </p>
                  <p className="text-[10px] text-text-muted mt-0.5">
                    {item.sub}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <p className="text-xs text-text-muted text-center leading-relaxed">
            By signing in, you agree to SPARK's terms of service and privacy
            policy. Your data is never sold or shared.
          </p>
        </div>
      </div>
    </div>
  );
};

LoginPage.displayName = "LoginPage";