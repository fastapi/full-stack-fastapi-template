import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export type UserRole = "user" | "company" | "admin";

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  initials: string;
  plan: string;
  companyId?: string;
  companyName?: string;
}

export const ROLE_COOKIE = "tabula_role";

export const roles: UserRole[] = ["user", "company", "admin"];

export function isRole(value: string | undefined): value is UserRole {
  return !!value && (roles as string[]).includes(value);
}

/** Mock profiles — one per role. Swap for a real session lookup later. */
const MOCK_USERS: Record<UserRole, AuthUser> = {
  user: {
    id: "u_mara",
    name: "Mara Vance",
    email: "mara@tabula.io",
    role: "user",
    initials: "MV",
    plan: "Pro · 10k pages",
  },
  company: {
    id: "u_devon",
    name: "Devon Park",
    email: "devon@northwind.co",
    role: "company",
    initials: "DP",
    plan: "Team · 100k pages",
    companyId: "co_northwind",
    companyName: "Northwind Co.",
  },
  admin: {
    id: "u_root",
    name: "Sasha Reed",
    email: "sasha@tabula.io",
    role: "admin",
    initials: "SR",
    plan: "Platform Admin",
  },
};

/** Reads the mock role cookie (defaults to "user") and returns the session. */
export async function getSession(): Promise<AuthUser> {
  const cookieStore = await cookies();
  const raw = cookieStore.get(ROLE_COOKIE)?.value;
  const role: UserRole = isRole(raw) ? raw : "user";
  return MOCK_USERS[role];
}

/**
 * Guards a role-specific page: returns the session if the current role is
 * allowed, otherwise redirects to that role's dashboard.
 */
export async function requireRole(allowed: UserRole[], locale: string): Promise<AuthUser> {
  const session = await getSession();
  if (!allowed.includes(session.role)) redirect(`/${locale}/dashboard`);
  return session;
}
