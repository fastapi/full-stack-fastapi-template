import { defineStyle, defineStyleConfig } from "@chakra-ui/react"

// Definir la variante ghost personalizada
const ghostVariant = defineStyle({
  bg: 'transparent',
  _hover: {
    bg: 'gray.100',
  },
  _active: {
    bg: 'gray.200',
  },
})

export const buttonTheme = defineStyleConfig({
  baseStyle: {
    fontWeight: 'bold',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    colorScheme: 'teal',
  },
  variants: {
    ghost: ghostVariant,
  },
  defaultProps: {
    variant: 'ghost',
  },
})
