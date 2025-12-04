import { createSystem, defaultConfig } from "@chakra-ui/react"
import { buttonRecipe } from "./theme/button.recipe"

export const system = createSystem(defaultConfig, {
  globalCss: {
    html: {
      fontSize: "16px",
      fontFamily: "'Sora', sans-serif",
    },
    body: {
      fontSize: "1rem",
      margin: 0,
      padding: 0,
      fontFamily: "'Rubik', sans-serif",
      color: "#1E293B",
      background: "#F8FAFC",

    },
    "h1, h2, h3, h4, h5, h6": {
      fontFamily: "Poppins, sans-serif",
      fontWeight: "600",
      color: "#1E3A8A",
    },
    ".main-link": {
      color: "#1E3A8A",
      fontWeight: "600",
    },
  },
  theme: {
    tokens: {
      colors: {
        // Navy & Gold Color System
        brand: {
          navy: { value: "#1E3A8A" },
          gold: { value: "#F59E0B" },
          darkGold: { value: "#D97706" },
          lightNavy: { value: "#3B82F6" },
          slate: { value: "#334155" },
        },
        ui: {
          main: { value: "#1E3A8A" }, // Navy as main
          accent: { value: "#F59E0B" }, // Gold as accent
          bg: { value: "#F8FAFC" },
          card: { value: "#FFFFFF" },
          border: { value: "#E2E8F0" },
          text: { value: "#1E293B" },
          textMuted: { value: "#64748B" },
        },
        status: {
          success: { value: "#10B981" },
          warning: { value: "#F59E0B" },
          error: { value: "#EF4444" },
          info: { value: "#3B82F6" },
        },
      },
      fonts: {
        heading: { value: "'Poppins', sans-serif" },
        body: { value: "'Rubik', sans-serif" },
      },
    },
    recipes: {
      button: buttonRecipe,
    },
  },
})