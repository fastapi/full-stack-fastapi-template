import { useSuspenseQuery } from "@tanstack/react-query";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { Suspense } from "react";

import { can } from "@/lib/auth/permissions";

import { type UserPublic, UsersService } from "@/client";
import AddUser from "@/components/Admin/AddUser";
import { getColumns, type UserTableData } from "@/components/Admin/columns";
import { DataTable } from "@/components/Common/DataTable";
import PendingUsers from "@/components/Pending/PendingUsers";
import useAuth from "@/hooks/useAuth";

function getUsersQueryOptions() {
  return {
    queryFn: () => UsersService.readUsers({ skip: 0, limit: 100 }),
    queryKey: ["users"],
  };
}

export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
  beforeLoad: async () => {
    const user = await UsersService.readUserMe();

    if (!user.role || !["admin", "manager"].includes(user.role)) {
      throw redirect({ to: "/forbidden" });
    }
  },
  head: () => ({
    meta: [
      {
        title: "Admin - FastAPI Template",
      },
    ],
  }),
});

function UsersTableContent() {
  const { user: currentUser } = useAuth();
  const { data: users } = useSuspenseQuery(getUsersQueryOptions());

  const tableData: UserTableData[] = users.data.map((user: UserPublic) => ({
    ...user,
    isCurrentUser: currentUser?.id === user.id,
  }));

  return <DataTable columns={getColumns(currentUser)} data={tableData} />;
}

function UsersTable() {
  return (
    <Suspense fallback={<PendingUsers />}>
      <UsersTableContent />
    </Suspense>
  );
}

function Admin() {
  const { user: currentUser } = useAuth();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Users</h1>
          <p className="text-muted-foreground">
            Manage user accounts and permissions
          </p>
        </div>
        {can(currentUser, "createUser") && <AddUser />}
      </div>
      <UsersTable />
    </div>
  );
}
