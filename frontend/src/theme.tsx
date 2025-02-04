import { extendTheme } from "@chakra-ui/react"

const disabledStyles = {
  _disabled: {
    backgroundColor: "ui.main",
  },
}

const theme = extendTheme({
  colors: {
    ui: {
      main: "#004D2A",      // Dark forest green
      secondary: "#E5DFD7", // Sandish brown
      success: "#48BB78",   // Keep success green
      danger: "#E53E3E",    // Keep danger red
      light: "#FFFFFF",     // Pure white
      dark: "#1A202C",      // Keep dark
      darkSlate: "#252D3D", // Keep dark slate
      dim: "#A0AEC0",       // Keep dim gray
    },
  },
  components: {
    Button: {
      variants: {
        primary: {
          backgroundColor: "ui.main",
          color: "ui.light",
          _hover: {
            backgroundColor: "#006837", // Slightly lighter forest green for hover
          },
          _disabled: {
            ...disabledStyles,
            _hover: {
              ...disabledStyles,
            },
          },
        },
        danger: {
          backgroundColor: "ui.danger",
          color: "ui.light",
          _hover: {
            backgroundColor: "#E32727",
          },
        },
      },
    },
    Tabs: {
      variants: {
        enclosed: {
          tab: {
            _selected: {
              color: "ui.main",
            },
          },
        },
      },
    },
  },
})

export default theme
