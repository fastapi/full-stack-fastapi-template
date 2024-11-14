// This file customizes the default Chakra UI theme with a set of defined colors 
// and component styles. It configures UI colors, button variants, and tab styling 
// to give the application a cohesive look and feel.

import { extendTheme } from "@chakra-ui/react"

// Define styles for disabled elements, used across components
const disabledStyles = {
  _disabled: {
    backgroundColor: "ui.main",
  },
}

// Extend Chakra's default theme with custom colors and component variants
const theme = extendTheme({
  // Define a color palette for consistent UI styling
  colors: {
    ui: {
      main: "#009688",         // Primary color, used in main elements
      secondary: "#EDF2F7",    // Secondary background color
      success: "#48BB78",      // Color to indicate success
      danger: "#E53E3E",       // Color to indicate danger or errors
      light: "#FAFAFA",        // Light background color
      dark: "#1A202C",         // Dark text color
      darkSlate: "#252D3D",    // Slightly lighter dark color for backgrounds
      dim: "#A0AEC0",          // Dimmed text color, often for placeholders or hints
    },
  },
  // Customize styles for specific Chakra UI components
  components: {
    Button: {
      // Define button variants for primary and danger actions
      variants: {
        primary: {
          backgroundColor: "ui.main",       // Background for primary button
          color: "ui.light",                // Text color for primary button
          _hover: {
            backgroundColor: "#00766C",     // Darker color on hover
          },
          _disabled: {
            ...disabledStyles,              // Apply disabled styles
            _hover: {
              ...disabledStyles,            // Prevent hover styling when disabled
            },
          },
        },
        danger: {
          backgroundColor: "ui.danger",     // Background for danger button
          color: "ui.light",                // Text color for danger button
          _hover: {
            backgroundColor: "#E32727",     // Darker color on hover for danger button
          },
        },
      },
    },
    Tabs: {
      // Define styles for the enclosed tab variant
      variants: {
        enclosed: {
          tab: {
            _selected: {
              color: "ui.main",             // Change color of selected tab
            },
          },
        },
      },
    },
  },
})

export default theme