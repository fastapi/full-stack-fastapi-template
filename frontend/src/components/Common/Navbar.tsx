import { Flex, Image } from "@chakra-ui/react"
import { Link } from "@tanstack/react-router"
import Logo from "/assets/images/fastapi-logo.svg"
import UserMenu from "./UserMenu"

function Navbar() {
  return (
    <Flex
      w="100%"
      p={4}
      color="white"
      align="center"
      justify="space-between"
      position="sticky"
      top="0"
      zIndex="1000"
      bg="bg.muted"
    >
      <Link to="/">
        <Image src={Logo} alt="Logo" w="180px" maxW="2xs" px={2} />
      </Link>
      <Flex gap={2} alignItems="center">
        <UserMenu />
      </Flex>
    </Flex>
  )
}

export default Navbar
