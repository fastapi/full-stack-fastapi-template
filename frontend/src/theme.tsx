//mport {
// extendTheme,
// createMultiStyleConfigHelpers,
// Textarea,
// defineStyle,
// defineStyleConfig,
// from "@chakra-ui/react";
//mport { sliderAnatomy as parts } from "@chakra-ui/anatomy";
//mport { inputAnatomy, } from "@chakra-ui/anatomy";
//mport { system } from "@chakra-ui/react/preset";
//
//
//
//onst { definePartsStyle, defineMultiStyleConfig } =
// createMultiStyleConfigHelpers(inputAnatomy.keys);
//
//onst textareaoutline = defineStyle({
// border: "2px dashed", // change the appearance of the border
// borderRadius: 0,
// bg: "white",
//        // remove the border radius
// fontWeight: "semibold", // change the font weight
// _hover: {
//   bg: "green.50",
//   borderColor: "009688",
//   _dark: {
//     bg: "whiteAlpha.100",
//   }
// },
//  _focus: {
//       borderColor: "green.500",
//       borderWidth: 2,
//       _dark: {
//         bg: "whiteAlpha.100",
//       },
//     },
//);
//
//onst textareaTheme = defineStyleConfig({
// variants: { outline: textareaoutline },
//);
/// default base style from the Input theme
//onst baseStyle = definePartsStyle({
// field: {
//   width: "100%",
//   minWidth: 0,
//   outline: 0,
//   position: "relative",
//   appearance: "none",
//   transitionProperty: "common",
//   transitionDuration: "normal",
//   _disabled: {
//     opacity: 0.4,
//     cursor: "not-allowed",
//   },
// },
//);
//
//
//
//
//onst variantInput = definePartsStyle((props) => {
// return {
//   field: {
//     fontFamily: "cursive", // change font family to mono
//     bg: "white",
//     borderColor: "009688",
//     fontsize: "large",
//
//     _focus: {
//       borderColor: "green.500",
//       borderWidth: 2,
//       _dark: {
//         bg: "whiteAlpha.100",
//       },
//     },
//     _hover: {
//       bg: "green.50",
//       borderColor: "009688",
//       _dark: {
//         bg: "whiteAlpha.100",
//       },
//     },
//   },
// };
//);
//
//onst variantTextArea = definePartsStyle((props) => {
// return {
//   field: {
//     fontFamily: "cursive", // change font family to mono
//     bg: "white",
//
//     borderColor: "green.500",
//     borderWidth: "2px",
//     fontsize: "XX-large",
//
//     _focus: {
//       borderColor: "green.500",
//       borderWidth: 2,
//       _dark: {
//         bg: "whiteAlpha.100",
//       },
//     },
//     _focusWithin: { borderColor: "green.500" },
//     _hover: {
//       bg: "green.500",
//       borderColor: "009688",
//     },
//   },
// };
//);
//
//onst disabledStyles = {
// _disabled: {
//   backgroundColor: "ui.light",
// },
//;
//onst variants = {
// outline: variantInput,
// line: variantTextArea,
//;
//onst inputTheme = defineMultiStyleConfig({
// baseStyle,
// variants,
// defaultProps: {
//   size: "md",
//   variant: "outline",
// },
//);
//
//onst TextAreaTheme = defineMultiStyleConfig({
// baseStyle,
// variants,
// defaultProps: {
//   size: "md",
//   variant: "textArea",
// },
//);
//
//onst theme = extendTheme({
// colors: {
//   ui: {
//     main: "#009688",
//     secondary: "#EDF2F7",
//     success: "#48BB78",
//     danger: "#E53E3E",
//     light: "B7E0FF",
//     dark: "#1A202C",
//     darkSlate: "#252D3D",
//     dim: "#A0AEC0",
//   },
// },
// components: {
//   Textarea: textareaTheme,
//   Input: inputTheme,
//   Button: {
//     variants: {
//       primary: {
//         backgroundColor: "ui.main",
//
//         color: "white",
//         _hover: {
//           backgroundColor: "#00766C",
//         },
//         _disabled: {
//           ...disabledStyles,
//           _hover: {
//             ...disabledStyles,
//           },
//         },
//       },
//       danger: {
//         backgroundColor: "ui.danger",
//         color: "ui.light",
//         _hover: {
//           backgroundColor: "#E32727",
//         },
//       },
//     },
//   },
//   Tabs: {
//     variants: {
//       enclosed: {
//         tab: {
//           _selected: {
//             color: "ui.main",
//           },
//         },
//       },
//     },
//   },
// },
//
// styles: {
//   global: (props) => ({
//     body: {
//       bg: "antiqueWhite",
//       fontFamily: "cursive",
//       fontSize: "large",
//     },
//   }),
// },
//);
//
//xport default system ;
//
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
    ".main-link": {
      color: "ui.main",
      fontWeight: "bold",
    },
  },
  theme: {
    tokens: {
      colors: {
        ui: {
          main: { value: "#009688" },
        },
      },
    },
    recipes: {
      button: buttonRecipe,
    },
  },
})