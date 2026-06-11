import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { API_BASE, TOKEN_COOKIE } from "@/lib/api";
import type { UserPublic } from "@/lib/client";

export type UserRole = "user" | "admin";

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  initials: string;
  plan: string;
}

export const roles: UserRole[] = ["user", "admin"];

export function isRole(value: string | undefined): value is UserRole {
  return !!value && (roles as string[]).includes(value);
}

function initialsOf(name: string): string {
  return (
    name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]!.toUpperCase())
      .join("") || "?"
  );
}

/** Maps the backend user onto the shape the shells/views render. */
export function toAuthUser(user: UserPublic): AuthUser {
  const name = user.full_name?.trim() || user.email.split("@")[0];
  return {
    id: user.id,
    name,
    email: user.email,
    role: user.is_superuser ? "admin" : "user",
    initials: initialsOf(name),
    plan: user.is_superuser ? "Platform Admin" : "Pay as you go",
  };
}

/**
 * Resolves the session from the auth cookie by asking the API for the current
 * user. Returns null when signed out or the token is no longer valid.
 */
export async function getSession(): Promise<AuthUser | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get(TOKEN_COOKIE)?.value;
  if (!token) return null;

  try {
    const res = await fetch(`${API_BASE}/api/v1/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (!res.ok) return null;
    return toAuthUser((await res.json()) as UserPublic);
  } catch {
    return null;
  }
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
