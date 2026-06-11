"use client";

import { useTransition } from "react";
import { useLocale, useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { login } from "@/lib/actions";

export default function LoginForm() {
  const t = useTranslations("auth.login");
  const locale = useLocale();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const hasError = searchParams.get("error") === "invalid";

  return (
    <form
      className="auth-form"
      action={(formData) => startTransition(() => void login(locale, formData))}
    >
      {hasError && <div className="field-error">{t("error")}</div>}

      <div className="field">
        <label htmlFor="login-email">{t("email")}</label>
        <input
          id="login-email"
          name="email"
          type="email"
          required
          autoComplete="email"
          placeholder={t("emailPlaceholder")}
        />
      </div>

      <div className="field">
        <label htmlFor="login-password">{t("password")}</label>
        <input
          id="login-password"
          name="password"
          type="password"
          required
          autoComplete="current-password"
          placeholder={t("passwordPlaceholder")}
        />
      </div>

      <div className="auth-demo-hint">
        {t("demoHintLabel")}
        <br />
        <b>mara@tabula.io</b> · <b>devon@northwind.co</b> · <b>sasha@tabula.io</b>
      </div>

      <button type="submit" className="btn btn-primary" disabled={isPending}>
        {t("submit")}
      </button>
    </form>
  );
}
