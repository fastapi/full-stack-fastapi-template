import {
  DrawerBackdrop,
  DrawerBody,
  DrawerCloseTrigger,
  DrawerContent,
  DrawerRoot,
  DrawerTrigger,
} from "@/components/ui/drawer"
import { Box, Flex, Image, Text, useDisclosure } from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { FiLogOut, FiMenu } from "react-icons/fi"

import type { UserPublic } from "@/client"
import useAuth from "@/hooks/useAuth"
import Logo from "/assets/images/fastapi-logo.svg"
import { Button } from "../ui/button"
import { NAVBAR_HEIGHT } from "./Navbar"
import SidebarItems from "./SidebarItems"

export const SidebarMobile = () => {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])
  const { open, onClose, onToggle } = useDisclosure()
  const { logout } = useAuth()

  const handleLogout = async () => {
    logout()
  }

  return (
    <>
      {/* Mobile */}
      <DrawerRoot open={open} placement="start" onOpenChange={onToggle}>
        <DrawerBackdrop />
        <DrawerTrigger asChild display={{ base: "flex", md: "none" }}>
          <Button aria-label="Open Menu" variant="ghost" fontSize="20px" m={2}>
            <FiMenu />
          </Button>
        </DrawerTrigger>
        <DrawerContent maxW="250px" display={{ base: "flex", md: "none" }}>
          <DrawerCloseTrigger />
          <DrawerBody py={8}>
            <Flex flexDir="column" justify="space-between">
              <Box>
                <Image src={Logo} alt="logo" p={6} />
                <SidebarItems onClose={onClose} />
                <Flex
                  as="button"
                  onClick={handleLogout}
                  p={2}
                  colorPalette="red"
                  fontWeight="bold"
                  alignItems="center"
                >
                  <FiLogOut />
                  <Text ml={2}>Log out</Text>
                </Flex>
              </Box>
              {currentUser?.email && (
                <Text lineClamp={2} fontSize="sm" p={2}>
                  Logged in as: {currentUser.email}
                </Text>
              )}
            </Flex>
          </DrawerBody>
        </DrawerContent>
      </DrawerRoot>
    </>
  )
}

export const SidebarDesktop = () => {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  return (
    <>
      <Box
        h="100vh"
        position="sticky"
        top={0}
        display={{ base: "none", md: "flex" }}
      >
        <Flex
          flexDir="column"
          justify="space-between"
          mt={NAVBAR_HEIGHT}
          p={4}
          borderRadius={12}
        >
          <Box>
            <SidebarItems />
          </Box>
          {currentUser?.email && (
            <Text lineClamp={2} fontSize="sm" p={2} maxW="180px">
              Logged in as: {currentUser.email}
            </Text>
          )}
        </Flex>
      </Box>
    </>
  )
}
