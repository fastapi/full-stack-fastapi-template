import type { ReactNode } from "react";
import { redirect } from "next/navigation";
import { FileSpreadsheet } from "lucide-react";
import { useTranslations } from "next-intl";
import { setRequestLocale } from "next-intl/server";
import { Link } from "@/lib/navigation";
import { getSession } from "@/lib/auth";
import ThemeToggle from "@/components/ui/ThemeToggle";
import LocaleSwitcher from "@/components/ui/LocaleSwitcher";

function AuthTopbar() {
  const t = useTranslations("auth");
  const tBrand = useTranslations("brand");
  return (
    <div className="auth-topbar">
      <Link href="/" className="brand">
        <span className="glyph">
          <FileSpreadsheet size={16} strokeWidth={2.4} />
        </span>
        <span>{tBrand("name")}</span>
      </Link>
      <div className="auth-topbar-actions">
        <Link href="/" className="btn btn-ghost">
          {t("back")}
        </Link>
        <ThemeToggle />
        <LocaleSwitcher />
      </div>
    </div>
  );
}

export default async function AuthLayout({
  children,
  params: { locale },
}: {
  children: ReactNode;
  params: { locale: string };
}) {
  setRequestLocale(locale);
  const session = await getSession();
  if (session) redirect(`/${locale}/dashboard`);

  return (
    <div className="auth-shell">
      <AuthTopbar />
      <main className="auth-main">{children}</main>
    </div>
  );
}
