import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"
import { UsersService } from "@/client"
import { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/admin")({
  component: AdminLayout,
  beforeLoad: async () => {
    // Check if user is logged in first
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }

    try {
      const user = await UsersService.readUserMe()
      if (!user.is_superuser) {
        throw redirect({
          to: "/",
        })
      }
    } catch (error) {
      // If API call fails (401/403), redirect to login
      throw redirect({
        to: "/login",
      })
    }
  },
})

function AdminLayout() {
  return (
    <div className="flex flex-col gap-6">
      <div className="border-b pb-4">
        <h1 className="text-3xl font-bold tracking-tight">Admin Panel</h1>
        <p className="text-muted-foreground">
          Manage users, items, and system settings
        </p>
      </div>
      <Outlet />
    </div>
  )
}
