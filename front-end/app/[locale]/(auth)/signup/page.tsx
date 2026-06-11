import { useTranslations } from "next-intl";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/lib/navigation";
import AuthCard from "@/components/auth/AuthCard";
import SignupForm from "@/components/auth/SignupForm";

function SignupFooter() {
  const t = useTranslations("auth.signup");
  return (
    <>
      {t("haveAccount")} <Link href="/login">{t("loginLink")}</Link>
    </>
  );
}

export default async function SignupPage({ params: { locale } }: { params: { locale: string } }) {
  setRequestLocale(locale);
  const t = await getTranslations("auth.signup");

  return (
    <AuthCard title={t("title")} subtitle={t("subtitle")} footer={<SignupFooter />}>
      <SignupForm />
    </AuthCard>
  );
}
