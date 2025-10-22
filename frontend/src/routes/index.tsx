import { useEffect } from "react"

import { createFileRoute, useNavigate } from "@tanstack/react-router"

import { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/")({
  component: RootRedirect,
})

function RootRedirect() {
  const navigate = useNavigate()

  useEffect(() => {
    navigate({
      to: isLoggedIn() ? "/dashboard" : "/landing",
      replace: true,
    })
  }, [navigate])

  return null
}

export default RootRedirect
