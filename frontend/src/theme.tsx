import { createSystem, defaultConfig } from "@chakra-ui/react"
import { buttonRecipe } from "./theme/button.recipe"

export const system = createSystem(defaultConfig, {
  globalCss: {
    html: {
      fontSize: "16px",
      colorScheme: "dark",
    },
    body: {
      fontSize: "0.875rem",
      margin: 0,
      padding: 0,
      bg: "gray.900",
      color: "white",
      minHeight: "100vh",
    },
    "*": {
      scrollbarWidth: "thin",
      scrollbarColor: "gray.600 gray.800",
    },
    "::-webkit-scrollbar": {
      width: "8px",
    },
    "::-webkit-scrollbar-track": {
      bg: "gray.800",
    },
    "::-webkit-scrollbar-thumb": {
      bg: "gray.600",
      borderRadius: "4px",
    },
    ".main-link": {
      color: "blue.400",
      fontWeight: "bold",
      _hover: {
        color: "blue.300",
      },
    },
  },
  theme: {
    tokens: {
      colors: {
        // Colores corporativos dark
        ui: {
          main: { value: "#3B82F6" }, // Azul principal
          bg: { value: "#0D1117" }, // Fondo principal
          surface: { value: "#161B22" }, // Superficies
          border: { value: "#30363D" }, // Bordes
          text: {
            primary: { value: "#F0F6FC" },
            secondary: { value: "#8B949E" },
            muted: { value: "#6E7681" },
          },
        },
        // Override default colors para dark mode
        gray: {
          50: { value: "#F9FAFB" },
          100: { value: "#F3F4F6" },
          200: { value: "#E5E7EB" },
          300: { value: "#D1D5DB" },
          400: { value: "#9CA3AF" },
          500: { value: "#6B7280" },
          600: { value: "#4B5563" },
          700: { value: "#374151" },
          800: { value: "#1F2937" },
          900: { value: "#111827" },
        },
      },
    },
    recipes: {
      button: buttonRecipe,
    },
    semanticTokens: {
      colors: {
        bg: {
          DEFAULT: { value: "{colors.ui.bg}" },
          surface: { value: "{colors.ui.surface}" },
          muted: { value: "{colors.gray.800}" },
        },
        text: {
          DEFAULT: { value: "{colors.ui.text.primary}" },
          muted: { value: "{colors.ui.text.secondary}" },
          subtle: { value: "{colors.ui.text.muted}" },
        },
        border: {
          DEFAULT: { value: "{colors.ui.border}" },
          muted: { value: "{colors.gray.700}" },
        },
      },
    },
  },
})
