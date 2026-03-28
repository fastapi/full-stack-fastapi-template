import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute, Link as RouterLink } from "@tanstack/react-router"
import { Plus, Search } from "lucide-react"
import { Suspense } from "react"

import { RacesService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import PendingItems from "@/components/Pending/PendingItems"
import { columns } from "@/components/Races/columns"
import { Button } from "@/components/ui/button"

function getRacesQueryOptions() {
  return {
    queryFn: () => RacesService.readRaces({ skip: 0, limit: 100 }),
    queryKey: ["races"],
  }
}

export const Route = createFileRoute("/_layout/admin/races/")({
  component: AdminRaces,
})

function RacesTableContent() {
  const { data: races } = useSuspenseQuery(getRacesQueryOptions())

  if (races.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Search className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No races yet</h3>
        <p className="text-muted-foreground">Add a new race to get started</p>
      </div>
    )
  }

  return <DataTable columns={columns} data={races.data} />
}

function RacesTable() {
  return (
    <Suspense fallback={<PendingItems />}>
      <RacesTableContent />
    </Suspense>
  )
}

function AdminRaces() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Race Management</h2>
          <p className="text-muted-foreground">
            Create and manage race events, categories, and registrations
          </p>
        </div>
        <Button asChild>
          <RouterLink to="/admin/races/new">
            <Plus className="mr-2 h-4 w-4" />
            Add Race
          </RouterLink>
        </Button>
      </div>
      <RacesTable />
    </div>
  )
}
