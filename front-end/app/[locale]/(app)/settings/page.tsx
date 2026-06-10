import { setRequestLocale } from "next-intl/server";
import SettingsView from "@/components/dashboard/SettingsView";

export default function SettingsPage({ params: { locale } }: { params: { locale: string } }) {
  setRequestLocale(locale);
  return <SettingsView />;
}
