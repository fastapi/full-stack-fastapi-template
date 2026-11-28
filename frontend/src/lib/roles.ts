import type { UserPublic, UserRole } from "@/client"

type MaybeUser = Pick<UserPublic, "role"> | null | undefined

export const ROLES = [
  "admin",
  "manager",
  "member",
] as const satisfies readonly UserRole[]

export const isAdmin = (user: MaybeUser) => user?.role === "admin"

export const isStaff = (user: MaybeUser) =>
  user?.role === "admin" || user?.role === "manager"
