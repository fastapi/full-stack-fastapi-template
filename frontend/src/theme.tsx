import { createSystem, defaultConfig } from "@chakra-ui/react"
import { buttonRecipe } from "./theme/button.recipe"

export const system = createSystem(defaultConfig, {
  globalCss: {
    html: {
      fontSize: "16px",
    },
    body: {
      fontSize: "0.875rem",
      margin: 0,
      padding: 0,
    },
  },
  theme: {
    tokens: {
      colors: {
        ui: {
          // Brand colors
          main: { value: "#009688" },
          secondary: { value: "#EDF2F7" },
          // Neutral colors
          light: { value: "#FAFAFA" },
          dark: { value: "#1A202C" },
          darkSlate: { value: "#252D3D" },
          dim: { value: "#A0AEC0" },
          // Feedback colors
          success: { value: "#48BB78" },
          danger: { value: "#E53E3E" },
        },
      },
    },
    recipes: {
      button: buttonRecipe,
    },
  },
})
