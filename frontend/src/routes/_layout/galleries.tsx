import { createFileRoute, Outlet } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/galleries")({
  component: GalleriesLayout,
  head: () => ({
    meta: [
      {
        title: 'Galleries',
      },
    ],
  })
})

function GalleriesLayout() {
  return <Outlet />
}
