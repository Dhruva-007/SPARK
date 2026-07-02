import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Primary backgrounds
        bg: {
          primary: "#F8F9FB",
          secondary: "#FFFFFF",
          elevated: "#FCFCFD",
        },
        // Text hierarchy
        text: {
          primary: "#111827",
          secondary: "#4B5563",
          muted: "#6B7280",
          disabled: "#9CA3AF",
        },
        // Brand accent
        accent: {
          DEFAULT: "#3F6DF6",
          hover: "#3158D8",
          light: "#EEF3FF",
          muted: "#DBEAFE",
        },
        // Semantic
        success: {
          DEFAULT: "#16A34A",
          light: "#DCFCE7",
        },
        warning: {
          DEFAULT: "#F59E0B",
          light: "#FEF3C7",
        },
        danger: {
          DEFAULT: "#DC2626",
          light: "#FEE2E2",
        },
        info: {
          DEFAULT: "#2563EB",
          light: "#DBEAFE",
        },
        // CMS momentum states
        momentum: {
          critical: "#DC2626",
          high: "#F59E0B",
          medium: "#EAB308",
          good: "#16A34A",
          peak: "#2563EB",
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

      fontFamily: {
        sans: [
          "Inter",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "sans-serif",
        ],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },

      fontSize: {
        xs: ["0.75rem", { lineHeight: "1rem" }],
        sm: ["0.875rem", { lineHeight: "1.25rem" }],
        base: ["1rem", { lineHeight: "1.5rem" }],
        lg: ["1.125rem", { lineHeight: "1.75rem" }],
        xl: ["1.25rem", { lineHeight: "1.75rem" }],
        "2xl": ["1.5rem", { lineHeight: "2rem" }],
        "3xl": ["1.875rem", { lineHeight: "2.25rem" }],
        "4xl": ["2.25rem", { lineHeight: "2.5rem" }],
        "5xl": ["3rem", { lineHeight: "1.25" }],
      },

      borderRadius: {
        sm: "6px",
        md: "10px",
        lg: "14px",
        xl: "18px",
        "2xl": "24px",
      },

      boxShadow: {
        xs: "0 1px 2px rgba(15, 23, 42, 0.04)",
        sm: "0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04)",
        md: "0 4px 6px rgba(15, 23, 42, 0.05), 0 2px 4px rgba(15, 23, 42, 0.04)",
        lg: "0 10px 15px rgba(15, 23, 42, 0.05), 0 4px 6px rgba(15, 23, 42, 0.03)",
        xl: "0 20px 25px rgba(15, 23, 42, 0.06), 0 8px 10px rgba(15, 23, 42, 0.04)",
        card: "0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04)",
        "card-hover": "0 4px 12px rgba(15, 23, 42, 0.08), 0 2px 4px rgba(15, 23, 42, 0.04)",
        button: "0 1px 2px rgba(63, 109, 246, 0.20), 0 1px 3px rgba(15, 23, 42, 0.08)",
        "button-hover": "0 4px 8px rgba(63, 109, 246, 0.25), 0 2px 4px rgba(15, 23, 42, 0.08)",
        modal: "0 25px 50px rgba(15, 23, 42, 0.12), 0 10px 20px rgba(15, 23, 42, 0.08)",
      },

      animation: {
        "fade-in": "fadeIn 200ms cubic-bezier(0.4, 0, 0.2, 1)",
        "slide-up": "slideUp 250ms cubic-bezier(0.4, 0, 0.2, 1)",
        "slide-down": "slideDown 250ms cubic-bezier(0.4, 0, 0.2, 1)",
        "scale-in": "scaleIn 200ms cubic-bezier(0.34, 1.56, 0.64, 1)",
        shimmer: "shimmer 2s linear infinite",
        "progress-fill": "progressFill 0.6s cubic-bezier(0.4, 0, 0.2, 1)",
      },

      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideDown: {
          "0%": { opacity: "0", transform: "translateY(-12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        scaleIn: {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        progressFill: {
          "0%": { width: "0%" },
          "100%": { width: "var(--progress-width)" },
        },
      },

      backgroundImage: {
        "gradient-page": "linear-gradient(180deg, #FAFAFB 0%, #F2F4F8 100%)",
        "gradient-button": "linear-gradient(135deg, #4F7BFF 0%, #3E67F5 100%)",
        "gradient-card": "linear-gradient(135deg, #FFFFFF 0%, #FAFBFF 100%)",
        shimmer:
          "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.8) 50%, transparent 100%)",
      },

      transitionTimingFunction: {
        spring: "cubic-bezier(0.34, 1.56, 0.64, 1)",
        smooth: "cubic-bezier(0.4, 0, 0.2, 1)",
      },

      transitionDuration: {
        fast: "100ms",
        normal: "200ms",
        slow: "300ms",
        page: "250ms",
      },
    },
  },
  plugins: [],
};

export default config;