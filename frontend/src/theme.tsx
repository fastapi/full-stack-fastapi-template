import { createSystem, defaultConfig, defineConfig } from "@chakra-ui/react"

// If you update this, run `npx chakra typegen ./theme.ts` to generate the types

// TODO reimplement component styles
// const disabledStyles = {
//   _disabled: {
//     backgroundColor: "ui.main",
//   },
// }

const config = defineConfig({
  theme: {
    tokens: {
      // colors: {
      //   main: {value: "#009688"},
      //   secondary: {value: "#EDF2F7"},
      //   success: {value: "#48BB78"},
      //   danger: {value: "#E53E3E"},
      //   light: {value: "#FAFAFA"},
      //   dark: {value: "#1A202C"},
      //   darkSlate: {value: "#252D3D"},
      //   dim: {value: "#A0AEC0"}
      // },
      // components: {
      //   Button: {
      //     variants: {
      //       primary: {
      //         backgroundColor: "ui.main",
      //         color: "ui.light",
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
    },
  },
})

export const system = createSystem(defaultConfig, config)
