import { createSystem, defaultConfig, defineConfig } from "@chakra-ui/react"

export const system = createSystem(
  defaultConfig,
  defineConfig({
    cssVarsPrefix: "ai-soul",
    globalCss: {
      "html, body": {
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif",
        fontSize: "0.875rem",
        lineHeight: "1.5",
        margin: 0,
        padding: 0,
        color: "gray.800",

        _dark: {
          color: "whiteAlpha.900",
          bg: "gray.900",
        },
      },
      "*": {
        boxSizing: "border-box",
      },
      "h1, h2, h3, h4, h5, h6": {
        fontWeight: "600",
        letterSpacing: "-0.025em",
        lineHeight: "1.25",
      },
      "h1": {
        fontSize: "2.25rem",
        fontWeight: "700",
        letterSpacing: "-0.05em",
      },
      "h2": {
        fontSize: "1.875rem",
        fontWeight: "600",
        letterSpacing: "-0.025em",
      },
      "h3": {
        fontSize: "1.5rem",
        fontWeight: "600",
      },
      "h4": {
        fontSize: "1.25rem",
        fontWeight: "600",
      },
      "h5": {
        fontSize: "1.125rem",
        fontWeight: "600",
      },
      "h6": {
        fontSize: "1rem",
        fontWeight: "600",
      },
      "p": {
        lineHeight: "1.6",
        marginBottom: "1rem",
      },
      "a": {
        transition: "color 0.2s ease-in-out",
      },
      "button": {
        fontFamily: "inherit",
        fontWeight: "500",
      },
      "input, textarea, select": {
        fontFamily: "inherit",
      },
    },
    theme: {
      tokens: {
        colors: {
          // Primary brand colors - using a more balanced green/teal palette
          "primary.50": { value: "#f0fdfa" },
          "primary.100": { value: "#ccfbf1" },
          "primary.200": { value: "#99f6e4" },
          "primary.300": { value: "#5eead4" },
          "primary.400": { value: "#2dd4bf" },
          "primary.500": { value: "#14b8a6" },
          "primary.600": { value: "#0d9488" },
          "primary.700": { value: "#0f766e" },
          "primary.800": { value: "#115e59" },
          "primary.900": { value: "#134e4a" },

          // Brand colors (same as primary for consistency)
          "brand.50": { value: "#f0fdfa" },
          "brand.100": { value: "#ccfbf1" },
          "brand.200": { value: "#99f6e4" },
          "brand.300": { value: "#5eead4" },
          "brand.400": { value: "#2dd4bf" },
          "brand.500": { value: "#14b8a6" },
          "brand.600": { value: "#0d9488" },
          "brand.700": { value: "#0f766e" },
          "brand.800": { value: "#115e59" },
          "brand.900": { value: "#134e4a" },

          // Teal color scheme for components (matching primary)
          "teal.50": { value: "#f0fdfa" },
          "teal.100": { value: "#ccfbf1" },
          "teal.200": { value: "#99f6e4" },
          "teal.300": { value: "#5eead4" },
          "teal.400": { value: "#2dd4bf" },
          "teal.500": { value: "#14b8a6" },
          "teal.600": { value: "#0d9488" },
          "teal.700": { value: "#0f766e" },
          "teal.800": { value: "#115e59" },
          "teal.900": { value: "#134e4a" },

          // Secondary colors - complementary blue-gray
          "secondary.50": { value: "#f8fafc" },
          "secondary.100": { value: "#f1f5f9" },
          "secondary.200": { value: "#e2e8f0" },
          "secondary.300": { value: "#cbd5e1" },
          "secondary.400": { value: "#94a3b8" },
          "secondary.500": { value: "#64748b" },
          "secondary.600": { value: "#475569" },
          "secondary.700": { value: "#334155" },
          "secondary.800": { value: "#1e293b" },
          "secondary.900": { value: "#0f172a" },

          // Neutral gray colors
          "gray.50": { value: "#f9fafb" },
          "gray.100": { value: "#f3f4f6" },
          "gray.200": { value: "#e5e7eb" },
          "gray.300": { value: "#d1d5db" },
          "gray.400": { value: "#9ca3af" },
          "gray.500": { value: "#6b7280" },
          "gray.600": { value: "#4b5563" },
          "gray.700": { value: "#374151" },
          "gray.800": { value: "#1f2937" },
          "gray.900": { value: "#111827" },

          // Status colors
          "success.50": { value: "#f0fdf4" },
          "success.100": { value: "#dcfce7" },
          "success.200": { value: "#bbf7d0" },
          "success.300": { value: "#86efac" },
          "success.400": { value: "#4ade80" },
          "success.500": { value: "#22c55e" },
          "success.600": { value: "#16a34a" },
          "success.700": { value: "#15803d" },
          "success.800": { value: "#166534" },
          "success.900": { value: "#14532d" },

          "warning.50": { value: "#fffbeb" },
          "warning.100": { value: "#fef3c7" },
          "warning.200": { value: "#fde68a" },
          "warning.300": { value: "#fcd34d" },
          "warning.400": { value: "#fbbf24" },
          "warning.500": { value: "#f59e0b" },
          "warning.600": { value: "#d97706" },
          "warning.700": { value: "#b45309" },
          "warning.800": { value: "#92400e" },
          "warning.900": { value: "#78350f" },

          "error.50": { value: "#fef2f2" },
          "error.100": { value: "#fee2e2" },
          "error.200": { value: "#fecaca" },
          "error.300": { value: "#fca5a5" },
          "error.400": { value: "#f87171" },
          "error.500": { value: "#ef4444" },
          "error.600": { value: "#dc2626" },
          "error.700": { value: "#b91c1c" },
          "error.800": { value: "#991b1b" },
          "error.900": { value: "#7f1d1d" },

          // Info colors
          "info.50": { value: "#eff6ff" },
          "info.100": { value: "#dbeafe" },
          "info.200": { value: "#bfdbfe" },
          "info.300": { value: "#93c5fd" },
          "info.400": { value: "#60a5fa" },
          "info.500": { value: "#3b82f6" },
          "info.600": { value: "#2563eb" },
          "info.700": { value: "#1d4ed8" },
          "info.800": { value: "#1e40af" },
          "info.900": { value: "#1e3a8a" },
        },
      },
    },
  }),
)
