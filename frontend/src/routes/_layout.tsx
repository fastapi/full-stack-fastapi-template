import { useEffect } from 'react'

import { Flex, Spinner } from "@chakra-ui/react"
import { Outlet, createFileRoute, redirect } from "@tanstack/react-router"

import Sidebar from "../components/Common/Sidebar"
import UserMenu from "../components/Common/UserMenu"
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
  const { isLoading, error, errorUpdateCount, logout } = useAuth()
  useEffect(() => {
    if (errorUpdateCount && error?.message === "Forbidden") {
      console.log("____Unauth____logout");
      logout();
    }
  }, [errorUpdateCount, error, logout]);

  return (
    <Flex maxW="large" h="auto" position="relative">
      <Sidebar />
      {isLoading ? (
        <Flex justify="center" align="center" height="100vh" width="full">
          <Spinner size="xl" color="ui.main" />
        </Flex>
      ) : (
        <Outlet />
      )}
      <UserMenu />
    </Flex>
  )
}
