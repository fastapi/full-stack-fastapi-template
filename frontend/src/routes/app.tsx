import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"
import AppLayout from "@/components/app/AppLayout"

export const Route = createFileRoute("/app")({
  beforeLoad: ({ location }) => {
    // Check if user is authenticated
    const isAuthenticated = localStorage.getItem("isAuthenticated") === "true"

    if (!isAuthenticated) {
      throw redirect({
        to: "/",
        search: {
          redirect: location.href,
        },
      })
    }

    // Check if profile is complete (skip check if already on profile-setup page)
    if (!location.pathname.includes("/profile-setup")) {
      const profileComplete =
        localStorage.getItem("profile_complete") === "true"

      // Also check user object for profile_complete flag
      const userStr = localStorage.getItem("user")
      let userProfileComplete = false
      if (userStr) {
        try {
          const user = JSON.parse(userStr)
          userProfileComplete = user.profile_complete === true
        } catch {
          // Ignore parse errors
        }
      }

      if (!profileComplete && !userProfileComplete) {
        throw redirect({
          to: "/app/profile-setup",
        })
      }
    }
  },
  component: () => (
    <AppLayout>
      <Outlet />
    </AppLayout>
  ),
})
