import { Box, Container } from "@chakra-ui/react"
import { Outlet, createFileRoute, redirect } from "@tanstack/react-router"
import React from "react"
import Navbar from "../components/Common/Navbar"
import Sidebar from "../components/Common/Sidebar"
import { isLoggedIn } from "../hooks/useAuth"

export const Route = createFileRoute("/_layout")({
  beforeLoad: ({ location }: { location: any }) => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
        search: {
          redirect: location.href,
        },
      })
    }
  },
  component: Layout,
})

function Layout() {
  return (
    <Box minH="100vh" bg="gray.50" _dark={{ bg: "gray.900" }}>
      <Navbar />
      <Box display="flex" pt="4rem">
        <Sidebar />
        <Box
          as="main"
          flex="1"
          ml={{ base: 0, md: "16rem" }}
          transition=".3s ease"
        >
          <Container maxW="full" p={0}>
            <Outlet />
          </Container>
        </Box>
      </Box>
    </Box>
  )
}

export default Layout
