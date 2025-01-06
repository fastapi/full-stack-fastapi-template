import {
  Icon as ChakraIcon,
  type IconProps as ChakraIconProps,
  Span,
} from "@chakra-ui/react"
import React from "react"
import type { IconType } from "react-icons"

// workaround for forwardRef issues using normal Chakra Icon
// see https://github.com/chakra-ui/chakra-ui/issues/9227

type ReactIconProps = ChakraIconProps & {
  icon: IconType
}

const ReactIcon = React.forwardRef<HTMLElement, ReactIconProps>(
  ({ icon: IconElement, ...props }, ref) => (
    <ChakraIcon {...props} asChild>
      <Span ref={ref}>
        <IconElement style={{ width: "100%", height: "100%" }} />
      </Span>
    </ChakraIcon>
  ),
)

export { ReactIcon }
