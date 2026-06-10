"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ROLE_COOKIE, isRole, type UserRole } from "@/lib/auth";

const HOME: Record<UserRole, string> = {
  user: "dashboard",
  company: "dashboard",
  admin: "dashboard",
};

/** Sets the mock role cookie and redirects into that role's dashboard. */
export async function launchAs(locale: string, role: string): Promise<void> {
  const target: UserRole = isRole(role) ? role : "user";
  const cookieStore = await cookies();
  cookieStore.set(ROLE_COOKIE, target, {
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
    sameSite: "lax",
  });
  redirect(`/${locale}/${HOME[target]}`);
}
