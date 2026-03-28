import type { ColumnDef } from "@tanstack/react-table"
import { Badge } from "@/components/ui/badge"
import { format } from "date-fns"

import type { RacePublic } from "@/client"
import { cn } from "@/lib/utils"
import { RaceActionsMenu } from "./RaceActionsMenu"

const statusColors = {
  draft: "bg-gray-500",
  published: "bg-blue-500",
  registration_open: "bg-green-500",
  registration_closed: "bg-yellow-500",
  completed: "bg-purple-500",
  cancelled: "bg-red-500",
}

const formatStatus = (status: string | undefined): string => {
  if (!status) return "Draft"
  return status
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ")
}

export const columns: ColumnDef<RacePublic>[] = [
  {
    accessorKey: "name",
    header: "Race Name",
    cell: ({ row }) => (
      <div className="space-y-1">
        <span className="font-semibold">{row.original.name}</span>
        {row.original.city && row.original.state && (
          <p className="text-sm text-muted-foreground">
            {row.original.city}, {row.original.state}
          </p>
        )}
      </div>
    ),
  },
  {
    accessorKey: "event_start_date",
    header: "Event Date",
    cell: ({ row }) => {
      const date = new Date(row.original.event_start_date)
      return (
        <div className="space-y-1">
          <p className="font-medium">{format(date, "MMM dd, yyyy")}</p>
          <p className="text-sm text-muted-foreground">{format(date, "h:mm a")}</p>
        </div>
      )
    },
  },
  {
    accessorKey: "location",
    header: "Location",
    cell: ({ row }) => {
      const location = row.original.location
      return (
        <span className="text-sm text-muted-foreground max-w-xs truncate block">
          {location}
        </span>
      )
    },
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.original.status || "draft"
      return (
        <Badge
          variant="outline"
          className={cn("text-white border-0", statusColors[status as keyof typeof statusColors])}
        >
          {formatStatus(status)}
        </Badge>
      )
    },
  },
  {
    accessorKey: "base_price",
    header: "Price",
    cell: ({ row }) => {
      const price = row.original.base_price
      const currency = row.original.currency
      return price !== null && price !== undefined ? (
        <span className="font-medium">
          {currency} {price.toFixed(2)}
        </span>
      ) : (
        <span className="text-muted-foreground italic">Not set</span>
      )
    },
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <RaceActionsMenu race={row.original} />
      </div>
    ),
  },
]
