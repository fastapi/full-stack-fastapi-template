"use client"

import { ChakraProvider } from "@chakra-ui/react"
import React, { type PropsWithChildren } from "react"
import { theme } from "../../theme"
import { ColorModeProvider } from "./color-mode"
import { Toaster, ToasterProvider } from "./toaster"

export function CustomProvider({ children }: PropsWithChildren) {
  return (
    <ChakraProvider theme={theme}>
      <ToasterProvider>
        <ColorModeProvider defaultTheme="light">
          {children}
        </ColorModeProvider>
        <Toaster />
      </ToasterProvider>
    </ChakraProvider>
  )
}
