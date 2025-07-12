import { extendTheme, type ThemeConfig } from "@chakra-ui/react"
import { buttonTheme } from "./theme/button.recipe"

// Configuración del tema
const config: ThemeConfig = {
  initialColorMode: 'dark',
  useSystemColorMode: false,
}

// Extender el tema de Chakra UI
export const theme = extendTheme({
  config,
  styles: {
    global: {
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
  },
  colors: {
    // Colores corporativos dark
    ui: {
      main: "#3B82F6", // Azul principal
      bg: "#0D1117", // Fondo principal
      surface: "#161B22", // Superficies
      border: "#30363D", // Bordes
      text: {
        primary: "#F0F6FC",
        secondary: "#8B949E",
        muted: "#6E7681"
      },
    },
    // Colores de escala de grises
    gray: {
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
  components: {
    Button: buttonTheme,
  },
  semanticTokens: {
    colors: {
      bg: {
        default: "ui.bg",
        _dark: "ui.bg",
        surface: {
          default: "ui.surface",
          _dark: "ui.surface",
        },
        muted: {
          default: "gray.100",
          _dark: "gray.800",
        },
      },
      text: {
        default: "ui.text.primary",
        _dark: "ui.text.primary",
        muted: {
          default: "ui.text.secondary",
          _dark: "ui.text.secondary",
        },
        subtle: {
          default: "ui.text.muted",
          _dark: "ui.text.muted",
        },
      },
      border: {
        default: "ui.border",
        _dark: "ui.border",
        muted: {
          default: "gray.200",
          _dark: "gray.700",
        },
      },
    },
  },
})
