import { defineRecipe } from "@chakra-ui/react"

export const buttonRecipe = defineRecipe({
  base: {
    fontFamily: "'Rubik', sans-serif",
    fontWeight: "600",
    borderRadius: "6px",
    transition: "all 0.2s",
  },
  variants: {
    variant: {
      solid: {
        bg: "#1E3A8A",
        color: "white",
        _hover: {
          bg: "#1E40AF",
        },
      },
      primary: {
        bg: "#F59E0B",
        color: "#1E3A8A",
        fontWeight: "600",
        _hover: {
          bg: "#D97706",
        },
      },
      outline: {
        borderColor: "#E2E8F0",
        color: "#475569",
        _hover: {
          borderColor: "#1E3A8A",
          color: "#1E3A8A",
        },
      },
      ghost: {
        color: "#64748B",
        _hover: {
          bg: "#F1F5F9",
          color: "#1E3A8A",
        },
      },
    },
    colorScheme: {
      blue: {
        bg: "#1E3A8A",
        color: "white",
        _hover: { bg: "#1E40AF" },
      },
      gold: {
        bg: "#F59E0B",
        color: "#1E3A8A",
        _hover: { bg: "#D97706" },
      },
      green: {
        bg: "#10B981",
        color: "white",
        _hover: { bg: "#059669" },
      },
    },
  },
  defaultVariants: {
    variant: "solid",
  },
})