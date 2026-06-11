import { setRequestLocale } from "next-intl/server";
import { requireRole } from "@/lib/auth";
import UsersView from "@/components/dashboard/UsersView";

export default async function UsersPage({ params: { locale } }: { params: { locale: string } }) {
  setRequestLocale(locale);
  await requireRole(["admin"], locale);
  return <UsersView />;
}
