import { Box, Flex, Spinner } from "@chakra-ui/react"
import { Outlet, createFileRoute, redirect } from "@tanstack/react-router"

import Navbar, { NAVBAR_HEIGHT } from "@/components/Common/Navbar"
import { SidebarDesktop } from "../components/Common/Sidebar"
import useAuth, { isLoggedIn } from "../hooks/useAuth"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function Layout() {
  const { isLoading } = useAuth()

  return (
    <Flex h="100vh" w="100vw" position="relative">
      <Navbar />
      <SidebarDesktop />
      {isLoading ? (
        <Flex justify="center" align="center" height="100vh" width="full">
          <Spinner size="xl" />
        </Flex>
      ) : (
        <Box h="100vh" w="100vw">
          <Box mt={NAVBAR_HEIGHT} p={4}>
            <Outlet />
          </Box>
        </Box>
      )}
    </Flex>
  )
}
