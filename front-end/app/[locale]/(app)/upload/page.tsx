import { setRequestLocale } from "next-intl/server";
import { requireRole } from "@/lib/auth";
import UploadView from "@/components/dashboard/UploadView";

export default async function UploadPage({ params: { locale } }: { params: { locale: string } }) {
  setRequestLocale(locale);
  await requireRole(["user", "admin"], locale);
  return <UploadView />;
}
