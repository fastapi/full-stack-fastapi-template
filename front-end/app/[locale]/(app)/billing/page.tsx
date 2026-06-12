import { setRequestLocale } from "next-intl/server";
import { requireRole } from "@/lib/auth";
import BillingView from "@/components/dashboard/BillingView";

export default async function BillingPage({ params: { locale } }: { params: { locale: string } }) {
  setRequestLocale(locale);
  await requireRole(["user", "company", "admin"], locale);
  return <BillingView />;
}
