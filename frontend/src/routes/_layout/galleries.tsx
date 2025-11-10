import { createFileRoute, Outlet } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/galleries")({
  component: GalleriesLayout,
})

function GalleriesLayout() {
  return <Outlet />
}
