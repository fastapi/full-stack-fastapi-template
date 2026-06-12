import { setRequestLocale } from "next-intl/server";
import { requireRole } from "@/lib/auth";
import MembersView from "@/components/dashboard/MembersView";

export default async function MembersPage({ params: { locale } }: { params: { locale: string } }) {
  setRequestLocale(locale);
  await requireRole(["company", "admin"], locale);
  return <MembersView />;
}
