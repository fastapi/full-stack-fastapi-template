import { setRequestLocale } from "next-intl/server";
import { requireRole } from "@/lib/auth";
import DocumentsView from "@/components/dashboard/DocumentsView";

export default async function DocumentsPage({ params: { locale } }: { params: { locale: string } }) {
  setRequestLocale(locale);
  await requireRole(["user", "company", "admin"], locale);
  return <DocumentsView />;
}
