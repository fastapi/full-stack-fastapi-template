import { useTranslations } from "next-intl";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/lib/navigation";
import AuthCard from "@/components/auth/AuthCard";
import LoginForm from "@/components/auth/LoginForm";

function LoginFooter() {
  const t = useTranslations("auth.login");
  return (
    <>
      {t("noAccount")} <Link href="/signup">{t("signupLink")}</Link>
    </>
  );
}

export default async function LoginPage({ params: { locale } }: { params: { locale: string } }) {
  setRequestLocale(locale);
  const t = await getTranslations("auth.login");

  return (
    <AuthCard title={t("title")} subtitle={t("subtitle")} footer={<LoginFooter />}>
      <LoginForm />
    </AuthCard>
  );
}
