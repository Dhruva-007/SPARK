/**
 * SPARK Design Tokens
 *
 * Single source of truth for the entire design system.
 * Every component consumes these tokens.
 */

export const tokens = {
  // ─────────────────────────────────────────────
  // COLOR SYSTEM
  // ─────────────────────────────────────────────
  color: {
    // Backgrounds
    bg: {
      primary: "#F8F9FB",
      secondary: "#FFFFFF",
      elevated: "#FCFCFD",
      glass: "rgba(255, 255, 255, 0.60)",
      glassOverlay: "rgba(255, 255, 255, 0.45)",
    },

    // Text
    text: {
      primary: "#111827",
      secondary: "#4B5563",
      muted: "#6B7280",
      disabled: "#9CA3AF",
      inverse: "#FFFFFF",
      accent: "#3F6DF6",
    },

    // Borders & Dividers
    border: {
      default: "rgba(15, 23, 42, 0.08)",
      subtle: "rgba(15, 23, 42, 0.05)",
      strong: "rgba(15, 23, 42, 0.14)",
      focus: "#3F6DF6",
    },

    // Accent / Brand
    accent: {
      primary: "#3F6DF6",
      hover: "#3158D8",
      light: "#EEF3FF",
      muted: "#DBEAFE",
    },

    // Semantic
    success: {
      base: "#16A34A",
      light: "#DCFCE7",
      muted: "#BBF7D0",
    },
    warning: {
      base: "#F59E0B",
      light: "#FEF3C7",
      muted: "#FDE68A",
    },
    danger: {
      base: "#DC2626",
      light: "#FEE2E2",
      muted: "#FECACA",
    },
    info: {
      base: "#2563EB",
      light: "#DBEAFE",
      muted: "#BFDBFE",
    },

    // CMS / Momentum semantic colors
    momentum: {
      critical: "#DC2626",   // 0-30% — critical risk
      high: "#F59E0B",       // 31-50% — high risk
      medium: "#EAB308",     // 51-70% — building
      good: "#16A34A",       // 71-85% — good momentum
      peak: "#2563EB",       // 86-100% — peak
    },

    // Neutral scale
    neutral: {
      50: "#F9FAFB",
      100: "#F3F4F6",
      200: "#E5E7EB",
      300: "#D1D5DB",
      400: "#9CA3AF",
      500: "#6B7280",
      600: "#4B5563",
      700: "#374151",
      800: "#1F2937",
      900: "#111827",
    },
  },

  // ─────────────────────────────────────────────
  // TYPOGRAPHY
  // ─────────────────────────────────────────────
  font: {
    family: {
      sans: '"Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
      mono: '"JetBrains Mono", "Fira Code", monospace',
    },
    size: {
      xs: "0.75rem",    // 12px
      sm: "0.875rem",   // 14px
      base: "1rem",     // 16px
      lg: "1.125rem",   // 18px
      xl: "1.25rem",    // 20px
      "2xl": "1.5rem",  // 24px
      "3xl": "1.875rem",// 30px
      "4xl": "2.25rem", // 36px
      "5xl": "3rem",    // 48px
    },
    weight: {
      normal: "400",
      medium: "500",
      semibold: "600",
      bold: "700",
      extrabold: "800",
    },
    lineHeight: {
      tight: "1.25",
      snug: "1.375",
      normal: "1.5",
      relaxed: "1.625",
      loose: "2",
    },
    letterSpacing: {
      tight: "-0.025em",
      normal: "0em",
      wide: "0.025em",
      wider: "0.05em",
      widest: "0.1em",
    },
  },

  // ─────────────────────────────────────────────
  // SPACING SCALE
  // ─────────────────────────────────────────────
  space: {
    0: "0px",
    1: "4px",
    2: "8px",
    3: "12px",
    4: "16px",
    5: "20px",
    6: "24px",
    8: "32px",
    10: "40px",
    12: "48px",
    16: "64px",
    20: "80px",
    24: "96px",
    32: "128px",
  },

  // ─────────────────────────────────────────────
  // BORDER RADIUS
  // ─────────────────────────────────────────────
  radius: {
    none: "0px",
    sm: "6px",
    md: "10px",
    lg: "14px",
    xl: "18px",
    "2xl": "24px",
    full: "9999px",
  },

  // ─────────────────────────────────────────────
  // SHADOWS — Minimal, purposeful depth
  // ─────────────────────────────────────────────
  shadow: {
    none: "none",
    xs: "0 1px 2px rgba(15, 23, 42, 0.04)",
    sm: "0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04)",
    md: "0 4px 6px rgba(15, 23, 42, 0.05), 0 2px 4px rgba(15, 23, 42, 0.04)",
    lg: "0 10px 15px rgba(15, 23, 42, 0.05), 0 4px 6px rgba(15, 23, 42, 0.03)",
    xl: "0 20px 25px rgba(15, 23, 42, 0.06), 0 8px 10px rgba(15, 23, 42, 0.04)",
    button: "0 1px 2px rgba(63, 109, 246, 0.20), 0 1px 3px rgba(15, 23, 42, 0.08)",
    buttonHover: "0 4px 8px rgba(63, 109, 246, 0.25), 0 2px 4px rgba(15, 23, 42, 0.08)",
    card: "0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04)",
    cardHover: "0 4px 12px rgba(15, 23, 42, 0.08), 0 2px 4px rgba(15, 23, 42, 0.04)",
    modal: "0 25px 50px rgba(15, 23, 42, 0.12), 0 10px 20px rgba(15, 23, 42, 0.08)",
  },

  // ─────────────────────────────────────────────
  // ANIMATION
  // ─────────────────────────────────────────────
  duration: {
    instant: "0ms",
    fast: "100ms",
    normal: "200ms",
    slow: "300ms",
    slower: "500ms",
    page: "250ms",
  },

  easing: {
    default: "cubic-bezier(0.4, 0, 0.2, 1)",
    in: "cubic-bezier(0.4, 0, 1, 1)",
    out: "cubic-bezier(0, 0, 0.2, 1)",
    inOut: "cubic-bezier(0.4, 0, 0.2, 1)",
    spring: "cubic-bezier(0.34, 1.56, 0.64, 1)",
  },

  // ─────────────────────────────────────────────
  // Z-INDEX SCALE
  // ─────────────────────────────────────────────
  zIndex: {
    base: 0,
    raised: 10,
    dropdown: 100,
    sticky: 200,
    overlay: 300,
    modal: 400,
    toast: 500,
    tooltip: 600,
  },

  // ─────────────────────────────────────────────
  // BREAKPOINTS
  // ─────────────────────────────────────────────
  breakpoint: {
    sm: "640px",
    md: "768px",
    lg: "1024px",
    xl: "1280px",
    "2xl": "1536px",
  },

  // ─────────────────────────────────────────────
  // OPACITY
  // ─────────────────────────────────────────────
  opacity: {
    0: "0",
    10: "0.10",
    20: "0.20",
    40: "0.40",
    60: "0.60",
    80: "0.80",
    100: "1",
  },
} as const;

export type Tokens = typeof tokens;