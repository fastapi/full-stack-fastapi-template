import { setRequestLocale } from "next-intl/server";
import { requireRole } from "@/lib/auth";
import CompaniesView from "@/components/dashboard/CompaniesView";

export default async function CompaniesPage({ params: { locale } }: { params: { locale: string } }) {
  setRequestLocale(locale);
  await requireRole(["admin"], locale);
  return <CompaniesView />;
}
