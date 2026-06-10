import type { ReactNode } from "react";
import { setRequestLocale } from "next-intl/server";
import { getSession } from "@/lib/auth";
import UserShell from "@/components/layouts/UserShell";
import CompanyShell from "@/components/layouts/CompanyShell";
import AdminShell from "@/components/layouts/AdminShell";

// Authenticated area. The role on the session decides which shell wraps the
// page (route guards on role-specific pages handle the rest). Using a single
// group avoids the parallel-route collision that three separate group layouts
// sharing `/dashboard` would cause.
export default async function AppLayout({
  children,
  params: { locale },
}: {
  children: ReactNode;
  params: { locale: string };
}) {
  setRequestLocale(locale);
  const session = await getSession();

  if (session.role === "admin") {
    return <AdminShell user={session}>{children}</AdminShell>;
  }
  if (session.role === "company") {
    return <CompanyShell user={session}>{children}</CompanyShell>;
  }
  return <UserShell user={session}>{children}</UserShell>;
}
