import { createFileRoute } from "@tanstack/react-router"

import AddRace from "@/components/Races/AddRace"

export const Route = createFileRoute("/_layout/admin/races/new")({
  component: AdminAddRace,
  head: () => ({
    meta: [
      {
        title: "Add Race - Admin",
      },
    ],
  }),
})

function AdminAddRace() {
  return <AddRace />
}
