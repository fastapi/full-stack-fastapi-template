import { Flex, Image } from "@chakra-ui/react"
import Logo from "/assets/images/fastapi-logo.svg"

import { RouterLink } from "../ui/router-link"
import { SidebarMobile } from "./Sidebar"
import UserMenu from "./UserMenu"

export const NAVBAR_HEIGHT = 12

const Navbar = () => {
  return (
    <>
      <Flex
        position="fixed"
        top={0}
        left={0}
        height={NAVBAR_HEIGHT}
        width="100%"
        alignItems="center"
        bg="white"
        zIndex={100}
        boxShadow="md"
      >
        <SidebarMobile />
        <RouterLink to={"/"} asChild>
          <Image src={Logo} alt="logo" h="100%" p={3} />
        </RouterLink>
        <Flex justifyContent="end" flex={1}>
          <UserMenu />
        </Flex>
      </Flex>
    </>
  )
}

export default Navbar
