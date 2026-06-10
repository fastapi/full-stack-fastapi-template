import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "var(--bg)",
          deep: "var(--bg-deep)",
        },
        surface: {
          DEFAULT: "var(--surface)",
          2: "var(--surface-2)",
          3: "var(--surface-3)",
        },
        fg: {
          DEFAULT: "var(--fg)",
          muted: "var(--fg-muted)",
          dim: "var(--fg-dim)",
          faint: "var(--fg-faint)",
        },
        line: {
          DEFAULT: "var(--line)",
          soft: "var(--line-soft)",
          bold: "var(--line-bold)",
        },
        cyan: {
          DEFAULT: "var(--cyan)",
          dim: "var(--cyan-dim)",
        },
        amber: {
          DEFAULT: "var(--amber)",
          dim: "var(--amber-dim)",
        },
        ok: { DEFAULT: "var(--ok)", dim: "var(--ok-dim)" },
        warn: { DEFAULT: "var(--warn)", dim: "var(--warn-dim)" },
        bad: { DEFAULT: "var(--bad)", dim: "var(--bad-dim)" },
      },
      fontFamily: {
        display: "var(--font-display)",
        mono: "var(--font-mono)",
        serif: "var(--font-serif)",
      },
      borderRadius: {
        sm: "var(--r-sm)",
        DEFAULT: "var(--r)",
        lg: "var(--r-lg)",
      },
      maxWidth: {
        page: "var(--maxw)",
      },
      boxShadow: {
        panel: "var(--shadow)",
        glow: "var(--shadow-glow)",
      },
    },
  },
  plugins: [],
};

export default config;
