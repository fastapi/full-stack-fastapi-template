import type { ReactNode } from "react";
import { setRequestLocale } from "next-intl/server";
import ProtectedShell from "@/components/layouts/ProtectedShell";

export default async function AppLayout({
  children,
  params: { locale },
}: {
  children: ReactNode;
  params: { locale: string };
}) {
  setRequestLocale(locale);
  console.log('run app layout')
  return <ProtectedShell locale={locale}>{children}</ProtectedShell>;
}
