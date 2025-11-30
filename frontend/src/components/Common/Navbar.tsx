import { Flex, Heading, useBreakpointValue } from "@chakra-ui/react"
import { Link } from "@tanstack/react-router"

import UserMenu from "./UserMenu"

function Navbar() {
  const display = useBreakpointValue({ base: "none", md: "flex" })

  return (
    <Flex
      display={display}
      justify="space-between"
      position="sticky"
      align="center"
      bg="bg.muted"
      w="100%"
      top={0}
      p={4}
    >
      <Link to="/">
        <Heading
          size="2xl"
          fontWeight="bold"
          letterSpacing="tight"
          _hover={{ opacity: 0.8 }}
        >
          Mosaic
        </Heading>
      </Link>
      <Flex gap={2} alignItems="center">
        <UserMenu />
      </Flex>
    </Flex>
  )
}

export default Navbar
