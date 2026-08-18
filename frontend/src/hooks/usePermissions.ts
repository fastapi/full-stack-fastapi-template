// React hook exposing role-based permission checks for the current user.
import useAuth from "@/hooks/useAuth"
import {
  type Permission,
  type UserRole,
  userHasAnyPermission,
  userHasPermission,
} from "@/lib/permissions"

export default function usePermissions() {
  const { user } = useAuth()
  const role = user?.role as UserRole | undefined

  return {
    role,
    can: (permission: Permission) => userHasPermission(role, permission),
    canAny: (permissions: Permission[]) =>
      userHasAnyPermission(role, permissions),
  }
}
