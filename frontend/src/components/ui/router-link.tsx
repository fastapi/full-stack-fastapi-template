import { Link } from "@chakra-ui/react"
import { type LinkComponent, createLink } from "@tanstack/react-router"
import * as React from "react"

// source: https://tanstack.com/router/latest/docs/framework/react/guide/custom-link

interface ChakraLinkProps
  extends Omit<React.ComponentPropsWithoutRef<typeof Link>, "href"> {
  // Add any additional props you want to pass to the link
}

const ChakraLinkComponent = React.forwardRef<
  HTMLAnchorElement,
  ChakraLinkProps
>((props, ref) => {
  return <Link ref={ref} {...props} />
})

const CreatedLinkComponent = createLink(ChakraLinkComponent)

/**
 * A custom link component that extends Chakra's Link with Tanstack Router Link functionality.
 * @remarks
 * Always use `RouterLink` as the parent in an `asChild` context (e.g., Button) to prevent forwardRef issues.
 */
export const RouterLink: LinkComponent<typeof ChakraLinkComponent> = (
  props,
) => {
  return (
    <CreatedLinkComponent
      textDecoration={"underline"}
      _hover={{ textDecoration: "none" }}
      _focus={{ textDecoration: "none" }}
      preload={"intent"}
      {...props}
    />
  )
}
