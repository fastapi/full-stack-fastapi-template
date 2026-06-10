import { setRequestLocale } from "next-intl/server";
import OverviewView from "@/components/dashboard/OverviewView";

export default function DashboardPage({ params: { locale } }: { params: { locale: string } }) {
  setRequestLocale(locale);
  return <OverviewView />;
}
