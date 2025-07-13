import type { ButtonProps as ChakraButtonProps } from "@chakra-ui/react"
import {
  AbsoluteCenter,
  Button as ChakraButton,
  Span,
  Spinner,
} from "@chakra-ui/react"
import * as React from "react"

interface ButtonLoadingProps {
  loading?: boolean
  loadingText?: React.ReactNode
}

export interface ButtonProps extends ChakraButtonProps, ButtonLoadingProps {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  function Button(props, ref) {
    const {
      loading,
      disabled,
      loadingText,
      children,
      variant = "solid",
      colorScheme = "teal",
      size = "md",
      ...rest
    } = props

    return (
      <ChakraButton
        disabled={loading || disabled}
        ref={ref}
        variant={variant}
        colorScheme={colorScheme}
        size={size}
        _hover={{
          transform: "translateY(-1px)",
        }}
        _active={{
          transform: "translateY(0)",
        }}
        transition="all 0.2s"
        {...rest}
      >
        {loading && !loadingText ? (
          <>
            <AbsoluteCenter display="inline-flex">
              <Spinner size="inherit" color="inherit" />
            </AbsoluteCenter>
            <Span opacity={0}>{children}</Span>
          </>
        ) : loading && loadingText ? (
          <>
            <Spinner size="inherit" color="inherit" mr={2} />
            {loadingText}
          </>
        ) : (
          children
        )}
      </ChakraButton>
    )
  },
)
