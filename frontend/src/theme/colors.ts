// Custom color scheme for AI Soul Entity
export const customColors = {
  // Primary brand colors - using a more balanced green/teal palette
  primary: {
    50: "#f0fdfa",
    100: "#ccfbf1",
    200: "#99f6e4",
    300: "#5eead4",
    400: "#2dd4bf",
    500: "#14b8a6",
    600: "#0d9488",
    700: "#0f766e",
    800: "#115e59",
    900: "#134e4a",
  },

  // Secondary colors - complementary blue-gray
  secondary: {
    50: "#f8fafc",
    100: "#f1f5f9",
    200: "#e2e8f0",
    300: "#cbd5e1",
    400: "#94a3b8",
    500: "#64748b",
    600: "#475569",
    700: "#334155",
    800: "#1e293b",
    900: "#0f172a",
  },

  // Accent colors - warm orange
  accent: {
    50: "#fef7ed",
    100: "#feebc8",
    200: "#fbd38d",
    300: "#f6ad55",
    400: "#ed8936",
    500: "#dd6b20",
    600: "#c05621",
    700: "#9c4221",
    800: "#7b341e",
    900: "#652b19",
  },

  // Status colors
  success: {
    50: "#f0fdf4",
    100: "#dcfce7",
    200: "#bbf7d0",
    300: "#86efac",
    400: "#4ade80",
    500: "#22c55e",
    600: "#16a34a",
    700: "#15803d",
    800: "#166534",
    900: "#14532d",
  },

  warning: {
    50: "#fffbeb",
    100: "#fef3c7",
    200: "#fde68a",
    300: "#fcd34d",
    400: "#fbbf24",
    500: "#f59e0b",
    600: "#d97706",
    700: "#b45309",
    800: "#92400e",
    900: "#78350f",
  },

  error: {
    50: "#fef2f2",
    100: "#fee2e2",
    200: "#fecaca",
    300: "#fca5a5",
    400: "#f87171",
    500: "#ef4444",
    600: "#dc2626",
    700: "#b91c1c",
    800: "#991b1b",
    900: "#7f1d1d",
  },

  // Info colors
  info: {
    50: "#eff6ff",
    100: "#dbeafe",
    200: "#bfdbfe",
    300: "#93c5fd",
    400: "#60a5fa",
    500: "#3b82f6",
    600: "#2563eb",
    700: "#1d4ed8",
    800: "#1e40af",
    900: "#1e3a8a",
  },

  // Neutral grays
  gray: {
    50: "#f9fafb",
    100: "#f3f4f6",
    200: "#e5e7eb",
    300: "#d1d5db",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    700: "#374151",
    800: "#1f2937",
    900: "#111827",
  },
}

// Color mappings for different UI elements
export const colorMappings = {
  // Primary buttons, links, etc.
  brand: customColors.primary,

  // Secondary elements
  secondary: customColors.secondary,

  // Accent elements
  accent: customColors.accent,

  // Status colors
  success: customColors.success,
  warning: customColors.warning,
  error: customColors.error,
  info: customColors.info,

  // Text and backgrounds
  gray: customColors.gray,
}

// Utility functions for color usage
export const getStatusColor = (status: string): string => {
  switch (status?.toLowerCase()) {
    case "success":
    case "completed":
    case "active":
    case "healthy":
    case "ok":
      return "success"
    case "warning":
    case "pending":
    case "processing":
    case "degraded":
      return "warning"
    case "error":
    case "failed":
    case "inactive":
    case "unhealthy":
      return "error"
    case "info":
    case "draft":
      return "info"
    default:
      return "gray"
  }
}

// Role-based color mapping
export const getRoleColor = (role: string): string => {
  switch (role?.toLowerCase()) {
    case "admin":
    case "superuser":
      return "error"
    case "trainer":
    case "moderator":
      return "info"
    default:
      return "gray"
  }
}
