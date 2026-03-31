import type { UserRole } from "@/client"

export const USER_MANAGER_ROLES: UserRole[] = [
  "comercial",
  "juridico",
  "financeiro",
  "rh",
  "super_admin",
]

export const USER_ROLE_LABELS: Record<UserRole, string> = {
  comercial: "Comercial",
  juridico: "Jur\u00eddico",
  financeiro: "Financeiro",
  rh: "RH",
  pj: "PJ",
  super_admin: "Super Admin",
}
