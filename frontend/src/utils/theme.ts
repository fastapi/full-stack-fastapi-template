// Theme constants for consistent styling across the application

export const THEME_COLORS = {
  // Primary brand color - use for main actions, branding
  primary: "teal",
  
  // Secondary actions, information
  secondary: "blue", 
  
  // Neutral actions, disabled states
  neutral: "gray",
  
  // Destructive actions, errors
  danger: "red",
  
  // Success states, confirmations
  success: "green",
  
  // Warnings, cautions
  warning: "orange",
} as const

export const getThemeColor = (type: keyof typeof THEME_COLORS): string => {
  return THEME_COLORS[type]
}

// Common color schemes for different UI elements
export const UI_COLORS = {
  // Buttons
  primaryButton: THEME_COLORS.primary,
  secondaryButton: THEME_COLORS.secondary,
  dangerButton: THEME_COLORS.danger,
  neutralButton: THEME_COLORS.neutral,
  
  // Badges
  primaryBadge: THEME_COLORS.primary,
  infoBadge: THEME_COLORS.secondary,
  successBadge: THEME_COLORS.success,
  warningBadge: THEME_COLORS.warning,
  dangerBadge: THEME_COLORS.danger,
  
  // Icons
  primaryIcon: THEME_COLORS.primary,
  secondaryIcon: THEME_COLORS.secondary,
  
  // Status indicators
  activeStatus: THEME_COLORS.success,
  inactiveStatus: THEME_COLORS.neutral,
  errorStatus: THEME_COLORS.danger,
  warningStatus: THEME_COLORS.warning,
} as const 