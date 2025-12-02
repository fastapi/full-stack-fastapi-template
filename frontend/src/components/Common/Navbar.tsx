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
      bg="#1E3A8A"
      w="100%"
      top={0}
      p={4}
      borderBottom="1px solid #1E40AF"
    >
      <Link to="/">
        <Heading
          size="2xl"
          fontWeight="700"
          letterSpacing="wide"
          color="#F59E0B"
          fontFamily="'Poppins', sans-serif"
          _hover={{ opacity: 0.9 }}
        >
          MOSAIC
        </Heading>
      </Link>
      <Flex gap={2} alignItems="center">
        <UserMenu />
      </Flex>
    </Flex>
  )
}

export default Navbar