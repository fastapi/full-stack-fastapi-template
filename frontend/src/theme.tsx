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
      colorPalette: 'purple',
    },
    ".main-link": {
      color: "ui.main",
      fontWeight: "bold",
    },
  },
  theme: {
    tokens: {
      fonts: {
        body: { value: 'var(--font-geist)' },
      },
    },
    semanticTokens: {
      radii: {
        l1: { value: '0.125rem' },
        l2: { value: '0.25rem' },
        l3: { value: '0.375rem' },
      },
    },
  },
})
