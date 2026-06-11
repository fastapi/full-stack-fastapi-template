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

/** Reads the mock role cookie and returns the session, or null if not signed in. */
export async function getSession(): Promise<AuthUser | null> {
  const cookieStore = await cookies();
  const raw = cookieStore.get(ROLE_COOKIE)?.value;
  if (!isRole(raw)) return null;
  return MOCK_USERS[raw];
}

/** Looks up a mock user by email (used by the login form's mock credential check). */
export function findUserByEmail(email: string): AuthUser | undefined {
  return Object.values(MOCK_USERS).find((u) => u.email.toLowerCase() === email.toLowerCase());
}

/**
 * Guards a role-specific page: returns the session if the current role is
 * allowed, redirects to /login if signed out, or to that role's dashboard
 * if signed in with a different role.
 */
export async function requireRole(allowed: UserRole[], locale: string): Promise<AuthUser> {
  const session = await getSession();
  if (!session) redirect(`/${locale}/login`);
  if (!allowed.includes(session.role)) redirect(`/${locale}/dashboard`);
  return session;
}
