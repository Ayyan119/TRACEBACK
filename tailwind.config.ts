import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bgApp: "var(--bg-app)",
        bgSecondary: "var(--bg-secondary)",
        bgSurface: "var(--bg-surface)",
        bgSurfaceHover: "var(--bg-surface-hover)",
        bgElevated: "var(--bg-elevated)",
        borderColor: "var(--border-color)",
        textPrimary: "var(--text-primary)",
        textSecondary: "var(--text-secondary)",
        textMuted: "var(--text-muted)",
        accentPrimary: "var(--accent-primary)",
        accentHover: "var(--accent-hover)",
        accentSubtle: "var(--accent-subtle)",
        statusSuccess: "var(--status-success)",
        statusWarning: "var(--status-warning)",
        statusDanger: "var(--status-danger)",
        statusInfo: "var(--status-info)",
      },
      fontFamily: {
        sans: ["var(--font-sans)"],
        mono: ["var(--font-mono)"],
      },
    },
  },
  plugins: [],
};

export default config;
