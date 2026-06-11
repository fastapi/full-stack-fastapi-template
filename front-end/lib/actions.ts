"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ROLE_COOKIE, findUserByEmail, isRole, type UserRole } from "@/lib/auth";

/** Mock sign-in: looks up the email against the seeded mock accounts. */
export async function login(locale: string, formData: FormData): Promise<void> {
  const email = String(formData.get("email") ?? "").trim();
  const user = findUserByEmail(email);

  if (!user) {
    redirect(`/${locale}/login?error=invalid`);
  }

  const cookieStore = await cookies();
  cookieStore.set(ROLE_COOKIE, user.role, {
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
    sameSite: "lax",
  });
  redirect(`/${locale}/dashboard`);
}

/** Mock sign-up: provisions a session for the chosen account type. */
export async function signup(locale: string, formData: FormData): Promise<void> {
  const role = formData.get("role")?.toString();
  const target: UserRole = isRole(role) ? role : "user";

  const cookieStore = await cookies();
  cookieStore.set(ROLE_COOKIE, target, {
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
    sameSite: "lax",
  });
  redirect(`/${locale}/dashboard`);
}

/** Clears the session cookie and returns to the login page. */
export async function logout(locale: string): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete(ROLE_COOKIE);
  redirect(`/${locale}/login`);
}
