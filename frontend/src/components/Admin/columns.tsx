import type { ColumnDef } from "@tanstack/react-table"

import type { UserPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { can } from "@/lib/auth/permissions"
import { cn } from "@/lib/utils"
import { UserActionsMenu } from "./UserActionsMenu"

export type UserTableData = UserPublic & {
  isCurrentUser: boolean
}

const baseColumns: ColumnDef<UserTableData>[] = [
  {
    accessorKey: "full_name",
    header: "Full Name",
    cell: ({ row }) => {
      const fullName = row.original.full_name
      return (
        <div className="flex items-center gap-2">
          <span
            className={cn("font-medium", !fullName && "text-muted-foreground")}
          >
            {fullName || "N/A"}
          </span>
          {row.original.isCurrentUser && (
            <Badge variant="outline" className="text-xs">
              You
            </Badge>
          )}
        </div>
      )
    },
  },
  {
    accessorKey: "email",
    header: "Email",
    cell: ({ row }) => (
      <span className="text-muted-foreground">{row.original.email}</span>
    ),
  },
  {
    accessorKey: "role",
    header: "Role",
    cell: ({ row }) => {
      const role = row.original.role ?? "member"
      return (
        <Badge variant={role === "admin" ? "default" : "secondary"}>
          {role.charAt(0).toUpperCase() + role.slice(1)}
        </Badge>
      )
    },
  },
  {
    accessorKey: "is_active",
    header: "Status",
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "size-2 rounded-full",
            row.original.is_active ? "bg-green-500" : "bg-gray-400",
          )}
        />
        <span className={row.original.is_active ? "" : "text-muted-foreground"}>
          {row.original.is_active ? "Active" : "Inactive"}
        </span>
      </div>
    ),
  },
]

const actionsColumn: ColumnDef<UserTableData> = {
  id: "actions",
  header: () => <span className="sr-only">Actions</span>,
  cell: ({ row }) => (
    <div className="flex justify-end">
      <UserActionsMenu user={row.original} />
    </div>
  ),
}

export function getColumns(
  currentUser: UserPublic | null | undefined,
): ColumnDef<UserTableData>[] {
  const canManageUsers =
    can(currentUser, "updateAnyUser") || can(currentUser, "deleteAnyUser")

  return canManageUsers ? [...baseColumns, actionsColumn] : baseColumns
}
