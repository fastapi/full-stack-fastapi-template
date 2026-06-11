import type { ReactNode } from "react";
import { redirect } from "next/navigation";
import { getSession } from "@/lib/auth";
import UserShell from "@/components/layouts/UserShell";
import CompanyShell from "@/components/layouts/CompanyShell";
import AdminShell from "@/components/layouts/AdminShell";

/**
 * Auth gate for the (app) route group: redirects signed-out visitors to
 * /login, then wraps the page in the shell that matches the session's role.
 */
export default async function ProtectedShell({
  children,
  locale,
}: {
  children: ReactNode;
  locale: string;
}) {
  const session = await getSession();
  if (!session) redirect(`/${locale}/login`);

  if (session.role === "admin") {
    return <AdminShell user={session}>{children}</AdminShell>;
  }
  if (session.role === "company") {
    return <CompanyShell user={session}>{children}</CompanyShell>;
  }
  return <UserShell user={session}>{children}</UserShell>;
}
