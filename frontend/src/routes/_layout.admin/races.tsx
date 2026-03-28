import { createFileRoute, Outlet } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/admin/races")({
  component: AdminRacesLayout,
  head: () => ({
    meta: [
      {
        title: "Race Management - Admin",
      },
    ],
  }),
})

function AdminRacesLayout() {
  return <Outlet />
}
