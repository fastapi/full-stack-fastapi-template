import { setRequestLocale } from "next-intl/server";
import { requireRole } from "@/lib/auth";
import ProfileView from "@/components/dashboard/ProfileView";

export default async function ProfilePage({ params: { locale } }: { params: { locale: string } }) {
  setRequestLocale(locale);
  const user = await requireRole(["user", "company", "admin"], locale);
  return <ProfileView user={user} />;
}
