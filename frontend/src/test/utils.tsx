import { render, type RenderOptions } from "@testing-library/react"
import { ChakraProvider, defaultSystem } from "@chakra-ui/react"
import type { ReactElement } from "react"

/**
 * Custom render function that wraps components with ChakraProvider
 * for testing Chakra UI components
 */
export function renderWithChakra(
  ui: ReactElement,
  options?: Omit<RenderOptions, "wrapper">,
) {
  return render(ui, {
    wrapper: ({ children }) => (
      <ChakraProvider value={defaultSystem}>{children}</ChakraProvider>
    ),
    ...options,
  })
}

// Re-export everything from testing-library
export * from "@testing-library/react"
