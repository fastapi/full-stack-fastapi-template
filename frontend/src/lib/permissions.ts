// Role-based permission helpers mirroring backend/app/core/permissions.py.
export type UserRole = "admin" | "manager" | "member"

export type Permission =
  | "users:list"
  | "users:create"
  | "users:update_any"
  | "users:delete"
  | "metrics:view"
  | "profile:update_self"
  | "settings:global"

const ROLE_PERMISSIONS: Record<UserRole, readonly Permission[]> = {
  admin: [
    "users:list",
    "users:create",
    "users:update_any",
    "users:delete",
    "metrics:view",
    "profile:update_self",
    "settings:global",
  ],
  manager: ["users:list", "metrics:view", "profile:update_self"],
  member: ["profile:update_self"],
}

export function userHasPermission(
  role: UserRole | undefined,
  permission: Permission,
): boolean {
  if (!role) return false
  return ROLE_PERMISSIONS[role]?.includes(permission) ?? false
}

export function userHasAnyPermission(
  role: UserRole | undefined,
  permissions: Permission[],
): boolean {
  return permissions.some((permission) => userHasPermission(role, permission))
}
